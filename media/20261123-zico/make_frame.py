"""20261123-zico 2장: 카드뉴스 검은 틀(frame) 안에 영상(원본 소리) + 아래 문구가 시간별로 바뀜."""
import re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).parent; R = D.parents[1]
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255); BG = (10, 10, 12)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
VW = 940; VH = round(560 * VW / 820); VX = (W - VW) // 2; VY = 300  # 원본에서 인물 중심 820x560 잘라 확대
SUBS = [  # (시작, 끝, 노란 줄, 회색 줄)
    (0.0, 3.1, "아이온큐에 넣은 '200억'", "마이너스 90% 안팎 손실(스포츠서울)"),
    (3.1, 6.2, "'50억' 대출에 직원 월급까지 밀렸다", "\"진짜 이번엔 내가 너무 힘들다\""),
    (6.2, 9.3, "누리꾼 반응 \"울어도 '또' 벌겠지\"", "7년 전 '일반인 비하' 논란도 다시 소환"),
    (9.3, 12.4, "누리꾼 반응 \"내가 더 '걱정'이다\"", "SOOP 방송 화면(11.22)"),
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
rich_center(d, 168, "엑셀방송 대부 커맨더지코", F("Medium", 46), FG)
rich_center(d, 236, "방송 중 결국 '오열'", F("Black", 54), FG)
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

src = D / "video/src.mp4"
inputs = ["-loop", "1", "-i", str(D / "frame_bg.png"), "-i", str(src), "-i", str(D / "frame_corner.png")]
chain = f"[1:v]crop=820:560:220:0,scale={VW}:{VH}:flags=lanczos,unsharp=5:5:0.6[v];[0:v][v]overlay={VX}:{VY}:shortest=1[a];[a][2:v]overlay=0:0[b]"
prev = "[b]"
for k, (a, b, _, _) in enumerate(SUBS):
    inputs += ["-i", str(D / f"fsub{k}.png")]
    chain += f";{prev}[{k + 3}:v]overlay=0:0:enable='between(t,{a},{b})'[s{k}]"; prev = f"[s{k}]"
chain += f";{prev}fps=30,format=yuv420p[o]"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", chain, "-map", "[o]", "-map", "1:a",
                "-t", "12.4", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                str(D / "02.mp4")], check=True)
print("ok")
