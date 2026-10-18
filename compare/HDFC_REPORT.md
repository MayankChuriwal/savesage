# HDFC — Rivo `card_catalogue` vs SaveSage scrape

Rivo **50** cards · SaveSage **82** · matched **44** (38 high-confidence, 6 need review) · Rivo-only **6** · SaveSage-only **22**

Matching is by normalized name, since SaveSage splits network variants (`hdfc-millennia-visa`/`-rupay`) that Rivo folds into one card. Matches below 0.75 are listed separately and should not be trusted.

## Structural coverage (high-confidence matches only)

| | Rivo | SaveSage |
|---|---|---|
| Earn rules | 307 | 415 |
| Rules with **MCC codes** | **116** (38%) | **0** (none exist) |
| Rules with merchant | 230 (75%) | 204 (49%) |
| Rules with **numeric cap** | **223** (73%) | 0 (prose only, 50 rows) |
| Rules with payment rail | 24 | 0 |
| Rules marked **unverified** | **279** (91%) | n/a |
| Category rate cells | 0 | 608 |

## Per-card discrepancies

### SWIGGY BLCK  
`rivo:hdfc-swiggy-blck` ↔ `savesage:hdfc-swiggy-blck` (score 0.75)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | MASTERCARD | VISA | CONFLICT |

Earn rules — Rivo **5**, SaveSage **25** (SaveSage states 25). Rivo MCC-tagged 4, capped 4.

**13 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Ibibo | 5/₹100 | — | — |
| Vijay Sales | 5/₹100 | — | — |
| Reliance Digital | 5/₹100 | — | Reliance Digital |
| Netflix | 5/₹100 | — | — |
| Sony LIV | 5/₹100 | — | — |
| Prime | 5/₹100 | — | — |
| Ixigo | 5/₹100 | — | — |
| Yatra | 5/₹100 | — | — |
| EaseMyTrip | 5/₹100 | — | — |
| Myntra | 5/₹100 | Online | Myntra |
| Pharmeasy | 5/₹100 | — | — |
| Insurance | 1/₹100 | Insurance | — |
| …1 more | | | |

Flags: **savesage has 25 rules vs rivo 5**

### SWIGGY ORNGE  
`rivo:hdfc-swiggy-ornge` ↔ `savesage:hdfc-swiggy-ornge` (score 0.76)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | MASTERCARD | VISA | CONFLICT |

Earn rules — Rivo **6**, SaveSage **25** (SaveSage states 25). Rivo MCC-tagged 4, capped 5.

**13 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Prime | 5/₹100 | — | — |
| Myntra | 5/₹100 | Online | Myntra |
| Pharmeasy | 5/₹100 | — | — |
| Vijay Sales | 5/₹100 | — | — |
| Reliance Digital | 5/₹100 | — | Reliance Digital |
| Netflix | 5/₹100 | — | — |
| EaseMyTrip | 5/₹100 | — | — |
| Ibibo | 5/₹100 | — | — |
| Sony LIV | 5/₹100 | — | — |
| Yatra | 5/₹100 | — | — |
| Ixigo | 5/₹100 | — | — |
| Utilities | 1/₹100 | Utilities | — |
| …1 more | | | |

Flags: **savesage has 25 rules vs rivo 6**

### SWIGGY  
`rivo:swiggy-hdfc-bank` ↔ `savesage:hdfc-swiggy, hdfc-swiggy-blck, hdfc-swiggy-ornge` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | MASTERCARD | VISA | CONFLICT |

Earn rules — Rivo **3**, SaveSage **16** (SaveSage states 16). Rivo MCC-tagged 2, capped 2.

**8 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Ajio | 5/₹100 | Online | Ajio via Amex Rewards Multiplier |
| Meesho | 5/₹100 | — | — |
| Amazon Fresh | 5/₹100 | — | — |
| Flipkart (Minutes) | 5/₹100 | — | — |
| Nykaa | 5/₹100 | — | — |
| Utilities | 1/₹100 | Utilities | — |
| Insurance | 1/₹100 | Insurance | — |
| Education | 1/₹100 | Education | — |

