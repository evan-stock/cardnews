"""20261116-leettutor: 리트 만점자 '생2 과외 선생' 등장 (고파스·에타 캡처, 엑스 @itwillbe_sage). 표지 lay one + 캡처 카드 2장."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
S = R / "media/20261116-sage/video"; A = R / "media/20261116-argent/video"; W, H = 1080, 1350
K = R / "media/20261116-sage3/video"
k1 = Image.open(K / "p1_1.jpg").convert("RGB"); k2 = Image.open(K / "p1_2.jpg").convert("RGB")
req = Image.open(A / "p1_1.jpg").convert("RGB"); tes = Image.open(A / "p1_2.jpg").convert("RGB")
gopas = Image.open(S / "p1_1.jpg").convert("RGB"); eta = Image.open(S / "p1_2.jpg").convert("RGB")


def vstack(parts, w=850, gap=0, bg=(18, 18, 18)):
    parts = [p.resize((w, round(p.height * w / p.width)), Image.LANCZOS) for p in parts]
    out = Image.new("RGB", (w, sum(p.height for p in parts) + gap * (len(parts) - 1)), bg); y = 0
    for p in parts: out.paste(p, (0, y)); y += p.height + gap
    return out


vstack([gopas.crop((0, 190, 850, 1110)), gopas.crop((0, 1345, 850, 1490))], bg=(255, 255, 255)).crop((20, 0, 830, 1065)).save(O / "cap_gopas.png")
req.crop((0, 190, 850, 845)).save(O / "cap_req.png")
tes.save(O / "cap_tes.png")
vstack([k1.crop((0, 640, 850, 1295))], bg=(155, 160, 170)).save(O / "cap_kakao.png")
cap_eta = vstack([eta.crop((0, 0, 850, 490)), eta.crop((0, 800, 850, 1015))]); cap_eta.save(O / "cap_eta.png")

specs = [
 {"out": str(O / "c02.jpg"), "sub": "고파스 익명 글 · 2025년 11월 10일 14:22 (수능 사흘 전)",
  "title": "\"생2 기본적인 거\n'1시간' 과외해 주실 분\"", "cap": str(O / "cap_req.png"), "cap_max_h": 600, "box_bg": [255, 255, 255],
  "caption": "고파스 게시글 캡처 (본인 글로 지목된 구인글)", "label": "과외를 구한 이유",
  "lines": ["\"과학 칼럼 쓰는데 생투만 '지식이 없어서'\"", "\"중지로 와 주실 수 있는 분만 3만 원 드릴게요\""]},
 {"out": str(O / "c03.jpg"), "sub": "구인글에 연락했던 사람이 공개한 카톡 · 2025년 11월 10일 14:32",
  "title": "샤가프 문제 그림을\n'텍스트로' 설명하는 법", "cap": str(O / "cap_kakao.png"), "cap_max_h": 640,
  "caption": "오픈채팅 대화 캡처 (11월 16일 공개)", "label": "\"그림설명을 텍스트로 어떻게 풀어서 설명할지\"",
  "lines": ["수능 사흘 전에 왜 필요했을까", "커뮤니티 'AI에 넣으려던 것' 추측 · 확인 안 됨"]},
 {"out": str(O / "c04.jpg"), "sub": "고파스 익명 글 · 2026년 11월 16일 12:08",
  "title": "과외했다는 생명과학 전공자\n\"'기본 지식'이 거의 없었다\"", "cap": str(O / "cap_tes.png"), "cap_max_h": 560,
  "caption": "고파스 게시글 캡처 (과외를 했다는 사람의 글)", "label": "\"DNA 구조·염기서열도 아예 몰랐다\"",
  "lines": ["개념서 대신 '수능 기출문제집'을 들고 와", "\"의아했다\"는 증언"]},
 {"out": str(O / "c05.jpg"), "sub": "고파스 구인글 댓글 · 2025년 11월 10일 14:55",
  "title": "과외 받은 쪽이 남긴 말\n\"선 3개가 '수소결합'이었구나\"", "cap": str(O / "cap_gopas.png"), "cap_max_h": 600, "box_bg": [255, 255, 255],
  "caption": "고파스 게시글 캡처 (첨부: 당시 댓글 · 3만 원 입금 내역)", "label": "그해 생2 '50점 만점'",
  "lines": ["본인 설명은 \"해설지 외워 '운 좋게' 50점\"", "19일 생중계는 '국어' 한 과목만"]},
]
sp = Path("/tmp/leettutor_specs.json"); sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)

# 표지 배경: 회색 그라데이션 + 왼쪽 인물 누끼 + 오른쪽 캡처 2장
bg = Image.new("RGB", (W, H)); g = ImageDraw.Draw(bg)
for y in range(H): g.line((0, y, W, y), fill=(int(228 - 40 * y / H),) * 3)
cov = bg.convert("RGBA")


def place(base, t, cx, cy, ang, wdt):
    t = t.resize((wdt, round(t.height * wdt / t.width)), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", t.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, t.width - 1, t.height - 1), 18, fill=255); t.putalpha(m)
    sh = Image.new("RGBA", (t.width + 60, t.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 36, t.width + 30, t.height + 36), 18, fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(14)); sh.alpha_composite(t, (30, 30)); sh = sh.rotate(ang, Image.BICUBIC, expand=True)
    base.alpha_composite(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2)))


person = Image.open(O / "person_new.png").convert("RGBA")  # 사용자 제공 사진(흰 배경 누끼)
# 눈 모자이크(2026.11.16 사용자 지시)
_b = (200, 100, 315, 150); _r = person.crop(_b); _r = _r.resize((max(1, _r.width // 9), max(1, _r.height // 9)), Image.NEAREST).resize(_r.size, Image.NEAREST); person.paste(_r, _b[:2])
ph = 1260; person = person.resize((round(person.width * ph / person.height), ph), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
cov.alpha_composite(person, (100, 150))
place(cov, req.crop((0, 190, 850, 845)), 900, 300, -3, 340)
place(cov, tes, 905, 640, 3, 340)
cov.convert("RGB").save(O / "cover_bg.jpg", quality=95)
print("ok")
