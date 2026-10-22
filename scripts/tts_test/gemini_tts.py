"""Gemini TTS 시험: drafts/gemini_tts_test.json 의 문장들을 목소리별로 만들어 state/tts_test/ 에 저장.
키는 환경변수 GEMINI_API_KEY 에서만 읽고, 로그에 찍지 않는다."""
import base64, json, os, subprocess, sys, time
import requests

cfg = json.load(open("drafts/gemini_tts_test.json"))
key = os.environ.get("GEMINI_API_KEY", "").strip()
out = "state/tts_test"
os.makedirs(out, exist_ok=True)
if not key:
    print("GEMINI_API_KEY 없음"); sys.exit(1)
print(f"키 있음, 글자 수 {len(key)}")

URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
model = cfg.get("model", "gemini-3.8-flash-tts")
style = cfg.get("style", "")
lines = cfg["lines"]
gap = cfg.get("gap", 0.5)


def tts(text, voice):
    content = {"type": "text", "text": text}
    if style:
        content["annotations"] = [{"type": "speech_metadata", "style": style}]
    body = {
        "model": model,
        "input": [{"type": "user_input", "content": [content]}],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voice}]},
    }
    for attempt in range(3):
        r = requests.post(URL, json=body, headers={"x-goog-api-key": key}, timeout=120)
        if r.status_code == 200:
            break
        print(f"  {voice} HTTP {r.status_code}: {r.text[:400]}")
        time.sleep(5 * (attempt + 1))
    else:
        return None
    d = r.json()
    for step in d.get("steps", []):
        for c in step.get("content", []) or []:
            if c.get("data"):
                return base64.b64decode(c["data"])
    print(f"  {voice} 응답에 오디오 없음: {json.dumps(d)[:400]}")
    return None


report = []
for voice in cfg["voices"]:
    parts = []
    for i, t in enumerate(lines):
        wav = tts(t, voice)
        if not wav:
            break
        p = f"{out}/_{voice}_{i}.wav"
        open(p, "wb").write(wav)
        parts.append(p)
    if len(parts) != len(lines):
        report.append(f"{voice}: 실패"); continue
    # 문장 사이 gap 초 쉬고 이어 붙여 mp3 로
    inputs, filt = [], []
    for i, p in enumerate(parts):
        inputs += ["-i", p]
        filt.append(f"[{i}:a]aresample=44100,apad=pad_dur={gap}[a{i}]")
    filt.append("".join(f"[a{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[o]")
    dst = f"{out}/gemini_{voice}.mp3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
                    "-map", "[o]", "-b:a", "128k", dst], check=True)
    for p in parts:
        os.remove(p)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst],
                         capture_output=True, text=True).stdout.strip()
    report.append(f"{voice}: 성공 {float(dur):.1f}초")

# 비교용 필재(타입캐스트) 원본도 같은 간격으로 이어 붙임
ref = cfg.get("ref_mp3s") or []
if ref:
    inputs, filt = [], []
    for i, p in enumerate(ref):
        inputs += ["-i", p]
        filt.append(f"[{i}:a]aresample=44100,apad=pad_dur={gap}[a{i}]")
    filt.append("".join(f"[a{i}]" for i in range(len(ref))) + f"concat=n={len(ref)}:v=0:a=1[o]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
                    "-map", "[o]", "-b:a", "128k", f"{out}/typecast_piljae.mp3"], check=True)
    report.append("필재 비교 파일: typecast_piljae.mp3")

msg = "\n".join(report)
print(msg)
open(f"{out}/report.txt", "w").write(f"model {model}\nstyle {style}\n{msg}\n")
