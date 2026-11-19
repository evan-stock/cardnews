"""20261119-leetmeme: 리트 만점자 사망 후 '이런 결말을 바란 건 아니야'(@history.me_me) 공감 글 + 우리 성찰.
자살보도 권고기준: 장소·방법 안 씀, 109 안내. 밈·조롱 없음, 고인 미화도 없음.
표지(lay one)·마지막 장은 manual 렌더, 2장 캡처 카드(post_cap_card), 3·4장 검은 바탕 틀(frame, leetfound 코드 복사)."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)


def rich_center(d, y, text, font, base):
    parts = re.split(r"('[^']*')", text); tw = sum(d.textlength(p.strip("'"), font=font) for p in parts if p)
    x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=font)


def rich(d, x, y, text, font, base=FG):
    for p in re.split(r"('[^']*')", text):
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base); x += d.textlength(p, font=font)


def logo(im):
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
    lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)


def frame(top, photo, bottom, sub=None):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    p = photo
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300), m)
    d = ImageDraw.Draw(im); y = 300 + p.height + 92
    rich_center(d, y, bottom, F("Black", 46), YE)
    if sub: rich_center(d, y + 62, sub, F("Medium", 32), (190, 190, 198))
    logo(im); return im


def panel(rows, h=640, gap=None):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = gap or (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198)); rich(d, 56, y + 42, v, F("Black", 42))
    return p


# 캡처 카드: 대학 에브리타임 익명 글(원글 캡처 그대로)
W_=dict(box_bg=[255, 255, 255])
specs = [
 {"out": str(O / "c02.jpg"), "sub": "건국대 에브리타임 익명 글 (11/19 15:36)", "title": "\"애초에 불쌍해서 '먹먹한 게 아님'\"",
  "cap": str(O / "kk1.jpg"), "cap_max_h": 740, **W_, "caption": "건국대 에브리타임 익명 게시글 캡처 (1/3)",
  "label": "부정행위도, 거짓말도 그가 한 일", "lines": ["그런데 사람들이 기대한 결말은 '이게 아니었다'"]},
 {"out": str(O / "c03.jpg"), "sub": "건국대 에브리타임 익명 글 (이어서)", "title": "\"이런 건 '아니었음'\"",
  "cap": str(O / "kk2.jpg"), "cap_max_h": 740, **W_, "caption": "건국대 에브리타임 익명 게시글 캡처 (2/3)",
  "label": "만점자 등장 → 의혹 → 변명 → 노쇼", "lines": ["그 모든 일의 마지막이 '찢어진 수험표 한 장'"]},
 {"out": str(O / "c04.jpg"), "sub": "건국대 에브리타임 익명 글 (이어서)", "title": "\"온갖 '밈이랑 드립의 소스'였음\"",
  "cap": str(O / "kk3.jpg"), "cap_max_h": 740, **W_, "caption": "건국대 에브리타임 익명 게시글 캡처 (3/3)",
  "label": "웃고 즐겼던 일주일", "lines": ["끝은 너무 '현실적'이었다"]},
 {"out": str(O / "c05.jpg"), "sub": "서강대 에브리타임 익명 글 (11/19 19:50)", "title": "\"며칠 전까지 '보이던 사람'이\"",
  "cap": str(O / "sg.jpg"), "cap_max_h": 760, **W_, "caption": "서강대 에브리타임 익명 게시글 캡처",
  "label": "같은 시간을 살았던 사람", "lines": ["몇 시간 전에 죽었다는 게 '거짓말 같다'"]},
 {"out": str(O / "c06.jpg"), "sub": "성균관대 에브리타임 익명 글 (11/19 19:37)", "title": "\"18수능 27수능 '수미상관'\"",
  "cap": str(O / "skku.jpg"), "cap_max_h": 740, **W_, "caption": "성균관대 에브리타임 익명 게시글 캡처",
  "label": "그가 끝까지 들고 다닌 건", "lines": ["혼자 힘으로 받은 '18수능 수험표'"]},
]
sp = O / "specs.json"; sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)

# 3장: 비어 있던 공개 검증 자리
emp = Image.open(O / "empty.jpg").convert("RGB").crop((620, 240, 1452, 860))
emp = ImageOps.fit(emp, (940, 700), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 50, 2))
frame(("리트 만점 → 부정행위 의혹 → 생중계 검증", "일주일 내내 '구경거리'였다"), emp,
      "오늘 아침, 이 자리는 '비어' 있었습니다", "IDA입시연구소 공개 검증 생중계 화면(11.19)").save(O / "c07.jpg", quality=93)

# 마지막 장: 우리 입장
frame(("감싸자는 게 아닙니다", "의혹은 '의혹대로' 가려져야 했습니다"),
      panel([("그런데 우리는", "그를 사람보다 '밈'으로 봤습니다"), ("오늘의쓸모도", "그 흐름 '안'에 있었습니다"),
             ("남는 질문", "의혹을 다루는 '선'은 어디였을까")], h=560),
      "고인의 명복을 빕니다", "자살예방 상담전화 109 · SNS상담 마들랜(24시간)").save(O / "c08.jpg", quality=93)
print("ok")
