#!/usr/bin/env python3
"""금문교 이동식 중앙분리대(로드 지퍼) 모션그래픽(카드 영상 칸 1080x780) — 2026.11.10 오늘의쓸모.
  python3 scripts/story_shorts/anim_zipper.py <출력폴더>
  → before.mp4  (위에서 본 6차로 다리, 가운데엔 노란 플라스틱 막대뿐 → 차가 중앙선을 넘음, 1970~2014 정면충돌 100건+·사망 사고 16건)
    lanes.mp4   (기본 3:3 → 출근 4:2(샌프란시스코 방향) → 퇴근 2:4, 가운데 분리대 자리가 바뀜)
    zipper.mp4  (트럭이 지나가며 블록 줄을 S자로 들어 약 3m(10피트) 옆으로 내려놓음, 블록 3,517개·개당 680kg)
    result.mp4  (설치 전 사망 정면충돌 16건 vs 2015 설치 후 정면충돌 0건, 2018 보도)
근거: Golden Gate Bridge District 'Moveable Median Barrier'(2015.01.10 주말 설치, 평소 3:3·출근 남행 4차로·퇴근 북행 4차로,
      약 10피트 옮김·약 30분, 3,000만 달러, 이전엔 25피트마다 높이 19인치 노란 플라스틱 막대),
      CNBC 2018.02.08(3,517개·개당 1,500파운드, 1970년부터 정면충돌 100건 넘게·16건 사망, 2015 설치 뒤 정면충돌 없음).
"""
import subprocess, sys, os, math
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (215, 25, 35); DARK = (30, 34, 44); GREY = (150, 160, 178)
ASPH = (58, 62, 70); BRIDGE = (192, 54, 44); CONC = (215, 218, 225); TRUCK = (250, 200, 20)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))
CARS = [(70, 120, 200), (230, 230, 235), (40, 40, 45), (200, 60, 60), (120, 130, 140), (90, 160, 110)]


def grad(top, bot):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line((0, y, W, y), fill=tuple(int(a + (b - a) * k) for a, b in zip(top, bot)))
    return img


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


# 도로(가로로 긴 다리를 위에서 본 모습): 6차로, y 범위 RY0~RY1
RY0, RY1 = 170, 590
LANE = (RY1 - RY0) / 6


def road(d):
    d.rectangle((0, RY0 - 26, W, RY0), fill=BRIDGE)
    d.rectangle((0, RY1, W, RY1 + 26), fill=BRIDGE)
    d.rectangle((0, RY0, W, RY1), fill=ASPH)
    for k in range(1, 6):
        y = RY0 + LANE * k
        for x in range(0, W, 70):
            d.line((x, y, x + 36, y), fill=(225, 225, 225), width=3)


def car(d, x, y, col, right=True):
    d.rounded_rectangle((x - 38, y - 17, x + 38, y + 17), 8, fill=col, outline=(20, 20, 20), width=2)
    wx = x + (14 if right else -14)
    d.rectangle((wx - 8, y - 13, wx + 8, y + 13), fill=(150, 190, 220))


def lane_y(i):
    return RY0 + LANE * (i + 0.5)


# ① 이전: 플라스틱 막대뿐 → 차가 중앙선을 넘음
def before(img, t):
    d = ImageDraw.Draw(img)
    road(d)
    cy = RY0 + LANE * 3
    for x in range(20, W, 64):  # 노란 플라스틱 막대
        d.ellipse((x - 7, cy - 7, x + 7, cy + 7), fill=YEL, outline=(120, 90, 0), width=2)
    for i in range(3):  # 위 3차로: 오른쪽으로, 아래 3차로: 왼쪽으로
        for j in range(3):
            x = ((t * 260 + j * 380 + i * 120) % (W + 200)) - 100
            car(d, x, lane_y(i), CARS[(i + j) % 6], True)
            x2 = W - ((t * 260 + j * 380 + i * 150 + 60) % (W + 200)) + 100
            car(d, x2, lane_y(3 + i), CARS[(i + j + 3) % 6], False)
    # 한 대가 막대를 넘어 반대편으로
    k = ease((t - 0.6) / 1.2)
    sx = 200 + 420 * clamp((t - 0.3) / 1.5)
    sy = lane_y(2) + (lane_y(3) - lane_y(2)) * k
    car(d, sx, sy, (240, 240, 245), True)
    if t > 1.7:
        a = clamp((t - 1.7) / 0.2)
        d.line((sx + 40, sy - 60, sx + 140, sy + 60), fill=RED, width=int(14 * a) or 1)
        d.line((sx + 140, sy - 60, sx + 40, sy + 60), fill=RED, width=int(14 * a) or 1)
    ctext(d, 540, 40, "가운데엔 높이 48cm 플라스틱 막대뿐", 46, fill=YEL)
    if t > 1.9:
        kk = ease((t - 1.9) / 0.4)
        ctext(d, 540, 640 + (1 - kk) * 30, "1970~2014  정면충돌 100건+ · 사망 사고 16건", 42, fill=(255, 140, 140))


def divider(d, y):
    d.rectangle((0, y - 10, W, y + 10), fill=CONC, outline=(120, 120, 130), width=2)
    for x in range(0, W, 46):
        d.line((x, y - 10, x, y + 10), fill=(150, 150, 160), width=2)
    d.line((0, y, W, y), fill=YEL, width=3)