Flags: **savesage has 16 rules vs rivo 3**; **savesage says not issuing, rivo says active**

### REGALIA  
`rivo:hdfc-bank-regalia` ↔ `savesage:hdfc-regalia, hdfc-regalia-gold, hdfc-regalia-first, hdfc-regalia-activ, hdfc-regalia-activ-rupay, hdfc-retailio` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | VISA | MASTERCARD | CONFLICT |

Earn rules — Rivo **1**, SaveSage **12** (SaveSage states 12). Rivo MCC-tagged 1, capped 0.

**11 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Jockey via SmartBuy | 40/₹200 | — | Jockey via SmartBuy |
| Hotels via SmartBuy | 40/₹200 | Online | Hotels via SmartBuy |
| PharmEasy via SmartBuy | 40/₹200 | — | PharmEasy via SmartBuy |
| Flights via SmartBuy | 20/₹200 | — | Flights |
| Myntra via SmartBuy | 20/₹200 | — | Myntra |
| Duty Free (Adani One) via Smartbuy | 20/₹200 | — | Duty Free (Adani One) |
| MMT via SmartBuy | 20/₹200 | — | MMT |
| RedBus via SmartBuy | 20/₹200 | — | RedBus |
| Gift Cards via SmartBuy | 20/₹200 | GiftCards | Gift Cards via SmartBuy |
| Retail | 4/₹200 | Shopping | — |
| Insurance | 4/₹200 | Insurance | — |

Flags: **savesage has 12 rules vs rivo 1**

### HDFC Bank BizPower Credit Card  
`rivo:hdfc-bizpower` ↔ `savesage:hdfc-biz-power` (score 0.89)

Scalar fields agree.

Earn rules — Rivo **16**, SaveSage **25** (SaveSage states 25). Rivo MCC-tagged 0, capped 0.

**23 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Hotels via SmartBuy | 50/₹200 | — | Hotels via SmartBuy |
| PharmEasy via SmartBuy | 50/₹200 | — | PharmEasy via SmartBuy |
| IGP via SmartBuy | 50/₹200 | — | IGP via SmartBuy |
| Jockey via SmartBuy | 50/₹200 | — | Jockey via SmartBuy |
| Drivado via SmartBuy | 25/₹200 | — | Drivado |
| GoogleAds | 25/₹200 | — | — |
| Nuclei via SmartBuy | 25/₹200 | — | Nuclei |
| Reliance Digital | 25/₹200 | — | Reliance Digital |
| PayZapp | 25/₹200 | — | — |
| Flights via SmartBuy | 25/₹200 | — | Flights |
| Redbus via SmartBuy | 25/₹200 | — | Redbus |
| Gift Cards via SmartBuy | 25/₹200 | GiftCards | Gift Cards via SmartBuy |
| …11 more | | | |

Flags: **rivo rules carry no MCC**; **savesage has 25 rules vs rivo 16**

### PIXEL PLAY  
`rivo:hdfc-bank-pixel-play` ↔ `savesage:hdfc-pixel-play, hdfc-pixel-play-rupay` (score 1.0)

Scalar fields agree.

Earn rules — Rivo **5**, SaveSage **14** (SaveSage states 14). Rivo MCC-tagged 2, capped 4.

**3 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Reliance Smart Bazaar | 5/₹100 | — | — |
| MakeMyTrip | 5/₹100 | Travel | MakeMyTrip via Amex Rewards Multiplier |
| Nykaa | 5/₹100 | — | — |

Flags: **savesage has 14 rules vs rivo 5**

### FREEDOM  
`rivo:hdfc-freedom` ↔ `savesage:hdfc-freedom` (score 1.0)

Scalar fields agree.

Earn rules — Rivo **2**, SaveSage **10** (SaveSage states 10). Rivo MCC-tagged 2, capped 1.

**4 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| UPI | 1/₹200 | UPI | — |
| Utilities | 1/₹200 | Utilities | — |
| Education | 1/₹200 | Education | — |
| Telecom & Cables | 1/₹200 | Telecom & Cable | — |

Flags: **savesage has 10 rules vs rivo 2**

