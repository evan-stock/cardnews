"""20261123-yeoui: 여의도의 현인 팻말 짤 + 삼전닉스 급락(11.23). 팻말 든 사람 얼굴 모자이크."""
from pathlib import Path
from PIL import Image, ImageOps
O = Path(__file__).parent / "cand"
im = Image.open(O / "meme.jpg").convert("RGB")
b = (755, 790, 905, 985); r = im.crop(b); w, h = r.size
im.paste(r.resize((w // 14, h // 14), Image.NEAREST).resize((w, h), Image.NEAREST), b[:2])
im.save(O / "meme_m.jpg", quality=95)
ImageOps.fit(im, (1080, 1350), Image.LANCZOS, centering=(.49, .4)).save(O / "cover_bg.jpg", quality=95)
im.crop((640, 240, 1060, 800)).save(O / "sign.jpg", quality=95)
print("ok")
