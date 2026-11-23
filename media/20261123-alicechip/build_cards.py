"""20261123-alicechip: 앨리스 황 칩 밀수망·프린스그룹 연결(FT 11.21, 이데일리·한경·서울경제 11.22). 의혹 보도, 단정 안 함."""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
MATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
op = lambda n: Image.open(O / n).convert("RGB")


def shadow_paste(base, img, x, y, rad=10, blur=16, alpha=110):
    sh = Image.new("RGBA", (img.width + 80, img.height + 80), (0, 0, 0, 0))
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), rad, fill=alpha)
    sh.paste((0, 0, 0, 255), (40, 50), m); sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(sh, (x - 40, y - 40))
    mm = Image.new("L", img.size, 0); ImageDraw.Draw(mm).rounded_rectangle((0, 0, img.width - 1, img.height - 1), rad, fill=255)
    base.paste(img.convert("RGBA"), (x, y), mm)



fit = lambda img, w, h, c=(.5, .5): ImageOps.fit(img, (w, h), Image.LANCZOS, centering=c)
# ── 안쪽 장: 캡처·자료화면 위주(검은 바탕 frame 틀) ──
import re
YE = (255, 216, 77); FG = (255, 255, 255)


def rich_center(d, y, text, font, base):
    parts = re.split(r"('[^']*')", text); tw = sum(d.textlength(p.strip("'"), font=font) for p in parts if p)
    x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=font)


def logo(im):
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
    lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)


def frame(top, photo, bottom, sub=None, body=()):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    p = photo; m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300), m)
    d = ImageDraw.Draw(im); y = 300 + p.height + 92
    rich_center(d, y, bottom, F("Black", 44), YE); y += 64
    for ln in body:
        rich_center(d, y, ln, F("Medium", 36), (235, 235, 240)); y += 52
    if sub: rich_center(d, y + (14 if body else 0), sub, F("Medium", 28), (150, 150, 158))
    logo(im); return im


def cap(name, box, w=940, maxh=760, mark=()):
    im = op(name).crop(box)
    if mark:
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(ov)
        for b in mark: dd.rectangle(b, fill=(255, 216, 77, 90))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    h = round(im.height * w / im.width)
    if h > maxh: im = im.crop((0, 0, im.width, round(maxh * im.width / w))); h = maxh
    return im.resize((w, h), Image.LANCZOS)


def stack(a, b, gap=16):
    im = Image.new("RGB", (940, a.height + gap + b.height), (10, 10, 12)); im.paste(a, (0, 0)); im.paste(b, (0, a.height + gap)); return im


def boxed(img, w=940, bg=(255, 255, 255), pad=30):
    k = (w - 2 * pad) / img.width; img = img.resize((w - 2 * pad, round(img.height * k)), Image.LANCZOS)
    b = Image.new("RGB", (w, img.height + 2 * pad), bg); b.paste(img, (pad, pad)); return b



# 2장: 이데일리 기사 화면
frame(("FT 탐사보도를 받은 국내 보도", "\"한국인 감금 조직과도 '연결고리'\""),
      cap("shot01.png", (0, 990, 1490, 1580)),
      "젠슨 황 연인 앨리스 황이 얽힌 '칩 밀수망'", "이데일리 화면(2026.11.22)",
      body=("파이낸셜타임스가 소식통 10여 명과 수백 개 기업 공시를 분석해", "엔비디아 칩이 중국으로 빠져나간 경로를 추적했습니다")).save(O / "c02.jpg", quality=93)

# 3장: 앨리스 황
frame(("중국 데이터센터 업계에선", "'젠슨의 개인비서'로 불렸다"),
      ImageOps.fit(op("press11.jpg"), (940, 560), Image.LANCZOS, centering=(.35, .4)),
      "싱가포르 메가스피드의 '얼굴' 역할", "앨리스 황(왼쪽)과 젠슨 황 · 사진: AFP 연합뉴스",
      body=("2023년 중국 게임사 싱가포르 법인을 사들여 메가스피드로 바꾸고", "경력에 흠 없는 '믿을 만한' 대외 임원을 맡았습니다")).save(O / "c03.jpg", quality=93)

# 4장: 프린스그룹
frame(("그 밀수망 끝에 있던 조직", "한국인 감금 '태자단지' 배후"),
      stack(ImageOps.fit(op("press03.jpg"), (940, 360), Image.LANCZOS), cap("shot03.png", (0, 520, 1100, 900), maxh=210)),
      "프린스그룹 2인자 후샤오웨이가 칩 운반 일부 맡아", "프린스은행 간판 · 위키백과 'Prince Group' 화면",
      body=("미국·영국이 사기 범죄단지 운영으로 제재한 캄보디아 기업입니다", "후샤오웨이는 올여름 일본에서 체포됐습니다")).save(O / "c04.jpg", quality=93)

# 5장: 한국 게임과의 연결
frame(("후샤오웨이가 돈을 번 곳은", "한국 게임 '미르의 전설'"),
      ImageOps.fit(op("press10.jpg"), (940, 520), Image.LANCZOS, centering=(.6, .4)),
      "불법 사설 서버로 큰돈, 게임은 '돈세탁' 통로", "앨리스 황(오른쪽) · 사진: 연합뉴스/AFP",
      body=("그의 조직은 위메이드 '미르의 전설' 사설 서버를 운영했고", "앨리스 황 남편이 투자한 중국 게임사가 두 사람을 잇는 고리였습니다")).save(O / "c05.jpg", quality=93)

# 6장: 경로와 규모
frame(("엔비디아 → 미국 자회사 → 메가스피드", "→ 동남아 → '중국 암시장'"),
      ImageOps.fit(op("press04.jpg"), (940, 520), Image.LANCZOS),
      "1년 수입 신고만 '6조 원'(46억 달러)", "사진: SBS",
      body=("인도네시아 경찰이 메가스피드 현지 법인을 급습했을 땐", "칩이 빠진 '빈 서버랙'만 남아 있었습니다")).save(O / "c06.jpg", quality=93)

# 7장: 반론
frame(("반론도 있다", "\"불법 네트워크 '없다'\""),
      cap("shot04.png", (480, 1590, 1800, 2080), mark=[(0, 400, 1320, 490)]),
      "엔비디아 \"메가스피드는 2025년 '차단' 명단에\"", "한국경제 화면(2026.11.22)",
      body=("프린스그룹은 후샤오웨이가 회사에서 일한 적 없다고 반박했고", "WSJ는 실제 운영자는 다른 중국인이라고 보도했습니다")).save(O / "c07.jpg", quality=93)

fit(op("press01.jpg"), W, H, (.55, .4)).save(O / "cover_bg.jpg", quality=95)
print("ok")
