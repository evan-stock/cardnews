"""20261119-leetticket: 리트 만점자 18수능 수험표를 두고 대학가 에타 반응(수원대 글, 연세대 글+댓글, 고려대·성균관대·서강대·건국대 댓글).
자살보도 권고기준: 캡처 속 장소('모텔방')·'자살'·죽음 단어 흐림, 죽음을 미화하는 본문 줄 흐림. 수리남 장면·얼굴 합성 밈·송강 드립·유서 언급 글은 뺌. 109는 캡션."""
import json, subprocess, sys
from pathlib import Path
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W_ = dict(box_bg=[255, 255, 255])
specs = [
 {"out": str(O / "c02.jpg"), "sub": "디시 시대인재 N 재수종합 갤러리 (11/19 21:46)", "title": "\"뭔 '디스토피아 소설' 읽은 것 같음\"",
  "cap": str(O / "dc1.jpg"), "cap_max_h": 760, **W_, "caption": "디시인사이드 시대인재 N 재수종합 갤러리 게시글 캡처 (1/3)",
  "label": "한 사람의 지난 10년을 소설처럼", "lines": ["학벌 콤플렉스 → 개명 → '방송·작가·강사'"]},
 {"out": str(O / "c03.jpg"), "sub": "디시인사이드 게시글 (이어서)", "title": "\"판을 너무 '키워놔서'\"",
  "cap": str(O / "dc2.jpg"), "cap_max_h": 760, **W_, "caption": "디시인사이드 시대인재 N 재수종합 갤러리 게시글 캡처 (2/3)",
  "label": "세무냥이 이후 이어진 일주일", "lines": ["무를 수 없었던 '수능 증명'"]},
 {"out": str(O / "c04.jpg"), "sub": "디시인사이드 게시글 (이어서)", "title": "\"나는 '도망갈 사람'이 아니다\"",
  "cap": str(O / "dc3.jpg"), "cap_max_h": 700, **W_, "caption": "디시인사이드 시대인재 N 재수종합 갤러리 게시글 캡처 (3/3)",
  "label": "그리고 수능 당일", "lines": ["그가 들고 간 건 '2018 수능 수험표'"]},
 {"out": str(O / "c06.jpg"), "sub": "수원대 에브리타임 익명 글 (11/19 14:38)", "title": "\"동정표 그딴 거 '아니고'\"",
  "cap": str(O / "suwon.jpg"), "cap_max_h": 760, **W_, "caption": "수원대 에브리타임 익명 게시글 캡처",
  "label": "왜 하필 18수능 수험표였을까", "lines": ["\"유일하게 '진실'이었던 것이라 그런 거냐\""]},
 {"out": str(O / "c07.jpg"), "sub": "연세대 에브리타임 익명 글과 댓글 (11/19 14:23)", "title": "\"모든 게 가짜였던 자의 '유일한 진짜'\"",
  "cap": str(O / "yonsei.jpg"), "cap_max_h": 760, **W_, "caption": "연세대 에브리타임 익명 게시글 캡처 (전남대·연세대·서울대 댓글)",
  "label": "학생들이 본 그 수험표", "lines": ["\"자기 인생에 '유일한 진실'이었음\""]},
 {"out": str(O / "c08.jpg"), "sub": "같은 글 댓글 (고려대·성균관대·서강대·건국대)", "title": "\"딱 '한 장밖에' 없는 수험표\"",
  "cap": str(O / "cmts.jpg"), "cap_max_h": 780, **W_, "caption": "연세대 에브리타임 게시글 댓글 캡처",
  "label": "수학 나형, 유일하게 받은 1등급", "lines": ["\"스스로 노력해서 얻은 '유일한 자부심'\""]},
]
sp = O / "specs.json"; sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)


# 5장: 수험표의 의미(X 칩찹ChipChap 글 참고, 우리 문장으로 재구성. 사망 장소·전과 연도 안 씀)
import re
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
def rich_center(d, y, text, font, base):
    parts = re.split(r"('[^']*')", text); tw = sum(d.textlength(p.strip("'"), font=font) for p in parts if p); x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'"); d.text((x, y), p, font=font, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=font)
def rich(d, x, y, text, font, base=FG):
    for p in re.split(r"('[^']*')", text):
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'"); d.text((x, y), p, font=font, fill=YE if hl else base); x += d.textlength(p, font=font)
def logo(im):
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
    lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)
def frame(top, photo, bottom, sub=None):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    p = photo; m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300), m); d = ImageDraw.Draw(im); y = 300 + p.height + 92
    rich_center(d, y, bottom, F("Black", 46), YE)
    if sub: rich_center(d, y + 62, sub, F("Medium", 32), (190, 190, 198))
    logo(im); return im
def panel(rows, h=640, gap=None):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = gap or (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198)); rich(d, 56, y + 42, v, F("Black", 42))
    return p
# 마지막 장: X 트윗 본문 캡처 한 장(이름·아이디 모자이크, 흰 바탕으로 반전, 카드에 출처 표기 없음 — 캡션 출처에만)
spec = [
 {"out": str(O / "c09.jpg"), "sub": "온라인에 올라온 글", "title": "\"마지막까지 '의미 있었던' 건 무엇이었나\"",
  "cap": str(O / "tw_all.jpg"), "cap_max_h": 920, "box_bg": [255, 255, 255], "caption": ""},
]
(O / "spec_tw.json").write_text(json.dumps(spec, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "spec_tw.json")], check=True)
print("tw ok")
