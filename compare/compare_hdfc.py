#!/usr/bin/env python3
"""Compare Rivo's card_catalogue against the SaveSage scrape, for one issuer.

Two catalogues built by different people from different sources will disagree.
The point is not to pick a winner overall but to say, field by field, which
source is usable for merchant/MCC-level card suggestion.

Read-only: reads a JSON export, never touches the database.
"""
import json, os, re, sys
from collections import Counter
from difflib import SequenceMatcher

HERE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(HERE, "..", "out", "cards.ndjson")

# Tokens that carry no identity — issuer, product noise, and the network
# variants SaveSage splits on but Rivo folds into one card.
NOISE = {"hdfc", "bank", "credit", "card", "the", "edition"}
NETWORKS = {"visa", "rupay", "mastercard", "amex", "diners", "club",
            "metal", "plastic"}


def norm(s, drop_network=False):
    toks = re.findall(r"[a-z0-9]+", (s or "").lower())
    drop = NOISE | (NETWORKS if drop_network else set())
    return [t for t in toks if t not in drop]


def key(s, drop_network=False):
    return " ".join(sorted(set(norm(s, drop_network))))


def sim(a, b):
    ta, tb = set(norm(a, True)), set(norm(b, True))
    if not ta or not tb:
        return 0.0
    jac = len(ta & tb) / len(ta | tb)
    seq = SequenceMatcher(None, key(a, True), key(b, True)).ratio()
    return max(jac, seq * 0.95)          # jaccard leads; sequence breaks ties


def money(x):
    return None if x is None else float(x)


def rivo_rules(c):
    return c.get("earn_rules") or []


def rivo_rate(r):
    """Effective %, however this row happens to encode it."""
    if r.get("effective_rate_pct") is not None:
        return float(r["effective_rate_pct"])
    pps, spend = r.get("points_per_spend"), r.get("spend_amount")
    if pps and spend:
        return pps / spend * 100
    return None


def ss_rate(r):
    v, p = r["rate"]["value"], r["rate"]["per"] or 100
    return (v / p * 100) if v else None