### MONEYBACK PLUS  
`rivo:hdfc-moneyback-plus` ↔ `savesage:hdfc-moneyback-plus, hdfc-moneyback` (score 1.0)

Scalar fields agree.

Earn rules — Rivo **2**, SaveSage **9** (SaveSage states 9). Rivo MCC-tagged 2, capped 1.

**4 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Reliance Smart | 20/₹200 | — | — |
| Grocery | 2/₹200 | F&B | — |
| UPI | 2/₹200 | UPI | — |
| Education | 2/₹200 | Education | — |

Flags: **savesage has 9 rules vs rivo 2**

### INFINIA METAL  
`rivo:hdfc-infinia-metal` ↔ `savesage:hdfc-infinia-metal, hdfc-infinia-plastic` (score 1.0)

Scalar fields agree.

Earn rules — Rivo **14**, SaveSage **20** (SaveSage states 20). Rivo MCC-tagged 5, capped 13.

**16 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| IGP via SmartBuy | 50/₹150 | — | IGP via SmartBuy |
| PharmEasy via SmartBuy | 50/₹150 | — | PharmEasy via SmartBuy |
| Jockey via SmartBuy | 50/₹150 | — | Jockey via SmartBuy |
| Hotels via SmartBuy | 50/₹150 | Travel | Hotels via SmartBuy |
| Apple via SmartBuy | 25/₹150 | — | Apple |
| RedBus via SmartBuy | 25/₹150 | — | RedBus |
| Holidays via SmartBuy | 25/₹150 | — | Holidays |
| Gift Cards via SmartBuy | 25/₹150 | GiftCards | Gift Cards via SmartBuy |
| Duty Free (Adani One) via Smartbuy | 25/₹150 | — | Duty Free (Adani One) |
| Trains via SmartBuy | 15/₹150 | — | Trains via SmartBuy |
| Insurance | 5/₹150 | Insurance | — |
| International | 5/₹150 | International | — |
| …4 more | | | |

### DINERS CLUB BLACK METAL  
`rivo:hdfc-diners-club-black-metal-edition` ↔ `savesage:hdfc-diners-club-black-metal, hdfc-diners-club-black, hdfc-biz-black-metal` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | DINERS | DINERS_CLUB | CONFLICT |

Earn rules — Rivo **15**, SaveSage **20** (SaveSage states 20). Rivo MCC-tagged 5, capped 13.

**17 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| PharmEasy via SmartBuy | 50/₹150 | — | PharmEasy via SmartBuy |
| Hotels via SmartBuy | 50/₹150 | Travel | Hotels via SmartBuy |
| IGP via SmartBuy | 50/₹150 | — | IGP via SmartBuy |
| Jockey via SmartBuy | 50/₹150 | — | Jockey via SmartBuy |
| RedBus via SmartBuy | 25/₹150 | — | RedBus |
| Duty Free (Adani One) via Smartbuy | 25/₹150 | — | Duty Free (Adani One) |
| Holidays via SmartBuy | 25/₹150 | — | Holidays |
| Apple via SmartBuy | 25/₹150 | — | Apple |
| Trains via SmartBuy | 15/₹150 | — | Trains via SmartBuy |
| Gift Cards via SmartBuy | 15/₹150 | GiftCards | Gift Cards via SmartBuy |
| Dining (Weekends) | 10/₹150 | — | — |
| Utilities | 5/₹150 | Utilities | — |
| …5 more | | | |

### DINERS CLUB BLACK  
`rivo:hdfc-diners-club-black` ↔ `savesage:hdfc-diners-club-black-metal, hdfc-diners-club-black, hdfc-biz-black-metal` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | DINERS | DINERS_CLUB | CONFLICT |

Earn rules — Rivo **15**, SaveSage **20** (SaveSage states 20). Rivo MCC-tagged 5, capped 13.

