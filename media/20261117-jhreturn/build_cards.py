"""20261117-jhreturn: 젠슨 황 X 글(11.17, 머스크 재게시) — 사과 + '이사회가 결정하면 CEO 복귀 영광'.
캡처: 사용자 제공 X 화면(엑스 자동 한국어 번역). 표지 사진: jensenback 보도사진(chip.jpg)."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350
t1 = Image.open(O / "tw1.png").convert("RGB"); t2 = Image.open(O / "tw2.png").convert("RGB")  # 사용자 제공 전체 폭 캡처 2장(1206x2622)
def vs(parts):
    o = Image.new("RGB", (max(p.width for p in parts), sum(p.height for p in parts))); y = 0
    for p in parts: o.paste(p, (0, y)); y += p.height
    return o
head = t1.crop((0, 375, 1175, 700))
vs([head, t2.crop((0, 505, 1175, 880))]).save(O / "tw_a.png")
vs([head, t2.crop((0, 930, 1175, 1620))]).save(O / "tw_b.png")
specs = [
 {"out": str(O / "c02.jpg"), "sub": "11월 17일 · 젠슨 황 X 게시물", "title": "먼저 '사과'했다", "cap": str(O / "tw_a.png"), "cap_max_h": 600, "box_bg": [0, 0, 0],
  "caption": "젠슨 황 X 게시물 캡처(X Grok 번역) · 일론 머스크 재게시", "label": "인정한 것", "lines": ["개인 생활의 '심각한 실수'", "이사회 독립 조사에 '협조' 약속"]},
 {"out": str(O / "c03.jpg"), "sub": "그리고 덧붙인 말", "title": "\"CEO 복귀를\n'영광'으로 생각하겠다\"", "cap": str(O / "tw_b.png"), "cap_max_h": 680, "box_bg": [0, 0, 0],
  "caption": "젠슨 황 X 게시물 캡처(X Grok 번역)", "label": "단, 조건", "lines": ["'이사회'가 복귀가 최선이라고 결정한다면"]},
]
sp = O / "specs.json"; sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)
# 표지(사용자): 화면 꽉 차게 + 로고를 젠슨 황 뒤로. 오른쪽 로고 부분을 배경으로 크게 깔고, 왼쪽 젠슨 황 부분을 앞에 겹쳐 페이드
src = Image.open(O / "chip.jpg").convert("RGB")  # 1280x720
bgl = ImageOps.fit(src.crop((560, 0, 1280, 720)), (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(45)); bgl = Image.blend(bgl, Image.new("RGB", (W, H), (6, 10, 6)), .45)  # 초록 벽 흐린 바탕
logo = src.crop((660, 30, 1250, 520)); LW = 680; logo = logo.resize((LW, round(logo.height * LW / logo.width)), Image.LANCZOS)
lm = Image.new("L", logo.size, 0); ImageDraw.Draw(lm).rounded_rectangle((50, 40, logo.width - 20, logo.height - 50), 80, fill=255); lm = lm.filter(ImageFilter.GaussianBlur(45))
bgl.paste(logo, (W - LW + 20, 70), lm)
jh = src.crop((0, 0, 640, 720)); JH = 1050; jh = jh.resize((round(jh.width * JH / jh.height), JH), Image.LANCZOS)
ox, oy = -170, 120
lay = bgl.copy(); lay.paste(jh, (ox, oy))
fx0, fx1 = ox + jh.width - 260, ox + jh.width - 10
row = Image.new("L", (W, 1)); row.putdata([255 if x < fx0 else 0 if x > fx1 else int(255 * (fx1 - x) / (fx1 - fx0)) for x in range(W)])
m = Image.new("L", (W, H), 0); m.paste(row.resize((W, JH)), (0, oy))
col = Image.new("L", (1, 70)); col.putdata([int(255 * y / 69) for y in range(70)])
m2 = Image.new("L", (W, H), 255); m2.paste(col.resize((W, 70)), (0, oy)); m2.paste(0, (0, 0, W, oy))
from PIL import ImageChops
mask = ImageChops.multiply(m, m2)
cov = Image.composite(lay, bgl, mask)
cov.save(O / "cover_bg.jpg", quality=95)
print("ok")
