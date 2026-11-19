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


# 2장: 해명문 첫머리(실명 가림)
frame(("'노베이스 6개월 합격' 감평사", "오늘 올린 '2차 해명문'"),
      cap("p1_1.jpg", (0, 200, 943, 1000), blur=[(595, 410, 720, 470)]),
      "\"추측과 의문이 '해소되지 않아' 다시 씁니다\"", "온라인 커뮤니티 캡처 · 11.19").save(O / "c02.jpg", quality=93)
# 3장: 베이스 관련(서울대 학사·석사)
frame(("\"회계·경제 지식 없이 6개월\"이라더니", "\"서울대 학사·도시계획학 '석사'\""),
      cap("p1_5.jpg", (40, 1030, 920, 1590), mark=[(0, 26, 880, 196)]),
      "\"학술적 글쓰기에 '익숙한 상태'로 시작\"", "2차 해명문 중 '3. 베이스 관련'").save(O / "c03.jpg", quality=93)
# 4장: 6개월 설명 사과
frame(("그러면서 처음으로 사과", "\"6개월로 설명한 건 '부적절'\""),
      cap("p1_6.jpg", (40, 1150, 920, 1850), mark=[(0, 520, 880, 650)]),
      "\"이전 지식의 영향을 '간과'했다\"", "2차 해명문 캡처").save(O / "c04.jpg", quality=93)
# 5장: 부정행위는 부인
frame(("AI 부정행위 의혹은 '부인'", "\"휴대폰은 입실 후 '꺼뒀다'\""),
      cap("p1_1.jpg", (40, 1500, 920, 1940)),
      "\"수사가 진행되면 밝혀질 사실\"", "2차 해명문 중 '1. AI 사용 등 부정행위 관련'").save(O / "c05.jpg", quality=93)
# 6장: 공부 인증 사진
frame(("의문 제기된 '계산기·포스트잇' 사진엔", "\"3월에 찍은 1차 공부 사진\""),
      cap("p1_8.jpg", (69, 845, 872, 1495)),
      "성적은 189명 중 '150등'… \"수석과는 거리 멀다\"", "해명문 캡처 / 한국경제(11.18)").save(O / "c06.jpg", quality=93)
cap("p1_5.jpg", (0, 700, 943, 1880), mark=[(40, 356, 920, 526)], w=1080, maxh=1350).save(O / "cover_src.jpg", quality=95)
fit("cover_src.jpg", W, H, (.5, .3)).save(O / "cover_bg.jpg", quality=95)
print("ok")
