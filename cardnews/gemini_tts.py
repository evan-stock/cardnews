"""Gemini TTS(2026.10.22 사용자 결정): 필재(맥북)가 안 될 때 쓰는 대체 목소리 = Gemini 'Sadaltager', 필재 속도로 맞춤.
무료 등급은 하루 10번만 부를 수 있어서 영상 하나당 1번만 부른다(내레이션 문장을 한 번에 읽히고 쉼에서 자름).
한도 초과·키 없음·자르기 실패면 None 을 돌려주고, 렌더러는 계속 맥북 목소리를 기다린다.
결과는 media/<id>/tts/gemini_<key>/<장면번호>.mp3 에 남겨 다시 렌더할 때 API 를 또 부르지 않는다."""
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile

URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
DEFAULT = {
    "enabled": True,
    "model": "gemini-3.8-flash-tts",
    "voice": "Sadaltager",
    "style": "유튜브 쇼츠 동물 영상 내레이션. 장난기 있는 중년 남성 다큐 해설자 말투, 또박또박",
    "tempo": 1.23,      # 10.22 시험: 1.23배(음높이 유지)가 필재 속도와 비슷
    "volume_db": 3.0,   # 필재보다 3~4dB 작게 나옴
}


def cfg(conf, d=None):
    """기본값 ← config shorts.tts.gemini ← 원고 voice.gemini(채널·영상별 목소리, 2026.10.23 댓글로 키우는 아이)"""
    over = ((d or {}).get("voice") or {}).get("gemini") or {}
    return {**DEFAULT, **((conf.get("shorts", {}).get("tts") or {}).get("gemini") or {}), **over}


def _silences(path, noise="-40dB", min_d=0.25):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", f"silencedetect=n={noise}:d={min_d}", "-f", "null", "-"],
                       capture_output=True, text=True)
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return list(zip(st, en))


def _duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout.strip())


def _pick_cuts(inner, dur, weights):
    """문장 길이 비율로 예상한 경계 위치에 가장 가까우면서 긴 쉼을 순서대로 고른다(2026.10.23).
    예전 방식(가장 긴 쉼 n-1개)은 한 문장 안의 쉼(마침표·쉼표)을 경계로 잘못 고르는 일이 있었다."""
    n = len(weights); tot = float(sum(weights)); cum, exp = 0.0, []
    for w in weights[:-1]:
        cum += w; exp.append(dur * cum / tot)
    S = len(inner); INF = float("inf")
    cost = lambda k, j: abs((inner[j][0] + inner[j][1]) / 2 - exp[k]) - 1.5 * (inner[j][1] - inner[j][0])
    best = [[INF] * S for _ in range(n - 1)]; prev = [[-1] * S for _ in range(n - 1)]
    for j in range(S):
        best[0][j] = cost(0, j)
    for k in range(1, n - 1):
        run, arg = INF, -1
        for j in range(S):
            if j > 0 and best[k - 1][j - 1] < run:
                run, arg = best[k - 1][j - 1], j - 1
            if arg >= 0:
                best[k][j] = run + cost(k, j); prev[k][j] = arg
    j = min(range(S), key=lambda x: best[n - 2][x]); out = []
    for k in range(n - 2, -1, -1):
        out.append(inner[j]); j = prev[k][j]
    return out[::-1]


def split_lines(wav, n, outdir, tempo, vol_db, weights=None):
    """한 파일을 n 문장으로 자른다. weights(문장별 글자 수)가 있으면 예상 위치 기준(_pick_cuts),
    없으면 가운데 쉼 중 가장 긴 n-1 개를 경계로 쓴다. 문장마다 앞뒤 무음을 자르고 tempo 배속."""
    dur = _duration(wav)
    inner = [(a, b) for a, b in _silences(wav) if a > 0.05 and b < dur - 0.05]
    if len(inner) < n - 1:
        return None
    if weights and n > 1:
        cuts = _pick_cuts(inner, dur, weights)
    else:
        cuts = sorted(sorted(inner, key=lambda s: s[1] - s[0], reverse=True)[:n - 1])
    bounds = [0.0] + [(a + b) / 2 for a, b in cuts] + [dur]
    trim = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
            "silenceremove=start_periods=1:start_threshold=-45dB,areverse")
    outs = []
    for i in range(n):
        o = os.path.join(outdir, f"{i}.mp3")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af",
                        f"atrim={bounds[i]:.3f}:{bounds[i + 1]:.3f},asetpts=PTS-STARTPTS,{trim},"
                        f"atempo={tempo:.3f},volume={vol_db}dB", "-ar", "44100", "-b:a", "160k", o], check=True)
        if _duration(o) < 0.3:
            return None
        outs.append(o)
    return outs


