"""20261124-inverse: 젠슨 황 복귀 직전 '투자 귀재'들 — 캐시 우드·짐 크레이머·전인구, 그리고 하이닉스 사장."""
import json, subprocess, sys, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; O.mkdir(exist_ok=True)
T = Path("/tmp/claude-tool-results/a493c683-e7b1-5bd7-9aa7-411f6fdd042e")
def shot(name, box, out):
    Image.open(T / f"mcp-claude-in-chrome-blob-{name}.jpg").convert("RGB").crop(box).save(O / out)
shot("1795458323423-mygw49-243d83af", (40, 30, 900, 310), "cap_ark.png")
shot("1795479534971-xlnk3m-61891883", (35, 25, 840, 470), "cap_cramer.png")
shot("1795479587969-xjs4pd-61ff1969", (35, 25, 830, 335), "cap_kospi.png")
shot("1795479564491-afvc0d-82451689", (35, 25, 940, 345), "cap_sk.png")
Image.open("/mnt/user-data/uploads/a8fe0336-image.jpg").convert("RGB").save(O / "cap_jig.png")

# 표지: 캡처 카드 3장을 둥근 카드로 겹쳐 놓은 콜라주
W_, H_ = 1080, 1350
bg = Image.new("RGB", (W_, H_), (16, 16, 20))
glow = Image.new("L", (W_, H_), 0); ImageDraw.Draw(glow).ellipse((-150, 50, 1230, 1050), fill=110)
bg = Image.composite(Image.new("RGB", (W_, H_), (60, 45, 20)), bg, glow.filter(ImageFilter.GaussianBlur(180)))
def card(src, w, angle, xy):
    global bg
    im = Image.open(O / src).convert("RGB"); h = int(im.height * w / im.width); im = im.resize((w, h))
    pad = 18; c = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    m = Image.new("L", c.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, c.width - 1, c.height - 1), 28, fill=255)
    c.paste(Image.new("RGBA", c.size, (255, 255, 255, 255)), (0, 0), m)
    im_m = Image.new("L", im.size, 0); ImageDraw.Draw(im_m).rounded_rectangle((0, 0, w - 1, h - 1), 16, fill=255)
    c.paste(im, (pad, pad), im_m)
    c = c.rotate(angle, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", (c.width + 60, c.height + 60), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 150), (30, 40), c.split()[3]); sh = sh.filter(ImageFilter.GaussianBlur(18))
    base = bg.convert("RGBA"); base.alpha_composite(sh, (xy[0] - 30, xy[1] - 30)); base.alpha_composite(c, xy); bg = base.convert("RGB")
card("cap_ark.png", 760, 4, (40, 40))
card("cap_cramer.png", 720, -5, (300, 300))
card("cap_jig.png", 700, 3, (60, 520))
bg.save(O / "cover.jpg", quality=95)

Wc = [255, 255, 255]
spec = [
 {"out": str(O / "c_ark.jpg"), "sub": "① '돈나무 언니' 캐시 우드", "box_bg": Wc,
  "title": "복귀 직전 한 주\n엔비디아 '1억 달러' 넘게 팔았다", "cap": str(O / "cap_ark.png"),
  "caption": "야후파이낸스(구루포커스) 기사 캡처", "label": "그 전주엔 1,600만 달러어치 샀다가 뒤집어",
  "lines": ["팔고 난 다음 주 월요일", "엔비디아는 하루 31% 급등"], "cap_max_h": 330},
 {"out": str(O / "c_cramer.jpg"), "sub": "② '인버스 크레이머' 짐 크레이머", "box_bg": Wc,
  "title": "금요일 '약세'로 돌아서자\n월요일 '폭등'", "cap": str(O / "cap_cramer.png"),
  "caption": "미디에이트 기사 캡처", "label": "\"인버스 크레이머는 자연법칙\" 밈 폭발",
  "lines": ["사임 직후엔 \"차익 실현해 비중 줄여라\"(CNBC)", "복귀 날엔 \"이건 엄청난 일\"이라며 환호"], "cap_max_h": 470},
 {"out": str(O / "c_jig.jpg"), "sub": "③ 전인구경제연구소",
  "title": "\"AI 버블이 터지고 있다\"\n직후 엔비디아 '31%' 급등", "cap": str(O / "cap_jig.png"),
  "caption": "유튜브 영상 화면", "label": "\"검은 월요일이 온다\" 영상, 조회 60만 넘어",
  "lines": ["월요일 코스피는 실제로 -3.31%였지만", "다음 날 장중 6%대 급등하며 5,000 회복"], "cap_max_h": 560},
 {"out": str(O / "c_kospi.jpg"), "sub": "그리고 하루 뒤", "box_bg": Wc,
  "title": "코스피 장중 '5,000' 회복\n6%대 급등", "cap": str(O / "cap_kospi.png"),
  "caption": "매일신문 기사 캡처", "label": "전날 '매도' 사이드카 → 오늘 '매수' 사이드카",
  "lines": ["삼성전자 9%대 · SK하이닉스 8%대 급등(서울신문)", "※ 장 초반 기준"], "cap_max_h": 400},
 {"out": str(O / "c_sk.jpg"), "sub": "진짜 귀재는 따로 있었다?", "box_bg": Wc,
  "title": "SK하이닉스 전략 담당 사장\n급락한 날 자사주 '16억' 매수", "cap": str(O / "cap_sk.png"),
  "caption": "서울신문 기사 캡처", "label": "주당 107만 7,263원에 1,500주",
  "lines": ["코스피가 3% 넘게 빠진 23일 장중 매수", "다음 날 하이닉스는 장 초반 8%대 급등"], "cap_max_h": 400},
]
json.dump(spec, open(O / "caps.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "caps.json")], check=True, cwd=R)

# 각 장 오른쪽 위에 인물 얼굴(사용자 제공 프로필 사진) 둥글게
U = Path("/mnt/user-data/uploads")
faces = {"c_ark.jpg": (U / "691ca6c2-image.webp", (350, 90, 650, 390)),
         "c_cramer.jpg": (U / "0b0b3624-image.jpg", (110, 0, 300, 190)),
         "c_jig.jpg": (U / "d1f00a46-image.jpg", (110, 40, 350, 280))}
for card_name, (src, box) in faces.items():
    cd = Image.open(O / card_name).convert("RGB"); S = 210
    f = Image.open(src).convert("RGB").crop(box).resize((S, S), Image.LANCZOS)
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse((0, 0, S - 1, S - 1), fill=255)
    ring = Image.new("RGBA", (S + 12, S + 12), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, S + 11, S + 11), fill=(255, 214, 0, 255))
    x, y = 1080 - S - 60, 40
    cd.paste(ring, (x - 6, y - 6), ring); cd.paste(f, (x, y), m); cd.save(O / card_name, quality=95)

cap = """(표지는 이해를 돕기 위한 AI 생성 이미지)
[젠슨 황이 돌아오기 직전, 시장 '고수'들은 어떤 선택을 했을까요]

엔비디아 이사회가 23일(현지시간) 젠슨 황을 CEO로 복귀시키자 엔비디아는 하루 31% 넘게 올랐고, 24일 코스피도 장중 6%대 뛰며 5,000선을 되찾았습니다. 공교롭게도 바로 직전, 유명 투자자들의 판단은 정반대였습니다.

'돈나무 언니' 캐시 우드의 아크인베스트는 지난주 엔비디아를 1억 700만 달러어치 넘게 팔았습니다. 그 전주에 약 1,600만 달러어치를 샀다가 방향을 뒤집은 것입니다(구루포커스).

'인버스 크레이머'로 유명한 CNBC 진행자 짐 크레이머는 금요일 엔비디아에 대해 약세로 돌아섰다는 보도가 나온 뒤, 월요일 주가가 폭등하면서 "인버스 크레이머는 자연법칙"이라는 밈이 쏟아졌습니다(미디에이트). 그는 사임 직후엔 차익 실현을 권했고, 복귀 날엔 "엄청난 일"이라며 반겼습니다(CNBC).

국내에선 전인구경제연구소의 '검은 월요일이 온다, AI버블이 터지고 있는 이유' 영상이 60만 회 넘게 조회됐습니다. 23일 코스피는 실제로 3.31% 내려 매도 사이드카까지 발동됐지만, 그날 밤 젠슨 황 복귀로 엔비디아가 31% 급등했고 다음 날 코스피는 장중 6%대 뛰며 5,000선을 되찾았습니다.

반면 윤풍영 SK하이닉스 사장은 코스피가 급락한 23일 자사주 1,500주(약 16억 원)를 장내 매수했고, 다음 날 SK하이닉스는 장 초반 8%대 급등했습니다(서울신문).

시장을 맞히는 건 고수에게도 어렵다는 걸 보여준 하루였습니다. 여러분은 이번에 어떤 선택을 하셨나요?

※ 투자 권유 아님, 정보 제공 목적. 주가·지수는 기사 작성 시점(장 초반) 기준입니다.
생각나는 친구에게 보내주세요!"""
d = [{
 "id": "20261124-inverse", "slot": "dinner", "mode": "render",
 "topic": "젠슨 황 복귀 직전 투자 귀재들: 캐시 우드 1억 달러 매도, 짐 크레이머 약세 전환, 전인구 '검은 월요일', 반대로 하이닉스 사장 자사주 16억 매수",
 "category": "경제",
 "images": ["cover_ai.jpg", "c_ark.jpg", "c_cramer.jpg", "c_jig.jpg", "c_kospi.jpg", "c_sk.jpg"],
 "slides": [
  {"lay": "one", "t": "젠슨 황 복귀 직전\n'투자 귀재'들의 선택"},
  {"raw": True}, {"raw": True}, {"raw": True}, {"raw": True}, {"raw": True}
 ],
 "caption": cap,
 "hashtags": ["젠슨황", "엔비디아", "캐시우드", "짐크레이머", "코스피"],
 "sources": [
  {"publisher": "야후파이낸스(구루포커스)", "date": "2026.11.23"},
  {"publisher": "미디에이트·CNBC", "date": "2026.11.23"},
  {"publisher": "전인구경제연구소 유튜브", "date": "2026.11.22"},
  {"publisher": "매일신문·서울신문", "date": "2026.11.24"}
 ],
 "photo_credits": ["야후파이낸스·미디에이트·매일신문·서울신문 화면, 전인구경제연구소 유튜브 화면"]
}]
json.dump(d, open(D / "draft.json", "w"), ensure_ascii=False, indent=1)
