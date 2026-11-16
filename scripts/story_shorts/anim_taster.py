#!/usr/bin/env python3
"""아이스크림 맛 감별사 존 해리슨(드라이어스/에디스, 1980~2010) 모션그래픽(카드 영상 칸 1080x780) — 2026.11.09 오늘의쓸모.
  python3 scripts/story_shorts/anim_taster.py <출력폴더>
  → policy.mp4  (혀 보험증서: 금액이 0 → 100만 달러로 올라감)
    taste.mp4   (숟가락을 뒤집어 따뜻한 윗부분을 혀에 → 굴리고 → 삼키지 않고 뱉음, 하루 약 60통)
    spoon.mp4   (나무·플라스틱 숟가락 = 뒷맛 ✗ / 18K 금 숟가락 = 뒷맛 없음)
    rules.mp4   (평일 금지: 양파·마늘·매운 음식·술·담배, 커피 대신 허브차)
근거: Deseret News 1992.06.23(100만 달러 보험, 삼키지 않음, 숟가락을 뒤집어 따뜻한 부분을 혀에, 굴리고 뱉음, 50~60통,
      매운 음식·술·담배 안 함), Seattle Times 2006.06.21(18K 금 숟가락 = 뒷맛 방지, 55갤런 통에 뱉음, 하루 약 60통,
      평일 양파·마늘·고추 안 먹고 커피 대신 허브차), The Hustle 2021.08.04, 위키백과 'John Harrison (ice cream taster)'.
"""
import subprocess, sys, os, math
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (215, 25, 35); DARK = (30, 34, 44); GREY = (150, 160, 178)
GOLD = (240, 190, 60); CREAM = (250, 235, 200); PINK = (235, 120, 140)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def grad(top, bot):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line((0, y, W, y), fill=tuple(int(a + (b - a) * k) for a, b in zip(top, bot)))
    return img


def run(name, dur, bg, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = bg.copy()
        draw(img, i / FPS)
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=5):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def tongue(d, cx, cy, s=1.0, wob=0.0):
    """분홍 혀(입 모양 안)"""
    d.ellipse((cx - 170 * s, cy - 70 * s, cx + 170 * s, cy + 70 * s), fill=(90, 30, 40))
    d.ellipse((cx - 120 * s, cy - 40 * s + wob, cx + 120 * s, cy + 90 * s + wob), fill=PINK)
    d.line((cx, cy - 20 * s + wob, cx, cy + 50 * s + wob), fill=(200, 90, 110), width=int(5 * s))
    for k in range(14):  # 미뢰 점
        a = k * 2.4
        x = cx + math.cos(a) * 70 * s * ((k % 4) / 4 + 0.3)
        y = cy + 25 * s + math.sin(a) * 30 * s * ((k % 3) / 3 + 0.4) + wob
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(250, 170, 185))


def spoon(d, x, y, ang, col, s=1.0):
    """숟가락: (x,y)=머리 중심, ang=손잡이 방향(라디안)"""
    hx, hy = x + math.cos(ang) * 230 * s, y + math.sin(ang) * 230 * s
    d.line((x, y, hx, hy), fill=col, width=int(20 * s))
    d.ellipse((x - 46 * s, y - 34 * s, x + 46 * s, y + 34 * s), fill=col, outline=(60, 60, 60), width=3)


# ① 혀 보험증서
def policy(img, t):
    d = ImageDraw.Draw(img)
    k = ease(t / 0.5)
    y0 = 60 + (1 - k) * 500
    d.rounded_rectangle((170, y0, 910, y0 + 640), 26, fill=(252, 248, 236), outline=GOLD, width=10)
    ctext(d, 540, y0 + 40, "보 험 증 서", 50, fill=DARK, stroke=0)
    d.line((240, y0 + 120, 840, y0 + 120), fill=GOLD, width=4)
    ctext(d, 540, y0 + 146, "보험 대상", 32, fill=GREY, stroke=0)
    tongue(d, 540, y0 + 255, 0.7)
    ctext(d, 540, y0 + 350, "존 해리슨의 '혀'(미뢰)", 38, fill=DARK, stroke=0)
    ctext(d, 540, y0 + 420, "보험금", 32, fill=GREY, stroke=0)
    v = int(1_000_000 * ease((t - 0.5) / 1.3))
    ctext(d, 540, y0 + 462, f"${v:,}", 84, fill=RED, stroke=0)
    if t > 2.0:
        a = clamp((t - 2.0) / 0.2)
        d.ellipse((730, y0 + 150, 880, y0 + 240), outline=(200, 30, 30), width=int(8 * a) or 1)
        ctext(d, 805, y0 + 172, "1992", 34, fill=(200, 30, 30), stroke=0)


