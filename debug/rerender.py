"""(임시 2026-11-13) 디시 세무사 갤 '나무 모의고사 최고점' 원글 찾기·캡처. 끝나면 원래 rerender.py로 되돌림."""
import asyncio, json, re
from pathlib import Path
from playwright.async_api import async_playwright
OUT = Path("media/ref-mock"); OUT.mkdir(parents=True, exist_ok=True)
QS = ["나무 모의고사", "모의고사 최고점", "나무모의고사", "전국모의고사 1등"]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1280, "height": 1600}, locale="ko-KR")
        pg = await ctx.new_page(); found = []
        for q in QS:
            url = f"https://gall.dcinside.com/mgallery/board/lists/?id=cta&s_type=search_subject_memo&s_keyword={q}"
            try:
                await pg.goto(url, wait_until="domcontentloaded", timeout=40000); await pg.wait_for_timeout(2000)
                rows = await pg.eval_on_selector_all("tr.us-post", "els=>els.map(r=>[r.getAttribute('data-no'), r.querySelector('td.gall_tit').innerText.trim(), (r.querySelector('td.gall_date')||{}).title||'', (r.querySelector('td.gall_count')||{}).innerText||''])")
                found.append([q, rows[:20]])
            except Exception as e:
                found.append([q, str(e)])
        (OUT / "search.json").write_text(json.dumps(found, ensure_ascii=False, indent=1))
        seen = []
        for q, rows in found:
            if isinstance(rows, str): continue
            for no, tit, dt, cnt in rows:
                if no in seen or not dt.startswith("2026-11"): continue
                seen.append(no)
                if len(seen) > 6: break
                await pg.goto(f"https://gall.dcinside.com/mgallery/board/view/?id=cta&no={no}", wait_until="domcontentloaded", timeout=40000)
                await pg.wait_for_timeout(2500)
                el = pg.locator(".gallview_contents").first
                try:
                    await el.screenshot(path=str(OUT / f"post_{no}.png"))
                except Exception:
                    await pg.screenshot(path=str(OUT / f"post_{no}.png"), full_page=True)
                head = await pg.inner_text(".gallview_head") if await pg.locator(".gallview_head").count() else ""
                body = await pg.inner_text(".write_div") if await pg.locator(".write_div").count() else ""
                (OUT / f"post_{no}.txt").write_text(head + "\n----\n" + body[:3000])
        await b.close()
asyncio.run(main())
