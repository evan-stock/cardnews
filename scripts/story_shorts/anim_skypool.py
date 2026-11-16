#!/usr/bin/env python3
"""빌딩 옥상 수영장 폭포(2025.3.28 미얀마 규모 7.7 지진, 방콕) — 모션그래픽(카드 영상 칸 1080x780) — 2026.11.02 오늘의쓸모.
  python3 scripts/story_shorts/anim_skypool.py <출력폴더>
  → far.mp4    (미얀마 진앙 → 방콕 약 1,000km, 느리고 긴 지진파가 퍼져 방콕에 닿음)
    sway.mp4   (같은 긴 흔들림에 낮은 건물은 거의 그대로, 고층은 꼭대기가 크게 휘청 → 옥상 수영장 물이 넘침)
    damper.mp4 (타이베이101: 87~92층에 매단 660톤 쇠공이 건물과 반대로 흔들려 흔들림을 최대 40% 줄임)
근거: YTN 2025.7.5(1Hz 이하 저주파=장주기 지진동은 멀리 가고 고층에 큰 영향, 방콕은 약 1,000km 밖),
      The Star 2026.4.3(방콕 연약 점토 분지가 흔들림을 3~6배 키움), YTN 2024.4.4(타이베이101 660t 댐퍼, 87~92층, 최대 40%).
"""
import math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (14, 26, 48); GRID = (28, 46, 78); WHITE = (250, 250, 252); RED = (232, 48, 44); YEL = (255, 210, 60)
POOL = (90, 200, 255); BLD = (150, 170, 196); BLD_E = (70, 90, 120); WIN = (210, 225, 240); GOLD = (222, 176, 70)
GROUND = (92, 78, 60)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))
random.seed(7)


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw(img, i / FPS)
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=5):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def grid(d):
    for x in range(0, W, 60):
        d.line((x, 0, x, H), fill=GRID, width=1)
    for y in range(0, H, 60):
        d.line((0, y, W, y), fill=GRID, width=1)


# ---------- 1. far: 1,000km 밖에서 온 느린 흔들림 ----------
EPI = (230, 300); BKK = (850, 560)


def far(img, t):
    d = ImageDraw.Draw(img); grid(d)
    # 퍼지는 지진파(느리고 굵은 원)
    for k in range(4):
        r = ((t * 260) - k * 230)
        if r > 0:
            a = clamp(1 - r / 1100)
            col = tuple(int(RED[i] * a + BG[i] * (1 - a)) for i in range(3))
            d.ellipse((EPI[0] - r, EPI[1] - r, EPI[0] + r, EPI[1] + r), outline=col, width=10)
    # 거리 점선
    n = 22
    for i in range(n):
        if i % 2: continue
        x0 = EPI[0] + (BKK[0] - EPI[0]) * i / n; y0 = EPI[1] + (BKK[1] - EPI[1]) * i / n
        x1 = EPI[0] + (BKK[0] - EPI[0]) * (i + 1) / n; y1 = EPI[1] + (BKK[1] - EPI[1]) * (i + 1) / n
        d.line((x0, y0, x1, y1), fill=WHITE, width=5)
    # 진앙
    pr = 22 + 6 * math.sin(t * 8)
    d.ellipse((EPI[0] - pr, EPI[1] - pr, EPI[0] + pr, EPI[1] + pr), fill=RED, outline=WHITE, width=4)
    ctext(d, EPI[0], EPI[1] - 120, "미얀마 진앙", 46)
    ctext(d, EPI[0], EPI[1] - 66, "규모 7.7", 40, fill=YEL)
    # 방콕(파도가 닿으면 흔들림)
    hit = (t * 260) > math.dist(EPI, BKK)
    jx = 10 * math.sin(t * 14) if hit else 0
    bx = BKK[0] + jx
    for k, (hh, ww) in enumerate(((150, 40), (210, 46), (120, 36))):
        x = bx - 80 + k * 60
        d.rectangle((x, BKK[1] - hh, x + ww, BKK[1]), fill=BLD, outline=BLD_E, width=3)
    d.line((BKK[0] - 120, BKK[1], BKK[0] + 120, BKK[1]), fill=WHITE, width=4)
    ctext(d, BKK[0], BKK[1] + 20, "방콕", 50, fill=YEL if hit else WHITE)
    # 거리 라벨
    a = ease(clamp((t - 0.4) / 0.6))
    if a > 0:
        mx, my = (EPI[0] + BKK[0]) / 2, (EPI[1] + BKK[1]) / 2
        ctext(d, mx + 70, my - 160, "약 1,000km", int(70 * (0.6 + 0.4 * a)), fill=YEL)


# ---------- 2. sway: 낮은 건물 vs 고층 ----------
GY = 700
DROPS = [(random.uniform(-1, 1), random.uniform(0, 1)) for _ in range(40)]


