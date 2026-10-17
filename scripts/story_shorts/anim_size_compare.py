#!/usr/bin/env python3
"""크기 비교 그래픽(카드 영상 칸 1080x780): 배경 사진 위에 기준 물체(지구 등)가 하나씩 나타나며 '몇 개 들어가는지' 보여준다.
  python3 anim_size_compare.py <배경.gif|jpg> <비교물.jpg> <출력.mp4> --span 0.80 --ratio 2.35 --label "약 30,000km" --count "지구 2개+"
  span  = 배경(칸 높이에 맞춘 정사각 이미지) 폭 대비 대상 지름 비율, ratio = 대상 지름 / 비교물 지름
"""
import argparse, math, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H, FPS, DUR = 1080, 780, 30, 4.5
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
YEL, WHT = (255, 216, 77), (255, 255, 255)
ease = lambda t: 0 if t <= 0 else 1 if t >= 1 else 1 - (1 - t) ** 3

ap = argparse.ArgumentParser()
ap.add_argument("bg"); ap.add_argument("obj"); ap.add_argument("out")
ap.add_argument("--span", type=float, default=0.8); ap.add_argument("--ratio", type=float, default=2.35)
ap.add_argument("--crop", type=float, default=1.0, help="비교물 사진에서 물체만 남기는 가운데 비율(예: 지구 사진 0.86)")
ap.add_argument("--label", default=""); ap.add_argument("--count", default="")
a = ap.parse_args()

bg = Image.open(a.bg).convert("RGB")
side = H
bgf = bg.resize((side, side), Image.LANCZOS)
base = Image.new("RGB", (W, H), (0, 0, 0)); x0 = (W - side) // 2; base.paste(bgf, (x0, 0))
base = Image.blend(base, Image.new("RGB", (W, H), (0, 0, 0)), 0.25)
span_px = side * a.span; cx, cy = W // 2, H // 2
d_obj = span_px / a.ratio
obj = Image.open(a.obj).convert("RGB")
s = int(min(obj.size) * a.crop); obj = ImageOps.fit(obj, (s, s), centering=(0.5, 0.5)).resize((int(d_obj), int(d_obj)), Image.LANCZOS)
m = Image.new("L", obj.size, 0); ImageDraw.Draw(m).ellipse([0, 0, obj.size[0] - 1, obj.size[1] - 1], fill=255)
n_full = int(a.ratio)
left = cx - span_px / 2
f = lambda sz: ImageFont.truetype(FB, sz, index=1)
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                      "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
for i in range(int(FPS * DUR)):
    t = i / FPS
    im = base.copy(); d = ImageDraw.Draw(im)
    g = ease((t - 0.2) / 0.8)  # 지름 선이 그려짐
    y = cy
    if g > 0:
        d.line([(left, y), (left + span_px * g, y)], fill=YEL, width=6)
        for xx in (left, left + span_px * g):
            d.line([(xx, y - 18), (xx, y + 18)], fill=YEL, width=6)
    if a.label and g > 0.6:
        lf = f(52); tw = d.textlength(a.label, font=lf)
        d.text((cx - tw / 2, y - 95), a.label, font=lf, fill=YEL, stroke_width=5, stroke_fill=(0, 0, 0))
    for k in range(n_full):  # 비교물이 하나씩 '톡' 나타남
        st = 1.3 + k * 0.6; e = ease((t - st) / 0.35)
        if e <= 0: continue
        sz = max(2, int(d_obj * (0.6 + 0.4 * e)))
        o = obj.resize((sz, sz)); mm = m.resize((sz, sz)).point(lambda v: int(v * e))
        ox = int(left + d_obj * k + (d_obj - sz) / 2); oy = int(y + 40 + (d_obj - sz) / 2)
        im.paste(o, (ox, oy), mm)
    if a.count and t > 1.3 + n_full * 0.6:
        e = ease((t - (1.3 + n_full * 0.6)) / 0.4); cf = f(int(70 * (0.7 + 0.3 * e)))
        tw = d.textlength(a.count, font=cf)
        d.text((cx - tw / 2, 40), a.count, font=cf, fill=WHT, stroke_width=6, stroke_fill=(0, 0, 0))
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait()
print("done", a.out)
