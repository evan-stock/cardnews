"""20261123-zico 3장: 2019 일반인 비하 — 방송정지 안내(YTN 2019.6.20 보도 화면) + 피해 당사자 글(인사이트 보도). 검은 틀."""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)


def rc(d, y, t, f, base):
    parts = re.split(r"('[^']*')", t); tw = sum(d.textlength(p.strip("'"), font=f) for p in parts if p); x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'"); d.text((x, y), p, font=f, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=f)


a = Image.open(O / "p19.jpg").convert("RGB")
b = Image.open(O / "v19.jpg").convert("RGB").crop((0, 1212, 700, 1478))
a = a.resize((940, round(a.height * 940 / a.width)), Image.LANCZOS)
b = b.resize((940, round(b.height * 940 / b.width)), Image.LANCZOS)
ph = Image.new("RGB", (940, a.height + 16 + b.height), (10, 10, 12)); ph.paste(a, (0, 0)); ph.paste(b, (0, a.height + 16))
if ph.height > 720: ph = ph.resize((round(940 * 720 / ph.height), 720), Image.LANCZOS)
im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
rc(d, 168, "7년 전엔 출근길 시민에게", F("Medium", 46), FG); rc(d, 236, "\"출근하세요?\" '비하' 방송", F("Black", 54), FG)
m = Image.new("L", ph.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, ph.width - 1, ph.height - 1), 18, fill=255)
im.paste(ph, ((W - ph.width) // 2, 300), m); d = ImageDraw.Draw(im); y = 300 + ph.height + 92
rc(d, y, "당시 방송 정지 '7일' · 장애인 비하로 사과한 적도", F("Black", 42), YE)
rc(d, y + 60, "2019년 6월 방송 화면 · 아래: 피해 당사자 글(인사이트 보도)", F("Medium", 28), (190, 190, 198))
lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)
im.save(O / "c03.jpg", quality=93); print("ok", ph.size)
