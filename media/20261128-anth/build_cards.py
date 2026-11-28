"""20261128-anth: 앤트로픽 투자 주의 이유(3번 검은 바탕 틀). 캡처: 미주갤 인스타(디시 원글), 머니투데이·테크노밸류 기사 화면(debug shot)."""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; V = D / "video"
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
LOGO = Image.open(R / "brand/logo_typo_A.png").convert("RGBA")


def rich_center(d, y, text, font, base):
    parts = re.split(r"('[^']*')", text); tw = sum(d.textlength(p.strip("'"), font=font) for p in parts if p)
    x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=font)


def logo(im):
    lh = 40; lg = LOGO.resize((int(LOGO.width * lh / LOGO.height), lh), Image.LANCZOS)
    im.paste(lg, ((W - lg.width) // 2, H - 62 - lh), lg)


def frame(top, photo, bottom, sub=None):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    p = photo
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300), m)
    d = ImageDraw.Draw(im); y = 300 + p.height + 92
    rich_center(d, y, bottom, F("Black", 46), YE)
    if sub: rich_center(d, y + 62, sub, F("Medium", 30), (190, 190, 198))
    logo(im); return im


def stackcap(paths, w=940, maxh=700, bg=(255, 255, 255)):
    ims = [Image.open(p).convert("RGB") for p in paths]
    ims = [i.resize((w, round(i.height * w / i.width)), Image.LANCZOS) for i in ims]
    h = sum(i.height for i in ims) + 20 * (len(ims) - 1)
    c = Image.new("RGB", (w, h), bg); y = 0
    for i in ims: c.paste(i, (0, y)); y += i.height + 20
    if c.height > maxh:
        k = maxh / c.height; s = c.resize((round(w * k), maxh), Image.LANCZOS)
        c = Image.new("RGB", (w, maxh), bg); c.paste(s, ((w - s.width) // 2, 0))
    return c.filter(ImageFilter.UnsharpMask(1.5, 50, 2))


def crop(name, box):  # 300폭 축소본 기준 좌표
    im = Image.open(O / f"{name}.jpg"); k = im.width / 300
    out = O / f"_{name}_{box[1]}.png"; im.crop(tuple(round(v * k) for v in box)).save(out); return out


def panel(rows, h=700):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap
        d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198))
        x = 56
        for part in re.split(r"('[^']*')", v):
            if not part: continue
            hl = part.startswith("'"); part = part.strip("'")
            d.text((x, y + 42), part, font=F("Black", 42), fill=YE if hl else FG); x += d.textlength(part, font=F("Black", 42))
    return p


# 2 커뮤니티 원글(디시 미주갤, 미주갤 인스타 게시물 1장)
dc = Image.open(V / "p1_1.jpg").convert("RGB")
dc = dc.resize((940, round(dc.height * 940 / dc.width)), Image.LANCZOS).crop((0, 0, 940, 700))
frame(("커뮤니티에 퍼진 경고글", "\"진심 '앤트로픽'은 조심해라\""), dc,
      "\"특별주 '1개'가 의결권 50.1%\"", "디시인사이드 미국주식갤러리(11.28)").save(O / "c02.jpg", quality=93)
# 3 클래스F(머니투데이)
frame(("상장 신고서에 담긴 구조", "창업자 7명이 단 '1주'로"),
      stackcap([crop("mt", (25, 30, 185, 70)), crop("mt", (25, 175, 185, 262))]),
      "주총 일반 안건 의결권 '50.1%'", "배당 권리·양도는 없음 · 머니투데이(10.27)").save(O / "c03.jpg", quality=93)
# 4 일반 주주는 49.9%(테크노밸류 칼럼)
frame(("그럼 일반 주주는?", "다 모아도 의결권 '49.9%'"),
      stackcap([crop("sp", (0, 65, 200, 85)), crop("sp", (33, 528, 200, 582))]),
      "이사 7명 중 4명은 '신탁'이 뽑는다", "일반 주식 49.9%는 테크노밸류(11.12) · 스페셜타임스").save(O / "c04.jpg", quality=93)
# 5 번 돈은 컴퓨팅으로(머니투데이 CAPEX + 테크노밸류)
frame(("벌어들인 돈은 어디로?", "2045년까지 '컴퓨팅'에 쏟는다"),
      stackcap([crop("mt", (25, 435, 185, 520))]),
      "인프라 약정 최대 '8000억 달러'", "브로드컴 5년 1252억 달러 계약 · 머니투데이·테크노밸류").save(O / "c05.jpg", quality=93)
# 6 주가·락업
frame(("상장 열흘째 주가", "그리고 다가오는 '락업 해제'"),
      panel([("11.18 공모가", "83달러"), ("11.19 상장 첫날", "97.17달러 (장중 '115달러')"), ("11.25", "82.79달러, 공모가 '아래로'"),
             ("11.27", "91.88달러"), ("12.15", "첫 락업 해제 약 '3억 주'")], h=700),
      "풀리는 물량 > 지수 편입 매수", "CNBC·Crypto Briefing·Investing.com · 종가 기준").save(O / "c06.jpg", quality=93)
print("ok")