def _request(text, c, key):
    import requests
    body = {"model": c["model"],
            "input": [{"type": "user_input", "content": [
                {"type": "text", "text": text,
                 **({"annotations": [{"type": "speech_metadata", "style": c["style"]}]} if c.get("style") else {})}]}],
            "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [{"voice": c["voice"]}]}}
    for attempt in range(2):
        r = requests.post(URL, json=body, headers={"x-goog-api-key": key}, timeout=180)
        if r.status_code == 200:
            for step in r.json().get("steps", []):
                for part in step.get("content", []) or []:
                    if part.get("data"):
                        return base64.b64decode(part["data"]), ""
            return None, "응답에 오디오 없음"
        if r.status_code == 429:  # 하루 한도 — 다시 해도 소용없음
            return None, "하루 한도 초과(429)"
        if r.status_code < 500:
            return None, f"HTTP {r.status_code} {r.text[:200]}"
    return None, f"HTTP {r.status_code}"


def median_pitch(paths):
    """음성 파일들의 중간 음높이(Hz). 자기상관으로 대략 잰다(2026.10.25, 3화 목소리가 2화보다 높게 나온 일)."""
    import numpy as np
    sr, N, F = 16000, 640, []
    for f in paths:
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(f), "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                             capture_output=True).stdout
        y = np.frombuffer(raw, np.int16).astype(float) / 32768
        for i in range(0, len(y) - N, 320):
            x = y[i:i + N]
            if np.sqrt((x ** 2).mean()) < 0.02:
                continue
            x = x - x.mean(); ac = np.correlate(x, x, "full")[N - 1:]
            lo, hi = sr // 300, sr // 65; k = lo + int(np.argmax(ac[lo:hi]))
            if ac[0] > 0 and ac[k] / ac[0] > 0.45:
                F.append(sr / k)
    return float(np.median(F)) if len(F) > 20 else None


def match_pitch(files, target, outdir):
    """Gemini 는 같은 목소리·지시문이어도 부를 때마다 톤이 달라진다 → 원고 voice.gemini.pitch_hz 에 맞춰
    음높이만 옮긴다(길이·타이밍 그대로, 반음 0.5개 이내면 그대로 둔다). 실패하면 원본을 돌려준다."""
    try:
        cur = median_pitch(files)
    except Exception as e:  # numpy 없음 등
        print(f"Gemini TTS: 음높이 측정 실패({e}) → 원본 사용")
        return files
    if not cur:
        return files
    ratio = max(0.8, min(1.25, target / cur))
    import math
    semis = 12 * math.log2(ratio)
    print(f"Gemini TTS: 음높이 {cur:.0f}Hz → 목표 {target}Hz ({semis:+.1f}반음)")
    if abs(semis) < 0.5:
        return files
    os.makedirs(outdir, exist_ok=True)
    outs = []
    for f in files:
        o = os.path.join(outdir, os.path.basename(str(f)))
        if not os.path.exists(o):
            r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-af",
                                f"rubberband=pitch={ratio:.4f}:formant=preserved", "-ar", "44100", "-b:a", "160k", o])
            if r.returncode != 0:  # rubberband 없는 ffmpeg: 재생 속도를 바꿨다가 길이만 되돌림
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-af",
                                f"asetrate=44100*{ratio:.4f},aresample=44100,atempo={1 / ratio:.4f}", "-b:a", "160k", o], check=True)
        outs.append(o)
    return outs


def scene_voices(d, base, conf):
    """내레이션 장면 번호 → mp3 경로. Gemini 를 못 쓰면 (None, 이유)."""
    files, why = _scene_voices(d, base, conf)
    c = cfg(conf, d)
    if files and c.get("pitch_hz"):
        idx = list(files)
        cache = os.path.dirname(files[idx[0]])
        outs = match_pitch([files[i] for i in idx], float(c["pitch_hz"]), os.path.join(cache, f"pitch_{int(c['pitch_hz'])}"))
        files = dict(zip(idx, outs))
    return files, why


def _scene_voices(d, base, conf):
    """내레이션 장면 번호 → mp3 경로. Gemini 를 못 쓰면 (None, 이유)."""
    c = cfg(conf, d)
    if not c.get("enabled") or (d.get("voice") or {}).get("engine") not in (None, "gemini"):
        return None, "꺼짐"
    idx = [i for i, s in enumerate(d["scenes"]) if (s.get("say") or "").strip()]
    if not idx:
        return None, "내레이션 없음"
    lines = [d["scenes"][i]["say"].replace("'", "").strip() for i in idx]
    k = hashlib.sha1(json.dumps([lines, c["model"], c["voice"], c["style"], c["tempo"], c["volume_db"]],
                                ensure_ascii=False).encode()).hexdigest()[:12]
    cache = base / "tts" / f"gemini_{k}"
    files = [cache / f"{j}.mp3" for j in range(len(lines))]
    if all(f.exists() for f in files):
        return {i: str(f) for i, f in zip(idx, files)}, "저장본"
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        return None, "GEMINI_API_KEY 없음"
    # 문장 사이에 긴 쉼을 넣어 한 번에 읽힌다(하루 10번 한도 → 영상당 1번)
    text = " <long pause> ".join(lines) if len(lines) > 1 else lines[0]
    wav, why = _request(text, c, key)
    if not wav:
        return None, why
    tmp = tempfile.mkdtemp()
    try:
        src = os.path.join(tmp, "all.wav")
        open(src, "wb").write(wav)
        outs = split_lines(src, len(lines), tmp, c["tempo"], c["volume_db"],
                          [max(1, len(l.replace(" ", ""))) for l in lines])
        if not outs:
            return None, f"문장 {len(lines)}개로 자르기 실패"
        cache.mkdir(parents=True, exist_ok=True)
        for o, f in zip(outs, files):
            shutil.copy(o, f)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return {i: str(f) for i, f in zip(idx, files)}, "새로 만듦"