**17 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| PharmEasy via SmartBuy | 50/₹150 | — | PharmEasy via SmartBuy |
| Hotels via SmartBuy | 50/₹150 | Travel | Hotels via SmartBuy |
| IGP via SmartBuy | 50/₹150 | — | IGP via SmartBuy |
| Jockey via SmartBuy | 50/₹150 | — | Jockey via SmartBuy |
| RedBus via SmartBuy | 25/₹150 | — | RedBus |
| Duty Free (Adani One) via Smartbuy | 25/₹150 | — | Duty Free (Adani One) |
| Holidays via SmartBuy | 25/₹150 | — | Holidays |
| Apple via SmartBuy | 25/₹150 | — | Apple |
| Trains via SmartBuy | 15/₹150 | — | Trains via SmartBuy |
| Gift Cards via SmartBuy | 15/₹150 | GiftCards | Gift Cards via SmartBuy |
| Dining (Weekends) | 10/₹150 | — | — |
| Utilities | 5/₹150 | Utilities | — |
| …5 more | | | |

### DOCTORS REGALIA  
`rivo:hdfc-doctors-regalia` ↔ `savesage:hdfc-doctors-regalia, hdfc-doctors-superia, hdfc-regalia-first, hdfc-regalia-activ, hdfc-regalia-activ-rupay, hdfc-regalia-gold, hdfc-regalia` (score 0.86)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `forex_markup_pct` | 2.0 | 3.5 | CONFLICT |
| `network` | None | VISA | rivo_missing |

Earn rules — Rivo **1**, SaveSage **5** (SaveSage states 5). Rivo MCC-tagged 1, capped 0.

**4 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Insurance | 4/₹150 | Insurance | — |
| Education | 4/₹150 | Education | — |
| Utilities | 4/₹150 | Utilities | — |
| Rent | 4/₹150 | Rent | — |

Flags: **savesage has 5 rules vs rivo 1**

### DINERS CLUB PREMIUM  
`rivo:hdfc-diners-club-premium` ↔ `savesage:hdfc-diners-club-premium` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `forex_markup_pct` | 2.0 | 3.5 | CONFLICT |
| `network` | DINERS | DINERS_CLUB | CONFLICT |

Earn rules — Rivo **1**, SaveSage **5** (SaveSage states 5). Rivo MCC-tagged 1, capped 0.

**4 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Utilities | 4/₹200 | Utilities | — |
| Wallets | 4/₹200 | Wallets | — |
| Insurance | 4/₹200 | Insurance | — |
| Education | 4/₹200 | Education | — |

Flags: **savesage has 5 rules vs rivo 1**

### SUPERIA  
`rivo:hdfc-superia` ↔ `savesage:hdfc-superia, hdfc-doctors-superia` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | None | VISA | rivo_missing |

Earn rules — Rivo **2**, SaveSage **6** (SaveSage states 6). Rivo MCC-tagged 1, capped 0.

**5 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Utilities | 3/₹200 | Utilities | — |
| Insurance | 3/₹200 | Insurance | — |
| Rent | 3/₹200 | Rent | — |
| Wallets | 3/₹200 | Wallets | — |
| Education | 3/₹200 | Education | — |

Flags: **savesage has 6 rules vs rivo 2**

### MARRIOTT BONVOY  
`rivo:marriott-bonvoy-hdfc-bank` ↔ `savesage:hdfc-marriott-bonvoy` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | DINERS | VISA | CONFLICT |

Earn rules — Rivo **3**, SaveSage **6** (SaveSage states 6). Rivo MCC-tagged 1, capped 0.

**2 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Marriott Hotels | 8/₹150 | Travel | Marriott |
| Grocery | 2/₹150 | F&B | — |

Flags: **savesage has 6 rules vs rivo 3**

### BIZBLACK METAL  
`rivo:hdfc-bizblack-metal` ↔ `savesage:hdfc-biz-black-metal, hdfc-diners-club-black-metal, hdfc-diners-club-black` (score 0.89)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | DINERS | VISA | CONFLICT |

Earn rules — Rivo **19**, SaveSage **22** (SaveSage states 22). Rivo MCC-tagged 6, capped 18.

