"""(임시 2026-11-25) threadreaderapp에서 vechen 스레드 글·사진 받기 → media/20261125-neon/thread/"""
import json, os, sys, urllib.request
from playwright.sync_api import sync_playwright
out = "media/20261125-neon/thread"; os.makedirs(out, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 2000})
    pg.goto("https://threadreaderapp.com/thread/2124226509757944001.html", wait_until="networkidle", timeout=90000)
    items = pg.evaluate("""() => [...document.querySelectorAll('.content-tweet')].map(e => ({
        id: e.getAttribute('data-tweet') || '', text: e.innerText,
        imgs: [...e.querySelectorAll('img')].map(i => i.getAttribute('data-src') || i.src).filter(s => s && s.includes('pbs.twimg.com/media'))}))""")
    json.dump(items, open(f"{out}/thread.json", "w"), ensure_ascii=False, indent=1)
    pg.screenshot(path=f"{out}/page.png", full_page=True)
    for n, it in enumerate(items):
        for k, u in enumerate(it["imgs"]):
            u = u.split("?")[0] + "?format=jpg&name=large" if "format=" not in u else u.replace("name=small", "name=large")
            try:
                req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
                open(f"{out}/t{n}_{k}.jpg", "wb").write(urllib.request.urlopen(req, timeout=60).read())
            except Exception as e: print("img fail", u, e)
    b.close()
print(len(items))
