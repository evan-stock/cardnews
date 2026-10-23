"""'인생 댓글로 정함' 댓글 투표 집계 (2026.10.23).

매일 마감 시각(오전 9시, .github/workflows/life-vote.yml)에 가장 최근 게시된 life 채널 쇼츠의 댓글을 읽어
선택지별 점수를 세고, 결과를 새 텔레그램 봇(TELEGRAM_BOT_TOKEN_LIFE)으로 보낸다. 결과는 state/life_votes/<id>.json.

점수 = 그 선택지를 고른 댓글 1개당 1점 + 그 댓글의 좋아요 수.
- 한 댓글이 선택지 두 개 이상을 말하면(예: "연필 말고 돈") 맨 앞에 나온 것으로 센다.
- 채널 주인 댓글은 세지 않는다. 같은 사람이 여러 번 쓰면 첫 댓글만 센다.
- 선택지는 원고 drafts/life.json 의 "vote": {"options": [{"n": 1, "name": "연필", "kw": ["연필", "공부"]}, ...]}
  (게시물 state/posts/<id>.json 에도 같이 저장된다). kw 를 안 쓰면 이름과 "1번" 같은 번호 표현만 본다.

수동 실행: python -m cardnews.life_vote [게시물id]
"""
import json
import os
import re
import sys

import requests

from . import telegram_bot as tg
from . import youtube
from .common import ROOT, all_posts, load_post, now

API = "https://www.googleapis.com/youtube/v3"
OUT = ROOT / "state" / "life_votes"
NUM = {1: ["①", "1️⃣"], 2: ["②", "2️⃣"], 3: ["③", "3️⃣"], 4: ["④", "4️⃣"], 5: ["⑤", "5️⃣"]}


def with_vote(p):
    """게시물에 vote 가 없으면(1화처럼 기능 추가 전에 보낸 것) 같은 id 의 원고 drafts/life.json 에서 가져온다."""
    if p and not p.get("vote"):
        try:
            d = json.load(open(ROOT / "drafts" / "life.json", encoding="utf-8"))
            if d.get("id") == p["id"] and d.get("vote"):
                p = {**p, "vote": d["vote"]}
        except (OSError, ValueError):
            pass
    return p


def latest_post():
    ps = [with_vote(p) for p in all_posts() if (p.get("yt") or {}).get("channel") == "life"
          and p.get("status") == "published" and p.get("yt_id")]
    ps = [p for p in ps if p.get("vote")]
    return max(ps, key=lambda p: p.get("published_at", "")) if ps else None


def comments(video_id, token):
    h = {"Authorization": f"Bearer {token}"}
    out, page = [], None
    while True:
        q = {"part": "snippet", "videoId": video_id, "maxResults": 100, "textFormat": "plainText", "order": "time"}
        if page:
            q["pageToken"] = page
        j = requests.get(f"{API}/commentThreads", params=q, headers=h, timeout=60).json()
        if "error" in j:
            raise RuntimeError(f"댓글 읽기 실패: {j['error'].get('message')}")
        for it in j.get("items", []):
            s = it["snippet"]["topLevelComment"]["snippet"]
            out.append({"text": s.get("textDisplay", ""), "likes": int(s.get("likeCount", 0)),
                        "author": (s.get("authorChannelId") or {}).get("value") or s.get("authorDisplayName"),
                        "name": s.get("authorDisplayName", ""), "at": s.get("publishedAt", "")})
        page = j.get("nextPageToken")
        if not page or len(out) >= 5000:
            return out


def my_channel_id(token):
    j = requests.get(f"{API}/channels", params={"part": "id", "mine": "true"},
                     headers={"Authorization": f"Bearer {token}"}, timeout=60).json()
    return (j.get("items") or [{}])[0].get("id")


def patterns(opt):
    n = int(opt["n"])
    words = [opt["name"], *opt.get("kw", [])]
    pats = [re.escape(w) for w in words if w]
    pats += [rf"(?<![0-9]){n}\s*번", rf"^\s*{n}\s*[.!)]*\s*$", *[re.escape(c) for c in NUM.get(n, [])]]
    return re.compile("|".join(pats), re.IGNORECASE | re.MULTILINE)


def pick(text, opts):
    """댓글에서 가장 먼저 나온 선택지 번호(없으면 None)."""
    best = None
    for o in opts:
        m = o["_re"].search(text)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), int(o["n"]))
    return best[1] if best else None


def tally(post, token):
    opts = [dict(o, _re=patterns(o)) for o in post["vote"]["options"]]
    owner = my_channel_id(token)
    seen, score, top = set(), {int(o["n"]): {"comments": 0, "likes": 0} for o in opts}, {}
    cs = sorted(comments(post["yt_id"], token), key=lambda c: c["at"])
    for c in cs:
        if c["author"] == owner or c["author"] in seen:
            continue
        n = pick(c["text"], opts)
        if n is None:
            continue
        seen.add(c["author"])
        score[n]["comments"] += 1
        score[n]["likes"] += c["likes"]
        if n not in top or c["likes"] > top[n]["likes"]:
            top[n] = c
    rows = []
    for o in opts:
        n = int(o["n"]); s = score[n]
        rows.append({"n": n, "name": o["name"], "points": s["comments"] + s["likes"], **s,
                     "best": {k: top[n][k] for k in ("text", "likes", "name")} if n in top else None})
    rows.sort(key=lambda r: (-r["points"], -r["likes"], r["n"]))
    return {"id": post["id"], "yt_id": post["yt_id"], "counted_at": now().isoformat(),
            "total_comments": len(cs), "valid_votes": len(seen), "ranking": rows,
            "winner": rows[0] if rows and rows[0]["points"] > 0 else None}


def message(post, r):
    lines = [f"🗳 투표 마감: {post['topic']}", f"댓글 {r['total_comments']}개 중 유효 {r['valid_votes']}표", ""]
    for i, x in enumerate(r["ranking"]):
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else "  "
        lines.append(f"{medal} {x['n']}번 {x['name']} — {x['points']}점 (댓글 {x['comments']} + 좋아요 {x['likes']})")
        if x["best"]:
            lines.append(f"     \"{x['best']['text'][:60]}\" ♥{x['best']['likes']} · {x['best']['name']}")
    lines.append("")
    if r["winner"]:
        w = r["winner"]
        tie = [x for x in r["ranking"][1:] if x["points"] == w["points"]]
        lines.append(f"👉 다음 화: {w['n']}번 {w['name']}" + (" (동점 → 좋아요 많은 쪽)" if tie else ""))
    else:
        lines.append("👉 표가 없어요. 원칙대로 김댓글이 직접 고르는 편으로 가요.")
    lines.append(f"https://youtube.com/shorts/{r['yt_id']}")
    return "\n".join(lines)


def run(pid=None):
    post = with_vote(load_post(pid)) if pid else latest_post()
    if not post:
        print("집계할 life 게시물이 없어요(게시됨 + vote 있는 것).")
        return
    if (OUT / f"{post['id']}.json").exists() and not pid:
        print("이미 집계함:", post["id"])
        return
    r = tally(post, youtube.access_token("life"))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{post['id']}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    msg = message(post, r)
    print(msg)
    if os.environ.get("TELEGRAM_BOT_TOKEN_LIFE") or os.environ.get("TELEGRAM_BOT_TOKEN"):
        with tg.channel("life"):
            tg.send_text(msg)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
