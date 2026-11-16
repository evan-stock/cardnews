"""93세 할머니 보이스피싱 역함정 재현 그래픽(2026.10.27 오쓸 TTS 릴스 2편).
letterbox 레이아웃 영상 영역 1080x780, 30fps. 장면마다 g1~g7.mp4.
사용: python scripts/story_shorts/anim_grandma.py <작업폴더> <출력폴더> [장면번호...]"""
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 780, 30
FB = "assets/fonts/Pretendard-Black.otf"
FS = "assets/fonts/Pretendard-SemiBold.otf"
BG = (20, 24, 33); YEL = (255, 212, 59); RED = (235, 60, 60); WHITE = (255, 255, 255)
NAVY = (38, 70, 140); SKIN = (246, 205, 170); HAIR = (205, 205, 210); LAV = (170, 140, 200)
DARK = (55, 55, 62); GREEN = (80, 200, 120); GRAY = (130, 138, 150)
_f = {}


def F(size, path=FB):
    k = (size, path)
    if k not in _f:
        _f[k] = ImageFont.truetype(path, size)
    return _f[k]


def ease(t):
    return 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3


def pop(t):  # 0→1 살짝 튀어오르며
    if t <= 0:
        return 0
    if t >= 1:
        return 1
    return 1 + 0.25 * math.sin(t * math.pi) * (1 - t) + (ease(t) - 1)


def text(d, xy, s, size, fill=WHITE, anchor="mm", a=255, path=FB, stroke=5):
    d.text(xy, s, font=F(size, path), fill=fill + (a,), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, a))


def grandma(d, x, y, s=1.0, a=255):
    """할머니: 보라 옷, 흰 머리 쪽, 안경. (x,y)=발 가운데."""
    b = lambda v: int(v * s)
    d.rounded_rectangle((x - b(70), y - b(190), x + b(70), y), b(40), fill=LAV + (a,))
    hx, hy = x, y - b(240)
    d.ellipse((hx - b(18), hy - b(88), hx + b(18), hy - b(52)), fill=HAIR + (a,))  # 쪽
    d.ellipse((hx - b(55), hy - b(55), hx + b(55), hy + b(55)), fill=SKIN + (a,))
    d.chord((hx - b(58), hy - b(60), hx + b(58), hy + b(40)), 180, 360, fill=HAIR + (a,))
    for ox in (-22, 22):
        d.ellipse((hx + b(ox) - b(15), hy - b(5), hx + b(ox) + b(15), hy + b(25)), outline=DARK + (a,), width=max(2, b(5)))
    d.line((hx - b(7), hy + b(10), hx + b(7), hy + b(10)), fill=DARK + (a,), width=max(2, b(4)))
    d.arc((hx - b(18), hy + b(22), hx + b(18), hy + b(42)), 20, 160, fill=DARK + (a,), width=max(2, b(4)))


def person(d, x, y, body, head=SKIN, cap=None, s=1.0, a=255, hood=False):
    b = lambda v: int(v * s)
    d.rounded_rectangle((x - b(65), y - b(190), x + b(65), y), b(36), fill=body + (a,))
    hx, hy = x, y - b(240)
    if hood:
        d.ellipse((hx - b(66), hy - b(66), hx + b(66), hy + b(62)), fill=body + (a,))
    d.ellipse((hx - b(50), hy - b(50), hx + b(50), hy + b(50)), fill=head + (a,))
    if cap:
        d.chord((hx - b(54), hy - b(62), hx + b(54), hy + b(18)), 180, 360, fill=cap + (a,))
        d.rectangle((hx - b(54), hy - b(24), hx + b(70), hy - b(12)), fill=cap + (a,))
        d.ellipse((hx - b(10), hy - b(52), hx + b(10), hy - b(32)), fill=YEL + (a,))
    for ox in (-18, 18):
        d.ellipse((hx + b(ox) - b(6), hy - b(2), hx + b(ox) + b(6), hy + b(10)), fill=DARK + (a,))


def police(d, x, y, s=1.0, a=255):
    person(d, x, y, NAVY, cap=(25, 40, 90), s=s, a=a)
    d.text((x, y - int(110 * s)), "POLICE", font=F(int(26 * s)), fill=YEL + (a,), anchor="mm")


