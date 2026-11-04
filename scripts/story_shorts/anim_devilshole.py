#!/usr/bin/env python3
"""사막 동굴 '데빌스홀'이 먼 지진에 출렁이는 이유 — 모션그래픽(카드 영상 칸 1080x780) — 2026.11.04 오늘의쓸모.
  python3 scripts/story_shorts/anim_devilshole.py <출력폴더>
  → map.mp4      (2019.7.5 리지크레스트 규모 7.1 진앙에서 지진파 동그라미가 퍼져 240km 떨어진 데빌스홀에 닿자 물이 출렁)
    section.mp4  (단면: 사막 땅 아래 바닥 모를 석회암 동굴 속 지하수 — 지진파가 지나가자 수면이 위아래로 최대 4.5m)
    distance.mp4 (거리 비교: 240km 캘리포니아 · 2,400km 멕시코 · 3,200km 알래스카 지진에도 매번 출렁)
근거: NPS 데스밸리 보도자료(2018.1.24 알래스카 M7.9 약 2,000마일·'지진 세이시', 2022.9.21 멕시코 M7.6 약 1,500마일·약 4피트 파도,
      '수백 피트 깊이' 석회암 동굴), KQED 2019.7(리지크레스트 M7.1 약 150마일, 물 10~15피트 오르내림, 바닥 미도달).
"""
import math, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (24, 20, 18); SAND = (196, 160, 112); SAND2 = (160, 126, 86); ROCK = (110, 92, 74); ROCK2 = (84, 70, 58)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (235, 64, 52); WATER = (60, 150, 230); WATER2 = (36, 100, 170)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw(img, i / FPS)
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()


def text(d, x, y, s, size, fill=WHITE, anchor="la", stroke=5):
    d.text((x, y), s, font=F(size), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))


def star(d, cx, cy, r, fill):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill, outline=(0, 0, 0))


def pool(d, cx, cy, t_hit, t, r=26):
    """데빌스홀 표시: 파란 웅덩이, 지진파가 닿은 뒤엔 물결 동그라미가 퍼짐."""
    wob = 0
    if t >= t_hit:
        k = t - t_hit
        wob = 7 * math.sin(k * 14) * math.exp(-k * 0.6)
        for j in range(3):
            rr = r + ((k * 70 + j * 28) % 84)
            a = 1 - ((k * 70 + j * 28) % 84) / 84
            c = tuple(int(WATER[i] * a + SAND[i] * (1 - a)) for i in range(3))
            d.ellipse((cx - rr, cy - rr * 0.7, cx + rr, cy + rr * 0.7), outline=c, width=5)
    d.ellipse((cx - r - wob, cy - r * 0.7 + wob, cx + r + wob, cy + r * 0.7 - wob), fill=WATER, outline=(0, 0, 0), width=3)


# ── 1) 지도: 진앙 → 240km 밖 데빌스홀 ─────────────────────────────
def draw_map(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), fill=SAND)
    for k in range(9):  # 사막 무늬(산맥 줄)
        y = 90 + k * 80
        d.line([(x, y + 18 * math.sin(x / 90 + k)) for x in range(0, W + 20, 20)], fill=SAND2, width=4)
    ex, ey = 250, 560    # 진앙(리지크레스트)
    px, py = 830, 250    # 데빌스홀
    dist = math.hypot(px - ex, py - ey)
    v = dist / 1.5       # 1.5초 만에 도착(그림용)
    t0 = 0.3
    # 지진파 동그라미
    if t > t0:
        for j in range(5):
            rr = (t - t0) * v - j * 110
            if 0 < rr < dist + 150:
                a = max(0.0, 1 - rr / (dist + 200))
                c = tuple(int(RED[i] * a + SAND[i] * (1 - a)) for i in range(3))
                d.ellipse((ex - rr, ey - rr, ex + rr, ey + rr), outline=c, width=7)
    # 거리 점선
    n = 26
    for k in range(n):
        if k % 2 == 0:
            a0, a1 = k / n, (k + 1) / n
            d.line((ex + (px - ex) * a0, ey + (py - ey) * a0, ex + (px - ex) * a1, ey + (py - ey) * a1),
                   fill=(70, 50, 30), width=5)
    mx, my = (ex + px) / 2, (ey + py) / 2
    text(d, mx + 30, my + 10, "240km", 64, YEL)
    star(d, ex, ey, 40 + 6 * math.sin(t * 20) * (t > t0), RED)
    text(d, ex, ey + 56, "진앙", 46, WHITE, "ma")
    text(d, ex, ey + 112, "2019.7.5 규모 7.1", 38, WHITE, "ma")
    pool(d, px, py, t0 + 1.5, t, 30)
    text(d, px, py - 96, "데빌스홀", 50, WHITE, "ma")
    text(d, 40, 30, "캘리포니아 → 네바다 사막", 40, (60, 40, 20), stroke=0)


