#!/usr/bin/env python3
"""나뭇가지를 덮은 '춤추는 솜뭉치'(솜털 진딧물·부기우기 진딧물) — 모션그래픽(카드 영상 칸 1080x780) — 2026.11.03 오늘의쓸모.
  python3 scripts/story_shorts/anim_aphid.py <출력폴더>
  → wax.mp4   (옆에서 본 진딧물 한 마리: 등에서 흰 '왁스 실'이 자라 나옴 — 털이 아님)
    sway.mp4  (나뭇가지 위 진딧물 떼: 무당벌레가 다가오자 다 같이 좌우로 흔들흔들)
    stab.mp4  (애벌레가 바늘 같은 입을 내밀어 다가온 손가락을 '콕')
근거: Ohio State BYGL 'Beware of Stiletto-Brandishing Boogie-Woogie Aphids'(흰 왁스 실, 건드리면 다 같이 흔듦 — 천적을 헷갈리게 한다는 추정,
      공격형 애벌레가 바늘 같은 입으로 떼 지어 찌름·화끈, 늦여름~가을 절정), Bangor Daily News 2021.10.21(춤으로 천적을 쫓는 진딧물),
      촬영자 @jonsimo 설명(나무 수액을 먹고, 방해받으면 리듬 있게 흔듦).
"""
import math, subprocess, sys, os, random
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (14, 22, 18); BARK = (120, 112, 96); BARK_D = (80, 74, 62); BODY = (150, 120, 70); BODY_D = (110, 86, 50)
WAX = (245, 246, 250); WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (226, 50, 44); SKIN = (236, 190, 160)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))
random.seed(3)


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


def aphid(d, x, y, s, wax=1.0, tilt=0.0, t=0.0, stylet=0.0):
    """옆에서 본 진딧물. x,y = 몸 가운데, s = 크기 배율, wax = 왁스 실 길이(0~1), tilt = 좌우 흔들림(라디안)."""
    def rot(px, py):
        c, sn = math.cos(tilt), math.sin(tilt)
        dx, dy = px - x, py - (y + 40 * s)          # 다리 쪽을 축으로 흔들림
        return (x + dx * c - dy * sn, y + 40 * s + dx * sn + dy * c)
    # 다리
    for k in range(3):
        lx = x - 40 * s + k * 40 * s
        a, b = rot(lx, y + 15 * s), rot(lx - 18 * s, y + 48 * s)
        d.line((a, b), fill=BODY_D, width=max(2, int(5 * s)))
    # 왁스 실(등 위로 휘날림)
    if wax > 0:
        for k in range(14):
            bx = x - 60 * s + k * 9 * s
            L = (70 + 50 * math.sin(k * 1.7)) * s * wax
            sw = math.sin(t * 3 + k) * 10 * s
            pts = [rot(bx, y - 20 * s)]
            for j in range(1, 6):
                u = j / 5
                pts.append(rot(bx - 30 * s * u + sw * u, y - 20 * s - L * u))
            d.line(pts, fill=WAX, width=max(2, int(7 * s)), joint="curve")
    # 몸통·머리
    body = [rot(x + 70 * s * math.cos(a), y + 32 * s * math.sin(a)) for a in [i * math.pi / 20 for i in range(40)]]
    d.polygon(body, fill=BODY, outline=BODY_D)
    hx, hy = rot(x + 78 * s, y + 4 * s)
    d.ellipse((hx - 18 * s, hy - 16 * s, hx + 18 * s, hy + 16 * s), fill=BODY_D)
    ex, ey = rot(x + 84 * s, y - 2 * s)
    d.ellipse((ex - 4 * s, ey - 4 * s, ex + 4 * s, ey + 4 * s), fill=(20, 10, 10))
    # 바늘 같은 입(스타일렛)
    if stylet > 0:
        a, b = rot(x + 92 * s, y + 10 * s), rot(x + 92 * s + 80 * s * stylet, y + 10 * s + 20 * s * stylet)
        d.line((a, b), fill=(60, 40, 30), width=max(3, int(6 * s)))


def wax(img, t):
    d = ImageDraw.Draw(img)
    g = ease(clamp((t - 0.3) / 1.6))
    aphid(d, 470, 470, 2.6, wax=g, t=t)
    d.rectangle((0, 600, W, 650), fill=BARK); d.rectangle((0, 645, W, 655), fill=BARK_D)
    if t < 1.2:
        ctext(d, 540, 40, "흰 '털'?", 60, YEL)
    else:
        ctext(d, 540, 40, "몸에서 뽑아낸 '왁스 실'", 60, YEL)
        d.line((760, 200, 640, 260), fill=YEL, width=6)
        ctext(d, 860, 150, "털 X", 54, RED)


BUGS = [(90 + k * 95, 560 - (k % 2) * 30) for k in range(10)]


def sway(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 600, W, 660), fill=BARK); d.rectangle((0, 655, W, 665), fill=BARK_D)
    on = clamp((t - 0.9) / 0.3)                         # 무당벌레가 다가오면 시작
    ang = math.sin(t * 2 * math.pi * 1.6) * 0.38 * on
    for (x, y) in BUGS:
        aphid(d, x, y, 0.7, wax=1.0, tilt=ang, t=t)
    # 무당벌레
    lx = -80 + 260 * ease(clamp(t / 1.0)) - 120 * ease(clamp((t - 1.8) / 0.8))
    d.ellipse((lx - 55, 640 - 70, lx + 55, 640 - 5), fill=RED, outline=(0, 0, 0), width=4)
    d.line((lx, 572, lx, 635), fill=(0, 0, 0), width=4)
    for dx, dy in [(-25, 600), (25, 600), (-20, 622), (22, 622)]:
        d.ellipse((lx + dx - 9, dy - 9, lx + dx + 9, dy + 9), fill=(0, 0, 0))
    d.ellipse((lx + 40, 585, lx + 80, 625), fill=(0, 0, 0))
    ctext(d, 540, 40, "건드리면 다 같이", 56)
    if on > 0:
        ctext(d, 540, 120, "흔들흔들!", 84, YEL, 6)
    if t > 1.8:
        ctext(d, 540, 700, "천적을 헷갈리게 하려는 걸로 추정", 38, (200, 200, 200), 4)


def stab(img, t):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 600, W, 660), fill=BARK); d.rectangle((0, 655, W, 665), fill=BARK_D)
    aphid(d, 360, 470, 2.0, wax=0.8, t=t, stylet=ease(clamp((t - 0.9) / 0.4)))
    # 다가오는 손가락
    fx = 1200 - 360 * ease(clamp(t / 1.0)) + (60 * ease(clamp((t - 1.4) / 0.3)) if t > 1.4 else 0)
    d.rounded_rectangle((fx, 420, fx + 600, 540), 60, fill=SKIN, outline=(170, 120, 100), width=4)
    d.ellipse((fx + 10, 440, fx + 70, 520), fill=(250, 215, 200))
    hit = 1.25 < t < 2.2
    if hit:
        ctext(d, fx + 60, 300, "콕!", 90, YEL, 6)
        for k in range(6):
            a = k * math.pi / 3
            d.line((fx + 40 + 50 * math.cos(a), 480 + 50 * math.sin(a), fx + 40 + 85 * math.cos(a), 480 + 85 * math.sin(a)), fill=RED, width=6)
    ctext(d, 540, 40, "바늘 같은 입", 58, YEL)
    if t > 1.6:
        ctext(d, 540, 700, "떼로 몰려와 찌르기도 (화끈)", 40)


run("wax", 2.8, wax)
run("sway", 3.0, sway)
run("stab", 2.8, stab)
print("ok")
