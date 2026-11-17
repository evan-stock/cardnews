"""20261117-nyang3: '냥이' 총정리 캐러셀(감평냥이·관세냥이·경희냥이). 표지 lay one + 캡처 카드 6장 + CTA.
캡처: X @kjibak 인용(스레드·블로그), X @Insight_sua 인용(에브리타임), X @juhyeon6749(디시 캡처) → cardnews fetch-video로 받음.
일반인 닉네임·아이디·프로필은 흐리게 가림. 의혹은 모두 '온라인 주장'으로만 씀.
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; W, H = 1080, 1350
A = R / "media/20261117-nyang2/video"; K = R / "media/20261117-nyangi/video"
def blur(im, boxes):
    im = im.copy()
    for b in boxes:
        r = im.crop(b).filter(ImageFilter.GaussianBlur(9)); im.paste(r, b[:2])
    return im
def vstack(parts, w=1200, bg=(255, 255, 255), gap=0):
    parts = [p.resize((w, round(p.height * w / p.width)), Image.LANCZOS) for p in parts]
    out = Image.new("RGB", (w, sum(p.height for p in parts) + gap * (len(parts) - 1)), bg); y = 0
    for p in parts: out.paste(p, (0, y)); y += p.height + gap
    return out
op = lambda p: Image.open(p).convert("RGB")
# 감평: 블로그 카테고리(합격수기 3편) / 스레드 반응(아이디 가림)
blog = op(A / "q1_1.jpg").crop((0, 1000, 1134, 2048)); blog.save(O / "cap_blog.png")
th = blur(op(A / "q1_4.jpg"), [(10, 0, 520, 95), (10, 255, 520, 360), (10, 695, 520, 800), (1080, 20, 1200, 80), (1080, 270, 1200, 330), (1080, 715, 1200, 775)])
th.save(O / "cap_threads.png")
# 관세: 에브리타임 글 + 연구원 답글
ev = op(A / "p2_1.jpg"); vstack([ev.crop((0, 180, 1206, 880)), ev.crop((0, 1640, 1206, 1900))], gap=0).save(O / "cap_ev.png")
ev2 = op(A / "p2_2.jpg"); ev2.crop((0, 150, 1206, 900)).save(O / "cap_ev2.png")
# 경희: 합격 화면 + 손글씨 복기 / 게임·봇 글(닉네임 가림)
pass_ = blur(op(K / "p1_1.jpg"), [(4, 30, 48, 58)]); hand = op(K / "p1_2.jpg")
hand.save(O / "cap_khu.png")  # 합격 화면은 표지 쪽에 쓰고 여기선 손글씨 복기만 크게
bot = blur(op(K / "p1_3.jpg"), [(3, 92, 52, 116)]); game = blur(op(K / "p1_4.jpg"), [(3, 96, 56, 120)])
hh = 760; bot = bot.resize((round(bot.width * hh / bot.height), hh)); game = game.resize((round(game.width * hh / game.height), hh))
side = Image.new("RGB", (bot.width + game.width + 16, hh), (255, 255, 255)); side.paste(bot, (0, 0)); side.paste(game, (bot.width + 16, 0)); side.save(O / "cap_game.png")
specs = [
 {"out": str(O / "c02.jpg"), "sub": "① 감평냥이 · 감정평가사 합격자", "title": "6개월 만에 합격\n수기는 '비공개'", "cap": str(O / "cap_blog.png"), "cap_max_h": 560, "box_bg": [255, 255, 255],
  "caption": "합격 수기 블로그 화면(X 게시물 캡처)", "label": "의혹이 번지자 생긴 일", "lines": ["합격 수기 3편이 '비공개'로 바뀌고", "감평 카페에 올린 수기도 사라졌다는 글"]},
 {"out": str(O / "c03.jpg"), "sub": "① 감평냥이 · 스레드 반응", "title": "\"평가사는 고작\n'180명' 뽑는데…\"", "cap": str(O / "cap_threads.png"), "cap_max_h": 560, "box_bg": [255, 255, 255],
  "caption": "스레드 게시물 캡처(아이디 가림)", "label": "온라인에서 나온 '주장'", "lines": ["\"이 사람마저 사실이면 기운 빠진다\"", "수험생들 사이에서 의혹이 퍼지는 중"]},
 {"out": str(O / "c04.jpg"), "sub": "② 관세냥이 · 관세사 수석 합격자", "title": "수석인데 인터뷰도\n축하 행사도 '안 왔다'", "cap": str(O / "cap_ev.png"), "cap_max_h": 560, "box_bg": [255, 255, 255],
  "caption": "에브리타임 게시물 캡처", "label": "10년 공식이 깨졌다", "lines": ["10년간 학원 두 곳이 수석·차석을 냈는데", "올해 수석은 '수강 이력이 없다'는 주장"]},
 {"out": str(O / "c05.jpg"), "sub": "② 관세냥이 · 관세청 입장", "title": "관세청 \"부정행위\n'확인된 사안 없다'\"", "cap": str(O / "cap_ev2.png"), "cap_max_h": 520, "box_bg": [255, 255, 255],
  "caption": "에브리타임 게시물 캡처", "label": "'동차 합격 급증'도 사실과 달랐다", "lines": ["동차 합격자 35명→38명→39명", "주장처럼 크게 늘지 않았습니다"]},
 {"out": str(O / "c06.jpg"), "sub": "③ 경희냥이 · 경희대 컴공 편입 합격생", "title": "두 달 뒤 30문제를\n'통째로' 복기", "cap": str(O / "cap_khu.png"), "cap_max_h": 580, "box_bg": [255, 255, 255],
  "caption": "디시인사이드 게시물 캡처(손글씨 복기)", "label": "기출 공개 전에 올린 손글씨", "lines": ["학교가 나중에 공개한 시험지와", "번호·보기 '순서까지' 모두 일치"]},
 {"out": str(O / "c07.jpg"), "sub": "③ 경희냥이 · 본인 해명", "title": "해명은\n'과잉기억증후군'", "cap": str(O / "cap_game.png"), "cap_max_h": 560, "box_bg": [255, 255, 255],
  "caption": "디시인사이드 게시물 캡처(닉네임 가림)", "label": "네티즌이 찾아낸 과거 글", "lines": ["시험 직전까지 게임 인증 글을 올리고", "AI로 디스코드 게임 봇을 만들고 있었다"]},
]
sp = Path("/tmp/nyang3_specs.json"); sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)
# 표지 배경: 회색 그라데이션 위에 캡처 세 장을 겹쳐 놓음
bg = Image.new("RGB", (W, H)); g = ImageDraw.Draw(bg)
for y in range(H): g.line((0, y, W, y), fill=(int(225 - 45 * y / H),) * 3)
cov = bg.convert("RGBA")
def place(base, t, cx, cy, ang, wdt):
    t = t.resize((wdt, round(t.height * wdt / t.width)), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", t.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, t.width - 1, t.height - 1), 18, fill=255); t.putalpha(m)
    sh = Image.new("RGBA", (t.width + 60, t.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 36, t.width + 30, t.height + 36), 18, fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(14)); sh.alpha_composite(t, (30, 30)); sh = sh.rotate(ang, Image.BICUBIC, expand=True)
    base.alpha_composite(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2)))
place(cov, blog.crop((0, 0, 1134, 600)), 290, 330, 4, 520)
place(cov, ev.crop((0, 180, 1206, 880)), 790, 300, -3, 560)
place(cov, hand, 560, 640, 2, 700)
cov.convert("RGB").save(O / "cover_bg.jpg", quality=95)
print("ok")
