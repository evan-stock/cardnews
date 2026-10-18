#!/usr/bin/env python3
"""'양치 후 헹구지 마라' 설명 모션그래픽(카드 영상 칸 1080x780) — 2026.10.18 오늘의쓸모.
  python3 scripts/story_shorts/anim_norinse.py <출력폴더>
  → count.mp4(헹굼 10번 카운트) rumor.mp4(6번·10번 헹궈라 말풍선) nhs.mp4(뱉기 O / 헹구기 X)
    settle.mp4(불소가 이에 내려앉음) wash.mp4(물이 불소막을 씻어냄) shield.mp4(남은 불소막이 충치균을 막음)
    society.mp4(국내 학회: 과하게 헹구면 효과↓) later.mp4(가글은 다른 시간에)
"""
import math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (240, 247, 252); INK = (30, 34, 44); GRAY = (150, 158, 172); LG = (214, 222, 232)
YEL = (255, 216, 77); RED = (235, 64, 52); GRN = (46, 184, 92); BLU = (40, 140, 255); SKY = (120, 200, 255)
TOOTH = (255, 255, 255); GUM = (246, 150, 165)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def writer(name):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                             os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)


def run(name, dur, draw):
    p = writer(name)
    for i in range(int(dur * FPS)):
        img = Image.new("RGBA", (W, H), BG + (255,))
        draw(img, i / FPS)
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=INK, stroke=0, sfill=(255, 255, 255)):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=sfill)


def tooth_mask(cx, cy, s):
    """어금니 모양 마스크(왕관 + 뿌리 2개). (cx,cy)=왕관 중심, s=배율."""
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    w, h = 300 * s, 210 * s
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(90 * s), fill=255)
    for k in (-1, 1):  # 윗면 두 봉우리
        d.ellipse((cx + k * 70 * s - 85 * s, cy - h / 2 - 40 * s, cx + k * 70 * s + 85 * s, cy - h / 2 + 90 * s), fill=255)
    for k in (-1, 1):  # 뿌리
        rx = cx + k * 78 * s
        d.polygon([(rx - 62 * s, cy + 40 * s), (rx + 62 * s, cy + 40 * s), (rx + 26 * s * k * 0 + 30 * s, cy + 250 * s),
                   (rx - 30 * s, cy + 250 * s)], fill=255)
        d.ellipse((rx - 30 * s, cy + 220 * s, rx + 30 * s, cy + 280 * s), fill=255)
    d.rectangle((cx - 20 * s, cy + 40 * s, cx + 20 * s, cy + 140 * s), fill=255)
    return m.filter(ImageFilter.GaussianBlur(1.2))


_TM = {}
def tooth(img, cx, cy, s=1.0, shield=0.0, face=True, smile=1.0):
    key = (cx, cy, s)
    if key not in _TM:
        mm = tooth_mask(cx, cy, s)
        _TM[key] = (mm, mm.filter(ImageFilter.MaxFilter(int(31 * s) | 1)), mm.filter(ImageFilter.MaxFilter(int(13 * s) | 1)))
    m, edge, outline = _TM[key]
    # 잇몸
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((cx - 260 * s, cy + 150 * s, cx + 260 * s, cy + 330 * s), int(70 * s), fill=GUM)
    # 불소막(파란 테두리 빛)
    if shield > 0:
        glow = Image.new("RGBA", (W, H), BLU + (0,)); glow.putalpha(edge.point(lambda v: int(v * 0.85 * shield)))
        glow = glow.filter(ImageFilter.GaussianBlur(10 * s))
        img.alpha_composite(glow)
    # 이 본체 + 테두리
    ol = Image.new("RGBA", (W, H), INK + (0,)); ol.putalpha(outline); img.alpha_composite(ol)
    body = Image.new("RGBA", (W, H), TOOTH + (0,)); body.putalpha(m); img.alpha_composite(body)
    d = ImageDraw.Draw(img)
    if face:  # 얼굴
        for k in (-1, 1):
            d.ellipse((cx + k * 55 * s - 14 * s, cy - 20 * s, cx + k * 55 * s + 14 * s, cy + 12 * s), fill=INK)
        if smile >= 0:
            d.arc((cx - 40 * s, cy + 0 * s, cx + 40 * s, cy + 55 * s), 20, 160, fill=INK, width=int(8 * s))
        else:
            d.arc((cx - 40 * s, cy + 35 * s, cx + 40 * s, cy + 90 * s), 200, 340, fill=INK, width=int(8 * s))
    return m


def cup(d, cx, cy, s=1.0, tilt=0):
    w, h = 130 * s, 170 * s
    d.polygon([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w * 0.38, cy + h / 2), (cx - w * 0.38, cy + h / 2)],
              fill=(255, 255, 255), outline=INK, width=int(6 * s))
    d.polygon([(cx - w * 0.46, cy - h * 0.15), (cx + w * 0.46, cy - h * 0.15), (cx + w * 0.38, cy + h / 2 - 6), (cx - w * 0.38, cy + h / 2 - 6)],
              fill=SKY)


