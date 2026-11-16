"""state/tg_outbox/*.md 를 텔레그램 기본 봇으로 보내고 지운다(2026.11.10, 소재 추천 알림용).
긴 글은 줄 단위로 3,900자 안쪽 조각으로 나눠 보낸다. README.md·.gitkeep 은 건너뛴다."""
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cardnews.telegram_bot import send_text  # noqa: E402

LIMIT = 3900


def chunks(text):
    out, cur = [], ""
    for line in text.splitlines(keepends=True):
        while len(line) > LIMIT:
            if cur:
                out.append(cur); cur = ""
            out.append(line[:LIMIT]); line = line[LIMIT:]
        if len(cur) + len(line) > LIMIT:
            out.append(cur); cur = ""
        cur += line
    if cur.strip():
        out.append(cur)
    return out


def main():
    box = pathlib.Path("state/tg_outbox")
    sent = 0
    for f in sorted(box.glob("*.md")):
        if f.name == "README.md":
            continue
        parts = chunks(f.read_text(encoding="utf-8"))
        for i, p in enumerate(parts):
            head = f"({i + 1}/{len(parts)})\n" if len(parts) > 1 else ""
            send_text(head + p)
            time.sleep(1)
        f.unlink()
        sent += 1
        print(f"보냄: {f.name} ({len(parts)}조각)")
    print(f"총 {sent}개")


if __name__ == "__main__":
    main()
