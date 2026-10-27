#!/usr/bin/env python3
"""비행 중 비상문 — 기압차 재연 모션그래픽(카드 영상 칸 1080x780) — 2026.10.27 오늘의쓸모.
  python3 scripts/story_shorts/anim_exitdoor.py <출력폴더>
  → cruise.mp4(고도 9km: 기내 공기 알갱이가 빽빽, 밖은 듬성. 문은 틀보다 커서 안으로 당겨야 열리는데
                기내 공기가 '몇 톤' 힘으로 문을 틀에 꽉 눌러 붙임 — 손이 당겨도 꿈쩍 안 함)
    descent.mp4(고도계 9,000m → 200m 로 내려가며 안팎 알갱이 수가 같아지고 화살표가 줄어 0 → 문이 안쪽으로 쑥 당겨짐)
"""
import math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
SKY = (70, 120, 190); CABIN = (236, 226, 206); WALL = (200, 206, 216); EDGE = (90, 100, 120)
INK = (24, 30, 44); WHITE = (250, 250, 252); RED = (232, 48, 44); YEL = (255, 210, 60); BLUE = (40, 90, 200)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))
random.seed(7)
IN_P = [(random.uniform(560, 1060), random.uniform(60, 720), random.uniform(0, 6.28)) for _ in range(150)]
OUT_P = [(random.uniform(20, 470), random.uniform(60, 720), random.uniform(0, 6.28)) for _ in range(150)]


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), SKY)
        draw(img, i / FPS)
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=4):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def arrow(d, x0, y, length, thick, col):
    """오른쪽→왼쪽(기내에서 밖으로) 미는 화살표. 머리 끝이 x0."""
    if length < 8:
        return
    head = min(length * 0.45, thick * 2.2)
    d.rectangle((x0 + head, y - thick / 2, x0 + length, y + thick / 2), fill=col)
    d.polygon([(x0, y), (x0 + head, y - thick * 1.2), (x0 + head, y + thick * 1.2)], fill=col)


def scene(img, t, n_out, push, door_dx, alt_txt, label, hand_pull):
    d = ImageDraw.Draw(img)
    # 기내(오른쪽)
    d.rectangle((520, 0, W, H), fill=CABIN)
    # 바깥 공기 알갱이(듬성) / 기내(빽빽)
    for k, (x, y, ph) in enumerate(OUT_P[:n_out]):
        xx = x + 6 * math.sin(t * 3 + ph); yy = y + 6 * math.cos(t * 2.6 + ph)
        d.ellipse((xx - 7, yy - 7, xx + 7, yy + 7), fill=(200, 225, 255))
    for x, y, ph in IN_P:
        xx = x + 6 * math.sin(t * 3 + ph); yy = y + 6 * math.cos(t * 2.6 + ph)
        d.ellipse((xx - 7, yy - 7, xx + 7, yy + 7), fill=(150, 170, 210))
    # 동체 벽(틀) — 문 구멍 y 200~600
    d.rectangle((470, 0, 520, 200), fill=WALL, outline=EDGE, width=3)
    d.rectangle((470, 600, 520, H), fill=WALL, outline=EDGE, width=3)
    # 문(플러그): 틀보다 위아래로 큼, 기내 쪽에 붙음. door_dx>0 이면 기내로 당겨짐
    dx = 520 + door_dx
    d.rounded_rectangle((dx, 170, dx + 46, 630), 10, fill=(232, 236, 244), outline=EDGE, width=4)
    d.rectangle((dx + 10, 360, dx + 38, 440), fill=(60, 70, 90))  # 손잡이
    # 손(당기기)
    hx = dx + 60 + hand_pull
    d.rounded_rectangle((hx, 375, hx + 120, 425), 22, fill=(240, 196, 160), outline=(170, 120, 90), width=3)
    for k in range(4):
        d.rounded_rectangle((hx - 8, 372 + k * 14, hx + 30, 384 + k * 14), 6, fill=(240, 196, 160), outline=(170, 120, 90), width=2)
    # 미는 화살표(기내→문)
    for k, yy in enumerate((230, 320, 480, 570)):
        wob = 6 * math.sin(t * 8 + k)
        arrow(d, dx + 52, yy, push * (300 + wob), 10 + 18 * (push > 0.3) * push, RED)
    # 고도계·라벨
    d.rounded_rectangle((40, 40, 420, 150), 18, fill=(20, 28, 44))
    ctext(d, 230, 52, "고도", 30, fill=(160, 175, 200), stroke=0)
    ctext(d, 230, 86, alt_txt, 46, fill=YEL, stroke=0)
    ctext(d, 260, 640, "바깥 공기", 34)
    ctext(d, 800, 640, "기내 공기", 34, fill=INK, stroke=0)
    if label:
        ctext(d, 780, 70, label, 46, fill=RED, stroke=0)


def cruise(img, t):
    shake = 3 * math.sin(t * 40) if t > 1.0 else 0
    scene(img, t, 38, 1.0, 0, "9,000 m", "몇 톤의 힘" if t > 0.6 else "", 10 + shake)


def descent(img, t):
    k = ease(clamp((t - 0.3) / 2.2))
    alt = int(9000 - (9000 - 200) * k)
    n_out = int(38 + (150 - 38) * k)
    push = 1 - k
    pull = ease(clamp((t - 2.7) / 0.6))
    scene(img, t, n_out, push, int(150 * pull), f"{alt:,} m", "힘 ≈ 0" if k > 0.95 else "", 10 + int(150 * pull))


run("cruise", 3.6, cruise)
run("descent", 3.8, descent)
print("ok")
