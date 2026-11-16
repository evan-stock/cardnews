#!/usr/bin/env python3
"""비행기 화장실 재떨이 설명 모션그래픽(카드 영상 칸 1080x780) — 2026.10.25 오늘의쓸모 '금연 비행기 화장실 재떨이'.
  python3 scripts/story_shorts/anim_ashtray.py <출력폴더>
  → bin.mp4(몰래 피운 꽁초를 휴지통에 버리면 휴지에 불이 붙음)
    smoke.mp4(1973 화장실에서 난 연기가 객실을 채운 여객기 — 사고 장면은 그리지 않음)
    gate.mp4(점검표 '재떨이 ✗' → 출발 보류, 시계가 돎)
"""
import math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (18, 28, 46); PANEL = (44, 58, 84); EDGE = (86, 106, 140); INK = (240, 244, 250); GRAY = (150, 162, 182)
YEL = (255, 216, 77); RED = (240, 66, 56); GRN = (46, 196, 100); ORG = (255, 140, 40); SMOKE = (190, 196, 206)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = Image.new("RGBA", (W, H), BG + (255,))
        draw(img, i / FPS)
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=INK):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill)


def flame(d, cx, by, h, w, t, seed=0):
    """흔들리는 불꽃(바깥 주황, 안 노랑)."""
    for col, sc in ((RED, 1.0), (ORG, 0.78), (YEL, 0.5)):
        top = (cx + 10 * math.sin(t * 9 + seed), by - h * sc * 1.25)
        d.polygon([(cx - w * sc * 0.5, by), (cx - w * sc * 0.35, by - h * sc * 0.6), top,
                   (cx + w * sc * 0.35, by - h * sc * 0.6), (cx + w * sc * 0.5, by)], fill=col)


def puffs(img, t, x0, y0, n, spread, rise, alpha=170, t0=0.0, size=40):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rnd = random.Random(7)
    for k in range(n):
        st = t0 + rnd.random() * 1.5
        a = t - st
        if a <= 0:
            continue
        ph = (a % 2.2) / 2.2
        x = x0 + rnd.uniform(-spread, spread) + 40 * math.sin(a * 2 + k)
        y = y0 - rise * ph
        r = size * (0.5 + ph * 1.6)
        al = int(alpha * (1 - ph) * clamp(a * 2))
        d.ellipse((x - r, y - r, x + r, y + r), fill=SMOKE + (al,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(8)))


# ── 1. 휴지통에 꽁초 ─────────────────────────────────
def s_bin(img, t):
    d = ImageDraw.Draw(img)
    # 화장실 벽면 + 휴지통 뚜껑(밀어서 여는 플랩)
    d.rounded_rectangle((300, 120, 780, 740), 30, fill=PANEL, outline=EDGE, width=4)
    d.rounded_rectangle((380, 200, 700, 290), 16, fill=(70, 86, 116), outline=EDGE, width=4)
    ctext(d, 540, 214, "휴지통 PUSH", 40, GRAY)
    # 속(단면): 휴지 뭉치
    d.rectangle((330, 320, 750, 710), fill=(30, 40, 60))
    rnd = random.Random(3)
    for k in range(34):
        x = rnd.uniform(350, 730); y = rnd.uniform(470, 700); r = rnd.uniform(26, 50)
        d.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=(232, 234, 238), outline=(190, 194, 204), width=2)
    # 꽁초가 떨어짐
    k = ease(clamp((t - 0.2) / 0.8))
    cx, cy = 540 + 30 * k, 260 + 230 * k
    ang = 0.6 + 1.2 * k
    c, s = math.cos(ang), math.sin(ang)
    L = 70
    d.line((cx - c * L / 2, cy - s * L / 2, cx + c * L / 2, cy + s * L / 2), fill=(250, 250, 250), width=14)
    d.line((cx + c * L / 2 - c * 18, cy + s * L / 2 - s * 18, cx + c * L / 2, cy + s * L / 2), fill=ORG, width=14)
    if t > 1.0:
        g = ease(clamp((t - 1.0) / 1.6))
        flame(d, 560, 520, 60 + 220 * g, 80 + 240 * g, t)
        puffs(img, t, 560, 380 - 120 * g, 14, 160, 260, 160, 1.0, 50)
    if t > 2.0:
        d = ImageDraw.Draw(img)
        a = ease(clamp((t - 2.0) / 0.3))
        r = 46 * a
        d.ellipse((900 - r, 140 - r, 900 + r, 140 + r), fill=RED)
        if a > 0.6:
            ctext(d, 900, 104, "!", 56)


