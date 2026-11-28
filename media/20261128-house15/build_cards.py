"""20261128-house15: '집 15채 산 96년생'(영크크 브이로그) 화제, 대출로 빌라 경매 모으기 구조·누리꾼 우려 캡처 카드."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"

def side(srcs, out, crop=None, gap=16, pad=16, bg=(11, 10, 24)):
    ims = [Image.open(O / s).convert("RGB") for s in srcs]
    if crop:
        ims = [i.crop(crop) for i in ims]
    w = sum(i.width for i in ims) + gap * (len(ims) - 1) + pad * 2
    h = max(i.height for i in ims) + pad * 2
    c = Image.new("RGB", (w, h), bg); x = pad
    for i in ims:
        c.paste(i, (x, pad)); x += i.width + gap
    c.save(O / out)

def stitch(src, boxes, out, pad=(40, 30), gap=24):
    im = Image.open(O / src).convert("RGB")
    parts = [im.crop(b) for b in boxes]
    w = max(p.width for p in parts) + pad[0] * 2
    h = sum(p.height for p in parts) + gap * (len(parts) - 1) + pad[1] * 2
    c = Image.new("RGB", (w, h), "white"); y = pad[1]
    for p in parts:
        c.paste(p, (pad[0], y)); y += p.height + gap
    c.save(O / out)

CROP = (60, 100, 860, 1120)
side(["p3.jpg", "p5.jpg"], "cap_auction.png", CROP)
side(["p15.jpg", "p17.jpg"], "cap_loan.png", CROP)
side(["p12.jpg", "p19.jpg"], "cap_15.png", CROP)
EXTRA = json.load(open(D / "extra.json")) if (D / "extra.json").exists() else {}
for k, v in EXTRA.get("stitch", {}).items():
    stitch(v["src"], v["boxes"], k)

DK = [11, 10, 24]; W = [255, 255, 255]
spec = [
 {"out": str(O / "c02.jpg"), "sub": "96년생 '영크크' 브이로그", "box_bg": DK,
  "title": "경매 최저가\n'8,600만원' 빌라", "cap": str(O / "cap_auction.png"),
  "caption": "영상 캡처 · 영크크 브이로그", "label": "감정가 1억6,850만원에서 51% 떨어진 값",
  "lines": ["\"이번에도 빌라가 똥값으로 나왔더라구요\"", "서울남부지법 경매에 나온 다세대 빌라"], "cap_max_h": 700},
 {"out": str(O / "c03.jpg"), "sub": "그런데 돈이 없다", "box_bg": DK,
  "title": "마통·직장 대출에\n'친구 대출'까지", "cap": str(O / "cap_loan.png"),
  "caption": "영상 캡처 · 영크크 브이로그", "label": "\"일단 돈이 없는 저는\"",
  "lines": ["마이너스 통장 5,000만원(금리 5.81%)", "직장 대출, 친구 대출(?)을 '끌어 모아서' 산다"], "cap_max_h": 700},
 {"out": str(O / "c04.jpg"), "sub": "그렇게 모은 게", "box_bg": DK,
  "title": "부동산 '15채'", "cap": str(O / "cap_15.png"),
  "caption": "영상 캡처 · 영크크 브이로그", "label": "\"시세보다 3,000만원 싸게 샀기 때문에\"",
  "lines": ["리조트 수영장 앞 독서 장면으로", "'\"영크크인 제가 15채를 모을 수 있었죠\"'"], "cap_max_h": 700},
]
spec += EXTRA.get("cards", [])
for s in spec:
    if not s["cap"].startswith("/"):
        s["cap"] = str(O / s["cap"]); s["out"] = str(O / s["out"])
json.dump(spec, open(O / "caps.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "caps.json")], check=True, cwd=R)
