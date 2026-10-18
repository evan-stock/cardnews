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
from .common import CFG, MEDIA, ROOT, all_posts, load_post, new_post_id, now, save_post, slot_time

SLOT_LABEL = {"lunch": "점심", "evening": "저녁"}


def build_caption(d, credits):
    parts = [d["caption"].strip()]
    src = ", ".join(f"{s.get('publisher', '')} {s.get('date', '')}".strip() for s in d["sources"][:3])
    parts.append(f"출처: {src}")
    if credits:
        parts[-1] += "\n사진: " + ", ".join(credits[:6]) + (", 위키미디어 커먼즈" if any("CC" in c or "Public domain" in c for c in credits) else "")
    tags = [h.lstrip("#") for h in d.get("hashtags", []) if h][:5]  # 인스타 해시태그 상한 5개
    if tags:
        parts.append(" ".join("#" + h for h in tags))
    return "\n\n".join(parts)


def media_url(pid, fname):
    base = os.environ.get("MEDIA_BASE_URL")
    if not base:
        repo = os.environ.get("GITHUB_REPOSITORY")
        branch = os.environ.get("GITHUB_REF_NAME", "main")
        base = f"https://raw.githubusercontent.com/{repo}/{branch}/media"
    return f"{base.rstrip('/')}/{pid}/{fname}"


def make_story(files, workdir):
    """게시 직후 올릴 스토리 이미지(표지 9:16). 실패해도 진행."""
    sc = CFG.get("stories", {})
    if not sc.get("enabled"):
        return None
    try:
        from .reels import story_image
        return story_image(files[0], os.path.join(str(workdir), "story.jpg"),
                           sc.get("top_text", "새 게시물"), sc.get("bottom_text", "프로필에서 전체 보기"))
    except Exception:
        traceback.print_exc()
        return None


def publish_story_for(post):
    if not CFG.get("stories", {}).get("enabled") or not (MEDIA / post["id"] / "story.jpg").exists():
        return
    try:
        sid = instagram.publish_story(media_url(post["id"], "story.jpg"))
        post["story_media_id"] = sid
    except Exception as e:
        post["story_error"] = str(e)[:300]
        tg.send_text(f"⚠️ 스토리 게시 실패(카드뉴스는 게시됨): {str(e)[:300]}")


def make_reel(files, workdir):
    """카드뉴스 전체를 자동으로 넘기는 9:16 릴스 영상(무음)을 만든다. 실패해도 카드뉴스는 그대로 진행."""
    if not CFG.get("reels", {}).get("enabled"):
        return None
    try:
        from .reels import cards_reel
        out = os.path.join(str(workdir), "reel.mp4")
        rc = CFG["reels"]
        cards_reel([f[:-4] + ".jpg" if f.endswith(".mp4") else f for f in files], out, per=rc.get("per_card", 3.0), first=rc.get("first_card", 2.0))
        return out
    except Exception:
        traceback.print_exc()
        return None


def reel_caption(post):
    """릴스에 카드 전체가 들어가므로 본문도 카드뉴스 본문 그대로."""
    return post["caption_full"].strip()


