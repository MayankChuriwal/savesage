# SaveSage credit-card scrape — acceptance report

Source: `savesage.club` / `api.savesage.club`, public unauthenticated endpoints only.

## 1. Completeness

- Cards in sitemap/catalogue: **727**
- Cards parsed: **727**
- Missing: **0** 
- Parse failures: **0**
- Rate-parse misses: **0**

### Earn rules — the app-wall test

- Rules emitted: **3729**
- Rules SaveSage states exist: **3729**
- **Recovered: 100%** (1505 returned structured, 2224 recovered from prose)

## 2. Field coverage

| Field | Cards with a value |
|---|---|
| `title` | 727/727 (100.0%) |
| `overview` | 727/727 (100.0%) |
| `network` | 727/727 (100.0%) |
| `return_percentage` | 727/727 (100.0%) |
| `fees.renewal` | 719/727 (98.9%) |
| `fees.forex_markup_pct` | 697/727 (95.9%) |
| `exclusions` | 672/727 (92.4%) |
| `fees.apr_pct` | 590/727 (81.2%) |
| `milestones` | 500/727 (68.8%) |
| `best_suited` | 489/727 (67.3%) |
| `benefits` | 481/727 (66.2%) |
| `fees.joining` | 469/727 (64.5%) |
| `lounge.tiers` | 380/727 (52.3%) |
| `apply_link` | 265/727 (36.5%) |

### Earn-rule field provenance

Base-rate rows (698) are excluded — they legitimately have no category.

| Field | Coverage | Breakdown |
|---|---|---|
| `rate` | 3729/3729 (100.0%) | {'api': 1505, 'parsed': 2224} |
| `category` | 2146/3031 (70.8%) | {'api': 479, 'dictionary': 1360, 'null': 885, 'name_matches_taxonomy': 307} |
| `merchant_raw` | 794/3031 (26.2%) | {'null': 2237, 'api': 285, 'dictionary': 425, 'parsed_from_name': 84} |

## 3. What the app-wall still costs

| Data | Have | SaveSage states | Note |
|---|---|---|---|
| Earn rules | 3729 | 3729 | names + rates fully recovered |
| Benefits (structured) | 794 | 1574 | rest available as prose only |
| Lounge (structured) | 450 | 693 | all tiers available as prose |
| Milestones | 1305 | — | never gated, fully structured |

## 4. Spot-check against live pages

Re-fetched 12 random cards and diffed. **12/12 exact.**

| Card | Result | Detail |
|---|---|---|
| `indusind-avios-visa-infinite` | OK | 11 rules |
| `indusind-legend` | OK | 7 rules |
| `dbs-5x-supercard` | OK | 2 rules |
| `axis-my-zone-rupay` | OK | 1 rules |
| `axis-freecharge` | OK | 1 rules |
| `hdfc-paytm-mobile` | OK | 3 rules |
| `sbm-credilio-novio-rupay-fd` | OK | 6 rules |
| `sbi-irctc-platinum` | OK | 2 rules |
| `bob-vikram` | OK | 5 rules |
| `federal-starbiz` | OK | 1 rules |
| `hdfc-regalia-gold` | OK | 20 rules |
| `rbl-world-plus-mastercard` | OK | 3 rules |

## 5. Category rate matrix (reward calculator)

A second, independent view of the same cards: every card asked what a fixed ₹10,000 spend earns in each of SaveSage's 16 standard categories. This is arithmetic on their numbers, not inference — and it covers every card uniformly, including the rules the app-wall hides.

- Cards covered: **727/727**
- Cells: **11632** (card × category), **0** failures
- Cards with a derived point value: **645**
- Most common point values: {0.25: 338, 1.0: 118, 0.2: 38, 0.5: 28, 1.2: 12, 0.1: 12}
- Cards earning nothing in all 16 categories: **17**

### Cross-validation against the card pages

Where a card page lists a category as an exclusion, does the calculator agree it earns nothing?

- Comparable pairs: **3120**
- **Agree: 3064 (98.2%)**
- Disagree: 56 (1.8%), across 40 cards — see `source_disagreements.json`
- Disagreements by category: {'Utilities': 15, 'Fuel': 10, 'Education': 6, 'UPI': 6, 'Insurance': 6, 'Rent': 5}

Both readings are preserved per card. Two of their own systems contradicting each other is a finding to surface, not something to average away.

## 6. Data-quality findings in SaveSage's own data

- **23 rule names carry conflicting labels** across cards (same rule name, different category/merchant). Majority wins; all alternatives kept in `taxonomy_dictionary.json`.
- `zero-forex-markup` collection includes cards charging up to 1.99% markup. Reproduced faithfully; `true-zero-forex` (ours) holds the 31 that are actually 0%.
- Category vocabulary is inconsistent: `GiftCards`/`Gift Cards`, `Online`/`Online Shopping`, and a literal `TRUE` as a category value. Folded on read; originals preserved in `raw/`.
- Catalogue reports 731 rows for 727 unique slugs — 4 duplicates.
- `redemption-options` tab returns no data for any card; it is an app advert. Dropped.