def check(d, cx, cy, r, ok=True, a=1.0):
    if a <= 0: return
    rr = r * (0.6 + 0.4 * ease(a))
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=GRN if ok else RED)
    lw = max(4, int(rr * 0.22))
    if ok:
        d.line([(cx - rr * 0.45, cy), (cx - rr * 0.1, cy + rr * 0.35), (cx + rr * 0.5, cy - rr * 0.35)], fill=(255, 255, 255), width=lw, joint="curve")
    else:
        k = rr * 0.42
        d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=(255, 255, 255), width=lw)
        d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=(255, 255, 255), width=lw)


def bubble(d, x, y, w, h, text, size, fill=(255, 255, 255), tcol=INK, tail=-1):
    d.rounded_rectangle((x, y, x + w, y + h), 36, fill=fill, outline=INK, width=6)
    tx = x + w * (0.25 if tail < 0 else 0.75)
    d.polygon([(tx - 20, y + h - 3), (tx + 20, y + h - 3), (tx + tail * 10, y + h + 40)], fill=fill, outline=INK)
    d.line([(tx - 18, y + h - 3), (tx + 18, y + h - 3)], fill=fill, width=8)
    ft = F(size); tw = d.textlength(text, font=ft)
    d.text((x + (w - tw) / 2, y + (h - size * 1.25) / 2), text, font=ft, fill=tcol)


