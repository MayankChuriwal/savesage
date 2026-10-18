#!/usr/bin/env python3
"""Stage 1: snapshot every savesage.club public API response to raw/.

Idempotent: a file that already exists is skipped, so a killed run resumes.
Nothing is parsed here on purpose -- stage 2 re-reads raw/ for free.
"""
import json, os, sys, threading, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

API = "https://api.savesage.club"
UA = "savesage-kb-research/1.0 (+churiwalmayank@gmail.com; contact to request rate change)"
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
DELAY = 1.0
WORKERS = 3          # 3 threads x 1s sleep = ~3 req/s in aggregate
TABS = ["earn-categories", "benefits-and-offers", "lounge-access",
        "milestones", "redemption-options"]


def get(url, tries=3):
    for n in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if e.code in (400, 404):          # real answer, not a failure
                return e.code, body
            if e.code == 429:
                time.sleep(30 * (n + 1)); continue
            return e.code, body
        except Exception as e:
            if n == tries - 1:
                return 0, json.dumps({"_crawl_error": str(e)})
            time.sleep(5 * (n + 1))
    return 0, json.dumps({"_crawl_error": "exhausted retries"})


def save(relpath, url):
    """Fetch url into raw/relpath unless already present. Returns True if fetched."""
    path = os.path.join(RAW, relpath)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    status, body = get(url)
    with open(path + ".meta", "w") as f:
        json.dump({"url": url, "status": status, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(body)
    os.replace(tmp, path)      # atomic: resume never sees a truncated file
    time.sleep(DELAY)
    return True


def crawl_list():
    """Paginate credit-card-filters, snapshot each page, return unique slugs."""
    slugs, cursor, page = [], None, 0
    while page < 20:
        rel = f"list/page-{page}.json"
        url = f"{API}/credit-card-filters?limit=100" + (f"&cursor={cursor}" if cursor else "")
        save(rel, url)
        d = json.load(open(os.path.join(RAW, rel)))
        cards = d.get("cards", [])
        slugs += [c["slug"] for c in cards]
        cursor = d.get("nextCursor")
        page += 1
        if not cursor or not cards:
            break
    seen, uniq = set(), []
    for s in slugs:
        if s not in seen:
            seen.add(s); uniq.append(s)
    print(f"list: {len(slugs)} rows, {len(uniq)} unique slugs, {page} pages", flush=True)
    return uniq


def main():
    os.makedirs(RAW, exist_ok=True)
    slugs = crawl_list()
    json.dump(slugs, open(os.path.join(RAW, "slugs.json"), "w"), indent=1)

    cells = [(f"cards/{slug}/{tab}.json", f"{API}/credit-card/{slug}?tab={tab}")
             for slug in slugs for tab in TABS]
    todo = [c for c in cells if not os.path.exists(os.path.join(RAW, c[0]))]
    print(f"tabs: {len(cells)} total, {len(todo)} to fetch", flush=True)

    t0 = time.time()
    lock = threading.Lock()
    counter = {"n": 0}

    def work(cell):
        save(*cell)
        with lock:
            counter["n"] += 1
            n = counter["n"]
        if n % 250 == 0:
            el = (time.time() - t0) / 60
            rate = n / max(el, 1e-9)
            print(f"  {n}/{len(todo)} tabs  ({el:.1f} min, {rate:.0f}/min, "
                  f"~{(len(todo)-n)/max(rate,1e-9):.0f} min left)", flush=True)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(work, todo))
    print(f"cards done: {len(todo)} fetched in {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
