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


ph = Image.open(O / "sign.jpg").convert("RGB"); ph = ph.resize((round(ph.width * 700 / ph.height), 700), Image.LANCZOS)
im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
rc(d, 168, "온라인에 도는 '여의도의 현인' 짤", F("Medium", 46), FG); rc(d, 236, "팻말에 적힌 '폭락' 목표가", F("Black", 54), FG)
m = Image.new("L", ph.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, ph.width - 1, ph.height - 1), 18, fill=255)
im.paste(ph, ((W - ph.width) // 2, 300), m); d = ImageDraw.Draw(im); y = 300 + ph.height + 92
rc(d, y, "1차 삼전 19만·닉스 114만 → 2차 14만·75만", F("Black", 42), YE)
rc(d, y + 60, "커뮤니티 게시글 사진(\"6월 촬영\" 주장, 출처 미확인)", F("Medium", 30), (190, 190, 198))
lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)
im.save(O / "c02.jpg", quality=93); print("ok")
