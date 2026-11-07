#!/usr/bin/env python3
"""'불을 대도 안 녹는 눈' 모션그래픽(영상 칸 1080x780) — 2026.11.07 오늘의쓸모.
  python3 scripts/story_shorts/anim_snowfire.py <출력폴더>
  → sponge.mp4 (눈뭉치 단면: 눈은 대부분 공기 → 불에 녹은 물은 바로 옆 눈이 스펀지처럼 빨아들임, 일부는 수증기로)
    soot.mp4   (라이터 가스가 덜 타서 생긴 '그을음'이 눈에 묻음 → 닦으면 다시 하얀 눈)
    years.mp4  (2014 애틀랜타 → 2021 텍사스 → 2026 미국 동부, 겨울마다 돌아오는 '가짜 눈' 소문)
근거: PolitiFact 2021.2.19 'No, snow isn't government-generated'(녹은 물을 주변 눈이 흡수, 검은 자국은 라이터 그을음),
      Full Fact 'Videos showing burning snow do not prove it is fake', USA Today 팩트체크 2021(승화),
      Yahoo 2014.1 애틀랜타 'chemtrail snow' 소문, AccuWeather 2026.1(뉴저지 영상 해명).
"""
import math, subprocess, sys, os, random
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (240, 70, 50); BLUE = (110, 190, 255)
NIGHT = (24, 32, 52); NIGHT_D = (10, 14, 26); SNOW = (238, 244, 252); SOOT = (40, 38, 40)
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


def flame(d, x, y, t, s=1.0):
    fl = 1 + 0.12 * math.sin(t * 23)
    h = 120 * s * fl; w = 44 * s
    d.polygon([(x - w, y), (x, y - h), (x + w, y)], fill=(255, 150, 40))
    d.polygon([(x - w * 0.5, y), (x, y - h * 0.6), (x + w * 0.5, y)], fill=(255, 235, 120))
    d.rectangle([x - 26 * s, y, x + 26 * s, y + 150 * s], fill=(200, 40, 40), outline=(0, 0, 0), width=3)


BG = grad(NIGHT, NIGHT_D)
random.seed(7)
# 눈 결정(작은 육각 별)들 — 사이가 빈 공간(공기)
FLAKES = [(random.uniform(470, 1010), random.uniform(120, 660), random.uniform(16, 28), random.uniform(0, 1))
          for _ in range(46)]


def star(d, x, y, r, col, wid=4):
    for k in range(3):
        a = k * math.pi / 3
        d.line([(x - r * math.cos(a), y - r * math.sin(a)), (x + r * math.cos(a), y + r * math.sin(a))], fill=col, width=wid)


# ---------- 1. sponge: 눈은 대부분 공기 → 녹은 물을 빨아들임 ----------
def sponge(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    # 확대 원(눈뭉치 단면)
    cx, cy, R = 740, 390, 300
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(34, 46, 72), outline=SNOW, width=6)
    for (x, y, r, ph) in FLAKES:
        if (x - cx) ** 2 + (y - cy) ** 2 < (R - 25) ** 2:
            star(d, x, y, r, SNOW)
    if t < 1.3:
        ctext(d, 250, 140, "눈뭉치 속을", 52)
        ctext(d, 250, 210, "확대하면", 52)
        if t > 0.5:
            ctext(d, 250, 330, "대부분", 50)
            ctext(d, 250, 400, "'빈 공간'", 64, BLUE)
    # 불꽃이 왼쪽 아래에서
    fx, fy = 440, 640
    if t > 1.1:
        flame(d, fx, fy, t, 0.8)
        # 녹은 물방울이 안쪽 빈 틈으로 빨려 들어감
        a = clamp((t - 1.3) / 1.6)
        for k in range(7):
            ph = (a * 1.4 + k / 7) % 1
            x = fx + 60 + (cx - fx + 40) * ph * (0.6 + 0.1 * k)
            y = fy - 90 - 250 * ph * (0.4 + 0.08 * k)
            d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=BLUE, outline=(0, 0, 0), width=2)
        arrow(d, 500, 520, 640 + 80 * ease(a), 400 - 60 * ease(a), YEL, 12)
    if t > 1.6:
        d.rectangle([0, 560, 420, 780], fill=NIGHT_D)
        ctext(d, 210, 470, "녹은 물은", 50)
        ctext(d, 210, 540, "옆 눈이 '쏙'", 56, BLUE)
        ctext(d, 210, 610, "(스펀지처럼)", 40, (200, 215, 235))
    return im


# ---------- 2. soot: 까만 건 라이터 그을음 ----------
def soot(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    bx, by, br = 600, 330, 210
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=SNOW, outline=(180, 190, 205), width=4)
    fx, fy = 600, 700
    k = ease(t / 1.4)
    wipe = clamp((t - 2.0) / 0.8)
    # 그을음 얼룩(아래쪽부터 번짐), 닦으면 사라짐
    r = 30 + 120 * k
    if wipe < 1:
        sm = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sm)
        sd.ellipse([bx - r, by + br - 40 - r * 0.7, bx + r, by + br - 40 + r * 0.5], fill=SOOT + (int(230 * (1 - wipe)),))
        im.paste(sm, (0, 0), sm); d = ImageDraw.Draw(im)
    if t < 2.0:
        flame(d, fx, fy - 40, t, 0.9)
        # 덜 탄 탄소 알갱이(검은 점)가 위로
        for j in range(14):
            ph = (t * 1.2 + j / 14) % 1
            x = fx + 50 * math.sin(j * 1.7 + t * 3)
            y = fy - 150 - 150 * ph
            d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(20, 20, 20))
        ctext(d, 200, 120, "라이터 가스가", 46)
        ctext(d, 200, 180, "덜 타면", 46)
        ctext(d, 200, 270, "그을음", 70, (160, 160, 160))
    else:
        # 휴지로 닦는 손(흰 사각형)
        wx = bx - 200 + 400 * wipe
        d.rounded_rectangle([wx - 70, by + 120, wx + 70, by + 220], 18, fill=(255, 255, 255), outline=(0, 0, 0), width=4)
        ctext(d, 200, 160, "닦아 보면", 52)
        ctext(d, 200, 240, "그냥 하얀 눈", 52, BLUE)
    if t > 1.2:
        ctext(d, 880, 560, "탄 건 눈이", 46)
        ctext(d, 880, 620, "아니라 연료", 52, YEL)
    return im


# ---------- 3. years: 겨울마다 돌아오는 소문 ----------
YEARS = [("2014", "미국 애틀랜타"), ("2021", "미국 텍사스"), ("2026", "미국 동부")]


def years(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    ctext(d, W / 2, 40, "'가짜 눈' 소문, 언제부터?", 56, YEL)
    d.line([(120, 400), (960, 400)], fill=(120, 140, 170), width=8)
    for i, (y, place) in enumerate(YEARS):
        a = ease((t - 0.35 - i * 0.55) / 0.4)
        if a <= 0:
            continue
        x = 200 + i * 340
        r = 22 * a
        d.ellipse([x - r, 400 - r, x + r, 400 + r], fill=RED, outline=WHITE, width=4)
        ctext(d, x, 230 - 30 * (1 - a), y, int(84 * (0.6 + 0.4 * a)))
        ctext(d, x, 450, place, 40)
    if t > 2.1:
        ctext(d, W / 2, 580, "폭설이 올 때마다 다시 돌아요", 50)
    return im


run("sponge", 3.4, sponge)
run("soot", 3.0, soot)
run("years", 3.0, years)
print("ok")
