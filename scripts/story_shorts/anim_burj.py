#!/usr/bin/env python3
"""부르즈 할리파 꼭대기에 선 승무원(에미레이트 2021 광고) 모션그래픽(카드 영상 칸 1080x780) — 2026.11.09 오늘의쓸모.
  python3 scripts/story_shorts/anim_burj.py <출력폴더>
  → height.mp4  (높이 비교: 63빌딩 249m · 롯데월드타워 555m · 부르즈 할리파 828m, 맨 끝에 사람 점)
    climb.mp4   (엘리베이터로 160층 → 그 위로는 사다리·계단을 걸어서 1시간 15분)
    harness.mp4 (유니폼 속에 숨긴 하네스 → 기둥 + 꼭대기 두 곳, 고정점 3곳)
근거: Khaleej Times 2021.08.09(828m, 160층에서 1시간 15분, 기둥 달린 맞춤 발판, 숨긴 하네스로 기둥과 꼭대기 두 곳에 고정,
      드론 1대로 이어서 촬영, 꼭대기에서 약 5시간), The National 2021.08.09, Airline Ratings 2022.01.14.
      63빌딩 249m(한화), 롯데월드타워 555m(롯데물산).
"""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (215, 25, 35); DARK = (30, 34, 44); GREY = (150, 160, 178)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))


def grad(top, bot):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line((0, y, W, y), fill=tuple(int(a + (b - a) * k) for a, b in zip(top, bot)))
    return img


SKY = grad((60, 110, 190), (215, 190, 150))


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


GROUND = 720
SCALE = 600 / 828  # 828m → 600px


def burj(d, cx, k, col=(205, 214, 228)):
    """부르즈 할리파 실루엣(아래부터 k 만큼 자람). 맨 끝 y 를 돌려줌"""
    h = 828 * SCALE * k
    top = GROUND - h
    tiers = [(0.00, 70), (0.25, 56), (0.45, 44), (0.62, 32), (0.75, 22), (0.84, 12), (0.90, 5)]
    for i, (s, half) in enumerate(tiers):
        e = tiers[i + 1][0] if i + 1 < len(tiers) else 1.0
        y1 = GROUND - 828 * SCALE * s; y2 = GROUND - 828 * SCALE * e
        y2 = max(y2, top)
        if y1 <= top:
            break
        d.rectangle((cx - half, y2, cx + half, y1), fill=col, outline=(90, 100, 120), width=2)
    return top


def tower(d, cx, hm, k, label, col):
    h = hm * SCALE * k
    d.rectangle((cx - 48, GROUND - h, cx + 48, GROUND), fill=col, outline=(90, 100, 120), width=2)
    for y in range(int(GROUND - h) + 10, GROUND - 6, 22):
        d.line((cx - 38, y, cx + 38, y), fill=(255, 255, 255), width=1)
    if k > 0.98:
        ctext(d, cx, GROUND - h - 64, f"{hm}m", 40)
        ctext(d, cx, GROUND + 6, label, 30, stroke=4)


def person(d, x, ytop, s=1.0):
    """빨간 모자 승무원(작게)"""
    d.rectangle((x - 5 * s, ytop + 10 * s, x + 5 * s, ytop + 30 * s), fill=(200, 170, 130))
    d.ellipse((x - 5 * s, ytop + 1 * s, x + 5 * s, ytop + 11 * s), fill=(235, 200, 175))
    d.rectangle((x - 5 * s, ytop - 3 * s, x + 5 * s, ytop + 3 * s), fill=RED)


# ① 높이 비교
def height(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, GROUND, W, H), fill=(120, 105, 85))
    tower(d, 190, 249, ease(t / 0.5), "63빌딩", (150, 170, 195))
    tower(d, 430, 555, ease((t - 0.3) / 0.6), "롯데월드타워", (130, 150, 180))
    kb = ease((t - 0.6) / 0.8)
    top = burj(d, 760, kb)
    if kb > 0.98:
        ctext(d, 760, GROUND + 6, "부르즈 할리파", 30, stroke=4)
        ctext(d, 900, top + 10, "828m", 44, fill=YEL)
        person(d, 760, top - 34, 1.0)
        a = clamp((t - 1.6) / 0.3)
        if a > 0:
            # 빨간 화살표 + 라벨
            x0, y0 = 600, top - 60
            d.line((x0, y0, 748, top - 22), fill=RED, width=8)
            d.polygon([(752, top - 18), (726, top - 24), (740, top - 44)], fill=RED)
            ctext(d, 520, y0 - 46, "여기 서 있어요", 36, fill=WHITE)


