#!/usr/bin/env python3
"""Cross-verify Rivo's card_catalogue against the SaveSage scrape.

SaveSage classified the same Indian card market independently, so where the two
agree a field is corroborated by a second source, and where they disagree one of
them is wrong. Neither is treated as authoritative: the output is a disagreement
list for a human, not a merge.

Read-only. Reads two JSON exports, writes a report.
"""
import json, os, re, sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher

HERE = os.path.dirname(os.path.abspath(__file__))
RIVO = os.path.join(HERE, "rivo_all.json")
SS = os.path.join(HERE, "..", "out", "cards.ndjson")

# Issuer names differ between the two sources; map Rivo's onto SaveSage's.
BANK_ALIAS = {
    "hdfc bank": "hdfc", "axis bank": "axis", "sbi bank": "sbi", "kotak bank": "kotak",
    "icici bank": "icici", "rbl bank": "rbl", "bank of baroda": "bob", "idfc first bank": "idfc",
    "indusind bank": "indusind", "yes bank": "yes-bank", "au small finance bank": "au",
    "federal bank": "federal", "standard chartered": "scb", "hsbc": "hsbc",
    "american express": "amex", "amex": "amex", "bobcard limited": "bob",
    "idbi bank": "idbi", "canara bank": "canara", "union bank of india": "union-bank",
    "punjab national bank": "pnb", "indian bank": "indian", "bank of india": "boi",
    "central bank of india": "central-bank", "uco bank": "uco", "csb bank": "csb",
    "dbs bank": "dbs", "dcb bank": "dcb", "bandhan bank": "bandhan-bank",
    "karur vysya bank": "kvb", "south indian bank": "south-indian", "sbm bank": "sbm",
    "equitas small finance bank": "equitas", "utkarsh small finance bank": "utkarsh",
    "jupiter": "jupiter", "onecard": "onecard", "slice": "slice",
}

NOISE = {"credit", "card", "the", "bank", "edition", "limited", "ltd"}
NET = {"visa", "rupay", "mastercard", "amex", "diners", "club", "metal", "plastic"}


def toks(s, drop_net=False):
    out = re.findall(r"[a-z0-9]+", (s or "").lower())
    drop = NOISE | (NET if drop_net else set())
    return [t for t in out if t not in drop]


def sim(a, b):
    ta, tb = set(toks(a, True)), set(toks(b, True))
    if not ta or not tb:
        return 0.0
    jac = len(ta & tb) / len(ta | tb)
    seq = SequenceMatcher(None, " ".join(sorted(ta)), " ".join(sorted(tb))).ratio()
    return max(jac, seq * 0.94)


