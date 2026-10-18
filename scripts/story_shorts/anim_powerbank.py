#!/usr/bin/env python3
"""보조배터리 설명 모션그래픽(카드 영상 칸 1080x780) — 2026.10.18 오늘의쓸모 '보조배터리 못 부치는 이유'.
  python3 scripts/story_shorts/anim_powerbank.py <출력폴더>
  → domino.mp4(열폭주 도미노) cargo.mp4(짐칸: 아무도 못 봄) cabin.mp4(객실: 승무원이 바로 대응)
    bin.mp4(선반 X → 몸 가까이 O) ban.mp4(기내 충전 금지) tape.mp4(단자 절연 테이프)
"""
import math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (243, 246, 250); INK = (30, 34, 44); GRAY = (150, 158, 172); LG = (214, 220, 230)
YEL = (255, 216, 77); RED = (235, 64, 52); ORG = (255, 140, 30); GRN = (46, 184, 92); BLU = (52, 120, 246)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def writer(name):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                             os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)


def ctext(d, cx, y, s, size, fill=INK, stroke=0, sfill=(255, 255, 255)):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=sfill)


def flame(d, cx, by, size, t, seed=0):
    """바닥 by 기준 위로 솟는 불꽃(세 겹)."""
    r = random.Random(seed)
    for k, (col, sc) in enumerate([(RED, 1.0), (ORG, 0.72), (YEL, 0.45)]):
        h = size * sc * (1 + 0.12 * math.sin(t * 18 + k + seed))
        w = size * sc * 0.55
        pts = [(cx - w, by)]
        for i in range(1, 6):
            a = i / 6
            pts.append((cx - w * (1 - a) + r.uniform(-4, 4), by - h * a * 0.6))
        pts += [(cx + w * 0.1 * math.sin(t * 12 + seed), by - h)]
        for i in range(5, 0, -1):
            a = i / 6
            pts.append((cx + w * (1 - a) + r.uniform(-4, 4), by - h * a * 0.6))
        pts.append((cx + w, by))
        d.polygon(pts, fill=col)


def smoke(img, cx, cy, t, n=6, spread=60, col=(90, 90, 96)):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i in range(n):
        ph = (t * 0.9 + i / n) % 1
        x = cx + math.sin(i * 2.1 + t * 2) * spread * ph
        y = cy - ph * 160
        rr = 18 + 50 * ph
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col + (int(150 * (1 - ph)),))
    lay = lay.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(lay)


def battery(d, x, y, w, h, heat=0.0, label=True):
    """셀 하나. heat 0(초록)→1(빨강)."""
    c0, c1 = GRN, RED
    col = tuple(int(c0[i] * (1 - heat) + c1[i] * heat) for i in range(3))
    d.rounded_rectangle((x, y, x + w, y + h), 18, fill=(255, 255, 255), outline=INK, width=6)
    d.rounded_rectangle((x + w * 0.3, y - 16, x + w * 0.7, y + 2), 6, fill=INK)
    lvl = h - 24
    d.rounded_rectangle((x + 12, y + 12, x + w - 12, y + h - 12), 10, fill=col)


def powerbank(d, cx, cy, s=1.0, heat=0.0):
    w, h = 150 * s, 250 * s
    col = tuple(int(INK[i] * (1 - heat) + RED[i] * heat) for i in range(3))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 26 * s, fill=col)
    for i in range(4):
        on = i < 3
        d.ellipse((cx - 36 * s + i * 24 * s - 7 * s, cy + h / 2 - 40 * s, cx - 36 * s + i * 24 * s + 7 * s, cy + h / 2 - 26 * s),
                  fill=(120, 230, 160) if on else (90, 96, 110))
    d.rounded_rectangle((cx - 30 * s, cy - h / 2 - 10 * s, cx + 30 * s, cy - h / 2 + 4 * s), 4, fill=(120, 126, 140))


def person(d, cx, by, s=1.0, col=BLU):
    d.ellipse((cx - 26 * s, by - 150 * s, cx + 26 * s, by - 98 * s), fill=col)
    d.rounded_rectangle((cx - 40 * s, by - 92 * s, cx + 40 * s, by), 30 * s, fill=col)


def check(d, cx, cy, r, ok=True, a=1.0):
    if a <= 0: return
    col = GRN if ok else RED
    rr = r * (0.6 + 0.4 * ease(a))
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=col)
    if ok:
        d.line([(cx - rr * 0.45, cy), (cx - rr * 0.1, cy + rr * 0.35), (cx + rr * 0.5, cy - rr * 0.35)], fill=(255, 255, 255), width=int(rr * 0.22), joint="curve")
    else:
        k = rr * 0.42
        d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=(255, 255, 255), width=int(rr * 0.22))
        d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=(255, 255, 255), width=int(rr * 0.22))


