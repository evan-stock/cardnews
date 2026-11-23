"""20261123-zico 2장 영상에 해설 자막(시간별 PNG 오버레이) — 02.mp4 다시 만듦."""
import re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).parent; R = D.parents[1]
W, H = 1080, 1350; YE = (255, 216, 77)
F = ImageFont.truetype(str(R / "assets/fonts/Pretendard-Black.otf"), 64)
SUBS = [  # 릴스 양식(왼쪽 정렬·Pretendard Black·마지막 줄 노랑·위에 로고), 4:5에 맞춰 축소
    (0.0, 3.1, "엑셀방송 대부\n커맨더지코 오열"),
    (3.1, 6.2, "200억 주식 -90%\n직원 월급도 밀려"),
    (6.2, 9.3, "누리꾼 반응\n\"울어도 또 벌겠지\""),
    (9.3, 12.4, "누리꾼 반응\n\"내가 더 걱정이다\""),
]
FS, LG, X, BASE = 92, 110, 60, 1250
LOGO = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); _lh = 36
LOGO = LOGO.resize((int(LOGO.width * _lh / LOGO.height), _lh), Image.LANCZOS)


def sub_png(text, out):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    g0, g1 = 760, 1100
    for y in range(g0, H):
        d.line((0, y, W, y), fill=(0, 0, 0, int(215 * min(1, (y - g0) / (g1 - g0)))))
    f = ImageFont.truetype(str(R / "assets/fonts/Pretendard-Black.otf"), FS)
    lines = text.split("\n"); y = BASE - (len(lines) - 1) * LG
    im.alpha_composite(LOGO, (X, y - FS - 26 - _lh))
    for k, ln in enumerate(lines):
        d.text((X, y + k * LG), ln, font=f, fill=YE if k == len(lines) - 1 else (255, 255, 255), anchor="ls")
    im.save(out)


inputs, chain, prev = [], "", "[0:v]"
for k, (a, b, t) in enumerate(SUBS):
    p = D / f"sub{k}.png"; sub_png(t, p); inputs += ["-i", str(p)]
    nxt = f"[v{k}]"
    chain += f"{prev}[{k + 1}:v]overlay=0:0:enable='between(t,{a},{b})'{nxt};"; prev = nxt
src = D / "02_raw.mp4"
if not src.exists():
    (D / "02.mp4").rename(src)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), *inputs, "-filter_complex", chain.rstrip(";"),
                "-map", prev, "-map", "0:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "copy",
                "-movflags", "+faststart", str(D / "02.mp4")], check=True)
print("ok")
