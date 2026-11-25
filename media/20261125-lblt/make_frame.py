"""20261125-lblt 2장(서울경제TV 생방송, 채널 띠 잘라냄): 카드뉴스 검은 틀(frame) 안에 영상(원본 소리) + 아래 문구가 시간별로 바뀜."""
import re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).parent; R = D.parents[1]
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255); BG = (10, 10, 12)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
VW = 940; VH = round(740 * VW / 1220); VX = (W - VW) // 2; VY = 300
SUBS = [
    (0.0, 6.6, "\"나스닥, 추가로 더 '빠질' 수 있다\"", "나스닥 차트를 짚으며"),
    (6.6, 10.3, "\"굉장히 '힘든' 시장인데…\"", "\"잘 이겨나가셔야 되고\""),
    (10.3, 16.8, "그리고 말을 '잇지 못했다'", "삼성전자 레버리지 차트 앞에서 · 서울경제TV"),
]


def rich_center(d, y, text, font, base):
    parts = re.split(r"('[^']*')", text); tw = sum(d.textlength(p.strip("'"), font=font) for p in parts if p)
    x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=font)


# 바탕: 검은 틀 + 위 두 줄 + 로고, 영상 자리 비움
bg = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(bg)
rich_center(d, 168, "주식 시황 생방송 도중", F("Medium", 46), FG)
rich_center(d, 236, "진행자가 '울컥'", F("Black", 54), FG)
lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
lg = lg.resize((lw, lh), Image.LANCZOS); bg.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)
bg.save(D / "frame_bg.png")
# 둥근 모서리 가림판(영상 위에 얹음)
cm = Image.new("RGBA", (W, H), (0, 0, 0, 0)); m = Image.new("L", (VW, VH), 255)
ImageDraw.Draw(m).rounded_rectangle((0, 0, VW - 1, VH - 1), 18, fill=0)
cm.paste(Image.new("RGBA", (VW, VH), BG + (255,)), (VX, VY), m); cm.save(D / "frame_corner.png")
# 시간별 아래 문구
y0 = VY + VH + 92
for k, (_, _, a, b) in enumerate(SUBS):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
    rich_center(dd, y0, a, F("Black", 46), YE); rich_center(dd, y0 + 62, b, F("Medium", 32), (190, 190, 198))
    im.save(D / f"fsub{k}.png")

src = D / "video/v1.mp4"
inputs = ["-loop", "1", "-i", str(D / "frame_bg.png"), "-i", str(src), "-i", str(D / "frame_corner.png")]
chain = f"[1:v]crop=1220:740:700:60,scale={VW}:{VH}:flags=lanczos,unsharp=5:5:0.6[v];[0:v][v]overlay={VX}:{VY}:shortest=1[a];[a][2:v]overlay=0:0[b]"
prev = "[b]"
for k, (a, b, _, _) in enumerate(SUBS):
    inputs += ["-i", str(D / f"fsub{k}.png")]
    chain += f";{prev}[{k + 3}:v]overlay=0:0:enable='between(t,{a},{b})'[s{k}]"; prev = f"[s{k}]"
chain += f";{prev}fps=30,format=yuv420p[o]"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", chain, "-map", "[o]", "-map", "1:a",
                "-t", "16.7", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                str(D / "02.mp4")], check=True)
print("ok")
