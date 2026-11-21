"""영상 장(검은 바탕 frame 틀 + 둥근 영상 + 말자막). 출처: 유튜브 [팟빵] CRIME(11.20) 배상훈 프로파일러, 엑스 @itwillbe_sage 클립."""
import re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; T = Path("/tmp/pv"); T.mkdir(exist_ok=True)
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
VW, VH, VY = 940, 508, 300

def rich_center(d, y, text, font, base):
    parts = re.split(r"('[^']*')", text); tw = sum(d.textlength(p.strip("'"), font=font) for p in parts if p); x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'"); d.text((x, y), p, font=font, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=font)

def bg(top, src_note):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    rich_center(d, H - 150, src_note, F("Medium", 28), (150, 150, 158))
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
    lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg); return im

def sub_png(text, path):
    im = Image.new("RGBA", (W, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, ln in enumerate(text.split("\n")): rich_center(d, 60 + i * 68, ln, F("Black", 50), FG)
    im.save(path)

def mask():
    m = Image.new("L", (VW, VH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, VW - 1, VH - 1), 18, fill=255); m.save(T / "mask.png")

def build(name, src, start, dur, top, subs, note):
    bg(top, note).save(T / f"{name}_bg.png"); mask()
    ins = ["-loop", "1", "-i", str(T / f"{name}_bg.png"), "-ss", str(start), "-t", str(dur), "-i", str(D / "video" / src), "-loop", "1", "-i", str(T / "mask.png")]
    fc = [f"[1:v]scale={VW}:{VH}:force_original_aspect_ratio=increase,crop={VW}:{VH},format=rgba[v]", "[2:v]format=gray[m]", "[v][m]alphamerge[vm]",
          f"[0:v][vm]overlay={(W-VW)//2}:{VY}:shortest=1[b0]"]
    last = "b0"
    for k, (a, b, t) in enumerate(subs):
        p = T / f"{name}_s{k}.png"; sub_png(t, p); ins += ["-loop", "1", "-i", str(p)]
        fc.append(f"[{last}][{3+k}:v]overlay=0:{VY+VH+30}:enable='between(t,{a-start:.2f},{b-start:.2f})'[b{k+1}]"); last = f"b{k+1}"
    fc.append(f"[{last}]fps=30,format=yuv420p[o]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(fc), "-map", "[o]", "-map", "1:a", "-t", str(dur),
                    "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(O / f"{name}.mp4")], check=True)
    print(name, "ok")

build("vjasu", "jasu.mp4", 11.6, 13.5, ("끝까지 '자수'하지 않은 이유", "\"자수 = '서울대생'이 아니라는 인정\""),
      [(11.6, 13.8, "\"자수란 게 뭐죠?\n내가 '인정'을 하는 거예요\""), (14.0, 17.4, "\"나는 '서울대생'이 아니라는 걸\n인정하는 거예요\""),
       (17.6, 21.7, "\"자기 정체성은 '서울대생'인데\n서울대 갈 사람이 아니라는 걸\""), (22.0, 25.1, "\"그럴 '실력'도 안 된다는 걸\n고백할 수밖에 없잖아요\"")],
      "유튜브 [팟빵] CRIME(11.20) · 배상훈 프로파일러")
build("vgak", "gakseong.mp4", 16.7, 29.3, ("패러글라이딩 '뇌 각성' 스토리", "\"사실은 '각성제' 경험일 것\""),
      [(16.7, 21.2, "\"저는 사실 이게\n'각성제'나 마약이라고 생각합니다\""), (21.4, 25.6, "\"본인도 검정고시나\n이런 걸 봤어요\""),
       (25.6, 28.0, "\"검정고시로 졸업했고\n수능도 봤어요\""), (28.0, 32.9, "\"고등학생들한테 떠도는\n'각성제'\""),
       (34.0, 36.8, "\"그걸 먹으면 마치\n그렇게 느끼게 되는 거예요\""), (37.0, 39.9, "\"순간 뭐가\n'확 도는' 느낌\""),
       (39.9, 43.0, "\"갑자기 끊으면\n'쫙 빠지는' 느낌\""), (43.0, 46.0, "\"그걸 본인이 '포장'했을\n가능성이 높아요\"")],
      "유튜브 [팟빵] CRIME(11.20) · 배상훈 프로파일러")
