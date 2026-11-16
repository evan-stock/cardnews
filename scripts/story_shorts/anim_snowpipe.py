#!/usr/bin/env python3
"""눈 오는 날 일부러 물을 뿌리는 도로 — 일본 '소세쓰 파이프(消雪パイプ)' 모션그래픽(영상 칸 1080x780) — 2026.11.06 오늘의쓸모.
  python3 scripts/story_shorts/anim_snowpipe.py <출력폴더>
  → under.mp4 (땅속 단면: 깊은 우물에서 펌프로 지하수를 끌어올려 도로 아래 관 → 노즐로 뿜어 올림, 온도계 12~13℃)
    melt.mp4  (왼쪽 맨 도로: 눈이 쌓임 / 오른쪽 물 뿌리는 도로: 0℃ 눈이 12~13℃ 물에 닿자마자 녹아 사라짐)
    limit.mp4 (1961 니가타현 나가오카 첫 설치 → 단, 더 추운 곳(홋카이도·산간)에선 뿌린 물이 얼어 못 씀 → 열선)
근거: 新潟県 長岡地域振興局 '消雪パイプ'(지하수 수온 겨울에도 12~13℃, 1961년 長岡市가 전국 최초 도로 설치),
      ja.wikipedia '消雪パイプ'(北海道·山間部처럼 추운 곳은 물 자체가 얼어 ロードヒーティング 사용).
"""
import math, subprocess, sys, os, random
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (240, 70, 50); BG = (22, 28, 40)
SKY = (70, 86, 110); ROAD = (52, 54, 60); SOIL = (96, 70, 48); SOIL_D = (70, 50, 34); WATER = (90, 190, 255); SNOW = (245, 248, 255)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(draw(i / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=6):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def arrow(d, x0, y0, x1, y1, col, w=12):
    d.line([(x0, y0), (x1, y1)], fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0); L = w * 2.6
    p1 = (x1 + L * math.cos(a + 2.6), y1 + L * math.sin(a + 2.6))
    p2 = (x1 + L * math.cos(a - 2.6), y1 + L * math.sin(a - 2.6))
    d.polygon([(x1 + w * 0.6 * math.cos(a), y1 + w * 0.6 * math.sin(a)), p1, p2], fill=col)


def thermo(d, x, y, h, frac, col, label):
    d.rounded_rectangle([x - 16, y, x + 16, y + h], radius=16, fill=(235, 238, 245), outline=(0, 0, 0), width=4)
    d.ellipse([x - 30, y + h - 20, x + 30, y + h + 40], fill=col, outline=(0, 0, 0), width=4)
    top = y + h - (h - 20) * frac
    d.rectangle([x - 8, top, x + 8, y + h], fill=col)
    ctext(d, x, y - 70, label, 50, col)


random.seed(3)
FLAKES = [(random.uniform(0, W), random.uniform(0, 1), random.uniform(5, 10), random.uniform(0.6, 1.1)) for _ in range(70)]


def snow(d, t, x0=0, x1=W, ymax=H, speed=230):
    for fx, fy, r, sp in FLAKES:
        if not (x0 <= fx <= x1):
            continue
        y = (fy * ymax + t * speed * sp) % ymax
        x = fx + 10 * math.sin(t * 2 + fy * 9)
        d.ellipse([x - r, y - r, x + r, y + r], fill=SNOW)


# ---------- 1. under: 땅속 단면 ----------
RY = 250  # 도로 표면 y


def under(t):
    im = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(im)
    snow(d, t, ymax=RY)
    d.rectangle([0, RY, W, RY + 30], fill=ROAD)
    d.rectangle([0, RY + 30, W, H], fill=SOIL)
    for k in range(5):
        d.line([(0, RY + 120 + k * 110), (W, RY + 120 + k * 110 + 20)], fill=SOIL_D, width=4)
    # 우물(깊은 관) + 펌프
    wx = 150
    d.rectangle([wx - 22, RY + 30, wx + 22, H], fill=(150, 156, 166), outline=(0, 0, 0), width=3)
    d.rounded_rectangle([wx - 60, RY - 70, wx + 60, RY], radius=12, fill=(60, 120, 200), outline=(0, 0, 0), width=4)
    ctext(d, wx, RY - 66, "펌프", 40)
    # 도로 아래 가로관
    py = RY + 55
    d.rectangle([wx, py - 12, W, py + 12], fill=(150, 156, 166), outline=(0, 0, 0), width=3)
    # 물 흐름: 우물 아래에서 위로 → 가로관 → 노즐
    fl = ease(t / 1.4)
    yb = H - (H - py) * fl
    d.rectangle([wx - 12, yb, wx + 12, H], fill=WATER)
    if t > 1.0:
        xr = wx + (W - wx) * ease((t - 1.0) / 0.9)
        d.rectangle([wx, py - 6, xr, py + 6], fill=WATER)
    arrow(d, wx + 70, H - 40, wx + 70, H - 160 - 120 * fl, YEL, 12)
    # 노즐에서 물 뿜기
    if t > 1.7:
        k2 = ease((t - 1.7) / 0.5)
        for nx in (420, 640, 860):
            d.ellipse([nx - 14, RY - 8, nx + 14, RY + 8], fill=WHITE, outline=(0, 0, 0), width=2)
            for dx in (-1.0, -0.45, 0.45, 1.0):
                pts = [(nx + dx * 90 * k2 * u, RY - 6 - 95 * k2 * 4 * u * (1 - u) * (1.2 - abs(dx) * 0.4)) for u in [i / 12 for i in range(13)]]
                d.line(pts, fill=WATER, width=6)
    # 온도계
    if t > 0.6:
        thermo(d, 960 if t < 1.7 else 960, 430, 220, 0.62 * ease((t - 0.6) / 0.8), RED, "12~13℃")
        ctext(d, 760, 640, "땅속 지하수", 54, YEL)
    return im


# ---------- 2. melt: 맨 도로 vs 물 뿌리는 도로 ----------
def melt(t):
    im = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(im)
    d.rectangle([W // 2 - 4, 0, W // 2 + 4, H], fill=(0, 0, 0))
    snow(d, t, 0, W // 2 - 10, ymax=520, speed=260)
    snow(d, t, W // 2 + 10, W, ymax=520, speed=260)
    # 도로
    d.rectangle([0, 520, W, H], fill=ROAD)
    # 왼쪽: 눈이 쌓임
    hpile = 20 + 110 * ease(t / 2.6)
    d.rounded_rectangle([20, 520 - hpile, W // 2 - 20, 540], radius=30, fill=SNOW)
    # 오른쪽: 물막 + 닿자마자 사라지는 눈 (작은 물방울 고리)
    d.rectangle([W // 2 + 10, 515, W, 540], fill=WATER)
    for k in range(6):
        ph = (t * 1.7 + k / 6) % 1
        x = W // 2 + 60 + k * 85
        r = 8 + 40 * ph
        d.ellipse([x - r, 528 - r * 0.3, x + r, 528 + r * 0.3], outline=(220, 245, 255), width=3)
    ctext(d, W * 0.25, 590, "그냥 도로", 56)
    ctext(d, W * 0.75, 590, "물 뿌리는 도로", 56, YEL)
    if t > 0.5:
        ctext(d, W * 0.25, 670, "눈 0℃ → 쌓임", 42, SNOW)
        ctext(d, W * 0.75, 670, "물 12~13℃ → 녹음", 42, WATER)
    return im


# ---------- 3. limit: 1961 나가오카 → 더 추운 곳은 못 씀 ----------
def limit(t):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    a = ease(t / 0.6)
    ctext(d, W * 0.27, 90, "1961", int(140 * (0.6 + 0.4 * a)), YEL)
    ctext(d, W * 0.27, 280, "니가타현 나가오카", 50)
    ctext(d, W * 0.27, 350, "도로에 첫 설치", 50)
    # 오른쪽: 더 추운 곳 → 뿌린 물이 얼음
    if t > 1.0:
        b = ease((t - 1.0) / 0.8)
        x0 = W * 0.73
        thermo(d, x0 - 150, 230, 260, 0.62 - 0.5 * b, (90, 160, 255), "더 추운 곳")
        # 물웅덩이 → 얼음 판
        col = tuple(int(WATER[i] * (1 - b) + (210, 235, 250)[i] * b) for i in range(3))
        d.rounded_rectangle([x0 - 70, 430, x0 + 200, 480], radius=20, fill=col, outline=(0, 0, 0), width=3)
        if b > 0.6:
            for k in range(3):
                d.line([(x0 - 40 + k * 80, 438), (x0 - 10 + k * 80, 470)], fill=WHITE, width=4)
        if t > 1.9:
            ctext(d, x0 + 65, 520, "물이 얼어버려", 50, (150, 200, 255))
            ctext(d, x0 + 65, 590, "못 써요", 60, RED)
    return im


run("under", 3.2, under)
run("melt", 3.0, melt)
run("limit", 3.2, limit)
print("ok")
