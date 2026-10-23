"""콜옵 3년 공식 릴스 빌드: 구간별 9:16(흐린 배경 + 가운데 영상 띠 + 위 캡션) → 이어붙이기 → 하단 제목 오버레이."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont

D = "media/20261023-codkorea-reel"
V = f"{D}/video"
T = f"{D}/cand/tmp"
os.makedirs(T, exist_ok=True)
W, H = 1080, 1920
BAND_Y, BAND_H = 370, 680
FB = "assets/fonts/Pretendard-Black.otf"
YEL, WHT = (255, 216, 77), (255, 255, 255)

# (파일, 시작, 길이, 원본에서 잘라 쓸 영역 crop=w:h:x:y 또는 None, 노랑 캡션, 흰 캡션)
SEGS = [
    ("v1.mp4", 6.5, 3.5, "1160:480:0:40", "2019 콜옵 = 러시아", "3년 뒤, 진짜 침공"),
    ("v4.mp4", 75.0, 2.0, None, "2022 콜옵 = 이란", ""),
    ("v5.mp4", 20.0, 3.5, "1080:620:0:460", "2022 콜옵 = 이란", "3년 뒤, 진짜 공습"),
    ("v2.mp4", 15.2, 2.0, None, "2026 콜옵 = 한반도", ""),
    ("v2.mp4", 27.0, 1.4, None, "2026 콜옵 = 한반도", ""),
    ("v2.mp4", 121.2, 1.6, None, "2026 콜옵 = 한반도", ""),
    ("v2.mp4", 132.0, 2.8, None, "2026 콜옵 = 한반도", "3년 뒤면… 2029?"),
]


def caption(path, yel, wht):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(FB, 84)
    f2 = ImageFont.truetype(FB, 64)
    d.text((W // 2, 230), yel, font=f1, fill=YEL, anchor="ms", stroke_width=4, stroke_fill=(0, 0, 0))
    if wht:
        d.text((W // 2, 330), wht, font=f2, fill=WHT, anchor="ms", stroke_width=4, stroke_fill=(0, 0, 0))
    im.save(path)


parts = []
for i, (f, ss, dur, crop, yel, wht) in enumerate(SEGS):
    cap = f"{T}/cap{i}.png"
    caption(cap, yel, wht)
    src = f"[0:v]{'crop=' + crop + ',' if crop else ''}setsar=1,split[a][b]"
    bg = f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.25[bg]"
    fg = f"[b]scale={W}:{BAND_H}:force_original_aspect_ratio=increase,crop={W}:{BAND_H}[fg]"
    comp = f"[bg][fg]overlay=0:{BAND_Y}[c];[c][1:v]overlay=0:0,fps=30,format=yuv420p[v]"
    out = f"{T}/p{i}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ss), "-t", str(dur), "-i", f"{V}/{f}", "-i", cap,
           "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo",
           "-filter_complex", f"{src};{bg};{fg};{comp};[0:a]aresample=44100,aformat=channel_layouts=stereo,apad[aa];[aa][2:a]amix=inputs=2:duration=shortest:normalize=0[ao]",
           "-map", "[v]", "-map", "[ao]", "-t", str(dur), "-c:v", "libx264", "-preset", "fast", "-crf", "18",
           "-c:a", "aac", "-ar", "44100", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:  # 소리 없는 원본이면 무음으로
        cmd2 = ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ss), "-t", str(dur), "-i", f"{V}/{f}", "-i", cap,
                "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo",
                "-filter_complex", f"{src};{bg};{fg};{comp}", "-map", "[v]", "-map", "2:a", "-t", str(dur),
                "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-ar", "44100", out]
        subprocess.run(cmd2, check=True)
    parts.append(out)

with open(f"{T}/list.txt", "w") as fp:
    fp.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{T}/list.txt",
                "-i", f"{D}/cand/overlay3.png", "-filter_complex", "[0:v][1:v]overlay=0:0,format=yuv420p[v];[0:a]loudnorm=I=-16:TP=-1.5[a]",
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "19",
                "-c:a", "aac", "-b:a", "160k", f"{D}/reel.mp4"], check=True)
print("ok")