**17 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Hotels via SmartBuy | 50/₹150 | Travel | Hotels via SmartBuy |
| Jockey via SmartBuy | 50/₹150 | — | Jockey via SmartBuy |
| IGP via SmartBuy | 50/₹150 | — | IGP via SmartBuy |
| PharmEasy via SmartBuy | 50/₹150 | — | PharmEasy via SmartBuy |
| Redbus via SmartBuy | 25/₹150 | — | Redbus |
| Holidays via SmartBuy | 25/₹150 | — | Holidays |
| Government | 25/₹150 | Government | — |
| Apple via SmartBuy | 25/₹150 | — | Apple |
| Duty Free (Adani One) via Smartbuy | 25/₹150 | — | Duty Free (Adani One) |
| MakeMyTrip MyBiz | 25/₹150 | Travel | MakeMyTrip |
| Nuclei via SmartBuy | 25/₹150 | — | Nuclei |
| Gift Cards via SmartBuy | 15/₹150 | GiftCards | Gift Cards via SmartBuy |
| …5 more | | | |

### DINERS CLUB PRIVILEGE  
`rivo:hdfc-diners-club-privilege` ↔ `savesage:hdfc-diners-club-privilege` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | DINERS | DINERS_CLUB | CONFLICT |

Earn rules — Rivo **15**, SaveSage **18** (SaveSage states 18). Rivo MCC-tagged 6, capped 14.

**13 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Hotels via SmartBuy | 40/₹200 | Travel | Hotels via SmartBuy |
| IGP via SmartBuy | 40/₹200 | — | IGP via SmartBuy |
| PharmEasy via SmartBuy | 40/₹200 | — | PharmEasy via SmartBuy |
| Jockey via SmartBuy | 40/₹200 | — | Jockey via SmartBuy |
| Duty Free (Adani One) via Smartbuy | 20/₹200 | — | Duty Free (Adani One) |
| RedBus via SmartBuy | 20/₹200 | — | RedBus |
| Holidays via SmartBuy | 20/₹200 | — | Holidays |
| Gift Cards via SmartBuy | 20/₹200 | GiftCards | Gift Cards via SmartBuy |
| Apple via SmartBuy | 20/₹200 | — | Apple |
| Trains via SmartBuy | 12/₹200 | — | Trains via SmartBuy |
| Utilities & Telecom | 4/₹200 | — | — |
| Insurance | 4/₹200 | Insurance | — |
| …1 more | | | |

### SOLITAIRE  
`rivo:hdfc-bank-solitaire` ↔ `savesage:hdfc-solitaire` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `forex_markup_pct` | None | 3.5 | rivo_missing |
| `network` | None | VISA | rivo_missing |

Earn rules — Rivo **2**, SaveSage **4** (SaveSage states 4). Rivo MCC-tagged 1, capped 0.

**1 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Fuel | 4.5/₹200 | Fuel | — |

Flags: **savesage has 4 rules vs rivo 2**

### BHARAT  
`rivo:hdfc-bharat` ↔ `savesage:hdfc-bharat` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `forex_markup_pct` | None | 3.5 | rivo_missing |
| `network` | None | RUPAY | rivo_missing |

Earn rules — Rivo **4**, SaveSage **6** (SaveSage states 6). Rivo MCC-tagged 2, capped 3.

**2 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Bill Payment & Recharges | 5/₹100 | — | — |
| PayZapp/EasyEMI/SmartBUY/SmartPay | 5/₹100 | — | — |

### REGALIA GOLD  
`rivo:hdfc-regalia-gold` ↔ `savesage:hdfc-regalia-gold, hdfc-regalia, hdfc-doctors-regalia, hdfc-regalia-first, hdfc-regalia-activ, hdfc-regalia-activ-rupay` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | MASTERCARD | VISA | CONFLICT |

Earn rules — Rivo **18**, SaveSage **20** (SaveSage states 20). Rivo MCC-tagged 7, capped 17.

**13 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Jockey via SmartBuy | 50/₹200 | — | Jockey via SmartBuy |
| PharmEasy via SmartBuy | 50/₹200 | — | PharmEasy via SmartBuy |
| IGP via SmartBuy | 50/₹200 | — | IGP via SmartBuy |
| Hotels via SmartBuy | 50/₹200 | Travel | Hotels via SmartBuy |
| Gift Cards via SmartBuy | 25/₹200 | GiftCards | Gift Cards via SmartBuy |
| Apple via SmartBuy | 25/₹200 | — | Apple |
| Duty Free (Adani One) via Smartbuy | 25/₹200 | — | Duty Free (Adani One) |
| Holidays via SmartBuy | 25/₹200 | — | Holidays |
| RedBus via SmartBuy | 25/₹200 | — | RedBus |
| Trains via SmartBuy | 15/₹200 | — | Trains via SmartBuy |
| Insurance | 5/₹200 | Insurance | — |
| Utilities | 5/₹200 | Utilities | — |
| …1 more | | | |

