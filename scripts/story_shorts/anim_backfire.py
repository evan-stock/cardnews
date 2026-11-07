#!/usr/bin/env python3
"""'맞불(백파이어)' 모션그래픽(영상 칸 1080x780) — 2026.11.07 오늘의쓸모.
  python3 scripts/story_shorts/anim_backfire.py <출력폴더>
  → spread.mp4 (위에서 본 산: 산불이 풀·나무(연료)를 따라 마을 쪽으로 내려옴)
    line.mp4   (마을 앞 길에서 소방관이 불을 붙임 → 맞불이 큰 불 쪽으로 올라가며 '미리 태운 빈 땅'을 만듦)
    stop.mp4   (큰 불이 빈 땅에 닿자 탈 게 없어 꺼짐 → 마을 무사)
근거: NSW RFS(Back burning = 다가오는 산불 앞에 불을 놓는 전술), NIFC(드립 토치로 back burn 점화),
      Wildfire Today 'backfiring operation'(산불 진행 방향의 연료를 먼저 태움).
"""
import math, subprocess, sys, os, random
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 214, 60); RED = (235, 60, 40); ORG = (255, 140, 30)
GROUND = (92, 78, 52); BURNT = (34, 30, 30); TREE = (60, 120, 52); TREE_D = (40, 88, 40)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))