# ② 맛보는 법: 숟가락 뒤집기 → 굴리기 → 뱉기
def taste(img, t):
    d = ImageDraw.Draw(img)
    tongue(d, 540, 520, 1.25, wob=math.sin(t * 9) * 6 if 1.2 < t < 2.0 else 0)
    # 숟가락이 뒤집히며 내려옴(아이스크림이 아래로)
    k = ease(t / 0.9)
    y = 160 + 300 * k
    spoon(d, 540, y, -0.5, (225, 228, 235), 1.6)
    if t < 1.3:
        d.ellipse((470, y + 20, 610, y + 95), fill=CREAM)
    lbl = "숟가락을 '뒤집어' 따뜻한 윗부분을 혀에" if t < 1.2 else ("혀 전체에 굴리고" if t < 2.0 else "삼키지 않고 '퉤'")
    ctext(d, 540, 40, lbl, 44, fill=YEL)
    if t >= 2.0:  # 뱉기 → 통
        kk = ease((t - 2.0) / 0.6)
        bx = 540 + 330 * kk; by = 520 + 80 * kk - 160 * math.sin(math.pi * kk)
        d.ellipse((bx - 50, by - 34, bx + 50, by + 34), fill=CREAM, outline=(200,170,120), width=3)
        d.rectangle((830, 560, 990, 740), fill=(80, 90, 110), outline=WHITE, width=3)
        ctext(d, 910, 620, "통", 44)
    ctext(d, 160, 680, "하루 약 60통", 40, fill=WHITE)


# ③ 숟가락 재질
def spoon_cmp(img, t):
    d = ImageDraw.Draw(img)
    items = [(200, (170, 120, 70), "나무", False), (540, (235, 235, 240), "플라스틱", False), (880, GOLD, "18K 금", True)]
    for i, (cx, col, name, ok) in enumerate(items):
        k = ease((t - i * 0.45) / 0.45)
        if k <= 0:
            continue
        yy = 260 + (1 - k) * 200
        spoon(d, cx, yy - 40, math.pi / 2, col, 1.4)
        if ok and t > 1.3:  # 반짝
            r = 30 + 12 * math.sin(t * 12)
            d.line((cx + 50, yy - 60 - r, cx + 50, yy - 60 + r), fill=WHITE, width=5)
            d.line((cx + 50 - r, yy - 60, cx + 50 + r, yy - 60), fill=WHITE, width=5)
        ctext(d, cx, 520, name, 46, fill=GOLD if ok else WHITE)
        if k >= 1:
            if ok:
                ctext(d, cx, 600, "뒷맛 없음", 40, fill=YEL)
            else:
                ctext(d, cx, 600, "숟가락 맛 섞임", 40, fill=(255, 120, 120))
    ctext(d, 540, 40, "맛에 섞이면 안 되는 것: 숟가락 맛", 42, fill=WHITE)


# ④ 평일 금지 목록
def rules(img, t):
    d = ImageDraw.Draw(img)
    ctext(d, 540, 30, "평일엔 금지", 56, fill=YEL)
    xs = ["양파", "마늘", "매운 음식", "술", "담배", "커피"]
    for i, s in enumerate(xs):
        k = ease((t - 0.15 - i * 0.22) / 0.25)
        if k <= 0:
            continue
        cx = 220 + (i % 3) * 320; cy = 230 + (i // 3) * 210
        d.rounded_rectangle((cx - 140, cy - 70, cx + 140, cy + 70), 20, fill=(60, 66, 82))
        ctext(d, cx, cy - 40, s, 52)
        if k >= 1:
            d.line((cx - 120, cy - 60, cx + 120, cy + 60), fill=RED, width=12)
    if t > 1.8:
        k = ease((t - 1.8) / 0.4)
        ctext(d, 540, 640 + (1 - k) * 40, "커피 대신 허브차 · 피자는 금요일 밤에만", 40, fill=(160, 230, 170))


run("policy", 2.8, grad((40, 30, 60), (90, 60, 90)), policy)
run("taste", 3.0, grad((50, 40, 60), (120, 80, 100)), taste)
run("spoon", 2.8, grad((30, 40, 70), (80, 90, 120)), spoon_cmp)
run("rules", 2.8, grad((35, 40, 55), (70, 75, 95)), rules)
print("ok")
