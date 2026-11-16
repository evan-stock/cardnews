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

[2026.10.20 시험] "layout": "full" — 세로 전체 화면(영상이 화면 전체, 위에 흰 제목 2줄, 가운데 아래 흰 자막).
  가로 원본은 자동으로 '가로 맞춤 + 흐린 배경'(video.fit 로 "cover"/"contain" 직접 지정 가능).
[2026.10.20 시험] 장면 "say": "내레이션" — 필재 목소리(털뭉치와 같은 맥북 방식). 자막은 text(없으면 say).
  목소리가 media/<id>/tts/<key>.mp3 에 없으면 state/tts_queue/<id>.json 요청서를 쓰고 종료 코드 3으로 끝난다
  → 요청서를 push → 맥북이 목소리를 올림 → scripts/story_shorts/wait_tts.sh <id> 로 기다린 뒤 다시 렌더.
  내레이션이 있으면 배경음악은 bgm.vol × bgm.duck(기본 0.5).
"""
import hashlib, json, math, os, re, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bgm_highlight  # noqa: E402

W, H, FPS = 1080, 1920, 30
# 배치 기준(2026.10.18 사용자 지정): '이런제품이?!' 쇼츠와 같은 높이.
# 로고 9~17% · 제목 20~29% · 영상 30~71% · 자막 73~81%(영상 바로 아래). 시청자 화면에서 앱 글자는 약 82%부터 덮는다.
HEAD_Y = 128                                  # 로고·채널명 (10.25 960 칸 시험 → 폰에서 자막이 채널명에 가려 되돌림)
TITLE_Y = 352                                 # 제목 2줄
BOX_Y, BOX_H = 580, 780                       # 영상 칸 1080x780
SUB_Y = BOX_Y + BOX_H + 44                    # 자막 시작(1줄 ≈1470, 2줄 ≈1550에서 끝남)
INK, GRAY, YEL = (17, 17, 17), (120, 120, 120), (255, 216, 77)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size, index=1)


# ── 전체 화면(layout full) ───────────────────────────────────────────
PRET = os.path.join(ROOT, "assets/fonts/Pretendard-Black.otf")
F_TITLE_Y = 200                                # 제목 시작(앱 위쪽 검색·메뉴 아이콘 아래)
F_SUB_CY = 1190                                # 자막 가운데(화면 62%, 앱 글자는 약 78%부터 덮음)


def pfont(size):
    return ImageFont.truetype(PRET, size) if os.path.exists(PRET) else font(size)


def draw_outline(d, x, y, line, fnt, align_w=None, stroke=9, hi=YEL):
    """흰 글자 + 검정 테두리, '강조어'는 노랑 글자."""
    segs = parse(line)
    total = sum(d.textlength(t, font=fnt) for t, _ in segs)
    if align_w is not None:
        x = x + (align_w - total) / 2
    for t, emph in segs:
        d.text((x, y), t, font=fnt, fill=hi if emph else (255, 255, 255), stroke_width=stroke, stroke_fill=(0, 0, 0))
        x += d.textlength(t, font=fnt)


def full_base(script):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad = Image.new("L", (1, 620))
    for yy in range(620):
        grad.putpixel((0, yy), int(190 * (1 - yy / 620) ** 1.3))
    shade = Image.new("RGBA", (W, 620), (0, 0, 0, 255))
    shade.putalpha(grad.resize((W, 620)))
    im.alpha_composite(shade)
    d = ImageDraw.Draw(im)
    tf = pfont(script.get("title_size", 86))
    y = F_TITLE_Y
    for line in script["hook"]["t"].split("\n")[:2]:
        draw_outline(d, 0, y, line, tf, align_w=W, stroke=8)
        y += int(tf.size * 1.25)
    # 채널 표시(작게) + 원작자
    lg, m = circle_logo(54)
    tag = "오늘의쓸모"
    tfnt = pfont(34)
    tw = 54 + 12 + d.textlength(tag, font=tfnt)
    x0 = (W - tw) / 2
    im.paste(lg, (int(x0), y + 14), m)
    d.text((x0 + 66, y + 20), tag, font=tfnt, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    if script.get("credit"):
        cf = font(22, True)
        t = script["credit"]
        d.text((W - 36 - d.textlength(t, font=cf), y + 82), t, font=cf, fill=(235, 235, 235),
               stroke_width=2, stroke_fill=(0, 0, 0))
    return im


def full_scene(base, text):
    im = base.copy()
    d = ImageDraw.Draw(im)
    sf = pfont(70)
    lines = wrap(text, sf, W - 240, d)[:2] if text else []
    y = F_SUB_CY - len(lines) * 92 // 2
    for line in lines:
        draw_outline(d, 0, y, line, sf, align_w=W, stroke=10)
        y += 92
    return im


# ── 내레이션(맥북 타입캐스트, 털뭉치와 같은 방식) ─────────────────────
def tts_cfg(script):
    import yaml
    c = (yaml.safe_load(open(os.path.join(ROOT, "config.yaml"), encoding="utf-8")) or {})
    t = {"model": "ssfm-v30", "emotion": "normal", "intensity": 1.0, "tempo": 1.1,
         **c.get("shorts", {}).get("tts", {})}
    return {**t, **(script.get("voice") or {})}


def tts_key(text, c, ctx):
    k = {"t": text, "v": c.get("voice_id"), "m": c.get("model"), "e": c.get("emotion"), "tp": c.get("tempo"),
         "i": c.get("intensity"), "p": ctx.get("previous_text", ""), "n": ctx.get("next_text", "")}
    return hashlib.sha1(json.dumps(k, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]


def voice_plan(script, media):
    """장면별 (key, text, ctx) 와 아직 없는 목록."""
    sl = script["scenes"]
    if not any((s.get("say") or "").strip() for s in sl):
        return {}, []
    c = tts_cfg(script)
    says = [(s.get("say") or "").replace("'", "") for s in sl]
    plan, need = {}, []
    for i, t in enumerate(says):
        if not t.strip():
            continue
        ctx = {"previous_text": says[i - 1] if i else "", "next_text": says[i + 1] if i + 1 < len(says) else ""}
        key = tts_key(t, c, ctx)
        plan[i] = os.path.join(media, "tts", f"{key}.mp3")
        if not os.path.exists(plan[i]):
            need.append({"key": key, "text": t, "ctx": ctx,
                         "voice": {k: c.get(k) for k in ("voice_id", "model", "emotion", "intensity", "tempo")}})
    return plan, need


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


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
        if a.count("'") % 2:  # '강조어' 가운데서 끊지 않는다
            continue
        wa, wb = d.textlength(a.replace("'", ""), font=fnt), d.textlength(b.replace("'", ""), font=fnt)
        if max(wa, wb) > maxw:
            continue
        score = abs(wa - wb) - (fnt.size * 2 if a.endswith(",") else 0)  # 쉼표 뒤에서 끊기를 선호
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


def render_scene(i, sc, script, base, tmp, media, voice=None):
    text = sc.get("text") or sc.get("say") or ""
    dur = float(sc.get("dur") or auto_dur(text))
    if voice:
        dur = max(dur if sc.get("dur") else 0, duration(voice) + 0.25)
    full = script.get("layout") == "full"
    png = os.path.join(tmp, f"card{i}.png")
    (full_scene(base, text) if full else scene_card(base, text)).save(png)
    out = os.path.join(tmp, f"seg{i:02d}.mp4")
    ov = float(sc.get("orig_vol", script.get("orig_vol", 0.3)))
    if full:
        return render_full(i, sc, png, out, dur, ov, media, voice)
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
        sp = "setpts=PTS-STARTPTS," + (f"setpts=PTS/{v['speed']}," if v.get("speed") else "")  # 장면 첫 프레임 흰 화면 방지
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


def render_full(i, sc, png, out, dur, ov, media, voice):
    """전체 화면: [1]=영상/사진(1080x1920) 위에 [0]=제목·자막 PNG(투명)."""
    if "img" in sc:
        src = os.path.join(media, sc["img"])
        z = float(sc.get("zoom", 0.08))
        frames = int(dur * FPS) + 1
        inputs = ["-loop", "1", "-i", png, "-loop", "1", "-i", src]
        vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
              f"zoompan=z='1+{z}*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}")
        filt = f"[1:v]{vf}[v]"
        aud = None
    else:
        v = sc.get("video") or {"src": sc["gfx"]}
        src = v["src"] if os.path.isabs(v["src"]) else os.path.join(media, v["src"])
        start = float(v.get("start", sc.get("start", 0)))
        sp = "setpts=PTS-STARTPTS," + (f"setpts=PTS/{v['speed']}," if v.get("speed") else "")  # 장면 첫 프레임 흰 화면 방지
        inputs = ["-loop", "1", "-i", png, "-stream_loop", "-1", "-ss", str(start), "-i", src]
        fit = v.get("fit")
        if not fit:
            r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                "stream=width,height", "-of", "csv=p=0", src], capture_output=True, text=True)
            try:
                w_, h_ = [int(x) for x in r.stdout.strip().split(",")[:2]]
                fit = "contain" if w_ / h_ > 0.8 else "cover"
            except ValueError:
                fit = "cover"
        if fit == "contain":  # 가로 원본: 가로 폭에 맞추고 위아래는 같은 화면을 흐리게
            fy = float(v.get("cy", 0.55))
            filt = (f"[1:v]{sp}fps={FPS},split[a][b];"
                    f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=40:2,"
                    f"eq=brightness=-0.2[bg];[b]scale={W}*{float(v.get('scale', 1.0))}:-2[fg];"
                    f"[bg][fg]overlay=(W-w)/2:(H-h)*{fy}[v]")
        else:
            filt = (f"[1:v]{sp}scale={W}:{H}:force_original_aspect_ratio=increase,"
                    f"crop={W}:{H}:(iw-{W})*{v.get('x', 0.5)}:(ih-{H})*{v.get('y', 0.5)},fps={FPS}[v]")
        aud = src if (ov > 0 and has_audio(src)) else None
    filt += ";[v][0:v]overlay=0:0:shortest=1,format=yuv420p[o]"
    cmd = ["ffmpeg", "-y", "-v", "error"] + inputs
    n = 2
    parts = []
    if aud:
        parts.append(f"[1:a]volume={ov},aresample=48000,aformat=channel_layouts=stereo[oa]")
    if voice:
        cmd += ["-i", voice]
        parts.append(f"[{n}:a]adelay=120|120,aresample=48000,aformat=channel_layouts=stereo,apad[va]")
        n += 1
    cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    sil = n
    labs = ([ "[oa]"] if aud else []) + (["[va]"] if voice else []) + [f"[{sil}:a]"]
    parts.append("".join(labs) + f"amix=inputs={len(labs)}:duration=longest:normalize=0[a]")
    filt += ";" + ";".join(parts)
    cmd += ["-filter_complex", filt, "-map", "[o]", "-map", "[a]",
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
    plan, need = voice_plan(script, media)
    if need:
        q = os.path.join(ROOT, "state", "tts_queue")
        os.makedirs(q, exist_ok=True)
        json.dump({"id": script["id"], "render": False, "channel": "worthy", "items": need},
                  open(os.path.join(q, f"{script['id']}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"WAIT_TTS {len(need)}개 장면 목소리 요청서 → state/tts_queue/{script['id']}.json (push 후 wait_tts.sh)")
        sys.exit(3)
    base = full_base(script) if script.get("layout") == "full" else base_card(script)
    segs, total = [], 0.0
    for i, sc in enumerate(script["scenes"]):
        s, d = render_scene(i, sc, script, base, tmp, media, plan.get(i))
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
        vol = float(b.get("vol", 0.6)) * (float(b.get("duck", 0.5)) if plan else 1.0)
        fo = max(0.0, total - 1.2)
        run(["ffmpeg", "-y", "-v", "error", "-i", joined, "-ss", str(st), "-i", bf, "-filter_complex",
             f"[1:a]atrim=0:{total},asetpts=PTS-STARTPTS,volume={vol},afade=t=in:d=0.15,afade=t=out:st={fo}:d=1.2[m];"
             f"[0:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-movflags", "+faststart", out])
        print(f"bgm {b['file']} start={st}s")
    else:
        run(["ffmpeg", "-y", "-v", "error", "-i", joined, "-c", "copy", "-movflags", "+faststart", out])
    if script.get("layout") == "full":
        run(["ffmpeg", "-y", "-v", "error", "-ss", "0.5", "-i", out, "-frames:v", "1", out.replace(".mp4", "_cover.jpg")])
    else:
        base.save(out.replace(".mp4", "_cover.jpg"))
    print(f"{out}  {total:.1f}s  scenes={len(segs)}")


if __name__ == "__main__":
    main()
