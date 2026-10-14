"""카드 이미지 → 9:16 릴스(mp4) 만들기.

사용: python -m cardnews.reels spec.json out.mp4
spec = {"scenes": [{"img": "path.jpg", "crop": [x0,y0,x1,y1] | null,
                    "lines": ["첫 줄", "'강조'된 둘째 줄"], "dur": 2.5,
                    "zoom": [1.0, 1.12]}],
        "handle": "@today.worthy"}
- 사진은 화면을 꽉 채우고(9:16), 장마다 천천히 확대
- 글자는 화면 중앙 아래(인스타 UI 피하는 안전 영역), '작은따옴표' 단어는 노란색
- img 가 null 이면 검은 배경(마지막 질문 장)
- 장마다 "say"(읽을 문장)가 있으면 edge-tts로 한국어 내레이션을 만들고,
  장 길이를 음성 길이에 맞춰 늘림. spec의 "voice"·"rate"로 목소리·속도 지정
- 내레이션이 없으면 무음 AAC 트랙(음악은 인스타 앱에서 추가 권장)
"""
import json, os, re, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
YELLOW, WHITE = (255, 212, 59), (255, 255, 255)
FONT_PATHS = [
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc", 1),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 1),
]


def font(size):
    for p, idx in FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size, index=idx)
    return ImageFont.load_default()


def segments(line):
    """"주례는 '전남편'?" → [(주례는 ,흰),(전남편,노랑),(?,흰)]"""
    out = []
    for i, part in enumerate(re.split(r"'", line)):
        if part:
            out.append((part, YELLOW if i % 2 else WHITE))
    return out


def fit_cover(img, w, h):
    s = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * s) + 1, int(img.height * s) + 1), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def base_frame(scene):
    if not scene.get("img"):
        return Image.new("RGB", (W, H), (12, 12, 14))
    img = Image.open(scene["img"]).convert("RGB")
    if scene.get("crop"):
        img = img.crop(tuple(scene["crop"]))
    # 위아래가 남으면 흐린 배경으로 채우고, 사진은 가로 폭을 꽉 채움
    bg = fit_cover(img, W, H).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), 0.45)
    fg_h = int(img.height * W / img.width)
    if fg_h >= H * 0.8:
        return fit_cover(img, W, H)
    fg = img.resize((W, fg_h), Image.LANCZOS)
    bg.paste(fg, (0, int(H * 0.36) - fg_h // 2))
    return bg


def text_layer(lines, handle, size=88):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # 아래쪽 어둡게(글자 가독성)
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(max(0, (y - H * 0.45) / (H * 0.55)) * 215))
    layer.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 0), grad.resize((W, H)))
    d = ImageDraw.Draw(layer)
    f = font(size)
    y = int(H * 0.60)
    for line in lines:
        segs = segments(line)
        total = sum(d.textlength(t, font=f) for t, _ in segs)
        while total > W - 120 and size > 50:  # 길면 줄여서 맞춤
            size -= 4
            f = font(size)
            total = sum(d.textlength(t, font=f) for t, _ in segs)
        x = (W - total) / 2
        for t, c in segs:
            d.text((x, y), t, font=f, fill=c, stroke_width=3, stroke_fill=(0, 0, 0))
            x += d.textlength(t, font=f)
        y += int(size * 1.35)
    if handle:
        d.text((W // 2, int(H * 0.115)), handle, font=font(38), fill=(255, 255, 255, 230),
               anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
    return layer


def audio_len(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def narrate(spec, tmp):
    """장별 음성 파일을 만들고 장 길이를 맞춤. 만든 오디오 트랙 경로를 돌려줌."""
    voice = spec.get("voice", "ko-KR-SunHiNeural")
    rate = spec.get("rate", "+12%")
    inputs, filters = [], []
    for i, sc in enumerate(spec["scenes"]):
        if sc.get("say"):
            mp3 = f"{tmp}/say{i}.mp3"
            subprocess.run(["edge-tts", "--voice", voice, f"--rate={rate}",
                            "--text", sc["say"], "--write-media", mp3], check=True)
            sc["dur"] = max(sc["dur"], round(audio_len(mp3) + 0.35, 2))
            inputs += ["-i", mp3]
        else:
            inputs += ["-f", "lavfi", "-t", str(sc["dur"]), "-i", "anullsrc=r=24000:cl=mono"]
        filters.append(f"[{i}:a]aresample=44100,apad=whole_dur={sc['dur']}[a{i}]")
    n = len(spec["scenes"])
    graph = ";".join(filters) + ";" + "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[out]"
    wav = f"{tmp}/voice.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph,
                    "-map", "[out]", "-ac", "2", wav], check=True)
    return wav


def render(spec, out):
    tmp = tempfile.mkdtemp()
    voice_track = narrate(spec, tmp) if any(sc.get("say") for sc in spec["scenes"]) else None
    n = 0
    for sc in spec["scenes"]:
        base = base_frame(sc)
        txt = text_layer(sc.get("lines", []), spec.get("handle"), sc.get("size", 88))
        z0, z1 = sc.get("zoom", [1.0, 1.10] if sc.get("img") else [1.0, 1.0])
        frames = int(sc["dur"] * FPS)
        for i in range(frames):
            z = z0 + (z1 - z0) * i / max(frames - 1, 1)
            cw, ch = int(W / z), int(H / z)
            fr = base.crop(((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2))
            fr = fr.resize((W, H), Image.BILINEAR).convert("RGBA")
            fr.alpha_composite(txt)
            fr.convert("RGB").save(f"{tmp}/{n:05d}.jpg", quality=92)
            n += 1
    audio_in = ["-i", voice_track] if voice_track else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%05d.jpg",
        *audio_in, "-shortest",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out], check=True)
    return out


