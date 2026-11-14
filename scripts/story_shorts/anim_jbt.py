#!/usr/bin/env python3
"""'전화 한 통에 4시간 걸린 뇌과학자 — 질 볼트 테일러' 모션그래픽(영상 칸 1080x780) — 2026.11.15 오늘의쓸모.
  python3 scripts/story_shorts/anim_jbt.py <출력폴더>
  → card.mp4   명함 위 숫자가 꼬불꼬불한 '낙서'로 녹아내림
    match.mp4  명함의 낙서 모양을 키패드 모양과 하나씩 맞춰 누르고, 누른 칸은 가림
    voice.mp4  수화기 너머 동료 말소리 파형이 '멍! 멍!'으로 바뀜
    speak.mp4  "질이야, 뇌졸중이 왔어" → "으으으으…"
    brain.mp4  왼쪽 뇌 혈관(뇌동정맥 기형)이 터지며 피가 번짐 · 1996.12.10 · 37세
    off.mp4    왼쪽 뇌의 말·숫자·읽기가 하나씩 꺼짐
    golf.mp4   골프공만 한 핏덩어리 → 수술 → 1996 → 2004 '8년'
    call119.mp4 키패드 1·1·9 불이 켜짐
근거: Oprah.com(4시간·명함 낙서 모양 맞추기), O 매거진(누른 칸 가리기·"Jhhhiiii"), Success(골든리트리버 같은 목소리),
      Shortform(1996.12.10, AVM, 좌반구), Hinduism Today(37세), DailyGood(골프공 크기 혈전·언어 중추 압박),
      Contemplative Inquiry(완전 회복 8년). 전화번호는 지어낸 것(실제 번호 아님).
"""
import math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s, index=1)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (230, 50, 45); DRED = (150, 20, 25)
GREY = (140, 146, 160); DGREY = (70, 74, 86); BG1 = (24, 30, 48); BG2 = (8, 10, 20)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def run(name, dur, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(draw(i / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def grad(top, bot):
    a = np.linspace(0, 1, H)[:, None, None]
    arr = np.array(top)[None, None, :] * (1 - a) + np.array(bot)[None, None, :] * a
    return Image.fromarray(np.repeat(arr, W, axis=1).astype(np.uint8))


BG = grad(BG1, BG2)


def ctext(d, cx, y, s, size, fill=WHITE, stroke=6):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


DIG = "617-555-0148"   # 지어낸 번호


def glyph_img(ch, size, melt, seed):
    """숫자 한 글자를 그린 뒤 melt(0~1)만큼 물결처럼 비틀어 '낙서'로 만든다."""
    im = Image.new("L", (int(size * 0.9), int(size * 1.4)), 0)
    d = ImageDraw.Draw(im)
    d.text((im.width * 0.08, -size * 0.05), ch, font=F(size), fill=255)
    if melt <= 0:
        return im
    a = np.array(im)
    rng = np.random.default_rng(seed)
    ph1, ph2 = rng.uniform(0, 6.28, 2)
    out = np.zeros_like(a)
    hh, ww = a.shape
    for y in range(hh):
        k = size / 100
        sh = int(melt * k * (14 * math.sin(y / (9 * k) + ph1) + 8 * math.sin(y / (4 * k) + ph2)))
        out[y] = np.roll(a[y], sh)
    out2 = np.zeros_like(out)
    for x in range(ww):
        sh = int(melt * size / 100 * 10 * math.sin(x / (7 * size / 100) + ph2))
        out2[:, x] = np.roll(out[:, x], sh)
    return Image.fromarray(out2).filter(ImageFilter.GaussianBlur(melt * 1.2))


GL_CACHE = {}


def glyph(ch, size, melt, seed):
    k = (ch, size, round(melt, 2), seed)
    if k not in GL_CACHE:
        GL_CACHE[k] = glyph_img(ch, size, melt, seed)
    return GL_CACHE[k]


def draw_card(im, x0, y0, w, h, melt, size=72):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x0 + 10, y0 + 12, x0 + w + 10, y0 + h + 12], 22, fill=(0, 0, 0))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], 22, fill=(246, 242, 232))
    # 연구소 빨간 뇌 로고(동료 명함 — 로고만 알아봤다는 일화)
    cx, cy = x0 + 90, y0 + 90
    d.ellipse([cx - 52, cy - 40, cx + 52, cy + 40], fill=(200, 40, 50))
    for k in range(5):
        d.arc([cx - 46 + k * 14, cy - 30, cx - 18 + k * 14, cy + 6], 180, 360, fill=(250, 200, 200), width=4)
    d.line([(cx, cy - 38), (cx, cy + 38)], fill=(250, 200, 200), width=4)
    # 이름 줄(흐린 막대)
    for k, ln in enumerate((300, 220)):
        d.rounded_rectangle([x0 + 170, y0 + 50 + k * 44, x0 + 170 + ln, y0 + 74 + k * 44], 8, fill=(200, 196, 186))
    # 전화번호
    x = x0 + 60
    for i, ch in enumerate(DIG):
        m = clamp(melt * 1.25 - i * 0.03)
        g = glyph(ch, size, m, ord(ch))
        col = Image.new("RGB", g.size, (40, 40, 48))
        im.paste(col, (int(x), int(y0 + h - 150)), g)
        x += size * 0.62 if ch != "-" else size * 0.45
    return im


