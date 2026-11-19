"""20261119-gamjeong: 감정평가사 6개월 합격자 2차 해명문(theqoo 캡처, @dopamine_crypto 11.19) + 한국경제·서울신문(11.18~19). 실명 가림."""
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

op = lambda n: Image.open(O / n).convert("RGB")


def cap(name, box, blur=(), mark=(), w=940, maxh=760):
    im = op(name).crop(box)
    for b in blur:  # 실명 가리기(잘라낸 좌표 기준)
        r = im.crop(b).filter(ImageFilter.GaussianBlur(14)); im.paste(r, b[:2])
    if mark:
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(ov)
        for m in mark: dd.rectangle(m, fill=(255, 216, 77, 90))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    h = round(im.height * w / im.width)
    if h > maxh: im = im.crop((0, 0, im.width, round(maxh * im.width / w))); h = maxh
    return im.resize((w, h), Image.LANCZOS)


def stack(a, b, gap=16):
    im = Image.new("RGB", (940, a.height + gap + b.height), (10, 10, 12)); im.paste(a, (0, 0)); im.paste(b, (0, a.height + gap)); return im


# 2장
frame(("세무사 AI 커닝이 터진 직후", "'6개월 합격' 수기에 쏟아진 의심"),
      cap("p1_1.jpg", (0, 200, 943, 1000), blur=[(595, 410, 720, 470)]),
      "결국 해명문을 '두 번' 썼다", "온라인 커뮤니티 캡처 · 11.19").save(O / "c02.jpg", quality=93)
# 3장
frame(("그가 밝힌 '단기 합격'의 이유", "서울대 학사·도시계획학 '석사'"),
      cap("p1_5.jpg", (40, 1030, 920, 1590), mark=[(0, 26, 880, 196)]),
      "\"학술적 글쓰기·도시계획 공부가 '이미' 돼 있었다\"", "2차 해명문 중 '3. 베이스 관련'").save(O / "c03.jpg", quality=93)
# 4장
frame(("'6개월'이라는 표현은", "\"부적절했다\" 먼저 '사과'"),
      cap("p1_6.jpg", (40, 1150, 920, 1850), mark=[(0, 520, 880, 650)]),
      "\"이전 지식의 영향을 '간과'했다\"", "2차 해명문 캡처").save(O / "c04.jpg", quality=93)
# 5장
frame(("부정행위 의혹엔", "\"휴대폰은 입실 후 '꺼뒀다'\""),
      cap("p1_1.jpg", (40, 1500, 920, 1940)),
      "수강 확인서·연습 답안·공부 사진까지 '공개'", "2차 해명문 중 '1. AI 사용 등 부정행위 관련'").save(O / "c05.jpg", quality=93)
# 6장
frame(("해명문의 마지막 말", "\"정당한 노고가 '무시당하지' 않기를\""),
      stack(cap("p1_9.jpg", (40, 690, 920, 1000), mark=[(0, 196, 880, 292)]), cap("p1_8.jpg", (69, 900, 872, 1460), maxh=420)),
      "성적은 189명 중 150등, 부정행위 증거는 '없다'", "2차 해명문 캡처 / 한국경제(11.18)").save(O / "c06.jpg", quality=93)
cap("p1_5.jpg", (0, 700, 943, 1880), mark=[(40, 356, 920, 526)], w=1080, maxh=1350).save(O / "cover_src.jpg", quality=95)
fit("cover_src.jpg", W, H, (.5, .3)).save(O / "cover_bg.jpg", quality=95)
print("ok")
