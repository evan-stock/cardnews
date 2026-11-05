#!/usr/bin/env python3
"""금보다 비싼 나무의 상처 — 침향(아퀼라리아) 모션그래픽(카드 영상 칸 1080x780) — 2026.11.05 오늘의쓸모.
  python3 scripts/story_shorts/anim_agarwood.py <출력폴더>
  → wound.mp4 (줄기 단면: ① 상처 → ② 균이 들어옴 → ③ 나무가 검은 방어 수지로 상처를 막음 = 침향)
    rare.mp4  (자연: 10그루 중 몇 그루만 침향 / 농장: 일부러 상처 → 줄줄이 침향)
    price.mp4 (하얀 나무 vs 침향 1.4kg 조각 — 20만 링깃(약 6천만 원) 카운터, 영상 속 소개 값)
근거: Wikipedia 'Agarwood'(상처·곰팡이 감염에 대한 반응으로 수지가 생김, 건강한 나무 속은 옅은 색),
      López-Sampson & Page 2018 / PMC9181942 리뷰(인공 유도: 구멍·못·화학·불 등 상처 내기),
      @vanessa_cwy TikTok(70년 된 캄보디아산 1.4kg 조각 20만 링깃이라고 소개).
"""
import math, subprocess, sys, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (240, 70, 50); BG = (24, 30, 36)
WOOD = (236, 218, 180); RING = (214, 192, 150); BARK = (112, 92, 70); RESIN = (58, 30, 14); GERM = (120, 170, 90)
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


def ltext(d, x, y, s, size, fill=WHITE, stroke=5):
    d.text((x, y), s, font=F(size), fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


# ---------- 1. 상처 → 균 → 수지 ----------
CX, CY, R = 610, 420, 300
rnd = random.Random(7)
GERMS = [(rnd.uniform(0, 1), rnd.uniform(-0.5, 0.5), rnd.uniform(0, 1)) for _ in range(26)]
BLOB = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.5, 1.0)) for _ in range(40)]


def wound(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.ellipse([CX - R - 26, CY - R - 26, CX + R + 26, CY + R + 26], fill=BARK)
    d.ellipse([CX - R, CY - R, CX + R, CY + R], fill=WOOD)
    for k in range(1, 9):
        r = R * k / 9
        d.ellipse([CX - r, CY - r, CX + r, CY + r], outline=RING, width=4)
    # 상처(왼쪽 바깥에서 안으로 파고드는 칼집)
    cut = ease(t / 0.6)
    x0 = CX - R - 26; x1 = x0 + 190 * cut
    d.polygon([(x0, CY - 16), (x1, CY - 4), (x1, CY + 4), (x0, CY + 16)], fill=(30, 20, 14))
    if t < 0.8:  # 불꽃
        fl = 1 - clamp((t - 0.5) / 0.3)
        d.polygon([(x0 - 120, CY - 10), (x1 - 10, CY), (x0 - 120, CY + 10)], fill=(255, int(120 + 60 * fl), 40))
    # 수지(검은 갈색)가 칼집 끝에서 번짐
    rs = ease((t - 1.2) / 1.6)
    if rs > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        bx, by = x0 + 170, CY
        for (u, v, s) in BLOB:
            rr = 26 + 40 * s * rs
            px = bx + u * 150 * rs + 40 * rs; py = by + v * 110 * rs
            ld.ellipse([px - rr, py - rr, px + rr, py + rr], fill=RESIN + (235,))
        lay = lay.filter(ImageFilter.GaussianBlur(6))
        mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).ellipse([CX - R, CY - R, CX + R, CY + R], fill=255)
        a = lay.split()[3]; a = Image.composite(a, Image.new("L", (W, H), 0), mask); lay.putalpha(a)
        img.paste(lay, (0, 0), lay); d = ImageDraw.Draw(img)
        d.polygon([(x0, CY - 16), (x1, CY - 4), (x1, CY + 4), (x0, CY + 16)], fill=(30, 20, 14))
    # 균(초록 점)이 칼집으로 들어옴
    gs = clamp((t - 0.6) / 0.9)
    if gs > 0:
        for (a_, b_, ph) in GERMS:
            k = clamp(gs * 1.3 - ph * 0.3)
            if k <= 0:
                continue
            gx = x0 - 60 + (230 + 60 * a_) * k; gy = CY + b_ * 70 * k + math.sin(t * 6 + ph * 9) * 4
            alpha = 1 - clamp((t - 2.4) / 0.6)
            if alpha <= 0:
                continue
            c = tuple(int(BG[i] + (GERM[i] - BG[i]) * alpha) for i in range(3))
            d.ellipse([gx - 9, gy - 9, gx + 9, gy + 9], fill=c)
    # 단계 글자
    steps = [("① 상처", 0.0), ("② 균이 들어옴", 0.7), ("③ 검은 수지로 막음", 1.4)]
    for i, (s, st) in enumerate(steps):
        if t >= st:
            ltext(d, 34, 40 + i * 70, s, 46, YEL if i == 2 else WHITE)
    if rs > 0.6:
        ctext(d, CX + 40, CY + R + 6 - 60, "= 침향", 60, YEL)
    return img


