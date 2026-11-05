#!/usr/bin/env python3
"""이 탱크는 사고가 아닙니다 — 철도 탱크차 진공 찌그러짐 모션그래픽(카드 영상 칸 1080x780) — 2026.11.05 오늘의쓸모.
  python3 scripts/story_shorts/anim_tankcrush.py <출력폴더>
  → steam.mp4 (탱크 옆 단면: ① 뜨거운 김으로 세척 → ② 뚜껑 꽉 → ③ 김이 식어 물방울 → 속은 거의 텅 빈 '진공')
    press.mp4 (둥근 단면: 바깥 공기가 사방에서 1㎡마다 약 10톤으로 누름 → 속에서 버티는 공기가 없어 '와그작')
    vent.mp4  (뚜껑·밸브를 열어 두면 바깥 공기가 들어와 안팎 압력이 같아져 멀쩡)
근거: 대기압 101.3kPa ≈ 1㎡당 약 10.3톤(1kgf/㎠), Paul Mueller Academy 'Top 4 causes of implosions in tanks'
      (세척 뒤 뜨거운 김이 식으며 생긴 진공 + 막힌 통기구), MythBusters 2016 'Tanker Crush'(김을 채운 뒤 밀폐·냉각해 탱크차를 찌그러뜨림).
"""
import math, subprocess, sys, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 210, 60); RED = (240, 70, 50); BG = (24, 30, 36)
STEEL = (96, 104, 112); STEEL_D = (60, 66, 72); INSIDE = (40, 48, 56); STEAM = (235, 238, 242); WATER = (80, 160, 235); BLUE = (90, 170, 255)
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


def arrow(d, x0, y0, x1, y1, col, w=12):
    d.line([(x0, y0), (x1, y1)], fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0); L = w * 2.6
    p1 = (x1 + L * math.cos(a + 2.6), y1 + L * math.sin(a + 2.6))
    p2 = (x1 + L * math.cos(a - 2.6), y1 + L * math.sin(a - 2.6))
    d.polygon([(x1 + w * 0.6 * math.cos(a), y1 + w * 0.6 * math.sin(a)), p1, p2], fill=col)


# ---------- 공통: 옆에서 본 탱크(캡슐) ----------
TX0, TX1, TY0, TY1 = 150, 930, 300, 600
HATCH_X = 540


def tank_side(d, lid_open):
    r = (TY1 - TY0) / 2
    d.rounded_rectangle([TX0 - 14, TY0 - 14, TX1 + 14, TY1 + 14], radius=r + 14, fill=STEEL)
    d.rounded_rectangle([TX0, TY0, TX1, TY1], radius=r, fill=INSIDE)
    # 바퀴·받침
    d.rectangle([TX0 + 40, TY1 + 14, TX1 - 40, TY1 + 40], fill=STEEL_D)
    for x in (TX0 + 110, TX0 + 200, TX1 - 200, TX1 - 110):
        d.ellipse([x - 34, TY1 + 30, x + 34, TY1 + 98], fill=(30, 34, 38), outline=STEEL, width=6)
    # 뚜껑(맨홀)
    d.rectangle([HATCH_X - 60, TY0 - 44, HATCH_X + 60, TY0 - 14], fill=STEEL)
    if lid_open > 0:
        ang = math.radians(-70 * lid_open)
        cx, cy = HATCH_X + 64, TY0 - 44
        pts = [(-128, 0), (0, 0), (0, -18), (-128, -18)]
        rp = [(cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)) for x, y in pts]
        d.polygon(rp, fill=STEEL_D)
        d.rectangle([HATCH_X - 50, TY0 - 30, HATCH_X + 50, TY0], fill=INSIDE)
    else:
        d.rectangle([HATCH_X - 66, TY0 - 62, HATCH_X + 66, TY0 - 44], fill=STEEL_D)


rnd = random.Random(11)
PUFFS = [(rnd.uniform(TX0 + 90, TX1 - 90), rnd.uniform(TY0 + 50, TY1 - 50), rnd.uniform(30, 58), rnd.uniform(0, 6)) for _ in range(34)]
DROPS = [(rnd.uniform(TX0 + 110, TX1 - 110), rnd.uniform(0, 0.5)) for _ in range(22)]


