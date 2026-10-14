from playwright.sync_api import sync_playwright
import pathlib
p=pathlib.Path(__file__).parent
with sync_playwright() as pw:
    b=pw.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':2160})
    pg.goto((p/'preview.html').as_uri()); pg.wait_for_timeout(4000)
    pg.locator('#a').screenshot(path=str(p/'osseul_blackhansans.png'))
    pg.locator('#b').screenshot(path=str(p/'osseul_noto.png')); b.close()
