"""명령어:
  python -m cardnews.main prepare --slot lunch|evening   소재 조사 → 사진 → 카드 → 텔레그램 미리보기
  python -m cardnews.main tick                           승인 확인, 시간 되면 게시, 만료 처리
  python -m cardnews.main publish --id 20261014-lunch    수동 즉시 게시(승인 무시)
  python -m cardnews.main chat-id                        텔레그램 채팅방 ID 확인(설치용)
  python -m cardnews.main refresh-token                  인스타 토큰 갱신(새 토큰 출력)
"""
import argparse
import datetime as dt
import os
import shutil
import traceback

from . import instagram, telegram_bot as tg
from .common import CFG, MEDIA, all_posts, load_post, new_post_id, now, save_post, slot_time

SLOT_LABEL = {"lunch": "점심", "evening": "저녁"}


def build_caption(d, credits):
    parts = [d["caption"].strip()]
    src = ", ".join(f"{s.get('publisher', '')} {s.get('date', '')}".strip() for s in d["sources"][:3])
    parts.append(f"출처: {src}")
    if credits:
        parts[-1] += "\n사진: " + ", ".join(credits[:6]) + (", 위키미디어 커먼즈" if any("CC" in c or "Public domain" in c for c in credits) else "")
    if d.get("hashtags"):
        parts.append(" ".join("#" + h for h in d["hashtags"]))
    return "\n\n".join(parts)


def media_url(pid, fname):
    base = os.environ.get("MEDIA_BASE_URL")
    if not base:
        repo = os.environ.get("GITHUB_REPOSITORY")
        branch = os.environ.get("GITHUB_REF_NAME", "main")
        base = f"https://raw.githubusercontent.com/{repo}/{branch}/media"
    return f"{base.rstrip('/')}/{pid}/{fname}"


def prepare(slot, force=False):
    from .images import pick_images
    from .render import render
    from .research import research

    try:
        tick()  # 준비 전에 밤사이 눌린 승인/거절 버튼부터 반영
    except Exception as e:
        print("사전 승인 확인 실패:", e)
    pid = new_post_id(slot)
    old = load_post(pid)
    if old and not force and old["status"] not in ("failed", "rejected"):
        print("이미 준비된 게시물:", pid, old["status"])
        return
    try:
        d = research(slot)
        workdir = MEDIA / pid
        from urllib.parse import urlparse
        pages = [s.get("url") for s in d["sources"] if s.get("url")] + [u for u in d.get("image_pages", []) if str(u).startswith("http")]
        pubs = {urlparse(s.get("url", "")).netloc.replace("www.", ""): s.get("publisher", "") for s in d["sources"] if s.get("url")}
        credits = pick_images(d["slides"], str(workdir / "bg"), pages=list(dict.fromkeys(pages)), publishers=pubs,
                              story=f"{d['topic']} / {d.get('core', '')}")
        # 사진을 못 구한 '사진 장'은 빼서 빈 배경 카드가 나가지 않게 한다(표지·팔로우 카드는 유지)
        last = len(d["slides"]) - 1
        d["slides"] = [s for i, s in enumerate(d["slides"]) if i in (0, last) or s.get("image") or s["t"].strip()]
        for i, s in enumerate(d["slides"][1:-1], 1):
            if not s["t"].strip():
                s["b"] = ""  # 사진 장은 글자 없이 (사진 순서와 설명이 어긋나는 문제 방지)
        files = render(d["slides"], str(workdir))
        shutil.rmtree(workdir / "bg", ignore_errors=True)
        post = {
            "id": pid, "slot": slot, "slot_label": SLOT_LABEL.get(slot, slot), "status": "pending",
            "created_at": now().isoformat(), "publish_at": slot_time(slot).isoformat(),
            "topic": d["topic"], "category": d.get("category", ""), "core": d.get("core", ""),
            "risk": d.get("risk", ""), "sources": d["sources"], "slides": [{"t": s["t"], "b": s["b"], "photo_query": s.get("photo_query", ""), "ai_prompt": s.get("ai_prompt", "")} for s in d["slides"]],
            "image_pages": d.get("image_pages", []),
            "caption_full": build_caption(d, credits), "credits": credits,
            "files": [os.path.relpath(f, MEDIA.parent) for f in files],
        }
        save_post(post)
        post["files"] = files
        post["tg_msg"] = tg.send_preview(post)
        post["files"] = [os.path.relpath(f, MEDIA.parent) for f in files]
        save_post(post)
        print("준비 완료:", pid, post["topic"])
    except Exception as e:
        traceback.print_exc()
        save_post({"id": pid, "slot": slot, "status": "failed", "created_at": now().isoformat(), "error": str(e)[:500]})
        try:
            tg.send_text(f"⚠️ {SLOT_LABEL.get(slot, slot)} 카드뉴스 준비 실패\n{str(e)[:500]}\n\nGitHub Actions에서 prepare를 다시 실행하거나 로그를 확인해주세요.")
        except Exception:
            pass
        raise