def steam(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    lid = 1 - ease((t - 0.8) / 0.35)  # 0.8~1.15초에 닫힘
    tank_side(d, lid)
    fill = ease(t / 0.8)              # 김이 차오름
    cool = ease((t - 1.3) / 1.2)      # 식으며 사라짐
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for (x, y, r, ph) in PUFFS:
        rr = r * fill * (1 - 0.85 * cool) * (1 + 0.08 * math.sin(t * 5 + ph))
        if rr <= 1:
            continue
        a = int(220 * (1 - 0.9 * cool))
        ld.ellipse([x - rr, y - rr, x + rr, y + rr], fill=STEAM + (a,))
    lay = lay.filter(ImageFilter.GaussianBlur(10))
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle([TX0, TY0, TX1, TY1], radius=(TY1 - TY0) / 2, fill=255)
    al = lay.split()[3]; lay.putalpha(Image.composite(al, Image.new("L", (W, H), 0), m))
    img.paste(lay, (0, 0), lay); d = ImageDraw.Draw(img)
    # 세척 호스에서 김 들어감
    if t < 0.9:
        k = 1 - clamp((t - 0.6) / 0.3)
        d.line([(HATCH_X, 120), (HATCH_X, TY0 - 30)], fill=(200, 60, 40), width=int(16 * k) + 1)
        for j in range(4):
            yy = 160 + ((t * 600 + j * 40) % 140)
            d.ellipse([HATCH_X - 18, yy - 18, HATCH_X + 18, yy + 18], fill=STEAM)
    # 물방울이 바닥으로
    if cool > 0:
        for (x, ph) in DROPS:
            k = clamp((cool - ph) / 0.5)
            if k <= 0:
                continue
            y = TY0 + 60 + (TY1 - TY0 - 110) * ease(k)
            d.ellipse([x - 9, y - 12, x + 9, y + 12], fill=WATER)
        d.rectangle([TX0 + 120, TY1 - 26 * cool - 4, TX1 - 120, TY1 - 4], fill=WATER)
    steps = [("① 뜨거운 김으로 세척", 0.0), ("② 뚜껑을 꽉 닫음", 0.9), ("③ 김이 식어 물로 → 속이 텅", 1.6)]
    for i, (s, st) in enumerate(steps):
        if t >= st:
            ltext(d, 40, 30 + i * 74, s, 48, YEL if i == 2 else WHITE)
    if cool > 0.7:
        ctext(d, (TX0 + TX1) / 2, (TY0 + TY1) / 2 - 44, "거의 '진공'", 66, YEL)
    return img


# ---------- 2. 바깥 공기가 누름 ----------
PCX, PCY, PR = 540, 470, 200


def press(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    squash = ease((t - 1.5) / 0.6)
    n = 72
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        dent = squash * (0.62 * max(0, math.cos(a - math.pi / 2)) ** 3 + 0.40 * max(0, math.cos(a + math.pi / 2)) ** 3
                         + 0.30 * max(0, math.cos(a)) ** 4 + 0.30 * max(0, math.cos(a - math.pi)) ** 6)
        r = PR * (1 - dent)
        pts.append((PCX + r * math.cos(a), PCY + r * math.sin(a)))
    d.polygon(pts, fill=STEEL)
    pts2 = [(PCX + (x - PCX) * 0.93, PCY + (y - PCY) * 0.93) for x, y in pts]
    d.polygon(pts2, fill=INSIDE)
    ctext(d, PCX, PCY - 26, "속: 공기 거의 없음", 34, (170, 180, 190), 4)
    # 사방에서 들어오는 화살표
    ap = ease(t / 0.6)
    pulse = 1 + 0.06 * math.sin(t * 9)
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        r0 = PR + 140 * pulse; r1 = PR + 26 + 110 * (1 - ap)
        if ap <= 0:
            continue
        arrow(d, PCX + r0 * math.cos(a), PCY + r0 * math.sin(a), PCX + r1 * math.cos(a), PCY + r1 * math.sin(a), BLUE, 14)
    k = ease((t - 0.3) / 0.8)
    ctext(d, W / 2, 22, f"바깥 공기: 1㎡마다 약 {10 * k:.0f}톤", 54, YEL)
    if squash > 0.4:
        ctext(d, PCX, H - 84, "버틸 게 없으니 '와그작'", 56, RED)
    return img


# ---------- 3. 열어 두면 ----------
def vent(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    lid = ease(t / 0.5)
    tank_side(d, lid)
    # 공기가 들어오는 화살표
    if t > 0.4:
        for j in range(3):
            ph = (t * 1.6 + j / 3) % 1
            y = 120 + (TY0 + 80 - 120) * ph
            arrow(d, HATCH_X, y - 60, HATCH_X, y, BLUE, 12)
    # 안에도 공기 점
    fillk = ease((t - 0.6) / 1.0)
    rr = random.Random(5)
    for _ in range(int(60 * fillk)):
        x = rr.uniform(TX0 + 80, TX1 - 80); y = rr.uniform(TY0 + 40, TY1 - 40)
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=BLUE)
    ltext(d, 40, 30, "뚜껑·밸브를 열어 두면", 52)
    if t > 1.2:
        ltext(d, 40, 104, "안팎 공기가 같아져 멀쩡", 52, YEL)
    if t > 1.8:
        ctext(d, W / 2, H - 92, "그래서 탱크마다 '숨구멍' 밸브", 46, WHITE)
    return img


if __name__ == "__main__":
    run("steam", 3.2, steam)
    run("press", 3.0, press)
    run("vent", 2.8, vent)
    print("ok", OUT)
