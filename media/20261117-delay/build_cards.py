"""20261117-delay: 수능 연기 찬반 정리(일타강사 7명 vs 교육부·총리). 표지·CTA lay one + 2~7장 검은 바탕 틀(frame).
사진: X @kingwest0219 게시물 첨부(강사 프로필 사진 7장 + 교육부 로고). 발언은 기사·원본 영상으로 확인한 것만 따옴표."""
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





V = R / "media/20261117-delay/video"
P = {k: Image.open(V / f"p1_{i}.jpg").convert("RGB") for i, k in enumerate(["mimi", "jiyoung", "seungje", "doyoung", "daejong", "jungsik", "woojin", "moe"], 1)}


def fit(img, w, h, c=(.5, .2)):
    return ImageOps.fit(img, (w, h), Image.LANCZOS, centering=c)


def pair(a, b, h=640):
    w = (940 - 16) // 2; p = Image.new("RGB", (940, h), (10, 10, 12))
    p.paste(fit(P[a], w, h), (0, 0)); p.paste(fit(P[b], w, h), (w + 16, 0)); return p


def label(p, names):
    """사진 아래쪽에 이름 딱지"""
    d = ImageDraw.Draw(p); f = F("ExtraBold", 30); n = len(names); w = p.width // n
    for i, t in enumerate(names):
        tw = d.textlength(t, font=f); x = i * w + (w - tw) / 2
        d.rounded_rectangle((x - 16, p.height - 64, x + tw + 16, p.height - 18), 10, fill=(0, 0, 0))
        d.text((x, p.height - 30), t, font=f, fill=YE, anchor="ls")
    return p


moe = Image.new("RGB", (940, 640), (255, 255, 255)); lg = P["moe"]; lg = lg.resize((900, round(lg.height * 900 / lg.width)), Image.LANCZOS)
moe.paste(lg, (20, (640 - lg.height) // 2))
frame(("영어 조정식 · 국어 유대종", "대책 없으면 '연기해야'"), label(pair("jungsik", "daejong"), ["조정식", "유대종"]),
      "가장 '강경'한 연기론", "16일 각자 SNS·영상으로 입장").save(O / "c02.jpg", quality=93)
frame(("수학 정승제 · 현우진", "\"의심 있는 시험 보게 해선 '안 돼'\""), label(pair("seungje", "woojin"), ["정승제", "현우진"]),
      "현우진도 '대책 부족하면 연기 검토'", "정승제는 '항공 보안급 입실 검사' 제안").save(O / "c03.jpg", quality=93)
frame(("미미미누 · 과학 윤도영", "'조건부' 연기론"), label(pair("mimi", "doyoung"), ["미미미누", "윤도영"]),
      "윤도영 \"확실한 방안 있을 때만, 길어야 '2주'\"", "미미미누는 수능 연기 검토 요구").save(O / "c04.jpg", quality=93)
frame(("사탐 이지영은 한발 물러서", "\"연기를 '직접' 주장하는 게 아니다\""), label(fit(P["jiyoung"], 940, 640), ["이지영"]),
      "그래도 '연기 포함 비상 대책' 준비하라", "\"20년 강의 중 이런 위기는 처음\"").save(O / "c05.jpg", quality=93)
frame(("반대는 정부 단 한 곳", "교육부 \"수능 '연기는 없다'\""), moe,
      "총리도 '예정대로' 치른다", "장관은 '연기하면 더 큰 혼란' 우려").save(O / "c06.jpg", quality=93)
panel = Image.new("RGB", (940, 640), (24, 24, 28)); d = ImageDraw.Draw(panel)
rows = [("시험장 1,312곳", "'스마트안경 전담 요원' 1명 이상"), ("매 교시", "모든 안경 '점검'"), ("적발 시", "시험 무효 + 응시 제한 1년→'3년' 추진"), ("전파 차단", "'법적·기술적 한계'로 검토 안 해")]
for i, (k, v) in enumerate(rows):
    y = 70 + i * 140; d.text((60, y), k, font=F("Medium", 34), fill=(190, 190, 198)); rich(d, 60, y + 46, v, F("Black", 44))
frame(("대신 내놓은 대책", "결국 '사람 눈'"), panel, "모레(19일) 그대로 치른다", "교육부 발표(11.16~17)").save(O / "c07.jpg", quality=93)
# 표지 배경: 강사 7명 격자(어둡게)
bg = Image.new("RGB", (W, H), (12, 12, 14)); ks = ["mimi", "jiyoung", "seungje", "doyoung", "daejong", "jungsik", "woojin"]
cw, ch = W // 4, 440
for i, k in enumerate(ks[:4]): bg.paste(fit(P[k], cw, ch), (i * cw, 0))
cw2 = W // 3
for i, k in enumerate(ks[4:]): bg.paste(fit(P[k], cw2, ch), (i * cw2, ch))
bg.save(O / "cover_bg.jpg", quality=95)
print("ok")
