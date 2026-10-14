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
        s = {"t": s.get("t", "").replace("\\n", "\n"), "b": s.get("b", "")}
        s["image"] = get_image(imgs[k] if k < len(imgs) else None, base, k)
        slides.append(s)
    if slides and not slides[-1]["image"]:
        slides[-1]["image"] = slides[0]["image"]  # 팔로우 카드는 표지 사진 재사용
    for f in glob.glob(str(base / "[0-9][0-9].jpg")):
        os.remove(f)
    files = render(slides, str(base))
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
    save_post(post)


def main(path):
    d = json.load(open(path, encoding="utf-8"))
    base = MEDIA / d["id"]
    os.makedirs(base, exist_ok=True)
    mode = d.get("mode", "collect")
    if mode == "collect" or not (base / "cand").exists() and any(not str(x).startswith("http") for x in d.get("images", [])):
        collect(d, base)
    if mode in ("render", "send"):
        build(d, base, mode == "send")


if __name__ == "__main__":
    main(sys.argv[1])
