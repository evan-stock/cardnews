"""20261115-aicase: 세무냥이 자수 뒤 쏟아진 'AI 부정' 고백 모음 + 정부 전수조사.
표지 배경(캡처 콜라주) · 2~5장 캡처 카드(post_cap_card) · 6장 검은 바탕 틀(타임라인 패널)."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

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


# ---------- 표지 배경: 고개 숙인 자수 장면 위에 '고백' 글 캡처 3장 ----------
bg = ImageOps.fit(Image.open(R / "media/20261115-brk/cand/v2_bow.jpg").convert("RGB"), (W, H), Image.LANCZOS, centering=(.5, .3))
bg = ImageEnhance.Brightness(bg).enhance(0.55)


def tile(img, width, pad=22, bgc="white"):
    img = img.resize((width - 2 * pad, round(img.height * (width - 2 * pad) / img.width)), Image.LANCZOS)
    t = Image.new("RGB", (width, img.height + 2 * pad), bgc); t.paste(img, (pad, pad)); return t


def place(base, t, cx, cy, ang):
    t = t.convert("RGBA")
    m = Image.new("L", t.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, t.width - 1, t.height - 1), 20, fill=255)
    t.putalpha(m)
    sh = Image.new("RGBA", (t.width + 60, t.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 36, t.width + 30, t.height + 36), 20, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(14)); sh.alpha_composite(t, (30, 30))
    sh = sh.rotate(ang, Image.BICUBIC, expand=True)
    base.paste(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2)), sh)


eta = Image.open(O / "src_eta.jpg").convert("RGB").crop((30, 40, 771, 210))
dc = Image.open(O / "src_dc.jpg").convert("RGB").crop((28, 184, 470, 210))
dc = dc.resize((dc.width * 2, dc.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 90, 2))
tele = Image.open(O / "src_tele.png").convert("RGB").crop((70, 600, 1110, 840))
cov = bg.convert("RGBA")
place(cov, tile(tele, 800), 470, 250, 3)
place(cov, tile(dc, 860, pad=26), 560, 470, -2.5)
place(cov, tile(eta, 820), 500, 660, 2)
cov.convert("RGB").save(O / "cover.jpg", quality=95)

# ---------- 2~5장: 캡처 카드 ----------
specs = [
    {"out": str(O / "c02.jpg"), "sub": "디시 감정평가사 갤러리 · 11월 15일 익명 글",
     "title": "\"작년에 합격하고 지금 군대\"\n'AI 안경 380달러'로 붙었다는 글", "cap": str(O / "cap_dc.png"),
     "cap_max_h": 520, "box_bg": [255, 255, 255], "caption": "디시인사이드 감정평가사 갤러리 게시글 캡처",
     "label": "믿거나 말거나",
     "lines": ["'1차 65점·2차 52점'으로 붙었다는 글인데", "같은 제목 글이 '수능·순경' 갤러리에도 올라왔습니다"]},
    {"out": str(O / "c03.jpg"), "sub": "에브리타임 '5급·행시' 게시판 · 11월 15일",
     "title": "\"사실 나도 세무냥이랑\n'같은 방법' 썼다\"", "cap": str(O / "cap_eta.png"),
     "cap_max_h": 520, "box_bg": [255, 255, 255], "caption": "에브리타임 게시글 캡처 (공감 25 · 댓글 31)",
     "label": "글쓴이 주장",
     "lines": ["2024·2025년 두 번 썼고 \"25년엔 '3개' 틀렸다\"", "\"학과 공부도 이걸로 때웠다\"는 말까지"]},
    {"out": str(O / "c04.jpg"), "sub": "에브리타임 '자유게시판'·유튜브 댓글 · 11월 15일",
     "title": "'세무 AI 텔레방'\n\"2년 전부터 789명 가입\"", "cap": str(O / "cap_tele.png"),
     "cap_max_h": 520, "caption": "에브리타임 게시글 · 유튜브 댓글 캡처 (공감 935)",
     "label": "온라인에서 도는 주장",
     "lines": ["이 말이 사실이라면, 잡힌 건 '한 명'뿐입니다", "나머지는 지금 이 순간에도 합격자 명단에"]},
    {"out": str(O / "c05.jpg"), "sub": "유튜브 뉴스 댓글 · 실제 수사 결과",
     "title": "\"알려진 지 꽤 됐는데 이제서야\"\n실제로 '잡힌 것'만 이만큼", "cap": str(O / "cap_topik.png"),
     "cap_max_h": 330, "caption": "유튜브 뉴스 영상 댓글 캡처",
     "label": "기사로 확인된 적발",
     "lines": ["10월 가스기사 실기, '스마트안경' 쓴 수험자 적발", "국가기술자격 AI 기기 부정, 올해만 '6건'", "토픽은 이어폰 정답 조직 의뢰자 '101명' 입건"]},
]
sp = Path("/tmp/aicase_specs.json"); sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)

# ---------- 6장: 하루 만에 벌어진 일 (타임라인 패널, 검은 바탕 틀) ----------
pw, ph = 940, 640
panel = Image.new("RGB", (pw, ph), (24, 24, 30)); d = ImageDraw.Draw(panel)
rows = [("오전", "세무사 수석, 유튜브서 'AI 부정행위' 자백·자수"),
        ("", "서울경찰청 광역수사단 배당"),
        ("오후", "산업인력공단 사과, '업무방해 고소'"),
        ("", "합격 취소 절차·'모든 국가자격시험' 점검"),
        ("오후", "청와대 긴급회의, '국가자격시험 전체'"),
        ("", "AI 부정 의심사례 '전수조사' 결정"),
        ("16일", "총리 주재 차관회의, 추가 대책")]
y = 44
for k, (t, s) in enumerate(rows):
    if t:
        if k: d.line((40, y - 22, pw - 40, y - 22), fill=(60, 60, 70), width=2)
        d.rounded_rectangle((40, y - 2, 140, y + 44), 12, fill=YE)
        tw = d.textlength(t, font=F("Black", 28)); d.text((90 - tw / 2, y + 4), t, font=F("Black", 28), fill=(10, 10, 12))
    rich(d, 170, y, s, F("SemiBold", 36) if t else F("Medium", 34), FG if t else (200, 200, 208))
    y += 66 if t else 98
frame(("세무사 수석 자수부터", "청와대 전수조사까지 '단 하루'"), panel,
      "'과거 범죄'도 끝까지 추적하라", sub="청와대 긴급회의 지시 · 수능장 1,312곳엔 안경 전담 요원").save(O / "c06.jpg", quality=95)
print("ok")
