"""엑스 스크리닝 1단계: debug get 으로 받은 fxtwitter 프로필 글(json)을 시간당 조회수 순으로 정리.
사용: python3 scripts/x_screen/rank.py media/<id>/cand [시간=24] [개수=60]
받기: debug/trigger.txt 에 계정마다
  get <id> https://api.fxtwitter.com/2/profile/<계정>/statuses <계정>.json
(계정 목록은 drafts/x_radar.yaml accounts + yonhaptweet·hanitweet·joongangilbo)"""
import glob, json, sys, time
d = sys.argv[1]; hours = float(sys.argv[2]) if len(sys.argv) > 2 else 24; top = int(sys.argv[3]) if len(sys.argv) > 3 else 60
rows = {}
for f in glob.glob(f"{d}/*.json"):
    try: res = json.load(open(f)).get("results", []) or []
    except Exception: continue
    for s in res:
        age = (time.time() - s.get("created_timestamp", 0)) / 3600
        if age > hours: continue
        m = s.get("media") or {}
        kind = "영상" if m.get("videos") else ("사진" if m.get("photos") else "글")
        v = s.get("views") or 0
        q = (s.get("quote") or {}).get("text", "")
        txt = (s.get("text", "") + (f" [인용:{q}]" if q else "")).replace("\n", " ")[:120]
        rows[s["id"]] = (v / max(age, 0.5), v, age, kind, s["author"]["screen_name"], s["id"], txt)
for r in sorted(rows.values(), reverse=True)[:top]:
    print(f"{r[0]/1e4:5.1f}만/h {r[1]/1e4:6.1f}만 {r[2]:4.1f}h {r[3]} https://x.com/{r[4]}/status/{r[5]} | {r[6]}")