def publish_reel_for(post):
    rc = CFG.get("reels", {})
    path = MEDIA / post["id"] / "reel.mp4"
    if not rc.get("enabled") or not path.exists():
        return
    try:
        tg.send_video(str(path), "🎬 릴스용 영상(표지). 저장해서 앱에서 음악을 붙여 올리세요.\n바로 아래 메시지가 릴스 본문이에요(길게 눌러 복사).")
        tg.send_text(reel_caption(post))  # 본문만 단독 메시지로: 길게 눌러 그대로 복사
    except Exception as e:
        print("릴스 영상·본문 전송 실패:", e)
    if rc.get("mode") != "auto":
        return
    try:
        mid, link = instagram.publish_reel(media_url(post["id"], "reel.mp4"), reel_caption(post),
                                           share_to_feed=rc.get("share_to_feed", False))
        post.update(reel_media_id=mid, reel_permalink=link)
        tg.send_text(f"🎬 릴스 게시 완료: {post['topic']}\n{link}\n음악은 앱에서 추가하세요.")
    except Exception as e:
        post["reel_error"] = str(e)[:300]
        tg.send_text(f"⚠️ 릴스 게시 실패(카드뉴스는 게시됨): {str(e)[:300]}")


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
        found = list(dict.fromkeys(s["image"] for s in d["slides"][:last] if s.get("image")))
        if found:  # 글이 있는 장인데 사진이 없으면, 찾은 사진을 돌려 써서 검은 빈 배경을 피한다
            k = 0
            for s in d["slides"][1:last]:
                if not s.get("image") and s["t"].strip():
                    s["image"] = found[(k + 1) % len(found)] if len(found) > 1 else found[0]
                    k += 1
        if len(found) < 3:
            d["risk"] = (f"⚠️ 쓸 만한 사진이 {len(found)}장뿐이라 같은 사진을 반복했어요. 거절하고 채팅에서 사진을 보강하는 걸 추천. "
                         + (d.get("risk") or "")).strip()
        d["slides"] = [s for i, s in enumerate(d["slides"]) if i in (0, last) or s.get("image") or s["t"].strip()]
        for i, s in enumerate(d["slides"][1:-1], 1):
            if not s["t"].strip():
                s["b"] = ""  # 사진 장은 글자 없이 (사진 순서와 설명이 어긋나는 문제 방지)
        files = render(d["slides"], str(workdir))
        make_reel(files, workdir)
        make_story(files, workdir)
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


def push_media(post):
    """게시 직전에 카드·릴스 파일이 GitHub에 올라가 있는지 확인(인스타가 공개 주소에서 가져가므로)."""
    if not os.environ.get("GITHUB_ACTIONS"):
        return
    import subprocess
    run = lambda *a: subprocess.run(list(a), cwd=str(MEDIA.parent), capture_output=True, text=True)
    run("git", "add", "-A", str(MEDIA / post["id"]))
    if run("git", "diff", "--cached", "--quiet").returncode != 0:
        run("git", "-c", "user.name=cardnews-bot", "-c", "user.email=cardnews-bot@users.noreply.github.com",
            "commit", "-m", f"cardnews: media {post['id']}")
        run("git", "pull", "--rebase", "origin", os.environ.get("GITHUB_REF_NAME", "main"))
        r = run("git", "push")
        print("미디어 업로드:", r.returncode, r.stderr[-200:])
        import time
        time.sleep(20)


def short_ig_account(post):
    """쇼츠를 함께 올릴 인스타 계정(원소스 멀티유즈, 2026.10.18). 유튜브 채널별로 config shorts.instagram 에서 정한다."""
    m = (CFG.get("shorts", {}).get("instagram") or {})
    return m.get(post.get("yt", {}).get("channel") or "default")


def short_to_instagram(post):
    """유튜브에 올린 쇼츠를 같은 영상 그대로 인스타 릴스로도 게시. 실패해도 유튜브 결과는 그대로 둔다."""
    acct = short_ig_account(post)
    if not acct or post.get("ig_media_id"):
        return
    if not instagram.configured(acct):
        print(f"인스타 계정 '{acct}' 토큰이 아직 없어 릴스는 건너뜀")
        return
    y = post.get("yt", {})
    title = y.get("title", "").replace("#shorts", "").strip()
    body = y.get("description", "")
    body = body.split("\n\n#shorts")[0]
    tags = " ".join("#" + t.lstrip("#").replace(" ", "") for t in (y.get("tags") or [])[:8])
    caption = f"{title}\n\n{body}\n\n{tags}".strip()[:2200]
    try:
        instagram.use(acct)
        mid, link = instagram.publish_reel(media_url(post["id"], os.path.basename(post["files"][0])), caption,
                                           share_to_feed=True)
        post.update(ig_media_id=mid, ig_permalink=link)
        tg.send_text(f"📸 인스타 릴스도 게시 완료: {post['topic']}\n{link}")
    except Exception as e:
        post["ig_error"] = str(e)[:500]
        tg.send_text(f"⚠️ 인스타 릴스 게시 실패(유튜브는 정상): {post['topic']}\n{str(e)[:400]}")
    finally:
        instagram.use(None)


