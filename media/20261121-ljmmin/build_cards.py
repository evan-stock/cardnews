"""20261121-ljmmin: 수능 부정 신고 포상금, 권익위 '최대 1억'(11.19) vs 대통령 X '최소 1억, 행위자 수만큼 가산'(11.21). 프로젝트 채팅에서 만든 4장 구성을 그대로 다시 만듦."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; 
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


fit = lambda img, w, h, c=(.5, .5): ImageOps.fit(img, (w, h), Image.LANCZOS, centering=c)
op = lambda p: Image.open(p).convert("RGB")


def panel(rows, h=640, gap=None):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = gap or (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198)); rich(d, 56, y + 42, v, F("Black", 42))
    return p




fit(op(O / "p1.jpg"), W, H, (.4, .3)).save(O / "cover_bg.jpg", quality=95)

def cap(path, box, w=940, maxh=640):
    im = op(O / path).crop(box); r = w / im.width; im = im.resize((w, int(im.height * r)), Image.LANCZOS)
    if im.height > maxh: im = im.crop((0, 0, w, maxh))
    return im

frame(("11월 21일 오후, 대통령 엑스", "\"최대 1억이 아니라 '최소 1억'\""),
      cap("xembed.png", (0, 0, 1290, 1000)),
      "부정행위자 수만큼 '더 얹어 준다'", "이재명 대통령 X 게시물 캡처(11.21)").save(O / "c02.jpg", quality=93)
frame(("그런데 이틀 전 정부 공식 발표는", "신고 포상금 '최대 1억'"),
      cap("segye.png", (0, 400, 1290, 1170)),
      "응시자격 정지 처분이 나와야 '지급'", "국민권익위원회 발표 · 세계일보(11.19)").save(O / "c03.jpg", quality=93)
frame(("부처가 발표한 기준을", "대통령이 엑스로 '직접 정정'"),
      cap("herald.png", (0, 290, 1290, 1215), maxh=680),
      "공식 발표 상한과 대통령 최소액이 '엇갈렸다'", "헤럴드경제 기사 캡처(11.21)").save(O / "c04.jpg", quality=93)
print("ok")
