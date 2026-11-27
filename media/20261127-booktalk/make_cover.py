"""20261127-booktalk 표지 배경: 인물 사진(밝은 배경 지우고 어두운 바탕) (책 카드 없음 — 다른 계정 동그라미 따라 하지 않음)."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
D = Path(__file__).parent
p = Image.open(D / "cand/lee_photo.jpg").convert("RGB"); a = np.asarray(p).astype(float)
bgc = np.median(np.concatenate([a[:40, :].reshape(-1, 3), a[:, :30].reshape(-1, 3), a[:, -30:].reshape(-1, 3)]), 0)
m = (np.sqrt(((a - bgc) ** 2).sum(2)) > 38).astype(np.uint8) * 255
mi = Image.fromarray(m).filter(ImageFilter.MedianFilter(7)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
W, H = 1080, 1350; k = 1.45; pw, ph = int(p.width * k), int(p.height * k)
ps = p.resize((pw, ph), Image.LANCZOS); ms = mi.resize((pw, ph), Image.LANCZOS)
cv = Image.new("RGB", (W, H), (14, 14, 16))
glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((-200, -150, 900, 800), fill=90); glow = glow.filter(ImageFilter.GaussianBlur(160))
cv = Image.composite(Image.new("RGB", (W, H), (58, 60, 66)), cv, glow)
cv.paste(ps, ((W - pw) // 2, -40), ms)
g = Image.new("L", (W, H), 0); d = ImageDraw.Draw(g)
for y in range(780, 1050): d.line((0, y, W, y), fill=int(255 * (y - 780) / 270))
for y in range(1050, H): d.line((0, y, W, y), fill=255)
cv = Image.composite(Image.new("RGB", (W, H), (12, 12, 14)), cv, g).convert("RGBA")
cv.convert("RGB").save(D / "cand/cover_bg.jpg", quality=94)
print("ok")