# ---------- 1. card: 숫자가 낙서로 ----------
def card(t):
    im = BG.copy()
    z = 1.0 + 0.05 * t
    melt = ease((t - 0.35) / 1.6)
    draw_card(im, 140, 160, 800, 420, melt)
    d = ImageDraw.Draw(im)
    if z != 1.0:
        im = im.resize((int(W * z), int(H * z)), Image.LANCZOS).crop((int(W * (z - 1) / 2), int(H * (z - 1) / 2), int(W * (z - 1) / 2) + W, int(H * (z - 1) / 2) + H))
    return im


# ---------- 2. match: 낙서 모양을 키패드와 맞추기 ----------
KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"]


def keypad(im, x0, y0, s, lit=None, covered=(), press=None):
    d = ImageDraw.Draw(im)
    for k, ch in enumerate(KEYS):
        r, c = divmod(k, 3)
        x = x0 + c * 120 * s; y = y0 + r * 110 * s
        box = [x, y, x + 104 * s, y + 94 * s]
        col = (70, 76, 92)
        if ch in covered:
            col = (40, 42, 50)
        if lit == ch:
            col = (255, 196, 40)
        dy = 6 * s if press == ch else 0
        d.rounded_rectangle([box[0], box[1] + dy, box[2], box[3] + dy], 14 * s, fill=col)
        if ch in covered and lit != ch:
            d.rounded_rectangle([box[0] + 8 * s, box[1] + 8 * s + dy, box[2] - 8 * s, box[3] - 8 * s + dy], 10 * s, fill=(28, 28, 34))
            continue
        g = glyph(ch, int(64 * s), 0.85, ord(ch))
        colimg = Image.new("RGB", g.size, (20, 20, 24) if lit == ch else (225, 228, 236))
        im.paste(colimg, (int(x + 52 * s - g.width / 2), int(y + 4 * s + dy)), g)


SEQ = ["6", "1", "7", "5"]


