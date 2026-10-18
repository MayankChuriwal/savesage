#!/usr/bin/env python3
"""Per-card HDFC discrepancy report: Rivo card_catalogue vs SaveSage scrape."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
RIVO = {c["slug"]: c for c in json.load(open(os.path.join(HERE, "rivo_hdfc.json")))}
SS = {c["slug"]: c for c in (json.loads(l) for l in
      open(os.path.join(HERE, "..", "out", "cards.ndjson")))}
CMP = json.load(open(os.path.join(HERE, "hdfc_comparison.json")))

HIGH = 0.75          # below this the name match is not trustworthy


def rate_of(x):
    if x.get("effective_rate_pct") is not None:
        return round(float(x["effective_rate_pct"]), 2)
    pps, sp = x.get("points_per_spend"), x.get("spend_amount")
    return round(pps / sp * 100, 2) if (pps and sp) else None


def main():
    L, A = [], lambda s: L.append(s)
    c = CMP["counts"]
    high = [x for x in CMP["cards"] if x.get("matched") and x["score"] >= HIGH]
    low = [x for x in CMP["cards"] if x.get("matched") and x["score"] < HIGH]
    none = [x for x in CMP["cards"] if not x.get("matched")]

    A("# HDFC — Rivo `card_catalogue` vs SaveSage scrape\n")
    A(f"Rivo **{c['rivo']}** cards · SaveSage **{c['savesage']}** · "
      f"matched **{c['matched']}** ({len(high)} high-confidence, {len(low)} need review) · "
      f"Rivo-only **{c['rivo_only']}** · SaveSage-only **{c['savesage_only']}**\n")
    A("Matching is by normalized name, since SaveSage splits network variants "
      "(`hdfc-millennia-visa`/`-rupay`) that Rivo folds into one card. Matches below "
      f"{HIGH} are listed separately and should not be trusted.\n")

    # ---- coverage table --------------------------------------------------
    t = lambda k: sum(x["rules"][k] for x in high)
    rc, sc = t("rivo_count"), t("savesage_count")
    A("## Structural coverage (high-confidence matches only)\n")
    A("| | Rivo | SaveSage |")
    A("|---|---|---|")
    A(f"| Earn rules | {rc} | {sc} |")
    A(f"| Rules with **MCC codes** | **{t('rivo_with_mcc')}** ({t('rivo_with_mcc')/rc*100:.0f}%) | **0** (none exist) |")
    A(f"| Rules with merchant | {t('rivo_with_merchant')} ({t('rivo_with_merchant')/rc*100:.0f}%) | {t('savesage_with_merchant')} ({t('savesage_with_merchant')/sc*100:.0f}%) |")
    A(f"| Rules with **numeric cap** | **{t('rivo_with_cap')}** ({t('rivo_with_cap')/rc*100:.0f}%) | 0 (prose only, {t('savesage_with_cap_text')} rows) |")
    A(f"| Rules with payment rail | {t('rivo_with_payment_rail')} | 0 |")
    A(f"| Rules marked **unverified** | **{t('rivo_unverified')}** ({t('rivo_unverified')/rc*100:.0f}%) | n/a |")
    A(f"| Category rate cells | 0 | {t('savesage_category_cells')} |")
    A("")

    # ---- per-card --------------------------------------------------------
    A("## Per-card discrepancies\n")
    for x in sorted(high, key=lambda z: -(z["rules"]["savesage_count"] - z["rules"]["rivo_count"])):
        r, rr = x["rules"], RIVO[x["slug"]]
        s = SS[x["matched"][0]]
        A(f"### {x['name']}  \n`rivo:{x['slug']}` ↔ `savesage:{', '.join(x['matched'])}` (score {x['score']})\n")

        diffs = [(k, v) for k, v in x["fields"].items()
                 if v["state"] in ("CONFLICT", "rivo_missing", "savesage_missing")]
        if diffs:
            A("| Field | Rivo | SaveSage | |")
            A("|---|---|---|---|")
            for k, v in diffs:
                A(f"| `{k}` | {v['rivo']} | {v['savesage']} | {v['state']} |")
            A("")
        else:
            A("Scalar fields agree.\n")

        A(f"Earn rules — Rivo **{r['rivo_count']}**, SaveSage **{r['savesage_count']}** "
          f"(SaveSage states {r['savesage_stated_total']}). "
          f"Rivo MCC-tagged {r['rivo_with_mcc']}, capped {r['rivo_with_cap']}.\n")

        if r["savesage_count"] > r["rivo_count"]:
            rivo_cats = {str(y.get("category") or "").lower() for y in rr["earn_rules"]}
            rivo_mer = {m.lower() for y in rr["earn_rules"]
                        for m in (y.get("merchants") or []) if isinstance(m, str)}
            missing = [y for y in s["earn_rules"]
                       if not y["is_base_rate"]
                       and (y["merchant_raw"] or "").lower() not in rivo_mer
                       and not any((y["name"] or "").lower() in cc for cc in rivo_cats)]
            if missing:
                A(f"**{len(missing)} earn rules SaveSage has that Rivo appears to lack:**\n")
                A("| Rule | Rate | Category | Merchant |")
                A("|---|---|---|---|")
                for y in missing[:12]:
                    A(f"| {y['name']} | {y['rate']['value']}/₹{y['rate']['per']} "
                      f"| {y['category'] or '—'} | {y['merchant_raw'] or '—'} |")
                if len(missing) > 12:
                    A(f"| …{len(missing)-12} more | | | |")
                A("")
        if r["rivo_count"] > r["savesage_count"]:
            A(f"Rivo carries {r['rivo_count'] - r['savesage_count']} more rules here — "
              "likely MCC-split variants of one commercial rule.\n")
        if x["flags"]:
            A("Flags: " + "; ".join(f"**{f}**" for f in x["flags"]) + "\n")

    # ---- gaps ------------------------------------------------------------
    A("## Cards only in SaveSage\n")
    A(f"{len(CMP['savesage_only_slugs'])} HDFC cards SaveSage has that Rivo's catalogue does not:\n")
    for sl in CMP["savesage_only_slugs"]:
        s = SS[sl]
        A(f"- `{sl}` — {s['title']} · ₹{s['fees']['renewal']}/yr · "
          f"{len(s['earn_rules'])} rules"
          f"{' · not issuing' if s['flags']['is_currently_issuing'] is False else ''}")
    A("")
    A("## Cards only in Rivo\n")
    for x in none:
        A(f"- `{x['slug']}` — {x['name']}")
    A("")
    A("## Matches needing human review\n")
    for x in low:
        A(f"- `{x['slug']}` ({x['name']}) → `{', '.join(x['matched'])}` — score {x['score']}")
    A("")

    open(os.path.join(HERE, "HDFC_REPORT.md"), "w").write("\n".join(L))
    print(f"wrote HDFC_REPORT.md — {len(high)} high-confidence cards detailed, "
          f"{len(low)} flagged for review, {len(none)} rivo-only, "
          f"{len(CMP['savesage_only_slugs'])} savesage-only")


if __name__ == "__main__":
    main()
