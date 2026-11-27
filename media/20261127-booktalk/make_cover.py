"""20261127-booktalk 표지: 중앙일보 11.17 자택 앞 사진(video/img1.jpg)을 rembg(u2net_human_seg)로 누끼 → 어두운 바탕 가운데."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
D = Path(__file__).parent
cut = Image.open(D / "cand/lee_cut.png").convert("RGBA"); cut = cut.crop(cut.getbbox())
W, H = 1080, 1350
bg = Image.new("RGB", (W, H), (10, 10, 12))
glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((90, -100, 990, 800), fill=110); glow = glow.filter(ImageFilter.GaussianBlur(170))
bg = Image.composite(Image.new("RGB", (W, H), (62, 64, 72)), bg, glow).convert("RGBA")
k = 1450 / cut.height; cut = cut.resize((round(cut.width * k), round(cut.height * k)), Image.LANCZOS)
face_cx = int(cut.width * 0.62)  # 얼굴 가운데(누끼 기준)
bg.alpha_composite(cut, (W // 2 - face_cx, 60))
g = Image.new("L", (W, H), 0); d = ImageDraw.Draw(g)
for y in range(820, 1060): d.line((0, y, W, y), fill=int(255 * (y - 820) / 240))
for y in range(1060, H): d.line((0, y, W, y), fill=255)
Image.composite(Image.new("RGB", (W, H), (10, 10, 12)), bg.convert("RGB"), g).save(D / "cand/cover_bg.jpg", quality=95)
print("ok")
