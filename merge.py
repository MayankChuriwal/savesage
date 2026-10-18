#!/usr/bin/env python3
"""Stage 4: fold the calculator matrix into each card, and record where the
two independent views disagree.

The card pages and the reward calculator are separate systems on SaveSage's
side. Where they contradict each other we keep BOTH and flag it, because a
disagreement between two of their own sources is a finding, not a bug to
average away.
"""
import json, os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def main():
    matrix = json.load(open(os.path.join(OUT, "category_rate_matrix.json")))
    cards = [json.loads(l) for l in open(os.path.join(OUT, "cards.ndjson"))]

    disagreements = []
    for c in cards:
        m = matrix.get(c["slug"])
        if not m:
            c["category_rates"] = None
            continue
        c["category_rates"] = m["categories"]
        c["rate_summary"] = m["summary"]

        excluded = {(e.get("category") or e.get("name") or "").strip()
                    for e in c["exclusions"]}
        for cat, cell in m["categories"].items():
            if cat in excluded and not cell["earns_nothing"]:
                disagreements.append({
                    "slug": c["slug"], "category": cat,
                    "card_page_says": "excluded, earns nothing",
                    "calculator_says": f"{cell['effective_rate_pct']}% effective",
                    "reward_worth_inr": cell["reward_worth_inr"],
                    "spend_tested": cell["spend_tested"],
                })
        c["completeness"]["categories_tested"] = m["summary"]["categories_tested"]
        c["completeness"]["categories_earning"] = m["summary"]["categories_earning"]

    with open(os.path.join(OUT, "cards.ndjson"), "w") as f:
        for c in cards:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    json.dump(cards, open(os.path.join(OUT, "cards.json"), "w"), ensure_ascii=False, indent=1)
    for c in cards:
        json.dump(c, open(os.path.join(OUT, "cards", f"{c['slug']}.json"), "w"),
                  ensure_ascii=False, indent=1)
    json.dump(disagreements, open(os.path.join(OUT, "source_disagreements.json"), "w"),
              ensure_ascii=False, indent=1)

    print(f"merged matrix into {sum(1 for c in cards if c['category_rates'])}/{len(cards)} cards")
    print(f"disagreements: {len(disagreements)} across "
          f"{len({d['slug'] for d in disagreements})} cards")
    print("by category:", dict(Counter(d["category"] for d in disagreements).most_common(6)))


if __name__ == "__main__":
    main()
