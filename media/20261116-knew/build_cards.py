"""20261116-knew: 수능 연기 안 하는 이유? 교육부는 이미 알고 있었다 (2004·2013·2026 기사 캡처)."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350
L = lambda n: Image.open(O / n).convert("RGB")


def vstack(parts, w=1400, gap=30, bg=(255, 255, 255)):
    parts = [p.resize((w, round(p.height * w / p.width)), Image.LANCZOS) for p in parts]
    out = Image.new("RGB", (w, sum(p.height for p in parts) + gap * (len(parts) - 1)), bg); y = 0
    for p in parts: out.paste(p, (0, y)); y += p.height + gap
    return out


g = Image.open(D / "video/img1.jpg").convert("RGB").crop((40, 300, 1120, 1300)); g.save(O / "toeic13.png")
vstack([L("seoul04_head.png").crop((0, 70, 1534, 324)), L("seoul04_p1.png")]).save(O / "cap2.png")
vstack([L("mt13_head.png"), L("mt13_sub.png"), L("mt13_p1.png").crop((0, 0, 1220, 190))]).save(O / "cap3.png")
vstack([L("segye_head.png"), L("segye_p1.png"), L("segye_p2.png")]).save(O / "cap5.png")

specs = [
 {"out": str(O / "c02.jpg"), "sub": "서울신문 · 2004년 11월 22일",
  "title": "22년 전 수능에서도\n'소문'이 '사실'이 됐다", "cap": str(O / "cap2.png"), "cap_max_h": 560, "box_bg": [255, 255, 255],
  "caption": "서울신문 기사 캡처", "label": "2004년 광주 휴대전화 수능 부정",
  "lines": ["그때 검토한 대책: 전파차단기·전자검색대", "결론: 전파법에 막혀 '무산'"]},
 {"out": str(O / "c03.jpg"), "sub": "머니투데이 · 2013년 11월 5일 (수능 이틀 전)",
  "title": "\"6500만 원이면 만점\"\n업체 \"5년째 적발 '없다'\"", "cap": str(O / "cap3.png"), "cap_max_h": 560, "box_bg": [255, 255, 255],
  "caption": "머니투데이 단독 기사 캡처", "label": "13년 전 기자가 직접 의뢰해 보니",
  "lines": ["초소형 장비 쓰는 '시험도우미' 업체", "\"올해는 의뢰자 6명 다 차서 웃돈 줘야\""]},
 {"out": str(O / "c04.jpg"), "sub": "연합뉴스 그래픽 · 2013년 11월 4일 · 자료 부산경찰청",
  "title": "가짜 깁스 속 스마트폰\n귓속엔 '2mm' 수신기", "cap": str(O / "toeic13.png"), "cap_max_h": 620, "box_bg": [255, 255, 255],
  "caption": "연합뉴스 그래픽 (디시인사이드 게시글 재인용)", "label": "같은 해 토익에선",
  "lines": ["수험생 12명이 시험장 밖에서 답을 받았다"]},
 {"out": str(O / "c05.jpg"), "sub": "세계일보 · 2026년 11월 16일",
  "title": "그리고 2026년\n여전히 '어렵다'", "cap": str(O / "cap5.png"), "cap_max_h": 560, "box_bg": [255, 255, 255],
  "caption": "세계일보 기사 캡처", "label": "22년 전과 같은 이유",
  "lines": ["전파 차단은 전파법상 허용 안 됨(교육부 브리핑)", "장관 \"연기하면 더 큰 혼란\""]},
]
sp = Path("/tmp/knew_specs.json"); sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)

# 표지: 어두운 바탕 + 2013 그래픽 크게 + 2004·2026 제목 캡처 기울여 겹치기
bg = Image.new("RGB", (W, H), (14, 14, 18)).convert("RGBA")


def place(base, t, x, y, ang, wdt, r=16):
    t = t.resize((wdt, round(t.height * wdt / t.width)), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", t.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, t.width - 1, t.height - 1), r, fill=255); t.putalpha(m)
    sh = Image.new("RGBA", (t.width + 60, t.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 38, t.width + 30, t.height + 38), r, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(16)); sh.alpha_composite(t, (30, 30)); sh = sh.rotate(ang, Image.BICUBIC, expand=True)
    base.alpha_composite(sh, (x, y))


place(bg, g, 60, 30, 0, 960)
place(bg, L("seoul04_head.png").crop((0, 70, 1534, 230)), -10, 40, 3, 700)
place(bg, L("mt13_head.png").crop((0, 0, 1520, 110)), 360, 560, -3, 720)
bg.convert("RGB").save(O / "cover_bg.jpg", quality=95)
print("ok")

# 5장(신규): 그때 vs 지금 — 방식은 그대로, 푸는 사람만 바뀌었다
import re
from PIL import ImageFont
YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)


def rich(d, x, y, text, font, base=FG, anchor="la"):
    parts = re.split(r"('[^']*')", text)
    if anchor == "ma":
        x -= sum(d.textlength(p.strip("'"), font=font) for p in parts if p) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base); x += d.textlength(p, font=font)


im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
d.text((90, 120), "2013 토익 부정 · 2026 AI 부정", font=F("SemiBold", 34), fill=YE)
rich(d, 90, 170, "수법은 '그대로'", F("Black", 64))
rich(d, 90, 250, "푸는 사람만 '사람 → AI'", F("Black", 64))
px, py, pw = 70, 380, 940
cols = [(px + 230, "2013년"), (px + 600, "2026년")]
d.rounded_rectangle((px, py, px + pw, py + 520), 22, fill=(24, 24, 30))
for cx, t in cols: d.text((cx, py + 34), t, font=F("Black", 34), fill=(200, 200, 208))
rows = [("찍기", "가짜 깁스 속 스마트폰", "초소형 카메라·안경"),
        ("듣기", "귓속 2mm 수신기", "귀에 넣는 '깨알' 기기"),
        ("풀기", "'토익 고득점자'가 풀이", "'생성형 AI'가 풀이")]
y = py + 100
for i, (k, a, b) in enumerate(rows):
    last = i == len(rows) - 1
    if last: d.rounded_rectangle((px + 14, y - 14, px + pw - 14, y + 104), 16, fill=(60, 52, 20))
    d.line((px + 24, y - 16, px + pw - 24, y - 16), fill=(55, 55, 64), width=2) if i and not last else None
    d.text((px + 34, y + 22), k, font=F("Black", 34), fill=YE if last else (170, 170, 180))
    rich(d, px + 160, y + 24, a, F("SemiBold", 31), base=FG)
    rich(d, px + 530, y + 24, b, F("SemiBold", 31), base=FG)
    y += 140
d.text((90, py + 560), "자료: 부산경찰청(2013, 연합뉴스 그래픽) · 세무사 수석 자수 보도", font=F("Medium", 26), fill=(150, 150, 160))
d.text((90, py + 600), "· 최은옥 교육부 차관 국회 답변(2026.11.16)", font=F("Medium", 26), fill=(150, 150, 160))
rich(d, W // 2, 1095, "그래서 막는 법도 '22년째' 같은 자리", F("Black", 42), base=FG, anchor="ma")
lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)
im.save(O / "c04b.jpg", quality=95)
print("ok5")
