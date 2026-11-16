#!/usr/bin/env python3
"""'헬기에서 고압선을 맨손으로' 모션그래픽(영상 칸 1080x780) — 2026.11.08 오늘의쓸모.
  python3 scripts/story_shorts/anim_lineman.py <출력폴더>
  → volt.mp4 (전선 76만 V 와 땅 0 V 사이에 몸이 끼면 전기가 몸을 지나 땅으로)
    bond.mp4 (헬기·사람은 공중에 떠 있어 땅과 끊김 → 막대(본딩 봉)를 대는 순간 '딱' 하고 전선과 같은 전압
              → 전압 차이 0 = 전류 0, 전선 위 참새와 같은 원리)
    suit.mp4 (금속실을 섞어 짠 옷 — 남은 전기는 옷 겉면으로만 흐름, 패러데이 슈트)
근거: Wikipedia 'Live-line working'(barehand method: 작업자를 전선과 같은 전위로 본딩, 도전성 슈트),
      Hubbell Power Systems 'Dressing for live-line barehand success'(도전성 슈트가 전기장 차폐·충전 전류 우회),
      TikTok @rykerwire 2025.5(High Voltage Aviation 라인맨 인터뷰 — 765,000 V, 'wand'로 본딩).
"""
import math, subprocess, sys, os, random
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (240, 70, 50); BLUE = (110, 190, 255)
SKY = (28, 40, 66); SKY_D = (12, 18, 32); GROUND = (70, 58, 44); WIRE = (200, 205, 215); SUIT = (150, 150, 140)
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


def grad(top, bot):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - k) + bot[i] * k) for i in range(3)))
    return im


def zigzag(d, pts, col, w, t, amp=10):
    """전류(지그재그 번개 선)."""
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = 8
        for k in range(n):
            u = k / n
            x = x0 + (x1 - x0) * u; y = y0 + (y1 - y0) * u
            off = amp * math.sin(k * 2.3 + t * 40)
            out.append((x + off, y))
    out.append(pts[-1])
    d.line(out, fill=col, width=w, joint="curve")


def person(d, x, y, s=1.0, col=SUIT, hood=True):
    """서 있는 사람(머리 중심 x,y)."""
    r = 26 * s
    d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=(0, 0, 0), width=3)
    d.rounded_rectangle([x - 30 * s, y + r, x + 30 * s, y + r + 110 * s], 14, fill=col, outline=(0, 0, 0), width=3)
    d.rectangle([x - 26 * s, y + r + 108 * s, x - 6 * s, y + r + 190 * s], fill=col, outline=(0, 0, 0), width=3)
    d.rectangle([x + 6 * s, y + r + 108 * s, x + 26 * s, y + r + 190 * s], fill=col, outline=(0, 0, 0), width=3)


BG = grad(SKY, SKY_D)


