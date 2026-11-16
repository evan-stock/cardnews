# 댓글로 키우는 아이 — 블록(복셀) 캐릭터 시안 (2026.10.23). 코드로 쌓은 블록을 비스듬히 그려 입체감을 낸다.
# 사용: python3 scripts/story_shorts/life_voxel.py <출력폴더>
import os, sys
from PIL import Image, ImageDraw, ImageFont

def shade(c, k): return tuple(max(0, min(255, int(v * k))) for v in c)

SKIN = (255, 214, 182); SKIN2 = (246, 194, 160); HAIR = (70, 48, 36); EYE = (40, 30, 30); WHITE = (255, 255, 255)
BLUSH = (255, 150, 160); MOUTH = (170, 60, 70); MINT = (140, 215, 190); MINT2 = (110, 190, 165)
YEL = (255, 205, 70); ORG = (255, 150, 60); JEAN = (80, 120, 200); NAVY = (55, 75, 130); RED = (225, 60, 80)
TEAR = (120, 200, 255)

class Model:
    def __init__(self): self.v = {}
    def box(self, x, y, d, w, h, dd, col):
        for i in range(w):
            for j in range(h):
                for k in range(dd): self.v[(x + i, y + j, d + k)] = col
    def px(self, x, y, d, col): self.v[(x, y, d)] = col

def head(m, x0, y0, expr="happy"):
    W, H, D = 10, 9, 8
    m.box(x0, y0, 0, W, H, D, SKIN)
    m.box(x0, y0 + H - 2, 0, W, 2, D, HAIR)           # 정수리 머리
    m.box(x0, y0 + 5, 1, 1, 2, D - 1, HAIR); m.box(x0 + W - 1, y0 + 5, 1, 1, 2, D - 1, HAIR)
    for i in (1, 2, 3, 6, 7, 8): m.px(x0 + i, y0 + H - 3, 0, HAIR)  # 앞머리 들쭉날쭉
    # 머리 한 가닥(트레이드마크): 위로 솟아 휘어진 블록
    for dx, dy in ((5, 0), (5, 1), (6, 2), (7, 2), (7, 1)): m.px(x0 + dx, y0 + H + dy, 3, HAIR)
    ex = (x0 + 2, x0 + 6); ey = y0 + 3
    if expr == "cry":
        for x in ex:
            m.px(x, ey + 1, 0, EYE); m.px(x + 1, ey, 0, EYE)
            m.px(x, ey - 1, 0, TEAR); m.px(x, ey - 2, 0, TEAR)
        m.box(x0 + 4, y0 + 1, 0, 2, 2, 1, MOUTH)
    else:
        for x in ex:
            m.box(x, ey, 0, 2, 2, 1, EYE); m.px(x, ey + 1, 0, WHITE)
        m.px(x0 + 4, y0 + 1, 0, MOUTH); m.px(x0 + 5, y0 + 1, 0, MOUTH)
    m.px(x0 + 1, y0 + 2, 0, BLUSH); m.px(x0 + 8, y0 + 2, 0, BLUSH)

def baby(expr="happy"):
    m = Model(); m.box(0, 0, 1, 10, 7, 6, MINT)
    for i in range(10): m.px(i, 5, 1, MINT2)
    m.box(3, 2, 0, 1, 1, 1, SKIN); m.box(6, 2, 0, 1, 1, 1, SKIN)  # 손
    head(m, 0, 7, expr); return m

def kid(expr="happy"):
    m = Model()
    m.box(2, 0, 2, 2, 5, 3, JEAN); m.box(6, 0, 2, 2, 5, 3, JEAN)
    m.box(1, 5, 2, 8, 7, 4, YEL)
    for i in range(8): m.px(1 + i, 8, 2, ORG)
    m.box(-2, 6, 2, 3, 6, 3, YEL); m.box(9, 6, 2, 3, 6, 3, YEL)
    m.box(-2, 4, 2, 3, 2, 3, SKIN); m.box(9, 4, 2, 3, 2, 3, SKIN)
    m.box(2, 5, 1, 1, 7, 1, (80, 140, 240)); m.box(7, 5, 1, 1, 7, 1, (80, 140, 240))  # 책가방 끈
    head(m, 0, 12, expr); return m