def plane_body(d, top, bot, cabin_line):
    # 동체 단면(옆에서 본 긴 캡슐)
    d.rounded_rectangle((40, top, W - 40, bot), (bot - top) // 2, fill=(255, 255, 255), outline=INK, width=7)
    d.line([(90, cabin_line), (W - 90, cabin_line)], fill=INK, width=6)
    for i in range(9):  # 창문
        x = 150 + i * 92
        d.rounded_rectangle((x, top + 40, x + 36, top + 82), 14, fill=(190, 220, 255), outline=INK, width=3)


def suitcase(d, x, y, w, h, col):
    d.rounded_rectangle((x, y, x + w, y + h), 12, fill=col, outline=INK, width=4)
    d.rounded_rectangle((x + w * 0.35, y - 14, x + w * 0.65, y + 2), 5, outline=INK, width=4)


def run(name, dur, draw):
    p = writer(name); n = int(dur * FPS)
    for i in range(n):
        t = i / FPS
        img = Image.new("RGBA", (W, H), BG + (255,))
        draw(img, t)
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close(); p.wait()


# 1) 열폭주 도미노 — 셀 6개, 왼쪽 한 칸이 달아오르며 옆으로 번짐
def s_domino(img, t):
    d = ImageDraw.Draw(img)
    n, w, h, gap = 6, 120, 230, 30
    x0 = (W - (n * w + (n - 1) * gap)) / 2; y = 360
    for i in range(n):
        st = 0.5 + i * 0.45
        heat = ease(clamp((t - st) / 0.5))
        battery(d, x0 + i * (w + gap), y, w, h, heat)
        if heat > 0.6:
            flame(d, x0 + i * (w + gap) + w / 2, y - 18, 70 + 20 * heat, t, seed=i)
    a = clamp((t - 0.2) / 0.4)
    if a > 0:
        ctext(d, W / 2, 90, "열폭주", 92, RED if int(t * 4) % 2 == 0 or t < 2 else INK)


# 2) 짐칸: 가방 속 보조배터리 → 연기, 아무도 못 봄
def s_cargo(img, t):
    d = ImageDraw.Draw(img)
    top, bot, cl = 170, 640, 440
    plane_body(d, top, bot, cl)
    for i in range(6):  # 객실 승객(위)
        person(d, 220 + i * 120, cl - 6, 0.85, GRAY)
    cols = [(120, 140, 170), (200, 150, 90), (150, 120, 180), (90, 160, 140), (180, 110, 110)]
    for i in range(5):
        suitcase(d, 170 + i * 150, 490, 120, 110, cols[i])
    hx, hy = 170 + 2 * 150 + 60, 545
    heat = ease(clamp((t - 0.6) / 0.8))
    if heat > 0:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        gd.ellipse((hx - 120, hy - 90, hx + 120, hy + 90), fill=RED + (int(150 * heat),))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(30)))
        d = ImageDraw.Draw(img)
        if heat > 0.5: smoke(img, hx, hy - 40, t, n=7, spread=50); d = ImageDraw.Draw(img)
    # 눈 + X : 아무도 못 봄
    a = clamp((t - 1.6) / 0.4)
    if a > 0:
        ex, ey = W / 2, 95
        d.ellipse((ex - 90, ey - 45, ex + 90, ey + 45), outline=INK, width=8)
        d.ellipse((ex - 24, ey - 24, ex + 24, ey + 24), fill=INK)
        d.line([(ex - 110, ey + 60), (ex + 110, ey - 60)], fill=RED, width=14)
    ctext(d, W / 2, 680, "짐칸", 52, RED)


# 3) 객실: 승객 손의 보조배터리 연기 → 승무원이 바로 와서 대응 ✓
def s_cabin(img, t):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 150, W - 40, 640), 60, fill=(255, 255, 255), outline=INK, width=7)
    for i in range(5):  # 좌석
        x = 120 + i * 190
        d.rounded_rectangle((x, 380, x + 110, 600), 24, fill=LG)
    person(d, 365, 560, 1.1, BLU)
    heat = ease(clamp((t - 0.4) / 0.6))
    powerbank(d, 450, 470, 0.38, heat)
    if heat > 0.5:
        smoke(img, 450, 420, t, n=5, spread=30); d = ImageDraw.Draw(img)
    # 승무원 이동
    k = ease(clamp((t - 1.0) / 1.0))
    cx = 980 - k * 380
    person(d, cx, 600, 1.25, (240, 120, 40))
    if k > 0.95:
        d.rounded_rectangle((cx - 90, 470, cx - 50, 560), 10, fill=RED)  # 소화기
    check(d, W / 2, 100, 60, True, clamp((t - 2.2) / 0.3))
    ctext(d, W / 2, 680, "객실", 52, GRN)