def publish_short(post):
    """승인된 쇼츠를 유튜브에 업로드. 게시 시각이 미래면 유튜브 예약 공개로 올린다."""
    from . import youtube
    try:
        at = dt.datetime.fromisoformat(post["publish_at"])
        # 중복 방지(2026.10.18 같은 영상이 두 번 올라간 사고): 같은 제목이 최근 업로드에 있으면 다시 올리지 않는다
        try:
            dup = [v for v, t in youtube.recent_uploads(post["yt"].get("channel")) if t == post["yt"]["title"][:100]]
        except Exception as e:
            dup = []
            print("최근 업로드 확인 실패(그대로 진행):", e)
        if dup:
            link = f"https://youtube.com/shorts/{dup[0]}"
            post.update(status="published", yt_id=dup[0], permalink=link, published_at=now().isoformat(),
                        note="이미 올라가 있어 다시 올리지 않음")
            tg.send_text(f"ℹ️ 이미 올라가 있는 영상이라 다시 올리지 않았어요: {post['topic']}\n{link}")
            save_post(post)
            sync_repo()
            return
        vid, link, st = youtube.upload(str(MEDIA.parent / post["files"][0]), post["yt"],
                                       None if post.get("publish_now") else at)
        post.update(status="published", yt_id=vid, permalink=link, published_at=now().isoformat())
        when = f"{at:%m/%d %H:%M} 자동 공개 예약" if st.get("publishAt") else "지금 공개"
        tg.send_text(f"▶️ 유튜브 쇼츠 업로드 완료({when}): {post['topic']}\n{link}")
        short_to_instagram(post)
    except Exception as e:
        post.update(status="failed", error=str(e)[:500])
        tg.send_text(f"⚠️ 유튜브 업로드 실패: {post['topic']}\n{str(e)[:500]}")
    save_post(post)
    sync_repo()  # 업로드 결과를 바로 저장소에 남긴다(실행이 중간에 끊겨도 상태가 사라지지 않게)


def do_publish(post):
    if post.get("kind") == "short":
        return publish_short(post)
    push_media(post)
    urls = [media_url(post["id"], os.path.basename(f)) for f in post["files"]]
    try:
        if post.get("format") == "reel":
            cover = media_url(post["id"], os.path.basename(post["cover"])) if post.get("cover") else None
            mid, link = instagram.publish_reel(urls[0], post["caption_full"], share_to_feed=True, cover_url=cover)
            post.update(status="published", ig_media_id=mid, permalink=link, published_at=now().isoformat())
            tg.send_text(f"🎬 릴스 게시 완료: {post['topic']}\n{link}\n\n📲 스토리 공유: 링크 열기 → 종이비행기 → '스토리에 추가'\n🎵 음악을 넣고 싶으면 앱에서 릴스 수정")
            save_post(post)
            return
        mid, link = instagram.publish_carousel(urls, post["caption_full"])
        post.update(status="published", ig_media_id=mid, permalink=link, published_at=now().isoformat())
        tg.send_text(f"🎉 게시 완료: {post['topic']}\n{link}\n\n📲 스토리 공유(10초): 링크 열기 → 종이비행기 → '스토리에 추가' → 투표·질문 스티커 붙여 올리기")
        publish_story_for(post)
        publish_reel_for(post)
    except Exception as e:
        post.update(status="failed", error=str(e)[:500])
        tg.send_text(f"⚠️ 게시 실패: {post['topic']}\n{str(e)[:500]}")
    save_post(post)


def send_app_kit(p):
    """[📱 앱으로 직접 올리기]: 유튜브 앱에서 쇼츠 음원(유행곡)을 붙여 올릴 수 있게 원본 화질 파일과 문구를 보낸다.
    배경음악이 있던 영상은 배경음악을 뺀 판(short_nobgm.mp4)을 보낸다. 이 게시물은 자동 업로드하지 않는다."""
    path = ROOT / (p.get("app_file") or p["files"][0])
    try:
        tg.send_document(str(path), f"📱 {p['topic']}\n저장 → 유튜브 앱 + → 동영상 업로드 → '사운드 추가'에서 음원 선택 → "
                                    "음량 조절에서 원본(내레이션·효과음) 크기 맞추기")
        y = p["yt"]
        tg.send_text(y["title"])
        tg.send_text(y["description"])
        tg.send_text(" ".join("#" + t for t in y.get("tags", [])) or "(태그 없음)")
        p.update(status="manual", decided_at=now().isoformat())
        tg.send_text(f"📱 앱 업로드용으로 보냈어요: {p['topic']} (자동 업로드는 하지 않아요. 위 세 메시지를 길게 눌러 복사)")
    except Exception as e:
        tg.send_text(f"⚠️ 앱 업로드용 파일 전송 실패: {p['topic']}\n{str(e)[:300]}")
    save_post(p)


