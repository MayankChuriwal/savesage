#!/usr/bin/env python3
"""Stage 2: raw/ -> normalized JSON knowledge base. Reads disk only, no network.

Provenance rules, applied per field:
  api        - SaveSage returned it structured
  parsed     - read deterministically off their prose (rate value / denominator)
  dictionary - their own label for this exact rule name, harvested from a card
               where the row happened to be unhidden
  null       - unknown. Never guessed.
"""
import json, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "out")

# "Earn 5 Reward Points per Rs.100 spent", "Get 2.5% Cashback ...", etc.
RATE_PATTERNS = [
    re.compile(r"(?:Earn|Get)\s+([\d,]+(?:\.\d+)?)\s*(?:Reward\s*Points?|RPs?|Points?|Miles?|Cashback|EDGE\s*(?:Reward\s*)?Points?)?\s*per\s*(?:₹|Rs\.?|INR)\s*([\d,]+)", re.I),
    re.compile(r"(?:Earn|Get)\s+([\d,]+(?:\.\d+)?)\s*%\s*(?:Cashback|back|Discount)", re.I),
]
NO_REWARD = re.compile(r"No\s+Reward|no\s+points|not\s+eligible", re.I)

# "Myntra via SmartBuy", "Flights via Amazon" -> merchant + booking channel.
VIA_RE = re.compile(r"^(.+?)\s+via\s+(.+?)$", re.I)

# The everything-else rate. Genuinely has no category -- it applies to any
# spend that no other rule claims -- so it must not count as a missing label.
BASE_NAMES = {"base rewards", "base reward", "base rate", "everyday rate",
              "all other spends", "other spends"}

# SaveSage's own category vocabulary is inconsistent; fold the variants so a
# name-match doesn't produce two spellings of one category.
VOCAB_ALIASES = {"GiftCards": "Gift Cards", "Online": "Online Shopping"}
VOCAB_JUNK = {"TRUE"}          # bad row in their data, never use as a category


def num(s):
    if s is None:
        return None
    s = str(s).replace(",", "").strip()
    try:
        f = float(s)
        return int(f) if f == int(f) else f
    except ValueError:
        return None


def load(slug, tab):
    p = os.path.join(RAW, "cards", slug, f"{tab}.json")
    if not os.path.exists(p):
        return None
    try:
        d = json.load(open(p))
    except (ValueError, OSError):
        return None
    if isinstance(d, list):
        d = d[0] if d else None
    if not isinstance(d, dict) or "tabData" not in d:
        return None
    return d


def parse_rate(text):
    """Return (value, per, is_percent) parsed off prose, or (None, None, None)."""
    if not text:
        return None, None, None
    if NO_REWARD.search(text):
        return 0, None, None
    m = RATE_PATTERNS[0].search(text)
    if m:
        return num(m.group(1)), num(m.group(2)), False
    m = RATE_PATTERNS[1].search(text)
    if m:
        return num(m.group(1)), 100, True
    return None, None, None


def build_dictionary(slugs):
    """name -> (category, subcategory, merchant), from every unhidden earnRow.

    Conflicts are resolved by majority; a name whose labels disagree across
    cards keeps the winner and is reported, so disagreement is visible rather
    than silently collapsed.
    """
    votes = defaultdict(Counter)
    for slug in slugs:
        d = load(slug, "earn-categories")
        if not d:
            continue
        for r in d["tabData"].get("earnRows") or []:
            name = (r.get("name") or "").strip()
            if not name:
                continue
            key = (r.get("category"), r.get("subCategory"), r.get("merchant"))
            if any(key):
                votes[name][key] += 1
    dictionary, conflicts = {}, []
    for name, c in votes.items():
        (cat, sub, mer), n = c.most_common(1)[0]
        dictionary[name] = {"category": cat, "subcategory": sub, "merchant_raw": mer}
        if len(c) > 1:
            conflicts.append({"name": name, "chosen": [cat, sub, mer],
                              "support": n, "total": sum(c.values()),
                              "alternatives": [list(k) for k in c if k != (cat, sub, mer)]})
    return dictionary, conflicts


def build_vocab(slugs):
    """Every category label SaveSage themselves use, normalized."""
    vocab = set()
    for slug in slugs:
        d = load(slug, "earn-categories")
        if not d:
            continue
        td = d["tabData"]
        for r in (td.get("earnRows") or []):
            for k in ("category", "subCategory"):
                if r.get(k):
                    vocab.add(r[k])
        for e in (td.get("exclusions") or []):
            if e.get("category"):
                vocab.add(e["category"])
    vocab = {VOCAB_ALIASES.get(v, v) for v in vocab} - VOCAB_JUNK
    return vocab


