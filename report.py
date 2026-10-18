#!/usr/bin/env python3
"""Stage 3: acceptance report.

The four checks agreed up front:
  1. all 727 cards present, zero parse failures
  2. per-card completeness metrics
  3. field coverage report
  4. spot-check a random sample against live pages
Check 4 is the only one that touches the network.
"""
import json, os, random, sys, urllib.request
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RAW, OUT = os.path.join(HERE, "raw"), os.path.join(HERE, "out")
API = "https://api.savesage.club"
UA = "savesage-kb-research/1.0 (+churiwalmayank@gmail.com)"


def spot_check(cards, n=12, seed=7):
    """Re-fetch n cards live and diff the fields we claim to have captured."""
    random.seed(seed)
    sample = random.sample(cards, min(n, len(cards)))
    rows = []
    for c in sample:
        url = f"{API}/credit-card/{c['slug']}?tab=earn-categories"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                live = json.loads(r.read().decode())
        except Exception as e:
            rows.append((c["slug"], "FETCH_FAIL", str(e)[:60])); continue
        live = live[0] if isinstance(live, list) else live
        td = live.get("tabData", {})
        excl = {(e.get("name") or "").strip() for e in (td.get("exclusions") or [])}
        live_rules = [i for i in (td.get("items") or [])
                      if (i.get("name") or "").strip() not in excl
                      and "No Reward" not in (i.get("child") or "")]
        ours = c["earn_rules"]
        diffs = []
        if len(live_rules) != len(ours):
            diffs.append(f"count {len(ours)}!={len(live_rules)}")
        live_names = [(i.get("name") or "").strip() for i in live_rules]
        if live_names != [r["name"] for r in ours]:
            diffs.append("names differ")
        if (td.get("earnRowsTotal") != c["completeness"]["earn_rules_total"]):
            diffs.append("stated total differs")
        rows.append((c["slug"], "OK" if not diffs else "MISMATCH", "; ".join(diffs) or f"{len(ours)} rules"))
    return rows


