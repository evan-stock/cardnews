#!/usr/bin/env python3
"""공중에 뜬 물방울(워터 펄) — 깜빡이는 조명(스트로보) 착시 모션그래픽(카드 영상 칸 1080x780) — 2026.11.04 오늘의쓸모.
  python3 scripts/story_shorts/anim_pearl.py <출력폴더>
  → fall.mp4   (노즐에서 물방울이 1초에 50~60개씩 쉬지 않고 떨어지는 '진짜 모습', 방울 수 카운터)
    strobe.mp4 (조명을 켜 두면 떨어지는 게 보이다가 → 물방울 박자에 맞춰 '깜빡' 비추면 매번 같은 자리에 → 멈춘 듯.
                오른쪽 아래 박자표: 물방울 ●와 조명 ⚡가 같은 간격)
    rise.mp4   (조명을 물방울보다 살짝 빠르게 깜빡이면, 비출 때마다 방울이 조금씩 위에 찍혀 '거꾸로 올라가' 보임)
근거: 워터펄(株式会社ウォーターパール) 제품 안내(IPROS — 음파로 둥근 물방울을 1초 50~60개 분사, 전용 스트로보 조명,
      잔상 현상으로 떠 있는 것처럼 보임), Science Buddies 'Stroboscopic Effect: Levitating Water Drops'
      (조명 깜빡임 = 물방울 박자면 멈춤, 조금 빠르면 위로, 조금 느리면 천천히 아래로).
"""
import math, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (10, 14, 24); DIM = (40, 48, 64); WHITE = (250, 250, 252); YEL = (255, 210, 60); CYAN = (150, 225, 255)
RED = (232, 60, 50); NOZ = (150, 160, 175)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))
COLS = [190, 340, 490, 640]          # 물방울 줄(x)
TOP, BOT = 120, 740                   # 노즐 아래 ~ 바닥
SP = 110                              # 방울 간격(px)
V = 220                               # 떨어지는 속도(px/s) → 박자 T = SP/V = 0.5s(그래픽용으로 아주 느리게 그림)
T = SP / V


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGB", (W, H), BG)
        draw(img, i / FPS)
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=4):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def nozzles(d):
    d.rectangle((110, 70, 720, 104), fill=NOZ, outline=(90, 100, 115), width=3)
    for x in COLS:
        d.polygon([(x - 18, 104), (x + 18, 104), (x + 7, 124), (x - 7, 124)], fill=NOZ)
    d.rectangle((110, BOT + 6, 720, BOT + 30), fill=(30, 60, 100))  # 바닥 물받이


def drop(d, x, y, col=CYAN, r=17, a=1.0, streak=0):
    c = tuple(int(cc * a + bb * (1 - a)) for cc, bb in zip(col, BG))
    if streak:
        d.line((x, y - streak, x, y), fill=tuple(int(v * 0.5) for v in c), width=10)
    d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    d.ellipse((x - r * 0.45, y - r * 0.55, x - r * 0.05, y - r * 0.15), fill=WHITE if a > 0.6 else c)


def positions(t, phase_col=True):
    """t 초의 방울 y 목록(줄마다 살짝 다른 위상)."""
    out = []
    for k, x in enumerate(COLS):
        off = (k * 0.37 * SP) if phase_col else 0
        y0 = (V * t + off) % SP
        ys = [TOP + y0 + n * SP for n in range(7) if TOP + y0 + n * SP < BOT - 10]
        out.append((x, ys))
    return out


def lamp(d, on, x=900, y=150):
    d.rounded_rectangle((x - 70, y - 40, x + 70, y + 40), 14, fill=(60, 66, 80) if not on else (255, 245, 200),
                        outline=(120, 128, 140), width=3)
    if on:
        for a in range(8):
            ang = a * math.pi / 4
            d.line((x + 90 * math.cos(ang), y + 70 * math.sin(ang), x + 130 * math.cos(ang), y + 100 * math.sin(ang)),
                   fill=YEL, width=7)
    ctext(d, x, y + 110, "조명", 34, stroke=0, fill=YEL if on else (160, 168, 180))


