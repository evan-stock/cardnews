"""state/posts/<id>.json 게시물(릴스 등)의 표지·영상·본문을 텔레그램으로 미리보기 전송(승인/거절 버튼 포함)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cardnews import telegram_bot as tg

pid = sys.argv[1]
post = json.loads(Path(f"state/posts/{pid}.json").read_text())
if post.get("cover") and Path(post["cover"]).exists():
    tg.send_photo(post["cover"], "🖼 표지")
for f in post.get("files", []):
    (tg.send_video if f.lower().endswith(".mp4") else tg.send_photo)(f, "")
when = post.get("publish_at", "")[:16].replace("T", " ")
tg.send_text(f"🎬 [{when} 게시 예정] 미리보기\n\n──── 본문 ────\n{post.get('caption_full','')}\n\n"
             f"이미 승인 상태예요. 거절을 누르면 게시가 취소돼요.",
             buttons=[[{"text": "✅ 승인", "callback_data": f"ok:{pid}"},
                       {"text": "❌ 거절", "callback_data": f"no:{pid}"}]])
print("sent", pid)
