#!/usr/bin/env python3
"""물에 잠긴 땅의 구멍이 만드는 소용돌이 — 모션그래픽(카드 영상 칸 1080x780) — 2026.11.14 오늘의쓸모.
  python3 scripts/story_shorts/anim_whirl.py <출력폴더>
  → hole.mp4 (단면: 물에 잠긴 풀밭 아래 '땅속 구멍' → 물이 사방에서 구멍으로 몰림 → 떠 있던 나무가 끌려감)
    spin.mp4 (위에서 본 모습: 아주 느린 회전이 가운데로 모이며 점점 빨라짐(피겨 스핀처럼, 각운동량) → 가운데 공기 구멍)
근거: 원촬영자 자막 "There's a hole in the ground"(TikTok @mnnature_awesomeness, 2023.04 세인트크로이강 범람),
      Andersen 외 2003 Physical Review Letters 91, 104502 'Anatomy of a Bathtub Vortex'(물이 배수구로 모이며 회전이 빨라지고 가운데 공기 기둥),
      Nerdist 2020(물리 교사 Mark Eichenlaub — 도는 방향은 코리올리 힘이 아니라 원래 물에 있던 회전 때문).
"""
import math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
SKY = (150, 170, 190); WATER = (60, 92, 110); WATER_D = (36, 62, 80); GROUND = (92, 70, 48); GROUND_D = (66, 48, 32)
GRASS = (96, 130, 60); WHITE = (250, 250, 252); RED = (232, 48, 44); YEL = (255, 210, 60); FLOW = (190, 230, 250)
TREE = (40, 110, 60); TRUNK = (110, 80, 50)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))
SURF, GY = 230, 470          # 수면 y, 땅(풀밭) y
HX, HW = 540, 70             # 구멍 x 중심, 폭/2
random.seed(7)


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), WATER)
        draw(img, i / FPS)
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=5):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def arrow(d, x0, y0, x1, y1, col, w=7, head=20):
    d.line((x0, y0, x1, y1), fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0)
    pts = [(x1, y1), (x1 - head * math.cos(a - 0.5), y1 - head * math.sin(a - 0.5)),
           (x1 - head * math.cos(a + 0.5), y1 - head * math.sin(a + 0.5))]
    d.polygon(pts, fill=col)


def pine(d, x, y, sc=1.0, ang=0.0):
    """작은 소나무(옆으로 누운 채 떠 있음). ang 라디안 회전."""
    def rot(px, py):
        c, s = math.cos(ang), math.sin(ang)
        return (x + (px * c - py * s) * sc, y + (px * s + py * c) * sc)
    d.line([rot(-70, 0), rot(70, 0)], fill=TRUNK, width=int(8 * sc))
    for k in range(4):
        bx = -40 + k * 30
        d.polygon([rot(bx - 26, 0), rot(bx + 30, -34 + k * 4), rot(bx + 30, 34 - k * 4)], fill=TREE)


def hole(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, SURF), fill=SKY)
    # 수면 — 구멍 위가 깔때기처럼 꺼짐
    dip = 60 * ease(clamp((t - 1.0) / 1.2))
    pts = []
    for x in range(0, W + 1, 12):
        r = abs(x - HX)
        y = SURF + 4 * math.sin(x / 40 + t * 3) + dip * math.exp(-(r / 120) ** 2)
        pts.append((x, y))
    d.polygon([(0, H)] + pts + [(W, H)], fill=WATER)
    # 땅(풀밭)과 땅속 구멍
    d.rectangle((0, GY, W, H), fill=GROUND)
    for x in range(0, W, 26):
        d.line((x, GY, x + 8, GY - 16), fill=GRASS, width=4)
    show = ease(clamp(t / 0.6))
    hw = HW * show
    d.rectangle((HX - hw, GY, HX + hw, H), fill=WATER_D)
    d.line((HX - hw, GY, HX - hw, H), fill=GROUND_D, width=6)
    d.line((HX + hw, GY, HX + hw, H), fill=GROUND_D, width=6)
    if t > 0.5:
        ctext(d, HX + 250, GY + 120, "땅속 구멍", 58, fill=YEL)
        arrow(d, HX + 130, GY + 150, HX + hw + 12, GY + 150, YEL, w=8)
    # 물이 사방에서 구멍으로 — 흐름 화살표(1.0초~)
    fl = clamp((t - 1.0) / 0.6)
    if fl > 0:
        for side in (-1, 1):
            for k in range(3):
                ph = (t * 0.9 + k / 3) % 1.0
                x0 = HX + side * (470 - ph * 330)
                y0 = SURF + 70 + k * 60
                x1 = HX + side * (400 - ph * 330 - 120)
                y1 = y0 + 30 + ph * 40
                col = tuple(int(c * fl + w * (1 - fl)) for c, w in zip(FLOW, WATER))
                arrow(d, x0, y0, x1, y1, col, w=6, head=18)
        for k in range(4):  # 구멍 속으로 쑥
            ph = (t * 1.6 + k / 4) % 1.0
            yy = GY - 40 + ph * 280
            arrow(d, HX, yy, HX, yy + 50, FLOW, w=7, head=18)
    # 떠 있던 소나무가 끌려감(2.4초~)
    pull = ease(clamp((t - 2.4) / 2.0))
    tx = 140 + (HX - 140) * pull
    ty = SURF - 6 + 8 * math.sin(t * 3) + dip * math.exp(-((tx - HX) / 120) ** 2) + 200 * clamp((t - 4.2) / 0.8)
    pine(d, tx, ty, 1.5, ang=pull * 1.4)
    if t > 3.4:
        ctext(d, 540, 40, "물이 한 구멍으로 몰린다", 56, fill=WHITE)