def num(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


def close(a, b, tol=0.01):
    """Numeric agreement. Both-null counts as agreement; one-null does not."""
    if a is None and b is None:
        return "both_null"
    if a is None:
        return "rivo_missing"
    if b is None:
        return "savesage_missing"
    return "agree" if abs(a - b) <= tol else "CONFLICT"


def main():
    rivo = json.load(open(RIVO))
    ss = [json.loads(l) for l in open(SS)]

    by_bank = defaultdict(list)
    for c in ss:
        by_bank[c["issuer"]["slug"]].append(c)

    agg = Counter()
    rows, unmatched_rivo = [], []
    matched_ss = set()

    for r in rivo:
        bank = BANK_ALIAS.get((r.get("bank_name") or "").strip().lower())
        pool = by_bank.get(bank, [])
        if not pool:
            agg["no_issuer_in_savesage"] += 1
            unmatched_rivo.append((r["slug"], r.get("bank_name"), "issuer not in savesage"))
            continue

        # Network is a MATCHING signal, not a field to compare. SaveSage splits
        # a card per network (axis-airtel VISA / axis-airtel-rupay RUPAY) where
        # Rivo keeps one row, so scoring on name alone picks whichever variant
        # reads closest -- systematically the unsuffixed one. That produced 75
        # phantom "network conflicts", 40 of them one-directional.
        rnet0 = (r.get("network") or "").upper().replace(" ", "_")
        best, score = None, 0.0
        for cand in pool:
            sc = sim(r["name"], cand.get("display_name") or cand["title"])
            cnet = (cand.get("network") or "").upper()
            if rnet0 and cnet:
                # Tie-break toward the variant on the same network; never let
                # this manufacture a match that the name did not already support.
                sc += 0.06 if (rnet0.startswith(cnet[:4]) or cnet.startswith(rnet0[:4])) else -0.06
            if sc > score:
                best, score = cand, sc
        if not best or score < 0.62:
            agg["no_card_match"] += 1
            unmatched_rivo.append((r["slug"], r.get("bank_name"), f"best score {score:.2f}"))
            continue

        matched_ss.add(best["slug"])
        agg["matched"] += 1
        confident = score >= 0.75
        agg["matched_confident" if confident else "matched_weak"] += 1

        fields = {}
        for label, a, b in [
            ("annual_fee", num(r.get("annual_fee")), num(best["fees"]["renewal"])),
            ("joining_fee", num(r.get("joining_fee")), num(best["fees"]["joining"])),
            ("forex_markup_pct", num(r.get("forex_markup_pct")), num(best["fees"]["forex_markup_pct"])),
        ]:
            state = close(a, b)
            fields[label] = {"rivo": a, "savesage": b, "state": state}
            if confident:
                agg[f"{label}:{state}"] += 1

        rnet = (r.get("network") or "").upper().replace(" ", "_")
        snet = (best.get("network") or "").upper()
        # Rivo says "Diners", SaveSage "DINERS_CLUB" — prefix match, not equality.
        netstate = "both_null" if not rnet and not snet else (
            "agree" if rnet and snet and (rnet.startswith(snet[:4]) or snet.startswith(rnet[:4]))
            else "CONFLICT" if rnet and snet else "missing")
        fields["network"] = {"rivo": rnet, "savesage": snet, "state": netstate}
        if confident:
            agg[f"network:{netstate}"] += 1

        ss_rules = len(best["earn_rules"])
        rv_rules = r.get("rule_count") or 0
        if confident:
            agg["rules_rivo_total"] += rv_rules
            agg["rules_ss_total"] += ss_rules
            if ss_rules > rv_rules:
                agg["savesage_has_more_rules"] += 1
            elif rv_rules > ss_rules:
                agg["rivo_has_more_rules"] += 1

        rows.append({
            "rivo_slug": r["slug"], "name": r["name"], "bank": r.get("bank_name"),
            "savesage_slug": best["slug"], "score": round(score, 2), "confident": confident,
            "fields": fields,
            "rules": {"rivo": rv_rules, "savesage": ss_rules,
                      "savesage_stated": best["completeness"]["earn_rules_total"]},
            "counts": {
                "milestones": [r.get("milestone_count") or 0, len(best["milestones"])],
                "redemption": [r.get("redemption_count") or 0, 0],
                "lounge": [r.get("lounge_count") or 0, len(best["lounge"]["tiers"])],
            },
            "savesage_issuing": best["flags"]["is_currently_issuing"],
            "rivo_status": r.get("status"),
        })

    ss_only = [c for c in ss if c["slug"] not in matched_ss]

    out = {
        "totals": {
            "rivo": len(rivo), "savesage": len(ss),
            "matched": agg["matched"], "confident": agg["matched_confident"],
            "weak": agg["matched_weak"],
            "rivo_unmatched": len(unmatched_rivo), "savesage_only": len(ss_only),
        },
        "aggregate": dict(agg),
        "cards": rows,
        "rivo_unmatched": unmatched_rivo,
        "savesage_only": [{"slug": c["slug"], "title": c["title"],
                           "issuer": c["issuer"]["name"],
                           "fee": c["fees"]["renewal"],
                           "rules": len(c["earn_rules"]),
                           "issuing": c["flags"]["is_currently_issuing"]} for c in ss_only],
    }
    json.dump(out, open(os.path.join(HERE, "catalogue_verification.json"), "w"),
              ensure_ascii=False, indent=1)

    t = out["totals"]
    print(f"rivo {t['rivo']}  savesage {t['savesage']}")
    print(f"matched {t['matched']} ({t['confident']} confident, {t['weak']} weak) · "
          f"rivo unmatched {t['rivo_unmatched']} · savesage-only {t['savesage_only']}")
    print()
    for f in ("annual_fee", "joining_fee", "forex_markup_pct", "network"):
        parts = {k.split(":")[1]: v for k, v in agg.items() if k.startswith(f + ":")}
        tot = sum(parts.values()) or 1
        ok = parts.get("agree", 0) + parts.get("both_null", 0)
        print(f"  {f:<18} agree {ok:>3}/{tot:<3} ({ok/tot*100:4.0f}%)  "
              f"CONFLICT {parts.get('CONFLICT',0):>3}  "
              f"rivo_missing {parts.get('rivo_missing',0):>3}  "
              f"ss_missing {parts.get('savesage_missing',0):>3}")
    print()
    print(f"  earn rules — rivo {agg['rules_rivo_total']}  savesage {agg['rules_ss_total']}")
    print(f"  savesage has more on {agg['savesage_has_more_rules']} cards; "
          f"rivo has more on {agg['rivo_has_more_rules']}")


if __name__ == "__main__":
    main()
