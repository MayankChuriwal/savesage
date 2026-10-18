#!/usr/bin/env python3
"""Stage 1b: taxonomy + bank hubs + best-for collections + blogs.

Bank hubs and best-for are clean-path HTML (robots allows those; only the
query-string faceted views are disallowed). The blogs API is 401, so blogs
come from their public HTML too.
"""
import json, os, re, time, urllib.request, xml.etree.ElementTree as ET
from crawl import get, save, RAW, DELAY, UA, API

SITE = "https://savesage.club"


def sitemap_urls():
    p = os.path.join(RAW, "sitemap.xml")
    if not os.path.exists(p):
        os.makedirs(RAW, exist_ok=True)
        _, body = get(f"{SITE}/sitemap.xml")
        open(p, "w").write(body)
        time.sleep(DELAY)
    root = ET.parse(p).getroot()
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    return [u.findtext(f"{ns}loc") for u in root.findall(f"{ns}url")]


def main():
    save("taxonomy/credit-card-categories.json", f"{API}/credit-card-categories")

    urls = sitemap_urls()
    hubs = [u for u in urls if re.match(rf"^{SITE}/credit-cards/[a-z0-9-]+(/[a-z0-9-]+)?$", u)]
    blogs = [u for u in urls if u.startswith(f"{SITE}/blogs/")]
    print(f"hubs: {len(hubs)}  blogs: {len(blogs)}")

    for u in hubs:
        rel = u.replace(f"{SITE}/credit-cards/", "").replace("/", "__")
        save(f"hubs/{rel}.html", u)
    for u in blogs:
        rel = u.replace(f"{SITE}/blogs/", "").replace("/", "__")
        save(f"blogs/{rel}.html", u)
    print("extras done")


if __name__ == "__main__":
    main()
