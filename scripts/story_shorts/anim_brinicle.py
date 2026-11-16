#!/usr/bin/env python3
"""바닷속 '죽음의 고드름' 브리니클(brinicle) 모션그래픽(영상 칸 1080x780) — 2026.11.06 오늘의쓸모.
  python3 scripts/story_shorts/anim_brinicle.py <출력폴더>
  → salt.mp4 (바다얼음 단면: 바닷물이 얼 때 소금은 얼음 결정 밖으로 밀려나 짜고 차가운 소금물(브라인)이 됨)
    tube.mp4 (무거운 소금물이 아래로 가라앉으며 닿는 바닷물을 얼려 속이 빈 '얼음 관'이 자람)
    map.mp4  (남극 로스섬 근처 — 2011년 BBC 'Frozen Planet' 팀이 처음 영상으로 촬영, 별명 '죽음의 손가락')
근거: Wikipedia 'Brinicle'(염분 배출·밀도 높은 차가운 브라인이 가라앉으며 주변을 얼림, 2011 Hugh Miller·Doug Anderson
      BBC Frozen Planet 촬영, Little Razorback Island), HuffPost UK 2011.11.23.
"""
import math, subprocess, sys, os, random
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (240, 70, 50)
SEA = (18, 60, 96); SEA_D = (10, 34, 60); ICE = (225, 240, 252); SALT = (255, 110, 170); BRINE = (150, 90, 220)
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


def grad(top, bot):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - k) + bot[i] * k) for i in range(3)))
    return im


BG = grad(SEA, SEA_D)
random.seed(5)
# 물 분자(파랑 점)와 소금(분홍 점)
PTS = [(random.uniform(40, W - 40), random.uniform(60, 330), random.random() < 0.22) for _ in range(150)]


# ---------- 1. salt: 바닷물이 얼 때 소금이 밀려남 ----------
def salt(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    fr = ease(t / 1.6)  # 얼음 비율
    iy = 60 + 270 * fr   # 얼음이 위에서 아래로 자람
    d.rectangle([0, 0, W, iy], fill=ICE)
    for k in range(0, W, 90):  # 얼음 결정 무늬
        d.line([(k, 0), (k + 40, iy)], fill=(200, 222, 240), width=3)
    for (x, y, is_salt) in PTS:
        if is_salt:
            # 얼음 안에 갇힌 소금은 아래로 밀려 내려옴
            yy = max(y, iy + 18 + (x % 50)) if y < iy else y
            yy += 120 * clamp((t - 1.6) / 1.4) * (1 if yy > iy else 0)
            r = 11
            d.ellipse([x - r, yy - r, x + r, yy + r], fill=SALT, outline=(0, 0, 0), width=2)
        elif y > iy:
            r = 7
            d.ellipse([x - r, y - r, x + r, y + r], fill=(90, 170, 240))
    ctext(d, W / 2, 10 + 0 * t, "바닷물이 얼면", 56, (20, 40, 70), stroke=0)
    if t > 1.0:
        lx = 130
        d.ellipse([lx - 14, 470, lx + 14, 498], fill=SALT, outline=(0, 0, 0), width=2)
        d.text((lx + 26, 458), "소금", font=F(44), fill=WHITE, stroke_width=5, stroke_fill=(0, 0, 0))
        arrow(d, 560, 380, 560, 500 + 40 * ease((t - 1.0) / 0.8), YEL, 12)
    if t > 1.7:
        ctext(d, W / 2, 560, "얼음 밖으로 밀려나", 56)
        ctext(d, W / 2, 640, "아주 짜고 차가운 '소금물'", 58, SALT)
    return im


# ---------- 2. tube: 소금물이 가라앉으며 얼음 관 ----------
def tube(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 90], fill=ICE)
    ctext(d, 200, 14, "바다얼음", 46, (20, 40, 70), stroke=0)
    cx = 540
    g = ease(t / 2.4)
    tip = 90 + 560 * g
    # 가운데 소금물 줄기(보라)
    wob = lambda y: cx + 18 * math.sin(y / 70 + t * 2)
    pts = [(wob(y), y) for y in range(90, int(tip), 8)]
    if len(pts) > 1:
        # 바깥 얼음 관(흰색, 두껍게)
        d.line(pts, fill=ICE, width=70)
        d.line(pts, fill=BRINE, width=26)
    # 떨어지는 소금물 방울
    for k in range(5):
        ph = (t * 1.4 + k / 5) % 1
        y = 90 + (tip - 90) * ph
        d.ellipse([wob(y) - 8, y - 8, wob(y) + 8, y + 8], fill=SALT)
    # 바다 바닥
    d.rectangle([0, 680, W, H], fill=(60, 52, 48))
    arrow(d, 760, 200, 760, 200 + 260 * g, YEL, 12)
    ctext(d, 900, 120, "무거워서", 50, YEL)
    ctext(d, 900, 190, "가라앉음", 50, YEL)
    if t > 0.9:
        # 관 옆 얼어붙는 화살표
        a = ease((t - 0.9) / 0.6)
        for yy in (300, 430):
            arrow(d, 300, yy, 300 + 170 * a, yy, (150, 220, 255), 9)
        ctext(d, 230, 500, "닿는 물이", 46)
        ctext(d, 230, 560, "꽁꽁", 56, (150, 220, 255))
    if t > 1.8:
        ctext(d, 820, 560, "= 얼음 관", 60, ICE)
    return im


# ---------- 3. map: 남극, 2011 첫 촬영 ----------
ANT = [(0.50, 0.20), (0.62, 0.22), (0.74, 0.30), (0.80, 0.42), (0.78, 0.55), (0.70, 0.66), (0.60, 0.70),
       (0.52, 0.64), (0.47, 0.70), (0.38, 0.72), (0.30, 0.64), (0.24, 0.52), (0.18, 0.46), (0.12, 0.40),
       (0.20, 0.36), (0.30, 0.32), (0.40, 0.24)]


def mapf(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    a = ease(t / 0.7)
    sc = 0.85 + 0.15 * a
    cx0, cy0, S = 330, 400, 620 * sc
    poly = [(cx0 + (x - 0.47) * S, cy0 + (y - 0.46) * S) for x, y in ANT]
    d.polygon(poly, fill=ICE, outline=(0, 0, 0))
    ctext(d, cx0, cy0 - 20, "남극", 60, (40, 70, 110), stroke=0)
    # 로스섬 위치(로스해 쪽 오목한 부분)
    px, py = cx0 + (0.50 - 0.47) * S, cy0 + (0.62 - 0.46) * S
    if t > 0.6:
        pr = 14 + 10 * abs(math.sin(t * 5))
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=RED, outline=WHITE, width=4)
        ctext(d, px, py + 30, "로스섬 근처", 40)
    if t > 1.0:
        ctext(d, 820, 170, "2011", int(120 * (0.7 + 0.3 * ease((t - 1.0) / 0.4))), YEL)
        ctext(d, 820, 320, "처음 영상으로 촬영", 46)
        ctext(d, 820, 380, "(BBC 다큐 팀)", 40, (200, 220, 240))
    if t > 1.8:
        ctext(d, 820, 500, "별명", 44)
        ctext(d, 820, 560, "'죽음의 손가락'", 60, RED)
    return im


run("salt", 3.2, salt)
run("tube", 3.0, tube)
run("map", 3.0, mapf)
print("ok")
