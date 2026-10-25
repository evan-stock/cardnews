#!/usr/bin/env python3
"""전자레인지 포도 플라즈마 설명 모션그래픽(카드 영상 칸 1080x960) — 2026.10.25 오늘의쓸모.
  python3 scripts/story_shorts/anim_grapeplasma.py <출력폴더>
  → whole.mp4(껍질 다리 없이 통포도 두 알 · 물 젤리 구슬 두 알도 맞닿은 점에서 불꽃 — 2019 PNAS 실험)
    hotspot.mp4(포도 속 물에 전자파가 갇혀 튕기다 두 알이 맞닿은 틈으로 몰려 번쩍)
"""
import math, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 960, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (20, 18, 30); INK = (244, 242, 250); GRAY = (160, 156, 178)
YEL = (255, 216, 77); RED = (240, 66, 56); GRN = (46, 196, 100); ORG = (255, 150, 40)
GRAPE = (110, 40, 120); GRAPE_HI = (170, 90, 180); GEL = (150, 210, 255)
clamp = lambda t: max(0.0, min(1.0, t))
ease = lambda t: 1 - (1 - clamp(t)) ** 3


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


def ball(img, cx, cy, r, col, hi, alpha=255):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (alpha,))
    d.ellipse((cx - r * 0.55, cy - r * 0.6, cx - r * 0.15, cy - r * 0.25), fill=hi + (min(255, alpha),))
    img.alpha_composite(lay)


def glow(img, cx, cy, r, a):
    """번쩍이는 플라즈마 빛(흰 중심 + 주황·보라 번짐)."""
    if a <= 0:
        return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for rr, col, al in ((r * 2.4, (200, 120, 255), 90), (r * 1.6, ORG, 160), (r, YEL, 230), (r * 0.5, (255, 255, 255), 255)):
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=col + (int(al * a),))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(max(2, r * 0.35))))


def whole(img, t):
    d = ImageDraw.Draw(img)
    ctext(d, W / 2, 40, "껍질로 안 이어도 된다", 64, YEL)
    ctext(d, W / 2, 128, "2019년 PNAS 실험", 38, GRAY)
    r = 118
    for k, (cx, col, hi, label) in enumerate(((290, GRAPE, GRAPE_HI, "통포도 두 알"), (790, GEL, (235, 248, 255), "물 젤리 구슬"))):
        app = ease((t - 0.15 - k * 0.5) / 0.5)
        if app <= 0:
            continue
        cy = 520 + (1 - app) * 60
        al = int(255 * app) if col == GRAPE else int(200 * app)
        ball(img, cx - r, cy, r, col, hi, al)
        ball(img, cx + r, cy, r, col, hi, al)
        ctext(d, cx, 700, label, 52, INK)
        # 맞닿은 점에서 번쩍(깜빡이며 커짐)
        tt = t - 1.0 - k * 0.5
        if tt > 0:
            a = clamp(tt * 3) * (0.75 + 0.25 * math.sin(tt * 40))
            glow(img, cx, cy - 20, 40 + 30 * clamp(tt), a)
    d = ImageDraw.Draw(img)
    if t > 2.2:
        ctext(d, W / 2, 800, "맞닿은 점에서 똑같이 '번쩍'", 50, ORG)


def hotspot(img, t):
    d = ImageDraw.Draw(img)
    ctext(d, W / 2, 40, "포도 속 '물'이 전자파를 가둔다", 60, YEL)
    r = 220; cy = 520; c1 = (W / 2 - r, cy); c2 = (W / 2 + r, cy)
    ball(img, c1[0], cy, r, GRAPE, GRAPE_HI)
    ball(img, c2[0], cy, r, GRAPE, GRAPE_HI)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    # 안에서 튕기는 물결(동심원) — 시간이 갈수록 맞닿은 점 쪽으로 쏠림
    pull = ease((t - 1.0) / 1.6)
    for (cx, _), sgn in ((c1, 1), (c2, -1)):
        for k in range(4):
            ph = ((t * 0.9 + k / 4) % 1.0)
            rr = 30 + ph * (r - 40)
            ox = cx + sgn * pull * (r - rr) * 0.9
            dl.ellipse((ox - rr, cy - rr * (1 - 0.3 * pull), ox + rr, cy + rr * (1 - 0.3 * pull)),
                       outline=(255, 230, 120, int(200 * (1 - ph))), width=6)
    img.alpha_composite(lay)
    # 몰린 에너지 → 번쩍
    a = clamp((t - 1.6) / 0.9)
    flick = 0.8 + 0.2 * math.sin(t * 45)
    glow(img, W / 2, cy, 30 + 70 * a, a * flick)
    d = ImageDraw.Draw(img)
    if t > 1.2:
        ctext(d, W / 2, 800, "두 알이 맞닿은 '틈'으로 몰려 번쩍", 50, ORG)


run("whole", 3.6, whole)
run("hotspot", 3.8, hotspot)
print("ok")
