"""채널 비교(YouTube Data API, 읽기 전용, 할당량 약 250).
drafts/bench_api.json {"handles":[...], "queries":[...], "since":"2026-10-01"}
→ state/bench/api_report.json + api_report.txt
- handles: 채널별 최근 업로드 100개(게시일·조회수)
- queries: 10.1 이후 한국 동물 쇼츠 검색(조회수순) → 올해 생긴 채널 찾아 최근 업로드까지 받음
"""
import json, statistics, sys, datetime as dt
import requests
sys.path.insert(0, ".")
from cardnews.youtube import access_token

API = "https://www.googleapis.com/youtube/v3/"
H = {"Authorization": f"Bearer {access_token()}"}
cfg = json.load(open("drafts/bench_api.json"))
SINCE = cfg.get("since", "2026-10-01")


def get(path, **p):
    r = requests.get(API + path, params=p, headers=H, timeout=60)
    j = r.json()
    if "error" in j:
        raise RuntimeError(f"{path} {p} → {j['error'].get('message')}")
    return j


def channel(handle=None, cid=None):
    p = {"part": "snippet,statistics,contentDetails"}
    if handle == "mine": p["mine"] = "true"
    elif handle: p["forHandle"] = handle
    else: p["id"] = cid
    it = get("channels", **p).get("items", [])
    return it[0] if it else None


def uploads(ch, n=100):
    pl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while len(ids) < n:
        j = get("playlistItems", part="contentDetails", playlistId=pl, maxResults=50, **({"pageToken": tok} if tok else {}))
        ids += [i["contentDetails"]["videoId"] for i in j.get("items", [])]
        tok = j.get("nextPageToken")
        if not tok: break
    out = []
    for k in range(0, len(ids), 50):
        for v in get("videos", part="snippet,statistics,contentDetails", id=",".join(ids[k:k+50])).get("items", []):
            out.append({"id": v["id"], "date": v["snippet"]["publishedAt"][:10], "title": v["snippet"]["title"][:60],
                        "views": int(v["statistics"].get("viewCount", 0)), "dur": v["contentDetails"]["duration"]})
    return out


def summ(vids):
    def s(xs):
        xs = [v["views"] for v in xs]
        return {"n": len(xs), "median": int(statistics.median(xs)) if xs else None, "max": max(xs) if xs else None,
                "over10k": sum(x >= 10000 for x in xs)}
    # 최근 3일 영상은 아직 덜 자라서 따로
    cut = (dt.date.today() - dt.timedelta(days=3)).isoformat()
    return {"before": s([v for v in vids if v["date"] < SINCE]),
            "after": s([v for v in vids if SINCE <= v["date"] < cut]),
            "last3d": s([v for v in vids if v["date"] >= cut])}


def info(ch):
    return {"title": ch["snippet"]["title"], "id": ch["id"], "created": ch["snippet"]["publishedAt"][:10],
            "subs": ch["statistics"].get("subscriberCount"), "videos": ch["statistics"].get("videoCount")}


rep = {"since": SINCE, "fixed": [], "found": [], "search_hits": []}
for h in cfg.get("handles", []):
    try:
        ch = channel(cid=h) if h.startswith("UC") else channel(handle=h)
        if not ch: rep["fixed"].append({"handle": h, "error": "not found"}); continue
        vids = uploads(ch, cfg.get("n", 100))
        if cfg.get("full"):  # 채널 전체 목록(날짜·조회수·길이·제목)을 tsv 로
            with open(f"state/bench/{ch['snippet']['title'].replace('/', '_')}.tsv", "w") as f:
                f.write("date\tviews\tdur\tid\ttitle\n")
                for v in vids:
                    f.write(f"{v['date']}\t{v['views']}\t{v['dur']}\t{v['id']}\t{v['title']}\n")
        rep["fixed"].append({"handle": h, **info(ch), **summ(vids), "recent": vids[:15]})
    except Exception as e:
        rep["fixed"].append({"handle": h, "error": str(e)})

cids = {}
for q in cfg.get("queries", []):
    try:
        j = get("search", part="snippet", type="video", q=q, regionCode="KR", relevanceLanguage="ko",
                videoDuration="short", order="viewCount", publishedAfter=SINCE + "T00:00:00Z", maxResults=50)
        for it in j.get("items", []):
            rep["search_hits"].append({"q": q, "vid": it["id"]["videoId"], "ch": it["snippet"]["channelTitle"],
                                       "cid": it["snippet"]["channelId"], "date": it["snippet"]["publishedAt"][:10],
                                       "title": it["snippet"]["title"][:60]})
            cids[it["snippet"]["channelId"]] = 1
    except Exception as e:
        rep["search_hits"].append({"q": q, "error": str(e)})

# 검색 결과 영상 조회수
vids = [h["vid"] for h in rep["search_hits"] if "vid" in h]
vv = {}
for k in range(0, len(vids), 50):
    for v in get("videos", part="statistics", id=",".join(vids[k:k+50])).get("items", []):
        vv[v["id"]] = int(v["statistics"].get("viewCount", 0))
for h in rep["search_hits"]:
    if "vid" in h: h["views"] = vv.get(h["vid"])

# 채널 정보 → 2026년 생긴 채널은 최근 업로드까지
ids = list(cids)
chs = []
for k in range(0, len(ids), 50):
    chs += get("channels", part="snippet,statistics,contentDetails", id=",".join(ids[k:k+50])).get("items", [])
for ch in chs:
    d = info(ch)
    if d["created"] >= cfg.get("young_after", "2026-01-01"):
        try:
            v = uploads(ch, 50)
            d.update(summ(v)); d["recent"] = v[:10]
        except Exception as e:
            d["error"] = str(e)
    rep["found"].append(d)

json.dump(rep, open("state/bench/api_report.json", "w"), ensure_ascii=False, indent=1)
with open("state/bench/api_report.txt", "w") as f:
    for c in rep["fixed"] + [c for c in rep["found"] if "before" in c]:
        f.write(f"{c.get('title', c.get('handle'))} 생성 {c.get('created')} 구독 {c.get('subs')} | 전 {c.get('before')} | 후 {c.get('after')} | 3일 {c.get('last3d')}\n")
print(open("state/bench/api_report.txt").read())