# 위에서 본 소용돌이
PARTS = [(random.uniform(120, 360), random.uniform(0, 6.283), random.uniform(0.8, 1.2)) for _ in range(70)]


def spin(img, t):
    d = ImageDraw.Draw(img)
    cx, cy = 540, 430
    d.rectangle((0, 0, W, H), fill=WATER)
    # 물 알갱이가 바깥에서 나선으로 안쪽으로 들어오며 빨라짐(각운동량: 반지름 × 속도 = 일정 → 각속도 ∝ 1/r²)
    core = ease(clamp((t - 2.4) / 1.0))
    rmin = 40 + 50 * core
    for r0, a0, s in PARTS:
        ph = (t * 0.22 * s + r0 / 360) % 1.0          # 각자 바깥→안 한 바퀴
        r = rmin + (480 - rmin) * (1 - ph) ** 1.6
        a = a0 + 2.2 * (480 / r) ** 1.3 * (ph + 0.2) * 3
        x, y = cx + r * math.cos(a), cy + r * math.sin(a) * 0.55
        w = (480 / r) ** 1.3
        tail = min(1.2, 0.06 * w)
        x2, y2 = cx + r * math.cos(a - tail), cy + r * math.sin(a - tail) * 0.55
        d.line((x, y, x2, y2), fill=FLOW, width=5)
        d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=WHITE)
    if core > 0:
        rr = 80 * core
        d.ellipse((cx - rr, cy - rr * 0.55, cx + rr, cy + rr * 0.55), fill=(20, 30, 40), outline=WHITE, width=4)
        ctext(d, cx, cy + 70, "공기 구멍", 54, fill=YEL)
    # 바깥 '느리게' / 안쪽 '빠르게' 표시
    ctext(d, 150, 640, "바깥: 느리게", 40, fill=WHITE)
    if t > 0.8:
        ctext(d, 540, cy - 130, "가운데: 빠르게!", 52, fill=RED)
    # 피겨 스핀 비유(1.2초~): 팔을 오므리면 빨라진다
    if t > 1.2:
        k = ease(clamp((t - 1.2) / 0.8))
        fx, fy = 930, 120
        d.rounded_rectangle((800, 20, 1060, 250), 18, fill=(18, 28, 40))
        d.ellipse((fx - 14, fy - 70, fx + 14, fy - 42), fill=WHITE)
        d.line((fx, fy - 42, fx, fy + 40), fill=WHITE, width=8)
        arm = 90 - 70 * k
        d.line((fx - arm, fy - 20, fx + arm, fy - 20), fill=WHITE, width=8)
        d.line((fx, fy + 40, fx - 22, fy + 80), fill=WHITE, width=8)
        d.line((fx, fy + 40, fx + 22, fy + 80), fill=WHITE, width=8)
        ctext(d, fx, 208, "팔 오므리면 빨라짐", 26, stroke=0)


run("hole", 5.2, hole)
run("spin", 4.8, spin)
print("ok")
