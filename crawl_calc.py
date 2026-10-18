#!/usr/bin/env python3
"""Stage 1c: reward-calculator sweep -> effective earn rate per card per category.

For every (card, category) it asks the public calculator what a fixed spend
earns. rewardWorth / spendAmount is the effective rate -- which is exactly the
per-category number the app-wall hides on the card pages.

One spend amount only (caps would need a second amount; see report).
Resumable: each response is a file, existing files are skipped.
"""
import json, os, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

BASE = "https://savesage.club/api/reward-calculator"
UA = "savesage-kb-research/1.0 (+churiwalmayank@gmail.com; contact to request rate change)"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw", "calc")
SPEND = 10000
DELAY = 1.0
WORKERS = 4          # 4 threads x 1s sleep = ~4 req/s in aggregate


def post(payload, tries=3):
    body = json.dumps(payload).encode()
    for n in range(tries):
        req = urllib.request.Request(f"{BASE}/calculate", data=body, method="POST",
                                     headers={"Content-Type": "application/json",
                                              "User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            b = e.read().decode("utf-8", "replace")
            if e.code == 429:
                time.sleep(30 * (n + 1)); continue
            if e.code in (400, 404):
                return e.code, b
            if n == tries - 1:
                return e.code, b
            time.sleep(5 * (n + 1))
        except Exception as e:
            if n == tries - 1:
                return 0, json.dumps({"_crawl_error": str(e)})
            time.sleep(5 * (n + 1))
    return 0, json.dumps({"_crawl_error": "exhausted retries"})


def main():
    bank_cards = json.load(open(os.path.join(HERE, "..", "rc_bank_cards.json")))
    cats = json.load(open(os.path.join(HERE, "..", "rc_categories.json")))
    slugs = [c["slug"] for c in cats]

    pairs = [(int(bid), int(c["id"]), c["label"]) for bid, v in bank_cards.items() for c in v["cards"]]
    total = len(pairs) * len(slugs)
    print(f"sweep: {len(pairs)} cards x {len(slugs)} categories = {total} calls", flush=True)

    os.makedirs(RAW, exist_ok=True)
    cells = []
    for bank_id, card_id, _ in pairs:
        os.makedirs(os.path.join(RAW, str(card_id)), exist_ok=True)
        for slug in slugs:
            path = os.path.join(RAW, str(card_id), slug.replace(" ", "_") + ".json")
            if not (os.path.exists(path) and os.path.getsize(path) > 0):
                cells.append((bank_id, card_id, slug, path))
    print(f"todo: {len(cells)} cells ({total - len(cells)} already on disk)", flush=True)

    t0 = time.time()
    lock = threading.Lock()
    counter = {"n": 0}

    def work(cell):
        bank_id, card_id, slug, path = cell
        status, body = post({"bankId": bank_id, "cardId": card_id,
                             "categorySlug": slug, "spendAmount": SPEND})
        rec = {"bankId": bank_id, "cardId": card_id, "categorySlug": slug,
               "spendAmount": SPEND, "status": status}
        try:
            rec["response"] = json.loads(body)
        except ValueError:
            rec["response_raw"] = body
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(rec, f, ensure_ascii=False)
        os.replace(tmp, path)      # atomic, so a killed run never leaves a half file
        time.sleep(DELAY)
        with lock:
            counter["n"] += 1
            n = counter["n"]
        if n % 1000 == 0:
            el = (time.time() - t0) / 60
            rate = n / max(el, 1e-9)
            print(f"  {n}/{len(cells)}  ({el:.1f} min, {rate:.0f}/min, "
                  f"~{(len(cells) - n) / max(rate, 1e-9):.0f} min left)", flush=True)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(work, cells))
    print(f"calc sweep done: {len(cells)} new cells in {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
