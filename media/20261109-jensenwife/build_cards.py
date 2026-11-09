"""20261109-jensenwife: '숙제 보여줄까?'로 만난 41년 + 이혼 시 재산분할 단순 계산. 1080x1350, 디자인 v2 색·글꼴.
연도 챕터 카드(하단 타임라인) + 계산 카드. 사용: python media/20261109-jensenwife/build_cards.py
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "scripts"))
from xpost_cards import W, H, P, BG, FG, MU, YE, LN, BOX, F, wrap, logo  # noqa: E402

OUT = Path(__file__).resolve().parent / "cand"
TL = ["1980", "1985", "1993", "2026"]


def rich_lines(d, x, y, lines, font, lh, base=FG):
    hl = False
    for ln in lines:
        cx = x
        buf = ""
        for c in ln + "\0":
            if c in "'\0":
                if buf:
                    d.text((cx, y), buf, font=font, fill=YE if hl else base)
                    cx += d.textlength(buf, font=font)
                    buf = ""
                if c == "'":
                    hl = not hl
            else:
                buf += c
        y += lh
    return y


def timeline(d, cur):
    y = H - 190
    x0, x1 = P + 20, W - P - 20
    d.line((x0, y, x1, y), fill=LN, width=3)
    step = (x1 - x0) / (len(TL) - 1)
    for i, t in enumerate(TL):
        x = x0 + i * step
        on = t == cur
        r = 13 if on else 8
        d.ellipse((x - r, y - r, x + r, y + r), fill=YE if on else (90, 92, 98))
        f = F("Black" if on else "SemiBold", 30 if on else 26)
        tw = d.textlength(t, font=f)
        d.text((x - tw / 2, y + 24), t, font=f, fill=YE if on else MU)


def chapter(name, year, sub, title, body, cur=None, top=150):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    ft, fb = F("Black", 72), F("Medium", 39)
    tl = title.split("\n")
    bl = [wrap(d, para, fb, W - 2 * P) for para in body]
    block = 190 + 76 + len(tl) * 94 + 38 + 44 + sum(len(b) * 60 + 16 for b in bl)
    top = max(110, int((H - 250 - block) / 2) + 10)
    d.text((P - 6, top), year, font=F("Black", 160), fill=YE)
    y = top + 200
    d.text((P, y), sub, font=F("SemiBold", 36), fill=MU)
    y += 76
    y = rich_lines(d, P, y, tl, ft, 94)
    y += 38
    d.rectangle((P, y, P + 64, y + 5), fill=YE)
    y += 44
    for b in bl:
        y = rich_lines(d, P, y, b, fb, 60) + 16
    if y > H - 230:
        print("경고: 타임라인과 겹침", name, y)
    timeline(d, cur or year)
    logo(im)
    im.save(OUT / f"{name}.jpg", quality=93)
    print(name, "top", top, "bottom", y)


def calc_card():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    y = 110
    d.text((P, y), "만약 이혼한다면 · 단순 계산", font=F("SemiBold", 32), fill=YE)
    y += 58
    y = rich_lines(d, P, y, ["아내 몫은 약 '110조 원'"], F("Black", 64), 84) + 20
    rows = [
        ("젠슨 황 순자산", "1,622억 달러", "약 220조 원 · 포브스 11월 9일"),
        ("그중 엔비디아 주식", "99%", "엔비디아 지분 약 3.4%"),
        ("결혼 → 창업", "1985 → 1993", "주식은 전부 '결혼 중' 생긴 재산"),
        ("캘리포니아 법", "절반씩", "부부가 함께 번 재산은 원칙적으로 반분"),
    ]
    bx0, bx1 = P, W - P
    bh = 4 * 118 + 150
    d.rounded_rectangle((bx0, y, bx1, y + bh), 28, fill=BOX, outline=LN, width=3)
    ry = y + 34
    for k, (a, b, c) in enumerate(rows):
        d.text((bx0 + 36, ry), a, font=F("SemiBold", 30), fill=MU)
        fb = F("Black", 44)
        d.text((bx1 - 36 - d.textlength(b, font=fb), ry - 6), b, font=fb, fill=FG)
        rich_lines(d, bx0 + 36, ry + 52, [c], F("Medium", 28), 40, base=(190, 194, 200))
        ry += 118
        if k < len(rows) - 1:
            d.line((bx0 + 36, ry - 22, bx1 - 36, ry - 22), fill=LN, width=2)
    d.rectangle((bx0 + 36, ry - 8, bx1 - 36, ry - 4), fill=YE)
    d.text((bx0 + 36, ry + 22), "아내 몫", font=F("Black", 40), fill=YE)
    fb = F("Black", 56)
    t = "811억 달러"
    d.text((bx1 - 36 - d.textlength(t, font=fb), ry + 10), t, font=fb, fill=YE)
    y += bh + 22
    d.rounded_rectangle((bx0, y, bx1, y + 112), 22, fill=(40, 34, 12), outline=YE, width=2)
    rich_lines(d, bx0 + 30, y + 18, ["국내 '세기의 이혼' 최태원·노소영 재산분할", "9,440억 원(2026.7 파기환송심)의 '100배' 넘는 금액"], F("SemiBold", 30), 42)
    y += 112 + 20
    for ln in ["이혼 얘기는 나온 적 없습니다. 혼전·혼후 계약 여부도",
               "알려지지 않았습니다. 지분 상당수는 부부가 함께",
               "관리하는 신탁에 있습니다. (계산: 아시아경제 11.9)"]:
        d.text((P, y), ln, font=F("Medium", 28), fill=MU)
        y += 42
    if y > H - 100:
        print("경고: calc 로고 겹침", y)
    logo(im)
    im.save(OUT / "calc.jpg", quality=93)
    print("calc bottom", y)


def photos():
    src = R / "media/20261109-jensenspy/cand"
    a = Image.open(src / "press24.jpg").convert("RGB")
    ImageOps.fit(a, (1080, 1350), centering=(0.36, 0.3)).save(OUT / "cover.jpg", quality=94)
    b = Image.open(src / "press07.jpg").convert("RGB")
    ImageOps.fit(b, (1080, 1350), centering=(0.3, 0.4)).save(OUT / "stage.jpg", quality=93)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    photos()
    calc_card()
    chapter("c1985", "1985", "만난 지 5년, 결혼",
            "\"서른 살에 'CEO'가\n되겠습니다\"",
            ["결혼해 달라며 로리에게 한 약속이었습니다.",
             "그리고 1993년, 정말 서른 살에 엔비디아를 세웠습니다."])
    chapter("c1993", "1993", "엔비디아 창업 직전",
            "아내가 건 조건,\n\"'둘이 같이' 그만둬라\"",
            ["공동창업자 맬러카우스키도 다니던 회사를 함께 그만둬야 남편도 그만둘 수 있다고 했습니다.", "맬러카우스키의 아내도 같은 조건이었습니다. (책 <The Nvidia Way>)"])
