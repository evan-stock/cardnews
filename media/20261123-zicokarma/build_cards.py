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
frame(("2019년, 출근하는 시민에게", "\"부럽네요\" 하고 돌아서서 '조롱'"), pic("old.jpg"),
      "\"야이 ㅋㅋㅋ 내가 '부럽겠냐'\"", "당시 아프리카TV 방송 화면").save(O / "c02.jpg", quality=93)
frame(("결국 '7일 방송 정지'", "장애인 비하 이어 '두 번째'"), cap("ytn.jpg", (0, 0, 860, 520), 520),
      "\"고작 7일? '솜방망이' 징계\" 비판", "YTN(2019.6.20)").save(O / "c03.jpg", quality=93)
frame(("연매출 364억 '엑셀방송 대부'", "\"아이가 학교에서 '놀림'받아\""), pic("iv.jpg", 720),
      "\"학부모들은 날 '범죄 단체 수장'처럼\"", "본인 유튜브 인터뷰 화면").save(O / "c04.jpg", quality=93)
frame(("그리고 2026년 11월", "200억 주식 '-90%'에 생방송 오열"), cap("ss.jpg", (0, 0, 860, 600), 600),
      "\"직원들 급여 밀린 건 '내 잘못'\"", "스포츠서울(11.23) · 주택담보대출 50억도").save(O / "c05.jpg", quality=93)
ImageOps.fit(op("ss.jpg").crop((478, 770, 860, 1440)), (W, H), Image.LANCZOS, centering=(.5, .5)).save(O / "cover_bg.jpg", quality=95)
print("ok")
