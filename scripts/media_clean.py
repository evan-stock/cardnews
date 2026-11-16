"""media/ 정리 (2026-11-11 사용자 결정).

- 게시 안 된 후보(state/posts 없음)·거절·만료·실패: 폴더 날짜(YYYYMMDD) 기준 2일 지나면 삭제.
- 게시됨(published)·앱 직접 올림(manual): 2일 지나면 완성본만 남기고 원본·클립 등은 삭제,
  맥북이 완성본을 받아 가면(state/archived.txt 에 id) 폴더째 삭제.
- 그 밖의 상태(pending·approved·held 등)와 날짜 없는 폴더는 건드리지 않는다.
- 맥북이 받아 갈 목록 state/archive_queue.json 을 새로 쓴다.
원본 영상은 보관하지 않는다. 출처·원작자는 state/posts·drafts·프로젝트 업로드 기록에 남는다.
사용: python scripts/media_clean.py [--dry-run]
"""
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
MEDIA, POSTS = ROOT / "media", ROOT / "state" / "posts"
ARCHIVED, QUEUE = ROOT / "state" / "archived.txt", ROOT / "state" / "archive_queue.json"
KEEP_DAYS = 2
GONE = {None, "rejected", "expired", "failed"}
DONE = {"published", "manual"}
SKIP_WORDS = ("nobgm", "nomusic", "candidates", "cover")


CHANNELS = {None: "털뭉치", "shop": "오늘의쓸모_유튜브", "life": "인생댓글로정함"}


def channel(post):
    """맥북 보관 폴더 이름: 쇼츠는 유튜브 채널별, 그 밖(카드뉴스·릴스)은 오늘의쓸모_인스타."""
    if post.get("kind") != "short":
        return "오늘의쓸모_인스타"
    return CHANNELS.get((post.get("yt") or {}).get("channel"), "기타_유튜브")


def finals(folder):
    """완성본: 폴더 맨 위의 mp4·jpg·png 중 음악 뺀 판·후보 모음·표지는 뺀다."""
    out = []
    for f in sorted(folder.iterdir()):
        if f.is_file() and f.suffix.lower() in (".mp4", ".jpg", ".png") and not any(w in f.name for w in SKIP_WORDS):
            out.append(f.relative_to(ROOT).as_posix())
    return out


def main(dry):
    today = dt.datetime.now(ZoneInfo("Asia/Seoul")).date()
    archived = set(ARCHIVED.read_text().split()) if ARCHIVED.exists() else set()
    queue, removed, freed = [], [], 0
    for folder in sorted(p for p in MEDIA.iterdir() if p.is_dir()):
        m = re.match(r"(\d{8})", folder.name)
        if not m:
            continue
        age = (today - dt.datetime.strptime(m.group(1), "%Y%m%d").date()).days
        post = POSTS / f"{folder.name}.json"
        status, info = None, {}
        if post.exists():
            try:
                info = json.loads(post.read_text(encoding="utf-8"))
                status = info.get("status")
            except Exception:
                continue
        if status in GONE and age > KEEP_DAYS:
            gone = [folder]
        elif status in DONE:
            fs = finals(folder)
            if folder.name in archived:
                gone = [folder] if age > KEEP_DAYS else []
            else:
                if fs:
                    queue.append({"id": folder.name, "channel": channel(info), "files": fs})
                keep = {ROOT / f for f in fs}
                gone = [x for x in folder.iterdir() if x not in keep] if age > KEEP_DAYS and fs else []
        else:
            gone = []
        for g in gone:
            freed += sum(f.stat().st_size for f in ([g] if g.is_file() else g.rglob("*")) if f.is_file())
            if not dry:
                shutil.rmtree(g) if g.is_dir() else g.unlink()
        if gone:
            removed.append(f"{folder.name}({status or '후보'}{'' if gone == [folder] else ', 완성본만 남김'})")
    if not dry:
        QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"삭제 {len(removed)}개, {freed / 1e9:.2f}GB / 맥북이 받아 갈 것 {len(queue)}개")
    for r in removed:
        print(" -", r)


if __name__ == "__main__":
    main("--dry-run" in sys.argv)