def scammer(d, x, y, s=1.0, a=255):
    person(d, x, y, (40, 40, 46), head=(220, 185, 150), s=s, a=a, hood=True)
    b = lambda v: int(v * s)
    d.rectangle((x - b(40), y - b(250), x + b(40), y - b(225)), fill=(15, 15, 18, a))  # 선글라스 띠


def phone(d, x, y, s=1.0, ang=0, a=255, screen=(40, 50, 70)):
    b = lambda v: int(v * s)
    im = Image.new("RGBA", (b(260), b(440)), (0, 0, 0, 0))
    pd = ImageDraw.Draw(im)
    pd.rounded_rectangle((0, 0, b(260), b(440)), b(40), fill=(230, 232, 238, a))
    pd.rounded_rectangle((b(16), b(40), b(244), b(400)), b(22), fill=screen + (a,))
    return im.rotate(ang, resample=Image.BICUBIC, expand=True)


def house(d, x, y, a=255, door_open=0.0):
    """집: (x,y)=바닥 가운데. 폭 520."""
    d.polygon([(x - 300, y - 330), (x, y - 520), (x + 300, y - 330)], fill=(150, 70, 60, a))
    d.rectangle((x - 260, y - 330, x + 260, y), fill=(225, 210, 180, a))
    d.rectangle((x - 210, y - 270, x - 70, y - 150), fill=(120, 170, 220, a), outline=(90, 70, 50, a), width=8)
    dx0, dx1 = x + 60, x + 200
    d.rectangle((dx0, y - 230, dx1, y), fill=(40, 30, 25, a))
    w = int((dx1 - dx0) * (1 - door_open))
    d.rectangle((dx0, y - 230, dx0 + w, y), fill=(120, 80, 45, a))
    if w > 20:
        d.ellipse((dx0 + w - 28, y - 120, dx0 + w - 12, y - 104), fill=YEL + (a,))


