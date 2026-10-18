#!/usr/bin/env python3
"""'호일은 왜 한쪽만 반짝일까' 설명 모션그래픽(카드 영상 칸 1080x780) — 2026.10.18 오늘의쓸모.
  python3 scripts/story_shorts/anim_foilside.py <출력폴더>
  → flip.mp4(반짝 면 ↔ 무광 면 뒤집기) rumor.mp4(어느 면이 안쪽? 말풍선) same.mp4(제조사: 어느 면이든 같다)
    mill.mp4(마지막 압연: 두 장을 겹쳐 롤러에 통과) split.mp4(롤러에 닿은 면=반짝, 서로 닿은 면=무광)
    nonstick.mp4(논스틱 호일만 무광 면 코팅)
"""
import math, random, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
BG = (240, 244, 250); INK = (30, 34, 44); GRAY = (150, 158, 172)
YEL = (255, 216, 77); RED = (235, 64, 52); GRN = (46, 184, 92); BLU = (40, 140, 255)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))
rng = np.random.default_rng(7)

# ---------- 호일 질감 (한 번만 계산) ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_sh = 205 + 28 * np.sin((xx * 0.9 + yy * 0.5) / 55) + 14 * np.sin((xx - yy * 1.3) / 23)
_sh += rng.normal(0, 2, (H, W))
SHINY = np.clip(np.stack([_sh, _sh + 4, _sh + 10], -1), 0, 255).astype(np.float32)
_ma = 172 + rng.normal(0, 9, (H, W))
_ma = np.array(Image.fromarray(np.clip(_ma, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32)
_ma += 6 * np.sin(xx / 140)
MATTE = np.clip(np.stack([_ma, _ma + 1, _ma + 3], -1), 0, 255).astype(np.float32)


def foil_patch(kind, w, h, t, sweep=True):
    """kind='shiny'|'matte' → w x h RGB 이미지. shiny 는 대각선 빛줄기가 지나감."""
    w, h = max(2, int(w)), max(2, int(h))
    if kind == "shiny":
        a = SHINY[:h, :w].copy()
        if sweep:
            px = ((t * 700) % (w + 900)) - 450
            band = np.exp(-(((xx[:h, :w] + yy[:h, :w] * 0.6) - px) / 70) ** 2) * 70
            a += band[..., None]
    else:
        a = MATTE[:h, :w].copy()
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def paste_sheet(img, kind, cx, cy, w, h, t, sx=1.0, sweep=True, radius=18):
    ww = max(2, int(w * sx))
    p = foil_patch(kind, ww, h, t, sweep)
    m = Image.new("L", (ww, int(h)), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, ww - 1, int(h) - 1), radius, fill=255)
    # 그림자
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((cx - ww / 2 + 10, cy - h / 2 + 14, cx + ww / 2 + 10, cy + h / 2 + 14), radius, fill=(0, 0, 0, 60))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    img.paste(p, (int(cx - ww / 2), int(cy - h / 2)), m)
    ImageDraw.Draw(img).rounded_rectangle((cx - ww / 2, cy - h / 2, cx + ww / 2, cy + h / 2), radius, outline=(120, 126, 138), width=3)


def sparkle(d, x, y, r, a=1.0, col=(255, 255, 255)):
    if a <= 0: return
    r = r * a
    d.polygon([(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y), (x + r * 0.22, y + r * 0.22),
               (x, y + r), (x - r * 0.22, y + r * 0.22), (x - r, y), (x - r * 0.22, y - r * 0.22)], fill=col, outline=(255, 200, 40), width=3)


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


def tag(d, cx, cy, s, size, fill=INK, tcol=(255, 255, 255), a=1.0):
    if a <= 0: return
    ft = F(size); w = d.textlength(s, font=ft); s2 = 0.7 + 0.3 * ease(a)
    pw, ph = (w + size * 0.9) * s2, size * 1.55 * s2
    d.rounded_rectangle((cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2), int(ph / 2), fill=fill)
    if a > 0.5:
        d.text((cx - w / 2, cy - size * 0.72), s, font=ft, fill=tcol)


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


# ---------- 장면 ----------
def s_flip(img, t):
    # 0~1.1 반짝 면, 1.1~1.7 뒤집기, 1.7~ 무광 면, 2.3~ 둘을 나란히 + ?
    if t < 2.3:
        if t < 1.1: kind, sx = "shiny", 1.0
        else:
            k = clamp((t - 1.1) / 0.6); sx = abs(math.cos(k * math.pi)); kind = "shiny" if k < 0.5 else "matte"
        paste_sheet(img, kind, W / 2, 400, 700, 470, t, sx=max(sx, 0.02))
        d = ImageDraw.Draw(img)
        if kind == "shiny" and t < 1.1:
            for (x, y, ph) in [(300, 250, 0), (760, 330, 0.4), (420, 560, 0.8), (820, 560, 0.2)]:
                sparkle(d, x, y, 36, 0.5 + 0.5 * math.sin(t * 9 + ph * 6))
            tag(d, W / 2, 105, "반짝 면", 56, fill=YEL, tcol=INK, a=clamp(t / 0.25))
        elif kind == "matte":
            tag(d, W / 2, 105, "무광 면", 56, fill=(110, 116, 128), a=clamp((t - 1.45) / 0.25))
    else:
        k = ease((t - 2.3) / 0.4)
        lx = W / 2 - 250 * k; rx = W / 2 + 250 * k
        paste_sheet(img, "shiny", lx, 420, 420, 400, t)
        paste_sheet(img, "matte", rx, 420, 420, 400, t)
        d = ImageDraw.Draw(img)
        tag(d, lx, 140, "반짝 면", 50, fill=YEL, tcol=INK)
        tag(d, rx, 140, "무광 면", 50, fill=(110, 116, 128))
        q = clamp((t - 2.5) / 0.25)
        if q > 0:
            r = 80 * (0.6 + 0.4 * ease(q)) * (1 + 0.06 * math.sin(t * 10))
            d.ellipse((W / 2 - r, 420 - r, W / 2 + r, 420 + r), fill=RED)
            ctext(d, W / 2, 420 - r * 0.85, "?", int(r * 1.35), fill=(255, 255, 255))


def potato(d, cx, cy, s=1.0):
    d.ellipse((cx - 150 * s, cy - 75 * s, cx + 150 * s, cy + 75 * s), fill=(150, 70, 110), outline=INK, width=6)
    for (dx, dy) in [(-60, -15), (30, 20), (90, -25)]:
        d.arc((cx + dx * s - 14, cy + dy * s - 6, cx + dx * s + 14, cy + dy * s + 6), 0, 180, fill=(100, 40, 70), width=4)


def s_rumor(img, t):
    paste_sheet(img, "shiny", W / 2, 560, 760, 300, t)
    d = ImageDraw.Draw(img)
    potato(d, W / 2, 520, 1.0)
    if t > 0.15: bubble(d, 50, 60, 400, 140, "반짝 면이 안쪽!", 50)
    if t > 0.8: bubble(d, 630, 50, 400, 140, "아니, 무광 면!", 50, tail=1)
    if t > 1.5: bubble(d, 340, 230, 400, 130, "무광엔 코팅?", 50, fill=(255, 245, 200))
    if t > 2.2:
        for k, (x, y) in enumerate([(120, 330), (960, 330)]):
            ctext(d, x, y - 60, "?", 110, fill=RED)


def s_same(img, t):
    lx, rx = 290, 790
    paste_sheet(img, "shiny", lx, 330, 400, 360, t)
    paste_sheet(img, "matte", rx, 330, 400, 360, t)
    d = ImageDraw.Draw(img)
    tag(d, lx, 110, "반짝 면", 48, fill=YEL, tcol=INK)
    tag(d, rx, 110, "무광 면", 48, fill=(110, 116, 128))
    e = clamp((t - 0.4) / 0.3)
    if e > 0:
        ctext(d, W / 2, 255, "=", int(150 * (0.6 + 0.4 * ease(e))), fill=INK, stroke=8)
    check(d, lx, 330, 70, True, clamp((t - 0.8) / 0.3))
    check(d, rx, 330, 70, True, clamp((t - 1.1) / 0.3))
    if t > 1.6:
        a = ease((t - 1.6) / 0.35)
        y = 640 + 40 * (1 - a)
        d.rounded_rectangle((90, y - 70, W - 90, y + 70), 34, fill=INK)
        ctext(d, W / 2, y - 44, "굽기·얼리기·보관 다 같다", 54, fill=(255, 255, 255))


def roller(d, cx, cy, r, ang):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(170, 178, 192), outline=INK, width=6)
    d.ellipse((cx - r * 0.82, cy - r * 0.82, cx + r * 0.82, cy + r * 0.82), outline=(205, 212, 224), width=10)
    for k in range(6):
        a = ang + k * math.pi / 3
        d.line([(cx + math.cos(a) * r * 0.2, cy + math.sin(a) * r * 0.2), (cx + math.cos(a) * r * 0.7, cy + math.sin(a) * r * 0.7)], fill=(120, 128, 142), width=10)
    d.ellipse((cx - r * 0.2, cy - r * 0.2, cx + r * 0.2, cy + r * 0.2), fill=(90, 96, 110))


