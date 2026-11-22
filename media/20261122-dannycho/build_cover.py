"""표지 배경: 왼쪽 방시혁·과즙세연 베벌리힐스 동행 장면(2024.8 유튜브 'I am Walking' 영상 캡처) + 오른쪽 로스트파티3 대니초. 경계·아래는 부드럽게(fade)."""
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps
import numpy as np
D = Path(__file__).parent / "cand"; W, H, PH, PW, FADE = 1080, 1350, 1010, 620, 160
L = Image.open(D / "ref_scoop.png").convert("RGB").crop((0, 505, 590, 1520))
L = ImageOps.fit(L, (PW, PH), Image.LANCZOS, centering=(0.45, 0.4))
R = Image.open(D / "d7.5.jpg").convert("RGB").crop((150, 0, 150 + 354, 570))
R = ImageOps.fit(R, (PW, PH), Image.LANCZOS, centering=(0.5, 0.3)).filter(ImageFilter.UnsharpMask(2, 70, 2))
base = Image.new("RGB", (W, H), (10, 10, 12))
base.paste(R, (W - PW, 0))
# 왼쪽 사진 오른쪽 끝을 FADE px에 걸쳐 투명하게 → 오른쪽 사진과 섞임
a = np.full((PH, PW), 255, np.float32); x0 = PW - FADE
a[:, x0:] = np.linspace(255, 0, FADE)[None, :]
base.paste(L, (0, 0), Image.fromarray(a.astype(np.uint8)))
# 아래쪽으로 검게 페이드
arr = np.asarray(base).astype(np.float32); y0 = PH - 260
g = np.ones(H, np.float32); g[y0:PH] = np.linspace(1, 0, PH - y0); g[PH:] = 0
bg = np.array([10, 10, 12], np.float32)
arr = arr * g[:, None, None] + bg * (1 - g[:, None, None])
Image.fromarray(arr.clip(0, 255).astype(np.uint8)).save(D / "cover2.jpg", quality=94)
print("ok")
