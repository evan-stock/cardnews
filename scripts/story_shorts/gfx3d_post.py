"""오쓸 3D 그래픽 후처리: Blender 렌더 프레임(810x585 등) → 1080x780 확대 + 은은한 빛 번짐 + 이름표 페이드인 → mp4

사용:
  python3 scripts/story_shorts/gfx3d_post.py --src <프레임 폴더> --out media/<id>/gfx/<이름>.mp4 \
      --labels '[["지하 고압수", 40, 30, 526, "#8ce4ff", 70], ["자갈층", 30, 30, 300, "#ffffff", 62]]'
  이름표 = [글자, 글자 크기, 왼쪽 x, 중앙 y(1080x780 기준), 글자색, 나타나기 시작하는 프레임]
  프레임 파일 이름은 f000.png, f001.png … (anim3d_*.py 가 이렇게 저장)
"""
import argparse, json, os, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--labels", default="[]")
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--glow", type=float, default=0.5, help="빛 번짐 세기(0 = 끔)")
args = ap.parse_args()

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"  # index=1 = KR
labels = json.loads(args.labels)
fonts = {}
def font(sz):
    if sz not in fonts:
        fonts[sz] = ImageFont.truetype(FONT, sz, index=1)
    return fonts[sz]

def hexrgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def pill(im, text, f, x, yc, color, alpha):
    if alpha <= 0:
        return im
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    w, h = r - l, b - t
    px, py = 18, 10
    d.rounded_rectangle((x, yc - h / 2 - py, x + w + 2 * px, yc + h / 2 + py), radius=12,
                        fill=(10, 12, 24, int(200 * alpha)))
    d.text((x + px - l, yc - h / 2 - t), text, font=f, fill=(*color, int(255 * alpha)))
    return Image.alpha_composite(im, layer)

tmp = tempfile.mkdtemp(prefix="gfx3d_")
frames = sorted(p for p in os.listdir(args.src) if p.endswith(".png"))
for n, p in enumerate(frames):
    fr = int(p[1:4])
    im = Image.open(os.path.join(args.src, p)).convert("RGB").resize((1080, 780), Image.LANCZOS)
    if args.glow:
        bright = im.point(lambda v: max(0, v - 215) * 5).filter(ImageFilter.GaussianBlur(14))
        im = Image.fromarray(np.clip(np.asarray(im, dtype="int16")
                                     + np.asarray(bright, dtype="int16") * args.glow, 0, 255).astype("uint8"))
    im = im.convert("RGBA")
    for text, sz, x, y, col, st in labels:
        im = pill(im, text, font(sz), x, y, hexrgb(col), min(max((fr - st) / 6, 0), 1))
    im.convert("RGB").save(os.path.join(tmp, f"f{n:03d}.png"))

os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(args.fps), "-i", f"{tmp}/f%03d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "veryfast", "-g", "15",
                "-an", args.out], check=True)
print("ok", args.out)