def main():
    rivo = json.load(open(os.path.join(HERE, "rivo_hdfc.json")))
    ss = [c for c in (json.loads(l) for l in open(KB)) if c["issuer"]["slug"] == "hdfc"]

    # ---- match -----------------------------------------------------------
    pairs, used = [], set()
    for r in rivo:
        rname = f"{r['name']} {r.get('variant') or ''}"
        best = sorted(((sim(rname, s.get("display_name") or s["title"]), s) for s in ss),
                      key=lambda t: -t[0])
        top = [(sc, s) for sc, s in best if sc >= 0.6]
        if top:
            for sc, s in top:
                used.add(s["slug"])
            pairs.append({"rivo": r, "ss": [s for _, s in top],
                          "score": top[0][0]})
        else:
            pairs.append({"rivo": r, "ss": [], "score": best[0][0] if best else 0})
    unmatched_ss = [s for s in ss if s["slug"] not in used]

    # ---- per-card comparison --------------------------------------------
    rows, agg = [], Counter()
    for p in pairs:
        r, matches = p["rivo"], p["ss"]
        if not matches:
            agg["rivo_only"] += 1
            rows.append({"slug": r["slug"], "name": r["name"], "matched": None})
            continue
        s = matches[0]
        rr, sr = rivo_rules(r), s["earn_rules"]

        d = {
            "slug": r["slug"], "name": r["name"], "matched": [m["slug"] for m in matches],
            "score": round(p["score"], 2),
            "fields": {}, "rules": {}, "flags": [],
        }

        # scalar field disagreements
        for label, rv, sv in [
            ("annual_fee", money(r.get("annual_fee")), s["fees"]["renewal"]),
            ("joining_fee", money(r.get("joining_fee")), s["fees"]["joining"]),
            ("forex_markup_pct", money(r.get("forex_markup_pct")), s["fees"]["forex_markup_pct"]),
            ("network", (r.get("network") or "").upper() or None, s["network"]),
        ]:
            same = (rv == sv) if not (isinstance(rv, float) and isinstance(sv, (int, float))) \
                   else abs(rv - (sv or 0)) < 0.01
            if rv is None and sv is None:
                state = "both_null"
            elif rv is None:
                state = "rivo_missing"
            elif sv is None:
                state = "savesage_missing"
            elif same:
                state = "agree"
            else:
                state = "CONFLICT"
            agg[f"{label}:{state}"] += 1
            d["fields"][label] = {"rivo": rv, "savesage": sv, "state": state}

        # rule-level structure
        r_mcc = sum(1 for x in rr if x.get("mcc_includes") or x.get("mcc_excludes"))
        r_mer = sum(1 for x in rr if x.get("merchants") or x.get("merchant_ids"))
        r_cap = sum(1 for x in rr if x.get("cap_per_month") or x.get("cap_spend_per_month"))
        r_rail = sum(1 for x in rr if x.get("payment_rail"))
        r_unver = sum(1 for x in rr if x.get("confidence") == "unverified")
        s_mer = sum(1 for x in sr if x["merchant_raw"])
        s_cat = sum(1 for x in sr if x["category"])
        s_cap = sum(1 for x in sr if x["cap"])

        d["rules"] = {
            "rivo_count": len(rr), "savesage_count": len(sr),
            "savesage_stated_total": s["completeness"]["earn_rules_total"],
            "rivo_with_mcc": r_mcc, "rivo_with_merchant": r_mer,
            "rivo_with_cap": r_cap, "rivo_with_payment_rail": r_rail,
            "rivo_unverified": r_unver,
            "savesage_with_merchant": s_mer, "savesage_with_category": s_cat,
            "savesage_with_cap_text": s_cap,
            "savesage_category_cells": len(s.get("category_rates") or {}),
        }
        if len(rr) == 0:
            d["flags"].append("rivo has ZERO earn rules")
            agg["rivo_zero_rules"] += 1
        if r_mcc == 0 and len(rr):
            d["flags"].append("rivo rules carry no MCC")
            agg["rivo_no_mcc"] += 1
        if len(sr) > len(rr) * 1.5 and len(rr):
            d["flags"].append(f"savesage has {len(sr)} rules vs rivo {len(rr)}")
        if len(rr) > len(sr) * 1.5 and len(sr):
            d["flags"].append(f"rivo has {len(rr)} rules vs savesage {len(sr)}")
        if r.get("status") == "discontinued" and s["flags"]["is_currently_issuing"]:
            d["flags"].append("rivo says discontinued, savesage says still issuing")
            agg["status_conflict"] += 1
        if r.get("status") != "discontinued" and s["flags"]["is_currently_issuing"] is False:
            d["flags"].append("savesage says not issuing, rivo says active")
            agg["status_conflict"] += 1
        rows.append(d)

    out = {
        "issuer": "HDFC",
        "counts": {"rivo": len(rivo), "savesage": len(ss),
                   "matched": sum(1 for r in rows if r.get("matched")),
                   "rivo_only": agg["rivo_only"],
                   "savesage_only": len(unmatched_ss)},
        "savesage_only_slugs": [s["slug"] for s in unmatched_ss],
        "aggregate": dict(agg),
        "cards": rows,
    }
    json.dump(out, open(os.path.join(HERE, "hdfc_comparison.json"), "w"),
              ensure_ascii=False, indent=1)

    c = out["counts"]
    print(f"rivo {c['rivo']}  savesage {c['savesage']}  matched {c['matched']}  "
          f"rivo-only {c['rivo_only']}  savesage-only {c['savesage_only']}")
    for k in sorted(agg):
        if "CONFLICT" in k or k.startswith("rivo_") or k == "status_conflict":
            print(f"  {k}: {agg[k]}")


if __name__ == "__main__":
    main()
