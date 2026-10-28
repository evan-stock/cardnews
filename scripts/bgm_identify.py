"""잘난지 쇼츠 배경음악 찾기: 받은 오디오(media/bgmid/*.m4a 등)를 구간별로 잘라 Shazam 으로 식별 → state/bench/bgm_id.tsv"""
import asyncio, glob, os, subprocess, json, sys
from shazamio import Shazam

async def main():
    sh = Shazam(); rows = []
    for f in sorted(glob.glob("bgmid/*.*")):
        if f.endswith(".json"): continue
        vid = os.path.basename(f).rsplit(".", 1)[0]
        hits = []
        for st in (1, 7, 13):
            seg = f"/tmp/{vid}_{st}.mp3"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(st), "-t", "8", "-i", f, "-ac", "1", seg])
            if not os.path.exists(seg): continue
            try:
                r = await sh.recognize(seg)
                t = r.get("track") or {}
                hits.append(f"{t.get('title','-')} / {t.get('subtitle','-')}" if t else "-")
            except Exception as e:
                hits.append(f"err {e}")
        title = ""
        jf = f"bgmid/{vid}.info.json"
        if os.path.exists(jf):
            d = json.load(open(jf)); title = d.get("title", "")
            if d.get("track"): hits.append(f"yt-track: {d.get('track')} / {d.get('artist')}")
        rows.append("\t".join([vid, title] + hits)); print(rows[-1], flush=True)
    open("state/bench/bgm_id.tsv", "w").write("\n".join(rows) + "\n")
asyncio.run(main())
