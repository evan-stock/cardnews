#!/usr/bin/env python3
"""비행기 그림자를 둘러싼 무지개 고리(글로리) 모션그래픽(카드 영상 칸 1080x780) — 2026.11.08 오늘의쓸모.
  python3 scripts/story_shorts/anim_glory.py <출력폴더>
  → sun.mp4   (옆에서 본 그림: 해 → 내 비행기 → 구름이 일직선, 구름 위 그림자 둘레에 무지개 고리가 피어남)
    drop.mp4  (구름 물방울 한 알: 가장자리로 들어간 빛이 안을 돌아 '왔던 쪽'으로 되돌아 나오며 색이 갈라짐)
    seat.mp4  (위에서 본 비행기: 해 반대편 창가 자리에서만 보임 + 구름 바로 위를 날 때)
근거: NASA APOD 2016.12.22 'An Airplane Glory', 홍콩 천문대 'The mysterious glory'(해를 등지고 물방울이 빛을 뒤로 흩뜨림,
      보는 사람은 자기 그림자 둘레의 글로리만 봄, 바깥이 빨강·안쪽이 파랑), AOPA 2025.9 'Pilot's halo', 위키백과 Glory (optical phenomenon).
"""
import math, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); SUN = (255, 196, 40); DARK = (30, 34, 44)
RAINBOW = [(150, 70, 230), (60, 110, 255), (40, 190, 110), (240, 220, 40), (255, 140, 30), (235, 50, 50)]  # 안쪽 파랑 → 바깥 빨강
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def grad(top, bot):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line((0, y, W, y), fill=tuple(int(a + (b - a) * k) for a, b in zip(top, bot)))
    return img


SKY = grad((70, 130, 210), (175, 205, 238))
NIGHT = grad((24, 32, 52), (44, 58, 86))


def run(name, dur, bg, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = bg.copy()
        draw(img, i / FPS)
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=5):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def plane_side(d, cx, cy, s=1.0, col=(240, 242, 248)):
    """옆에서 본 여객기(오른쪽을 향함)"""
    d.rounded_rectangle((cx - 90 * s, cy - 13 * s, cx + 90 * s, cy + 13 * s), int(13 * s), fill=col, outline=(60, 70, 90), width=3)
    d.polygon([(cx - 80 * s, cy - 8 * s), (cx - 110 * s, cy - 48 * s), (cx - 92 * s, cy - 48 * s), (cx - 55 * s, cy - 8 * s)], fill=col, outline=(60, 70, 90))
    d.polygon([(cx - 15 * s, cy + 4 * s), (cx + 25 * s, cy + 4 * s), (cx - 35 * s, cy + 30 * s), (cx - 55 * s, cy + 30 * s)], fill=(200, 205, 215), outline=(60, 70, 90))
    for k in range(6):
        x = cx - 40 * s + k * 18 * s
        d.ellipse((x - 3 * s, cy - 6 * s, x + 3 * s, cy), fill=(60, 90, 140))


def glory(img, cx, cy, r, k, squash=1.0, width=9):
    """무지개 고리(안쪽 파랑 → 바깥 빨강), k = 0~1 피어남"""
    if k <= 0:
        return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for i, c in enumerate(RAINBOW):
        rr = r * (0.62 + 0.08 * i) * (0.5 + 0.5 * k)
        ld.ellipse((cx - rr, cy - rr * squash, cx + rr, cy + rr * squash), outline=c + (int(220 * k),), width=width)
    lay = lay.filter(ImageFilter.GaussianBlur(3))
    img.paste(lay, (0, 0), lay)


def clouds(d, y0):
    d.rectangle((0, y0, W, H), fill=(236, 238, 244))
    for x in range(-40, W + 80, 110):
        d.ellipse((x, y0 - 34, x + 150, y0 + 40), fill=(236, 238, 244))


# ① 해 → 내 비행기 → 구름 일직선
def sun(img, t):
    d = ImageDraw.Draw(img)
    clouds(d, 600)
    sx, sy = 120, 150
    d.ellipse((sx - 52, sy - 52, sx + 52, sy + 52), fill=SUN)
    for k in range(12):
        a = k * math.pi / 6 + t
        d.line((sx + 64 * math.cos(a), sy + 64 * math.sin(a), sx + 84 * math.cos(a), sy + 84 * math.sin(a)), fill=SUN, width=6)
    px, py = 450, 360
    gx, gy = px + (px - sx) * (600 - py) / (py - sy), 600  # 해-비행기 연장선이 구름에 닿는 점
    k = ease(t / 0.9)
    # 햇빛 선(해 → 비행기 → 구름)
    ex = sx + (gx - sx) * k; ey = sy + (gy - sy) * k
    for s in range(0, 100, 4):
        a = s / 100; b = (s + 2) / 100
        if b > k:
            break
        d.line((sx + (gx - sx) * a, sy + (gy - sy) * a, sx + (gx - sx) * b, sy + (gy - sy) * b), fill=YEL, width=6)
    plane_side(d, px, py, 1.35)
    if t > 0.8:  # 구름 위 그림자
        a = clamp((t - 0.8) / 0.3)
        d.ellipse((gx - 46, gy - 9, gx + 46, gy + 9), fill=tuple(int(236 - 120 * a) for _ in range(3)))
        glory(img, gx, gy, 120, ease((t - 1.0) / 0.9), squash=0.28, width=10)
        d = ImageDraw.Draw(img)
    ctext(d, 540, 30, "해 → 내 비행기 → 구름, 일직선", 54, fill=YEL)
    if t > 1.5:
        ctext(d, 600, 480, "구름에 비친 '내 비행기' 그림자", 44)
    if t > 2.2:
        ctext(d, 600, 690, "그 둘레에 무지개 고리", 44, fill=(40, 40, 50), stroke=0)


