"""채팅에서 직접 쓴 카드뉴스 원고(drafts/*.json)를 API 비용 없이 렌더링한다.

원고 형식:
{"id":"20261014-lunch","slot":"lunch","mode":"collect|render|send",
 "topic":"","core":"","risk":"","slides":[{"t":"","b":""}...],
 "caption":"","hashtags":[],"sources":[{"publisher":"","url":"","date":""}],
 "image_pages":["기사 주소"], "images":["press03","https://...jpg"...]}

mode=collect : 기사에서 후보 사진을 모아 media/<id>/cand/ 에 번호 붙여 저장 + 한 장짜리 모아보기(candidates.jpg)
mode=render  : images 순서대로 장마다 사진을 넣어 렌더링(텔레그램 전송 없음)
mode=send    : render + 게시 대기(pending) 저장 + 텔레그램 미리보기 전송(승인하면 기존 흐름대로 게시)
"""
import glob
import json
import os
import shutil
import sys

from .common import MEDIA, ROOT, now, save_post, slot_time
from .images import BROWSER_UA, _good_image, press_images

import requests


def collect(d, base):
    cand = base / "cand"
    shutil.rmtree(cand, ignore_errors=True)
    pool = press_images(d.get("image_pages", []) + [s["url"] for s in d.get("sources", []) if s.get("url")],
                        str(cand), limit=int(d.get("limit", 24)))
    os.makedirs(cand, exist_ok=True)
    for k, u in enumerate(d.get("image_urls", []), 1):  # 글에 직접 붙은 이미지 주소
        p = cand / f"url{k:02d}.jpg"
        try:
            r = requests.get(u, headers={**BROWSER_UA, "Referer": d.get("referer", u)}, timeout=40)
            if r.ok:
                open(p, "wb").write(r.content)
                if _good_image(str(p)):
                    pool.append((str(p), "url"))
                    continue
            print("이미지 실패:", r.status_code, u[:80])
        except Exception as e:
            print("이미지 오류:", e)
        if p.exists():
            p.unlink()
    from PIL import Image, ImageDraw
    th = []
    for path, src in pool:
        im = Image.open(path).convert("RGB")
        im.thumbnail((300, 300))
        tile = Image.new("RGB", (300, 330), "white")
        tile.paste(im, ((300 - im.width) // 2, 30))
        ImageDraw.Draw(tile).text((6, 6), f"{os.path.basename(path)[:-4]}  {src[:24]}", fill="black")
        th.append(tile)
    if th:
        cols = 4
        sheet = Image.new("RGB", (300 * cols, 330 * ((len(th) + cols - 1) // cols)), "white")
        for k, t in enumerate(th):
            sheet.paste(t, ((k % cols) * 300, (k // cols) * 330))
        sheet.save(base / "candidates.jpg", quality=80)
    json.dump([[os.path.basename(p), s] for p, s in pool], open(base / "candidates.json", "w"), ensure_ascii=False)
    print("후보 사진", len(pool))
    texts = {}
    for u in d.get("read_pages", []):
        for src in (u, "https://r.jina.ai/" + u):
            try:
                r = requests.get(src, headers=BROWSER_UA, timeout=40)
                if r.ok and len(r.text) > 500:
                    texts[u] = r.text[:300000]
                    break
            except Exception as e:
                print("본문 읽기 실패:", src, e)
    if texts:
        json.dump(texts, open(base / "pages.json", "w"), ensure_ascii=False, indent=1)


def get_image(ref, base, k):
    """'press03' 같은 후보 번호 또는 이미지 주소."""
    if not ref:
        return None
    if not ref.startswith("http"):
        p = base / "cand" / (ref if ref.endswith(".jpg") else ref + ".jpg")
        return str(p) if p.exists() else None
    p = base / "bg" / f"u{k:02d}.jpg"
    os.makedirs(p.parent, exist_ok=True)
    r = requests.get(ref, headers=BROWSER_UA, timeout=30)
    if not r.ok:
        return None
    open(p, "wb").write(r.content)
    return str(p) if _good_image(str(p)) else None


def build(d, base, send):
    from .main import SLOT_LABEL, build_caption
    from .render import render
    imgs = d.get("images", [])
    slides = []
    for k, s in enumerate(d["slides"]):
        s = {"t": s.get("t", "").replace("\\n", "\n"), "b": s.get("b", ""), "sub": s.get("sub", "")}
        s["image"] = get_image(imgs[k] if k < len(imgs) else None, base, k)
        slides.append(s)
    if slides and not slides[-1]["image"]:
        slides[-1]["image"] = slides[0]["image"]  # 팔로우 카드는 표지 사진 재사용
    for f in glob.glob(str(base / "[0-9][0-9].jpg")) + glob.glob(str(base / "[0-9][0-9].mp4")):
        os.remove(f)
    vids = {k: s["video"] for k, s in enumerate(d["slides"]) if s.get("video")}
    texted = [k for k in vids if slides[k]["t"].strip() or slides[k]["b"].strip()]
    files = render(slides, str(base), overlays=texted)
    from .main import make_reel, make_story
    make_reel(files, base)   # 릴스·스토리는 카드 이미지(jpg)로
    make_story(files, base)
    if vids:
        from .video import video_slide
        for k, v in vids.items():  # 영상 장: 원본 영상 위에 같은 글자를 얹은 mp4로 교체
            out = str(base / f"{k + 1:02d}.mp4")
            video_slide(str(base / v["src"]), str(base / f"{k + 1:02d}_overlay.png") if k in texted else None, out,
                        v.get("start", 0), v.get("dur", 10), v.get("x", 0.5), v.get("y", 0.5))
            files[k] = out
    if not send:
        return
    pid, slot = d["id"], d.get("slot", "lunch")
    credits = list(dict.fromkeys(d.get("photo_credits", [])))
    post = {"id": pid, "slot": slot, "slot_label": SLOT_LABEL.get(slot, slot), "status": "pending",
            "created_at": now().isoformat(), "publish_at": slot_time(slot).isoformat(),
            "topic": d["topic"], "category": d.get("category", ""), "core": d.get("core", ""),
            "risk": d.get("risk", ""), "sources": d["sources"], "slides": [{"t": s["t"], "b": s["b"]} for s in slides],
            "caption_full": build_caption(d, credits), "credits": credits, "manual": True}
    from . import telegram_bot as tg
    post["files"] = files
    post["tg_msg"] = tg.send_preview(post)
    post["files"] = [os.path.relpath(f, ROOT) for f in files]
    if d.get("publish_now"):
        post.update(status="approved", publish_at=now().isoformat(), decided_at=now().isoformat())
    elif d.get("publish_at"):  # 채팅에서 승인받고 시각을 정한 경우: "2026-10-15T21:00:00+09:00"
        post.update(publish_at=d["publish_at"])
        if d.get("approved"):
            post.update(status="approved", decided_at=now().isoformat())
    save_post(post)


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    for d in (data if isinstance(data, list) else [data]):
        one(d)


def one(d):
    base = MEDIA / d["id"]
    os.makedirs(base, exist_ok=True)
    mode = d.get("mode", "collect")
    if mode == "collect" or not (base / "cand").exists() and any(not str(x).startswith("http") for x in d.get("images", [])):
        collect(d, base)
    if mode in ("render", "send"):
        build(d, base, mode == "send")


if __name__ == "__main__":
    main(sys.argv[1])
