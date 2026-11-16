"""20261116-leetall: 리트 만점자 '수능 전과목 풀겠다' 단독 기사 캡처. 표지 lay one + 기사 캡처 카드 + 조건 변화 + CTA."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; W, H = 1080, 1350
src = Image.open(O / "src_shot.png").convert("RGB")
head = src.crop((20, 712, 1186, 1075)); photo = src.crop((0, 1330, 1206, 2135))
def vstack(parts, w=1166, bg=(255, 255, 255)):
    parts = [p.resize((w, round(p.height * w / p.width)), Image.LANCZOS) for p in parts]
    out = Image.new("RGB", (w, sum(p.height for p in parts)), bg); y = 0
    for p in parts: out.paste(p, (0, y)); y += p.height
    return out
cap = vstack([head, photo]); cap.save(O / "cap_news.png")
specs = [{"out": str(O / "c02.jpg"), "sub": "중앙일보 단독 · 11월 16일 (이규림 기자)",
  "title": "\"수능 '전과목' 풀겠다\"\n생중계로 입증 예고", "cap": str(O / "cap_news.png"), "cap_max_h": 600, "box_bg": [255, 255, 255],
  "caption": "중앙일보 기사 화면 캡처", "label": "부정행위 여부엔 답 대신",
  "lines": ["\"사실이라면 실시간 문제 풀이를 '왜' 하겠느냐\"", "\"목요일(수능 당일)까지 기다려달라\""]}]
sp = Path("/tmp/leetall_specs.json"); sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)
# 표지 배경
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
place(cov, vstack([head]), 760, 250, -2, 600)
place(cov, photo.crop((150, 0, 1056, 805)), 820, 640, 3, 420)
person = Image.open(R / "media/20261115-nowyeosi/cand/person_cut2.png").convert("RGBA")
ph = 1180; person = person.resize((round(person.width * ph / person.height), ph), Image.LANCZOS)
cov.alpha_composite(person, (-170, H - ph))
cov.convert("RGB").save(O / "cover_bg.jpg", quality=95)
print("ok")
