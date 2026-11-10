#!/usr/bin/env python3
"""얼어붙는 비눗방울 '스노글로브 효과' 모션그래픽(실사 먼저 → 그래픽 설명 구성용, 카드 영상 칸 1080x780) — 2026.11.10 오늘의쓸모.
  python3 scripts/story_shorts/anim_bubble.py <출력폴더>
  → start.mp4 (눈에 닿은 바닥부터 얼기 시작 → 얼 때 나온 열로 바닥 -6℃ · 꼭대기 -20℃)
    flow.mp4  (온도 차이로 막 속 물이 바닥→꼭대기로 흐름(마랑고니) → 떨어진 얼음 조각이 실려 돎 = 스노글로브)
근거: Ahmadi, Nath, Kingett, Yue, Boreyko 'How soap bubbles freeze', Nature Communications 10, 2531 (2019, 버지니아공대),
      Virginia Tech 보도자료(ScienceDaily 2019.06.22), Physics Today 2019.06.20
      (얼음 바닥 위 -20℃ 냉동실 실험: 접촉선부터 얼기 시작, 잠열로 바닥 약 -6℃·꼭대기 -20℃ 약 14℃ 차이,
       뜨거운 쪽→차가운 쪽 마랑고니 흐름이 얼음 결정을 떼어 내 실어 나름, 결정마다 새 어는 점이 되어 더 빨리 언다).
"""
import subprocess, sys, os, math
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 780, 30
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F = lambda s: ImageFont.truetype(FB, s)
WHITE = (250, 250, 252); YEL = (255, 205, 40); DARK = (30, 34, 44)
WARM = (255, 140, 60); COLD = (90, 170, 255)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3
clamp = lambda t: max(0.0, min(1.0, t))

CX, R = 540, 215
GY = 640                     # 눈 바닥 높이
CY = GY - R + 18             # 방울 중심(바닥에 살짝 눌려 앉음)


def bg():
    img = Image.new("RGB", (W, H), (16, 24, 42)); d = ImageDraw.Draw(img)
    for y in range(GY, H):   # 눈 바닥
        c = 225 - (y - GY) // 3
        d.line((0, y, W, y), fill=(c, c + 4, c + 12))
    for k in range(40):      # 눈 알갱이
        x = (k * 137) % W; y = GY + 8 + (k * 53) % (H - GY - 12)
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 255, 255))
    return img


def run(name, dur, base, draw):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-g", "15", os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        img = base.copy()
        draw(img, i / FPS)
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close(); p.wait()