def waves(img, t, front, alpha=200):
    """왼쪽에서 오른쪽으로 쓸고 가는 물결. front = 물 앞머리 x."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k, (col, off) in enumerate([((120, 200, 255), 0), ((80, 170, 250), 60), ((170, 225, 255), 120)]):
        ys = list(range(-20, H + 40, 20))
        pts = [(front - off + 40 * math.sin(y / 60 + t * 8 + k), y) for y in ys]
        pts += [(front - off - 380 + 40 * math.sin(y / 50 + t * 7 + k), y) for y in reversed(ys)]
        d.polygon(pts, fill=col + (alpha,))
    img.alpha_composite(lay)


# ---------------- 장면 ----------------
def s_count(img, t):
    d = ImageDraw.Draw(img)
    n = min(10, int(t / 0.22) + 1)
    # 컵 흔들림
    cup(d, 300, 420 + 8 * math.sin(t * 25), 1.6)
    # 물방울 튀기
    r = random.Random(int(t * 9))
    for _ in range(6):
        x = 300 + r.uniform(-120, 120); y = 260 + r.uniform(-60, 40)
        d.ellipse((x - 10, y - 14, x + 10, y + 14), fill=SKY)
    ctext(d, 720, 250, f"{n}번", 210, BLU if n < 10 else RED)
    ctext(d, 720, 520, "헹굼", 80, INK)


def s_rumor(img, t):
    d = ImageDraw.Draw(img)
    tooth(img, W // 2, 430, 0.75, 0, True, 1)
    d = ImageDraw.Draw(img)
    if t > 0.2: bubble(d, 70, 90, 330, 150, "6번은 헹궈!", 52)
    if t > 0.9: bubble(d, 680, 70, 330, 150, "10번 이상!", 52, tail=1)
    if t > 1.6: bubble(d, 90, 520, 300, 120, "치약 남으면?", 44)


def s_nhs(img, t):
    d = ImageDraw.Draw(img)
    ctext(d, W / 2, 50, "영국 NHS 권고", 64, INK)
    # 왼쪽: 뱉기
    lx, rx = 290, 790
    d.ellipse((lx - 150, 200, lx + 150, 500), fill=(255, 255, 255), outline=INK, width=6)
    # 입 모양 + 거품 뱉기
    d.arc((lx - 70, 300, lx + 70, 400), 200, 340, fill=INK, width=10)
    k = (t * 1.5) % 1
    for i in range(4):
        y = 380 + (k + i * 0.25) % 1 * 120
        d.ellipse((lx - 16 + i * 6, y, lx + 16 + i * 6, y + 26), fill=(255, 255, 255), outline=GRAY, width=3)
    check(d, lx, 590, 62, True, clamp((t - 0.6) / 0.3))
    ctext(d, lx, 670, "뱉기만", 52, GRN)
    cup(d, rx, 350, 1.4)
    check(d, rx, 590, 62, False, clamp((t - 1.2) / 0.3))
    ctext(d, rx, 670, "물로 헹구기", 52, RED)
    d.line([(W / 2, 170), (W / 2, 720)], fill=LG, width=4)


PARTS = [(random.Random(i).uniform(380, 700), random.Random(i * 7).uniform(-300, -20), random.Random(i * 3).uniform(0, 1)) for i in range(70)]


def s_settle(img, t):
    m = tooth(img, W // 2, 400, 0.95, shield=ease(clamp((t - 1.4) / 1.0)), face=True, smile=1)
    d = ImageDraw.Draw(img)
    for i, (x, y0, ph) in enumerate(PARTS):
        k = ease(clamp((t - ph * 0.8) / 1.2))
        y = y0 + k * (300 - y0) + 30 * math.sin(i)
        if k < 1:
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=BLU)
    ctext(d, 200, 60, "불소", 80, BLU)


def s_wash(img, t):
    sh = 1 - ease(clamp((t - 0.8) / 1.2))
    tooth(img, W // 2, 400, 0.95, shield=sh, face=True, smile=1 if sh > 0.5 else -1)
    front = -150 + t * 520
    waves(img, t, front, 170)
    d = ImageDraw.Draw(img)
    r = random.Random(5)
    for i in range(30):  # 씻겨 나가는 불소 알갱이
        if t < 0.8: break
        x = 400 + r.uniform(0, 300) + (t - 0.8) * 500 * r.uniform(0.6, 1.4)
        y = 260 + r.uniform(0, 300) + 40 * math.sin(t * 5 + i)
        if x < W: d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=BLU)


def s_shield(img, t):
    tooth(img, W // 2, 400, 0.95, shield=1.0 + 0.0 * t, face=True, smile=1)
    d = ImageDraw.Draw(img)
    r = random.Random(11)
    for i in range(7):  # 충치균이 날아와 튕겨남
        st = i * 0.35
        k = clamp((t - st) / 0.9)
        if k <= 0: continue
        side = -1 if i % 2 else 1
        sx, sy = W / 2 + side * 560, 120 + r.uniform(0, 420)
        tx, ty = W / 2 + side * 210, 300 + r.uniform(0, 160)
        if k < 0.6:
            x = sx + (tx - sx) * k / 0.6; y = sy + (ty - sy) * k / 0.6
        else:
            kk = (k - 0.6) / 0.4; x = tx + side * 300 * kk; y = ty - 160 * kk
        d.ellipse((x - 30, y - 30, x + 30, y + 30), fill=(130, 200, 90), outline=INK, width=4)
        for a in range(6):
            ang = a * math.pi / 3
            d.line([(x + 30 * math.cos(ang), y + 30 * math.sin(ang)), (x + 44 * math.cos(ang), y + 44 * math.sin(ang))], fill=INK, width=4)
        d.ellipse((x - 12, y - 8, x - 2, y + 2), fill=INK); d.ellipse((x + 2, y - 8, x + 12, y + 2), fill=INK)
    ctext(d, W / 2, 40, "불소 코팅", 70, BLU)


def s_society(img, t):
    d = ImageDraw.Draw(img)
    ctext(d, W / 2, 60, "국내 예방치과·구강보건학회", 54, INK)
    # 물 컵 개수 늘수록 효과 막대 줄어듦
    n = min(8, int(t / 0.3) + 1)
    for i in range(n):
        cup(d, 140 + i * 80, 260, 0.5)
    lvl = max(0.15, 1 - n * 0.11)
    bx, by, bw, bh = 260, 380, 560, 90
    d.rounded_rectangle((bx, by, bx + bw, by + bh), 30, fill=LG)
    d.rounded_rectangle((bx, by, bx + max(60, bw * lvl), by + bh), 30, fill=BLU if lvl > 0.4 else RED)
    ctext(d, W / 2, 500, "충치 예방 효과", 52, INK)
    if t > 2.2: ctext(d, W / 2, 590, "↓", 90, RED)


def s_later(img, t):
    d = ImageDraw.Draw(img)
    # 시계 + 가글 병
    cx, cy = 330, 380
    d.ellipse((cx - 170, cy - 170, cx + 170, cy + 170), fill=(255, 255, 255), outline=INK, width=10)
    ang = -math.pi / 2 + t * 2.2
    d.line([(cx, cy), (cx + 120 * math.cos(ang), cy + 120 * math.sin(ang))], fill=INK, width=10)
    d.line([(cx, cy), (cx + 80 * math.cos(ang / 12 - 1), cy + 80 * math.sin(ang / 12 - 1))], fill=INK, width=14)
    d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=INK)
    bx = 760
    d.rounded_rectangle((bx - 90, 260, bx + 90, 560), 40, fill=(90, 200, 190), outline=INK, width=6)
    d.rounded_rectangle((bx - 50, 200, bx + 50, 270), 14, fill=INK)
    ctext(d, bx, 380, "가글", 54, (255, 255, 255))
    ctext(d, W / 2, 640, "양치 직후 X → 다른 시간 O", 50, INK)


os.makedirs(OUT, exist_ok=True)
run("count", 3.2, s_count)
run("rumor", 3.4, s_rumor)
run("nhs", 3.6, s_nhs)
run("settle", 3.4, s_settle)
run("wash", 3.4, s_wash)
run("shield", 3.6, s_shield)
run("society", 3.6, s_society)
run("later", 3.4, s_later)
print("ok", OUT)