# ── 2. 1973 화장실 연기 ───────────────────────────────
def plane_side(d, x0, y0, s, col=INK):
    d.rounded_rectangle((x0, y0, x0 + 700 * s, y0 + 110 * s), int(55 * s), fill=col)
    d.polygon([(x0 + 640 * s, y0 + 10 * s), (x0 + 720 * s, y0 - 110 * s), (x0 + 770 * s, y0 - 110 * s),
               (x0 + 700 * s, y0 + 40 * s)], fill=col)
    d.polygon([(x0 + 260 * s, y0 + 70 * s), (x0 + 380 * s, y0 + 70 * s), (x0 + 300 * s, y0 + 200 * s),
               (x0 + 250 * s, y0 + 200 * s)], fill=(200, 206, 216))
    for k in range(14):
        wx = x0 + (90 + k * 38) * s
        d.ellipse((wx, y0 + 28 * s, wx + 18 * s, y0 + 50 * s), fill=(60, 80, 110))


def s_smoke(img, t):
    d = ImageDraw.Draw(img)
    ctext(d, 540, 40, "1973", 110, YEL)
    plane_side(d, 160, 360, 1.0)
    # 뒤쪽 화장실 칸 표시
    lx = 160 + 600
    d.rounded_rectangle((lx - 40, 372, lx + 20, 452), 10, fill=(70, 86, 116))
    ctext(d, lx - 10, 384, "WC", 30, INK)
    g = ease(clamp((t - 0.4) / 2.2))
    # 연기가 뒤에서 앞으로 객실을 채움(창문을 회색으로 덮음)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    front = lx - 620 * g
    ld.rounded_rectangle((max(front, 170), 380, lx + 20, 460), 30, fill=(120, 124, 132, int(220 * clamp(g * 3))))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6)))
    puffs(img, t, lx - 80, 360, 12, 70, 200, 150, 0.4, 36)
    d = ImageDraw.Draw(img)
    if t > 1.2:
        a = ease(clamp((t - 1.2) / 0.4))
        ctext(d, 540, 620, "화장실 휴지통 불 → 객실에 연기", 54 if a > 0.99 else int(54 * a) + 1, RED)


# ── 3. 출발 전 점검표 ─────────────────────────────────
def s_gate(img, t):
    d = ImageDraw.Draw(img)
    # 점검표
    d.rounded_rectangle((90, 90, 590, 700), 26, fill=(236, 240, 246))
    ctext(d, 340, 112, "출발 전 점검", 50, (30, 40, 60))
    items = ["엔진", "연료", "비상구", "연기 감지기", "재떨이"]
    for k, it in enumerate(items):
        y = 210 + k * 92
        show = clamp((t - 0.15 * k) / 0.25)
        if show <= 0:
            continue
        d.text((140, y), it, font=F(46), fill=(30, 40, 60))
        if k < 4:
            d.line((480, y + 32, 505, y + 56, 550, y + 6), fill=GRN, width=12)
        elif t > 1.0:
            a = ease(clamp((t - 1.0) / 0.3))
            r = 30 * a
            d.line((515 - r, y + 31 - r, 515 + r, y + 31 + r), fill=RED, width=13)
            d.line((515 - r, y + 31 + r, 515 + r, y + 31 - r), fill=RED, width=13)
    if t > 1.0:
        a = ease(clamp((t - 1.0) / 0.3))
        d.rounded_rectangle((115, 566, 568, 646), 14, outline=RED, width=int(2 + 5 * a))
    # 시계(바늘이 빨리 돎)
    cx, cy, R = 820, 330, 170
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(236, 240, 246), outline=EDGE, width=8)
    for k in range(12):
        a = k * math.pi / 6
        d.line((cx + math.sin(a) * (R - 30), cy - math.cos(a) * (R - 30), cx + math.sin(a) * (R - 12),
                cy - math.cos(a) * (R - 12)), fill=(60, 70, 90), width=6)
    sp = 0 if t < 1.3 else (t - 1.3) * 3.2
    hm = sp * 2 * math.pi
    hh = sp * 2 * math.pi / 12
    d.line((cx, cy, cx + math.sin(hm) * (R - 40), cy - math.cos(hm) * (R - 40)), fill=(30, 40, 60), width=8)
    d.line((cx, cy, cx + math.sin(hh) * (R - 80), cy - math.cos(hh) * (R - 80)), fill=(30, 40, 60), width=12)
    d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=RED)
    if t > 1.3:
        a = ease(clamp((t - 1.3) / 0.4))
        d.rounded_rectangle((640, 560, 1000, 650), 18, fill=RED)
        ctext(d, 820, 568, "출발 보류", 52, INK)


run("bin", 3.0, s_bin)
run("smoke", 3.0, s_smoke)
run("gate", 3.2, s_gate)
print("ok", OUT)