def beat(d, flash_T, t, y=600, label2="조명"):
    """오른쪽 아래 박자표: 위 줄 물방울 ●(간격 T), 아래 줄 조명 ⚡(간격 flash_T)."""
    x0, x1 = 770, 1050
    d.rounded_rectangle((x0 - 20, y - 70, x1 + 10, y + 110), 14, fill=(18, 24, 38), outline=(70, 80, 100), width=2)
    ctext(d, (x0 + x1) / 2, y - 62, "박자", 26, stroke=0, fill=(170, 180, 200))
    pxs = 120  # 1초 = 120px
    scroll = (t * pxs * 0.6) % (T * pxs)
    for n in range(-1, 8):
        xx = x0 + n * T * pxs - scroll
        if x0 - 5 < xx < x1:
            d.ellipse((xx - 9, y - 9, xx + 9, y + 9), fill=CYAN)
    sc2 = (t * pxs * 0.6) % (flash_T * pxs)
    for n in range(-1, 9):
        xx = x0 + n * flash_T * pxs - sc2
        if x0 - 5 < xx < x1:
            d.polygon([(xx - 6, y + 40), (xx + 8, y + 40), (xx - 2, y + 56), (xx + 10, y + 56), (xx - 8, y + 80), (xx - 2, y + 60), (xx - 12, y + 60)], fill=YEL)


def fall(img, t):
    d = ImageDraw.Draw(img)
    nozzles(d)
    for x, ys in positions(t):
        for y in ys:
            drop(d, x, y, streak=26)
    # 오른쪽: 초당 방울 수
    n = int(55 * ease(clamp(t / 1.6)))
    d.rounded_rectangle((770, 260, 1050, 470), 18, fill=(20, 28, 44))
    ctext(d, 910, 276, "노즐 하나에서", 30, stroke=0, fill=(170, 185, 210))
    ctext(d, 910, 318, f"1초 {n}방울" if t < 1.6 else "1초 50~60방울", 56 if t < 1.6 else 46, fill=YEL, stroke=0)
    ctext(d, 910, 398, "쉬지 않고 '뚝뚝'", 34, stroke=0)
    for k in range(3):
        ax = 910; ay = 520 + k * 60 + (t * 120) % 60
        d.polygon([(ax - 22, ay), (ax + 22, ay), (ax, ay + 30)], fill=(90, 110, 140))


def strobe(img, t):
    d = ImageDraw.Draw(img)
    nozzles(d)
    SW = 1.0                      # 앞 1초: 조명 켜 둠 → 떨어지는 게 보임
    if t < SW:
        for x, ys in positions(t):
            for y in ys:
                drop(d, x, y, streak=26)
        lamp(d, True)
        ctext(d, 900, 330, "켜 두면", 40); ctext(d, 900, 384, "떨어지는 게 보임", 32, stroke=0)
        beat(d, T, t)
        return
    # 뒤: 물방울 박자(T)마다 한 번씩 번쩍 → 비춘 순간만 보임(눈에 잔상) → 매번 같은 자리 = 멈춘 듯
    k = math.floor((t - SW) / T)
    tf = SW + k * T
    since = t - tf
    on = since < 0.07
    for x, ys in positions(tf):
        for y in ys:
            drop(d, x, y, a=1.0 if on else 0.85)
    if on:
        d.rectangle((0, 0, W, H), outline=(255, 245, 200), width=10)
    lamp(d, on)
    ctext(d, 900, 330, "박자 맞춰 '깜빡'", 38, fill=YEL)
    ctext(d, 900, 384, "매번 같은 자리 → 멈춘 듯", 28, stroke=0)
    beat(d, T, t)


def rise(img, t):
    d = ImageDraw.Draw(img)
    nozzles(d)
    TF = T * 0.85                 # 조명이 물방울보다 살짝 빠름
    k = math.floor(t / TF)
    tf = k * TF
    on = (t - tf) < 0.07
    # 비출 때마다 실제 위치 = V*tf, 박자로 접으면 한 칸 덜 내려옴 → 화면엔 조금씩 위로
    for x, ys in positions(tf):
        for y in ys:
            drop(d, x, y, a=1.0 if on else 0.85)
    if on:
        d.rectangle((0, 0, W, H), outline=(255, 245, 200), width=10)
    lamp(d, on)
    ctext(d, 900, 330, "조금 '빨리' 깜빡", 38, fill=YEL)
    ctext(d, 900, 384, "비출 때마다 살짝 위", 28, stroke=0)
    # 위로 가는 화살표
    ay = 560 - (t * 50) % 80
    d.polygon([(900, ay - 60), (860, ay), (940, ay)], fill=YEL)
    d.rectangle((888, ay, 912, ay + 70), fill=YEL)
    if t > 1.2:
        ctext(d, 900, 650, "거꾸로 '올라감'", 40, fill=YEL)


run("fall", 3.0, fall)
run("strobe", 3.2, strobe)
run("rise", 3.0, rise)
print("ok")
