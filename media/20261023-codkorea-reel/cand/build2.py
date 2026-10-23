"""콜옵 3년 공식 릴스 v2: 9:16 꽉 채움, 한 번에 글자 한 덩어리, 연도 카드 → 실제 장면 같은 박자, 마지막 정적 후 2029?"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = "media/20261023-codkorea-reel"
V = f"{D}/video"
T = f"{D}/cand/tmp2"
os.makedirs(T, exist_ok=True)
W, H = 1080, 1920
FB = "assets/fonts/Pretendard-Black.otf"
YEL, WHT = (255, 216, 77), (255, 255, 255)
LOGO = "brand/logo_typo_A.png"


def text_png(path, lines, y_center=760, sizes=None, colors=None, logo=False):
    """lines를 가운데 정렬로 크게. 검은 외곽선 + 은은한 그림자."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sizes = sizes or [150] * len(lines)
    colors = colors or [WHT] * len(lines)
    gap = 30
    hs = [s for s in sizes]
    total = sum(hs) + gap * (len(lines) - 1)
    y = y_center - total // 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds, d = ImageDraw.Draw(sh), ImageDraw.Draw(im)
    for l, s, c in zip(lines, sizes, colors):
        f = ImageFont.truetype(FB, s)
        ds.text((W // 2, y + s), l, font=f, fill=(0, 0, 0, 200), anchor="ms")
        d.text((W // 2, y + s), l, font=f, fill=c, anchor="ms", stroke_width=max(4, s // 25), stroke_fill=(0, 0, 0))
        y += s + gap
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    out = Image.alpha_composite(sh, im)
    if logo:
        lg = Image.open(LOGO).convert("RGBA")
        lh = 50
        lg = lg.resize((int(lg.width * lh / lg.height), lh), Image.LANCZOS)
        out.alpha_composite(lg, ((W - lg.width) // 2, 1500))
    out.save(path)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-1500:])
        raise SystemExit(1)


def clip(out, src, ss, dur, crop, png, zoom=0.04):
    """원본 → crop → 1080x1920 꽉 → 천천히 확대 → 글자 PNG."""
    n = int(dur * 30)
    vf = (f"[0:v]crop={crop},scale={W*2}:{H*2},setsar=1,"
          f"zoompan=z='1+{zoom}*on/{n}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps=30,"
          f"eq=contrast=1.08:saturation=1.1[b];[b][1:v]overlay=0:0,format=yuv420p[v]")
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ss), "-t", str(dur), "-i", src, "-loop", "1", "-i", png,
         "-filter_complex", vf, "-map", "[v]", "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17", out])


def news_clip(out, src, ss, dur, crop, png):
    """가로 뉴스 화면: 흐린 배경 위에 가로 원본을 화면 가운데 크게(살짝 확대해 양옆 조금 잘림)."""
    n = int(dur * 30)
    vf = (f"[0:v]crop={crop},setsar=1,split[a][b];"
          f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.3[bg];"
          f"[b]scale=-2:820,crop={W}:820,eq=contrast=1.08[fg];"
          f"[bg][fg]overlay=0:760[c];[c][1:v]overlay=0:0,fps=30,format=yuv420p[v]")
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ss), "-t", str(dur), "-i", src, "-loop", "1", "-i", png,
         "-filter_complex", vf, "-map", "[v]", "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17", out])


def card(out, dur, png, bg=None):
    """검은(또는 흐린) 바탕 + 글자. 글자는 살짝 커지며 등장."""
    n = int(dur * 30)
    src = ["-f", "lavfi", "-i", f"color=c=0x0a0a0c:s={W}x{H}:r=30"] if bg is None else ["-loop", "1", "-i", bg]
    vf = (f"[1:v]format=rgba,scale={W*2}:{H*2},zoompan=z='if(lt(on,6),1.12-0.02*on,1)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps=30[t];"
          f"[0:v]scale={W}:{H},setsar=1[b];[b][t]overlay=0:0,format=yuv420p[v]")
    run(["ffmpeg", "-y", "-loglevel", "error", *src, "-loop", "1", "-i", png, "-filter_complex", vf,
         "-map", "[v]", "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17", out])


def blurred_frame(out, src, ss, crop):
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ss), "-i", src, "-frames:v", "1",
         "-vf", f"crop={crop},scale={W}:{H},boxblur=40:2,eq=brightness=-0.35", out])


