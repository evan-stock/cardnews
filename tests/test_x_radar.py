"""엑스 급상승 감지기 판단 로직 확인(네트워크 없이)."""
import importlib.util
import json
import pathlib

spec = importlib.util.spec_from_file_location("x_radar", pathlib.Path(__file__).parents[1] / "scripts/x_radar.py")
xr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xr)


def tid_at(ts):
    return str((int(ts * 1000) - xr.TW_EPOCH_MS) << 22)


def cfg(**kw):
    c = dict(xr.DEFAULTS, accounts=[], inbox=[])
    c.update(kw)
    return c


def fake_meter(table):
    def m(tid):
        v, l = table[tid]
        return {"author": "a", "name": "A", "followers": 1000000, "text": "글", "lang": "ko",
                "views": v, "likes": l, "rts": 0, "replies": 0, "video": True, "photo": False, "url": ""}
    return m


def test_id_time_roundtrip():
    assert abs(xr.created_from_id(tid_at(1790000000)) - 1790000000) < 1


def test_alert_on_velocity_then_once(tmp_path):
    t0 = 1790000000.0
    hot, slow, old = tid_at(t0 - 3600), tid_at(t0 - 3600 * 2), tid_at(t0 - 3600 * 20)
    c = cfg(inbox=[f"https://x.com/a/status/{x}" for x in (hot, slow, old)])
    sent = []
    table = {hot: (40000, 500), slow: (40000, 300), old: (5000000, 90000)}
    xr.run(c, tmp_path, sent.append, now=t0, meter=fake_meter(table), sleep=lambda s: None)
    assert sent == []  # 첫 측정: 평균 속도가 기준 아래, 오래된 글은 제외
    table = {hot: (70000, 900), slow: (42000, 310), old: (9000000, 99000)}
    xr.run(c, tmp_path, sent.append, now=t0 + 600, meter=fake_meter(table), sleep=lambda s: None)
    assert len(sent) == 1 and hot in sent[0] and "급상승" in sent[0]  # 10분에 3만 = 시간당 18만
    table[hot] = (120000, 1500)
    xr.run(c, tmp_path, sent.append, now=t0 + 1200, meter=fake_meter(table), sleep=lambda s: None)
    assert len(sent) == 1  # 같은 글은 다시 안 보냄
    table[hot] = (250000, 3000)
    xr.run(c, tmp_path, sent.append, now=t0 + 1800, meter=fake_meter(table), sleep=lambda s: None)
    assert len(sent) == 2 and "계속 오르는 중" in sent[1]  # 알린 뒤 3배
    assert "@a" in (tmp_path / "board.md").read_text(encoding="utf-8")


def test_small_account_reach(tmp_path):
    t0 = 1790000000.0
    tid = tid_at(t0 - 3600 * 3)
    def m(_):
        return {"author": "s", "name": "S", "followers": 2000, "text": "x", "lang": "ko", "views": 60000,
                "likes": 100, "rts": 0, "replies": 0, "video": False, "photo": True, "url": ""}
    sent = []
    xr.run(cfg(inbox=[tid]), tmp_path, sent.append, now=t0, meter=m, sleep=lambda s: None)
    assert len(sent) == 1 and "작은 계정" in sent[0]


def test_timeline_parse_and_drop(tmp_path):
    t0 = 1790000000.0
    new, old = tid_at(t0 - 600), tid_at(t0 - 3600 * 40)
    html = '<script id="__NEXT_DATA__" type="application/json">' + json.dumps({"props": {"pageProps": {"timeline": {"entries": [
        {"type": "tweet", "content": {"tweet": {"id_str": new, "user": {"screen_name": "w"}}}},
        {"type": "tweet", "content": {"tweet": {"id_str": old, "user": {"screen_name": "w"}}}},
        {"type": "tweet", "content": {"tweet": {"id_str": "5", "retweeted_status": {}}}}]}}}}) + "</script>"
    assert [x[0] for x in xr.parse_timeline_html(html)] == [new, old]
    xr.run(cfg(accounts=["w"]), tmp_path, lambda t: None, now=t0, discover=lambda a: xr.parse_timeline_html(html),
           meter=fake_meter({new: (10, 1)}), sleep=lambda s: None)
    assert list(json.loads((tmp_path / "track.json").read_text())) == [new]
