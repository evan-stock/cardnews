#!/usr/bin/env python3
"""엑스 급상승 감지기 (오늘의쓸모 소재 선점용).

같은 게시물의 조회수·좋아요를 10분 간격으로 다시 재서 '지금 시간당 얼마나 늘고 있는지'를 계산하고,
올린 지 얼마 안 됐는데 빠르게 오르는 글만 텔레그램으로 알린다.

후보를 모으는 길(설정 파일 drafts/x_radar.yaml):
  1) accounts: 지켜볼 계정 목록 → 계정의 최근 글을 공개 임베드 경로로 읽는다(로그인 없음, 막히면 건너뜀)
  2) inbox:    게시물 주소 목록 → 채팅에서 찾은 글·직접 넣은 글을 바로 추적
수치는 fxtwitter 공개 경로로 읽는다(scripts/x_video.py 와 같은 곳).

사용: python3 scripts/x_radar.py [--config drafts/x_radar.yaml] [--state <폴더>] [--dry]
상태: <폴더>/track.json(추적 중인 글과 측정 기록), <폴더>/board.md(지금 순위표), <폴더>/log.txt
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys
import time
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
KST = dt.timezone(dt.timedelta(hours=9))
TW_EPOCH_MS = 1288834974657  # 게시물 번호 앞자리에 올린 시각이 들어 있다

DEFAULTS = {
    "max_age_h": 12,          # 이보다 오래된 글은 '선점'이 아니므로 알리지 않는다
    "drop_age_h": 30,         # 이보다 오래되면 추적에서 뺀다
    "min_views": 30000,       # 이 조회수 아래는 아직 판단하지 않는다
    "views_per_h": 100000,    # 지금 시간당 조회수 증가가 이 이상이면 알림
    "likes_per_h": 2000,      # 또는 시간당 좋아요 증가가 이 이상이면 알림
    "reach_ratio": 3.0,       # 또는 조회수가 팔로워 수의 몇 배 이상(작은 계정 글이 터지는 신호), 6시간 이내 글만
    "realert_x": 3.0,         # 알린 뒤 조회수가 이 배수로 더 커지면 한 번 더 알림
    "langs": [],              # 비우면 모든 언어. 예: [ko, en, ja]
    "video_only": False,      # true 면 영상 있는 글만 알림
    "max_track": 200,         # 한 번에 재는 글 수 상한
    "per_account": 8,         # 계정마다 최근 글 몇 개까지 후보로
}


def now_ts():
    return time.time()


def created_from_id(tid):
    return ((int(tid) >> 22) + TW_EPOCH_MS) / 1000


def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def status_id(url):
    m = re.search(r"/status(?:es)?/(\d+)", url) or re.fullmatch(r"\s*(\d{15,20})\s*", url)
    return m.group(1) if m else None


# ---------- 후보 모으기 ----------
def parse_timeline_html(html):
    """임베드 타임라인 HTML 안 __NEXT_DATA__ 에서 (게시물 번호, 작성자) 목록을 뽑는다."""
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except ValueError:
        return []
    entries = (((data.get("props") or {}).get("pageProps") or {}).get("timeline") or {}).get("entries") or []
    out = []
    for e in entries:
        t = (e.get("content") or {}).get("tweet") or {}
        tid = t.get("id_str") or (e.get("entry_id") or "").replace("tweet-", "")
        if tid and tid.isdigit() and "retweeted_status" not in t:
            out.append((tid, ((t.get("user") or {}).get("screen_name"))))
    return out


def discover_account(name):
    html = http_get(f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{name}")
    return parse_timeline_html(html)


# ---------- 수치 재기 ----------
def parse_fx(d):
    t = d.get("tweet") or {}
    if not t:
        return None
    a = t.get("author") or {}
    media = t.get("media") or {}
    return {
        "author": a.get("screen_name"), "name": a.get("name"), "followers": a.get("followers"),
        "text": (t.get("text") or "").strip(), "lang": t.get("lang"),
        "views": t.get("views") or 0, "likes": t.get("likes") or 0,
        "rts": t.get("retweets") or 0, "replies": t.get("replies") or 0,
        "video": bool(media.get("videos")), "photo": bool(media.get("photos")),
        "url": t.get("url"),
    }


def measure(tid):
    return parse_fx(json.loads(http_get(f"https://api.fxtwitter.com/status/{tid}")))


# ---------- 판단 ----------
def judge(post, cfg, now):
    """측정 기록으로 속도를 계산하고 알릴지 정한다. 돌려주는 값: (알림 종류 또는 None, 계산값 dict)"""
    snaps = post["snaps"]
    cur = snaps[-1]
    age_h = max((now - post["created"]) / 3600, 0.05)
    calc = {"age_h": age_h, "views": cur["v"], "likes": cur["l"],
            "avg_vph": cur["v"] / age_h, "avg_lph": cur["l"] / age_h, "now_vph": None, "now_lph": None}
    prev = next((s for s in reversed(snaps[:-1]) if cur["t"] - s["t"] >= 300), None)
    if prev:
        hrs = (cur["t"] - prev["t"]) / 3600
        calc["now_vph"] = max(cur["v"] - prev["v"], 0) / hrs
        calc["now_lph"] = max(cur["l"] - prev["l"], 0) / hrs
    vph = calc["now_vph"] if calc["now_vph"] is not None else calc["avg_vph"]
    lph = calc["now_lph"] if calc["now_lph"] is not None else calc["avg_lph"]
    calc["vph"], calc["lph"] = vph, lph
    fol = post.get("followers") or 0
    calc["reach"] = cur["v"] / fol if fol >= 500 else None

    if cfg["langs"] and post.get("lang") not in cfg["langs"]:
        return None, calc
    if cfg["video_only"] and not post.get("video"):
        return None, calc
    if age_h > cfg["max_age_h"] or cur["v"] < cfg["min_views"]:
        return None, calc
    if post.get("alerted"):
        if not post.get("realerted") and cur["v"] >= post["alerted_views"] * cfg["realert_x"]:
            return "more", calc
        return None, calc
    if vph >= cfg["views_per_h"] or lph >= cfg["likes_per_h"]:
        return "hot", calc
    if calc["reach"] and calc["reach"] >= cfg["reach_ratio"] and age_h <= 6:
        return "reach", calc
    return None, calc


def man(n):
    n = float(n)
    if n >= 1e8:
        return f"{n / 1e8:.1f}억"
    if n >= 1e4:
        return f"{n / 1e4:.1f}만" if n < 1e5 else f"{n / 1e4:.0f}만"
    return f"{n:,.0f}"


def age_str(h):
    return f"{h * 60:.0f}분 전" if h < 1 else f"{h:.1f}시간 전"


def link(tid, post):
    return f"https://x.com/{post.get('author') or 'i'}/status/{tid}"


def alert_text(kind, tid, post, c):
    head = {"hot": "🚀 엑스 급상승", "reach": "🌱 작은 계정 글이 터지는 중", "more": "📈 계속 오르는 중"}[kind]
    kinds = "영상" if post.get("video") else "사진" if post.get("photo") else "글"
    lines = [
        f"{head} · {kinds} · {age_str(c['age_h'])} 게시",
        f"@{post.get('author')} (팔로워 {man(post.get('followers') or 0)})",
        f"조회 {man(c['views'])} · 좋아요 {man(c['likes'])}",
        f"지금 속도: 시간당 조회 +{man(c['vph'])} · 좋아요 +{man(c['lph'])}"
        + ("" if c["now_vph"] is not None else " (첫 측정, 게시 후 평균)"),
    ]
    if c.get("reach"):
        lines.append(f"조회수가 팔로워의 {c['reach']:.1f}배")
    txt = re.sub(r"\s+", " ", post.get("text") or "")
    if txt:
        lines.append("")
        lines.append(txt[:220] + ("…" if len(txt) > 220 else ""))
    lines.append("")
    lines.append(link(tid, post))
    return "\n".join(lines)


def board(track, cfg, now):
    rows = []
    for tid, p in track.items():
        if not p.get("snaps"):
            continue
        _, c = judge(dict(p, alerted=False), cfg, now)
        rows.append((c["vph"], tid, p, c))
    rows.sort(key=lambda r: -r[0])
    out = [f"# 엑스 급상승 순위표 ({dt.datetime.fromtimestamp(now, KST):%m-%d %H:%M} 기준)", "",
           "| 시간당 조회 | 조회 | 좋아요 | 게시 | 종류 | 알림 | 글 |", "|---|---|---|---|---|---|---|"]
    for vph, tid, p, c in rows[:40]:
        txt = re.sub(r"[\s|]+", " ", p.get("text") or "")[:50]
        kind = "영상" if p.get("video") else "사진" if p.get("photo") else "글"
        out.append(f"| +{man(vph)} | {man(c['views'])} | {man(c['likes'])} | {age_str(c['age_h'])} | {kind} | "
                   f"{'보냄' if p.get('alerted') else ''} | [@{p.get('author')}]({link(tid, p)}) {txt} |")
    return "\n".join(out) + "\n"


def load_cfg(path):
    import yaml
    raw = yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8")) or {}
    cfg = dict(DEFAULTS)
    cfg.update(raw.get("rules") or {})
    cfg["accounts"] = [str(a).lstrip("@") for a in raw.get("accounts") or []]
    cfg["inbox"] = [str(u) for u in raw.get("inbox") or []]
    return cfg


def run(cfg, state_dir, send, now=None, discover=discover_account, meter=measure, sleep=time.sleep):
    now = now or now_ts()
    state_dir = pathlib.Path(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    tf = state_dir / "track.json"
    track = json.loads(tf.read_text(encoding="utf-8")) if tf.exists() else {}
    log = []

    def add(tid, src):
        if tid in track:
            return
        created = created_from_id(tid)
        if (now - created) / 3600 > cfg["drop_age_h"]:
            return
        track[tid] = {"created": created, "src": src, "snaps": []}

    for u in cfg["inbox"]:
        tid = status_id(u)
        if tid:
            add(tid, "inbox")
    for acc in cfg["accounts"]:
        try:
            found = discover(acc)
            for tid, _ in sorted(found, key=lambda x: -int(x[0]))[: cfg["per_account"]]:
                add(tid, f"@{acc}")
            log.append(f"계정 @{acc}: 글 {len(found)}개")
        except Exception as e:  # noqa: BLE001 — 한 계정이 막혀도 나머지는 계속
            log.append(f"계정 @{acc} 읽기 실패: {e}")
        sleep(0.5)

    for tid in [t for t, p in track.items() if (now - p["created"]) / 3600 > cfg["drop_age_h"]]:
        del track[tid]

    sent = 0
    order = sorted(track, key=lambda t: -track[t]["created"])[: cfg["max_track"]]
    for tid in order:
        p = track[tid]
        try:
            m = meter(tid)
        except Exception as e:  # noqa: BLE001
            p["fail"] = p.get("fail", 0) + 1
            log.append(f"측정 실패 {tid}: {e}")
            if p["fail"] >= 5 and not p["snaps"]:
                del track[tid]
            continue
        if not m:
            continue
        p.update({k: m[k] for k in ("author", "name", "followers", "text", "lang", "video", "photo")})
        p["snaps"] = (p["snaps"] + [{"t": int(now), "v": m["views"], "l": m["likes"], "r": m["rts"]}])[-24:]
        kind, c = judge(p, cfg, now)
        if kind:
            try:
                send(alert_text(kind, tid, p, c))
                sent += 1
                if kind == "more":
                    p["realerted"] = True
                else:
                    p["alerted"], p["alerted_views"] = int(now), m["views"]
            except Exception as e:  # noqa: BLE001
                log.append(f"알림 보내기 실패 {tid}: {e}")
        sleep(0.3)

    tf.write_text(json.dumps(track, ensure_ascii=False, indent=0), encoding="utf-8")
    (state_dir / "board.md").write_text(board(track, cfg, now), encoding="utf-8")
    stamp = f"{dt.datetime.fromtimestamp(now, KST):%m-%d %H:%M}"
    log.insert(0, f"[{stamp}] 추적 {len(track)}개 · 알림 {sent}건")
    lf = state_dir / "log.txt"
    old = lf.read_text(encoding="utf-8").splitlines() if lf.exists() else []
    lf.write_text("\n".join((log + old)[:400]) + "\n", encoding="utf-8")
    print("\n".join(log))
    return sent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="drafts/x_radar.yaml")
    ap.add_argument("--state", default="state/x_radar")
    ap.add_argument("--dry", action="store_true", help="텔레그램으로 보내지 않고 화면에만 출력")
    a = ap.parse_args()
    cfg = load_cfg(a.config)
    if a.dry or not os.environ.get("TELEGRAM_BOT_TOKEN"):
        send = lambda t: print("--- 알림 ---\n" + t)  # noqa: E731
    else:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
        from cardnews.telegram_bot import send_text
        send = send_text
    run(cfg, a.state, send)


if __name__ == "__main__":
    main()