# 4) 선반 X (연기 안 보임) → 몸 가까이 O
def s_bin(img, t):
    d = ImageDraw.Draw(img)
    # 왼쪽: 선반
    lx = W * 0.27
    d.rounded_rectangle((lx - 200, 200, lx + 200, 330), 30, fill=(255, 255, 255), outline=INK, width=7)
    d.line([(lx - 200, 300), (lx + 200, 300)], fill=INK, width=4)
    if t > 0.5:
        smoke(img, lx + 150, 210, t, n=5, spread=25, col=(170, 170, 176)); d = ImageDraw.Draw(img)
    check(d, lx, 470, 70, False, clamp((t - 0.6) / 0.3))
    ctext(d, lx, 580, "선반 위", 54, RED)
    # 오른쪽: 몸 가까이(좌석 앞 주머니)
    rx = W * 0.73
    d.rounded_rectangle((rx - 120, 180, rx + 120, 420), 30, fill=LG)
    d.rounded_rectangle((rx - 90, 300, rx + 90, 400), 16, fill=(200, 206, 218), outline=INK, width=4)
    powerbank(d, rx, 300, 0.32, 0)
    check(d, rx, 470, 70, True, clamp((t - 1.4) / 0.3))
    ctext(d, rx, 580, "몸 가까이", 54, GRN)
    d.line([(W / 2, 170), (W / 2, 640)], fill=LG, width=4)


# 5) 기내 충전 금지
def s_ban(img, t):
    d = ImageDraw.Draw(img)
    a = ease(clamp(t / 0.5))
    # 휴대폰 + 보조배터리 + 케이블
    px, py = W / 2 + 140, 330
    d.rounded_rectangle((px - 75, py - 140, px + 75, py + 140), 24, fill=INK)
    d.rounded_rectangle((px - 62, py - 120, px + 62, py + 110), 14, fill=(120, 180, 255))
    powerbank(d, W / 2 - 160, 360, 0.6, 0)
    d.line([(W / 2 - 160, 440), (W / 2 - 160, 520), (px, 520), (px, py + 140)], fill=INK, width=8, joint="curve")
    r = 250 * (0.7 + 0.3 * a)
    if t > 0.6:
        d.ellipse((W / 2 - r, 340 - r, W / 2 + r, 340 + r), outline=RED, width=26)
        d.line([(W / 2 - r * 0.7, 340 + r * 0.7), (W / 2 + r * 0.7, 340 - r * 0.7)], fill=RED, width=26)
    ctext(d, W / 2, 640, "2026.1.26~ 기내 충전 금지", 50, INK)
    ctext(d, W / 2, 705, "대한항공·아시아나·진에어·에어부산·에어서울", 34, GRAY)


# 6) 단자 절연 테이프
def s_tape(img, t):
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 360
    d.rounded_rectangle((cx - 300, cy - 150, cx + 300, cy + 150), 40, fill=INK)
    ports = [cx - 150, cx, cx + 150]
    for px in ports:
        d.rounded_rectangle((px - 45, cy - 30, px + 45, cy + 30), 10, fill=(200, 205, 215))
    # 테이프가 왼쪽에서 밀려 들어옴
    k = ease(clamp((t - 0.4) / 1.0))
    tx = cx - 520 + k * 520
    d.rounded_rectangle((tx - 240, cy - 50, tx + 240, cy + 50), 8, fill=YEL + (255,))
    if k > 0.98:
        check(d, cx + 330, cy - 170, 60, True, clamp((t - 1.5) / 0.3))
    ctext(d, W / 2, 600, "절연 테이프", 56, INK)


os.makedirs(OUT, exist_ok=True)
run("domino", 4.2, s_domino)
run("cargo", 3.8, s_cargo)
run("cabin", 3.6, s_cabin)
run("bin", 3.4, s_bin)
run("ban", 3.4, s_ban)
run("tape", 3.4, s_tape)
print("ok", OUT)