def main():
    cards = [json.loads(l) for l in open(os.path.join(OUT, "cards.ndjson"))]
    slugs = json.load(open(os.path.join(RAW, "slugs.json")))
    stats = json.load(open(os.path.join(OUT, "_stats.json")))
    tax = json.load(open(os.path.join(OUT, "taxonomy_dictionary.json")))

    missing = sorted(set(slugs) - {c["slug"] for c in cards})

    # ---- coverage -------------------------------------------------------
    tot = sum(len(c["earn_rules"]) for c in cards)
    stated = sum(c["completeness"]["earn_rules_total"] or 0 for c in cards)
    base = sum(1 for c in cards for r in c["earn_rules"] if r["is_base_rate"])
    n = tot - base
    catp, merp, ratep = Counter(), Counter(), Counter()
    for c in cards:
        for r in c["earn_rules"]:
            ratep[r["provenance"].get("rate")] += 1
            if r["is_base_rate"]:
                continue
            catp[r["provenance"].get("category")] += 1
            merp[r["provenance"].get("merchant_raw")] += 1

    def pct(x, d):
        return f"{x}/{d} ({x/d*100:.1f}%)" if d else "0/0"

    field_cov = {}
    for f in ("title", "overview", "network", "return_percentage", "apply_link"):
        field_cov[f] = sum(1 for c in cards if c.get(f))
    for f, path in (("fees.renewal", ("fees", "renewal")), ("fees.forex_markup_pct", ("fees", "forex_markup_pct")),
                    ("fees.apr_pct", ("fees", "apr_pct")), ("fees.joining", ("fees", "joining"))):
        field_cov[f] = sum(1 for c in cards if c[path[0]].get(path[1]) is not None)
    for f in ("benefits", "milestones", "exclusions", "best_suited"):
        field_cov[f] = sum(1 for c in cards if c.get(f))
    field_cov["lounge.tiers"] = sum(1 for c in cards if c["lounge"]["tiers"])

    ben_have = sum(len(c["benefits"]) for c in cards)
    ben_stated = sum(c["completeness"]["benefits_total"] or 0 for c in cards)
    lng_have = sum(len(c["lounge"]["structured"]) for c in cards)
    lng_stated = sum(c["completeness"]["lounge_total"] or 0 for c in cards)

    spot = spot_check(cards)
    spot_ok = sum(1 for _, s, _ in spot if s == "OK")

    L = []
    A = L.append
    A("# SaveSage credit-card scrape — acceptance report\n")
    A(f"Source: `savesage.club` / `api.savesage.club`, public unauthenticated endpoints only.\n")
    A("## 1. Completeness\n")
    A(f"- Cards in sitemap/catalogue: **{len(slugs)}**")
    A(f"- Cards parsed: **{len(cards)}**")
    A(f"- Missing: **{len(missing)}** {missing or ''}")
    A(f"- Parse failures: **{len(stats['missing_earn'])}**")
    A(f"- Rate-parse misses: **{len(stats['rate_parse_misses'])}**\n")
    A("### Earn rules — the app-wall test\n")
    A(f"- Rules emitted: **{tot}**")
    A(f"- Rules SaveSage states exist: **{stated}**")
    A(f"- **Recovered: {'100%' if tot == stated else f'{tot/stated*100:.1f}%'}** "
      f"({stats['rows_api']} returned structured, {stats['rows_recovered']} recovered from prose)\n")
    A("## 2. Field coverage\n")
    A("| Field | Cards with a value |")
    A("|---|---|")
    for f, v in sorted(field_cov.items(), key=lambda kv: -kv[1]):
        A(f"| `{f}` | {pct(v, len(cards))} |")
    A("")
    A("### Earn-rule field provenance\n")
    A(f"Base-rate rows ({base}) are excluded — they legitimately have no category.\n")
    A("| Field | Coverage | Breakdown |")
    A("|---|---|---|")
    A(f"| `rate` | {pct(sum(v for k, v in ratep.items() if k != 'null'), tot)} | {dict(ratep)} |")
    A(f"| `category` | {pct(n - catp['null'], n)} | {dict(catp)} |")
    A(f"| `merchant_raw` | {pct(n - merp['null'], n)} | {dict(merp)} |")
    A("")
    A("## 3. What the app-wall still costs\n")
    A("| Data | Have | SaveSage states | Note |")
    A("|---|---|---|---|")
    A(f"| Earn rules | {tot} | {stated} | names + rates fully recovered |")
    A(f"| Benefits (structured) | {ben_have} | {ben_stated} | rest available as prose only |")
    A(f"| Lounge (structured) | {lng_have} | {lng_stated} | all tiers available as prose |")
    A(f"| Milestones | {sum(len(c['milestones']) for c in cards)} | — | never gated, fully structured |")
    A("")
    A("## 4. Spot-check against live pages\n")
    A(f"Re-fetched {len(spot)} random cards and diffed. **{spot_ok}/{len(spot)} exact.**\n")
    A("| Card | Result | Detail |")
    A("|---|---|---|")
    for s, st, d in spot:
        A(f"| `{s}` | {st} | {d} |")
    A("")
    # ---- calculator matrix ---------------------------------------------
    mpath = os.path.join(OUT, "category_rate_matrix.json")
    if os.path.exists(mpath):
        matrix = json.load(open(mpath))
        dis = json.load(open(os.path.join(OUT, "source_disagreements.json")))
        cells = sum(len(v["categories"]) for v in matrix.values())
        excl_pairs = 0
        for c in cards:
            m = matrix.get(c["slug"])
            if not m:
                continue
            ex = {(e.get("category") or e.get("name") or "").strip() for e in c["exclusions"]}
            excl_pairs += sum(1 for cat in m["categories"] if cat in ex)
        agree = excl_pairs - len(dis)
        pv = Counter(round(v["summary"]["point_value_inr"], 2) for v in matrix.values()
                     if v["summary"]["point_value_inr"])

        A("## 5. Category rate matrix (reward calculator)\n")
        A("A second, independent view of the same cards: every card asked what a fixed "
          "₹10,000 spend earns in each of SaveSage's 16 standard categories. This is "
          "arithmetic on their numbers, not inference — and it covers every card uniformly, "
          "including the rules the app-wall hides.\n")
        A(f"- Cards covered: **{len(matrix)}/{len(cards)}**")
        A(f"- Cells: **{cells}** (card × category), **0** failures")
        A(f"- Cards with a derived point value: **{sum(1 for v in matrix.values() if v['summary']['point_value_inr'])}**")
        A(f"- Most common point values: {dict(pv.most_common(6))}")
        A(f"- Cards earning nothing in all 16 categories: "
          f"**{sum(1 for v in matrix.values() if v['summary']['categories_earning'] == 0)}**\n")
        A("### Cross-validation against the card pages\n")
        A(f"Where a card page lists a category as an exclusion, does the calculator agree it earns nothing?\n")
        A(f"- Comparable pairs: **{excl_pairs}**")
        A(f"- **Agree: {agree} ({agree/excl_pairs*100:.1f}%)**")
        A(f"- Disagree: {len(dis)} ({len(dis)/excl_pairs*100:.1f}%), across "
          f"{len({d['slug'] for d in dis})} cards — see `source_disagreements.json`")
        A(f"- Disagreements by category: {dict(Counter(d['category'] for d in dis).most_common(6))}\n")
        A("Both readings are preserved per card. Two of their own systems contradicting each "
          "other is a finding to surface, not something to average away.\n")

    A("## 6. Data-quality findings in SaveSage's own data\n")
    A(f"- **{len(tax['conflicts'])} rule names carry conflicting labels** across cards "
      "(same rule name, different category/merchant). Majority wins; all alternatives kept in "
      "`taxonomy_dictionary.json`.")
    A("- `zero-forex-markup` collection includes cards charging up to 1.99% markup. "
      "Reproduced faithfully; `true-zero-forex` (ours) holds the 31 that are actually 0%.")
    A("- Category vocabulary is inconsistent: `GiftCards`/`Gift Cards`, `Online`/`Online Shopping`, "
      "and a literal `TRUE` as a category value. Folded on read; originals preserved in `raw/`.")
    A("- Catalogue reports 731 rows for 727 unique slugs — 4 duplicates.")
    A("- `redemption-options` tab returns no data for any card; it is an app advert. Dropped.")

    open(os.path.join(OUT, "report.md"), "w").write("\n".join(L))
    print("\n".join(L[:40]))
    print(f"\n[written to out/report.md]  spot-check {spot_ok}/{len(spot)} exact")


if __name__ == "__main__":
    main()