def tower(d, cx, base_y, h, w, top_dx, floors, pool=False, t=0.0):
    """아래는 고정, 위로 갈수록 top_dx 만큼 휘는 건물(조각으로 그림)."""
    seg = 24
    for s in range(seg):
        f0, f1 = s / seg, (s + 1) / seg
        dx0 = top_dx * f0 ** 2; dx1 = top_dx * f1 ** 2
        y0 = base_y - h * f0; y1 = base_y - h * f1
        d.polygon([(cx - w / 2 + dx0, y0), (cx + w / 2 + dx0, y0), (cx + w / 2 + dx1, y1), (cx - w / 2 + dx1, y1)], fill=BLD)
    # 창문 줄
    for k in range(1, floors):
        f = k / floors; dx = top_dx * f ** 2; y = base_y - h * f
        d.line((cx - w / 2 + dx + 6, y, cx + w / 2 + dx - 6, y), fill=WIN, width=2)
    # 외곽선
    pts_l = [(cx - w / 2 + top_dx * (s / seg) ** 2, base_y - h * s / seg) for s in range(seg + 1)]
    pts_r = [(cx + w / 2 + top_dx * (s / seg) ** 2, base_y - h * s / seg) for s in range(seg + 1)]
    d.line(pts_l, fill=BLD_E, width=4); d.line(pts_r, fill=BLD_E, width=4)
    if pool:
        tx = cx + top_dx; ty = base_y - h
        # 수영장 물: 기울어 한쪽으로 넘침
        tilt = max(-1, min(1, top_dx / 90))
        d.polygon([(tx - w / 2 + 6, ty - 4 + 30 * tilt), (tx + w / 2 - 6, ty - 4 - 30 * tilt), (tx + w / 2 - 6, ty + 18), (tx - w / 2 + 6, ty + 18)], fill=POOL)
        if abs(tilt) > 0.45:
            side = -1 if tilt > 0 else 1
            ex = tx + side * (w / 2 - 4)
            for u, ph in DROPS:
                fall = ((t * 1.6 + ph) % 1.0)
                yy = ty + fall * 420
                xx = ex + side * (8 + 30 * fall + 10 * u)
                d.ellipse((xx - 6, yy - 9, xx + 6, yy + 9), fill=POOL)


def sway(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, GY, W, H), fill=GROUND)
    # 땅의 느린 긴 파도
    pts = [(x, GY - 10 * math.sin(2 * math.pi * (x / 900 - t * 0.55))) for x in range(0, W + 1, 12)]
    d.line(pts, fill=YEL, width=6)
    g = math.sin(2 * math.pi * t * 0.55 * 1.3)
    amp = ease(clamp(t / 0.8))
    # 낮은 건물: 거의 그대로
    tower(d, 250, GY, 170, 170, 4 * g * amp, 5)
    # 고층: 꼭대기가 크게 휨(긴 흔들림과 박자가 맞음)
    tower(d, 720, GY, 560, 110, 110 * g * amp, 30, pool=True, t=t)
    ctext(d, 250, GY - 250, "낮은 건물", 44)
    ctext(d, 250, GY - 196, "거의 그대로", 40, fill=YEL)
    ctext(d, 540, 20, "느리고 '긴' 흔들림이 오면", 50)
    if t > 1.0:
        ctext(d, 905, 120, "고층은", 44)
        ctext(d, 905, 172, "꼭대기가", 44)
        ctext(d, 905, 226, "휘청", 58, fill=RED)


# ---------- 3. damper: 타이베이101 660톤 쇠공 ----------
def damper(img, t):
    d = ImageDraw.Draw(img); grid(d)
    g = math.sin(2 * math.pi * t * 0.8)
    damp = 1 - 0.4 * ease(clamp((t - 1.2) / 1.2))  # 쇠공이 움직이기 시작하면 흔들림이 줄어듦
    top = 70 * g * damp
    cx, base, h, w = 430, 760, 700, 150
    tower(d, cx, base, h, w, top, 26)
    # 87~92층 구역(위에서 약 15%)
    f0, f1 = 0.80, 0.93
    y0 = base - h * f1; y1 = base - h * f0
    dx = top * ((f0 + f1) / 2) ** 2
    d.rectangle((cx - w / 2 + dx + 6, y0, cx + w / 2 + dx - 6, y1), fill=(40, 52, 80), outline=GOLD, width=3)
    # 쇠공: 건물과 반대 방향으로 흔들림
    k = ease(clamp((t - 0.4) / 0.8))
    ax, ay = cx + dx, y0 + 6
    bx = ax - 48 * g * k; by = y1 - 40
    d.line((ax - 24, ay, bx, by), fill=(200, 200, 200), width=3)
    d.line((ax + 24, ay, bx, by), fill=(200, 200, 200), width=3)
    r = 36
    d.ellipse((bx - r, by - r, bx + r, by + r), fill=GOLD, outline=(120, 90, 30), width=3)
    for q in range(-2, 3):
        d.line((bx - r + 6, by + q * 12, bx + r - 6, by + q * 12), fill=(176, 136, 50), width=2)
    # 반대 방향 화살표
    if k > 0.5 and abs(g) > 0.3:
        s = 1 if g > 0 else -1
        d.line((ax + s * 90, ay - 30, ax + s * 150, ay - 30), fill=WHITE, width=6)
        d.polygon([(ax + s * 165, ay - 30), (ax + s * 145, ay - 42), (ax + s * 145, ay - 18)], fill=WHITE)
        d.line((bx - s * 60, by + 60, bx - s * 120, by + 60), fill=YEL, width=6)
        d.polygon([(bx - s * 135, by + 60), (bx - s * 115, by + 48), (bx - s * 115, by + 72)], fill=YEL)
    # 라벨
    ctext(d, 820, 60, "타이베이101", 52)
    ctext(d, 820, 128, "87~92층에 매단", 40)
    ctext(d, 820, 182, "660톤 쇠공", 64, fill=YEL)
    a = ease(clamp((t - 1.4) / 0.6))
    if a > 0:
        ctext(d, 820, 330, "건물과 '반대로' 흔들려", 40)
        ctext(d, 820, 392, "흔들림 최대", 44)
        ctext(d, 820, 450, "-40%", int(96 * (0.7 + 0.3 * a)), fill=RED)


run("far", 3.2, far)
run("sway", 3.2, sway)
run("damper", 3.4, damper)
print("ok")
