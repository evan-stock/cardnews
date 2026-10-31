# 2026.10.31 임시: 폴란드 헌재 릴스 영상 받아쓰기(faster-whisper). 끝나면 원래 rerender.py로 되돌림.
import json, subprocess, sys, traceback, os
base = "media/20261031-polandcourt-reel/video/"
log = []
try:
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "faster-whisper"], capture_output=True, text=True)
    log.append(r.stdout[-1500:] + r.stderr[-1500:])
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    out = {}
    for v in ["v1", "v2"]:
        src = base + v + ".wav"
        segs, info = m.transcribe(src, language="pl", word_timestamps=True)
        out[v] = [{"s": round(s.start, 2), "e": round(s.end, 2), "t": s.text,
                   "w": [[round(w.start, 2), round(w.end, 2), w.word] for w in (s.words or [])]} for s in segs]
    json.dump(out, open(base + "transcript.json", "w"), ensure_ascii=False, indent=1)
except Exception:
    log.append(traceback.format_exc())
open(base + "transcript_log.txt", "w").write("\n".join(log))
