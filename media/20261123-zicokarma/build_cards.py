"""20261123-zicokarma: 커맨더지코 '카르마' — 2019 출근길 시민 조롱(7일 정지, YTN) → 아이 놀림 고백(유튜브 인터뷰) → 2026.11 200억 주식 -90% 생방송 오열(스포츠서울).
본문 기사 캡처. 아이 이름은 안 씀. gampy/build_cards.py 복사."""
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
def pic(src, w=940):
    im = op(src); return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
# 2026.11.23 사용자 지시로 방향 바꿈: '엑셀 접고 주식 올인한 이유'(돈 많아도 무시받은 이야기)
def ivp(n, box=None, w=720):
    im = op(n)
    if box: im = im.crop(box)
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
frame(("엑셀방송 그만두는 이유를 묻자", "\"가장 '상처'받게 된 게…\""), ivp("iv1.jpg", (0, 260, 803, 968), 640),
      "연매출 364억 '엑셀방송 대부'의 고백", "본인 유튜브 인터뷰 화면").save(O / "c02.jpg", quality=93)
frame(("학교 다니는 첫째 아이에게", "\"너네 아빠 '지코'ㅋㅋㅋ\""), ivp("iv4.jpg"),
      "\"그걸 또 애가 알아서 '상처' 받아\"", "본인 유튜브 인터뷰 화면").save(O / "c03.jpg", quality=93)
frame(("돈은 벌었지만", "학부모들 시선은 '범죄 단체 수장'"), ivp("iv12.jpg"),
      "\"애들은 죄가 없잖아, 근데 학부모들은…\"", "본인 유튜브 인터뷰 화면").save(O / "c04.jpg", quality=93)
frame(("결국 엑셀방송 '중단' 선언", "\"이제 엑셀은 '이만했으면' 됐다\""), cap("insight.jpg", (0, 0, 868, 500), 480),
      "\"옛 열혈 후원자 절반은 '감옥'에\"", "인사이트(2025.10.17)").save(O / "c05.jpg", quality=93)
frame(("그리고 택한 건 '주식'", "아이온큐에 200억 → '-90%'"), cap("ss.jpg", (0, 0, 860, 600), 600),
      "\"직원들 급여 밀린 건 '내 잘못'\" 생방송 오열", "스포츠서울(11.23) · 주택담보대출 50억도").save(O / "c06.jpg", quality=93)
ImageOps.fit(op("iv6.jpg").crop((0, 0, 927, 680)), (W, H), Image.LANCZOS, centering=(.5, .5)).save(O / "cover_bg.jpg", quality=95)
print("ok")
