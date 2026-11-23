"""20261123-zico: 커맨더지코 주식 폭락 오열(스포츠서울 11.23). 엑스 정리 숫자는 사용자 지시로 '온라인 정리' 표시해 본문에."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
D = Path(__file__).parent; O = D / "cand"; R = D.parents[1]


def clip(src, boxes, out):
    ims = [Image.open(O / src).convert("RGB").crop(b) for b in boxes]
    W_ = max(i.width for i in ims); gap = 30
    c = Image.new("RGB", (W_ + 80, sum(i.height for i in ims) + gap * (len(ims) - 1) + 60), (255, 255, 255)); y = 30
    for i in ims: c.paste(i, (40, y)); y += i.height + gap
    c.save(O / out)


clip("ss.jpg", [(0, 590, 1520, 795), (0, 1080, 1520, 1190)], "k02.png")
clip("ss.jpg", [(0, 1565, 1520, 1680), (0, 1763, 1520, 1875)], "k03.png")
clip("ss.jpg", [(0, 2516, 1520, 2625), (0, 2705, 1520, 2820)], "k04.png")
clip("ss.jpg", [(0, 3659, 1520, 3765)], "k05.png")
clip("ss.jpg", [(0, 3828, 1520, 4110)], "k06.png")

E = [255, 255, 255]; base = {"box_bg": E, "cap_max_h": 660, "caption": "스포츠서울 기사 캡처"}
spec = [
 dict(base, out=str(O / "c02.jpg"), sub="스포츠서울 · 11월 23일", title="200억 넣은 주식 폭락에\n방송 중 '오열'", cap=str(O / "k02.png"),
      label="22일 SOOP 라이브, 집에서 술 마시며", lines=["\"너무 힘들다\" 눈물로 호소"]),
 dict(base, out=str(O / "c03.jpg"), sub="스포츠서울 · 11월 23일", title="아이온큐 레버리지\n마이너스 '90%'", cap=str(O / "k03.png"),
      label="50억 주택담보대출까지", lines=["\"주식은 내 돈 아니다 생각해야\""]),
 dict(base, out=str(O / "c04.jpg"), sub="스포츠서울 · 11월 23일", title="\"직원들 월급도\n'밀렸다'\"", cap=str(O / "k04.png"),
      label="소속 스트리머 정산도 지연", lines=["\"진짜 이번엔 내가 너무 힘들다\""]),
 dict(base, out=str(O / "c05.jpg"), sub="스포츠서울 · 11월 23일", title="세금도 남았다\n거액 '추징금' 전망", cap=str(O / "k05.png"),
      label="온라인 정리엔 \"내년 세금 '90억'\"", lines=["아내에게 빌린 '15억'·정산금 '20억' 미지급 주장도"]),
 dict(base, out=str(O / "c06.jpg"), sub="스포츠서울 · 11월 23일", title="7년 전 '일반인 비하'\n그 방송인이었다", cap=str(O / "k06.png"),
      label="2019년 출근길 시민에 \"출근하세요?\"", lines=["2023년 별풍선만 '360억' 추산(온라인 정리)"]),
]
json.dump(spec, open(O / "cap_spec.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "cap_spec.json")], check=True)
# (화질 낮아 교체) f = Image.open(O / "f4.5.jpg").convert("RGB").crop((400, 0, 914, 642))
# f = ImageEnhance.Sharpness(f.resize((1080, 1349), Image.LANCZOS)).enhance(1.4)
# f.save(O / "cover_bg.jpg", quality=95)
print("ok")
