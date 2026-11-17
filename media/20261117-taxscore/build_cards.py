"""20261117-taxscore(속보): 헤럴드경제 단독 — 세무사 1차 회계학개론 90점 이상 1명(2024)·2명(2025)→66명(2026), 33배.
자료: 한국산업인력공단→안철수 의원실. 표지는 사진 대신 막대그래프(저작권 없는 자체 그래픽).
"""
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



# 표지 배경: 막대그래프
bg = Image.new("RGB", (W, H), (12, 12, 16)); d = ImageDraw.Draw(bg)
base = 840; top = 150; mx = 66
bars = [("2024", 1, "1명"), ("2025", 2, "2명"), ("2026", 66, "66명")]
bw = 210; xs = [150, 435, 720]
for (yr, v, lab), x in zip(bars, xs):
    h = max(10, (base - top - 90) * v / mx); col = YE if v == 66 else (90, 90, 100)
    d.rounded_rectangle((x, base - h, x + bw, base), 14, fill=col)
    d.text((x + bw / 2, base - h - 24), lab, font=F("Black", 64 if v == 66 else 52), fill=col if v == 66 else (200, 200, 208), anchor="ms")
    d.text((x + bw / 2, base + 60), yr, font=F("ExtraBold", 40), fill=(170, 170, 178), anchor="ms")
d.line((110, base, 970, base), fill=(70, 70, 80), width=3)
d.text((W / 2, 95), "세무사 1차 회계학개론 90점 이상 득점자", font=F("ExtraBold", 38), fill=(200, 200, 208), anchor="ms")
bg.save(O / "cover_bg.jpg", quality=95)

frame(("1차 회계학개론 90점 이상 득점자", "1년 새 '33배' 폭증"),
      panel([("2024년", "1명 · 최고점 90점"), ("2025년", "2명 · 최고점 95점"), ("2026년(올해)", "'66명' · 최고점 '100점'")], h=520),
      "2차 회계학도 1부 '5명'·2부 '2명' 90점↑", "한국산업인력공단 자료(안철수 의원실)").save(O / "c02.jpg", quality=93)
frame(("수석 합격자가 자백한 수법", "'초소형 카메라' + AI"),
      panel([("① 촬영", "초소형 카메라로 '시험 문제' 촬영"), ("② 전송", "AI로 보내 '풀이'"), ("③ 확인", "스마트폰으로 '답' 확인")], h=520),
      "\"개인의 일탈이 아니라, '조직범죄'를 의심해야\"", "안철수 의원").save(O / "c03.jpg", quality=93)
frame(("한국산업인력공단의 답", "시험 땐 '신고 0건'"),
      panel([("시험 당시", "부정행위 의심 신고·특이사항 '없었다'"), ("앞으로", "최근 3~5년 합격자 점수 분포 '재점검'"), ("의심 사례", "나오면 '정밀조사'")], h=520),
      "이미 합격한 사람도 '다시 본다'", "헤럴드경제·국민일보(11.17)").save(O / "c04.jpg", quality=93)
print("ok")