def match(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    # 왼쪽: 명함의 낙서 한 글자씩 크게
    step = 0.62
    k = min(len(SEQ) - 1, int(t / step))
    u = (t - k * step) / step
    ch = SEQ[k]
    d.rounded_rectangle([60, 150, 400, 560], 26, fill=(246, 242, 232))
    g = glyph(ch, 230, 0.85, ord(ch))
    im.paste(Image.new("RGB", g.size, (40, 40, 48)), (int(230 - g.width / 2), 190), g)
    ctext(d, 230, 590, "명함 속 모양", 40, fill=GREY, stroke=4)
    # 화살표
    a = ease(u / 0.4)
    d.line([(420, 355), (420 + 90 * a, 355)], fill=YEL, width=10)
    if a > 0.8:
        d.polygon([(510, 335), (540, 355), (510, 375)], fill=YEL)
    # 오른쪽: 키패드
    covered = SEQ[:k]
    lit = ch if u > 0.35 else None
    press = ch if 0.55 < u < 0.8 else None
    keypad(im, 580, 120, 1.15, lit=lit, covered=covered, press=press)
    return im


# ---------- 3. voice: 말소리 파형 → 멍멍 ----------
def handset(d, cx, cy, s, col):
    d.rounded_rectangle([cx - 40 * s, cy - 150 * s, cx + 40 * s, cy + 150 * s], 30 * s, fill=col)
    d.ellipse([cx - 70 * s, cy - 190 * s, cx + 70 * s, cy - 110 * s], fill=col)
    d.ellipse([cx - 70 * s, cy + 110 * s, cx + 70 * s, cy + 190 * s], fill=col)


def voice(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    handset(d, 160, 390, 1.0, (210, 214, 224))
    morph = ease((t - 0.9) / 0.7)
    for i in range(46):
        x = 300 + i * 15
        f1 = abs(math.sin(i * 0.55 + t * 9)) * 0.6 + 0.3 * abs(math.sin(i * 1.7 + t * 5))
        f2 = (1.0 if (i // 7) % 2 == 0 else 0.15) * (0.7 + 0.3 * abs(math.sin(t * 20 + i)))
        hgt = 200 * ((1 - morph) * f1 + morph * f2)
        col = tuple(int(a + (b - a) * morph) for a, b in zip((120, 200, 255), (255, 120, 60)))
        d.rounded_rectangle([x, 390 - hgt / 2, x + 9, 390 + hgt / 2], 4, fill=col)
    if t < 1.0:
        ctext(d, 680, 560, "동료: \"질? 무슨 일이야?\"", 46, fill=(150, 210, 255))
    if morph > 0.3:
        for k, (x, y) in enumerate([(470, 150), (760, 120), (960, 200)]):
            if t > 1.0 + k * 0.35:
                sc = 1 + 0.2 * math.sin(t * 12 + k)
                ctext(d, x, y, "멍!", int(70 * sc), fill=(255, 150, 70), stroke=7)
    return im


# ---------- 4. speak: 내 말도 ----------
def speak(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([120, 170, 960, 470], 50, fill=(246, 246, 250))
    d.polygon([(240, 460), (300, 470), (200, 560)], fill=(246, 246, 250))
    full = "나야, 질이야. 도와줘"
    junk = "으으으… 이이이…"
    if t < 1.1:
        n = int(len(full) * clamp(t / 0.9))
        s = full[:n]; col = (30, 30, 40)
    else:
        u = clamp((t - 1.1) / 0.6)
        n = int(len(full) * (1 - u))
        s = junk[:max(1, int(len(junk) * u))] + full[len(full) - n:] if u < 1 else junk
        col = (200, 40, 50)
        jx = random.Random(int(t * 30)).uniform(-6, 6)
        d = ImageDraw.Draw(im)
        ft = F(64); w = d.textlength(s, font=ft)
        d.text((540 - w / 2 + jx, 270), s, font=ft, fill=col)
        return im
    ft = F(64); w = d.textlength(s, font=ft)
    d.text((540 - w / 2, 270), s, font=ft, fill=col)
    return im


# ---------- 5. brain: 왼쪽 뇌 혈관이 터짐 ----------
def brain_shape():
    """위에서 본 뇌(왼쪽·오른쪽 반구) 마스크와 주름선."""
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    d.ellipse([250, 90, 535, 690], fill=255)    # 화면 왼쪽 = 왼쪽 뇌
    d.ellipse([545, 90, 830, 690], fill=255)
    return m


BM = brain_shape()


def folds(d, col, w=5):
    rng = random.Random(7)
    for side in (0, 1):
        x0 = 270 if side == 0 else 565
        for k in range(16):
            y = 120 + k * 36
            pts = []
            for i in range(12):
                x = x0 + i * 21
                pts.append((x, y + 14 * math.sin(i * 1.3 + k * 0.9 + side * 2) + rng.uniform(-3, 3)))
            d.line(pts, fill=col, width=w)


BRAIN = Image.new("RGB", (W, H), (0, 0, 0))
_bd = ImageDraw.Draw(BRAIN)
_bd.rectangle([0, 0, W, H], fill=(232, 168, 172))
folds(_bd, (190, 110, 120), 6)


def brain_base(dim_left=0.0):
    im = BG.copy()
    b = BRAIN.copy()
    if dim_left > 0:
        arr = np.array(b).astype(float)
        arr[:, :540] = arr[:, :540] * (1 - 0.65 * dim_left) + np.array([40, 44, 56]) * 0.65 * dim_left
        b = Image.fromarray(arr.astype(np.uint8))
    im.paste(b, (0, 0), BM)
    return im


def brain(t):
    im = brain_base(); d = ImageDraw.Draw(im)
    ctext(d, 392, 20, "왼쪽 뇌", 40, fill=WHITE, stroke=5)
    ctext(d, 688, 20, "오른쪽 뇌", 40, fill=WHITE, stroke=5)
    # 혈관 줄기
    vx, vy = 420, 380
    pulse = 1 + 0.25 * max(0, math.sin(t * 9)) * (1 - ease((t - 1.2) / 0.3))
    d.line([(300, 640), (360, 520), (400, 430), (vx, vy)], fill=(160, 20, 30), width=12)
    if t < 1.2:
        r = 26 * pulse * (0.6 + 0.4 * clamp(t / 1.0))
        d.ellipse([vx - r, vy - r, vx + r, vy + r], fill=(180, 20, 30))
        ctext(d, 392, 700, "엉킨 혈관 덩어리", 36, fill=GREY, stroke=4)
    else:
        u = ease((t - 1.2) / 1.2)
        blob = Image.new("L", (W, H), 0); bd = ImageDraw.Draw(blob)
        rng = random.Random(3)
        for k in range(14):
            ang = k / 14 * 2 * math.pi
            rr = (40 + 130 * u) * rng.uniform(0.6, 1.0)
            cx = vx + math.cos(ang) * rr * 0.6; cy = vy + math.sin(ang) * rr * 0.8
            q = 40 + 70 * u
            bd.ellipse([cx - q, cy - q, cx + q, cy + q], fill=255)
        blob = blob.filter(ImageFilter.GaussianBlur(10))
        lm = np.array(BM) > 0; lm[:, 540:] = False
        mask = Image.fromarray((np.array(blob) * lm).astype(np.uint8))
        im.paste(Image.new("RGB", (W, H), (150, 10, 20)), (0, 0), mask)
        if t > 1.2 and t < 1.45:
            fl = Image.new("RGB", (W, H), (255, 255, 255))
            im = Image.blend(im, fl, 0.35 * (1 - (t - 1.2) / 0.25))
        d = ImageDraw.Draw(im)
        ctext(d, W / 2, 700, "1996년 12월 10일 · 37살", 46, fill=YEL)
    return im


# ---------- 6. off: 왼쪽 뇌 기능이 꺼짐 ----------
LBL = [("말", 200), ("숫자", 330), ("읽기", 460), ("나는 누구?", 590)]


def off(t):
    dim = ease((t - 0.2) / 2.0)
    im = brain_base(dim); d = ImageDraw.Draw(im)
    for k, (s, y) in enumerate(LBL):
        on = t < 0.4 + k * 0.45
        col = YEL if on else (175, 178, 190)
        ctext(d, 392, y, s, 54, fill=col, stroke=6)
        if not on:
            w = d.textlength(s, font=F(54))
            d.line([(392 - w / 2 - 10, y + 40), (392 + w / 2 + 10, y + 40)], fill=RED, width=8)
    glow = 0.5 + 0.5 * math.sin(t * 4)
    ctext(d, 688, 380, "오른쪽 뇌는", 44, fill=(150, 220, 255), stroke=5)
    ctext(d, 688, 440, "아직 켜져 있다", 44, fill=(150, 220, 255), stroke=5)
    return im


# ---------- 7. golf: 골프공 크기 핏덩어리 · 8년 ----------
def golf(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    a = ease(t / 0.6)
    gx, gy, r = 320, 330, 140 * a
    d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=(245, 245, 245))
    rng = random.Random(1)
    for k in range(40):
        ang = rng.uniform(0, 6.28); rr = rng.uniform(0, 0.85) * r
        x = gx + math.cos(ang) * rr; y = gy + math.sin(ang) * rr
        d.ellipse([x - 7 * a, y - 7 * a, x + 7 * a, y + 7 * a], fill=(215, 215, 220))
    ctext(d, gx, 500, "골프공", 44, fill=WHITE, stroke=5)
    b = ease((t - 0.4) / 0.6)
    if b > 0:
        cx, cy = 760, 330
        pts = []
        for k in range(24):
            ang = k / 24 * 6.283
            rr = 140 * b * (0.88 + 0.12 * math.sin(k * 2.3))
            pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
        d.polygon(pts, fill=(130, 12, 22))
        ctext(d, cx, 500, "핏덩어리", 44, fill=(255, 120, 120), stroke=5)
        ctext(d, W / 2, 300, "=", 90, fill=YEL)
    # 1996 → 2004 카운터
    c = clamp((t - 1.3) / 1.2)
    if c > 0:
        yr = 1996 + int(round(8 * ease(c)))
        ctext(d, W / 2, 590, f"{yr}년", 84, fill=YEL if c >= 1 else WHITE, stroke=7)
        if c >= 1:
            ctext(d, W / 2, 690, "다시 일어서기까지 8년", 40, fill=WHITE, stroke=5)
    return im


# ---------- 8. call119 ----------
def call119(t):
    im = BG.copy()
    lit = None
    if 0.3 < t < 0.8:
        lit = "1"
    elif 0.9 < t < 1.4:
        lit = "1"
    elif 1.5 < t < 3.0:
        lit = "9"
    d = ImageDraw.Draw(im)
    for k, ch in enumerate(KEYS):
        r, c = divmod(k, 3)
        x = 330 + c * 150; y = 60 + r * 130
        on = ch == lit
        col = (255, 196, 40) if on else (70, 76, 92)
        d.rounded_rectangle([x, y, x + 130, y + 112], 18, fill=col)
        ft = F(70); w = d.textlength(ch, font=ft)
        d.text((x + 65 - w / 2, y + 4), ch, font=ft, fill=(20, 20, 24) if on else (225, 228, 236))
    n = (1 if t > 0.3 else 0) + (1 if t > 0.9 else 0) + (1 if t > 1.5 else 0)
    ctext(d, W / 2, 610, "1 1 9"[: max(0, n * 2 - 1)], 90, fill=YEL, stroke=8)
    return im


SC = {"card": (2.8, card), "match": (2.6, match), "voice": (2.6, voice), "speak": (2.4, speak),
      "brain": (3.0, brain), "off": (2.6, off), "golf": (2.9, golf), "call119": (3.0, call119)}
only = sys.argv[2:] or list(SC)
for k in only:
    dur, fn = SC[k]
    run(k, dur, fn)
    print("ok", k)
