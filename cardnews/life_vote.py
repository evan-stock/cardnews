"""'인생 댓글로 정함' 댓글 투표 집계 (2026.10.23).

매일 마감 시각(오전 9시, .github/workflows/life-vote.yml)에 가장 최근 게시된 life 채널 쇼츠의 댓글을 읽어
선택지별 점수를 세고, 결과를 새 텔레그램 봇(TELEGRAM_BOT_TOKEN_LIFE)으로 보낸다. 결과는 state/life_votes/<id>.json.

규칙(2026.10.23 사용자 결정, 설명란 "댓글 1등(좋아요 가장 많은 댓글)대로"와 같음):
- **선택지를 말한 댓글 중 좋아요가 가장 많은 댓글 1개**가 이긴다.
- 좋아요가 같으면 그 선택지 전체 지지(그 선택지를 고른 댓글 수 + 좋아요 합)가 큰 쪽, 그래도 같으면 먼저 쓴 댓글.
- 선택지를 말하지 않은 댓글(잡담·분탕)은 아예 후보가 아니다.
- 욕설·혐오·성적 표현·도배·링크 댓글은 후보에서 빼고 그다음 댓글로 넘어간다(BAD). 뺀 것은 결과에 따로 적는다.
- 한 댓글이 선택지 두 개 이상을 말하면(예: "연필 말고 돈") 맨 앞에 나온 것으로 본다. 채널 주인 댓글은 제외.
- 선택지는 원고 drafts/life.json 의 "vote": {"options": [{"n": 1, "name": "연필", "kw": ["연필", "공부"]}, ...]}
  (게시물 state/posts/<id>.json 에도 같이 저장된다). kw 를 안 쓰면 이름과 "1번" 같은 번호 표현만 본다.
- 결과의 winner.comment(글·닉네임·좋아요)는 다음 화 첫 장면 '어제 댓글 1등' 카드에 쓴다.

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
# 1등 후보에서 빼는 댓글(분탕 방지). 부분 일치. 필요하면 원고 vote.ban 으로 더한다.
BAD = ["씨발", "시발", "ㅅㅂ", "ㅆㅂ", "병신", "ㅂㅅ", "좆", "개새", "새끼", "미친놈", "미친년", "꺼져", "죽어", "자살",
       "섹스", "야동", "보지", "자지", "fuck", "shit", "한남", "한녀", "김치녀", "틀딱", "급식충", "장애인", "http", "www.", "카톡", "텔레",
       "오픈채팅", "수익", "부업"]
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


def bad(text, extra=()):
    t = text.lower().replace(" ", "")
    return any(w in t for w in [*BAD, *extra]) or len(set(text)) <= 2 and len(text) > 15  # 같은 글자 도배


def tally(post, token):
    opts = [dict(o, _re=patterns(o)) for o in post["vote"]["options"]]
    names = {int(o["n"]): o["name"] for o in opts}
    owner = my_channel_id(token)
    cs = sorted(comments(post["yt_id"], token), key=lambda c: c["at"])
    seen, cands, skipped = set(), [], []
    for c in cs:
        if c["author"] == owner or c["author"] in seen:
            continue
        n = pick(c["text"], opts)
        if n is None:
            continue
        seen.add(c["author"])
        row = {"n": n, "name": names[n], "text": c["text"], "likes": c["likes"], "author": c["name"], "at": c["at"]}
        (skipped if bad(c["text"], post["vote"].get("ban", [])) else cands).append(row)
    count = {n: sum(1 for c in cands if c["n"] == n) for n in names}
    support = {n: count[n] + sum(c["likes"] for c in cands if c["n"] == n) for n in names}  # 선택지 전체 지지(댓글 수 + 좋아요)
    # 좋아요 많은 순 → 동률이면 그 선택지의 전체 지지가 큰 쪽 → 그래도 같으면 먼저 쓴 댓글
    cands.sort(key=lambda r: (-r["likes"], -support[r["n"]], r["at"]))
    tie = len(cands) > 1 and cands[0]["likes"] == cands[1]["likes"] and cands[0]["n"] != cands[1]["n"]
    return {"id": post["id"], "yt_id": post["yt_id"], "counted_at": now().isoformat(), "rule": "top_liked_comment",
            "total_comments": len(cs), "valid_votes": len(cands), "count_by_option": count, "support": support,
            "tie": tie,
            "top": cands[:5], "skipped": skipped[:10],
            "winner": {"n": cands[0]["n"], "name": cands[0]["name"], "comment": cands[0]} if cands else None}


def message(post, r):
    lines = [f"🗳 투표 마감: {post['topic']}",
             f"댓글 {r['total_comments']}개 중 선택지 댓글 {r['valid_votes']}개 (규칙: 좋아요 가장 많은 댓글 1개)", ""]
    for i, x in enumerate(r["top"][:3]):
        medal = ["🥇", "🥈", "🥉"][i]
        lines.append(f"{medal} ♥{x['likes']} · {x['n']}번 {x['name']} · {x['author']}")
        lines.append(f"     \"{x['text'][:70]}\"")
    if r["skipped"]:
        lines += ["", f"🚫 분탕·욕설로 뺀 댓글 {len(r['skipped'])}개 (최고 ♥{max(x['likes'] for x in r['skipped'])})"]
    lines.append("")
    if r["winner"]:
        w = r["winner"]
        if r.get("tie"):
            sp = r["support"]
            lines.append("⚖️ 좋아요 동률 → 선택지 전체(댓글 수 + 좋아요)로 결정: "
                         + " / ".join(f"{n}번 {sp[n]}" for n in sorted(sp, key=lambda k: -sp[k])))
        lines.append(f"👉 다음 화: {w['n']}번 {w['name']}")
        lines.append("   다음 화 첫 장면에 위 1등 댓글을 '어제 댓글 1등' 카드로 넣어요.")
    else:
        lines.append("👉 선택지 댓글이 없어요. 원칙대로 김댓글이 직접 고르는 편으로 가요.")
    lines.append("")
    lines.append("1등 댓글이 마음에 안 들면 채팅에서 'n번으로 바꿔'라고 하면 돼요.")
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