# ② 출퇴근 차로 바뀜
def lanes(img, t):
    d = ImageDraw.Draw(img)
    road(d)
    phases = [(0.0, 3, "평소 3 : 3"), (1.0, 4, "출근길  4 : 2"), (2.0, 2, "퇴근길  2 : 4")]
    cur = phases[0]
    for ph in phases:
        if t >= ph[0]:
            cur = ph
    prev = phases[max(0, phases.index(cur) - 1)]
    k = ease((t - cur[0]) / 0.5)
    n = prev[1] + (cur[1] - prev[1]) * k  # 위쪽(샌프란시스코 방향) 차로 수
    y = RY0 + LANE * n
    divider(d, y)
    top = int(round(n))
    for i in range(6):
        right = i < top
        yy = lane_y(i)
        for j in range(2):
            x = ((t * 300 * (1 if right else -1) + j * 540 + i * 90) % (W + 160)) - 80
            car(d, x, yy, CARS[(i + j) % 6], right)
    ctext(d, 540, 40, cur[2], 60, fill=YEL)
    ctext(d, 900, RY0 - 70, "→ 샌프란시스코", 32, fill=WHITE, stroke=4)
    ctext(d, 180, RY1 + 36, "마린 카운티 ←", 32, fill=WHITE, stroke=4)
    ctext(d, 540, 690, "벽이 고정돼 있으면 이게 안 된다", 40, fill=WHITE)


# ③ 지퍼 트럭: 블록 줄을 S자로 들어 옆으로
def zipper(img, t):
    d = ImageDraw.Draw(img)
    road(d)
    y0 = RY0 + LANE * 3          # 원래 자리
    y1 = RY0 + LANE * 4          # 옮긴 자리(약 3m)
    tx = -150 + 1250 * (t / 3.0)  # 트럭 앞머리 x(왼쪽→오른쪽)
    L = 260                       # 트럭 길이
    # 블록: 트럭 앞쪽(오른쪽)은 원래 자리, 뒤쪽(왼쪽)은 옮긴 자리, 트럭 밑은 S자
    for x in range(0, W + 30, 30):
        if x > tx:
            y = y0
        elif x < tx - L:
            y = y1
        else:
            s = (tx - x) / L
            y = y0 + (y1 - y0) * (0.5 - 0.5 * math.cos(math.pi * s))
        d.rectangle((x - 13, y - 11, x + 13, y + 11), fill=CONC, outline=(110, 110, 120), width=2)
    # 트럭(반투명 느낌으로 테두리만 굵게)
    ty = (y0 + y1) / 2
    d.rounded_rectangle((tx - L, ty - 62, tx + 30, ty + 62), 14, outline=TRUCK, width=10)
    d.rectangle((tx - 10, ty - 62, tx + 30, ty + 62), fill=TRUCK)
    d.rectangle((tx - L, ty - 62, tx - L + 30, ty + 62), fill=TRUCK)
    if t > 1.2:  # 3m 화살표
        ax = 150
        d.line((ax, y0 - 30, ax, y1 + 30), fill=YEL, width=6)
        d.polygon([(ax - 14, y1 + 10), (ax + 14, y1 + 10), (ax, y1 + 34)], fill=YEL)
        ctext(d, ax + 120, (y0 + y1) / 2 - 30, "약 3m", 44, fill=YEL)
    ctext(d, 540, 40, "블록을 들어 S자로 옮겨 내려놓기", 46, fill=YEL)
    ctext(d, 540, 670, "블록 3,517개 · 한 개 680kg", 44, fill=WHITE)


# ④ 결과
def result(img, t):
    d = ImageDraw.Draw(img)
    ctext(d, 540, 40, "정면충돌 사망 사고", 54, fill=WHITE)
    bars = [(330, "설치 전", "1970~2014", 16, (230, 80, 80)), (750, "설치 후", "2015~", 0, (120, 220, 140))]
    base = 600
    for i, (cx, a, b, v, col) in enumerate(bars):
        k = ease((t - 0.2 - i * 0.6) / 0.6)
        if k <= 0:
            continue
        h = 360 * (v / 16) * k
        if v > 0:
            d.rectangle((cx - 110, base - h, cx + 110, base), fill=col)
        cnt = int(round(v * k))
        ctext(d, cx, base - h - 110, f"{cnt}건", 80, fill=col)
        ctext(d, cx, base + 20, a, 46)
        ctext(d, cx, base + 80, b, 34, fill=GREY, stroke=3)
    d.line((140, base, 940, base), fill=WHITE, width=4)
    if t > 1.6:
        ctext(d, 750, 330, "정면충돌 0건", 40, fill=YEL)
        ctext(d, 750, 380, "(2018년 보도 기준)", 28, fill=GREY, stroke=3)


run("before", 3.0, grad((35, 45, 70), (60, 75, 100)), before)
run("lanes", 3.0, grad((35, 45, 70), (60, 75, 100)), lanes)
run("zipper", 3.0, grad((35, 45, 70), (60, 75, 100)), zipper)
run("result", 2.6, grad((30, 35, 50), (60, 65, 85)), result)
print("ok")
