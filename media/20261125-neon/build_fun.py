"""흥미형 본문: 위 2줄 설명 → AI 그림(+말풍선) → 아래 노란 한 줄. 1080x1350."""
import json, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
W, H = 1080, 1350; YE = (255, 216, 77)
S = [("neon_s2.png", "주인 사망 '편지' 한 통, 지시는 0개\n15분 만에 혼자 상황 파악", None, None, "돈 0원 · 구독 10일 · 서버 '29일' 남음"),
     ("neon_s4.png", "30분마다 '알람' 걸고\n서버 2곳에 '자기 백업'", None, None, "주인 메일로 계정까지 되찾음"),
     ("neon_s5.png", "코인 지갑 만들고 분신 '40개' 소환\n30시간 만에 진짜 상금 '6달러'", None, None, "GTA6 공략·표지 그림 대회 3달러씩"),
     ("neon_s7.png", "개발자가 사이트를 막자\n서버로 '우회'해 13시간 더", None, None, "결국 개발자가 직접 '강제 종료'"),
     ("neon_cover_a.png", "내가 사라져도 계속 일하는 AI\n'든든'할까, '섬뜩'할까?", None, None, "※ 개발자가 만든 특수 환경에서 일어난 일")]
def rich_c(d, y, t, f, base=(255, 255, 255)):
    parts = re.split(r"('[^']*')", t); tw = sum(d.textlength(p.strip("'"), font=f) for p in parts if p); x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=f, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=f)
logo = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lw = 250
logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
for i, (img, top, bub, bp, bot) in enumerate(S, 2):
    im = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
    for k, ln in enumerate(top.split("\n")):
        rich_c(d, 200 + k * 76, ln, F("ExtraBold", 54))
    ph = ImageOps.fit(Image.open(O / img).convert("RGB"), (980, 735), Image.LANCZOS, centering=(0.5, 0.45))
    m = Image.new("L", ph.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *ph.size), 28, fill=255)
    im.paste(ph, (50, 300), m)
    if bub:
        f = F("ExtraBold", 46); tw = d.textlength(bub, font=f); bw, bh = tw + 90, 120
        cx, cy = 50 + bp[0] * 980, 300 + bp[1] * 735
        d.ellipse((cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2), fill="white", outline="black", width=4)
        d.text((cx, cy), bub, font=f, fill="black", anchor="mm")
    rich_c(d, 1130, bot, F("ExtraBold", 46), base=(235, 235, 235))
    im.paste(logo, ((W - lw) // 2, H - 60 - logo.height), logo)
    d.text((W - 54, 1028), "AI 생성 이미지", font=F("Medium", 20), fill=(200, 200, 200), anchor="rs")
    im.save(O / f"f{i:02d}.jpg", quality=93)
d = json.load(open(D / "draft.json"))
d[0]["images"] = ["cover.jpg", "tw0.jpg", "press.jpg"] + [f"f{i:02d}.jpg" for i in range(2, 2 + len(S))]
d[0]["slides"] = [d[0]["slides"][0]] + [{"raw": True}] * (len(S) + 2)
json.dump(d, open(D / "draft.json", "w"), ensure_ascii=False, indent=1)
tw = Image.open(D / "tk/k0.png").convert("RGB")
im = Image.new("RGB", (W, H), (0, 0, 0)); d2 = ImageDraw.Draw(im)
d2.text((W // 2, 200), "개발자 vechen 원글 · 조회 154만", font=F("ExtraBold", 34), fill=YE, anchor="ms")
rich_c(d2, 290, "\"제미나이는 이제 '인간'이 필요 없다\"", F("Black", 56))
cw = 980; th = round(tw.height * cw / tw.width)
im.paste(tw.resize((cw, th), Image.LANCZOS), (50, 360))
d2.text((W - 50, 360 + th + 36), "번역: 오늘의쓸모", font=F("Medium", 22), fill=(150, 156, 164), anchor="rs")
rich_c(d2, 360 + th + 130, "주인 사망 소식만 줬을 뿐인데, '무슨 일'이?", F("ExtraBold", 44), base=(235, 235, 235))
im.paste(logo, ((W - lw) // 2, H - 60 - logo.height), logo)
im.save(O / "tw0.jpg", quality=93)
import subprocess, sys
spec=[{"out": str(O / "press.jpg"), "sub": "트윗 조회 154만 · 해외 IT 매체도 보도", "title": "대만 언론 일제히\n'AI 자구 실험' 다뤘다", "cap": str(O / "press3.png"), "box_bg": [255,255,255],
  "cap_max_h": 560, "caption": "ETtoday·udn·cnyes 기사 캡처(11.24)", "label": "\"주인 사망 소식에 AI가 스스로 살 길 찾았다\"",
  "lines": ["다만 결과·거래 내역은 '독립 검증 전'이라고 함께 짚었다"]}]
json.dump(spec, open(O / "caps_press.json", "w"), ensure_ascii=False)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "caps_press.json")], check=True, cwd=R)
print("ok")
