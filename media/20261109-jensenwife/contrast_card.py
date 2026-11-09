"""20261109-jensenwife: 대조 카드(6월 유퀴즈 '숙제 보여줄까?' ↔ 11월 메일 '불충실했습니다'). 1080x1350.
사용: python media/20261109-jensenwife/contrast_card.py
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "scripts"))
from xpost_cards import W, H, P, BG, FG, MU, YE, LN, BOX, F, logo  # noqa: E402

C = Path(__file__).resolve().parent / "cand"


def rounded(im, img, x, y, w):
    h = round(img.height * w / img.width)
    img = img.resize((w, h), Image.LANCZOS)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 24, fill=255)
    im.paste(img, (x, y), m)
    ImageDraw.Draw(im).rounded_rectangle((x, y, x + w - 1, y + h - 1), 24, outline=LN, width=3)
    return y + h


def main():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    y = 96
    d.text((P, y), "2026년 6월 10일 · tvN 유퀴즈", font=F("SemiBold", 32), fill=YE)
    y += 58
    y = rounded(im, Image.open(C / "yq_hands.jpg").convert("RGB"), P, y, W - 2 * P)
    y += 18
    d.text((P, y), "\"17살에 아내 만나고 쇼핑을 끊었어요\" · 방송 자막", font=F("Medium", 30), fill=MU)
    y += 66
    # 5개월 뒤 화살표
    cx = W // 2
    d.line((cx, y, cx, y + 70), fill=YE, width=5)
    d.polygon([(cx - 18, y + 60), (cx + 18, y + 60), (cx, y + 88)], fill=YE)
    t = "5개월 뒤"
    f = F("Black", 44)
    d.text((cx + 34, y + 14), t, font=f, fill=YE)
    y += 116
    d.text((P, y), "2026년 11월 8일 · 전 직원에게 보낸 메일", font=F("SemiBold", 32), fill=YE)
    y += 58
    bh = 250
    d.rounded_rectangle((P, y, W - P, y + bh), 28, fill=BOX, outline=LN, width=3)
    d.text((P + 40, y + 36), "I was unfaithful to my wife.", font=F("Medium", 38), fill=(205, 208, 214))
    d.rectangle((P + 40, y + 104, P + 96, y + 108), fill=YE)
    ko = [("\"아내에게 ", FG), ("불충실", YE), ("했습니다\"", FG)]
    x = P + 40
    for s, c in ko:
        d.text((x, y + 134), s, font=F("Black", 64), fill=c)
        x += d.textlength(s, font=F("Black", 64))
    y += bh + 30
    d.text((P, y), "상대는 미 정보당국이 중국 스파이로 보는 앨리스 황입니다.", font=F("Medium", 32), fill=FG)
    y += 50
    print("bottom", y)
    logo(im)
    im.save(C / "contrast.jpg", quality=93)


if __name__ == "__main__":
    main()