C_MW4 = "405:720:437:0"        # 1280x720 가운데 9:16
C_KYIV = "1020:500:0:20"     # CNN 하단 자막·우상단 지명 딱지 제외
C_TEH = "800:1422:140:480"    # 알자지라 로고·지명 딱지 아래

P = []
# 0) 후킹: 서울 거리 + 채널 기본 제목(로고 포함)
run(["python3", "scripts/reel_overlay.py", f"{T}/hook.png", "콜옵 배경 3년 뒤\\n진짜 전쟁 났다\\n다음은 한반도?"])
clip(f"{T}/s0.mp4", f"{V}/v2.mp4", 15.2, 2.2, C_MW4, f"{T}/hook.png"); P.append("s0")

beats = [
    # (연도 카드 글자, 실제 장면 소스, 시작, 길이, crop, 실제 장면 글자)
    (["2019 콜옵", "배경: 러시아"], f"{V}/v1.mp4", 7.0, 2.0, C_KYIV, ["3년 뒤", "진짜 침공"]),
    (["2022 콜옵", "배경: 이란"], f"{V}/v5.mp4", 20.0, 2.0, C_TEH, ["3년 뒤", "진짜 공습"]),
]
for i, (ct, src, ss, dur, crop, rt) in enumerate(beats, 1):
    bg = f"{T}/bg{i}.png"
    blurred_frame(bg, src, ss, crop)
    text_png(f"{T}/c{i}.png", ct, y_center=900, sizes=[170, 110], colors=[YEL, WHT])
    card(f"{T}/c{i}.mp4", 1.1, f"{T}/c{i}.png", bg); P.append(f"c{i}")
    if i == 1:
        text_png(f"{T}/r{i}.png", rt, y_center=500, sizes=[110, 150], colors=[WHT, YEL])
        news_clip(f"{T}/r{i}.mp4", src, ss, dur, crop, f"{T}/r{i}.png")
    else:
        text_png(f"{T}/r{i}.png", rt, y_center=640, sizes=[110, 150], colors=[WHT, YEL])
        clip(f"{T}/r{i}.mp4", src, ss, dur, crop, f"{T}/r{i}.png")
    P.append(f"r{i}")

# 2026 카드 → 게임 속 한국 장면 3컷(같은 박자)
bg = f"{T}/bg3.png"; blurred_frame(bg, f"{V}/v2.mp4", 27.0, C_MW4)
text_png(f"{T}/c3.png", ["2026 콜옵", "배경: 한반도"], y_center=900, sizes=[170, 110], colors=[YEL, WHT])
card(f"{T}/c3.mp4", 1.1, f"{T}/c3.png", bg); P.append("c3")
empty = f"{T}/empty.png"; Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(empty)
text_png(f"{T}/today.png", ["오늘 출시"], y_center=640, sizes=[110], colors=[WHT])
for k, (ss, crop) in enumerate([(27.0, "405:720:600:0"), (121.2, "405:720:437:0"), (132.0, C_MW4)]):
    clip(f"{T}/g{k}.mp4", f"{V}/v2.mp4", ss, 1.0, crop, f"{T}/today.png" if k == 0 else empty); P.append(f"g{k}")

# 정적 0.5초 → 3년 뒤면 → 2029?
bg = f"{T}/bg4.png"; blurred_frame(bg, f"{V}/v2.mp4", 133.0, C_MW4)
card(f"{T}/q0.mp4", 0.5, empty); P.append("q0")
text_png(f"{T}/q1.png", ["3년 뒤면…"], y_center=900, sizes=[130], colors=[WHT])
card(f"{T}/q1.mp4", 1.0, f"{T}/q1.png", bg); P.append("q1")
text_png(f"{T}/q2.png", ["3년 뒤면…", "2029?"], y_center=860, sizes=[130, 260], colors=[WHT, YEL], logo=True)
card(f"{T}/q2.mp4", 2.4, f"{T}/q2.png", bg); P.append("q2")

with open(f"{T}/list.txt", "w") as fp:
    fp.writelines(f"file '{os.path.abspath(T)}/{p}.mp4'\n" for p in P)
run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{T}/list.txt",
     "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-map", "0:v", "-map", "1:a", "-shortest",
     "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", f"{D}/reel.mp4"])
run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.5", "-i", f"{D}/reel.mp4", "-frames:v", "1", "-q:v", "2", f"{D}/reel_cover.jpg"])
print("ok")
