#!/usr/bin/env python3
"""Stage 2c: bank hubs + best-for collections.

Hub pages paginate at 24 and deeper pages need the query form robots
disallows, so each hub gives us its FIRST page only. That first page is not a
consolation prize -- it is SaveSage's own editorial ranking for that
collection, in order, which no attribute filter can reconstruct.

Full membership is rebuilt from card attributes instead, marked as derived.
"""
import glob, json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "out")

SLUG_RE = re.compile(r'/credit-card/([a-z0-9-]+)"')
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
TAG_RE = re.compile(r"<[^>]+>")


def text(s):
    return html.unescape(TAG_RE.sub("", s)).strip()


def ordered_slugs(raw):
    """Card slugs in page order, deduped, first occurrence wins."""
    seen, out = set(), []
    for m in SLUG_RE.finditer(raw.replace('\\"', '"')):
        s = m.group(1)
        if s not in seen:
            seen.add(s); out.append(s)
    return out


# Collections we can rebuild from catalogue attributes. Each rule was fitted
# against the count SaveSage states on its own hub page, and against the 24
# cards that hub actually lists -- so these are reverse-engineered from their
# behaviour, not guessed. Counts land 1-3 under theirs because they count 731
# catalogue rows and we count 727 unique slugs.
#
# "zero-forex-markup" is a misnomer on their side: only 10 of the 24 cards
# their own hub lists actually charge 0%, and the fitted rule is <= 1.99. We
# keep it as-is because this field's job is to REPRODUCE their collection --
# tightening it to == 0 would drop 14 cards they demonstrably include. The
# honest version of that fact is published separately as OURS, below.
#
# forexMarkupPercent is null on 26 cards (unknown, NOT zero), so every rule
# here tests `is not None` before comparing.
APPROXIMATE = {"premium"}          # fitted to a range, not an exact stated count

# Collections that are ours, not SaveSage's. Same shape, different provenance.
OURS = {
    "true-zero-forex": (
        lambda c: c.get("forexMarkupPercent") == 0,
        "Cards charging exactly 0% forex markup. Distinct from SaveSage's "
        "'zero-forex-markup' collection, which includes cards up to 1.99%.",
    ),
}

DERIVED = {
    "lifetime-free":            lambda c: not c.get("joiningFee") and not c.get("renewalFee"),
    "lifetime-free-rupay":      lambda c: not c.get("joiningFee") and not c.get("renewalFee") and c.get("networkType") == "RUPAY",
    "rupay-upi":                lambda c: c.get("networkType") == "RUPAY",
    "zero-forex-markup":        lambda c: c.get("forexMarkupPercent") is not None and c["forexMarkupPercent"] <= 1.99,
    "annual-fee-under-1000":    lambda c: 0 < (c.get("renewalFee") or 0) < 1000,
    "premium":                  lambda c: (c.get("renewalFee") or 0) >= 5000,
    "business":                 lambda c: bool(c.get("isBusinessCard")),
    "no-credit-history":        lambda c: bool(c.get("isFdCard")),
    "airport-lounge-access":    lambda c: bool(c.get("loungeTypes")),
    "lounge-access-under-1000": lambda c: bool(c.get("loungeTypes")) and 0 < (c.get("renewalFee") or 0) < 1000,
    "free-with-lounge-access":  lambda c: bool(c.get("loungeTypes")) and not c.get("joiningFee") and not c.get("renewalFee"),
    "golf":                     lambda c: "GOLF" in (c.get("benefitTypes") or []),
    "insurance":                lambda c: "INSURANCE" in (c.get("benefitTypes") or []),
    "concierge":                lambda c: "CONCIERGE" in (c.get("benefitTypes") or []),
    "memberships":             lambda c: "MEMBERSHIP" in (c.get("benefitTypes") or []),
    "movies-and-events":        lambda c: "MOVIES_AND_EVENTS" in (c.get("benefitTypes") or []),
    "dining":                   lambda c: "DINING_ORDER_IN" in (c.get("benefitTypes") or []),
    "shopping":                 lambda c: "SHOPPING" in (c.get("benefitTypes") or []),
    "travel-benefits":          lambda c: "TRAVEL" in (c.get("benefitTypes") or []),
    "cashback":                 lambda c: "cashback" in (c.get("categorySlugs") or []),
    "brand-wallets":            lambda c: "brand-wallet" in (c.get("categorySlugs") or []),
    "travel-bookings":          lambda c: "travel-booking" in (c.get("categorySlugs") or []),
    "rewards-catalogue":        lambda c: "catalogue-products" in (c.get("categorySlugs") or []),
}


def main():
    catalogue = {}
    for f in glob.glob(os.path.join(RAW, "list", "*.json")):
        for c in json.load(open(f)).get("cards", []):
            catalogue.setdefault(c["slug"], c)

    banks, collections = {}, {}
    for path in sorted(glob.glob(os.path.join(RAW, "hubs", "*.html"))):
        name = os.path.basename(path)[:-5]
        raw = open(path, encoding="utf-8", errors="replace").read()
        h1 = H1_RE.search(raw)
        rec = {
            "slug": name.replace("best-for__", ""),
            "heading": text(h1.group(1)) if h1 else None,
            "url": f"https://savesage.club/credit-cards/{name.replace('__', '/')}",
            "top_cards_in_site_order": ordered_slugs(raw),
        }
        (collections if name.startswith("best-for__") else banks)[rec["slug"]] = rec

    # rebuild full membership where the rule is exact
    for slug, fn in DERIVED.items():
        members = sorted(s for s, c in catalogue.items() if fn(c))
        rec = collections.setdefault(slug, {"slug": slug, "heading": None,
                                            "url": f"https://savesage.club/credit-cards/best-for/{slug}",
                                            "top_cards_in_site_order": []})
        rec["derived_members"] = members
        rec["derived_count"] = len(members)
        rec["membership_source"] = "derived_from_card_attributes"
        rec["membership_confidence"] = "approximate" if slug in APPROXIMATE else "fitted_to_site_count"

    for slug, rec in collections.items():
        rec.setdefault("derived_members", None)
        rec.setdefault("membership_source", "site_first_page_only")
        rec.setdefault("defined_by", "savesage")

    # our own collections -- never mixed into the reproduced ones
    for slug, (fn, note) in OURS.items():
        members = sorted(s for s, c in catalogue.items() if fn(c))
        collections[slug] = {
            "slug": slug, "heading": None, "url": None,
            "top_cards_in_site_order": [],
            "derived_members": members, "derived_count": len(members),
            "membership_source": "derived_from_card_attributes",
            "membership_confidence": "exact",
            "defined_by": "us", "note": note,
        }

    for slug, rec in banks.items():
        rec["members"] = sorted(s for s, c in catalogue.items() if c.get("bankSlug") == slug)
        rec["count"] = len(rec["members"])

    os.makedirs(OUT, exist_ok=True)
    json.dump(banks, open(os.path.join(OUT, "banks.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(collections, open(os.path.join(OUT, "collections.json"), "w"), ensure_ascii=False, indent=1)
    covered = sum(1 for r in collections.values() if r["derived_members"] is not None)
    print(f"banks: {len(banks)} ({sum(r['count'] for r in banks.values())} memberships)")
    print(f"collections: {len(collections)}, {covered} with full derived membership, "
          f"{len(collections)-covered} first-page-only")


if __name__ == "__main__":
    main()