TOP, BOT = 40, 600          # 산(연료) 구역
LINE_Y = 560                # 마을 앞 길(소방관이 불 붙이는 곳)
random.seed(3)
TREES = [(random.uniform(10, 1070), random.uniform(TOP + 10, BOT - 46), random.uniform(13, 22)) for _ in range(330)]


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(draw(i / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def label(d, x, y, s, size, fill=WHITE, bg=None, anchor="mm"):
    ft = F(size)
    if bg:
        b = d.textbbox((x, y), s, font=ft, anchor=anchor)
        d.rounded_rectangle([b[0] - 16, b[1] - 10, b[2] + 16, b[3] + 10], 14, fill=bg)
        d.text((x, y), s, font=ft, fill=fill, anchor=anchor)
    else:
        d.text((x, y), s, font=ft, fill=fill, anchor=anchor, stroke_width=6, stroke_fill=(0, 0, 0))


def arrow(d, x0, y0, x1, y1, col, w=12):
    d.line([(x0, y0), (x1, y1)], fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0); L = w * 2.6
    p1 = (x1 + L * math.cos(a + 2.6), y1 + L * math.sin(a + 2.6))
    p2 = (x1 + L * math.cos(a - 2.6), y1 + L * math.sin(a - 2.6))
    d.polygon([(x1 + w * 0.6 * math.cos(a), y1 + w * 0.6 * math.sin(a)), p1, p2], fill=col)


def wave(x, t, k=0.0):
    return 18 * math.sin(x / 70 + t * 3 + k) + 10 * math.sin(x / 31 - t * 5 + k)


def flames_band(d, y_of_x, t, size=1.0, up=True):
    """y_of_x(x) 위치에 불꽃 띠를 그림."""
    for x in range(0, W + 30, 30):
        y = y_of_x(x)
        h = (46 + 22 * math.sin(x * 0.37 + t * 19)) * size
        s = 1 if up else -1
        d.polygon([(x - 22 * size, y), (x, y - s * h), (x + 22 * size, y)], fill=ORG)
        d.polygon([(x - 11 * size, y), (x, y - s * h * 0.55), (x + 11 * size, y)], fill=(255, 236, 120))


def village(d, safe=False, t=0.0):
    d.rectangle([0, BOT, W, H], fill=(70, 72, 80))
    d.rectangle([0, LINE_Y - 6, W, LINE_Y + 8], fill=(150, 150, 150))  # 길
    for i, x in enumerate(range(120, 1000, 190)):
        y = 690
        d.rectangle([x - 46, y - 30, x + 46, y + 40], fill=(232, 222, 200), outline=(0, 0, 0), width=3)
        d.polygon([(x - 60, y - 28), (x, y - 76), (x + 60, y - 28)], fill=(190, 70, 60), outline=(0, 0, 0))
        d.rectangle([x - 12, y + 8, x + 12, y + 40], fill=(110, 80, 50))


def terrain(d, burnt_rows):
    """burnt_rows(x, y) → True 면 탄 땅."""
    d.rectangle([0, TOP, W, BOT], fill=GROUND)
    for (x, y, r) in TREES:
        if burnt_rows(x, y):
            d.ellipse([x - r * 0.5, y - r * 0.5, x + r * 0.5, y + r * 0.5], fill=(20, 18, 18))
        else:
            d.ellipse([x - r, y - r, x + r, y + r], fill=TREE, outline=TREE_D, width=2)


def scorched(d, y0f, y1f):
    """y0f(x)~y1f(x) 사이를 검게."""
    pts_top = [(x, y0f(x)) for x in range(0, W + 1, 20)]
    pts_bot = [(x, y1f(x)) for x in range(W, -1, -20)]
    d.polygon(pts_top + pts_bot, fill=BURNT)


# ---------- 1. spread: 산불이 연료를 따라 마을 쪽으로 ----------
def spread(t):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    front = TOP + 40 + 150 * ease(t / 3.0) + 10 * t   # 큰 불 앞선
    fy = lambda x: front + wave(x, t)
    terrain(d, lambda x, y: y < fy(x) - 10)
    scorched(d, lambda x: TOP, lambda x: fy(x))
    village(d)
    flames_band(d, fy, t, 1.15)
    label(d, 160, TOP + 40, "산불", 52, fill=WHITE, bg=RED, anchor="mm")
    # 연료 표시
    a = clamp((t - 0.5) / 0.5)
    if a > 0:
        label(d, 760, 500, "풀·나무 = 연료", 50, fill=(20, 20, 20), bg=YEL)
        for k, x in enumerate((420, 560, 700)):
            yy = fy(x) + 50 + 10 * math.sin(t * 6 + k)
            arrow(d, x, yy, x, yy + 70 + 20 * ease(clamp(t - 0.6)), (255, 90, 60), 11)
    label(d, 1010, 640, "마을", 40, bg=(30, 60, 120))
    return im


# ---------- 2. line: 맞불이 큰 불 쪽으로 올라가며 빈 땅을 만듦 ----------
def line(t):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    front = TOP + 40 + 150 + 30 + 8 * t              # spread 끝 위치에서 이어서 천천히
    fy = lambda x: front + wave(x, t + 3)
    lit = clamp(t / 0.9)                                # 왼쪽→오른쪽으로 점화
    back = LINE_Y - 12 - 130 * ease(clamp((t - 0.6) / 2.2))   # 맞불이 위로 올라감
    by = lambda x: back + 0.6 * wave(x, t, 2.0) if x <= lit * W else LINE_Y - 12
    terrain(d, lambda x, y: y < fy(x) - 10 or (y > by(x) and x <= lit * W))
    scorched(d, lambda x: TOP, lambda x: fy(x))
    scorched(d, lambda x: by(x), lambda x: LINE_Y - 6)
    village(d)
    flames_band(d, fy, t, 1.15)
    # 맞불 불꽃(작고 낮게)
    for x in range(0, int(lit * W) + 1, 30):
        y = by(x); h = 30 + 12 * math.sin(x * 0.5 + t * 21)
        d.polygon([(x - 15, y), (x, y - h), (x + 15, y)], fill=ORG)
    # 점화하는 소방관(점)
    fx = lit * W
    if lit < 1:
        d.ellipse([fx - 16, LINE_Y - 16, fx + 16, LINE_Y + 16], fill=YEL, outline=(0, 0, 0), width=3)
    label(d, 160, TOP + 40, "산불", 52, fill=WHITE, bg=RED)
    a = clamp((t - 0.9) / 0.4)
    if a > 0:
        label(d, 300, LINE_Y + 0 - 6 - 95, "맞불", 50, fill=(20, 20, 20), bg=YEL)
        x0 = 640; y0 = LINE_Y - 40
        arrow(d, x0, y0, x0, y0 - 90 * a, YEL, 12)
    if t > 1.6:
        label(d, 820, (back + LINE_Y) / 2 + 4, "미리 태운 빈 땅", 40, bg=(20, 20, 20))
    return im


# ---------- 3. stop: 빈 땅에 닿자 꺼짐 ----------
def stop(t):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    gap_top = LINE_Y - 12 - 130
    start = TOP + 40 + 150 + 30 + 24
    front = min(gap_top - 6, start + (gap_top - start) * ease(t / 1.2))
    fy = lambda x: front + wave(x, t + 6) * (0.4 if front >= gap_top - 8 else 1)
    terrain(d, lambda x, y: y < fy(x) - 10 or y > gap_top)
    scorched(d, lambda x: TOP, lambda x: fy(x))
    scorched(d, lambda x: gap_top + 0.6 * wave(x, 3, 2.0), lambda x: LINE_Y - 6)
    village(d)
    die = clamp((t - 1.2) / 0.9)
    if die < 1:
        flames_band(d, fy, t, 1.15 * (1 - die))
    label(d, 160, TOP + 40, "산불", 52, fill=WHITE, bg=RED)
    a = clamp((t - 1.7) / 0.4)
    if a > 0:
        label(d, 540, gap_top - 70, "탈 게 없음 → 멈춤", 56, fill=(20, 20, 20), bg=YEL)
    b = clamp((t - 2.2) / 0.3)
    if b > 0:
        cx, cy = 920, 640
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(40, 170, 80), outline=(255, 255, 255), width=4)
        d.line([(cx - 20, cy), (cx - 5, cy + 16), (cx + 22, cy - 16)], fill=WHITE, width=9)
    return im


if __name__ == "__main__":
    run("spread", 3.0, spread)
    run("line", 3.0, line)
    run("stop", 3.0, stop)
