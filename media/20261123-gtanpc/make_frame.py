"""20261123-gtanpc 2장(IGN 영상, 원본 자막·제목 잘라냄): 카드뉴스 검은 틀(frame) 안에 영상(원본 소리) + 아래 문구가 시간별로 바뀜."""
import re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

D = Path(__file__).parent; R = D.parents[1]
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255); BG = (10, 10, 12)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
VW = 940; VH = round(880 * VW / 1206); VX = (W - VW) // 2; VY = 300
SUBS = [
    (0.0, 5.0, "차고 문을 따고 들어가 보니", "GTA6 '레오니다' 한 주택가 집"),
    (5.0, 9.0, "\"IT’S A SIMULATION\" '음모론 게시판'", "여긴 가짜 세상이다"),
    (9.0, 15.0, "\"모르는 사람들이 '똑같이' 생겼다\"", "벽을 뚫고 지나가는 사람도 봤다"),
    (15.0, 19.0, "\"차들이 '사라진다', 아이들이 '없다'\"", "게임 속 그 현상들"),
    (19.0, 21.5, "\"왜 레오니다를 '못 떠나지'?\"", "게임 무대 밖으론 못 나간다"),
    (21.5, 25.0, "\"J와 L만 '자유'로운 존재\"", "주인공 제이슨·루시아"),
    (25.0, 30.0, "\"요즘 범죄가 '급증'했다\"", "플레이어가 게임을 시작했으니까"),
    (30.0, 33.0, "\"우리, 게임 속에 있는 거야?\"", "영상: IGN"),
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
rich_center(d, 168, "실제로 들어가 본 그 집", F("Medium", 46), FG)
rich_center(d, 236, "차고 속 '음모론 게시판'", F("Black", 54), FG)
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

src = D / "video/ign.mp4"
inputs = ["-loop", "1", "-i", str(D / "frame_bg.png"), "-ss", "19", "-t", "33", "-i", str(src), "-i", str(D / "frame_corner.png")]
chain = f"[1:v]crop=1206:880:0:290,scale={VW}:{VH}:flags=lanczos,unsharp=5:5:0.6[v];[0:v][v]overlay={VX}:{VY}:shortest=1[a];[a][2:v]overlay=0:0[b]"
prev = "[b]"
for k, (a, b, _, _) in enumerate(SUBS):
    inputs += ["-i", str(D / f"fsub{k}.png")]
    chain += f";{prev}[{k + 3}:v]overlay=0:0:enable='between(t,{a},{b})'[s{k}]"; prev = f"[s{k}]"
chain += f";{prev}fps=30,format=yuv420p[o]"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", chain, "-map", "[o]", "-map", "1:a",
                "-t", "33", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                str(D / "02.mp4")], check=True)
print("ok")