### IRCTC  
`rivo:irctc-hdfc-bank` ↔ `savesage:hdfc-irctc` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | RUPAY | VISA | CONFLICT |

Earn rules — Rivo **3**, SaveSage **4** (SaveSage states 4). Rivo MCC-tagged 1, capped 2.

**2 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| IRCTC via SmartBuy | 5/₹100 | Online | IRCTC via SmartBuy |
| Grocery | 1/₹100 | F&B | — |

### PLATINUM EDGE  
`rivo:hdfc-platinum-edge` ↔ `savesage:hdfc-platinum-edge, hdfc-corporate-platinum` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | None | VISA | rivo_missing |

Earn rules — Rivo **2**, SaveSage **3** (SaveSage states 3). Rivo MCC-tagged 2, capped 0.

**2 earn rules SaveSage has that Rivo appears to lack:**

| Rule | Rate | Category | Merchant |
|---|---|---|---|
| Wallets | 2/₹150 | Wallets | — |
| Insurance | 2/₹150 | Insurance | — |

### SHOPPERS STOP  
`rivo:shoppers-stop-hdfc-bank` ↔ `savesage:hdfc-shoppers-stop, hdfc-shoppers-stop-black` (score 1.0)

Scalar fields agree.

Earn rules — Rivo **3**, SaveSage **3** (SaveSage states 3). Rivo MCC-tagged 1, capped 0.

### TEACHERS PLATINUM  
`rivo:hdfc-teachers-platinum` ↔ `savesage:hdfc-teachers-platinum, hdfc-times-platinum` (score 0.87)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | None | VISA | rivo_missing |

Earn rules — Rivo **2**, SaveSage **2** (SaveSage states 2). Rivo MCC-tagged 1, capped 0.

### DINERS CLUB REWARDZ  
`rivo:hdfc-diners-club-rewardz` ↔ `savesage:hdfc-diners-club-rewardz` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | DINERS | DINERS_CLUB | CONFLICT |

Earn rules — Rivo **1**, SaveSage **1** (SaveSage states 1). Rivo MCC-tagged 1, capped 0.

### DINERS CLUB MILES  
`rivo:hdfc-diners-club-miles` ↔ `savesage:hdfc-diners-club-miles` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `forex_markup_pct` | 3.0 | 3.5 | CONFLICT |
| `network` | DINERS | DINERS_CLUB | CONFLICT |

Earn rules — Rivo **1**, SaveSage **1** (SaveSage states 1). Rivo MCC-tagged 1, capped 0.

### SHOPPERS STOP BLACK  
`rivo:shoppers-stop-black-hdfc-bank` ↔ `savesage:hdfc-shoppers-stop-black, hdfc-shoppers-stop` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | MASTERCARD | VISA | CONFLICT |

Earn rules — Rivo **3**, SaveSage **3** (SaveSage states 3). Rivo MCC-tagged 1, capped 0.

### BUSINESS REGALIA  
`rivo:hdfc-business-regalia` ↔ `savesage:hdfc-business-regalia, hdfc-business-regalia-first, hdfc-giga-business, hdfc-business-freedom, hdfc-paytm-business, hdfc-csc-small-business, hdfc-business-moneyback` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | None | VISA | rivo_missing |

Earn rules — Rivo **2**, SaveSage **2** (SaveSage states 2). Rivo MCC-tagged 1, capped 0.

### PIXEL GO  
`rivo:hdfc-bank-pixel-go` ↔ `savesage:hdfc-pixel-go` (score 1.0)

Scalar fields agree.

Earn rules — Rivo **3**, SaveSage **3** (SaveSage states 3). Rivo MCC-tagged 1, capped 2.

