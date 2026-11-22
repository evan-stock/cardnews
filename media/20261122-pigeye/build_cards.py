"""20261122-pigeye: 이 대통령 X(11.22) 순방 비판 반박 '불안견불 돈안견돈'. 인용은 경향·파이낸셜·네이트(국민일보)·경북도민일보 기사에 실린 문장 그대로. 야당 반응은 10월 최보윤 수석대변인 발언(이번 글 직접 반응은 미확인)."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; 
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


fit = lambda img, w, h, c=(.5, .5): ImageOps.fit(img, (w, h), Image.LANCZOS, centering=c)
op = lambda p: Image.open(p).convert("RGB")


def panel(rows, h=640, gap=None):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = gap or (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198)); rich(d, 56, y + 42, v, F("Black", 42))
    return p




fit(op(O / "press04.jpg"), W, H, (.55, .3)).save(O / "cover_bg.jpg", quality=95)

frame(("22일 이재명 대통령 엑스", "\"불안견불 '돈안견돈'\""),
      panel([("고사 풀이", "부처 눈엔 부처만, '돼지 눈엔 돼지만'"),
             ("겨냥", "\"순방 가는 대통령이 '놀러 가는 것'으로\""),
             ("고충", "\"치아가 흔들리고 '코피'까지 자주 터지는\""),
             ("덧붙임", "\"표현이 거칠다는 '비방은 자제' 바란다\"")], h=640),
      "\"임기 초 순방은 꼭 해야 할 '국정과제'\"", "이재명 대통령 X 게시글(11.22)").save(O / "c02.jpg", quality=93)

frame(("처음이 아니다", "또다시 꺼낸 '돼지 눈'"),
      panel([("10월 말", "순방 비판에 X로 처음 '돼지 눈' 표현"),
             ("11월 2일", "'부적절' 지적엔 '한문' 쓰면 다르냐 반박"),
             ("11월 16~19일", "필리핀 아세안 · 중국 'APEC' 순방"),
             ("11월 22일", "'잦은 순방' 비판에 고사 '재인용'")], h=640),
      "순방 논란 때마다 같은 답", "국민일보·경향신문 보도").save(O / "c03.jpg", quality=93)

frame(("순방, 외유인가 국익인가", "여야 '정면충돌'"),
      panel([("국민의힘 (10월)", "야당 땐 '혈세 낭비', 집권하니 '링거 투혼'?"),
             ("청와대 성기홍 수석", "캐나다 총리는 '닷새 중 하루' 정상외교"),
             ("민주당 전은수 원내대변인", "순방 '횟수' 아닌 '성과'로 평가해야")], h=640),
      "국민의힘, 순방 '횟수·체류 일수' 문제 삼아", "경북도민일보·국민일보 보도").save(O / "c04.jpg", quality=93)
print("ok")
