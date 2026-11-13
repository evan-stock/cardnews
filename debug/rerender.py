"""(임시 2026-11-13 d19) 기사·커뮤니티 원본 화면 캡처. 끝나면 원래 rerender.py로 되돌림."""
import asyncio, os
from pathlib import Path
from playwright.async_api import async_playwright
OUT = Path("media/20261113-d19/shots"); OUT.mkdir(parents=True, exist_ok=True)
JOBS = [
 ("joseilbo", "https://m.joseilbo.com/news/view.htm?newsid=579544", "대화가 어렵다"),
 ("joseilbo_pc", "https://www.joseilbo.com/news/htmls/2026/11/20261112579544.html", "대화가 어렵다"),
 ("fmk", "https://m.fmkorea.com/best/10545865839", "집체교육"),
 ("fmk2", "https://m.fmkorea.com/best/10547994317", "노쇼"),
 ("mbong", "https://mbong.kr/issue/130719286", "잠수"),
]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 430, "height": 932}, device_scale_factor=3, locale="ko-KR",
              user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
        for name, url, key in JOBS:
            pg = await ctx.new_page()
            try:
                await pg.goto(url, wait_until="domcontentloaded", timeout=40000); await pg.wait_for_timeout(4000)
                loc = pg.get_by_text(key).first
                try:
                    await loc.scroll_into_view_if_needed(timeout=5000); await pg.evaluate("window.scrollBy(0,-250)")
                except Exception as e:
                    print(name, "no key", e)
                await pg.wait_for_timeout(800)
                await pg.screenshot(path=str(OUT / f"{name}.png"))
                await pg.screenshot(path=str(OUT / f"{name}_full.png"), full_page=True)
                (OUT / f"{name}.txt").write_text((await pg.inner_text("body"))[:6000])
                print(name, "ok")
            except Exception as e:
                print(name, "ERR", e); (OUT / f"{name}.err").write_text(str(e))
            await pg.close()
        await b.close()
asyncio.run(main())
