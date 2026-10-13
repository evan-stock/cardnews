"""외부 API 없이 전체 흐름을 검증하는 테스트 (렌더링은 실제로 실행).
실행: python -m tests.test_flow  (프로젝트 루트에서, playwright 필요)
"""
import datetime as dt
import glob
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("GITHUB_REPOSITORY", "me/cardnews")

from cardnews import common, images, main, research  # noqa: E402

LOG = []


def fake_clock(h, m, day=None):
    day = day or dt.date(2026, 10, 14)
    t = dt.datetime.combine(day, dt.time(h, m), tzinfo=common.TZ)
    common.now = main.now = research.now = lambda: t


def sample():
    return {
        "topic": "테스트 소재", "category": "해외 시사", "core": "핵심", "why": "이유", "risk": "",
        "slides": [{"t": f"제목 {i}", "b": f"본문 {i} 입니다.", "photo_query": f"q{i}", "ai_prompt": "p"} for i in range(6)]
        + [{"t": "팔로우하고 먼저 받아보세요", "b": "매일 화제 소식", "photo_query": "q6", "ai_prompt": ""}],
        "caption": "후킹 한 줄\n\n요약", "hashtags": ["테스트", "#오늘의쓸모"],
        "sources": [{"publisher": "Axios", "title": "t", "url": "https://x", "date": "2026.10.13"}],
    }


def setup(tmp_imgs):
    research.research = lambda slot: research.validate(sample(), 7)

    def pick(slides, outdir, **k):
        for i, s in enumerate(slides):
            s["image"] = tmp_imgs[i % len(tmp_imgs)] if tmp_imgs and i % 2 == 0 else None
        return ["Tester(CC BY 2.0)"]
    images.pick_images = pick
    import cardnews.images as im_mod
    im_mod.pick_images = pick
    main.tg.send_preview = lambda post: LOG.append(("preview", post["id"], len(post["files"]))) or 99
    main.tg.send_text = lambda text, **k: LOG.append(("text", text.splitlines()[0]))
    main.instagram.publish_carousel = lambda urls, cap: (LOG.append(("ig", len(urls), urls[0], cap[:20])) or ("m1", "https://instagram.com/p/x"))


def run():
    # 깨끗한 상태
    shutil.rmtree(common.POSTS, ignore_errors=True)
    shutil.rmtree(common.MEDIA, ignore_errors=True)
    if os.path.exists(common.STATE / "telegram_offset.txt"):
        os.remove(common.STATE / "telegram_offset.txt")
    imgs = sorted(glob.glob(os.path.join(ROOT, "tests", "img", "*.jpg")))
    setup(imgs)

    # 1) JSON 추출/검증
    d = research.extract_json('설명...\n```json\n{"a":1}\n```')
    assert d == {"a": 1}

    # 2) 라이선스 필터
    assert images.OK_LICENSE.match("CC BY-SA 4.0") and images.OK_LICENSE.match("Public domain")
    assert not images.OK_LICENSE.match("Fair use")

    # 3) 점심: 11:15 준비 → 12:00 승인 → 12:30 대기 → 13:01 게시
    fake_clock(11, 15)
    main.prepare("lunch")
    p = common.load_post("20261014-lunch")
    assert p["status"] == "pending" and len(p["files"]) == 7, p
    assert "출처: Axios 2026.10.13" in p["caption_full"] and "#오늘의쓸모" in p["caption_full"]
    assert "##" not in p["caption_full"]
    main.prepare("lunch")  # 중복 준비 방지
    assert sum(1 for x in LOG if x[0] == "preview") == 1

    main.tg.poll_decisions = lambda: [("20261014-lunch", "ok")]
    fake_clock(12, 0)
    main.tick()
    assert common.load_post("20261014-lunch")["status"] == "approved"
    main.tg.poll_decisions = lambda: []
    fake_clock(12, 30)
    main.tick()
    assert common.load_post("20261014-lunch")["status"] == "approved"
    fake_clock(13, 1)
    main.tick()
    p = common.load_post("20261014-lunch")
    assert p["status"] == "published" and p["permalink"], p
    ig = [x for x in LOG if x[0] == "ig"][0]
    assert ig[1] == 7 and ig[2] == "https://raw.githubusercontent.com/me/cardnews/main/media/20261014-lunch/01.jpg", ig

    # 4) 저녁: 승인 없음 → 18:00+3h 지나면 만료
    fake_clock(16, 15)
    main.prepare("evening")
    fake_clock(20, 59)
    main.tick()
    assert common.load_post("20261014-evening")["status"] == "pending"
    fake_clock(21, 1)
    main.tick()
    assert common.load_post("20261014-evening")["status"] == "expired"

    # 5) 거절 처리, 늦은 승인(게시 시각 이후)은 바로 게시
    fake_clock(11, 15, dt.date(2026, 10, 15))
    main.prepare("lunch")
    main.tg.poll_decisions = lambda: [("20261015-lunch", "no")]
    main.tick()
    assert common.load_post("20261015-lunch")["status"] == "rejected"
    fake_clock(16, 15, dt.date(2026, 10, 15))
    main.prepare("evening")
    main.tg.poll_decisions = lambda: [("20261015-evening", "ok")]
    fake_clock(18, 40, dt.date(2026, 10, 15))
    main.tick()
    assert common.load_post("20261015-evening")["status"] == "published"

    # 6) 실패 시 상태 기록 + 알림
    research.research = lambda slot: (_ for _ in ()).throw(RuntimeError("검색 실패 테스트"))
    fake_clock(11, 15, dt.date(2026, 10, 16))
    try:
        main.prepare("lunch")
    except RuntimeError:
        pass
    assert common.load_post("20261016-lunch")["status"] == "failed"
    assert any(x[0] == "text" and "준비 실패" in x[1] for x in LOG)

    # 7) 기사·영상 사진 수집 (가짜 웹)
    from unittest import mock
    img = open(imgs[0], "rb").read() if imgs else b""
    html = ('<html><head><meta property="og:image" content="https://news.x/main.jpg"><meta name="twitter:image" content="/logo.png"></head>'
            '<body><article><img src="https://news.x/a1.jpg"><img data-src="https://news.x/a2.jpg"><img src="/icons/btn.png"></article></body></html>')

    def fake_get(url, headers=None, timeout=None, params=None):
        r = mock.Mock(ok=True, status_code=200)
        r.raise_for_status = lambda: None
        if "oembed" in url:
            r.json = lambda: {"thumbnail_url": "https://tt.x/thumb.jpg"}
        elif url.endswith(".jpg"):
            r.content = img
            r.headers = {"content-type": "image/jpeg"}
        else:
            r.text = html
        return r
    with mock.patch("cardnews.images.requests.get", fake_get):
        assert images.page_images("https://news.x/story") == ["https://news.x/main.jpg", "https://news.x/a1.jpg", "https://news.x/a2.jpg"], images.page_images("https://news.x/story")
        assert images.page_images("https://www.tiktok.com/@a/video/1") == ["https://tt.x/thumb.jpg"]
        assert images.page_images("https://www.youtube.com/watch?v=abc")[0].endswith("/abc/maxresdefault.jpg")
        if imgs:
            got = images.press_images(["https://news.x/story"], "/tmp/press_test")
            assert len(got) == 1 and got[0][1] == "news.x", got  # 같은 이미지 내용은 중복 제거

    print("모든 테스트 통과")
    print(json.dumps(LOG, ensure_ascii=False, indent=0)[:1500])


if __name__ == "__main__":
    run()