def stamp(img, s, t, color=RED, x=None, y=None, size=110, rot=-12):
    """도장처럼 쾅 찍히는 글자."""
    if t <= 0:
        return img
    k = 1.8 - 0.8 * ease(t / 0.35)
    a = int(255 * min(1, t / 0.2))
    fnt = F(size)
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    bw = td.textlength(s, font=fnt) + 70
    box = Image.new("RGBA", (int(bw), size + 60), (0, 0, 0, 0))
    bd = ImageDraw.Draw(box)
    bd.rounded_rectangle((4, 4, box.width - 4, box.height - 4), 18, outline=color + (a,), width=10)
    bd.text((box.width // 2, box.height // 2), s, font=fnt, fill=color + (a,), anchor="mm")
    box = box.resize((max(1, int(box.width * k)), max(1, int(box.height * k)))).rotate(rot, expand=True, resample=Image.BICUBIC)
    cx, cy = (x or W // 2), (y or H // 2)
    img.alpha_composite(box, (int(cx - box.width / 2), int(cy - box.height / 2)))
    return img


def base():
    im = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, 640, W, H), fill=(32, 37, 48, 255))  # 바닥
    return im, d


def label(d):
    d.text((22, 18), "재현 그래픽", font=F(26, FS), fill=(190, 190, 195, 200))


# ── 장면 ────────────────────────────────────────────────
def s1(t):  # 할머니 집, 창문 뒤 숨은 경찰, '93세'
    im, d = base()
    house(d, 560, 650)
    peek = ease((t - 1.2) / 0.6)
    if peek > 0:  # 창문 아래에서 경찰 모자가 쑥
        cy = int(500 - 40 * peek)
        d.rectangle((350, 380, 490, 500), fill=(120, 170, 220, 255))
        for k, cx in enumerate((385, 455)):
            d.ellipse((cx - 30, cy - 30 + k * 6, cx + 30, cy + 30 + k * 6), fill=SKIN)
            d.chord((cx - 33, cy - 40 + k * 6, cx + 33, cy + 6 + k * 6), 180, 360, fill=(25, 40, 90))
        d.rectangle((350, 380, 490, 500), outline=(90, 70, 50), width=8)
        d.line((420, 380, 420, 500), fill=(90, 70, 50), width=6)
    gs = pop(t / 0.5)
    if gs > 0:
        grandma(d, 190, 650, s=0.95 * gs)
    k = pop((t - 0.4) / 0.5)
    if k > 0:
        text(d, (200, 150), "93세", int(120 * k), YEL)
    if t > 2.0:
        a = int(255 * ease((t - 2.0) / 0.4))
        text(d, (870, 150), "경찰 대기 중", 54, WHITE, a=a)
    label(d)
    return im


def s2(t):  # 걸려온 전화 '경찰입니다' → 가짜
    im, d = base()
    ring = t < 3.0
    ang = 8 * math.sin(t * 40) if ring else 0
    ph = phone(d, 0, 0, s=1.15, ang=ang)
    im.alpha_composite(ph, (540 - ph.width // 2, 360 - ph.height // 2))
    d = ImageDraw.Draw(im, "RGBA")
    text(d, (540, 300), "경찰서", 62, WHITE, stroke=0)
    text(d, (540, 370), "전화 왔어요", 34, (200, 205, 215), path=FS, stroke=0)
    d.ellipse((490, 430, 590, 530), fill=GREEN)
    text(d, (540, 480), "통화", 34, WHITE, stroke=0)
    if ring:
        for k in range(3):
            r = 200 + ((t * 160 + k * 60) % 180)
            a = int(160 * (1 - ((t * 160 + k * 60) % 180) / 180))
            d.arc((540 - r, 360 - r, 540 + r, 360 + r), 200, 250, fill=YEL + (a,), width=10)
            d.arc((540 - r, 360 - r, 540 + r, 360 + r), 290, 340, fill=YEL + (a,), width=10)
    a = int(255 * ease((t - 0.3) / 0.4))
    if a > 0:
        d.rounded_rectangle((40, 50, 300, 116), 18, fill=(60, 66, 82))
        text(d, (170, 83), "일본 시가현", 36, YEL, path=FS, stroke=0)
    stamp(im, "가짜 경찰", t - 3.0, x=770, y=560, size=86)
    label(ImageDraw.Draw(im, "RGBA"))
    return im


def s3(t):  # 카드 + 무단 인출 경고 → 수사관이 가지러 감
    im, d = base()
    x = int(-400 + 690 * ease(t / 0.7))
    d.rounded_rectangle((x - 230, 170, x + 170, 420), 26, fill=(40, 110, 200))
    d.rectangle((x - 230, 220, x + 170, 262), fill=(20, 30, 50))
    d.rounded_rectangle((x - 190, 300, x - 120, 350), 8, fill=YEL)
    text(d, (x + 60, 375), "현금카드", 40, WHITE, stroke=0)
    w = pop((t - 0.9) / 0.4)
    if w > 0:
        d.rounded_rectangle((x - 230, 450, x - 230 + int(400 * w), 530), 18, fill=RED)
        if w > 0.8:
            text(d, (x - 30, 490), "! 무단 인출", 46, WHITE, stroke=0)
    g = ease((t - 2.0) / 0.6)
    if g > 0:
        for k in range(int(8 * g)):
            xx = 520 + k * 40
            d.line((xx, 300, xx + 22, 300), fill=YEL, width=8)
        d.polygon([(860, 280), (890, 300), (860, 320)], fill=YEL)
        scammer(d, 960, 640, s=0.9, a=int(255 * g))
        text(d, (850, 110), "\"수사관이 받으러", 40, WHITE, a=int(255 * g))
        text(d, (850, 160), "갈게요\"", 40, WHITE, a=int(255 * g))
    label(d)
    return im


def s4(t):  # 할머니 '!' → 진짜 경찰(110)에 신고
    im, d = base()
    grandma(d, 300, 650, s=1.15)
    k = pop((t - 0.3) / 0.4)
    if k > 0:
        d.ellipse((330, 120, 330 + int(110 * k), 120 + int(110 * k)), fill=YEL)
        text(d, (330 + int(55 * k), 120 + int(55 * k)), "!", int(90 * k), (20, 20, 20), stroke=0)
    g = ease((t - 1.3) / 0.5)
    if g > 0:
        ph = phone(d, 0, 0, s=0.85, screen=(30, 90, 60))
        ph.putalpha(ph.getchannel("A").point(lambda v: int(v * g)))
        im.alpha_composite(ph, (720 - ph.width // 2, 330 - ph.height // 2))
        d = ImageDraw.Draw(im, "RGBA")
        text(d, (720, 280), "110", 92, WHITE, a=int(255 * g), stroke=0)
        text(d, (720, 360), "진짜 경찰", 40, WHITE, a=int(255 * g), path=FS, stroke=0)
    c = ease((t - 2.4) / 0.4)
    if c > 0:
        d.line((620, 640, 680, 700), fill=GREEN + (int(255 * c),), width=18)
        d.line((680, 700, 800, 560), fill=GREEN + (int(255 * c),), width=18)
        text(d, (900, 640), "신고!", 64, GREEN, a=int(255 * c))
    label(d)
    return im


def s5(t):  # 남자가 집 앞에 도착 + 93세 vs 47세 비교
    im, d = base()
    house(d, 330, 650)
    x = int(1250 - 520 * ease(t / 1.4))
    scammer(d, x, 650, s=0.95)
    if t > 1.0:
        a = int(255 * ease((t - 1.0) / 0.3))
        text(d, (x, 300), "47세", 60, WHITE, a=a)
    b = ease((t - 1.8) / 0.8)
    if b > 0:
        d.rounded_rectangle((560, 40, 1050, 260), 22, fill=(0, 0, 0, 150))
        text(d, (630, 100), "93세", 40, YEL, stroke=0)
        d.rounded_rectangle((690, 82, 690 + int(330 * b), 118), 10, fill=YEL)
        text(d, (630, 190), "47세", 40, WHITE, stroke=0)
        d.rounded_rectangle((690, 172, 690 + int(165 * b), 208), 10, fill=WHITE)
        if b > 0.95:
            text(d, (950, 190), "딱 절반", 40, RED, stroke=0)
    label(d)
    return im


def s6(t):  # 문이 열리고 경찰 출동 → 체포
    im, d = base()
    house(d, 330, 650, door_open=ease((t - 0.2) / 0.4))
    sx = 730
    for k, (px, s) in enumerate(((470, 0.9), (610, 0.85), (900, 0.9))):
        e = ease((t - 0.5 - k * 0.25) / 0.5)
        if e > 0:
            police(d, int(px if k < 2 else 1200 - 300 * e), 650, s=s * min(1, e + 0.2), a=int(255 * e))
    scammer(d, sx, 650, s=0.95)
    h = ease((t - 1.7) / 0.4)
    if h > 0:
        for ox in (-22, 22):
            d.ellipse((sx + ox - 26, 500, sx + ox + 26, 552), outline=(200, 200, 210, int(255 * h)), width=10)
    stamp(im, "체포", t - 2.1, x=540, y=200, size=120)
    label(ImageDraw.Draw(im, "RGBA"))
    return im


def s7(t):  # 일당 수사: 가운데 남자 + 물음표 3명
    im, d = base()
    scammer(d, 540, 640, s=0.9)
    for k, (x, y) in enumerate(((180, 300), (900, 280), (220, 600), (880, 600))):
        e = ease((t - 0.4 - k * 0.35) / 0.4)
        if e <= 0:
            continue
        a = int(255 * e)
        for j in range(12):
            fx = 540 + (x - 540) * j / 12
            fy = 420 + (y - 420) * j / 12
            if j % 2 == 0:
                d.ellipse((fx - 5, fy - 5, fx + 5, fy + 5), fill=GRAY + (a,))
        d.ellipse((x - 60, y - 60, x + 60, y + 60), fill=(45, 45, 55, a), outline=GRAY + (a,), width=6)
        text(d, (x, y), "?", 80, YEL, a=a, stroke=0)
    if t > 2.0:
        text(d, (540, 100), "일당 수사 중", 60, WHITE, a=int(255 * ease((t - 2.0) / 0.4)))
    label(d)
    return im


SCENES = {1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 6: s6, 7: s7}

if __name__ == "__main__":
    work, out = sys.argv[1], sys.argv[2]
    pick = [int(x) for x in sys.argv[3:]] or list(SCENES)
    os.makedirs(out, exist_ok=True)
    T = 8.0
    for n in pick:
        wd = f"{work}/g{n}"
        os.makedirs(wd, exist_ok=True)
        for i in range(int(T * FPS)):
            SCENES[n](i / FPS).convert("RGB").save(f"{wd}/f{i:04d}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{wd}/f%04d.png",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", f"{out}/g{n}.mp4"],
                       check=True)
        print("ok", n)
