#!/usr/bin/env python3
"""오늘의쓸모 흰 카드형 쇼츠 렌더러 (TTS 없음 · 자막 + 배경음악 하이라이트).

  python3 scripts/story_shorts/card_render.py drafts/worthy/<id>.json [출력.mp4]

원고 예(필드 설명은 스킬 today-worthy-shorts):
{"id":"20261018-sprite-card","media":"media/20261018-sprite2",
 "hook":{"t":"증거 없던 '붉은 번개'\\n찍히기까지 '103년'"},
 "credit":"영상: @florian.riou · 사진: NASA",
 "bgm":{"file":"assets/bgm/worthy/conspiracy_theory.mp3","start":"auto","vol":0.6},
 "orig_vol":0.3,
 "scenes":[{"text":"구름 위에서 터진 '붉은 번개'","video":{"src":"video/flash.mp4","start":2.6,"x":0.5,"y":0.4}},
           {"text":"…","gfx":"/abs/or/repo/path/a1886_card.mp4","start":0},
           {"text":"…","img":"cand/iss.jpg","zoom":0.08}]}
- dur 를 안 쓰면 글자 수로 정한다(글자 ÷ 8 + 0.8초, 2.0~4.0초).
- 강조어는 '작은따옴표' → 노랑 형광 띠.
"""
import json, math, os, re, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bgm_highlight  # noqa: E402

W, H, FPS = 1080, 1920, 30
# 배치 기준(2026.10.18 사용자 지정): '이런제품이?!' 쇼츠와 같은 높이.
# 로고 9~17% · 제목 20~29% · 영상 30~71% · 자막 73~81%(영상 바로 아래). 시청자 화면에서 앱 글자는 약 82%부터 덮는다.
HEAD_Y = 128                                  # 로고·채널명
TITLE_Y = 352                                 # 제목 2줄
BOX_Y, BOX_H = 580, 780                       # 영상 칸 1080x780
SUB_Y = BOX_Y + BOX_H + 44                    # 자막 시작(1줄 ≈1470, 2줄 ≈1550에서 끝남)
INK, GRAY, YEL = (17, 17, 17), (120, 120, 120), (255, 216, 77)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size, index=1)


def parse(text):
    """"a 'b' c" → [("a ",False),("b",True),(" c",False)]"""
    out, emph = [], False
    for part in re.split(r"(')", text):
        if part == "'":
            emph = not emph
        elif part:
            out.append((part, emph))
    return out


def wrap(text, fnt, maxw, d):
    """한 줄에 안 들어가면 공백에서 두 줄로 균형 있게 나눈다."""
    plain = text.replace("'", "")
    if d.textlength(plain, font=fnt) <= maxw or " " not in plain:
        return [text]
    words = text.split(" ")
    best = None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        wa, wb = d.textlength(a.replace("'", ""), font=fnt), d.textlength(b.replace("'", ""), font=fnt)
        if max(wa, wb) > maxw:
            continue
        score = abs(wa - wb)
        if best is None or score < best[0]:
            best = (score, a, b)
    if best is None:
        k = len(words) // 2
        return [" ".join(words[:k]), " ".join(words[k:])]
    a, b = best[1], best[2]
    # 따옴표가 줄을 넘어가면 각 줄에서 닫고 다시 연다
    if a.count("'") % 2:
        a, b = a + "'", "'" + b
    return [a, b]


def draw_rich(d, x, y, line, fnt, align_w=None):
    segs = parse(line)
    total = sum(d.textlength(s, font=fnt) for s, _ in segs)
    if align_w is not None:
        x = x + (align_w - total) / 2
    asc, desc = fnt.getmetrics()
    for s, emph in segs:
        w = d.textlength(s, font=fnt)
        if emph:
            pad = fnt.size * 0.08
            d.rounded_rectangle([x - pad, y + asc * 0.42, x + w + pad, y + asc + desc * 0.35],
                                radius=int(fnt.size * 0.12), fill=YEL)
        d.text((x, y), s, font=fnt, fill=INK)
        x += w


def circle_logo(size):
    im = Image.open(os.path.join(ROOT, "assets/worthy/logo.png")).convert("RGB").resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255)
    return im, m


def base_card(script):
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    lg, m = circle_logo(124)
    im.paste(lg, (60, HEAD_Y), m)
    d.text((204, HEAD_Y + 14), "@today.worthy", font=font(34, True), fill=GRAY)
    d.text((202, HEAD_Y + 58), "오늘의쓸모", font=font(48), fill=INK)
    tf = font(script.get("title_size", 88))
    y = TITLE_Y
    for line in script["hook"]["t"].split("\n")[:2]:
        draw_rich(d, 64, y, line, tf)
        y += int(tf.size * 1.2)
    if script.get("credit"):
        cf = font(24, True)
        t = script["credit"]
        d.text((W - 40 - d.textlength(t, font=cf), BOX_Y + BOX_H + 8), t, font=cf, fill=GRAY)
    return im


def scene_card(base, text):
    im = base.copy()
    d = ImageDraw.Draw(im)
    sf = font(62)
    lines = wrap(text, sf, W - 300, d)[:2]  # 오른쪽 버튼 줄(약 150px) 피해서 좌우 150px 여백
    y = SUB_Y
    for line in lines:
        draw_rich(d, 0, y, line, sf, align_w=W)
        y += 82
    return im