# ② 물방울 한 알
def drop(img, t):
    d = ImageDraw.Draw(img)
    cx, cy, R = 600, 420, 230
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(70, 120, 190), outline=(170, 210, 255), width=6)
    d.ellipse((cx - R * 0.55, cy - R * 0.75, cx - R * 0.25, cy - R * 0.5), fill=(150, 195, 245))
    # 들어오는 흰 빛: 왼쪽에서 물방울 위쪽 가장자리로
    k1 = ease(t / 0.6)
    entry = (cx - R * 0.15, cy - R * 0.99)
    start = (40, entry[1])
    d.line((start[0], start[1], start[0] + (entry[0] - start[0]) * k1, entry[1]), fill=WHITE, width=10)
    # 안을 돌기: 원 둘레를 따라
    if t > 0.6:
        k2 = ease((t - 0.6) / 0.8)
        a0 = math.radians(-96); a1 = a0 + math.radians(250) * k2
        pts = [(cx + (R - 14) * math.cos(a0 + (a1 - a0) * j / 40), cy + (R - 14) * math.sin(a0 + (a1 - a0) * j / 40)) for j in range(41)]
        d.line(pts, fill=WHITE, width=8)
    # 되돌아 나오는 빛: 왼쪽으로, 색이 갈라짐
    if t > 1.4:
        k3 = ease((t - 1.4) / 0.7)
        a = math.radians(-96 + 250)
        ox, oy = cx + R * math.cos(a), cy + R * math.sin(a)
        for i, c in enumerate(RAINBOW):
            ang = math.radians(180 + (i - 2.5) * 3.2)
            L = 520 * k3
            d.line((ox, oy, ox + L * math.cos(ang), oy + L * math.sin(ang)), fill=c, width=7)
        d = ImageDraw.Draw(img)
    ctext(d, 540, 28, "구름 물방울 한 알 (실제 지름 0.02mm 안팎)", 44)
    if t > 0.7:
        ctext(d, 540, 100, "가장자리로 들어간 빛이 안을 돌아", 50, fill=YEL)
    if t > 1.7:
        ctext(d, 540, 680, "'왔던 쪽'으로 되돌아 나오며 색이 갈라진다", 46, fill=YEL)


# ③ 어디 앉아야 보이나 — 위에서 본 비행기
def seat(img, t):
    d = ImageDraw.Draw(img)
    cx, cy = 540, 420
    # 동체(위에서 본)
    d.rounded_rectangle((cx - 60, cy - 250, cx + 60, cy + 250), 60, fill=(235, 238, 245), outline=(60, 70, 90), width=4)
    d.polygon([(cx - 60, cy - 30), (cx - 330, cy + 60), (cx - 330, cy + 100), (cx - 60, cy + 50)], fill=(215, 220, 230), outline=(60, 70, 90))
    d.polygon([(cx + 60, cy - 30), (cx + 330, cy + 60), (cx + 330, cy + 100), (cx + 60, cy + 50)], fill=(215, 220, 230), outline=(60, 70, 90))
    d.polygon([(cx - 20, cy + 210), (cx - 120, cy + 270), (cx + 120, cy + 270), (cx + 20, cy + 210)], fill=(215, 220, 230), outline=(60, 70, 90))
    # 창가 줄
    for k in range(9):
        y = cy - 190 + k * 26
        d.rectangle((cx - 52, y, cx - 40, y + 14), fill=(60, 90, 140))
        d.rectangle((cx + 40, y, cx + 52, y + 14), fill=(60, 90, 140))
    # 해: 왼쪽
    sx, sy = 110, 300
    d.ellipse((sx - 56, sy - 56, sx + 56, sy + 56), fill=SUN)
    ctext(d, sx, sy + 66, "해", 40, fill=YEL)
    # 해 반대편(오른쪽) 창가 강조 + 그쪽 구름에 고리
    if t > 0.5:
        a = clamp((t - 0.5) / 0.4)
        pul = 0.5 + 0.5 * math.sin(t * 7)
        d.rectangle((cx + 34, cy - 196, cx + 58, cy + 40), outline=(255, int(120 + 100 * pul), 40), width=6)
        ctext(d, 820, 250, "해 반대편 창가", 46, fill=YEL)
        d = ImageDraw.Draw(img)
    if t > 0.9:
        glory(img, 880, 650, 110, ease((t - 0.9) / 0.8), squash=0.55, width=9)
        d = ImageDraw.Draw(img)
        d.ellipse((865, 642, 895, 658), fill=(90, 95, 110))
    if t > 1.6:
        ctext(d, 540, 28, "구름 바로 위를 날 때, 해를 등진 쪽", 50)


run("sun", 3.3, SKY, sun)
run("drop", 3.3, NIGHT, drop)
run("seat", 3.1, SKY, seat)
print("done", OUT)
