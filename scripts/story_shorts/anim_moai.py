#!/usr/bin/env python3
"""이스터섬 모아이는 '걸어서' 왔다 — 모션그래픽(카드 영상 칸 1080x780) — 2026.11.03 오늘의쓸모.
  python3 scripts/story_shorts/anim_moai.py <출력폴더>
  → roll.mp4    (누운 모아이를 통나무 위로 굴려 옮기는 그림 + '최대 80톤' → 학자들의 통나무설)
    legend.mp4  (섬 사람 말풍선 "모아이는 걸어서 왔다" → '전설일 뿐' 도장이 쾅)
    walk.mp4    (D자 밑면 + 앞으로 기운 석상, 좌우 밧줄로 흔들면 지그재그로 전진 + 18명·40분·100m 카운터)
근거: Lipo & Hunt 2025, Journal of Archaeological Science 183:106383(4.35톤 복제품, 18명, 40분에 100m, D자 밑면·앞으로 기움, 962개 분석),
      Univ. of Arizona 인류학과 보도(라파누이 구전 '석상이 걸어왔다', 서양 학자들은 신화로 치부하고 통나무설, 최대 80톤), Sci.News 2025.10.7.
"""
import math, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (18, 24, 34); STONE = (176, 160, 130); STONE_D = (120, 106, 84); GROUND = (92, 74, 54); GRASS = (70, 120, 60)
WOOD = (140, 92, 50); WOOD_D = (96, 60, 30); WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (226, 50, 44)
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


def ctext(d, cx, y, s, size, fill=WHITE, stroke=5):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def moai_pts(cx, by, s, lean=0.0, roll=0.0):
    """서 있는 모아이 외곽선(옆모습 비슷한 정면 실루엣). cx=밑면 가운데, by=바닥 y, lean=앞으로 기움(라디안), roll=좌우 흔들림(라디안)."""
    base = [(-70, 0), (70, 0), (78, -40), (72, -160), (60, -200), (64, -240), (56, -300), (40, -320),
            (-40, -320), (-56, -300), (-64, -240), (-60, -200), (-72, -160), (-78, -40)]
    # 흔들림 축 = 밑면 한쪽 모서리(roll>0 이면 오른쪽 모서리로 서서 왼쪽이 들림)
    px = 70 if roll >= 0 else -70
    out = []
    for x, y in base:
        x, y = x * s, y * s
        dx, dy = x - px * s, y
        c, sn = math.cos(roll), math.sin(roll)
        x2, y2 = px * s + dx * c - dy * sn, dx * sn + dy * c
        out.append((cx + x2 + (-y2) * math.sin(lean) * 0.0, by + y2))
    return out


def draw_moai(d, cx, by, s, roll=0.0):
    pts = moai_pts(cx, by, s, roll=roll)
    d.polygon(pts, fill=STONE, outline=STONE_D)
    # 얼굴(눈썹·코·입) — 몸통 위쪽 기준점에서 같이 회전
    def P(x, y):
        px = 70 if roll >= 0 else -70
        x, y = x * s, y * s
        dx, dy = x - px * s, y
        c, sn = math.cos(roll), math.sin(roll)
        return (cx + px * s + dx * c - dy * sn, by + dx * sn + dy * c)
    d.line([P(-44, -268), P(44, -268)], fill=STONE_D, width=max(3, int(10 * s)))
    d.polygon([P(-10, -262), P(10, -262), P(16, -215), P(-16, -215)], fill=STONE_D)
    d.line([P(-26, -192), P(26, -192)], fill=STONE_D, width=max(3, int(7 * s)))
    d.line([P(-58, -150), P(-20, -110)], fill=STONE_D, width=max(2, int(5 * s)))
    d.line([P(58, -150), P(20, -110)], fill=STONE_D, width=max(2, int(5 * s)))
    return P


