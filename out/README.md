# SaveSage credit-card knowledge base

Scraped from `savesage.club` / `api.savesage.club`, public unauthenticated
endpoints only. 727 unique cards, 40 issuers, 24 collections.

See `report.md` for acceptance metrics and data-quality findings.

## Files

| File | What |
|---|---|
| `cards.json` | All 727 cards, one array. Pretty-printed. |
| `cards.ndjson` | Same, one card per line. Use this for pipelines. |
| `cards/<slug>.json` | One file per card, human-diffable. |
| `category_rate_matrix.json` | 727 cards x 16 categories: effective rate, points, point value. |
| `best_card_per_category.json` | Best card per category, recovered from the calculator. |
| `banks.json` | 40 issuers, full membership. |
| `collections.json` | 24 collections. `defined_by` says whose definition it is. |
| `taxonomy_dictionary.json` | rule name -> category/subcategory/merchant, plus conflicts. |
| `source_disagreements.json` | Where the card page and the calculator contradict each other. |
| `report.md` | Acceptance report. |

## Provenance

Every earn-rule field says where it came from. Never guessed — unknown is `null`.

| Value | Meaning |
|---|---|
| `api` | SaveSage returned it structured |
| `parsed` | read deterministically off their prose |
| `dictionary` | their own label for this rule name, harvested from a card where it was unhidden |
| `name_matches_taxonomy` | the rule name is itself one of their category labels |
| `parsed_from_name` | split out of "<Merchant> via <Channel>" |
| `inferred_card_unit` | reward unit taken from the card's own visible rows |
| `null` | unknown |

`is_base_rate: true` marks the everyday rate. It has no category by nature, not by omission.

## Rebuilding

`python3 build.py` re-derives everything in `out/` from `raw/`. Only the report's
spot-check touches the network. `raw/` holds every original response, so the
schema can change without re-crawling.

## Caveats

- Caps and minimum-spend thresholds exist only on rows SaveSage left unhidden.
  Detecting the rest needs a second calculator sweep at a higher spend amount.
- `category_rate_matrix` was measured at a single ₹10,000 spend, so it reflects
  the uncapped rate.
- `forexMarkupPercent` is null on 26 cards. Unknown, not zero.
- 4 duplicate slugs in their catalogue: 731 rows, 727 unique cards.
