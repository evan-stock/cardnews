"""기존 게시물을 Claude 재호출 없이 사진 수집·렌더링만 다시 해본다 (비용 0).
trigger.txt 가 'shot <id> <url>' 이면 그 페이지를 실제 브라우저(모바일 화면)로 캡처해 media/<id>/cand/ 에 저장한다(2026.11.21)."""
import json, os, shutil, sys
_a = sys.argv[1].strip().split()
if _a and _a[0] == "shot":
    from pathlib import Path
    from playwright.sync_api import sync_playwright
    out = Path("media") / _a[1] / "cand"; out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 430, "height": 932}, device_scale_factor=3, locale="ko-KR",
                        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
        r = pg.goto(_a[2], wait_until="domcontentloaded", timeout=60000); pg.wait_for_timeout(5000)
        print("status", r.status if r else None, pg.title())
        pg.screenshot(path=str(out / "shot_full.png"), full_page=True)
        open(out / "shot_text.txt", "w").write(pg.inner_text("body"))
        b.close()
    sys.exit(0)
sys.path.insert(0, os.getcwd())
from cardnews.common import load_post, MEDIA
from cardnews.images import pick_images
from cardnews.render import render
pid = sys.argv[1].strip()
p = load_post(pid)
slides = [dict(s) for s in p["slides"]]
pages = [s["url"] for s in p["sources"] if s.get("url")] + p.get("image_pages", [])
out = MEDIA / (pid + "-retry")
shutil.rmtree(out, ignore_errors=True)
credits = pick_images(slides, str(out / "bg"), pages=pages, story=p["topic"] + " / " + p.get("core", ""))
last = len(slides) - 1
slides = [s for i, s in enumerate(slides) if i in (0, last) or s.get("image") or s["t"].strip()]
for s in slides[1:-1]:
    if not s["t"].strip():
        s["b"] = ""
files = render(slides, str(out))
shutil.rmtree(out / "bg", ignore_errors=True)
json.dump({"credits": credits, "files": files, "with_image": [bool(s.get("image")) for s in slides]}, open(out / "result.json", "w"), ensure_ascii=False, indent=1)
print(credits, len(files))
# 1791905991
