"""괌 호텔 취소 편지 재구성 이미지(1080x1350). 글은 위쪽 ~60%에, 아래는 카드 글자 자리."""
import random
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = "/home/claude/cardnews/assets/fonts/"
PEN = FONTS + "NanumPenScript-Regular.ttf"
OUT = "/home/claude/cardnews/media/20261022-guamletter/cand/"
W, H = 1080, 1350
random.seed(7)


def desk():
    """어두운 나무 책상 느낌 배경."""
    im = Image.new("RGB", (W, H), (38, 28, 22))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 3):
        v = random.randint(-8, 8)
        d.line([(0, y), (W, y + random.randint(-6, 6))], fill=(46 + v, 33 + v, 25 + v), width=2)
    im = im.filter(ImageFilter.GaussianBlur(2))
    # 위에서 떨어지는 따뜻한 조명
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((-200, -350, W + 200, 900), fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    im = Image.composite(Image.new("RGB", (W, H), (120, 95, 70)), im, glow.point(lambda p: p // 2))
    return im


def paper(lines, size, lh, top_pad, width, height, highlights=(), sign=None):
    """줄 공책 편지지에 손글씨. highlights: 형광펜 칠할 (줄번호, 시작글자, 끝글자)."""
    pw, ph = width, height
    p = Image.new("RGBA", (pw, ph), (250, 244, 228, 255))
    d = ImageDraw.Draw(p)
    f = ImageFont.truetype(PEN, size)
    # 줄
    for y in range(top_pad + lh - 14, ph - 20, lh):
        d.line([(50, y), (pw - 40, y)], fill=(170, 195, 220, 255), width=2)
    d.line([(86, 0), (86, ph)], fill=(232, 150, 150, 255), width=2)
    hl = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    for i, ln in enumerate(lines):
        y = top_pad + i * lh
        for (li, a, b) in highlights:
            if li == i:
                x0 = 110 + d.textlength(ln[:a], font=f)
                x1 = 110 + d.textlength(ln[:b], font=f)
                hd.rounded_rectangle((x0 - 6, y + lh * 0.28, x1 + 6, y + lh * 0.86), 8, fill=(255, 216, 77, 170))
    p = Image.alpha_composite(p, hl)
    d = ImageDraw.Draw(p)
    for i, ln in enumerate(lines):
        y = top_pad + i * lh
        d.text((110 + random.randint(-2, 2), y + random.randint(-2, 2)), ln, font=f, fill=(35, 40, 70, 255))
    # 종이 결
    noise = Image.effect_noise((pw, ph), 10).convert("L").point(lambda v: 255 - abs(v - 128) // 6)
    p = Image.composite(p, Image.new("RGBA", (pw, ph), (225, 215, 195, 255)), noise)
    return p


def place(bg, p, x, y, angle):
    p = p.rotate(angle, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", p.size, (0, 0, 0, 0))
    sh.putalpha(p.getchannel("A").point(lambda a: 150 if a else 0))
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    bg = bg.convert("RGBA")
    bg.alpha_composite(sh, (x + 14, y + 22))
    bg.alpha_composite(p, (x, y))
    return bg.convert("RGB")


def page(name, lines, size=52, lh=74, highlights=(), angle=-1.5, top=36, height=None):
    bg = desk()
    height = height or (60 + top + len(lines) * lh + 40)
    p = paper(lines, size, lh, 60, 960, height, highlights)
    bg = place(bg, p, 46, top, angle)
    bg.save(OUT + name, quality=93)
    print(name, height)


# 1) 표지 배경: 편지 끝부분 크게(아래 글자 자리는 비움)
cover = [
    "내 예약을 취소해주던지,",
    "예약자 이름을 '미스 팍'에서",
    "'미스 야마다'로 바꾸던지",
    "둘 중 하나를 해주길 바라.",
    "",
    "from. 너의 달콤한 예비 고객,",
    "                         야마다.",
]
page("letter_cover.jpg", cover, size=68, lh=96, highlights=[(2, 1, 7), (6, 25, 28)], angle=-2.2, top=70, height=900)

# 2) 편지 앞부분
p1 = [
    "To. 괌의 그 호텔",
    "",
    "헬로, 난 너의 호텔에 숙박하기로 한",
    "미스 팍이라고 해.",
    "너도 알다시피 코로나로 전 세계가",
    "도그판이 됐잖니.",
    "물론 너희가 그런 이유로 예약 취소를",
    "해주는 너그러운 호텔이 아닌 건 알아.",
    "벌써 한국인 21명 정도가 너희의 단호한",
    "태도에 깊은 감명을 받아, 우리 민족 고유의",
    "격한 표현이 포함된 후기를 올렸거든.",
]
page("letter_p1.jpg", p1, size=58, lh=80, angle=1.2, top=40)

# 3) 문제의 문단
p2 = [
    "취소를 요구했더니 날짜 변경 말고는",
    "아무것도 해줄 수 없다고 했다며.",
    "하지만 대체 어떤 날짜로 바꿔야",
    "너희 호텔에 갈 수 있을까?",
    "한국에서 출발하는 비행기들이",
    "괌 운항을 중단했어.",
    "이제 내가 괌에 갈 수 있는 유일한 방법은",
    "대한해협을 헤엄쳐 일본에 밀입국한 다음,",
    "일본인 한 명을 살해하고",
    "신분을 강탈하는 것뿐이야.",
]
page("letter_p2.jpg", p2, size=58, lh=82, highlights=[(7, 0, 9)], angle=-1.0, top=40)

# 4) 마무리
p3 = [
    "너희가 원한다면,",
    "어쩔 수 없이 나는 그것을 실행해야겠지.",
    "",
    "내 예약을 취소해주던지,",
    "예약자 이름을 미스 팍에서",
    "미스 야마다로 바꾸던지",
    "둘 중 하나를 해주길 바라.",
    "",
    "from. 너의 달콤한 예비 고객, 야마다.",
]
page("letter_p3.jpg", p3, size=60, lh=86, highlights=[(5, 0, 6), (8, 20, 23)], angle=1.4, top=40)