def do_publish(post):
    urls = [media_url(post["id"], os.path.basename(f)) for f in post["files"]]
    try:
        mid, link = instagram.publish_carousel(urls, post["caption_full"])
        post.update(status="published", ig_media_id=mid, permalink=link, published_at=now().isoformat())
        tg.send_text(f"🎉 게시 완료: {post['topic']}\n{link}")
    except Exception as e:
        post.update(status="failed", error=str(e)[:500])
        tg.send_text(f"⚠️ 게시 실패: {post['topic']}\n{str(e)[:500]}")
    save_post(post)


def tick():
    decisions = tg.poll_decisions()
    for pid, act in decisions:
        p = load_post(pid)
        if not p or p["status"] != "pending":
            continue
        p["status"] = "approved" if act == "ok" else "rejected"
        p["decided_at"] = now().isoformat()
        save_post(p)
        if act == "ok":
            at = dt.datetime.fromisoformat(p["publish_at"])
            tg.send_text(f"✅ 승인됨: {p['topic']}\n" + ("곧 게시해요" if now() >= at else f"{at:%H:%M}에 게시돼요"))
        if act == "no":
            tg.send_text(f"❌ 거절됨: {p['topic']} (게시하지 않아요)")
    exp = dt.timedelta(hours=CFG["approval"]["expire_hours"])
    for p in all_posts():
        if p["status"] not in ("pending", "approved"):
            continue
        at = dt.datetime.fromisoformat(p["publish_at"])
        if p["status"] == "approved" and now() >= at:
            do_publish(p)
        elif p["status"] == "pending" and now() > at + exp:
            p["status"] = "expired"
            save_post(p)
            tg.send_text(f"⌛ 승인 시간이 지나 게시하지 않았어요: {p['topic']}")


def prune(days=7):
    cut = now() - dt.timedelta(days=days)
    for p in all_posts():
        try:
            if dt.datetime.fromisoformat(p["created_at"]) < cut and p["status"] in ("published", "rejected", "expired", "failed"):
                shutil.rmtree(MEDIA / p["id"], ignore_errors=True)
        except Exception:
            pass


def chat_id_helper():
    ups = tg._api("getUpdates")
    seen = {}
    for u in ups:
        m = u.get("message") or {}
        c = m.get("chat") or {}
        if c:
            seen[c["id"]] = c.get("username") or c.get("title") or c.get("first_name")
    print(seen or "봇에게 먼저 아무 메시지나 보낸 뒤 다시 실행하세요.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prepare", "tick", "publish", "chat-id", "refresh-token", "prune", "ping"])
    ap.add_argument("--slot", choices=list(CFG["slots"]))
    ap.add_argument("--id")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.cmd == "prepare":
        prepare(a.slot, a.force)
    elif a.cmd == "tick":
        tick()
        prune()
    elif a.cmd == "publish":
        do_publish(load_post(a.id))
    elif a.cmd == "chat-id":
        chat_id_helper()
    elif a.cmd == "refresh-token":
        print(instagram.refresh_token())
    elif a.cmd == "prune":
        prune()
    elif a.cmd == "ping":
        tg.send_text("✅ 오늘의쓸모 자동화 연결 테스트 성공!\nGitHub Actions → 텔레그램 연결이 잘 됐어요.")


if __name__ == "__main__":
    main()