### INDIAN OIL  
`rivo:hdfc-indianoil` ↔ `savesage:hdfc-indian-oil` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | RUPAY | VISA | CONFLICT |

Earn rules — Rivo **5**, SaveSage **5** (SaveSage states 5). Rivo MCC-tagged 3, capped 4.

### MILLENNIA  
`rivo:hdfc-millennia` ↔ `savesage:hdfc-millennia-visa, hdfc-millennia-diners-club, hdfc-millennia-rupay, hdfc-millennia-mastercard` (score 1.0)

Scalar fields agree.

Earn rules — Rivo **15**, SaveSage **14** (SaveSage states 14). Rivo MCC-tagged 6, capped 14.

Rivo carries 1 more rules here — likely MCC-split variants of one commercial rule.

### DOCTORS SUPERIA  
`rivo:hdfc-doctors-superia` ↔ `savesage:hdfc-doctors-superia, hdfc-superia` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | None | MASTERCARD | rivo_missing |

Earn rules — Rivo **2**, SaveSage **1** (SaveSage states 1). Rivo MCC-tagged 2, capped 0.

Rivo carries 1 more rules here — likely MCC-split variants of one commercial rule.

Flags: **rivo has 2 rules vs savesage 1**

### TATA NEU PLUS  
`rivo:tata-neu-plus-hdfc-bank` ↔ `savesage:hdfc-tata-neu-plus, hdfc-tata-neu-plus-rupay` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | RUPAY | VISA | CONFLICT |

Earn rules — Rivo **27**, SaveSage **24** (SaveSage states 24). Rivo MCC-tagged 8, capped 23.

Rivo carries 3 more rules here — likely MCC-split variants of one commercial rule.

### TATA NEU INFINITY  
`rivo:tata-neu-infinity-hdfc-bank` ↔ `savesage:hdfc-tata-neu-infinity, hdfc-tata-neu-infinity-rupay` (score 0.75)

Scalar fields agree.

Earn rules — Rivo **27**, SaveSage **24** (SaveSage states 24). Rivo MCC-tagged 8, capped 23.

Rivo carries 3 more rules here — likely MCC-split variants of one commercial rule.

### PHONEPE UNO  
`rivo:phonepe-hdfc-bank-uno` ↔ `savesage:hdfc-phonepe-uno, hdfc-phonepe-ultimo` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `forex_markup_pct` | 3.5 | None | savesage_missing |

Earn rules — Rivo **17**, SaveSage **13** (SaveSage states 13). Rivo MCC-tagged 7, capped 16.

Rivo carries 4 more rules here — likely MCC-split variants of one commercial rule.

### PHONEPE ULTIMO  
`rivo:phonepe-hdfc-bank-ultimo` ↔ `savesage:hdfc-phonepe-ultimo, hdfc-phonepe-uno` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `forex_markup_pct` | 3.5 | None | savesage_missing |

Earn rules — Rivo **17**, SaveSage **13** (SaveSage states 13). Rivo MCC-tagged 7, capped 16.

Rivo carries 4 more rules here — likely MCC-split variants of one commercial rule.

### 6E Rewards IndiGo HDFC Bank Credit Card  
`rivo:hdfc-6e-rewards-indigo` ↔ `savesage:hdfc-6e-rewards-indigo, hdfc-6e-rewards-xl-indigo` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `network` | MASTERCARD | VISA | CONFLICT |

Earn rules — Rivo **12**, SaveSage **6** (SaveSage states 6). Rivo MCC-tagged 0, capped 0.

Rivo carries 6 more rules here — likely MCC-split variants of one commercial rule.

Flags: **rivo rules carry no MCC**; **rivo has 12 rules vs savesage 6**; **rivo says discontinued, savesage says still issuing**

### HDFC BANK UPI RUPAY  
`rivo:hdfc-bank-upi-rupay` ↔ `savesage:hdfc-upi-rupay-credit` (score 1.0)

| Field | Rivo | SaveSage | |
|---|---|---|---|
| `forex_markup_pct` | None | 3.5 | rivo_missing |

Earn rules — Rivo **16**, SaveSage **5** (SaveSage states 5). Rivo MCC-tagged 7, capped 15.