def roll(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 610, W, H), fill=GROUND)
    # 통나무 4개(굴러감)
    shift = 160 * ease(clamp(t / 2.0))
    for k in range(4):
        x = 140 + k * 190 + shift * 0.5
        d.ellipse((x - 38, 532, x + 38, 608), fill=WOOD, outline=WOOD_D, width=5)
        a = t * 4 + k
        d.line((x, 570, x + 30 * math.cos(a), 570 + 30 * math.sin(a)), fill=WOOD_D, width=5)
    # 누운 모아이
    mx = 110 + shift
    d.rounded_rectangle((mx, 430, mx + 560, 532), 30, fill=STONE, outline=STONE_D, width=4)
    d.rounded_rectangle((mx + 440, 410, mx + 600, 532), 30, fill=STONE, outline=STONE_D, width=4)
    d.line((mx + 470, 440, mx + 470, 500), fill=STONE_D, width=8)
    ctext(d, 540, 40, "통나무 위로 굴렸다?", 64, YEL)
    if t > 0.8:
        ctext(d, 540, 130, "무게는 최대 80톤", 52)
    if t > 1.9:
        k = ease(clamp((t - 1.9) / 0.25))
        cx0, cy0 = 520, 470
        d.line((cx0 - 260 * k, cy0 - 140 * k, cx0 + 260 * k, cy0 + 140 * k), fill=RED, width=18)
        d.line((cx0 + 260 * k, cy0 - 140 * k, cx0 - 260 * k, cy0 + 140 * k), fill=RED, width=18)
        ctext(d, 540, 680, "오래 정답처럼 여겨진 설명", 40, (220, 220, 220), 4)


def legend(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 640, W, H), fill=GRASS)
    # 섬 사람(단순 실루엣)
    d.ellipse((150, 380, 250, 480), fill=(120, 80, 60))
    d.rounded_rectangle((130, 480, 270, 650), 40, fill=(200, 90, 60))
    # 모아이
    draw_moai(d, 820, 640, 1.2)
    # 말풍선
    k = ease(clamp(t / 0.4))
    if k > 0:
        d.rounded_rectangle((260, 150, 260 + 470 * k, 330), 40, fill=WHITE, outline=(0, 0, 0), width=5)
        d.polygon([(290, 320), (330, 320), (240, 400)], fill=WHITE)
        if k >= 1:
            ft = F(52)
            d.text((300, 180), "모아이는", font=ft, fill=(30, 30, 30))
            d.text((300, 250), "'걸어서' 왔어", font=ft, fill=(200, 40, 30))
    ctext(d, 540, 30, "대대로 내려온 이야기", 50, YEL)
    if t > 1.3:
        s = 1.6 - 0.6 * ease(clamp((t - 1.3) / 0.2))
        ft = F(int(90 * s)); txt = "전설일 뿐"
        w = d.textlength(txt, font=ft)
        cx, cy = 470, 500
        d.rounded_rectangle((cx - w / 2 - 30, cy - 70 * s, cx + w / 2 + 30, cy + 70 * s), 16, outline=RED, width=10)
        d.text((cx - w / 2, cy - 62 * s), txt, font=ft, fill=RED)
        ctext(d, 540, 690, "학자들은 '신화'라며 믿지 않았다", 40, (220, 220, 220), 4)


def walk(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 600, W, H), fill=GROUND)
    # 걸음: 0.6초마다 좌우로 흔들며 조금씩 전진
    period = 0.6
    ph = (t % (2 * period)) / (2 * period)
    rollang = 0.16 * math.sin(ph * 2 * math.pi)
    steps = t / period
    cx = 330 + 50 * steps
    # 지나온 발자국(지그재그)
    for k in range(int(steps)):
        fx = 300 + 55 * k + (35 if k % 2 else -35) * 0.6
        d.ellipse((fx - 24, 612, fx + 24, 628), fill=(70, 54, 38))
    P = draw_moai(d, cx, 600, 1.35, roll=rollang)
    # 좌우 밧줄
    head = P(0, -300)
    d.line((head, (cx - 420, 330)), fill=(230, 200, 140), width=6)
    d.line((head, (cx + 420, 330)), fill=(230, 200, 140), width=6)
    if rollang > 0.05:
        ctext(d, max(90, cx - 330), 280, "당겨!", 44, YEL)
    elif rollang < -0.05:
        ctext(d, min(990, cx + 330), 280, "당겨!", 44, YEL)
    ctext(d, 540, 30, "둥근 D자 밑면 + 앞으로 기운 몸", 46, YEL)
    if t > 1.0:
        k = clamp((t - 1.0) / 1.4)
        m, dist = int(40 * k + 0.5), int(100 * k + 0.5)
        ctext(d, 540, 680, f"18명이 {m}분 동안 {dist}m", 58, WHITE, 6)


run("roll", 2.8, roll)
run("legend", 2.6, legend)
run("walk", 3.0, walk)
print("ok")
