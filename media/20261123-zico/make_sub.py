"""20261123-zico 2장 영상에 해설 자막(시간별 PNG 오버레이) — 02.mp4 다시 만듦."""
import re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).parent; R = D.parents[1]
W, H = 1080, 1350; YE = (255, 216, 77)
F = ImageFont.truetype(str(R / "assets/fonts/Pretendard-Black.otf"), 64)
SUBS = [  # (시작, 끝, 두 줄)
    (0.0, 3.0, "엑셀방송 대부 커맨더지코\n방송 중 결국 '오열'"),
    (3.0, 6.2, "아이온큐에 넣은 '200억'\n마이너스 90%"),
    (6.2, 9.4, "'50억' 대출에\n직원 월급까지 밀렸다"),
    (9.4, 12.4, "\"진짜 이번엔\n내가 너무 힘들다\""),
]


def sub_png(text, out):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # 아래쪽 은은한 그라데이션
    for y in range(900, H):
        a = int(200 * (y - 900) / (H - 900)); d.line((0, y, W, y), fill=(0, 0, 0, a))
    lines = text.split("\n"); y = H - 120 - 84 * (len(lines) - 1)
    for ln in lines:
        parts = re.split(r"('[^']*')", ln); tw = sum(d.textlength(p.strip("'"), font=F) for p in parts if p)
        x = (W - tw) / 2
        for p in parts:
            if not p: continue
            hl = p.startswith("'"); p = p.strip("'")
            d.text((x, y), p, font=F, fill=YE if hl else (255, 255, 255), anchor="ls", stroke_width=6, stroke_fill=(0, 0, 0))
            x += d.textlength(p, font=F)
        y += 84
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