def adult(expr="happy"):
    m = Model()
    m.box(2, 0, 2, 2, 8, 3, (45, 50, 70)); m.box(6, 0, 2, 2, 8, 3, (45, 50, 70))
    m.box(1, 8, 2, 8, 9, 4, NAVY)
    m.box(4, 13, 1, 2, 4, 1, WHITE); m.box(4, 10, 0, 2, 6, 1, RED)
    m.box(-2, 9, 2, 3, 8, 3, NAVY); m.box(9, 9, 2, 3, 8, 3, NAVY)
    m.box(-2, 7, 2, 3, 2, 3, SKIN); m.box(9, 7, 2, 3, 2, 3, SKIN)
    head(m, 0, 17, expr); return m

def render(m, s=24, flat=False, edge=True):
    xs = [k[0] for k in m.v]; ys = [k[1] for k in m.v]; ds = [k[2] for k in m.v]
    ox, oy = 0.5 * s, 0.38 * s  # 깊이 1칸 = 오른쪽 위로
    if flat: ox = oy = 0
    minx, maxx = min(xs) * s, (max(xs) + 1) * s + max(ds) * ox + s
    maxy = (max(ys) + 1) * s + max(ds) * oy + s
    Wd, Hd = int(maxx - minx + 2 * s), int(maxy + 2 * s)
    im = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def P(x, y, k): return (x * s - minx + s + k * ox, Hd - s - y * s - k * oy)
    order = sorted(m.v, key=lambda p: (-p[2], p[1], p[0]))
    line = (60, 40, 30, 90) if edge else None
    for (x, y, k) in order:
        c = m.v[(x, y, k)]
        if not flat: c = shade(c, 1 + (((x * 73856093) ^ (y * 19349663) ^ (k * 83492791)) % 9 - 4) / 100)  # 블록 질감
        if flat:
            if (x, y, k - 1) in m.v: continue
        else:
            if (x, y + 1, k) not in m.v:  # 윗면
                d.polygon([P(x, y + 1, k), P(x + 1, y + 1, k), P(x + 1, y + 1, k + 1), P(x, y + 1, k + 1)], fill=shade(c, 1.12), outline=line)
            if (x + 1, y, k) not in m.v:  # 오른면
                d.polygon([P(x + 1, y, k), P(x + 1, y, k + 1), P(x + 1, y + 1, k + 1), P(x + 1, y + 1, k)], fill=shade(c, 0.78), outline=line)
        if (x, y, k - 1) not in m.v:  # 앞면
            d.polygon([P(x, y, k), P(x + 1, y, k), P(x + 1, y + 1, k), P(x, y + 1, k)], fill=c, outline=line)
    return im.crop(im.getbbox())

def main(out):
    os.makedirs(out, exist_ok=True)
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    F = lambda n: ImageFont.truetype(os.path.join(root, "assets/fonts/Jua-Regular.ttf"), n)
    rows = [("E안 블록 3D (비스듬히)", False), ("F안 픽셀 2D (정면 도트)", True)]
    cols = [("아기", baby, "happy"), ("초등학생", kid, "happy"), ("어른", adult, "happy"), ("울 때", baby, "cry")]
    cw, ch = 320, 560
    sheet = Image.new("RGB", (60 + 4 * cw, 110 + len(rows) * (ch + 90)), (232, 242, 250)); d = ImageDraw.Draw(sheet)
    for j, (lab, _, _) in enumerate(cols): d.text((60 + j * cw + cw / 2, 60), lab, font=F(40), fill=(90, 100, 120), anchor="mm")
    for i, (name, flat) in enumerate(rows):
        y0 = 100 + i * (ch + 90)
        d.text((30, y0 + 25), name, font=F(56), fill=(40, 50, 80), anchor="lm")
        for j, (_, fn, e) in enumerate(cols):
            im = render(fn(e), s=22, flat=flat, edge=False)
            im.thumbnail((cw - 30, ch - 60), Image.NEAREST if flat else Image.LANCZOS)
            sheet.paste(im, (int(60 + j * cw + (cw - im.width) / 2), int(y0 + 70 + (ch - 60 - im.height))), im)
    sheet.save(f"{out}/voxel_options.png")

if __name__ == "__main__":
    main(sys.argv[1])
