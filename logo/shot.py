from playwright.sync_api import sync_playwright
import pathlib
p=pathlib.Path(__file__).parent
with sync_playwright() as pw:
    b=pw.chromium.launch(); pg=b.new_page(viewport={'width':1680,'height':900})
    pg.goto((p/'preview.html').as_uri()); pg.wait_for_timeout(4000)
    pg.screenshot(path=str(p/'fonts.png'),full_page=True); b.close()
