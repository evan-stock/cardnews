"""기존 게시물을 Claude 재호출 없이 사진 수집·렌더링만 다시 해본다 (비용 0)."""
import json, os, shutil, sys
sys.path.insert(0, os.getcwd())
from cardnews.common import load_post, MEDIA
from cardnews.images import pick_images
from cardnews.render import render
pid = sys.argv[1]
p = load_post(pid)
slides = [dict(s) for s in p["slides"]]
pages = [s["url"] for s in p["sources"] if s.get("url")] + p.get("image_pages", [])
out = MEDIA / (pid + "-retry")
shutil.rmtree(out, ignore_errors=True)
credits = pick_images(slides, str(out / "bg"), pages=pages)
last = len(slides) - 1
slides = [s for i, s in enumerate(slides) if i in (0, last) or s.get("image") or s["t"].strip()]
files = render(slides, str(out))
shutil.rmtree(out / "bg", ignore_errors=True)
json.dump({"credits": credits, "files": files, "with_image": [bool(s.get("image")) for s in slides]}, open(out / "result.json", "w"), ensure_ascii=False, indent=1)
print(credits, len(files))