def strip(d, x0, x1, y0, y1, col, t, speed, out=(120, 126, 138)):
    d.rectangle((x0, y0, x1, y1), fill=col, outline=out, width=3)
    # 움직임 표시 줄무늬
    step = 90; off = (t * speed) % step
    x = x0 - step + off
    while x < x1:
        if x > x0: d.line([(x, y0 + 3), (x + 18, y0 + 3)], fill=(255, 255, 255), width=3)
        x += step


def s_mill(img, t):
    d = ImageDraw.Draw(img)
    cx, cy, r = 560, 400, 165
    ang = t * 2.5
    # 들어가는 두 장(두꺼움) / 나오는 두 장(얇음)
    A = (214, 222, 236); B = (226, 216, 200)
    strip(d, -10, cx, cy - 50, cy - 2, A, t, 140)
    strip(d, -10, cx, cy + 2, cy + 50, B, t, 140)
    strip(d, cx, W + 10, cy - 20, cy - 1, A, t, 300)
    strip(d, cx, W + 10, cy + 1, cy + 20, B, t, 300)
    roller(d, cx, cy - 20 - r, r, -ang)
    roller(d, cx, cy + 20 + r, r, ang)
    # 라벨
    a = clamp((t - 0.3) / 0.3)
    if a > 0:
        tag(d, 190, 270, "호일 2장", 48, fill=BLU, a=a)
        d.line([(190, 300), (190, 345)], fill=BLU, width=8)
    a2 = clamp((t - 1.4) / 0.3)
    if a2 > 0:
        tag(d, 900, 300, "겹쳐서 쭉", 48, fill=INK, a=a2)
        d.line([(900, 330), (900, 380)], fill=INK, width=8)
    a3 = clamp((t - 2.2) / 0.3)
    if a3 > 0:
        tag(d, 900, 500, "0.016mm", 46, fill=RED, a=a3)


