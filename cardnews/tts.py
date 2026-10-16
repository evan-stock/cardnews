"""쇼츠 내레이션 TTS. 타입캐스트 API(무료 플랜 월 3만 크레딧=3만 글자)를 먼저 쓰고,
키가 없거나·월 한도를 넘었거나·오류가 나면 edge-tts(무료, 캡컷 기본 목소리와 비슷한 느낌)로 자동 대체한다.

사용:
  python -m cardnews.tts voices            타입캐스트 한국어 목소리 목록(쇼츠용 우선) → 텔레그램/화면
  python -m cardnews.tts say "문장" out.mp3  한 문장 시험 생성
설정: config.yaml 의 shorts.tts
"""
import json
import os
import subprocess
import sys

import requests

from .common import CFG, now, read_text, write_text

API = "https://api.typecast.ai"


def cfg():
    return {**{"engine": "typecast", "model": "ssfm-v30", "voice_id": "", "emotion": "normal", "intensity": 1.0,
               "tempo": 1.1, "monthly_cap": 28000, "edge_voice": "ko-KR-InJoonNeural", "edge_rate": "+15%"},
            **CFG.get("shorts", {}).get("tts", {})}


# ── 사용량 기록(월별 글자 수) ─────────────────────────────────────────
def _usage():
    try:
        u = json.loads(read_text("typecast_usage.json", "{}") or "{}")
    except Exception:
        u = {}
    return u


def used_this_month():
    return int(_usage().get(now().strftime("%Y-%m"), 0))


def _add_usage(n):
    u = _usage()
    k = now().strftime("%Y-%m")
    u[k] = int(u.get(k, 0)) + n
    write_text("typecast_usage.json", json.dumps(u))


# ── 엔진 ─────────────────────────────────────────────────────────────
def typecast(text, out, c):
    key = os.environ.get("TYPECAST_API_KEY")
    if not key:
        raise RuntimeError("TYPECAST_API_KEY 없음")
    if not c.get("voice_id"):
        raise RuntimeError("config.yaml shorts.tts.voice_id 가 비어 있음(python -m cardnews.tts voices 로 고르기)")
    if used_this_month() + len(text) > int(c["monthly_cap"]):
        raise RuntimeError(f"이번 달 타입캐스트 무료 한도 근접({used_this_month()}자 사용)")
    body = {"text": text, "model": c["model"], "voice_id": c["voice_id"], "language": "kor",
            "output": {"audio_format": "mp3", "audio_tempo": float(c["tempo"]), "target_lufs": -14.0,
                       "remove_silence_ms": 150}}
    if c.get("emotion") == "smart":
        body["prompt"] = {"emotion_type": "smart"}
    elif c.get("emotion") and c["emotion"] != "normal":
        body["prompt"] = {"emotion_type": "preset", "emotion_preset": c["emotion"],
                          "emotion_intensity": float(c.get("intensity", 1.0))}
    h = {"X-API-KEY": key, "Content-Type": "application/json"}
    r = requests.post(f"{API}/v1/text-to-speech", headers=h, json=body, timeout=120)
    if r.status_code == 422 and "prompt" in body:  # 감정 필드 형식이 안 맞으면 감정 없이 재시도
        body.pop("prompt")
        r = requests.post(f"{API}/v1/text-to-speech", headers=h, json=body, timeout=120)
    if not r.ok or not r.content or r.headers.get("content-type", "").startswith("application/json"):
        raise RuntimeError(f"타입캐스트 {r.status_code}: {r.text[:200]}")
    open(out, "wb").write(r.content)
    _add_usage(len(text))
    return "typecast"


def edge(text, out, c):
    subprocess.run(["edge-tts", "--voice", c["edge_voice"], f"--rate={c['edge_rate']}", "--text", text,
                    "--write-media", out], check=True, capture_output=True)
    return "edge"


def silent(text, out, c):
    """시험용(네트워크 없을 때): 글자 수로 길이만 맞춘 무음."""
    dur = max(1.0, len(text.replace(" ", "")) / 7.0)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-t", f"{dur:.2f}", "-i",
                    "anullsrc=r=44100:cl=mono", "-c:a", "libmp3lame", out], check=True)
    return "silent"


ENGINES = {"typecast": typecast, "edge": edge, "silent": silent}


def say(text, out, override=None):
    """text를 out(mp3)으로. 실제로 쓴 엔진 이름을 돌려준다."""
    c = {**cfg(), **(override or {})}
    order = [c["engine"]] + [e for e in ("typecast", "edge") if e != c["engine"]]
    if c["engine"] == "silent":
        order = ["silent"]
    err = []
    for e in order:
        try:
            return ENGINES[e](text, out, c)
        except Exception as ex:
            err.append(f"{e}: {ex}")
            print("TTS 대체:", err[-1])
    raise RuntimeError("TTS 전부 실패 → " + " / ".join(err))


def voices():
    key = os.environ.get("TYPECAST_API_KEY")
    if not key:
        raise SystemExit("TYPECAST_API_KEY 가 필요해요.")
    r = requests.get(f"{API}/v3/voices", headers={"X-API-KEY": key}, params={"model": cfg()["model"]}, timeout=60)
    r.raise_for_status()
    vs = r.json()
    shorts = [v for v in vs if any("Short" in u for u in v.get("use_cases", []))]
    rest = [v for v in vs if v not in shorts]
    lines = []
    for v in (shorts + rest)[:60]:
        nm = v.get("voice_name", {})
        nm = nm.get("kor") or nm.get("eng") if isinstance(nm, dict) else nm
        lines.append(f"{nm} | {v.get('gender', '')} {v.get('age', '')} | {v['voice_id']} | "
                     f"{','.join(v.get('use_cases', [])[:3])}\n  미리듣기: {v.get('preview_url', '')}")
    text = "🎙 타입캐스트 목소리(쇼츠용 먼저)\n\n" + "\n".join(lines)
    print(text)
    if os.environ.get("TELEGRAM_BOT_TOKEN"):
        from . import telegram_bot as tg
        for i in range(0, len(text), 3800):
            tg.send_text(text[i:i + 3800])


if __name__ == "__main__":
    if sys.argv[1] == "voices":
        voices()
    elif sys.argv[1] == "say":
        print(say(sys.argv[2], sys.argv[3]))