if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])


def cover_reel(card_jpg, out, seconds=8, hint="전체 이야기는 프로필 게시물에서 →"):
    """카드 표지(4:5)를 잘리지 않게 9:16 화면 가운데에 넣은 무음 릴스.

    - 카드(1080x1350)는 세로 285~1635px에 그대로 들어가서 인스타 피드(4:5)와
      프로필 격자(3:4)에서 잘리는 부분이 없음. 위아래 빈칸은 같은 사진을 흐리게 채움.
    - 위쪽 빈칸에 '전체 이야기는 프로필 게시물에서' 안내 한 줄(hint="" 이면 생략).
    - 아주 천천히 확대(1.00→1.03)해서 정지 화면처럼 보이지 않게 함. 음악은 앱에서 추가.
    """
    card = Image.open(card_jpg).convert("RGB")
    if card.size != (1080, 1350):
        card = fit_cover(card, 1080, 1350)
    bg = fit_cover(card, W, H).filter(ImageFilter.GaussianBlur(45))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), 0.5)
    top = (H - 1350) // 2
    if hint:
        d = ImageDraw.Draw(bg)
        d.text((W // 2, top // 2 + 20), hint, font=font(44), fill=WHITE, anchor="mm",
               stroke_width=2, stroke_fill=(0, 0, 0))
    tmp = tempfile.mkdtemp()
    frames = int(seconds * FPS)
    for i in range(frames):
        z = 1.0 + 0.03 * i / max(frames - 1, 1)
        cw, ch = int(1080 * z), int(1350 * z)
        fr = bg.copy()
        c = card.resize((cw, ch), Image.BILINEAR).crop(((cw - 1080) // 2, (ch - 1350) // 2,
                                                        (cw - 1080) // 2 + 1080, (ch - 1350) // 2 + 1350))
        fr.paste(c, (0, top))
        fr.save(f"{tmp}/{i:05d}.jpg", quality=92)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%05d.jpg",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out], check=True)
    return out
