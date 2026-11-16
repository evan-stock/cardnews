"""SNS 게시물 '실제 캡처' 카드 (안사리 카드 양식, 2026.11.08).
노란 작은 줄(날짜·출처) → 굵은 제목 → 둥근 테두리 안 캡처 → 회색 캡션 → 노란 소제목 + 본문 → 하단 로고. 1080x1350.
사용: python scripts/post_cap_card.py spec.json
spec: {"out": "...jpg", "sub": "...", "title": "줄1\\n'강조'", "cap": "캡처.png", "cap_crop": [x0,y0,x1,y1] (선택),
       "cap_max_h": 560 (선택), "caption": "...", "label": "...", "lines": ["'강조' 포함 줄", ...]}
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xpost_cards import W, H, P, BG, MU, YE, LN, F, rich, logo, head  # noqa: E402


def card(s):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    y = head(d, s["sub"], s["title"], y=s.get("top", 110))
    cap = Image.open(s["cap"]).convert("RGB")
    if s.get("cap_crop"):
        cap = cap.crop(tuple(s["cap_crop"]))
    bw = W - 2 * P
    pad = 6
    cw = bw - 2 * pad
    ch = round(cap.height * cw / cap.width)
    mh = s.get("cap_max_h", 560)
    if ch > mh:  # 너무 길면 높이에 맞추고 가운데
        cw, ch = round(cap.width * mh / cap.height), mh
    cap = cap.resize((cw, ch), Image.LANCZOS)
    bh = ch + 2 * pad
    y += 6
    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, bw - 1, bh - 1), 26, fill=255)
    box = Image.new("RGB", (bw, bh), tuple(s.get("box_bg", (11, 10, 24))))
    box.paste(cap, ((bw - cw) // 2, pad))
    im.paste(box, (P, y), mask)
    d.rounded_rectangle((P, y, P + bw - 1, y + bh - 1), 26, outline=LN, width=3)
    y += bh + 18
    d.text((P, y), s["caption"], font=F("Medium", 24), fill=MU)
    y += 64
    if s.get("label"):
        d.text((P, y), s["label"], font=F("SemiBold", 32), fill=YE)
        y += 56
    for ln in s.get("lines", []):
        rich(d, P, y, ln, F("Medium", 34))
        y += 52
    if y > H - 100:
        print("경고: 본문이 로고와 겹칠 수 있음", y)
    logo(im)
    im.save(s["out"], quality=93)
    print(s["out"], "bottom", y)


if __name__ == "__main__":
    for s in json.load(open(sys.argv[1], encoding="utf-8")):
        card(s)
