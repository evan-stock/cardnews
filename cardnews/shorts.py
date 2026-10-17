"""유튜브 쇼츠 자동 제작: 대본(장면별 문장) → TTS 내레이션 → 실제 영상·사진·AI 장면 9:16 합성
→ 상단 고정 제목 + 내레이션 싱크 자막 → (선택) BGM → 텔레그램 미리보기·승인 → 유튜브 업로드.

사용: python -m cardnews.shorts drafts/shorts.json   (GitHub Actions shorts.yml이 push 때 자동 실행)

원고 형식(drafts/shorts.json, 목록도 가능):
{
 "id": "20261017-robot", "mode": "render" | "send",
 "hook": {"tag": "실제 영상", "t": "줄1\\n줄2\\n'강조 줄'"},       # 영상 내내 위쪽에 고정되는 제목
 "scenes": [
   {"say": "내레이션 문장", "video": {"src": "video/v1.mp4", "start": 3.0, "x": 0.5, "y": 0.5, "audio": 0.0}},
   {"say": "...", "img": "cand/press03.jpg", "zoom": 0.10},
   {"say": "...", "img": "cand/url01.jpg", "label": "AI 참고 이미지"},
   {"say": "...", "sub": "자막을 따로 쓰고 싶을 때(없으면 say를 자막으로)"},
   {"say": "구독하면 매일 화제 소식을 받아보실 수 있습니다", "img": "cand/press01.jpg", "end": true}
 ],
 "yt": {"title": "제목 #shorts", "description": "본문", "tags": ["..."], "category": 24,
        "privacy": "public", "synthetic": false},
 "voice": {"voice_id": "...", "emotion": "toneup", "tempo": 1.15},   # 선택: config 덮어쓰기
 "bgm": "assets/bgm/파일.mp3", "bgm_volume": 0.10,                   # 선택
 "sources": [{"publisher": "", "url": "", "date": ""}], "photo_credits": ["매체/계정"],
 "publish_now": true | "publish_at": "2026-10-17T19:00:00+09:00", "approved": true
}
- 장면 길이 = 그 문장 음성 길이. 영상이 짧으면 반복, 사진은 천천히 확대.
- 자막은 문장을 12~16자 단위로 끊어 글자 수 비율로 음성에 맞춘다. '작은따옴표' 단어는 노란색.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .common import CFG, MEDIA, ROOT, now, save_post

W, H, FPS = 1080, 1920, 30
YELLOW, WHITE, RED = (255, 212, 59), (255, 255, 255), (235, 52, 52)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def scfg():
    return {**{"layout": "band", "band": 430, "title_size": 96, "sub_size": 82, "sub_y": 0.68, "gap": 0.12,
               "chunk": 14, "zoom": 0.10, "video_audio": 0.0, "bgm_volume": 0.10, "category": 24,
               "mascot": None}, **CFG.get("shorts", {})}


def area(sc):
    """영상이 들어가는 영역 (위쪽 y, 높이). band 레이아웃이면 검정 띠 아래, 아니면 전체 화면."""
    if sc.get("layout") == "band":
        b = int(sc["band"]) // 2 * 2
        return b, H - b
    return 0, H


def font(size, bold=False):
    """굵은 한글 폰트. 서버에 Black이 없으면 Bold로, 그것도 없으면 시스템 한글 폰트로 대체한다.
    (PIL 기본 글꼴로 떨어지면 글자가 깨알처럼 작아지므로 절대 쓰지 않는다)"""
    for p in ([FONT_B] if bold else [FONT, FONT_B]):
        if os.path.exists(p):
            return ImageFont.truetype(p, size, index=1)
    r = subprocess.run(["fc-match", "-f", "%{file}", "Noto Sans CJK KR:weight=bold"], capture_output=True, text=True)
    if r.stdout and os.path.exists(r.stdout):
        return ImageFont.truetype(r.stdout, size)
    raise RuntimeError("한글 폰트가 없습니다: fonts-noto-cjk 설치 필요")


def segs(line, base=None, hi=None):
    return [(p, (hi or YELLOW) if i % 2 else (base or WHITE)) for i, p in enumerate(line.split("'")) if p]


def draw_line(d, y, line, size, max_w=W - 110, stroke=8, anchor_mid=True, base=None, hi=None):
    """한 줄을 가운데 정렬로 그림. 넓으면 글자 크기를 줄인다. 실제 쓴 크기를 돌려준다."""
    s = segs(line, base, hi)
    f = font(size)
    tw = sum(d.textlength(t, font=f) for t, _ in s)
    while tw > max_w and size > 40:
        size -= 3
        f = font(size)
        tw = sum(d.textlength(t, font=f) for t, _ in s)
    x = (W - tw) / 2
    for t, c in s:
        d.text((x, y), t, font=f, fill=c, stroke_width=stroke, stroke_fill=(0, 0, 0))
        x += d.textlength(t, font=f)
    return size


# ── 글자 레이어 ───────────────────────────────────────────────────────
def band_png(hook, out, sc, credit=""):
    """A안(2026.10.17 확정): 위쪽 검정 띠 + 2줄 제목(1줄 노랑, 2줄 흰색) + 띠 아래 빨간 태그 +
    왼쪽 아래 원작자 표기 + 오른쪽 아래 마스코트. 영상 위에 계속 얹는 투명 PNG."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    top, _ = area(sc)
    d.rectangle((0, 0, W, top), fill=(0, 0, 0, 255))
    lines = [l for l in hook["t"].replace("\\n", "\n").split("\n") if l.strip()][:3]
    size = sc["title_size"] if len(lines) <= 2 else int(sc["title_size"] * 0.82)
    lh = int(size * 1.25)
    y = (top - lh * len(lines)) // 2 + int(size * 0.05)
    for i, line in enumerate(lines):
        base_col = YELLOW if i == 0 else WHITE
        parts = [(p, YELLOW if k % 2 else base_col) for k, p in enumerate(line.split("'")) if p]
        f, sz = font(size), size
        tw = sum(d.textlength(t, font=f) for t, _ in parts)
        while tw > W - 90 and sz > 50:
            sz -= 3
            f = font(sz)
            tw = sum(d.textlength(t, font=f) for t, _ in parts)
        x = (W - tw) / 2
        for t, c in parts:
            d.text((x, y), t, font=f, fill=c, stroke_width=4, stroke_fill=(0, 0, 0))
            x += d.textlength(t, font=f)
        y += lh
    if hook.get("tag") and sc.get("tag"):  # 2026.10.17 사용자 결정: 기본으로 태그를 그리지 않는다
        f = font(40)
        tag = "● " + hook["tag"]
        tw = d.textlength(tag, font=f)
        d.rounded_rectangle((36, top + 28, 36 + tw + 44, top + 96), 14, fill=RED)
        d.text((58, top + 62), tag, font=f, fill=WHITE, anchor="lm")
    if credit:
        d.text((40, H - 70), credit, font=font(30, True), fill=(235, 235, 235), stroke_width=3, stroke_fill=(0, 0, 0))
    m = sc.get("mascot")
    if m and os.path.exists(ROOT / m):
        mi = Image.open(ROOT / m).convert("RGBA")
        mi.thumbnail((190, 190))
        im.alpha_composite(mi, (W - mi.width - 30, H - mi.height - 40))
    im.save(out)


