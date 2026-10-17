#!/usr/bin/env python3
"""맥북에서 타입캐스트 목소리를 만들어 저장소에 올리는 작은 프로그램(표준 라이브러리만 사용).

흐름: 서버(GitHub Actions)가 state/tts_queue/<id>.json 요청서를 남김
   → 이 프로그램(launchd 로 2분마다 실행)이 요청서를 읽고 집 인터넷으로 타입캐스트 호출
   → media/<id>/tts/<key>.mp3 + .json(단어별 시각) 을 GitHub API 로 올리고 요청서를 지움
   → shorts 워크플로를 다시 실행 → 영상 완성 → 텔레그램 미리보기

설정 파일: ~/.cardnews_tts/config.json  {"typecast_key": "...", "github_token": "...", "repo": "evan-stock/cardnews"}
로그: ~/.cardnews_tts/log.txt
"""
import base64
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request

HOME = os.path.expanduser("~/.cardnews_tts")
CFG = json.load(open(os.path.join(HOME, "config.json"), encoding="utf-8"))
REPO = CFG.get("repo", "evan-stock/cardnews")
GH = f"https://api.github.com/repos/{REPO}"
TC = "https://api.typecast.ai/v1/text-to-speech/with-timestamps?granularity=word"
UA = "typecast-direct/1 python-urllib typecast-integration/1 (source=api-page; generated_by=claude-code)"
MONTHLY_CAP = int(CFG.get("monthly_cap", 14000))  # 무료 API 월 15,000자


def log(*a):
    line = dt.datetime.now().strftime("%m-%d %H:%M:%S ") + " ".join(str(x) for x in a)
    print(line)
    with open(os.path.join(HOME, "log.txt"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def req(url, method="GET", data=None, headers=None, timeout=120):
    h = dict(headers or {})
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        h.setdefault("Content-Type", "application/json")
    r = urllib.request.Request(url, data=body, method=method, headers=h)
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def gh(path, method="GET", data=None):
    return req(GH + path, method, data, {"Authorization": f"Bearer {CFG['github_token']}",
                                         "Accept": "application/vnd.github+json", "User-Agent": "cardnews-mac-tts"})


def usage(add=0):
    p = os.path.join(HOME, "usage.json")
    u = json.load(open(p)) if os.path.exists(p) else {}
    m = dt.date.today().strftime("%Y-%m")
    u[m] = int(u.get(m, 0)) + add
    json.dump(u, open(p, "w"))
    return u[m]


def typecast(text, v, ctx):
    body = {"text": text, "model": v.get("model") or "ssfm-v30", "voice_id": v["voice_id"], "language": "kor",
            "output": {"audio_format": "mp3", "audio_tempo": float(v.get("tempo") or 1.1), "target_lufs": -14.0,
                       "remove_silence_ms": 150}}
    emo = v.get("emotion")
    if emo == "smart":
        body["prompt"] = {"emotion_type": "smart", **{k: x for k, x in (ctx or {}).items() if x}}
    elif emo and emo != "normal":
        body["prompt"] = {"emotion_type": "preset", "emotion_preset": emo,
                          "emotion_intensity": float(v.get("intensity") or 1.0)}
    h = {"X-API-KEY": CFG["typecast_key"], "User-Agent": UA}
    try:
        j = req(TC, "POST", body, h)
    except urllib.error.HTTPError as e:
        if e.code == 422 and "prompt" in body:
            body.pop("prompt")
            j = req(TC, "POST", body, h)
        else:
            raise RuntimeError(f"타입캐스트 {e.code}: {e.read()[:1000]!r}")
    words = [{"text": w["text"], "start": float(w["start"]), "end": float(w["end"])} for w in (j.get("words") or [])]
    return base64.b64decode(j["audio"]), words


def put_file(path, content_bytes, msg):
    try:
        sha = gh(f"/contents/{path}").get("sha")
    except urllib.error.HTTPError:
        sha = None
    data = {"message": msg, "content": base64.b64encode(content_bytes).decode()}
    if sha:
        data["sha"] = sha
    gh(f"/contents/{path}", "PUT", data)


def main():
    try:
        files = gh("/contents/state/tts_queue")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return  # 요청 없음
        raise
    for f in [x for x in files if x["name"].endswith(".json")]:
        meta = gh(f"/contents/{f['path']}")
        q = json.loads(base64.b64decode(meta["content"]))
        vid = q["id"]
        need = sum(len(it["text"]) for it in q["items"])
        if usage() + need > MONTHLY_CAP:
            log(f"⚠️ 이번 달 한도 근접({usage()}자) — {vid} 건너뜀")
            continue
        log(f"▶ {vid}: {len(q['items'])}개 장면")
        for it in q["items"]:
            audio, words = typecast(it["text"], it["voice"], it.get("ctx"))
            usage(len(it["text"]))
            put_file(f"media/{vid}/tts/{it['key']}.mp3", audio, f"tts(mac): {vid} {it['key']}")
            put_file(f"media/{vid}/tts/{it['key']}.json", json.dumps(words, ensure_ascii=False).encode(),
                     f"tts(mac): {vid} {it['key']} words")
            time.sleep(1)
        gh(f"/contents/{f['path']}", "DELETE", {"message": f"tts(mac): {vid} 완료", "sha": meta["sha"]})
        gh("/actions/workflows/shorts.yml/dispatches", "POST", {"ref": "main", "inputs": {"cmd": "render"}})
        log(f"✅ {vid} 목소리 올림 → 영상 만들기 다시 실행")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa
        log("❌", repr(e)[:500])
        sys.exit(1)