# ---------- 2. 자연 vs 농장 ----------
def tree(d, x, y, dark, cuts=0.0, s=1.0):
    d.ellipse([x - 44 * s, y - 150 * s, x + 44 * s, y - 70 * s], fill=(70, 130, 70))
    d.rectangle([x - 14 * s, y - 80 * s, x + 14 * s, y], fill=(170, 150, 120))
    if cuts > 0:
        for k in range(3):
            yy = y - 66 * s + k * 20 * s
            d.line([(x - 14 * s, yy), (x - 14 * s + 22 * s * cuts, yy)], fill=(30, 20, 14), width=max(2, int(4 * s)))
    if dark > 0:
        d.rectangle([x - 8 * s, y - 70 * s, x + 8 * s, y - 70 * s + 64 * s * dark], fill=RESIN)


def rare(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.line([(W / 2, 40), (W / 2, H - 40)], fill=(80, 90, 100), width=4)
    ctext(d, W / 4, 34, "자연", 54)
    ctext(d, 3 * W / 4, 34, "농장", 54, YEL)
    lucky = {3}
    for i in range(10):
        cx = 70 + (i % 5) * 100; cy = 300 + (i // 5) * 230
        dk = ease((t - 0.9) / 0.8) if i in lucky else 0
        tree(d, cx, cy, dk)
        if i in lucky and dk > 0.5:
            d.ellipse([cx - 62, cy - 170, cx + 62, cy + 20], outline=YEL, width=6)
        cx2 = W / 2 + 70 + (i % 5) * 100
        ct = ease((t - 0.3 - 0.06 * i) / 0.4)
        dk2 = ease((t - 1.3 - 0.05 * i) / 0.7)
        tree(d, cx2, cy, dk2, ct)
    if t > 1.2:
        ctext(d, W / 4, 660, "몇 그루뿐", 52)
    if t > 1.9:
        ctext(d, 3 * W / 4, 660, "일부러 상처 → 줄줄이", 46, YEL)
    return img


# ---------- 3. 값 ----------
CHUNK = [(0, 0), (60, -30), (140, -10), (210, -50), (300, -20), (330, 60), (300, 150), (220, 190), (120, 170), (30, 130)]


def chunk(d, ox, oy, col, streak, s=1.0):
    pts = [(ox + x * s, oy + y * s) for x, y in CHUNK]
    d.polygon(pts, fill=col)
    rr = random.Random(3)
    for k in range(14):
        x = ox + rr.uniform(30, 290) * s; y = oy + rr.uniform(-10, 150) * s
        d.line([(x, y), (x + rr.uniform(-20, 20) * s, y + rr.uniform(20, 50) * s)], fill=streak, width=int(5 * s))


def price(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    a = ease(t / 0.5)
    chunk(d, 90, 260, WOOD, RING, 1.0)
    ctext(d, 255, 500, "그냥 나무", 48)
    ctext(d, 255, 566, "향 거의 없음", 40, (190, 190, 195))
    b = ease((t - 0.4) / 0.5)
    if b > 0:
        chunk(d, 600, 260, RESIN, (120, 70, 30), 1.0)
        ctext(d, 765, 500, "침향 1.4kg", 48, YEL)
        k = ease((t - 0.8) / 1.4)
        ctext(d, 765, 566, f"{int(200000 * k):,} 링깃", 44, WHITE)
        if t > 2.1:
            ctext(d, 765, 630, "(약 6천만 원)", 44, YEL)
    ctext(d, W / 2, 712, "※ 영상 속 판매자 소개 값", 28, (170, 170, 178), 3)
    return img


if __name__ == "__main__":
    run("wound", 3.2, wound)
    run("rare", 3.0, rare)
    run("price", 3.0, price)
    print("ok", OUT)
