#!/usr/bin/env python3
"""엑스(X/트위터) 게시물 영상 받기 — yt-dlp 실패 시 예비 경로.

사용: python3 scripts/x_video.py <x 게시물 주소> <저장 폴더> <번호 i> [--meta-only]
- 게시물 정보(작성자·날짜·본문·영상 길이)를 <폴더>/x<i>.json 으로 저장한다(출처·시점 확인용).
- --meta-only 가 아니면 영상을 <폴더>/v<i>.mp4 (여러 개면 v<i>_2.mp4 …)로 받는다.
- fxtwitter → vxtwitter 순서로 시도. 둘 다 실패하면 종료 코드 1.
"""
import json
import os
import re
import sys
import urllib.request

RAW = {}
UA = "Mozilla/5.0 (cardnews-bot; +https://github.com/evan-stock/cardnews)"


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def from_fx(tid):
    d = get_json(f"https://api.fxtwitter.com/status/{tid}")
    t = d.get("tweet") or {}
    RAW["fx"] = {k: t.get(k) for k in ("media", "card", "quote", "embed_card", "broadcast") if t.get(k)}
    vids = []
    for v in (t.get("media") or {}).get("videos") or []:
        best = v.get("url")
        mp4s = [x for x in v.get("variants") or [] if "mp4" in (x.get("content_type") or x.get("url", ""))]
        if mp4s:
            best = max(mp4s, key=lambda x: x.get("bitrate") or 0).get("url") or best
        if best:
            vids.append({"url": best, "w": v.get("width"), "h": v.get("height"), "dur": v.get("duration")})
    meta = {
        "src": "fxtwitter",
        "author": (t.get("author") or {}).get("screen_name"),
        "name": (t.get("author") or {}).get("name"),
        "date": t.get("created_at"),
        "text": t.get("text"),
        "views": t.get("views"),
        "likes": t.get("likes"),
        "retweets": t.get("retweets"),
        "quote": ((t.get("quote") or {}).get("url")),
    }
    # 인용 게시물 안의 영상도 후보로
    if not vids and t.get("quote"):
        for v in ((t["quote"].get("media") or {}).get("videos") or []):
            if v.get("url"):
                vids.append({"url": v["url"], "w": v.get("width"), "h": v.get("height"), "dur": v.get("duration"), "from": "quote"})
    return meta, vids


def from_vx(tid):
    d = get_json(f"https://api.vxtwitter.com/Twitter/status/{tid}")
    vids = [
        {"url": m["url"], "w": (m.get("size") or {}).get("width"), "h": (m.get("size") or {}).get("height"),
         "dur": (m.get("duration_millis") or 0) / 1000 or None}
        for m in d.get("media_extended") or [] if m.get("type") in ("video", "gif") and m.get("url")
    ]
    meta = {"src": "vxtwitter", "author": d.get("user_screen_name"), "name": d.get("user_name"),
            "date": d.get("date"), "text": d.get("text"), "likes": d.get("likes"), "retweets": d.get("retweets")}
    return meta, vids


def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://x.com/"})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
    return os.path.getsize(path)


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    url, out, i = sys.argv[1], sys.argv[2], sys.argv[3]
    meta_only = "--meta-only" in sys.argv
    m = re.search(r"/status(?:es)?/(\d+)", url)
    if not m:
        print(f"게시물 번호를 못 찾음: {url}")
        return 1
    tid = m.group(1)
    os.makedirs(out, exist_ok=True)
    meta, vids, errs = None, [], []
    for fn in (from_fx, from_vx):
        try:
            meta, vids = fn(tid)
            if vids or meta_only:
                break
        except Exception as e:  # noqa: BLE001 — 다음 경로로 넘어간다
            errs.append(f"{fn.__name__}: {e}")
    if meta is None:
        meta = {}
    meta.update({"url": url, "id": tid, "videos": vids, "errors": errs})
    fx = RAW.get("fx") or {}
    card = (fx.get("card") or {}).get("url")
    if not vids:
        # 영상이 없는 이유를 한 단어로 남긴다(지난 '실패'는 대부분 사진 글·기사 링크 글이었다)
        if card:
            meta["kind"] = "기사링크"
        elif (fx.get("media") or {}).get("photos"):
            meta["kind"] = "사진만"
        elif fx.get("quote"):
            meta["kind"] = "인용글(영상 없음)"
        else:
            meta["kind"] = "글만/삭제됨"
        meta["card"] = card
        meta["quote_url"] = (fx.get("quote") or {}).get("url")
    with open(os.path.join(out, f"x{i}.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    if meta_only:
        return 0
    if not vids and card:
        # 기사 링크 글: 영상이 기사 페이지에 있는 경우가 많다 → 기사 주소로 yt-dlp 한 번 더
        import subprocess
        r = subprocess.run(["yt-dlp", "-q", "--no-playlist", "-f", "bv*+ba/b", "-S", "res:1920", "--merge-output-format", "mp4",
                            "-o", os.path.join(out, f"v{i}.%(ext)s"), card], capture_output=True, text=True)
        if r.returncode == 0:
            print(f"받음 v{i} (기사 페이지 {card})")
            return 0
        print(f"기사 페이지에서도 영상 못 받음: {card} {r.stderr[-200:]}")
    if not vids:
        print(f"영상 없는 글({meta.get('kind')}): {url}")
        return 1
    for k, v in enumerate(vids, 1):
        name = f"v{i}.mp4" if k == 1 else f"v{i}_{k}.mp4"
        size = download(v["url"], os.path.join(out, name))
        print(f"받음 {name} {size // 1024}KB ({meta.get('src')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
