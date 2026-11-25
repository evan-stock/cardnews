"""20261125-johuidae: 김민석 민주당 대표 조희대 대법원장 탄핵 5당 연대 공식 제안 → 신장식 \"지나치게 추상적\"·절차 합의 역제안(경향·데일리안 11.25). 본문 기사 캡처, 마무리 장 없음."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)


def rich_center(d, y, text, font, base):
    parts = re.split(r"('[^']*')", text); tw = sum(d.textlength(p.strip("'"), font=font) for p in parts if p)
    x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=font)


def rich(d, x, y, text, font, base=FG):
    for p in re.split(r"('[^']*')", text):
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base); x += d.textlength(p, font=font)


def logo(im):
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
    lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)


def frame(top, photo, bottom, sub=None):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    p = photo
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300), m)
    d = ImageDraw.Draw(im); y = 300 + p.height + 92
    rich_center(d, y, bottom, F("Black", 46), YE)
    if sub: rich_center(d, y + 62, sub, F("Medium", 32), (190, 190, 198))
    logo(im); return im


def fit(name, w=940, h=700, c=(.5, .5), crop=None):
    im = Image.open(O / name).convert("RGB")
    if crop: im = im.crop(crop)
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=c)
    return im.filter(ImageFilter.UnsharpMask(2, 60, 2))






fit = lambda img, w, h, c=(.5, .5): ImageOps.fit(img, (w, h), Image.LANCZOS, centering=c)
op = lambda n: Image.open(O / n).convert("RGB")


def panel(rows, h=640, gap=None):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = gap or (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198)); rich(d, 56, y + 42, v, F("Black", 42))
    return p




def cap(src, box, h):
    im = op(src).crop(box); return im.resize((round(im.width * h / im.height), h), Image.LANCZOS) if im.width * h / im.height <= 940 else im.resize((940, round(im.height * 940 / im.width)), Image.LANCZOS)
# 2026.11.25 사용자 지시: 빈 공간 많은 두 장을 한 장으로(캡처 두 개 위아래)
k = cap("khan.jpg", (0, 370, 860, 600), 300); dl = cap("dailian.jpg", (0, 0, 860, 300), 330)
k = k.resize((940, round(k.height * 940 / k.width))); dl = dl.resize((940, round(dl.height * 940 / dl.width)))
stack = Image.new("RGB", (940, k.height + 28 + dl.height), (10, 10, 12)); stack.paste(k, (0, 0)); stack.paste(dl, (0, k.height + 28))
frame(("김민석 '조희대 탄핵 5당 연대' 제안", "혁신당조차 \"지나치게 '추상적'\""), stack,
      "\"절차·일정부터 합의하자\" 역제안", "경향신문·데일리안(11.25)").save(O / "c02.jpg", quality=93)
frame(("무소속 한동훈 의원", "\"인용되면 '의원직' 사퇴\""), cap("handh.jpg", (0, 240, 860, 600), 380),
      "\"서영교·박선원도 '직' 걸어라\"", "조선일보(11.25)").save(O / "c03.jpg", quality=93)
# 표지(2026.11.25 사용자 지시): 왼쪽 김민석, 오른쪽 조희대 나란히, 세로 경계 페이드
HW, fade = 600, 120
def half(n, cx):
    im = op(n); im = im.resize((round(im.width * H / im.height), H), Image.LANCZOS); cx = round(cx * im.width)
    x0 = max(0, min(im.width - HW, cx - HW // 2)); return im.crop((x0, 0, x0 + HW, H))
L = half("press06.jpg", 0.57); Rt = half("jo.jpg", 0.5)
cv = Image.new("RGB", (W, H)); cv.paste(Rt, (W - HW, 0))
m = Image.new("L", (HW, H), 255); md = ImageDraw.Draw(m)
for x in range(HW - fade, HW): md.line([(x, 0), (x, H)], fill=round(255 * (HW - x) / fade))
cv.paste(L, (0, 0), m); cv.filter(ImageFilter.UnsharpMask(2, 40, 2)).save(O / "cover_bg.jpg", quality=95)
print("ok")
