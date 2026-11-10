"""맥북: 게시된 쇼츠·카드뉴스 완성본을 ~/Movies/쇼츠보관 으로 받아 두기 (2026.11.11).

목소리 도우미(~/.cardnews_tts/tts_local.py, 2분마다)가 끝에 부른다. 1시간에 한 번만 실제로 돈다.
1) 저장소 state/archive_queue.json(매일 media-clean 이 씀)을 읽고
2) 각 완성본을 ~/Movies/쇼츠보관/<YYYY-MM>/<id>/ 에 받고
3) 다 받은 id 를 state/archived.txt 에 더한다 → 다음 media-clean 이 저장소에서 지운다.
토큰은 목소리 도우미 config.json 의 github_token 을 쓴다.
"""
import base64
import json
import time
import urllib.request
from pathlib import Path

HOME = Path.home()
BASE = HOME / ".cardnews_tts"
DEST = HOME / "Movies" / "쇼츠보관"
STAMP = BASE / "archive" / "last_run"
LOG = BASE / "archive" / "log.txt"
REPO = "evan-stock/cardnews"


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")


def api(path, token, data=None, method=None, raw=False):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/{path}",
        data=None if data is None else json.dumps(data).encode(),
        method=method,
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github.raw" if raw else "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        body = r.read()
    return body if raw else json.loads(body or b"{}")


def main():
    if STAMP.exists() and time.time() - STAMP.stat().st_mtime < 3600:
        return
    STAMP.parent.mkdir(parents=True, exist_ok=True)
    STAMP.touch()
    token = json.loads((BASE / "config.json").read_text())["github_token"]
    queue = json.loads(api("contents/state/archive_queue.json", token, raw=True) or b"[]")
    done = []
    for item in queue:
        pid = item["id"]
        folder = DEST / f"{pid[:4]}-{pid[4:6]}" / pid
        try:
            for path in item["files"]:
                out = folder / Path(path).name
                if out.exists() and out.stat().st_size > 0:
                    continue
                folder.mkdir(parents=True, exist_ok=True)
                out.write_bytes(api(f"contents/{path}", token, raw=True))
            done.append(pid)
        except Exception as e:  # 다음 시간에 다시
            log(f"실패 {pid}: {e}")
    if not done:
        return
    for attempt in range(3):
        try:
            cur = api("contents/state/archived.txt", token)
            text, sha = base64.b64decode(cur["content"]).decode(), cur["sha"]
        except Exception:
            text, sha = "", None
        have = set(text.split())
        new = [d for d in done if d not in have]
        if not new:
            break
        body = {"message": f"archive: 맥북에 완성본 {len(new)}개 받음",
                "content": base64.b64encode((text + "".join(d + "\n" for d in new)).encode()).decode()}
        if sha:
            body["sha"] = sha
        try:
            api("contents/state/archived.txt", token, body, "PUT")
            log(f"받음 {len(new)}개: {' '.join(new)}")
            break
        except Exception as e:
            log(f"archived.txt 쓰기 실패({attempt + 1}): {e}")
            time.sleep(5)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"오류: {e}")