def split_via(name):
    """'Myntra via SmartBuy' -> ('Myntra', 'SmartBuy'). Deterministic, not a guess."""
    m = VIA_RE.match(name or "")
    return (m.group(1).strip(), m.group(2).strip()) if m else (None, None)


def card_unit(earn_rows):
    """Single reward unit for this card, or None if its rows disagree."""
    units = {r.get("unit") for r in earn_rows if r.get("unit")}
    return units.pop() if len(units) == 1 else None


def build_earn(d, dictionary, vocab, stats):
    td = d["tabData"]
    rows = td.get("earnRows") or []
    items = td.get("items") or []
    exclusion_names = {(e.get("name") or "").strip() for e in (td.get("exclusions") or [])}
    by_name = {(r.get("name") or "").strip(): r for r in rows}
    unit = card_unit(rows)

    out = []
    for it in items:
        name = (it.get("name") or "").strip()
        text = (it.get("child") or "").strip()
        if name in exclusion_names or NO_REWARD.search(text or ""):
            continue                                   # handled as exclusions
        r = by_name.get(name)
        prov = {}
        if r:                                          # unhidden: fully structured
            value, per, u = r.get("points"), r.get("per"), r.get("unit")
            cat, sub, mer = r.get("category"), r.get("subCategory"), r.get("merchant")
            cap, cycle, mn = r.get("cap"), r.get("capCycle"), r.get("minTxnAmount")
            prov = {"rate": "api",
                    "category": "api" if cat else "null",
                    "merchant_raw": "api" if mer else "null"}
            stats["rows_api"] += 1
        else:                                          # hidden: recover from prose
            value, per, is_pct = parse_rate(text)
            u = "Percent" if is_pct else unit
            hit = dictionary.get(name)
            cat = hit["category"] if hit else None
            sub = hit["subcategory"] if hit else None
            mer = hit["merchant_raw"] if hit else None
            cap = cycle = mn = None
            prov = {"rate": "parsed" if value is not None else "null",
                    "category": "dictionary" if (hit and cat) else "null",
                    "merchant_raw": "dictionary" if (hit and mer) else "null",
                    "unit": "inferred_card_unit" if (u and not is_pct) else prov.get("unit", "null")}
            stats["rows_recovered"] += 1
            if hit and cat:
                stats["rows_dict_filled"] += 1
            if value is None:
                stats["rate_parse_misses"].append((name, text))

        is_base = name.lower() in BASE_NAMES
        merchant, channel = split_via(name)

        # Fallback 1: the rule name IS one of their own category labels.
        if not cat and not is_base:
            cand = VOCAB_ALIASES.get(name, name)
            if cand in vocab:
                cat = cand
                prov["category"] = "name_matches_taxonomy"
                stats["cat_from_name"] += 1

        # Fallback 2: "<Merchant> via <Channel>" splits deterministically.
        if merchant and not mer:
            mer = merchant
            prov["merchant_raw"] = "parsed_from_name"
            stats["merchant_from_via"] += 1

        out.append({
            "name": name,
            "is_base_rate": is_base,
            "rate": {"value": value, "per": per, "currency": "INR", "unit": u},
            "category": cat, "subcategory": sub,
            "merchant_raw": mer, "booking_channel": channel,
            "cap": cap, "cap_cycle": cycle, "min_txn": mn,
            "raw_text": text,
            "provenance": prov,
        })
    return out, td


