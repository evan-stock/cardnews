"""릴스 커버 썸네일(1080x1920). 사용: python -m cardnews.thumb drafts/thumb.json
{"id":"20261015-coffin","img":"cand/reel_frame_1080.jpg","tag":"실제 영상","t":"줄1\\n줄2\\n'강조'","sub":"","out":"reel_cover.jpg"}
- 글자는 위쪽(프로필 격자 3:4 잘림·릴스 하단 UI를 피함), '작은따옴표' 단어는 노란색
"""
import base64, html, json, re, sys
from playwright.sync_api import sync_playwright
from .common import CFG, MEDIA, ROOT


def make(d):
    base = MEDIA / d["id"]
    img = base64.b64encode(open(base / d["img"], "rb").read()).decode()
    lines = [html.escape(x, quote=False) for x in d["t"].split("\n")]
    title = "<br>".join(re.sub(r"'([^']+)'", r"<em>\1</em>", x) for x in lines)
    out = base / d.get("out", "reel_cover.jpg")
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto((ROOT / "templates" / "thumb.html").as_uri())
        pg.evaluate("""(x)=>{document.getElementById('bg').src=x.img;
          document.getElementById('t').innerHTML=x.t; document.getElementById('sub').textContent=x.sub||'';
          document.getElementById('hd').textContent=x.hd; if(x.tag){document.getElementById('tag').textContent=x.tag}else{document.getElementById('tagw').style.display='none'}}""",
                    {"img": "data:image/jpeg;base64," + img, "t": title, "sub": d.get("sub", ""), "tag": d.get("tag", ""),
                     "hd": CFG["brand"]["handle"].lstrip("@").upper()})
        pg.evaluate("async()=>{await document.fonts.ready; await new Promise(r=>setTimeout(r,500))}")
        if d.get("overlay"):  # 영상에 얹을 투명 PNG(사진 없이 글자·그림자만)
            pg.evaluate("()=>{document.getElementById('bg').remove();document.body.style.background='transparent';document.getElementById('c').style.background='transparent'}")
            pg.locator("#c").screenshot(path=str(out), type="png", omit_background=True)
        else:
            pg.locator("#c").screenshot(path=str(out), type="jpeg", quality=93)
        b.close()
    return out


if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    for d in (data if isinstance(data, list) else [data]):
        print(make(d))