def title_png(hook, out, sc):
    """(이전 방식) 위쪽 고정 제목: 어두운 그라데이션 + ● TODAY.WORTHY + 빨간 태그 + 굵은 제목 2~3줄."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = Image.new("L", (1, H))
    for y in range(H):
        g.putpixel((0, y), int(max(0.0, 1 - y / (H * 0.42)) ** 1.3 * 200))
    im.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 0), g.resize((W, H)))
    d = ImageDraw.Draw(im)
    y = int(H * 0.085)
    hd = "● " + CFG["brand"]["handle"].lstrip("@").upper()
    d.text((W // 2, y), hd, font=font(34, True), fill=(255, 255, 255, 235), anchor="mm")
    y += 46
    if hook.get("tag"):
        f = font(38)
        tag = "● " + hook["tag"]
        tw = d.textlength(tag, font=f)
        d.rounded_rectangle(((W - tw) / 2 - 22, y, (W + tw) / 2 + 22, y + 62), 14, fill=RED)
        d.text((W // 2, y + 31), tag, font=f, fill=WHITE, anchor="mm")
        y += 84
    size = sc["title_size"]
    for line in hook["t"].replace("\\n", "\n").split("\n"):
        used = draw_line(d, y, line, size)
        y += int(used * 1.25)
    im.save(out)
    return y  # 제목 아래 끝 위치


def sub_png(text, out, sc, label=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = int(H * sc["sub_y"])
    lines = text.split("\n")
    base = tuple(sc["sub_color"]) if sc.get("sub_color") else None
    hi = tuple(sc["sub_hi"]) if sc.get("sub_hi") else None
    for line in lines:
        used = draw_line(d, y, line, sc["sub_size"], max_w=W - 60, stroke=sc.get("sub_stroke", 12), base=base, hi=hi)
        y += int(used * 1.28)
    if label:
        d.text((40, int(H * sc["sub_y"]) - 70), "※ " + label, font=font(34, True), fill=(235, 235, 235),
               stroke_width=4, stroke_fill=(0, 0, 0))
    im.save(out)


def balanced(text, n):
    """문장을 줄 길이가 비슷하게 나눈다(공백 기준). 줄 수 = 글자수/n 올림(최소 1, 최대 3). 끝 마침표는 뺀다."""
    t = re.sub(r"[.]$", "", text.replace("\n", " ").strip())
    words = t.split()
    k = max(1, min(3, -(-len(t.replace(" ", "")) // n)))
    if k == 1 or len(words) < 2:
        return t
    best = None
    import itertools
    for cuts in itertools.combinations(range(1, len(words)), k - 1):
        parts = [" ".join(words[a:b]) for a, b in zip((0,) + cuts, cuts + (len(words),))]
        if any(p.count("'") % 2 for p in parts):
            continue
        score = max(len(p) for p in parts) - 6 * sum(p.endswith(",") for p in parts[:-1])  # 쉼표에서 끊기 선호
        if best is None or score < best[0]:
            best = (score, parts)
    return "\n".join(re.sub(r",$", "", p) for p in best[1]) if best else t


def chunks(text, n):
    """자막 덩어리: 문장부호에서 먼저 끊고, n자(공백 제외)를 넘기 전에 띄어쓰기에서 끊는다.
    작은따옴표 강조가 덩어리 사이에서 갈리지 않게 한다."""
    words = text.replace("\n", " ").split()
    out, cur = [], []
    clen = lambda ws: sum(len(w) for w in ws)
    for w in words:
        if cur and clen(cur) + len(w) > n and " ".join(cur).count("'") % 2 == 0:
            out.append(" ".join(cur))
            cur = []
        cur.append(w)
        if re.search(r"[.!?…,]$", w) and clen(cur) >= n * 0.5 and " ".join(cur).count("'") % 2 == 0:
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return [re.sub(r"[.,]$", "", c) for c in out]  # 자막 끝 마침표·쉼표는 뺀다(쇼츠 관례)


# ── 배경 ──────────────────────────────────────────────────────────────
def fit_cover(img, w, h, cx=0.5, cy=0.5):
    s = max(w / img.width, h / img.height)
    img = img.resize((max(w, int(img.width * s) + 1), max(h, int(img.height * s) + 1)), Image.LANCZOS)
    x, y = int((img.width - w) * cx), int((img.height - h) * cy)
    return img.crop((x, y, x + w, y + h))


def still(path, out, cx=0.5, cy=0.5, sc=None):
    """사진을 영상 영역에 맞춘다. band 레이아웃: 띠 아래(1080x1490)를 꽉 채운다(가로 사진도 크롭)."""
    img = Image.open(path).convert("RGB")
    if sc and sc.get("layout") == "band":
        _, ah = area(sc)
        fit_cover(img, W, ah, cx, cy).save(out, quality=94)
        return
    if img.height / img.width >= 1.25:
        fit_cover(img, W, H, cx, cy).save(out, quality=94)
        return
    bg = fit_cover(img, W, H).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), 0.45)
    fh = min(int(img.height * W / img.width), int(H * 0.42))
    fg = fit_cover(img, W, fh, cx, cy)
    bg.paste(fg, (0, max(int(H * 0.33), int(H * 0.50) - fh // 2)))  # 위쪽 제목을 피해서
    bg.save(out, quality=94)


def blank(out, h=H):
    Image.new("RGB", (W, h), (14, 14, 18)).save(out, quality=94)


def probe(path, what="format=duration"):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", what, "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return r.stdout.strip()


def has_audio(path):
    return bool(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                                "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip())


# ── 장면 합성 ─────────────────────────────────────────────────────────
def word_times(subs, words, dur):
    """타입캐스트 단어 시각으로 자막 덩어리 시간을 정한다. 덩어리의 단어 수만큼 순서대로 묶는다.
    단어 수가 안 맞으면(자막을 따로 쓴 경우 등) None."""
    n = [len(c.split()) for c in subs]
    if not words or sum(n) != len(words):
        return None
    times, i = [], 0
    for k, m in enumerate(n):
        a = 0.0 if k == 0 else words[i]["start"]
        i += m
        b = dur if k == len(n) - 1 else words[i]["start"]
        times.append((a, b))
    return times


def scene_clip(base, sc_i, scene, title, voice_mp3, tmp, sc, out, words=None):
    adur = float(probe(voice_mp3))
    dur = round(max(adur + sc["gap"], float(scene.get("min", 0))), 2)
    if scene.get("dur"):  # 장면 길이 직접 지정(내레이션 없는 영상에서 주로 사용)
        dur = float(scene["dur"])
        adur = max(0.5, dur - sc["gap"])
    if sc.get("caption_lines") and not scene.get("nosub"):  # 내레이션 없는 '감동 자막' 방식: 한 장면 = 문장 하나를 2줄로
        subs = [balanced(scene.get("sub") or scene["say"], sc["caption_lines"])]
    else:
        subs = chunks(scene.get("sub") or scene["say"], sc["chunk"]) if not scene.get("nosub") else []
    times = word_times(subs, words, dur) if not scene.get("sub") else None
    if times is None:  # 단어 시각이 없으면(Edge TTS 등) 글자 수 비율로 나눈다
        lens = [max(2, len(c.replace(" ", ""))) for c in subs]
        tot, t, times = sum(lens) or 1, 0.0, []
        for k, l in enumerate(lens):
            a = t
            t += adur * l / tot
            times.append((a, dur if k == len(lens) - 1 else t))
    pngs = []
    for k, c in enumerate(subs):
        p = f"{tmp}/s{sc_i:02d}_{k:02d}.png"
        sub_png(c, p, sc, scene.get("label"))
        pngs.append(p)
    if not subs and scene.get("label"):
        p = f"{tmp}/s{sc_i:02d}_lb.png"
        sub_png("", p, sc, scene["label"])
        pngs.append(p)
        times.append((0, dur))

    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    v = scene.get("video")
    if v:
        src = str(base / v["src"])
        cmd += ["-stream_loop", "-1", "-ss", str(v.get("start", 0)), "-t", str(dur), "-i", src]
        vw, vh = map(int, probe(src, "stream=width,height").split("\n")[0].split(",")[:2])
        fit = v.get("fit", "auto")
        top, ah = area(sc)
        if fit == "auto":  # 가로 영상은 잘리지 않게 가운데 띠로, 세로 영상은 꽉 채움
            fit = "fit" if vw / vh > (1.1 if sc.get("layout") != "band" else 9.9) else "fill"  # band: 기본 꽉 채움(x로 크롭 위치)
        if sc.get("layout") == "band":
            if fit == "fit":  # 아주 넓은 영상: 영역 안 가운데 띠 + 흐린 배경
                fh = min(int(vh * W / vw) // 2 * 2, ah)
                vf = (f"[0:v]split[a0][b0];[a0]scale=-2:{ah},crop=1080:{ah},boxblur=30:2,eq=brightness=-0.18[bb];"
                      f"[b0]scale=1080:-2:flags=lanczos,crop=1080:{fh}[ff];[bb][ff]overlay=0:{(ah - fh) // 2},"
                      f"pad=1080:1920:0:{top}:black,setsar=1,fps={FPS},format=yuv420p[bg]")
            else:
                vf = (f"[0:v]scale='if(gt(a,1080/{ah}),-2,1080)':'if(gt(a,1080/{ah}),{ah},-2)':flags=lanczos,"
                      f"crop=1080:{ah}:(in_w-1080)*{v.get('x', 0.5)}:(in_h-{ah})*{v.get('y', 0.5)},"
                      f"pad=1080:1920:0:{top}:black,setsar=1,fps={FPS},format=yuv420p[bg]")
        elif fit == "fit":
            fh = min(int(vh * W / vw) // 2 * 2, int(H * 0.42) // 2 * 2)
            top = max(int(H * 0.33), int(H * 0.50) - fh // 2)
            vf = (f"[0:v]split[a0][b0];[a0]scale=-2:1920,crop=1080:1920,boxblur=30:2,eq=brightness=-0.18[bb];"
                  f"[b0]scale=1080:-2:flags=lanczos,crop=1080:{fh}:0:(in_h-{fh})*{v.get('y', 0.5)}[ff];"
                  f"[bb][ff]overlay=0:{top},setsar=1,fps={FPS},format=yuv420p[bg]")
        else:
            vf = (f"[0:v]scale='if(gt(a,0.5625),-2,1080)':'if(gt(a,0.5625),1920,-2)':flags=lanczos,"
                  f"crop=1080:1920:(in_w-1080)*{v.get('x', 0.5)}:(in_h-1920)*{v.get('y', 0.5)},"
                  f"setsar=1,fps={FPS},format=yuv420p[bg]")
        if v.get("blur"):  # 원본에 박힌 글자(욕설 캡션 등)를 흐리게: [x, y, w, h] 원본 좌표
            bx, by, bw, bh = v["blur"]
            vf = vf.replace("[0:v]", f"[0:v]delogo=x={bx}:y={by}:w={bw}:h={bh},", 1)
        vol = float(v.get("audio", sc["video_audio"]))
        orig = has_audio(src) and vol > 0
    else:
        st = f"{tmp}/still{sc_i:02d}.jpg"
        if scene.get("img"):
            still(str(base / scene["img"]), st, scene.get("x", 0.5), scene.get("y", 0.5), sc)
        else:
            blank(st, area(sc)[1] if sc.get("layout") == "band" else H)
        z = float(scene.get("zoom", sc["zoom"]))
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", st]
        top, ah = area(sc)
        vf = (f"[0:v]scale=w='trunc(1080*(1+{z}*t/{dur})/2)*2':h=-2:eval=frame:flags=bicubic,"
              f"crop=1080:{ah},pad=1080:1920:0:{top}:black,setsar=1,fps={FPS},format=yuv420p[bg]")
        orig, vol = False, 0
    n_in = 1
    last = "bg"
    if title and scene.get("title", True):
        cmd += ["-i", title]
        vf += f";[{last}][{n_in}:v]overlay=0:0[t{n_in}]"
        last = f"t{n_in}"
        n_in += 1
    for p, (a, b) in zip(pngs, times):
        cmd += ["-i", p]
        vf += f";[{last}][{n_in}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[t{n_in}]"
        last = f"t{n_in}"
        n_in += 1
    cmd += ["-i", voice_mp3]
    vi = n_in
    vf += f";[{vi}:a]aresample=44100,aformat=channel_layouts=stereo,apad=whole_dur={dur}[na]"
    if orig:
        vf += (f";[0:a]aresample=44100,aformat=channel_layouts=stereo,volume={vol},apad=whole_dur={dur}[oa]"
               f";[na][oa]amix=inputs=2:duration=first:normalize=0[a]")
    else:
        vf += ";[na]anull[a]"
    cmd += ["-filter_complex", vf, "-map", f"[{last}]", "-map", "[a]", "-t", str(dur),
            "-c:v", "libx264", "-preset", "medium", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "20",
            "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2", out]
    subprocess.run(cmd, check=True)
    return dur


class WaitTTS(Exception):
    """맥북(로컬)에서 목소리를 만들어 올 때까지 기다리는 중."""


def tts_key(text, c, ctx):
    import hashlib
    k = {"t": text, "v": c.get("voice_id"), "m": c.get("model"), "e": c.get("emotion"), "tp": c.get("tempo"),
         "i": c.get("intensity"), "p": (ctx or {}).get("previous_text", ""), "n": (ctx or {}).get("next_text", "")}
    return hashlib.sha1(json.dumps(k, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]


def local_tts_on(d):
    """config shorts.tts.mode: local 이면, 서버(GitHub Actions)에서는 타입캐스트를 직접 부르지 않고
    맥북이 만들어 올린 media/<id>/tts/<key>.mp3 를 쓴다(2026.10.17: 클라우드 IP 이상활동 경고 대응)."""
    from .tts import cfg as tts_cfg
    c = {**tts_cfg(), **(d.get("voice") or {})}
    return (c.get("mode") == "local" and c.get("engine") == "typecast" and os.environ.get("GITHUB_ACTIONS")
            and d.get("narration") is not False), c


def render(d):
    ch = (CFG.get("shorts", {}).get("channels") or {}).get((d.get("yt") or {}).get("channel") or "", {})
    if ch.get("voice"):  # 채널 기본 목소리(예: 쇼핑 채널 = 진우). 원고 voice가 있으면 그게 우선
        d = {**d, "voice": {**ch["voice"], **(d.get("voice") or {})}}
    sc = {**scfg(), **(ch.get("style") or {}), **d.get("style", {})}  # 채널별 디자인 덮어쓰기(마스코트·띠 높이·자막 크기 등)
    from .tts import cfg as tts_cfg
    if tts_cfg().get("engine") == "none" and not (d.get("voice") or {}).get("engine"):
        d = {**d, "narration": False}  # TTS 일시 중지(engine: none): 자막+원본 소리+배경음악으로 만든다
    if d.get("narration") is False:  # TTS 없이 원본 소리 + 배경음악(감동형 등). 자막이 이야기를 끌고 간다
        d = {**d, "voice": {**(d.get("voice") or {}), "engine": "silent"}}
        sc["video_audio"] = sc.get("quiet_video_audio", 1.0)
        sc["bgm_volume"] = sc.get("quiet_bgm_volume", 0.35)
        # 자막: 하루일기식 — 작은 초록 글씨 2줄, 화면 가운데 위쪽(2026.10.17 사용자 요청)
        for k, v in {"sub_size": 72, "sub_y": 0.40, "sub_color": [120, 255, 90], "sub_hi": [255, 230, 60],
                     "sub_stroke": 7, "caption_lines": 13}.items():
            sc[k] = (sc.get("quiet") or {}).get(k, v)
    base = MEDIA / d["id"]
    os.makedirs(base, exist_ok=True)
    tmp = tempfile.mkdtemp()
    from .tts import say
    title = None
    if d.get("hook"):
        title = f"{tmp}/title.png"
        if sc.get("layout") == "band":
            credit = d.get("credit") or ("영상: " + ", ".join(list(dict.fromkeys(d.get("photo_credits", [])))[:2])
                                         if d.get("photo_credits") else "")
            band_png(d["hook"], title, sc, credit)
        else:
            title_png(d["hook"], title, sc)
    local_on, lc = local_tts_on(d)
    if local_on:  # 맥북이 만든 목소리가 다 있는지 확인, 없으면 요청서를 남기고 대기
        sl, need = d["scenes"], []
        for i, scene in enumerate(sl):
            ctx = {"previous_text": sl[i - 1]["say"].replace("'", "") if i else "",
                   "next_text": sl[i + 1]["say"].replace("'", "") if i + 1 < len(sl) else ""}
            text = scene["say"].replace("'", "")
            key = tts_key(text, lc, ctx)
            if not (base / "tts" / f"{key}.mp3").exists():
                need.append({"key": key, "text": text, "ctx": ctx,
                             "voice": {k: lc.get(k) for k in ("voice_id", "model", "emotion", "intensity", "tempo")}})
        if need:
            q = ROOT / "state" / "tts_queue"
            q.mkdir(parents=True, exist_ok=True)
            json.dump({"id": d["id"], "created": now().isoformat(), "items": need},
                      open(q / f"{d['id']}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            raise WaitTTS(f"{len(need)}개 장면 목소리를 맥북에서 만드는 중")
    segs_, engines, total = [], [], 0.0
    for i, scene in enumerate(d["scenes"]):
        mp3 = f"{tmp}/v{i:02d}.mp3"
        sc_list = d["scenes"]
        ctx = {"previous_text": sc_list[i - 1]["say"].replace("'", "") if i else "",
               "next_text": sc_list[i + 1]["say"].replace("'", "") if i + 1 < len(sc_list) else ""}
        if local_on:
            key = tts_key(scene["say"].replace("'", ""), lc, ctx)
            f = base / "tts" / f"{key}.mp3"
            shutil.copy(f, mp3)
            words = json.load(open(base / "tts" / f"{key}.json", encoding="utf-8")) or None
            eng = "typecast"
        else:
            eng, words = say(scene["say"].replace("'", ""), mp3, d.get("voice"), ctx=ctx, timed=True)
        engines.append(eng)
        seg = f"{tmp}/seg{i:02d}.mp4"
        total += scene_clip(base, i, scene, title, mp3, tmp, sc, seg, words)
        segs_.append(seg)
        print(f"장면 {i + 1}/{len(d['scenes'])} {engines[-1]} 누적 {total:.1f}초")
    lst = f"{tmp}/list.txt"
    open(lst, "w").write("".join(f"file '{s}'\n" for s in segs_))
    joined = f"{tmp}/joined.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    joined], check=True)
    out = str(base / "short.mp4")
    bgm = d.get("bgm") or sc.get("bgm")
    if bgm and os.path.exists(ROOT / bgm):
        vol = float(d.get("bgm_volume", sc["bgm_volume"]))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined, "-stream_loop", "-1", "-i", str(ROOT / bgm),
                        "-filter_complex",
                        f"[1:a]volume={vol},afade=t=out:st={max(0, total - 1.5):.2f}:d=1.5[b];"
                        f"[0:a][b]amix=inputs=2:duration=first:normalize=0[a]",
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", out], check=True)
    else:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined, "-c", "copy", "-movflags", "+faststart",
                        out], check=True)
    # 미리보기용 첫 화면
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.6", "-i", out, "-frames:v", "1", "-q:v", "3",
                    str(base / "short_cover.jpg")], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"완성: {out} ({total:.1f}초, TTS {sorted(set(engines))})")
    if total > 60:
        print("⚠️ 60초를 넘었어요. 쇼츠는 3분까지 되지만 추천은 15~45초가 유리합니다.")
    return out, total, engines


def description(d, engines):
    y = d.get("yt", {})
    parts = [y.get("description", "").strip()]
    src = ", ".join(f"{s.get('publisher', '')} {s.get('date', '')}".strip() for s in d.get("sources", [])[:3])
    note = []
    if src:
        note.append(f"출처: {src}")
    credits = list(dict.fromkeys(d.get("photo_credits", [])))
    if credits:
        note.append("사진·영상: " + ", ".join(credits[:6]))
    if any(s.get("label") for s in d["scenes"]):
        note.append("※ 일부 장면은 AI로 만든 참고 이미지입니다.")
    if "typecast" in engines:
        note.append("음성: Typecast")
    if d.get("bgm_credit"):  # CC BY 음악 등 표기 의무가 있는 곡
        note.append("음악: " + d["bgm_credit"])
    if note:
        parts.append("\n".join(note))
    tags = [t.lstrip("#") for t in y.get("tags", [])][:4]
    parts.append(" ".join("#" + t for t in ["shorts"] + tags))
    return "\n\n".join(p for p in parts if p)


def send_preview(post, path):
    from . import telegram_bot as tg
    tg.send_video(path, f"▶️ 쇼츠 미리보기 {post['seconds']:.0f}초 · TTS {','.join(post['tts'])}")
    when = "승인 즉시" if post.get("publish_now") else post["publish_at"][5:16].replace("T", " ")
    text = (f"🎬 [유튜브 쇼츠] {post['topic']}\n공개: {post['yt']['privacy']} · {when}\n\n"
            f"제목: {post['yt']['title']}\n\n──── 설명란 ────\n{post['yt']['description']}\n\n"
            f"태그: {', '.join(post['yt'].get('tags', []))}")
    return tg.send_text(text, buttons=[[{"text": "✅ 업로드", "callback_data": f"ok:{post['id']}"},
                                        {"text": "❌ 거절", "callback_data": f"no:{post['id']}"}]])["message_id"]


def one(d):
    if d.get("mode", "render") not in ("render", "send"):
        return
    try:
        out, total, engines = render(d)
    except WaitTTS as e:
        print("⏳", e)
        if os.environ.get("TELEGRAM_BOT_TOKEN"):
            from . import telegram_bot as tg
            tg.send_text(f"🎙 '{d.get('topic') or d['id']}' 목소리를 맥북에서 만드는 중이에요. "
                         "맥북이 켜져 있으면 몇 분 안에 미리보기가 와요(꺼져 있으면 켜질 때까지 대기).")
        return
    if d["mode"] != "send":
        return
    y = d.get("yt", {})
    title = y.get("title") or d["hook"]["t"].replace("\\n", " ").replace("\n", " ").replace("'", "")
    if "#shorts" not in title.lower() and len(title) <= 90:
        title += " #shorts"
    post = {"id": d["id"], "kind": "short", "status": "pending", "created_at": now().isoformat(),
            "publish_at": d.get("publish_at") or now().isoformat(), "publish_now": bool(d.get("publish_now")),
            "topic": d.get("topic") or title, "sources": d.get("sources", []), "seconds": total, "tts": sorted(set(engines)),
            "files": [os.path.relpath(out, ROOT)],
            "yt": {"title": title[:100], "description": description(d, engines)[:4900],
                   "tags": [t.lstrip("#") for t in y.get("tags", [])][:15],
                   "category": int(y.get("category", scfg()["category"])), "privacy": y.get("privacy", "public"),
                   "synthetic": bool(y.get("synthetic", any(s.get("label") for s in d["scenes"]))),
                   "channel": y.get("channel")}}
    post["tg_msg"] = send_preview(post, out)
    if d.get("approved"):  # 채팅에서 이미 승인받은 경우만. publish_now는 '승인되면 바로 공개'라는 뜻일 뿐 승인을 대신하지 않는다
        post.update(status="approved", decided_at=now().isoformat())
    save_post(post)


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    for d in (data if isinstance(data, list) else [data]):
        one(d)


if __name__ == "__main__":
    main(sys.argv[1])