# ---------- 1. volt: 전선과 땅 사이에 몸이 끼면 ----------
def volt(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    d.rectangle([0, 640, W, H], fill=GROUND)
    ctext(d, 900, 668, "땅 0 V", 50, fill=WHITE)
    # 전선
    glow = 6 + 3 * math.sin(t * 9)
    d.line([(0, 150), (W, 150)], fill=YEL, width=int(10 + glow))
    d.line([(0, 150), (W, 150)], fill=WIRE, width=10)
    ctext(d, 880, 70, "전선 76만 V", 56, fill=YEL)
    # 사다리(땅에 닿음) 위의 사람 → 손을 위로
    lx = 430
    for x in (lx - 60, lx + 60):
        d.line([(x, 640), (x, 330)], fill=(120, 120, 120), width=10)
    for y in range(360, 640, 50):
        d.line([(lx - 60, y), (lx + 60, y)], fill=(120, 120, 120), width=8)
    reach = ease(clamp(t / 0.8))
    hx, hy = lx + 40, 330 - 175 * reach
    person(d, lx, 250 - 0, 0.75, col=(230, 200, 170), hood=False)
    d.line([(lx + 18, 290), (hx, max(hy, 158))], fill=(230, 200, 170), width=16)
    if t > 0.8:
        k = clamp((t - 0.8) / 0.5)
        pts = [(hx, 150), (lx + 10, 300), (lx, 420), (lx - 10, 560), (lx - 20, 640)]
        n = max(2, int(len(pts) * k + 0.999))
        zigzag(d, pts[:n], RED, 12, t)
        if t > 1.4:
            fl = 1 if int(t * 8) % 2 == 0 else 0.6
            ctext(d, 180, 300, "몸을 지나", 58, fill=tuple(int(c * fl) for c in RED))
            ctext(d, 180, 380, "땅으로 찌릿", 58, fill=tuple(int(c * fl) for c in RED))
        if t > 1.9:
            # 큰 X
            a = ease(clamp((t - 1.9) / 0.3))
            r = 110 * a
            cx, cy = 760, 400
            d.line([(cx - r, cy - r), (cx + r, cy + r)], fill=RED, width=22)
            d.line([(cx - r, cy + r), (cx + r, cy - r)], fill=RED, width=22)
    return im


def heli(d, x, y, t, s=1.0):
    """옆에서 본 작은 헬기(본체 중심 x,y)."""
    d.ellipse([x - 110 * s, y - 60 * s, x + 90 * s, y + 60 * s], fill=(200, 40, 40), outline=(0, 0, 0), width=4)
    d.ellipse([x - 100 * s, y - 45 * s, x - 20 * s, y + 20 * s], fill=(60, 80, 100))
    d.polygon([(x + 80 * s, y - 20 * s), (x + 260 * s, y - 10 * s), (x + 260 * s, y + 5 * s), (x + 80 * s, y + 20 * s)],
              fill=(200, 40, 40), outline=(0, 0, 0))
    ph = (t * 30) % 1
    rl = 220 * s * (0.4 + 0.6 * abs(math.cos(ph * math.pi)))
    d.line([(x - rl, y - 78 * s), (x + rl, y - 78 * s)], fill=(30, 30, 30), width=int(8 * s))
    d.line([(x, y - 60 * s), (x, y - 78 * s)], fill=(30, 30, 30), width=int(8 * s))
    d.line([(x - 120 * s, y + 85 * s), (x + 80 * s, y + 85 * s)], fill=(30, 30, 30), width=int(8 * s))
    # 바깥 받침대(사람이 앉는 곳)
    d.rectangle([x - 40 * s, y + 60 * s, x + 200 * s, y + 72 * s], fill=(170, 170, 170), outline=(0, 0, 0))


# ---------- 2. bond: 막대를 대는 순간 같은 전압 ----------
def bond(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    wy = 470
    d.line([(0, wy), (W, wy)], fill=WIRE, width=10)
    ctext(d, 150, wy + 22, "76만 V", 44, fill=YEL)
    hx, hy = 330, 250
    heli(d, hx, hy, t, 1.0)
    person(d, hx + 130, hy + 2, 0.55)
    # 막대(본딩 봉) 내려옴
    k = ease(clamp(t / 0.7))
    wx0, wy0 = hx + 160, hy + 90
    wx1, wy1 = wx0 + 70 * k, wy0 + (wy - wy0) * k
    d.line([(wx0, wy0), (wx1, wy1)], fill=(240, 200, 60), width=10)
    # 접촉 순간 '딱' 불꽃
    if 0.7 < t < 1.15:
        for a in range(0, 360, 30):
            r = 30 + 40 * ((t * 13 + a) % 1)
            d.line([(wx1, wy1), (wx1 + r * math.cos(math.radians(a)), wy1 + r * math.sin(math.radians(a)))],
                   fill=(180, 220, 255), width=5)
        ctext(d, wx1 + 110, wy1 - 120, "딱!", 70, fill=BLUE)
    # 사람 전압 게이지
    lvl = ease(clamp((t - 0.75) / 0.6))
    gx, gy, gh = 760, 120, 300
    d.rounded_rectangle([gx, gy, gx + 60, gy + gh], 12, outline=WHITE, width=5)
    d.rectangle([gx + 8, gy + gh - 8 - (gh - 16) * lvl, gx + 52, gy + gh - 8], fill=YEL)
    ctext(d, gx + 30, gy - 70, "헬기·사람", 40)
    vtxt = f"{int(76 * lvl)}만 V" if lvl > 0.02 else "0 V"
    ctext(d, gx + 170, gy + gh / 2 - 30, vtxt, 52, fill=YEL)
    if t > 1.5:
        a = clamp((t - 1.5) / 0.3)
        col = tuple(int(c * a) for c in WHITE)
        ctext(d, 540, 560, "전압 차이 0 → 전류 0", 64, fill=tuple(int(c * a) for c in YEL))
    if t > 2.1:
        # 전선 위 참새
        bx = 900 + 0 * t; by = wy - 30
        a = ease(clamp((t - 2.1) / 0.3))
        d.ellipse([bx - 34 * a, by - 24 * a, bx + 34 * a, by + 22 * a], fill=(150, 110, 70), outline=(0, 0, 0), width=3)
        d.ellipse([bx + 18 * a, by - 40 * a, bx + 50 * a, by - 8 * a], fill=(150, 110, 70), outline=(0, 0, 0), width=3)
        d.polygon([(bx + 50 * a, by - 26 * a), (bx + 66 * a, by - 22 * a), (bx + 50 * a, by - 18 * a)], fill=YEL)
        d.line([(bx - 6, by + 22 * a), (bx - 6, wy - 4)], fill=(240, 160, 60), width=4)
        d.line([(bx + 8, by + 22 * a), (bx + 8, wy - 4)], fill=(240, 160, 60), width=4)
        ctext(d, bx, wy + 30, "참새도 같은 원리", 40, fill=WHITE)
    return im


# ---------- 3. suit: 금속실 옷, 전기는 겉으로만 ----------
def suit(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    cx, top = 330, 110
    # 옷(겉) — 금속 그물
    body = [(cx - 70, top + 90), (cx + 70, top + 90), (cx + 110, top + 300), (cx + 70, top + 330),
            (cx + 60, top + 620), (cx - 60, top + 620), (cx - 70, top + 330), (cx - 110, top + 300)]
    d.ellipse([cx - 62, top - 20, cx + 62, top + 100], fill=SUIT, outline=(0, 0, 0), width=4)
    d.polygon(body, fill=SUIT, outline=(0, 0, 0))
    for x in range(cx - 110, cx + 112, 22):
        d.line([(x, top - 20), (x, top + 620)], fill=(185, 185, 175), width=2)
    for y in range(top - 20, top + 620, 22):
        d.line([(cx - 110, y), (cx + 110, y)], fill=(185, 185, 175), width=2)
    # 안쪽 몸(파랑 = 안전)
    d.ellipse([cx - 36, top + 10, cx + 36, top + 78], fill=(90, 150, 230))
    d.rounded_rectangle([cx - 46, top + 110, cx + 46, top + 580], 30, fill=(90, 150, 230))
    # 겉면을 따라 흐르는 노란 전류 점
    path = [(cx - 62, top + 40), (cx - 110, top + 300), (cx - 66, top + 620)]
    path2 = [(cx + 62, top + 40), (cx + 110, top + 300), (cx + 66, top + 620)]
    for pth in (path, path2):
        for k in range(6):
            u = (t * 0.9 + k / 6) % 1
            seg = 0 if u < 0.5 else 1; v = (u - 0.5 * seg) / 0.5
            (x0, y0), (x1, y1) = pth[seg], pth[seg + 1]
            x = x0 + (x1 - x0) * v; y = y0 + (y1 - y0) * v
            d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=YEL, outline=(0, 0, 0), width=2)
    a = ease(clamp((t - 0.3) / 0.4))
    if a > 0:
        ctext(d, 760, 160, "금속실을 섞어 짠 옷", 54, fill=tuple(int(c * a) for c in WHITE))
        ctext(d, 760, 300, "전기는 겉으로만", 60, fill=tuple(int(c * a) for c in YEL))
    b = ease(clamp((t - 1.2) / 0.4))
    if b > 0:
        ctext(d, 760, 440, "몸은 그대로", 60, fill=tuple(int(c * b) for c in BLUE))
    return im


run("volt", 2.9, volt)
run("bond", 3.4, bond)
run("suit", 3.1, suit)
print("ok")
