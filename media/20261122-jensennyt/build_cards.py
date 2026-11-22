"""20261122-jensennyt: NYT(11.20) 젠슨 황 20년 폭언 경영. 본문 장 = 실제 기사 캡처(로고·제목·부제가 이어진 한 화면, debug shot clean) + 검은 바탕 틀(frame)."""
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
    p = photo; py = 300  # 예전 게시물(20261121-ljmmin)과 같은 위치
    rich_center(d, py - 132, top[0], F("Medium", 46), FG); rich_center(d, py - 64, top[1], F("Black", 54), FG)
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, py), m)
    d = ImageDraw.Draw(im); y = py + p.height + 92
    rich_center(d, y, bottom, F("Black", 46), YE)
    if sub: rich_center(d, y + 62, sub, F("Medium", 32), (190, 190, 198))
    logo(im); return im


op = lambda n: Image.open(O / n).convert("RGB")


def cap(name, y0, y1, w=940, maxh=780, x1=860, pad=0):
    im = op(name); im = im.crop((0, y0, min(x1, im.width), y1))
    if pad: im = ImageOps.expand(im, pad, fill=(255, 255, 255))
    h = round(im.height * w / im.width)
    if h > maxh: w, h = round(im.width * maxh / im.height), maxh
    return im.resize((w, h), Image.LANCZOS)


frame(("뉴욕타임스 11월 20일(현지) 보도", "\"직원들이 너무 '부자'가 됐다\""), cap("cl_sedaily2.jpg", 215, 645),
      "남은 방법은 '모욕'이었다", "서울경제 기사 캡처(11.22)").save(O / "c02.jpg", quality=93)
frame(("동료들이 보는 앞에서", "그가 했다는 말"), cap("cl_seoul.jpg", 300, 540, x1=850),
      "\"두 팔 뜯어 '때려죽이겠다'\"까지", "서울신문 기사 캡처(11.22)").save(O / "c03.jpg", quality=93)
frame(("2004년, 처음 막아선 인사 책임자", "'두 달 만에' 해고됐다"), cap("cl_sedaily.jpg", 215, 585),
      "100만 달러(약 14억) 넘는 '비밀 합의'", "서울경제 기사 캡처(11.21)").save(O / "c04.jpg", quality=93)
frame(("2024년 9월, 본인 입으로", "\"해고보다 '고문'해서 위대하게\""), cap("cap_fortune.jpg", 595, 772, pad=16),
      "\"반쯤 농담\"이라며 공개 대담에서", "Fortune 기사 캡처(2024.9.5)").save(O / "c05.jpg", quality=93)
print("ok")