def tick():
    decisions = tg.poll_decisions()
    for pid, act in decisions:
        p = load_post(pid)
        if not p or p["status"] != "pending":
            continue
        if act == "app" and p.get("kind") == "short":  # 앱 직접 업로드: 파일 + 복사할 문구를 보내고 자동 업로드는 하지 않는다
            send_app_kit(p)
            continue
        if act not in ("ok", "no"):
            continue
        p["status"] = "approved" if act == "ok" else "rejected"
        p["decided_at"] = now().isoformat()
        save_post(p)
        if act == "ok" and p.get("kind") == "short":
            tg.send_text(f"✅ 승인됨: {p['topic']}\n유튜브에 올리는 중이에요")
            continue
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
        if p["status"] == "approved" and p.get("kind") == "short":  # 쇼츠는 승인 즉시 업로드(예약은 유튜브가 처리)
            do_publish(p)
        elif p["status"] == "approved" and now() >= at:
            do_publish(p)
        elif p["status"] == "pending" and now() > at + (dt.timedelta(hours=24) if p.get("kind") == "short" else exp):
            p["status"] = "expired"
            save_post(p)
            tg.send_text(f"⌛ 승인 시간이 지나 게시하지 않았어요: {p['topic']}")


def sync_repo():
    """GitHub Actions에서: 로컬 상태 변경을 커밋하고 최신 main을 받아온 뒤 올린다."""
    if not os.environ.get("GITHUB_ACTIONS"):
        return
    import subprocess
    run = lambda *a: subprocess.run(list(a), cwd=str(MEDIA.parent), capture_output=True, text=True)
    # pull --rebase --autostash 도 커밋을 만들므로 저장소에 이름을 넣어 둔다(2026.10.18: 없어서 동기화가 계속 실패,
    # 새 게시물·승인이 실행 중인 watch 에 반영되지 않았음)
    run("git", "config", "user.name", "cardnews-bot")
    run("git", "config", "user.email", "cardnews-bot@users.noreply.github.com")
    run("git", "add", "-A", "state", "media")
    if run("git", "diff", "--cached", "--quiet").returncode != 0:
        run("git", "-c", "user.name=cardnews-bot", "-c", "user.email=cardnews-bot@users.noreply.github.com",
            "commit", "-m", f"cardnews: watch sync {now():%H%M}")
    r = run("git", "pull", "--rebase", "--autostash", "origin", os.environ.get("GITHUB_REF_NAME", "main"))
    if r.returncode != 0:
        print("동기화 실패:", r.stderr[-300:])
        run("git", "rebase", "--abort")
        return
    run("git", "push")


def watch(hours=6):
    """GitHub 예약 실행이 자주 밀려서, 대기 중인 게시물이 끝날 때까지 1분마다 직접 확인한다."""
    import time
    end = now() + dt.timedelta(hours=hours)
    while now() < end:
        sync_repo()  # 채팅에서 바꾼 예약·새 게시물을 실행 중에도 반영
        try:
            tick()
        except Exception:
            traceback.print_exc()
        if not any(p["status"] in ("pending", "approved") for p in all_posts()):
            print("대기 중인 게시물 없음, 종료")
            return
        time.sleep(60)


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
    ap.add_argument("cmd", choices=["prepare", "tick", "watch", "publish", "chat-id", "refresh-token", "prune", "ping"])
    ap.add_argument("--slot", choices=list(CFG["slots"]))
    ap.add_argument("--id")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.cmd == "prepare":
        prepare(a.slot, a.force)
    elif a.cmd == "watch":
        watch()
    elif a.cmd == "tick":
        tick()
        prune()
    elif a.cmd == "publish":
        do_publish(load_post(a.id))
    elif a.cmd == "chat-id":
        chat_id_helper()
    elif a.cmd == "refresh-token":
        print(instagram.refresh_token(a.id))  # --id furball 이면 털뭉치 계정
    elif a.cmd == "prune":
        prune()
    elif a.cmd == "ping":
        tg.send_text("✅ 오늘의쓸모 자동화 연결 테스트 성공!\nGitHub Actions → 텔레그램 연결이 잘 됐어요.")


if __name__ == "__main__":
    main()