def build_card(slug, meta, dictionary, vocab, stats):
    earn_doc = load(slug, "earn-categories")
    if not earn_doc:
        stats["missing_earn"].append(slug)
        return None

    c = earn_doc.get("card") or {}
    ov = earn_doc.get("cardOverview") or {}
    earn_rules, td = build_earn(earn_doc, dictionary, vocab, stats)

    ben = load(slug, "benefits-and-offers")
    btd = ben["tabData"] if ben else {}
    lng = load(slug, "lounge-access")
    ltd = lng["tabData"] if lng else {}
    mst = load(slug, "milestones")
    mtd = mst["tabData"] if mst else {}

    best = [s.strip() for s in (ov.get("bestSuited") or "").split(",") if s.strip()]

    return {
        "slug": slug,
        "card_id": earn_doc.get("cardId"),
        "title": earn_doc.get("title"),
        "display_name": meta.get("displayName"),
        "issuer": {"slug": c.get("bankSlug") or meta.get("bankSlug"),
                   "name": c.get("bankName") or meta.get("bankName")},
        "network": c.get("networkType") or meta.get("networkType"),
        "fees": {"joining": c.get("joiningFee"), "renewal": c.get("renewalFee"),
                 "addon": c.get("addOnCardFee"),
                 "forex_markup_pct": c.get("forexMarkupPercent"),
                 "apr_pct": c.get("aprPercent")},
        "return_percentage": c.get("returnPercentage"),
        "overview": ov.get("overviewText"),
        "best_suited": best,
        "flags": {"is_fd_card": meta.get("isFdCard"),
                  "is_business": meta.get("isBusinessCard"),
                  "is_popular": meta.get("isPopular"),
                  "is_currently_issuing": meta.get("isCurrentlyIssuing")},
        "collections": meta.get("categorySlugs") or [],
        "benefit_types": meta.get("benefitTypes") or [],
        "lounge_types": meta.get("loungeTypes") or [],
        "images": {"card": c.get("cardImageLink"), "bank_logo": c.get("bankLogoUrl")},
        "apply_link": c.get("applyLink"),

        "earn_rules": earn_rules,
        "exclusions": td.get("exclusions") or [],
        "benefits": btd.get("benefitRows") or [],
        "benefits_prose": btd.get("items") or [],
        "lounge": {"tiers": ltd.get("loungeAccessItems") or [],
                   "structured": ltd.get("loungeRows") or [],
                   "airports": ltd.get("loungeAirports")},
        "milestones": mtd.get("mileStoneItems") or [],

        "completeness": {
            "earn_rules_total": td.get("earnRowsTotal"),
            "earn_rules_structured": len(td.get("earnRows") or []),
            "earn_rules_emitted": len(earn_rules),
            "earn_rules_with_category": sum(1 for r in earn_rules if r["category"]),
            "benefits_total": btd.get("benefitRowsTotal"),
            "benefits_structured": len(btd.get("benefitRows") or []),
            "lounge_total": ltd.get("loungeRowsTotal"),
            "lounge_structured": len(ltd.get("loungeRows") or []),
            "milestones_count": len(mtd.get("mileStoneItems") or []),
        },
        "source": {"site": "savesage.club", "api": "api.savesage.club",
                   "tabs": ["earn-categories", "benefits-and-offers",
                            "lounge-access", "milestones"]},
    }


def main():
    slugs = json.load(open(os.path.join(RAW, "slugs.json")))
    meta_by_slug = {}
    for f in sorted(os.listdir(os.path.join(RAW, "list"))):
        if not f.endswith(".json"):
            continue
        for c in json.load(open(os.path.join(RAW, "list", f))).get("cards", []):
            meta_by_slug.setdefault(c["slug"], c)

    dictionary, conflicts = build_dictionary(slugs)
    print(f"dictionary: {len(dictionary)} rule names, {len(conflicts)} with conflicting labels")

    vocab = build_vocab(slugs)
    print(f"category vocabulary: {len(vocab)} labels")

    stats = {"rows_api": 0, "rows_recovered": 0, "rows_dict_filled": 0,
             "cat_from_name": 0, "merchant_from_via": 0,
             "rate_parse_misses": [], "missing_earn": []}

    os.makedirs(os.path.join(OUT, "cards"), exist_ok=True)
    cards = []
    for slug in slugs:
        card = build_card(slug, meta_by_slug.get(slug, {}), dictionary, vocab, stats)
        if card:
            cards.append(card)
            json.dump(card, open(os.path.join(OUT, "cards", f"{slug}.json"), "w"),
                      ensure_ascii=False, indent=1)

    with open(os.path.join(OUT, "cards.ndjson"), "w") as f:
        for c in cards:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    json.dump(cards, open(os.path.join(OUT, "cards.json"), "w"), ensure_ascii=False, indent=1)
    json.dump({"rule_name_to_taxonomy": dictionary, "conflicts": conflicts},
              open(os.path.join(OUT, "taxonomy_dictionary.json"), "w"),
              ensure_ascii=False, indent=1)

    json.dump(stats, open(os.path.join(OUT, "_stats.json"), "w"), ensure_ascii=False, indent=1)
    print(f"cards: {len(cards)}  api rows: {stats['rows_api']}  "
          f"recovered: {stats['rows_recovered']}  dict-filled: {stats['rows_dict_filled']}  "
          f"cat-from-name: {stats['cat_from_name']}  merchant-from-via: {stats['merchant_from_via']}  "
          f"rate misses: {len(stats['rate_parse_misses'])}")


if __name__ == "__main__":
    main()
