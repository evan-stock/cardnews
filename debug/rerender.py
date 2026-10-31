# 2026.10.31 임시: 폴란드 헌재 릴스 영상 받아쓰기(faster-whisper). 끝나면 원래 rerender.py로 되돌림.
import json, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "faster-whisper"], check=True)
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
base = "media/20261031-polandcourt-reel/video/"
out = {}
for v in ["v1", "v2"]:
    segs, info = m.transcribe(base + v + ".mp4", language="pl", word_timestamps=True, vad_filter=False)
    out[v] = [{"s": round(s.start, 2), "e": round(s.end, 2), "t": s.text,
               "w": [[round(w.start, 2), round(w.end, 2), w.word] for w in (s.words or [])]} for s in segs]
json.dump(out, open(base + "transcript.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False)[:3000])
