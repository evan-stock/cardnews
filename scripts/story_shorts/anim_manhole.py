#!/usr/bin/env python3
"""폭우 때 맨홀 뚜껑이 날아가는 원리 — 재연 모션그래픽(카드 영상 칸 1080x780) — 2026.10.28 오늘의쓸모.
  python3 scripts/story_shorts/anim_manhole.py <출력폴더>
  → airpush.mp4 (땅속 단면: 빗물이 하수관으로 밀려들며 갇힌 공기를 맨홀 쪽으로 짓눌러 → 뚜껑이 물기둥과 함께 튀어 오름)
    hidden.mp4  (흙탕물에 잠긴 길: 물 위로는 멀쩡해 보이지만 물속엔 뚜껑 없는 구멍)
    net.mp4     (맨홀 속 추락방지망: 뚜껑이 날아가도 그물이 사람을 받쳐 줌, 450kg 견딤)
"""
import math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
SKY = (40, 46, 62); SOIL = (120, 92, 66); SOIL2 = (100, 76, 54); ROAD = (58, 60, 66); PIPE = (150, 150, 158)
WATER = (60, 130, 220); MUD = (150, 118, 80); AIR = (225, 235, 250); INK = (24, 30, 44)
WHITE = (250, 250, 252); RED = (232, 48, 44); YEL = (255, 210, 60); IRON = (80, 82, 90)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))
random.seed(3)


def run(name, dur, draw, bg=SKY):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), bg)
        draw(img, i / FPS)
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()


def label(d, x, y, s, size, fill=WHITE, center=True):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((x - w / 2 if center else x, y), s, font=ft, fill=fill, stroke_width=5, stroke_fill=(0, 0, 0))


def rain(d, t, y1):
    for k in range(70):
        x = (k * 97 + t * 40) % W
        y = (k * 53 + t * 900) % max(1, y1)
        d.line((x, y, x - 6, y + 26), fill=(150, 170, 200), width=3)


# ---------- 1. 갇힌 공기가 뚜껑을 밀어 올림 ----------
RY = 300            # 도로 표면
SX0, SX1 = 640, 760  # 맨홀 통로(세로)
PY0, PY1 = 560, 700  # 하수관(가로)
AIRP = [(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 6.28)) for _ in range(90)]


def airpush(img, t):
    d = ImageDraw.Draw(img)
    rain(d, t, RY)
    d.rectangle((0, RY, W, H), fill=SOIL)
    for k in range(0, W, 60):
        d.ellipse((k + 10, RY + 60 + (k * 7) % 140, k + 22, RY + 72 + (k * 7) % 140), fill=SOIL2)
    d.rectangle((0, RY, W, RY + 26), fill=ROAD)
    # 관·통로 안쪽(빈 공간)
    d.rectangle((0, PY0, W, PY1), fill=PIPE)
    d.rectangle((0, PY0 + 12, W, PY1 - 12), fill=(36, 40, 52))
    d.rectangle((SX0, RY, SX1, PY0 + 12), fill=PIPE)
    d.rectangle((SX0 + 12, RY + 26, SX1 - 12, PY0 + 14), fill=(36, 40, 52))
    # 빗물이 왼쪽에서 밀려듦: 관 안 물 앞쪽 x
    fill = ease(clamp(t / 2.2))
    wx = 40 + fill * 560
    d.rectangle((0, PY0 + 12, wx, PY1 - 12), fill=WATER)
    for k in range(6):  # 물결 화살표
        ax = (wx - 120 - k * 110 + (t * 260) % 110)
        if 0 < ax < wx - 30:
            d.polygon([(ax + 40, (PY0 + PY1) / 2), (ax, (PY0 + PY1) / 2 - 16), (ax, (PY0 + PY1) / 2 + 16)], fill=(200, 230, 255))
    # 갇힌 공기: 물 앞쪽 ~ 오른쪽 끝 + 통로. 물이 차오를수록 좁은 곳에 빽빽
    burst = clamp((t - 2.25) / 0.25)
    ax0, ax1 = wx + 6, W
    for (u, v, ph) in AIRP:
        if u < 0.65:
            x = ax0 + u / 0.65 * (ax1 - ax0 - 10); y = PY0 + 20 + v * (PY1 - PY0 - 40)
        else:
            x = SX0 + 22 + v * (SX1 - SX0 - 44); y = RY + 40 + (u - 0.65) / 0.35 * (PY0 - RY - 30)
        jit = 3 + 6 * fill
        x += jit * math.sin(t * 9 + ph); y += jit * math.cos(t * 8 + ph)
        if burst > 0 and u >= 0.65:
            y -= burst * 300
        r = 6
        d.ellipse((x - r, y - r, x + r, y + r), fill=AIR)
    # 위로 미는 화살표(점점 커짐)
    if t < 2.3:
        L = 30 + 90 * fill
        cx = (SX0 + SX1) / 2
        d.rectangle((cx - 9, RY + 40, cx + 9, RY + 40 + L), fill=YEL)
        d.polygon([(cx, RY + 10), (cx - 26, RY + 44), (cx + 26, RY + 44)], fill=YEL)
    # 뚜껑
    up = ease(burst) * 250
    rot = burst * 0.6
    lx = (SX0 + SX1) / 2 + burst * 60; ly = RY + 10 - up
    shake = 4 * math.sin(t * 60) * fill if t < 2.25 else 0
    hw = 78
    pts = [(-hw, -10), (hw, -10), (hw, 10), (-hw, 10)]
    pts = [(lx + shake + px * math.cos(rot) - py * math.sin(rot), ly + px * math.sin(rot) + py * math.cos(rot)) for px, py in pts]
    # 물기둥
    if burst > 0:
        top = RY - 20 - 300 * ease(burst)
        d.polygon([(SX0 + 10, RY + 26), (SX1 - 10, RY + 26), (SX1 + 40, top), (SX0 - 40, top)], fill=(170, 200, 235))
        for k in range(14):
            a = k / 14 * math.pi
            rr = 120 + 160 * burst
            x = (SX0 + SX1) / 2 + math.cos(a) * rr; y = RY - math.sin(a) * rr * 0.9
            d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(170, 200, 235))
    d.polygon(pts, fill=IRON, outline=(30, 30, 34))
    label(d, 220, PY1 + 14, "빗물이 한꺼번에", 46)
    label(d, 930, PY1 + 14, "갇힌 공기", 46, fill=YEL)
    if burst > 0.5:
        label(d, 300, 120, "펑!", 110, fill=YEL)


