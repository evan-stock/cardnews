"""(임시 2026-11-13) 인스타 참고 게시물 embed 화면 캡처. 끝나면 원래 rerender.py로 되돌림."""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright
SC = "DfqUqlLE_Hc"
OUT = Path(f"media/ref-{SC}"); OUT.mkdir(parents=True, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 540, "height": 1100}, device_scale_factor=2, locale="ko-KR")
        pg = await ctx.new_page()
        await pg.goto(f"https://www.instagram.com/p/{SC}/embed/captioned/", wait_until="networkidle", timeout=60000)
        await pg.wait_for_timeout(3000)
        (OUT / "embed.txt").write_text(await pg.inner_text("body"))
        imgs = []
        for i in range(12):
            await pg.screenshot(path=str(OUT / f"s{i+1:02d}.png"), full_page=True)
            srcs = await pg.eval_on_selector_all("img", "els=>els.map(e=>[e.src,e.alt,e.naturalWidth])")
            imgs.append(srcs)
            nxt = pg.locator("button[aria-label*='Next'], button[aria-label*='다음'], .coreSpriteRightChevron")
            if await nxt.count() == 0: break
            try:
                await nxt.first.click(timeout=3000); await pg.wait_for_timeout(1500)
            except Exception: break
        (OUT / "imgs.json").write_text(json.dumps(imgs, ensure_ascii=False, indent=1))
        await b.close()
asyncio.run(main())
