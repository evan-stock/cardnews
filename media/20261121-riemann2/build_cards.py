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
    # 1) 알푀게 메모 원문 첫 문장 캡처 + 'working with Claude' 빨간 테두리
    memo = op("memo.png").crop((130, 22, 1110, 97))
    k = 1040 / memo.width; memo = memo.resize((1040, round(memo.height * k)), Image.LANCZOS)
    cv.paste(memo, (20, 150))
    d = ImageDraw.Draw(cv)
    x0, x1 = 20 + (383 - 130) * k - 8, 20 + (652 - 130) * k + 6
    d.rectangle((x0, 150 + (28 - 22) * k, x1, 150 + (66 - 22) * k), outline=(226, 30, 30), width=6)
    d.text((40, 110), "레벤트 알푀게 메모 원문 (2026.11.20)", font=F("Medium", 28), fill=(120, 120, 126))
    # 2) 리만 가설 수식 카드
    card = Image.new("RGB", (900, 210), (250, 250, 250)); cd = ImageDraw.Draw(card)
    cd.text((40, 30), "ζ(s) = 0  ⇒  Re(s) = 1/2", font=ImageFont.truetype(MATH, 58), fill=(30, 30, 34))
    cd.line((40, 118, 860, 118), fill=(210, 210, 214), width=2)
    cd.text((40, 140), "리만 제타 함수의 자명하지 않은 모든 0은 실수부가 1/2이다", font=F("Medium", 32), fill=(60, 60, 66))
    shadow_paste(cv, card, 40, 330)
    # 3) 상금 줄
    d = ImageDraw.Draw(cv); f = F("SemiBold", 40); y = 600
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
    sh.paste((0, 0, 0, 255), (40, 52), sm); sh = sh.filter(ImageFilter.GaussianBlur(18)); cv.alpha_composite(sh, (640, 520))
    cv.alpha_composite(ring, (680, 560))
    cv.convert("RGB").save(O / "cover_bg.jpg", quality=95)


cover()
print("ok")