def ctext(d, cx, y, s, size, fill=WHITE, stroke=5):
    ft = F(size); w = d.textlength(s, font=ft)
    d.text((cx - w / 2, y), s, font=ft, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def lerp(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def bubble(img, ice_h, tint=0.0):
    """방울 그리기. ice_h = 바닥에서부터 언 높이(px). tint>0 이면 테두리를 바닥 주황 → 꼭대기 파랑으로."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.ellipse((CX - R, CY - R, CX + R, CY + R), fill=(170, 210, 255, 40))
    # 언 부분(바닥부터)
    if ice_h > 0:
        top = CY + R - ice_h
        mask = Image.new("L", (W, H), 0); md = ImageDraw.Draw(mask)
        md.ellipse((CX - R, CY - R, CX + R, CY + R), fill=255)
        md.rectangle((0, 0, W, top), fill=0)
        ice = Image.new("RGBA", (W, H), (235, 245, 255, 215))
        ov.paste(ice, (0, 0), mask)
        d = ImageDraw.Draw(ov)
        # 결정 무늬
        for k in range(14):
            a = math.pi * (0.1 + 0.8 * k / 13)
            x = CX - R * 0.9 * math.cos(a); y = CY + R - 6 - (k * 37) % max(8, int(ice_h - 4))
            if y > top + 6:
                star(d, x, y, 9, (160, 190, 225, 255), 2)
    # 테두리(막)
    for k in range(72):
        a0 = 2 * math.pi * k / 72; a1 = 2 * math.pi * (k + 1) / 72
        yk = (math.sin((a0 + a1) / 2) + 1) / 2          # 0=꼭대기 1=바닥
        col = lerp(COLD, WARM, yk) if tint > 0 else (210, 230, 255)
        col = lerp((210, 230, 255), col, tint) if tint > 0 else col
        d.arc((CX - R, CY - R, CX + R, CY + R), math.degrees(a0), math.degrees(a1) + 0.5, fill=col + (255,), width=9)
    # 반짝임
    d.arc((CX - R + 40, CY - R + 40, CX + R - 40, CY + R - 40), 200, 245, fill=(255, 255, 255, 200), width=8)
    img.paste(ov, (0, 0), ov)


def star(d, x, y, r, col, w=3):
    for k in range(3):
        a = math.pi / 3 * k
        d.line((x - r * math.cos(a), y - r * math.sin(a), x + r * math.cos(a), y + r * math.sin(a)), fill=col, width=w)


def ring_pt(a, rr=R - 4):
    return CX + rr * math.cos(a), CY + rr * math.sin(a)


# ① 바닥부터 얼고, 얼 때 나온 열로 바닥이 따뜻해짐
def start(img, t):
    ice = 70 * ease((t - 0.3) / 1.6)
    tint = ease((t - 2.4) / 0.6)
    bubble(img, ice, tint)
    d = ImageDraw.Draw(img)
    ctext(d, 540, 26, "영하 20℃ 공기 · 얼음 바닥 위 비눗방울", 44)
    if t < 2.4:
        a = clamp((t - 0.2) / 0.4)
        if a > 0:
            for sx in (-1, 1):   # 접촉선 화살표
                x = CX + sx * (R * 0.62); y = GY - 18
                d.line((x + sx * 150, y + 40, x + sx * 20, y + 4), fill=YEL, width=8)
                d.polygon([(x + sx * 4, y), (x + sx * 40, y - 6), (x + sx * 30, y + 26)], fill=YEL)
            ctext(d, 540, 104, "눈에 닿은 바닥부터 얼기 시작", 46, fill=YEL)
    else:
        # 얼음 줄에서 올라오는 열(물결선)
        for k in range(5):
            x0 = CX - 140 + k * 70
            ph = (t * 1.6 + k * 0.3) % 1.0
            y0 = CY + R - 80 - ph * 120
            pts = [(x0 + 10 * math.sin((y0 - j * 6) / 9 + t * 6), y0 - j * 6) for j in range(10)]
            d.line(pts, fill=WARM + (0,) if False else WARM, width=5)
        ctext(d, 540, 104, "얼 때 나온 열로 바닥이 데워진다", 46, fill=WARM)
        a = ease((t - 2.8) / 0.5)
        if a > 0:
            # 온도 딱지
            d.rounded_rectangle((CX + R + 20, CY - R + 10, CX + R + 230, CY - R + 92), 16, fill=COLD)
            ctext(d, CX + R + 125, CY - R + 18, "-20℃", 54, fill=WHITE, stroke=3)
            d.rounded_rectangle((CX + R + 20, CY + R - 150, CX + R + 230, CY + R - 68), 16, fill=WARM)
            ctext(d, CX + R + 125, CY + R - 142, "-6℃", 54, fill=WHITE, stroke=3)
            ctext(d, CX - R - 120, CY - 30, "약 14℃", 50, fill=YEL)
            ctext(d, CX - R - 120, CY + 30, "차이", 50, fill=YEL)


# ② 온도 차이 → 막 속 물이 위로 흐르며 얼음 조각을 싣고 돎
def flow(img, t):
    bubble(img, 70, 1.0)
    d = ImageDraw.Draw(img)
    # 흐름: 바닥(따뜻) → 꼭대기(차가움)로 막을 따라 올라가는 점·화살표
    for side in (-1, 1):
        for k in range(7):
            ph = (t * 0.45 + k / 7) % 1.0
            a = math.pi / 2 + side * (0.55 + ph * (math.pi - 0.75))   # 바닥 옆 → 꼭대기
            x, y = ring_pt(a, R - 22)
            ang = a + side * math.pi / 2
            dx, dy = math.cos(ang) * 18, math.sin(ang) * 18
            d.polygon([(x + dx, y + dy), (x - dx * 0.6 - dy * 0.7, y - dy * 0.6 + dx * 0.7),
                       (x - dx * 0.6 + dy * 0.7, y - dy * 0.6 - dx * 0.7)], fill=YEL)
    if t < 2.4:
        ctext(d, 540, 26, "따뜻한 바닥 → 차가운 꼭대기로", 46, fill=YEL)
        ctext(d, 540, 96, "막 속 물이 끌려 올라간다", 46)
    else:
        ctext(d, 540, 26, "얼음 조각이 실려 빙글빙글", 46, fill=YEL)
        ctext(d, 540, 96, "= '스노글로브' 효과", 46)
    # 얼음 조각: 2.0초부터 얼음 줄에서 떨어져 흐름을 타고 돎
    n = int(clamp((t - 1.8) / 2.6) * 22)
    for k in range(n):
        born = 1.8 + k * (2.6 / 22)
        age = t - born
        side = -1 if k % 2 else 1
        ph = (age * 0.32 + (k % 5) * 0.03)
        a = math.pi / 2 + side * (0.6 + min(ph, 1.0) * (math.pi - 0.8))
        rr = R - 40 - (k * 23) % 120 * min(1, age)
        x, y = ring_pt(a, rr)
        x += 8 * math.sin(age * 3 + k)
        star(d, x, y, 9 + k % 4 * 2, (255, 255, 255), 4)
    ctext(d, 540, 718, "2019 미국 버지니아공대 · Nature Communications", 34, fill=(220, 225, 235), stroke=4)


if __name__ == "__main__":
    B = bg()
    run("start", 5.0, B, start)
    run("flow", 5.0, B, flow)
    print("ok", OUT)
