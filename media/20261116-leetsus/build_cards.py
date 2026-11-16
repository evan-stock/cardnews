"""20261116-leetsus: 리트 만점자 의혹 6가지 (엑스 글 6개 첨부 캡처). 표지·CTA lay one, 2장 영상 frame, 3~8장 캡처 카드."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
S = R / "media/20261116-leetimg/video"; V = R / "media/20261116-leetx/video/v1.mp4"
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
img = lambda n: Image.open(S / f"img{n}.jpg").convert("RGB")


def blur(im, box, k=18):
    r = im.crop(box).filter(ImageFilter.GaussianBlur(k)); im.paste(r, box[:2]); return im


def vstack(parts, w=1080, gap=14, bg=(255, 255, 255)):
    parts = [p.resize((w, round(p.height * w / p.width)), Image.LANCZOS) for p in parts]
    out = Image.new("RGB", (w, sum(p.height for p in parts) + gap * (len(parts) - 1)), bg); y = 0
    for p in parts: out.paste(p, (0, y)); y += p.height + gap
    return out


def hstack(parts, h=900, gap=16, bg=(40, 40, 46)):
    parts = [p.resize((round(p.width * h / p.height), h), Image.LANCZOS) for p in parts]
    out = Image.new("RGB", (sum(p.width for p in parts) + gap * (len(parts) - 1), h), bg); x = 0
    for p in parts: out.paste(p, (x, 0)); x += p.width + gap
    return out


# ---- 캡처 조각 ----
i1, i2 = img(1), img(2)
vstack([i2.crop((0, 170, 823, 650)), i1.crop((0, 0, 665, 92)), i1.crop((0, 1180, 665, 1265))], bg=(20, 20, 24)).save(O / "cap3.png")
vstack([img(3).crop((0, 300, 1320, 960)), img(5).crop((0, 409, 1298, 625))], bg=(20, 20, 24)).save(O / "cap4.png")
img(19).crop((0, 0, 850, 820)).save(O / "cap5.png")
i20, i21 = img(20), img(21)
i20.save(O / "cap6.png"); i21.crop((0, 120, 1206, 1812)).save(O / "cap6b.png")
i12 = img(12)
vstack([i12.crop((0, 218, 1080, 560)), i12.crop((0, 1060, 1080, 1250)), img(13).crop((0, 1930, 1080, 2140))], bg=(230, 230, 230)).save(O / "cap7.png")
i16 = img(16)
vstack([i16.crop((0, 60, 1080, 150)), i16.crop((0, 975, 1080, 1054)), img(17).crop((0, 0, 1074, 830))], bg=(230, 230, 230)).save(O / "cap8.png")

specs = [
 {"out": str(O / "c03.jpg"), "sub": "에브리타임 고시게시판 · 본인 디시 글 (11월 16일 00:43)",
  "title": "25~29번 '다섯 문제'를\n연달아 고쳤다", "cap": str(O / "cap3.png"), "cap_max_h": 530,
  "caption": "에브리타임 게시글 · 디시인사이드 본인 게시글 캡처", "label": "본인 해명",
  "lines": ["\"후반으로 갈수록 집중력이 떨어져 잔실수가 늘었다\"", "\"3개가 연달아 지운 답이 실제 답과 일치하는 것이", "'확률적으로 희박'하다는 점도 인정합니다\""]},
 {"out": str(O / "c04.jpg"), "sub": "더쿠 글 (조회 7.2만) · 본인 디시 답글 (11월 16일)",
  "title": "1번 밑에 적힌 '33'\n4·5번 정답은 3·3", "cap": str(O / "cap4.png"), "cap_max_h": 600,
  "caption": "더쿠 게시글 · 디시인사이드 댓글 캡처", "label": "\"33은 뭔가요?\" 질문에 본인 답",
  "lines": ["\"아마 며칠 후에 집에서 통화하면서 '끄적인' 거 같아요\""]},
 {"out": str(O / "c05.jpg"), "sub": "고파스 익명 글 · 2025년 11월 10일 (수능 사흘 전)",
  "title": "수능 사흘 전\n\"생2 1시간 '과외'해 주실 분\"", "cap": str(O / "cap5.png"), "cap_max_h": 600,
  "caption": "고려대 커뮤니티 고파스 익명 게시글 캡처", "label": "온라인에서 나온 주장",
  "lines": ["이 글이 본인이라면, 생명과학Ⅱ 만점도 의심받습니다", "본인 디시 글: 해설지 보며 외웠고 \"운 좋게 50 받은 겁니다\""]},
 {"out": str(O / "c06.jpg"), "sub": "서울대 에브리타임 자유게시판 · 11월 15일 23:25",
  "title": "서울대생이 던진 질문 '11개'\n1번부터 6번", "cap": str(O / "cap6.png"), "cap_max_h": 760, "box_bg": [255, 255, 255],
  "caption": "에브리타임 게시글 캡처 (1/2)", "label": "", "lines": []},
 {"out": str(O / "c06b.jpg"), "sub": "서울대 에브리타임 자유게시판 · 11월 15일 23:25",
  "title": "7번부터 11번\n\"이걸 '믿으라는' 거냐\"", "cap": str(O / "cap6b.png"), "cap_max_h": 760, "box_bg": [255, 255, 255],
  "caption": "에브리타임 게시글 캡처 (2/2, 공감 66 · 댓글 50)", "label": "", "lines": []},
 {"out": str(O / "c07.jpg"), "sub": "온라인 커뮤니티 · 11월 16일",
  "title": "성적 발표 8월 18일\n책 출간은 '2주 뒤'", "cap": str(O / "cap7.png"), "cap_max_h": 600,
  "caption": "온라인 커뮤니티 게시글 캡처 (책 정보·사업자 정보 화면)", "label": "출판사 대표도 본인",
  "lines": ["시험 7월 19일 → 발표 8월 18일 → 홍보 22일 → 출간 9월 2일", "출판사 '바른뇌연구소' 대표 이진우, 업력 '3개월'"]},
 {"out": str(O / "c08.jpg"), "sub": "본인 디시 글 (11월 12일) · 갤로그 화면 (11월 16일)",
  "title": "\"16일까지 확정\" 약속한 날\n갤로그는 '0'", "cap": str(O / "cap8.png"), "cap_max_h": 600,
  "caption": "디시인사이드 게시글 · 갤로그 화면 캡처", "label": "오늘 오후 2시 '주관사 공지' 예고",
  "lines": ["게시물·댓글은 모두 '비공개'로 바뀌었습니다", "19일 생중계는 그대로 할까요"]},
]
sp = Path("/tmp/leetsus_specs.json"); sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)
print("ok")

# ---------- 표지 배경: 회색 바탕 + 왼쪽 누끼 + 오른쪽 위 캡처 2장 ----------
bg = Image.new("RGB", (W, H), (214, 216, 220)); g = ImageDraw.Draw(bg)
for y in range(H): g.line((0, y, W, y), fill=(int(228 - 40 * y / H),) * 3)
cov = bg.convert("RGBA")


def place(base, t, cx, cy, ang, wdt):
    t = t.resize((wdt, round(t.height * wdt / t.width)), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", t.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, t.width - 1, t.height - 1), 18, fill=255); t.putalpha(m)
    sh = Image.new("RGBA", (t.width + 60, t.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 36, t.width + 30, t.height + 36), 18, fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(14)); sh.alpha_composite(t, (30, 30)); sh = sh.rotate(ang, Image.BICUBIC, expand=True)
    base.alpha_composite(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2)))


place(cov, Image.open(O / "cap6.png"), 790, 330, -3, 520)
place(cov, img(2).crop((0, 170, 823, 650)), 800, 700, 3, 470)
person = Image.open(R / "media/20261115-nowyeosi/cand/person_cut2.png").convert("RGBA")
ph = 1180; person = person.resize((round(person.width * ph / person.height), ph), Image.LANCZOS)
cov.alpha_composite(person, (-170, H - ph))
cov.convert("RGB").save(O / "cover_bg.jpg", quality=95)

# ---------- 2장: 인터뷰 영상 (검은 바탕 틀 + 영상 구멍) ----------
def rich_center(d, y, text, font, base):
    parts = re.split(r"('[^']*')", text); tw = sum(d.textlength(p.strip("'"), font=font) for p in parts if p); x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'"); d.text((x, y), p, font=font, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=font)


PW, PH, PY = 940, 531, 330
im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
rich_center(d, 190, "\"위기는 딱 한 문제였다\"", F("Medium", 46), FG)
rich_center(d, 262, "\"답 바꾼 건 '23번 하나'\"", F("Black", 58), FG)
y = PY + PH + 100
rich_center(d, y, "그런데 시험지엔 '다른 번호'들이 고쳐져 있었다", F("Black", 44), YE)
rich_center(d, y + 60, "유튜브 인터뷰 · 엑스 @eom0x 정리 (조회 10만)", F("Medium", 30), (190, 190, 198))
lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)
card = im.convert("RGBA"); m = Image.new("L", (PW, PH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, PW - 1, PH - 1), 18, fill=255)
hole = Image.new("L", (W, H), 255); hole.paste(Image.eval(m, lambda v: 255 - v), (70, PY)); card.putalpha(hole)
card.save("/tmp/leetsus_v2.png")
fr = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "9", "-i", str(V), "-frames:v", "1", "-vf", f"scale={PW}:{PH}", "/tmp/v2frame.png"])
still = Image.new("RGB", (W, H)); still.paste(Image.open("/tmp/v2frame.png"), (70, PY)); still.paste(card, (0, 0), card); still.save(O / "c02_still.jpg", quality=95)
(D / "video").mkdir(exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(V), "-i", "/tmp/leetsus_v2.png", "-filter_complex",
  f"color=c=0x0a0a0c:s=1080x1350:r=30[bg];[0:v]scale={PW}:{PH}:flags=lanczos[v];[bg][v]overlay=70:{PY}:shortest=1[t];[t][1:v]overlay=0:0,format=yuv420p[o]",
  "-map", "[o]", "-map", "0:a", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
  str(D / "video/card2.mp4")], check=True)
print("ok2")