# ---------- 2. 흙탕물 아래 숨은 구멍 ----------
SURF = 330


def hidden(img, t):
    d = ImageDraw.Draw(img)
    rain(d, t, SURF)
    # 단면: 물 위(멀쩡해 보임) / 물속(구멍)
    d.rectangle((0, SURF, W, 560), fill=MUD)
    for k in range(0, W, 40):
        y = SURF + 6 * math.sin(k / 50 + t * 4)
        d.ellipse((k - 26, y - 10, k + 26, y + 10), fill=MUD)
    d.rectangle((0, 560, W, 600), fill=ROAD)
    d.rectangle((0, 600, W, H), fill=SOIL)
    # 뚜껑 없는 구멍
    hx0, hx1 = 600, 760
    d.rectangle((hx0, 560, hx1, H), fill=(14, 14, 18))
    d.rectangle((hx0 + 12, 600, hx1 - 12, H), fill=(26, 26, 30))
    # 깜빡이는 빨간 점선 테두리
    if int(t * 3) % 2 == 0:
        for k in range(hx0 - 20, hx1 + 20, 26):
            d.rectangle((k, 548, k + 14, 556), fill=RED)
    # 사람 다리가 물속을 걸어옴
    px = 120 + ease(clamp(t / 2.6)) * 360
    for side, ph in ((-1, 0), (1, math.pi)):
        sw = 22 * math.sin(t * 6 + ph)
        d.line((px + side * 14, 240, px + side * 14 + sw, 556), fill=(40, 46, 70), width=30)
        d.ellipse((px + side * 14 + sw - 26, 540, px + side * 14 + sw + 26, 566), fill=(20, 22, 30))
    d.rounded_rectangle((px - 46, 130, px + 46, 260), 20, fill=(200, 60, 60))
    d.ellipse((px - 32, 62, px + 32, 126), fill=(240, 200, 170))
    d.line((px + 40, 150, px + 70, 70), fill=(30, 30, 34), width=8)
    d.pieslice((px - 30, 10, px + 170, 110), 180, 360, fill=(60, 90, 200))
    label(d, 760, 120, "물 위에선 그냥 길", 50)
    label(d, (hx0 + hx1) / 2, 640, "구멍", 60, fill=RED)


# ---------- 3. 추락방지망 ----------
def net(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), fill=SOIL)
    for k in range(0, W, 60):
        d.ellipse((k + 10, 300 + (k * 7) % 400, k + 22, 312 + (k * 7) % 400), fill=SOIL2)
    d.rectangle((0, 200, W, 240), fill=ROAD)
    cx0, cx1 = 380, 700
    d.rectangle((cx0, 200, cx1, H), fill=(110, 112, 120))
    d.rectangle((cx0 + 20, 240, cx1 - 20, H), fill=(30, 32, 40))
    # 그물: 통로 위쪽에 걸림
    ny = 330
    sag = 50 * ease(clamp((t - 1.0) / 0.6))
    for k in range(0, 11):
        x = cx0 + 20 + k * (cx1 - cx0 - 40) / 10
        s = sag * math.sin(math.pi * k / 10)
        d.line((x, ny - 10, x, ny + 10 + s), fill=YEL, width=4)
    for j in range(4):
        pts = []
        for k in range(0, 21):
            x = cx0 + 20 + k * (cx1 - cx0 - 40) / 20
            pts.append((x, ny - 10 + j * 7 + sag * math.sin(math.pi * k / 20)))
        d.line(pts, fill=YEL, width=4)
    # 떨어지는 무게(사람 대신 상자 '사람')
    fall = ease(clamp(t / 1.0))
    by = 60 + fall * (ny - 150) + sag * 0.9
    d.rounded_rectangle(((cx0 + cx1) / 2 - 60, by, (cx0 + cx1) / 2 + 60, by + 110), 18, fill=(200, 60, 60))
    label(d, (cx0 + cx1) / 2, by + 26, "사람", 44)
    if t > 1.2:
        label(d, 890, 420, "450kg", 70, fill=YEL)
        label(d, 890, 510, "견딤", 56)
    label(d, 190, 420, "추락", 60)
    label(d, 190, 500, "방지망", 60)


run("airpush", 3.4, airpush)
run("hidden", 3.2, hidden)
run("net", 3.2, net)
print("ok")
