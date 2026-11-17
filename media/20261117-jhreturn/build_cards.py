"""20261117-jhreturn: 젠슨 황 X 글(11.17, 머스크 재게시) — 사과 + '이사회가 결정하면 CEO 복귀 영광'.
캡처: 사용자 제공 X 화면(엑스 자동 한국어 번역). 표지 사진: jensenback 보도사진(chip.jpg)."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350
im = Image.open(O / "tweet.png").convert("RGB")
def vs(parts):
    o = Image.new("RGB", (max(p.width for p in parts), sum(p.height for p in parts))); y = 0
    for p in parts: o.paste(p, (0, y)); y += p.height
    return o
head = im.crop((0, 380, 1206, 505)); gap = Image.new("RGB", (1206, 24))
vs([head, gap, im.crop((0, 1352, 1206, 1675))]).save(O / "tw_a.png")
vs([head, gap, im.crop((0, 1720, 1206, 2290))]).save(O / "tw_b.png")
specs = [
 {"out": str(O / "c02.jpg"), "sub": "11월 17일 · 젠슨 황 X 게시물", "title": "먼저 '사과'했다", "cap": str(O / "tw_a.png"), "cap_max_h": 520, "box_bg": [0, 0, 0],
  "caption": "젠슨 황 X 게시물 캡처(엑스 자동 번역) · 일론 머스크 재게시", "label": "인정한 것", "lines": ["개인 생활의 '심각한 실수'", "이사회 독립 조사에 '협조' 약속"]},
 {"out": str(O / "c03.jpg"), "sub": "그리고 덧붙인 말", "title": "\"CEO 복귀를\n'영광'으로 생각하겠다\"", "cap": str(O / "tw_b.png"), "cap_max_h": 600, "box_bg": [0, 0, 0],
  "caption": "젠슨 황 X 게시물 캡처(엑스 자동 번역)", "label": "단, 조건", "lines": ["'이사회'가 복귀가 최선이라고 결정한다면"]},
]
sp = O / "specs.json"; sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)
ImageOps.fit(Image.open(O / "chip.jpg").convert("RGB"), (W, H), Image.LANCZOS, centering=(.2, .3)).save(O / "cover_bg.jpg", quality=95)
print("ok")