def rough_line(y, x0, x1, amp, seed):
    r = random.Random(seed)
    return [(x, y + r.uniform(-amp, amp)) for x in range(int(x0), int(x1) + 1, 12)]


def s_split(img, t):
    d = ImageDraw.Draw(img)
    x0, x1 = 120, 960
    sep = 150 * ease((t - 1.8) / 0.6)
    topy = 300 - sep; boty = 400 + sep  # 위 장: topy~topy+80, 아래 장: boty-80~boty
    # 롤러 일부(위·아래)
    if sep < 5:
        d.rectangle((0, 0, W, 175), fill=(196, 202, 214)); d.line([(0, 175), (W, 175)], fill=INK, width=6)
        d.rectangle((0, 525, W, H), fill=(196, 202, 214)); d.line([(0, 525), (W, 525)], fill=INK, width=6)
        ctext(d, W / 2, 70, "롤러", 50, fill=(90, 96, 110)); ctext(d, W / 2, 620, "롤러", 50, fill=(90, 96, 110))
    A = (214, 222, 236); B = (226, 216, 200)
    # 위 장
    top = [(x0, topy)] + [(x1, topy)] + list(reversed(rough_line(topy + 80, x0, x1, 7, 1)))
    d.polygon(top, fill=A)
    # 아래 장
    bot = rough_line(boty - 80, x0, x1, 7, 2) + [(x1, boty), (x0, boty)]
    d.polygon(bot, fill=B)
    # 반짝 면: 바깥쪽(위 장의 윗면, 아래 장의 아랫면)
    a = clamp((t - 0.3) / 0.3)
    if a > 0:
        d.line([(x0, topy), (x1, topy)], fill=(255, 255, 255), width=10)
        d.line([(x0, boty), (x1, boty)], fill=(255, 255, 255), width=10)
        for k, x in enumerate(range(200, 900, 170)):
            sparkle(d, x, topy, 26, a * (0.6 + 0.4 * math.sin(t * 8 + k)))
            sparkle(d, x + 80, boty, 26, a * (0.6 + 0.4 * math.sin(t * 8 + k + 1)))
    # 무광 면: 안쪽 거친 선
    b = clamp((t - 2.1) / 0.3)
    if b > 0:
        d.line(rough_line(topy + 80, x0, x1, 7, 1), fill=(110, 116, 128), width=7)
        d.line(rough_line(boty - 80, x0, x1, 7, 2), fill=(110, 116, 128), width=7)
    # 라벨
    if a > 0:
        tag(d, W / 2, topy - 50 if sep > 5 else 230, "롤러에 닿은 면 = 반짝", 44, fill=YEL, tcol=INK, a=a)
    if b > 0:
        my = (topy + 80 + boty - 80) / 2
        tag(d, W / 2, my, "서로 닿은 면 = 무광", 44, fill=(110, 116, 128), a=b)


