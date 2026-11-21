"""20261121-mdeet: 미트(MDEET) 수석 AI 부정 의혹 해명과 남은 불신. 실명 안 씀, 얼굴 모자이크 보도 화면만. 2012 익명글 연결 등 확인 안 된 신상은 쓰지 않음. 근거: 헤럴드경제·이투데이·서울신문·위키트리·아이뉴스24(11.20~21), X·스레드 반응."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; 
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


fit = lambda img, w, h, c=(.5, .5): ImageOps.fit(img, (w, h), Image.LANCZOS, centering=c)
op = lambda p: Image.open(p).convert("RGB")


def panel(rows, h=640, gap=None):
    p = Image.new("RGB", (940, h), (24, 24, 28)); d = ImageDraw.Draw(p); gap = gap or (h - 60) // len(rows)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * gap; d.text((56, y), k, font=F("Medium", 32), fill=(190, 190, 198)); rich(d, 56, y + 42, v, F("Black", 42))
    return p




# 표지: 메가엠디 유튜브 인터뷰 화면(언론 보도 모자이크본)
fit(op(O / "press01.jpg"), W, H, (.5, .3)).save(O / "cover_bg.jpg", quality=95)

# 입장문 캡처(이름·생년 줄 제외)
op(O / "press10.jpg").crop((40, 190, 1160, 690)).save(O / "statement.jpg", quality=95)
op(R / "media/20261121-mdeet/video/p3_1.jpg").crop((0, 30, 1116, 540)).save(O / "threads.jpg", quality=95)

spec = [
    {"out": str(O / "c02.jpg"), "sub": "11월 20일 · 수험생 카페에 올린 입장문", "title": "\"AI 부정행위 루머\n'사실 아니다'\"",
     "cap": str(O / "statement.jpg"), "caption": "미트 수석 합격자 입장문 일부(위키트리 보도 갈무리)",
     "label": "\"근거 없는 비방엔 '법적 대응'\"",
     "lines": ["세무냥이·리트냥이 이후 '미트냥이'로 불려", "결국 6년치 성적표·시험지를 직접 공개"]},
    {"out": str(O / "c04.jpg"), "sub": "그래도 남은 의심", "title": "\"텝스가 이렇게\n'오르는' 시험이 아니에요\"",
     "cap": str(O / "threads.jpg"), "caption": "스레드 댓글 갈무리",
     "label": "\"자연과학 말고 '수학' 시험지만?\"",
     "lines": ["과학 과목 풀이는 왜 안 냈냐는 의심도", "성적표가 '시험장 결백'까지 증명하진 못한다는 지적"]},
]
json.dump(spec, open(O / "cap_spec.json", "w"), ensure_ascii=False)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "cap_spec.json")], check=True)

# 3장 해명 내용
frame(("본인이 밝힌 '6년'", "\"1년 준비\"는 오해였다"),
      panel([("준비 기간", "MDEET·텝스 합쳐 '6년'"),
             ("2021·2022", "130.5점·124.4점, '텝스'에 막혀 탈락"),
             ("텝스", "410점 → '496점'까지 올려"),
             ("공개 자료", "성적표·시험지·대학 '성적표'까지")], h=640),
      "지방대 자퇴·학점은행제 '비전공자'", "\"출신 학교 때문에 의심받았다\"는 입장").save(O / "c03.jpg", quality=93)

# 5장 냥이 낙인
frame(("세무냥이·리트냥이·미트냥이", "'냥이'가 남긴 것"),
      panel([("세무냥이", "AI 커닝 '자백' · 실제 부정"),
             ("리트냥이", "의혹 속 공개 검증 불참, '사망'"),
             ("미트냥이", "해명에도 '검증하자' 여론"),
             ("X 반응", "\"냥이가 하도 나와서 '믿음'이 사라졌다\"")], h=640),
      "고득점자는 '스스로 증명'해야 하나", "의사단체 \"특정인 아닌 시험 공정성 문제\"").save(O / "c05.jpg", quality=93)
print("ok")
