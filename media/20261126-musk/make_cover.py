"""20261126-musk 표지 배경: 실제 트윗 캡처 카드를 오른쪽 위에 작게, 머스크 머리 뒤로(배경이 밝은 회색이라 밝기로 인물 가림판 만듦).
결과는 cand/cover_bg.jpg → manual 렌더가 제목을 얹는다."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFilter
D = Path(__file__).parent
src = ImageOps.fit(Image.open(D / "video/img1.jpg").convert("RGB"), (1080, 1350), Image.LANCZOS, centering=(.5, .05))
bg = src
a = np.asarray(bg).astype(float); lum = a.mean(2); sat = a.max(2) - a.min(2)
person = ((lum < 150) | (sat > 40)).astype(np.uint8) * 255
mask = Image.fromarray(person).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.5))
cap = Image.open(D / "cand/musk_cap_real.png").convert("RGB")
w = 440; cap = cap.resize((w, round(cap.height * w / cap.width)), Image.LANCZOS); h = cap.height
pad = 10; card = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
d.rounded_rectangle((0, 0, card.width - 1, card.height - 1), 18, fill=(0, 0, 0, 255), outline=(80, 80, 88, 255), width=2)
m = Image.new("L", cap.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 10, fill=255)
card.paste(cap, (pad, pad), m)
card = card.rotate(-4, expand=True, resample=Image.BICUBIC)
sh = Image.new("RGBA", (card.width + 60, card.height + 60), (0, 0, 0, 0)); sh.paste((0, 0, 0, 110), (30, 40), card.split()[3])
sh = sh.filter(ImageFilter.GaussianBlur(14))
x, y = 1080 - card.width - 24, 60
out = bg.convert("RGBA"); out.alpha_composite(sh, (x - 30, y - 30)); out.alpha_composite(card, (x, y))
# out = Image.composite(bg.convert("RGBA"), out, mask)  # 인물(머리)이 카드 위로
out.convert("RGB").save(D / "cand/cover_bg.jpg", quality=94)
mask.save(D / "cand/person_mask.png")
print("ok", x, y, card.size)
