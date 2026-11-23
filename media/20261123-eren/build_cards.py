"""20261123-eren: 리만가설 증명 Lean 코드 시각화(X @juhyeon6749) ↔ 진격의 거인 최종장 에렌(시조의 거인) 닮은꼴. 오늘의쓸모 캐러셀.
본문: 실제 트윗 화면 캡처 + 비교. nypost-rep/build_cards.py 복사."""
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




import subprocess
xe = op("xembed.jpg").crop((0, 0, 860, 1300)); xe = xe.resize((round(xe.width * 620 / xe.height), 620), Image.LANCZOS)
frame(("엑스에 올라온 그림 한 장", "\"리만가설 증명 코드 '시각화'\""), xe,
      "가운데 줄기가 '120단계' 증명 뼈대", "가지는 증명에 쓰인 보조정리들 · 엑스 @juhyeon6749").save(O / "c02.jpg", quality=93)
a = ImageOps.fit(op("viz.jpg"), (452, 600), Image.LANCZOS); b = ImageOps.fit(op("eren_colossus.png").crop((250, 0, 1600, 1600)), (452, 600), Image.LANCZOS)
pair = Image.new("RGB", (940, 600), (10, 10, 12)); pair.paste(a, (0, 0)); pair.paste(b, (488, 0))
frame(("그런데 어디서 많이 본 모양", "최종장 에렌 '시조의 거인'"), pair,
      "척추에 뼈가 줄줄이, '땅울림' 그 장면", "왼쪽: 증명 시각화 · 오른쪽: 진격의 거인(이사야마 하지메)").save(O / "c03.jpg", quality=93)
ImageOps.fit(op("viz.jpg"), (W, H), Image.LANCZOS, centering=(.5, .35)).save(O / "cover_bg.jpg", quality=95)
print("ok")