Rivo carries 11 more rules here — likely MCC-split variants of one commercial rule.

Flags: **rivo has 16 rules vs savesage 5**

## Cards only in SaveSage

22 HDFC cards SaveSage has that Rivo's catalogue does not:

- `hdfc-paytm-select` — HDFC Paytm Select credit card · ₹1000/yr · 9 rules
- `hdfc-paytm` — HDFC Paytm credit card · ₹500/yr · 5 rules
- `hdfc-paytm-mobile` — HDFC Paytm Mobile credit card · ₹348/yr · 3 rules
- `hdfc-easyemi` — HDFC EasyEMI credit card · ₹500/yr · 6 rules
- `hdfc-corporate-premium` — HDFC Corporate Premium credit card · ₹0/yr · 1 rules
- `hdfc-sap-concur-solutions-black-corporate` — HDFC SAP Concur Solutions Black Corporate credit card · ₹0/yr · 1 rules
- `hdfc-sap-concur-solutions-prime-corporate` — HDFC SAP Concur Solutions Prime Corporate credit card · ₹0/yr · 1 rules
- `hdfc-biz-grow` — HDFC Biz Grow credit card · ₹500/yr · 8 rules
- `hdfc-biz-first` — HDFC Biz First credit card · ₹500/yr · 18 rules
- `hdfc-paytm-select-business` — HDFC Paytm SELECT Business credit card · ₹1000/yr · 6 rules
- `hdfc-upi-rupay-biz` — HDFC UPI RuPay Biz credit card · ₹99/yr · 5 rules
- `hdfc-flipkart-wholesale` — HDFC Flipkart Wholesale credit card · ₹499/yr · 5 rules
- `hdfc-hog-diners-club` — HDFC H.O.G Diners Club credit card · ₹10000/yr · 6 rules
- `hdfc-harleydavidson-diners-club` — HDFC Harley-Davidson Diners Club credit card · ₹2500/yr · 9 rules
- `hdfc-equitas-elegance` — HDFC Equitas Elegance credit card · ₹1000/yr · 4 rules
- `hdfc-equitas-excite` — HDFC Equitas Excite credit card · ₹500/yr · 5 rules
- `hdfc-best-price-save-smart` — HDFC Best Price Save Smart credit card · ₹500/yr · 4 rules
- `hdfc-bharat-cashback` — HDFC Bharat Cashback credit card · ₹500/yr · 7 rules
- `hdfc-paytm-digital` — HDFC Paytm Digital credit card · ₹149/yr · 5 rules
- `hdfc-pine-labs` — HDFC Pine Labs credit card · ₹499/yr · 6 rules
- `hdfc-best-price-save-max` — HDFC Best Price Save Max credit card · ₹1000/yr · 5 rules
- `hdfc-purchase-premium` — HDFC Purchase Premium credit card · ₹0/yr · 2 rules

## Cards only in Rivo

- `hdfc-diners-club-international` — DINERS CLUB INTERNATIONAL
- `hdfc-visa-signature` — VISA SIGNATURE
- `hdfc-world-mastercard` — WORLD MASTERCARD
- `hdfc-bizpower-business` — BIZPOWER BUSINESS
- `hdfc-intermiles-signature` — INTERMILES SIGNATURE
- `hdfc-jetprivilege-titanium` — JETPRIVILEGE TITANIUM

## Matches needing human review

- `hdfc-diners-club-intermiles` (DINERS CLUB INTERMILES) → `hdfc-diners-club-miles` — score 0.63
- `hdfc-titanium-edge` (TITANIUM EDGE) → `hdfc-platinum-edge, hdfc-times-titanium` — score 0.73
- `hdfc-regalia-first` (REGALIA FIRST) → `hdfc-regalia-first` — score 0.69
- `hdfc-all-miles` (ALL MILES) → `hdfc-diners-club-miles` — score 0.68
- `hdfc-bank-platinum-plus` (PLATINUM PLUS) → `hdfc-times-platinum, hdfc-teachers-platinum` — score 0.7
- `hdfc-intermiles-platinum` (INTERMILES PLATINUM) → `hdfc-platinum-edge` — score 0.65
