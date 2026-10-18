#!/usr/bin/env python3
"""Stage 2b: reward-calculator sweep -> per-card category rate matrix.

Everything here is arithmetic on their numbers, not inference:
  effective_rate_pct = rewardWorth / spendAmount * 100
  points_per_100     = rewardPoints / spendAmount * 100
  point_value_inr    = rewardWorth / rewardPoints      (when points > 0)

A category returning 0 is an earn exclusion for that card, confirmed
independently of the card page's own exclusions list.
"""
import json, os, glob
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw", "calc")
OUT = os.path.join(HERE, "out")


def r2(x):
    return None if x is None else round(x + 0.0, 4)


def main():
    by_card = defaultdict(dict)
    best_by_cat = defaultdict(lambda: defaultdict(int))
    errors = []

    for f in glob.glob(os.path.join(RAW, "*", "*.json")):
        try:
            d = json.load(open(f))
        except (ValueError, OSError) as e:
            errors.append((f, str(e))); continue
        if d.get("status") != 200 or "response" not in d:
            errors.append((f, f"status={d.get('status')}")); continue

        r = d["response"]
        u = r.get("userCard") or {}
        spend = d["spendAmount"] or 0
        worth, pts = u.get("rewardWorth"), u.get("rewardPoints")
        cat = d["categorySlug"]

        by_card[d["cardId"]][cat] = {
            "effective_rate_pct": r2(worth / spend * 100) if (worth is not None and spend) else None,
            "points_per_100": r2(pts / spend * 100) if (pts is not None and spend) else None,
            "reward_worth_inr": worth,
            "reward_points": pts,
            "point_value_inr": r2(worth / pts) if (pts and worth is not None) else None,
            "is_cashback": u.get("isCashbackCard"),
            "earns_nothing": (worth == 0),
            "spend_tested": spend,
        }
        s = r.get("suggestedCard") or {}
        if s.get("cardId"):
            best_by_cat[cat][s["cardId"]] += 1

    # resolve every id we saw to a slug from the catalogue snapshot
    id_to_slug = {}
    for f in glob.glob(os.path.join(HERE, "raw", "list", "*.json")):
        for c in json.load(open(f)).get("cards", []):
            id_to_slug[c["id"]] = c["slug"]

    matrix = {}
    for cid, cats in by_card.items():
        rates = [v["effective_rate_pct"] for v in cats.values() if v["effective_rate_pct"] is not None]
        pvs = [v["point_value_inr"] for v in cats.values() if v["point_value_inr"]]
        matrix[id_to_slug.get(cid, f"unknown-{cid}")] = {
            "card_id": cid,
            "categories": cats,
            "summary": {
                "categories_tested": len(cats),
                "categories_earning": sum(1 for v in cats.values() if not v["earns_nothing"]),
                "max_rate_pct": max(rates) if rates else None,
                "base_rate_pct": min([x for x in rates if x > 0], default=None),
                "point_value_inr": max(set(pvs), key=pvs.count) if pvs else None,
            },
        }

    best = {cat: [{"card_id": cid, "slug": id_to_slug.get(cid), "times_suggested": n}
                  for cid, n in sorted(ids.items(), key=lambda kv: -kv[1])]
            for cat, ids in best_by_cat.items()}

    os.makedirs(OUT, exist_ok=True)
    json.dump(matrix, open(os.path.join(OUT, "category_rate_matrix.json"), "w"),
              ensure_ascii=False, indent=1)
    json.dump(best, open(os.path.join(OUT, "best_card_per_category.json"), "w"),
              ensure_ascii=False, indent=1)
    print(f"matrix: {len(matrix)} cards, {sum(len(v['categories']) for v in matrix.values())} cells, "
          f"{len(errors)} errors")
    if errors[:3]:
        print("sample errors:", errors[:3])


if __name__ == "__main__":
    main()