def auto_dur(text):
    n = len(text.replace("'", "").replace(" ", ""))
    return round(min(4.0, max(2.0, n / 8 + 0.8)), 2)


def has_audio(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return bool(r.stdout.strip())


def run(cmd):
    subprocess.run(cmd, check=True)


def render_scene(i, sc, script, base, tmp, media):
    dur = float(sc.get("dur") or auto_dur(sc["text"]))
    png = os.path.join(tmp, f"card{i}.png")
    scene_card(base, sc["text"]).save(png)
    out = os.path.join(tmp, f"seg{i:02d}.mp4")
    ov = float(sc.get("orig_vol", script.get("orig_vol", 0.3)))
    cover = (f"scale={W}:{BOX_H}:force_original_aspect_ratio=increase,"
             f"crop={W}:{BOX_H}:(iw-{W})*{{x}}:(ih-{BOX_H})*{{y}}")
    if "img" in sc:
        src = os.path.join(media, sc["img"])
        z = float(sc.get("zoom", 0.08))
        frames = int(dur * FPS)
        vf = (f"scale={W*2}:{BOX_H*2}:force_original_aspect_ratio=increase,crop={W*2}:{BOX_H*2},"
              f"zoompan=z='1+{z}*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{BOX_H}:fps={FPS}")
        inputs = ["-loop", "1", "-i", png, "-loop", "1", "-i", src]
        filt = f"[1:v]{vf}[v];[0:v][v]overlay=0:{BOX_Y}:shortest=1,format=yuv420p[o]"
        aud = None
    else:
        v = sc.get("video") or {"src": sc["gfx"]}
        src = v["src"] if os.path.isabs(v["src"]) else os.path.join(media, v["src"])
        start = float(v.get("start", sc.get("start", 0)))
        sp = f"setpts=PTS/{v['speed']}," if v.get("speed") else ""
        inputs = ["-loop", "1", "-i", png, "-stream_loop", "-1", "-ss", str(start), "-i", src]
        if v.get("fit") == "contain":
            # 그래픽처럼 잘리면 안 되는 화면: 칸 높이에 맞춰 줄이고, 양옆은 같은 화면을 흐리게 채움
            filt = (f"[1:v]{sp}fps={FPS},split[a][b];"
                    f"[a]{cover.format(x=0.5, y=0.5)},boxblur=30:2,eq=brightness=-0.15[bg];"
                    f"[b]scale=-2:{BOX_H}[fg];[bg][fg]overlay=(W-w)/2:0[v];"
                    f"[0:v][v]overlay=0:{BOX_Y}:shortest=1,format=yuv420p[o]")
        else:
            vf = sp + cover.format(x=v.get("x", 0.5), y=v.get("y", 0.5))
            filt = f"[1:v]{vf},fps={FPS}[v];[0:v][v]overlay=0:{BOX_Y}:shortest=1,format=yuv420p[o]"
        aud = src if (ov > 0 and has_audio(src)) else None
    cmd = ["ffmpeg", "-y", "-v", "error"] + inputs
    if aud:
        filt += f";[1:a]volume={ov},aresample=48000,aformat=channel_layouts=stereo[a]"
        amap = ["-map", "[a]"]
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        amap = ["-map", "2:a"]
    cmd += ["-filter_complex", filt, "-map", "[o]"] + amap + [
        "-t", f"{dur}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k", out]
    run(cmd)
    return out, dur


def main():
    path = sys.argv[1]
    script = json.load(open(path))
    media = os.path.join(ROOT, script.get("media", f"media/{script['id']}"))
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(media, "short_card.mp4")
    tmp = tempfile.mkdtemp(prefix="card_")
    base = base_card(script)
    segs, total = [], 0.0
    for i, sc in enumerate(script["scenes"]):
        s, d = render_scene(i, sc, script, base, tmp, media)
        segs.append(s)
        total += d
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
    joined = os.path.join(tmp, "joined.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    b = script.get("bgm")
    if b:
        bf = os.path.join(ROOT, b["file"])
        st = b.get("start", "auto")
        if st == "auto":
            r = bgm_highlight.find_start(bgm_highlight.load(bf), total)
            st = r[0] if isinstance(r, tuple) else r
        vol = float(b.get("vol", 0.6))
        fo = max(0.0, total - 1.2)
        run(["ffmpeg", "-y", "-v", "error", "-i", joined, "-ss", str(st), "-i", bf, "-filter_complex",
             f"[1:a]atrim=0:{total},asetpts=PTS-STARTPTS,volume={vol},afade=t=in:d=0.15,afade=t=out:st={fo}:d=1.2[m];"
             f"[0:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-movflags", "+faststart", out])
        print(f"bgm {b['file']} start={st}s")
    else:
        run(["ffmpeg", "-y", "-v", "error", "-i", joined, "-c", "copy", "-movflags", "+faststart", out])
    base.save(out.replace(".mp4", "_cover.jpg"))
    print(f"{out}  {total:.1f}s  scenes={len(segs)}")


if __name__ == "__main__":
    main()
