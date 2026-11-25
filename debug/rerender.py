"""기존 게시물을 Claude 재호출 없이 사진 수집·렌더링만 다시 해본다 (비용 0).
trigger.txt 가 'shot <id> <url>' 이면 그 페이지를 실제 브라우저(모바일 화면)로 캡처해 media/<id>/cand/ 에 저장한다(2026.11.21)."""
import json, os, shutil, sys
_a = sys.argv[1].strip().split()
if _a and _a[0] in ("shot", "get"):
    # 한 줄에 하나: 'shot <id> <url> [이름]' = 브라우저 캡처, 'get <id> <url> <이름>' = 파일 받기
    from pathlib import Path
    import requests
    from playwright.sync_api import sync_playwright
    UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for n, line in enumerate(sys.argv[1].strip().splitlines()):
            a = line.split()
            if len(a) < 3: continue
            out = Path("media") / a[1] / "cand"; out.mkdir(parents=True, exist_ok=True)
            name = a[3] if len(a) > 3 else f"shot{n}"
            try:
                if a[0] == "get":
                    r = requests.get(a[2], headers={"User-Agent": "cardnews-bot/1.0 (https://github.com/evan-stock/cardnews)"}, timeout=60)
                    print("get", r.status_code, a[2]); (out / name).write_bytes(r.content); continue
                pg = (b.new_page(viewport={"width": 1100, "height": 1000}, device_scale_factor=2, locale="ko-KR") if "desk" in a[4:]  # 'desk' = PC 화면(가로로 긴 기사 캡처, 예전 캡처 카드 양식 20261116-knew, 2026.11.22)
                      else b.new_page(viewport={"width": 430, "height": 932}, device_scale_factor=2, locale="ko-KR", user_agent=UA))
                r = pg.goto(a[2], wait_until="domcontentloaded", timeout=60000); pg.wait_for_timeout(5000)
                try: pg.wait_for_load_state("networkidle", timeout=15000); pg.evaluate("document.fonts.ready")
                except Exception: pass
                if "clean" in a[4:]:  # 'shot ... clean [noimg]' = 광고·고정 배너를 페이지에서 지우고 찍기(로고·제목·문단이 한 화면에 이어지게, 2026.11.22). noimg = 기사 본문 사진·빈 광고 자리도 지움
                    pg.evaluate("""(noimg) => {
                      const kill = e => e && e.remove();
                      document.querySelectorAll('iframe,ins,[id*=google_ads],[class*=adsbygoogle],[id^=div-gpt],[class*=banner],[id*=banner],[class*=ad-],[class*=_ad],[class^=ad],[id^=ad],[class*=advert],[class*=sponsor]').forEach(kill);
                      document.querySelectorAll('body *').forEach(e => { const s = getComputedStyle(e); if ((s.position === 'fixed' || s.position === 'sticky') && !e.querySelector('h1') && e.getBoundingClientRect().top > 80) kill(e); });
                      if (noimg) document.querySelectorAll('figure,picture,.photo,[class*=img],[class*=photo],[class*=image]').forEach(e => { if (!e.querySelector('h1,h2,p')) kill(e); });
                      document.querySelectorAll('div,section,aside').forEach(e => { if (!e.innerText.trim() && !e.querySelector('img,svg,video') && e.getBoundingClientRect().height > 40) kill(e); });
                    }""", "noimg" in a[4:])
                    pg.wait_for_timeout(800)
                if "font" in a[4:]:  # 'shot <id> <url> <이름> font' = 앱처럼 보이게 Pretendard 글꼴로 바꿔 찍기(2026.11.22)
                    import base64
                    fr = base64.b64encode(open("assets/fonts/Pretendard-Medium.otf", "rb").read()).decode()
                    fb = base64.b64encode(open("assets/fonts/Pretendard-ExtraBold.otf", "rb").read()).decode()
                    pg.add_style_tag(content=f"@font-face{{font-family:PJ;src:url(data:font/otf;base64,{fr});font-weight:400}}"
                                             f"@font-face{{font-family:PJ;src:url(data:font/otf;base64,{fb});font-weight:700}}"
                                             "*{font-family:PJ,-apple-system,sans-serif !important}")
                    pg.wait_for_timeout(1500)
                print("shot", r.status if r else None, pg.title(), a[2])
                pg.screenshot(path=str(out / f"{name}.jpg"), full_page=True, type="jpeg", quality=82)
                open(out / f"{name}.txt", "w").write(pg.inner_text("body") + "\n\n[링크]\n" + "\n".join(pg.eval_on_selector_all("a[href]", "els => els.map(e => e.href + ' ' + e.innerText.slice(0,60).replace(/\\n/g,' '))"))); pg.close()
            except Exception as e:
                print("실패", a[2], e)
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