# ② 160층까지 엘리베이터, 그 위는 걸어서
def climb(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, GROUND, W, H), fill=(120, 105, 85))
    cx = 540
    top = burj(d, cx, 1.0)
    y160 = GROUND - 585 * SCALE  # 160층 ≈ 585m 안팎(최상층 거주 공간 위)
    # 엘리베이터 구간
    ke = ease(t / 0.8)
    d.line((cx, GROUND - 4, cx, GROUND - 4 - (GROUND - 4 - y160) * ke), fill=(80, 200, 255), width=10)
    ctext(d, cx - 250, y160 - 10, "160층까지 엘리베이터", 34, fill=(140, 220, 255))
    # 걸어서 구간(점선)
    kw = clamp((t - 0.9) / 1.6)
    if kw > 0:
        n = int(18 * kw)
        for i in range(n):
            yy = y160 - (y160 - top) * (i / 18)
            d.ellipse((cx - 6, yy - 6, cx + 6, yy + 6), fill=YEL)
        mins = int(75 * kw)
        ctext(d, cx + 250, (y160 + top) / 2 - 40, "사다리·계단을 걸어서", 32, fill=YEL)
        ctext(d, cx + 250, (y160 + top) / 2 + 4, (f"{mins // 60}시간 {mins % 60}분" if mins >= 60 else f"{mins}분"), 54, fill=WHITE)
    if kw >= 1:
        person(d, cx, top - 34, 1.2)


# ③ 숨은 하네스
def harness(img, t):
    d = ImageDraw.Draw(img)
    # 꼭대기 끝(첨탑) + 발판 + 기둥
    d.polygon([(470, H), (610, H), (575, 560), (505, 560)], fill=(190, 198, 212), outline=(90, 100, 120))
    d.rectangle((440, 530, 640, 560), fill=(70, 74, 84))
    d.rectangle((600, 250, 614, 530), fill=(50, 54, 62))
    ctext(d, 760, 236, "기둥 달린 발판", 32, fill=(220, 226, 236))
    # 승무원(크게)
    cx = 520
    d.rectangle((cx - 34, 330, cx + 34, 450), fill=(200, 170, 130))      # 상의
    d.rectangle((cx - 30, 450, cx - 6, 530), fill=(190, 160, 120))      # 다리
    d.rectangle((cx + 6, 450, cx + 30, 530), fill=(190, 160, 120))
    d.ellipse((cx - 26, 268, cx + 26, 324), fill=(235, 200, 175))
    d.rounded_rectangle((cx - 28, 252, cx + 28, 282), 8, fill=RED)
    # 유니폼이 투명해지며 하네스가 드러남
    k = ease((t - 0.4) / 0.6)
    if k > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        a = int(255 * k)
        ld.line((cx - 34, 400, cx + 34, 400), fill=(255, 150, 0, a), width=10)
        ld.line((cx - 30, 340, cx + 20, 400), fill=(255, 150, 0, a), width=8)
        ld.line((cx + 30, 340, cx - 20, 400), fill=(255, 150, 0, a), width=8)
        img.paste(lay, (0, 0), lay)
        d = ImageDraw.Draw(img)
        ctext(d, 250, 300, "유니폼 속", 36)
        ctext(d, 250, 346, "숨긴 하네스", 40, fill=(255, 170, 40))
    # 고정줄 3개
    pts = [(607, 380), (500, 556), (580, 556)]
    for i, (px, py) in enumerate(pts):
        kk = ease((t - 1.1 - i * 0.35) / 0.35)
        if kk <= 0:
            continue
        sx, sy = cx, 404
        ex, ey = sx + (px - sx) * kk, sy + (py - sy) * kk
        d.line((sx, sy, ex, ey), fill=YEL, width=6)
        if kk >= 1:
            d.ellipse((px - 11, py - 11, px + 11, py + 11), fill=RED, outline=WHITE, width=3)
    if t > 2.3:
        ctext(d, 820, 600, "고정점 3곳", 48, fill=YEL)


run("height", 2.6, SKY, height)
run("climb", 3.0, SKY, climb)
run("harness", 3.0, grad((70, 120, 200), (190, 200, 215)), harness)
print("ok")
