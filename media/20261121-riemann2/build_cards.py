"""20261121-riemann2: 클로드 리만 가설 증명 주장(알푀게 메모 11.20) — 캡처·자료화면 위주 판.
표지: 메모 원문 캡처(빨간 테두리) + 리만 가설 수식 카드 + 상금 줄 + 제타 함수 그래프 원형."""
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


def cover():
    cv = Image.new("RGBA", (W, H), (244, 244, 241, 255))
    # 1) 위키백과 '리만 가설' 첫 문단 캡처 + 빨간 테두리
    wk = op("shot01.png")
    a = wk.crop((30, 580, 1100, 822)); k = 1040 / a.width; a = a.resize((1040, round(a.height * k)), Image.LANCZOS)
    cv.paste(a, (20, 90)); d = ImageDraw.Draw(cv)
    d.rectangle((20 + (186 - 30) * k, 90 + (586 - 580) * k, 20 + (345 - 30) * k, 90 + (640 - 580) * k), outline=(226, 30, 30), width=6)
    # 2) 위키백과 리만 가설 공식 상자 캡처
    b = wk.crop((40, 880, 1080, 1125)); kb = 960 / b.width; b = b.resize((960, round(b.height * kb)), Image.LANCZOS)
    shadow_paste(cv, b, 40, 90 + a.height + 40)
    # 3) 상금 줄
    d = ImageDraw.Draw(cv); f = F("SemiBold", 40); y = 660
    t1, t2, t3 = "리만 가설 해결 상금은 ", "100만 달러", " 입니다"
    w1, w2, w3 = (d.textlength(t, font=f) for t in (t1, t2, t3))
    d.rectangle((40, y - 14, 40 + w1 + w2 + w3 + 48, y + 62), fill=(255, 255, 255))
    d.rounded_rectangle((64 + w1 - 6, y - 4, 64 + w1 + w2 + 6, y + 52), 8, fill=(214, 230, 255))
    d.text((64, y), t1, font=f, fill=(30, 30, 34)); d.text((64 + w1, y), t2, font=f, fill=(30, 30, 34)); d.text((64 + w1 + w2, y), t3, font=f, fill=(30, 30, 34))
    # 4) 제타 함수 0점 그래프(위키미디어) 원형
    g = ImageOps.fit(op("press13.jpg"), (380, 380), Image.LANCZOS, centering=(.55, .5))
    ring = Image.new("RGBA", (400, 400), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, 399, 399), fill=(255, 255, 255, 255))
    m = Image.new("L", (380, 380), 0); ImageDraw.Draw(m).ellipse((0, 0, 379, 379), fill=255)
    ring.paste(g.convert("RGBA"), (10, 10), m)
    shadow_paste(cv, Image.new("RGB", (1, 1)), -100, -100)  # no-op 안전
    sh = Image.new("RGBA", (480, 480), (0, 0, 0, 0)); sm = Image.new("L", (400, 400), 0); ImageDraw.Draw(sm).ellipse((0, 0, 399, 399), fill=120)
    sh.paste((0, 0, 0, 255), (40, 52), sm); sh = sh.filter(ImageFilter.GaussianBlur(18)); cv.alpha_composite(sh, (640, 560))
    cv.alpha_composite(ring, (680, 600))
    cv.convert("RGB").save(O / "cover_bg.jpg", quality=95)


cover()
print("ok")


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


# 2장: 알푀게 메모 원문(빨간 표시) + 본인 사진
memo_full = op("memo.png").crop((130, 20, 1110, 300))
ov = memo_full.copy(); dd = ImageDraw.Draw(ov); dd.rectangle((250, 8, 520, 50), outline=(226, 30, 30), width=5)
p_al = ImageOps.fit(op("alpoge.jpg"), (940, 300), Image.LANCZOS, centering=(.62, .3))
frame(("11월 20일, 앤트로픽 수학자 알푀게", "\"클로드와 함께 '증명' 찾았다\""),
      stack(boxed(ov), ImageOps.fit(op("alpoge.jpg"), (940, 220), Image.LANCZOS, centering=(.62, .3))), "\"결승선 앞에서 클로드가 '날아다녔다'\"", "알푀게 개인 웹사이트 메모 원문 · 사진: 본인 사이트", body=("같은 방법으로 '일반화 리만 가설'까지 풀었다고 주장했고,", "증명은 컴퓨터가 검사하는 언어(Lean) 코드로 공개했습니다")).save(O / "c02.jpg", quality=93)

# 3장: 위키백과 리만 가설(밀레니엄 문제 상자)
frame(("167년 동안 아무도 못 푼", "'밀레니엄 7대 난제'"),
      stack(cap("shot01.png", (30, 580, 1100, 822)), cap("shot01.png", (1130, 1130, 1760, 1530), w=940, maxh=230)),
      "소수가 흩어진 방식에 숨은 '규칙'", "위키백과 '리만 가설' 화면", body=("1859년 독일 수학자 리만이 내놓은 가설로,", "2, 3, 5, 7처럼 불규칙해 보이는 소수에도", "정해진 패턴이 있다는 주장입니다")).save(O / "c03.jpg", quality=93)

# 4장: 클레이수학연구소 'Unsolved'
frame(("풀면 상금 '100만 달러'", "클레이연구소엔 아직 '미해결'"),
      cap("shot04.png", (0, 120, 1800, 1000), mark=[(60, 440, 400, 520)]),
      "학술지 게재 뒤 '2년' 검증해야 인정", "클레이수학연구소 홈페이지 화면", body=("지금도 공식 페이지엔 'Unsolved'(미해결)로 나옵니다", "주장이 맞는지 수학자들이 검증을 막 시작했습니다")).save(O / "c04.jpg", quality=93)

# 5장: 제타 함수 그래프
frame(("증명했다는 건 이것", "0은 전부 '한 줄' 위에 있다"),
      boxed(op("press13.jpg").crop((0, 80, 1000, 920)), w=620, bg=(255, 255, 255), pad=10),
      "가운데 세로선(실수부 1/2) = '임계선'", "리만 제타 함수 그래프 · 위키미디어 공용", body=("리만 가설은 '의미 있는 0은 모두 이 선 위에 있다'는 것", "지금까지 수조 개를 확인했지만 증명은 없었습니다")).save(O / "c05.jpg", quality=93)
print("inner ok")
