"""20261119-leetsearch: 리트 만점자 소재 수색(모텔→아차산 방향→택시 송파 방향) + 수사 착수·수능 시험지 증거보전. 실명 안 씀, 로프·극단 추측 안 씀. leetjail/build_cards.py 복사."""
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




frame(("전날 집 나선 뒤 '광진구 모텔'로", "오늘 아침, 그곳도 빠져나갔다"),
      panel([("전날", "집 나선 뒤 '귀가 안 해'"), ("밤", "광진구의 한 모텔에 '투숙'"), ("오늘 오전 8시 2분", "모텔 나와 '아차산 방향' 이동"), ("오전 8시 42분", "'신변 우려' 신고 접수"), ("오전 9시 21분", "초동대응팀 출동, 산 일대 'CCTV' 확인")], h=700),
      "경찰, 동선 따라 '아차산 일대' 수색", "이데일리·경기신문·아주경제(11.19)").save(O / "c02.jpg", quality=93)
frame(("이어 오전 8~9시께", "택시 타고 '송파구 방향'으로"),
      panel([("수색 지역", "광진구 → '송파구'로 넓혀"), ("마지막 공개 행적", "전날 한 언론사 '인터뷰'"), ("휴대전화", "전날부터 '꺼진 상태'"), ("경찰", "\"개인적 사안이라 '확인해줄 수 없다'\"")], h=640),
      "아직 '소재 확인 안 돼'", "연합뉴스(11.19)").save(O / "c03.jpg", quality=93)
frame(("행방 찾는 사이", "수사는 '본격화'"),
      panel([("수사팀", "서울청 광역수사단 '금융범죄수사대'"), ("혐의", "'사기·업무방해' 등 고발 2건"), ("증거보전", "'2026학년도 수능 시험지' 요청"), ("보관 장소", "응시한 고교에 '그대로 남아'")], h=640),
      "신병 확보 등 '강제수사' 불가피 전망", "파이낸셜뉴스·한국경제·연합뉴스(11.19)").save(O / "c04.jpg", quality=93)
print("ok")