# ── 2) 단면: 땅속 지하수가 출렁 ───────────────────────────────────
def draw_section(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 150), fill=(120, 170, 220))       # 하늘
    d.rectangle((0, 150, W, H), fill=ROCK)
    for k in range(6):                                       # 지층
        y = 210 + k * 95
        d.line([(x, y + 10 * math.sin(x / 70 + k * 2)) for x in range(0, W + 20, 20)], fill=ROCK2, width=6)
    d.rectangle((0, 140, W, 170), fill=SAND)
    # 동굴(좁은 틈, 아래로 갈수록 끝이 안 보임)
    cx = 600
    cave = [(cx - 70, 160), (cx + 60, 160), (cx + 40, 330), (cx + 90, 520), (cx + 50, H), (cx - 60, H), (cx - 90, 520), (cx - 50, 330)]
    d.polygon(cave, fill=(30, 26, 24))
    # 지진파 화살표(왼쪽에서 들어옴)
    hit = 0.9
    for j in range(3):
        x = -120 + (t - j * 0.25) * 650
        if -150 < x < cx - 80:
            y = 380 + j * 110
            d.line((x, y, x + 90, y), fill=RED, width=12)
            d.polygon([(x + 90, y - 22), (x + 130, y), (x + 90, y + 22)], fill=RED)
    text(d, 30, 190, "지진파", 52, RED)
    # 수면: 평소 y=300, 지진파 뒤 ±90px(=4.5m 표시용)
    amp = 0 if t < hit else 90 * math.exp(-(t - hit) * 0.35)
    lvl = 300 + amp * math.sin((t - hit) * 7) if t >= hit else 300
    tilt = 0 if t < hit else 18 * math.sin((t - hit) * 7 + 1.2)
    water = Image.new("RGB", (W, H), WATER2)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.polygon(cave, fill=255)
    md.polygon([(0, 0), (W, 0), (W, lvl + tilt), (0, lvl - tilt)], fill=0)
    img.paste(water, (0, 0), mask)
    d = ImageDraw.Draw(img)
    d.line((cx - 120, lvl - tilt * 1.1, cx + 120, lvl + tilt * 1.1), fill=WATER, width=8)
    # 높이 자
    if t >= hit:
        d.line((cx + 170, 210, cx + 170, 390), fill=YEL, width=6)
        for yy in (210, 390):
            d.line((cx + 150, yy, cx + 190, yy), fill=YEL, width=6)
        text(d, cx + 205, 250, "최대", 40, YEL)
        text(d, cx + 205, 296, "4.5m", 64, YEL)
    text(d, cx, H - 70, "바닥은 아직 아무도 모름", 40, WHITE, "ma")
    text(d, cx - 110, 175, "지하수", 38, (180, 220, 255), "ra")


# ── 3) 거리 비교 ─────────────────────────────────────────────────
ROWS = [("캘리포니아", "240km", 240), ("멕시코", "2,400km", 2400), ("알래스카", "3,200km", 3200)]


def draw_distance(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), fill=(20, 26, 38))
    text(d, W / 2, 34, "이만큼 먼 지진에도 '출렁'", 52, WHITE, "ma")
    x0, x1 = 300, 1010
    for k, (name, lab, km) in enumerate(ROWS):
        y = 230 + k * 190
        ts = 0.2 + k * 0.8
        p = ease(clamp((t - ts) / 0.6))
        text(d, x0, y - 78, name, 44, WHITE)
        L = (x1 - x0) * km / 3200 * p
        d.line((x0, y, x0 + L, y), fill=RED if k == 0 else YEL, width=16)
        if p > 0:
            star(d, x0 + L, y, 24, RED)
            text(d, x0 + max(L, 120) - 10, y + 26, lab, 44, YEL, "ra")
        pool(d, 170, y, ts + 0.6, t, 30)
        if k == 0:
            text(d, 170, y + 40, "데빌스홀", 30, (180, 220, 255), "ma")


run("map", 3.2, draw_map)
run("section", 3.2, draw_section)
run("distance", 3.2, draw_distance)
print("ok", OUT)
