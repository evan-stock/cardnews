# 임시: X 게시물 임베드 화면 캡처(20261106-chipshock 3장용). 끝나면 원래 rerender.py로 되돌림.
import json, sys, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
out = Path("media/20261106-chipshock/cand"); out.mkdir(parents=True, exist_ok=True)
ids = {"reply": "2118387329694117986", "orig": "2118054336077127797"}
log = []
try:
    j = json.load(urllib.request.urlopen(urllib.request.Request(
        "https://api.fxtwitter.com/RepYassAnsari/status/2118387329694117986", headers={"User-Agent": "Mozilla/5.0"}), timeout=20))
    q = (j.get("tweet") or {}).get("quote") or {}
    log.append(json.dumps({"quote_id": q.get("id"), "quote_text": q.get("text"), "quote_author": (q.get("author") or {}).get("screen_name"),
                           "reply_text": j["tweet"].get("text"), "views": j["tweet"].get("views")}, ensure_ascii=False))
    if q.get("id"): ids["musk"] = q["id"]
except Exception as e:
    log.append(f"fx err {e}")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 560, "height": 1400}, device_scale_factor=2.5)
    for name, tid in ids.items():
        try:
            pg.goto(f"https://platform.twitter.com/embed/Tweet.html?id={tid}&theme=dark&lang=ko&dnt=true", wait_until="networkidle", timeout=45000)
            pg.wait_for_timeout(4000)
            el = pg.locator("article").first
            el.screenshot(path=str(out / f"xcap_{name}.png"))
            log.append(f"ok {name} {tid}")
        except Exception as e:
            pg.screenshot(path=str(out / f"xcap_{name}_page.png"), full_page=True)
            log.append(f"fail {name} {tid} {e}")
    b.close()
(out / "xcap_log.txt").write_text("\n".join(log), encoding="utf-8")
print("\n".join(log))
