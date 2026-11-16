"""20261117-stalk: 리트 만점자 스토킹 폭로(다음카페 글, 엑스 @eom0x·@nowyeosi 첨부). 표지·CTA lay one, 2~5장 캡처 카드."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; S = D / "video"
W, H = 1080, 1350
img = lambda n: Image.open(S / f"{n}.jpg").convert("RGB")


def vstack(parts, w=1080, gap=14, bg=(255, 255, 255)):
    parts = [p.resize((w, round(p.height * w / p.width)), Image.LANCZOS) for p in parts]
    out = Image.new("RGB", (w, sum(p.height for p in parts) + gap * (len(parts) - 1)), bg); y = 0
    for p in parts: out.paste(p, (0, y)); y += p.height + gap
    return out


title = img("p2_2").crop((0, 0, 1076, 185))
vstack([title, img("p2_1").crop((0, 150, 1080, 1300))], bg=(230, 230, 230)).save(O / "cap2.png")
img("p2_9").save(O / "cap3.png")
vstack([img("p2_4").crop((0, 0, 1079, 365)), img("p2_7").crop((0, 2370, 1079, 2932))], bg=(230, 230, 230)).save(O / "cap4.png")
vstack([img("p2_10").crop((0, 60, 1079, 820)), img("p2_13")], bg=(230, 230, 230)).save(O / "cap5.png")

specs = [
 {"out": str(O / "c02.jpg"), "sub": "다음카페 게시글 · 11월 17일 새벽 (댓글 601)",
  "title": "\"리트 만점 이진우(이희찬)에게\n'스토킹'을 당했습니다\"", "cap": str(O / "cap2.png"), "cap_max_h": 600,
  "caption": "다음카페 게시글 캡처 (엑스 @nowyeosi·@eom0x 공유)", "label": "폭로자 주장",
  "lines": ["과외 공고를 보고 '여학생 척' 가명으로 접근", "번호를 받자마자 전화·메신저로 '욕설'을 쏟아냈다"]},
 {"out": str(O / "c03.jpg"), "sub": "폭로자가 공개한 메신저 캡처 · 가명 '이예원'",
  "title": "\"손가락 인증 못하죠?\"\n\"'문서확인번호'도 못해\"", "cap": str(O / "cap3.png"), "cap_max_h": 620,
  "caption": "폭로 글 첨부 캡처 (원본 가림 처리 그대로)", "label": "지금 그가 받는 의혹",
  "lines": ["성적 '인증'·시험지 조작·개명", "폭로가 사실이라면, 그 말이 그대로 돌아온 셈입니다"]},
 {"out": str(O / "c04.jpg"), "sub": "폭로 글 첨부 · 2025년 1~3월 경찰 문자",
  "title": "로펌 700만 원, 경찰 신고\n끝내 '수사 종결'", "cap": str(O / "cap4.png"), "cap_max_h": 600,
  "caption": "폭로 글 본문 · 경찰 문자 캡처", "label": "폭로자 주장",
  "lines": ["\"고통을 주는 게 의미가 있나 싶어서\" 직접 종결", "\"범법행위로 처벌이 불가능하다는 현실에 무력감\""]},
 {"out": str(O / "c05.jpg"), "sub": "폭로자 추가 글 · 댓글",
  "title": "\"이희찬 씨와 저는\n'일면식도' 없는 사이\"", "cap": str(O / "cap5.png"), "cap_max_h": 620,
  "caption": "다음카페 게시글·작성자 댓글 캡처", "label": "폭로자가 지목한 이름 '이희찬'",
  "lines": ["온라인에선 이진우 씨의 '개명 전 이름'이라는 주장이 돌고 있습니다", "폭로자는 편집 없는 통화 녹음도 올렸다고 밝혔습니다"]},
]
sp = Path("/tmp/stalk_specs.json"); sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)

def place(base, t, cx, cy, ang, wdt):
    t = t.resize((wdt, round(t.height * wdt / t.width)), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", t.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, t.width - 1, t.height - 1), 18, fill=255); t.putalpha(m)
    sh = Image.new("RGBA", (t.width + 60, t.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 36, t.width + 30, t.height + 36), 18, fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(14)); sh.alpha_composite(t, (30, 30)); sh = sh.rotate(ang, Image.BICUBIC, expand=True)
    base.alpha_composite(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2)))


# 표지: 사용자 제공 프로필 사진(cand/cover_src.webp) + 눈 모자이크
im = Image.open(O / "cover_src.webp").convert("RGB"); k = W / im.width
im = im.resize((W, round(im.height * k)), Image.LANCZOS)
x0, y0, x1, y1 = [round(v * k) for v in (385, 190, 565, 245)]
r = im.crop((x0, y0, x1, y1)); r = r.resize(((x1 - x0) // 14, (y1 - y0) // 14), Image.BILINEAR).resize((x1 - x0, y1 - y0), Image.NEAREST); im.paste(r, (x0, y0))
sx = -230  # 인물을 왼쪽으로, 오른쪽에 캡처 자리
c = im.crop((W - 2, 0, W - 1, im.height)).resize((W, im.height)).copy()
c.paste(im.crop((-sx, 0, W, im.height)), (0, 0))
full = Image.new("RGB", (W, H)); full.paste(c, (0, 0))
full.paste(c.crop((0, c.height - 2, W, c.height - 1)).resize((W, H - c.height)), (0, c.height))
cov = full.convert("RGBA")
place(cov, img("p2_9").crop((0, 0, 1080, 1000)), 830, 520, 3, 400)
place(cov, title, 790, 170, -2, 500)
c = cov.convert("RGB")
c.save(O / "cover_bg.jpg", quality=95)
print("ok")
