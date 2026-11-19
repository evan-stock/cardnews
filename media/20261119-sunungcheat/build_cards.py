"""20261119-sunungcheat: 2027 수능 부정행위 총정리(재난문자 35명·용인 초소형카메라·서초 깔창폰). 교육부·제주의소리·뉴스1·SBS·MBC·싱글리스트(11.19)."""
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


def panel(rows, h=640, gap=None):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = gap or (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198)); rich(d, 56, y + 42, v, F("Black", 42))
    return p



frame(("오전 8시 30분, 시험장마다 '삐'", "켜져 있던 폰 '22대' 들통"),
      fit("press24.jpg", 940, 700, (.35, .5)),
      "오후 2번 더 울려 하루 '35명' 적발", "위급재난문자 화면 · 아시아경제 / 교육부 집계(11.19)").save(O / "c02.jpg", quality=93)
frame(("용인 시험장, 엄단 경고에도", "결국 '초소형 카메라' 나왔다"),
      fit("press32.jpg", 940, 529),
      "재수생 즉시 '퇴실' · 경찰 수사", "SBS 자막뉴스 화면(11.19)").save(O / "c03.jpg", quality=93)
frame(("손톱만 한 이 카메라 하나로", "'시험 무효+형사처벌'"),
      fit("press11.jpg", 940, 700, (.5, .6)),
      "갖고만 있어도 '부정행위'", "시험장 안내문 앞 초소형 카메라(예시) · 국민일보").save(O / "c04.jpg", quality=93)
frame(("서초구 시험장, 2교시 수학 시간", "'신발 깔창' 속에서 벨이 울렸다"),
      fit("press25.jpg", 940, 600),
      "학교가 112 신고, 경찰이 시험장 '안으로'", "MBC·싱글리스트(11.19) / 사진 연합뉴스(자료)").save(O / "c05.jpg", quality=93)
frame(("이 와중에 다시 소환된 사진", "\"차라리 '팬티만' 입고 보자\""),
      fit("press33.jpg", 940, 640),
      "10년 전 인도 군 채용 시험 현장", "한국경제·파이낸셜뉴스(11.17)").save(O / "c06.jpg", quality=93)
frame(("단추마다 '스티커' 붙인다는 말에", "SNS에 돈 '수능날 입으면 연행되는 옷'"),
      fit("meme_jacket.jpg", 940, 600, crop=(108, 20, 1172, 696)),
      "\"스티커 붙이다 시험 끝나겠다\"", "YTN 화면(출처: X) · 11.18").save(O / "c07.jpg", quality=93)
fit("press15.jpg", W, H, (.5, .5)).save(O / "cover_bg.jpg", quality=95)
print("ok")