def egg(d, cx, cy, s=1.0):
    pts = []
    for k in range(24):
        a = k / 24 * 2 * math.pi
        rr = 120 * s * (1 + 0.12 * math.sin(a * 5))
        pts.append((cx + math.cos(a) * rr * 1.2, cy + math.sin(a) * rr * 0.75))
    d.polygon(pts, fill=(255, 255, 255), outline=INK)
    d.ellipse((cx - 48 * s, cy - 44 * s, cx + 48 * s, cy + 44 * s), fill=(255, 190, 40), outline=(220, 140, 20), width=4)


def s_nonstick(img, t):
    paste_sheet(img, "matte", W / 2, 470, 820, 420, t)
    d = ImageDraw.Draw(img)
    # 코팅 점무늬
    a = clamp((t - 0.2) / 0.4)
    if a > 0:
        for i in range(14):
            for j in range(7):
                x = 160 + i * 58 + (j % 2) * 29; y = 300 + j * 52
                rr = 7 * a
                d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(120, 190, 255))
    tag(d, W / 2, 95, "논스틱 호일", 56, fill=BLU, a=clamp(t / 0.25))
    e = clamp((t - 0.9) / 0.5)
    if e > 0:
        egg(d, W / 2 - 120 + 120 * ease(e), 470, 1.0)
    if t > 1.6:
        tag(d, W / 2, 700, "코팅된 무광 면 = 음식 쪽", 46, fill=INK, a=clamp((t - 1.6) / 0.3))
        check(d, W / 2 + 230, 400, 60, True, clamp((t - 1.8) / 0.3))


if __name__ == "__main__":
    only = sys.argv[2:] or ["flip", "rumor", "same", "mill", "split", "nonstick"]
    table = {"flip": (3.2, s_flip), "rumor": (3.4, s_rumor), "same": (3.4, s_same),
             "mill": (3.6, s_mill), "split": (3.8, s_split), "nonstick": (3.6, s_nonstick)}
    for n in only:
        run(n, *table[n])
        print("ok", n)
