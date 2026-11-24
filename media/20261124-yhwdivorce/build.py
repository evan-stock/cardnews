"""20261124-yhwdivorce: 양홍원·원현주 결혼식 37일 만에 이혼 발표(원현주 SNS, 11.24). 10.24 불륜설 게시물 후속."""
import json, subprocess, sys, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; O.mkdir(exist_ok=True)
T = Path("/tmp/claude-tool-results/a493c683-e7b1-5bd7-9aa7-411f6fdd042e")
def shot(name, box, out):
    Image.open(T / f"mcp-claude-in-chrome-blob-{name}.jpg").convert("RGB").crop(box).save(O / out)
shot("1795505573445-015psb-95f8392e", (35, 170, 840, 520), "cap_stmt.png")
shot("1795505627783-803xox-1ed70195", (30, 200, 790, 435), "cap_issue.png")
shot("1795505592496-zouzea-c94816e4", (30, 25, 880, 250), "cap_newsis.png")
shot("1795505627783-dkkinq-5d2d22af", (30, 200, 790, 440), "cap_signs.png")
# 원현주 인스타 스토리(입장문) — 게시 화면 왼쪽 이미지
shot("1795505487729-ow2nr4-0dd0eae3", (508, 130, 745, 478), "cap_story.png")
shot("1795506430036-8wiqqo-edc70d13", (380, 180, 903, 620), "cap_story_big.png")
shot("1795506420064-hmls0k-3da1ba7a", (30, 30, 840, 405), "cap_y1.png")
shot("1795506420064-3rimrs-e03f1ee2", (30, 30, 840, 345), "cap_y2.png")
shot("1795507932375-pyf0i3-adb09a8b", (20, 160, 850, 505), "cap_why.png")

# 표지: 캡처 카드 콜라주
W_, H_ = 1080, 1350
bg = Image.new("RGB", (W_, H_), (16, 16, 20))
glow = Image.new("L", (W_, H_), 0); ImageDraw.Draw(glow).ellipse((-150, 0, 1230, 1000), fill=110)
bg = Image.composite(Image.new("RGB", (W_, H_), (70, 30, 40)), bg, glow.filter(ImageFilter.GaussianBlur(180)))
def card(src, w, angle, xy):
    global bg
    im = Image.open(O / src).convert("RGB"); h = int(im.height * w / im.width); im = im.resize((w, h), Image.LANCZOS)
    pad = 16; c = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    m = Image.new("L", c.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, c.width - 1, c.height - 1), 26, fill=255)
    c.paste(Image.new("RGBA", c.size, (255, 255, 255, 255)), (0, 0), m)
    im_m = Image.new("L", im.size, 0); ImageDraw.Draw(im_m).rounded_rectangle((0, 0, w - 1, h - 1), 14, fill=255)
    c.paste(im, (pad, pad), im_m); c = c.rotate(angle, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", (c.width + 60, c.height + 60), (0, 0, 0, 0)); sh.paste((0, 0, 0, 150), (30, 40), c.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(18)); base = bg.convert("RGBA")
    base.alpha_composite(sh, (xy[0] - 30, xy[1] - 30)); base.alpha_composite(c, xy); bg = base.convert("RGB")
card("cap_issue.png", 820, -4, (40, 60))
card("cap_story.png", 420, 5, (560, 300))
card("cap_stmt.png", 700, 3, (30, 470))
bg.save(O / "cover.jpg", quality=95)

Wc = [255, 255, 255]
spec = [
 {"out": str(O / "c_won.jpg"), "sub": "원현주 · 11월 24일 인스타그램 스토리",
  "title": "\"원만하게 합의해\n이혼 절차 '거의 종료'\"", "cap": str(O / "cap_story_big.png"),
  "caption": "원현주 인스타그램 스토리", "label": "이혼 사유는 밝히지 않았다",
  "lines": ["\"자세한 이야기는 드리기 어렵다\"", "\"안부 물어주신 분들께 진심으로 감사\""], "cap_max_h": 620},
 {"out": str(O / "c_y1.jpg"), "sub": "양홍원 · 하루 전(23일) 인스타그램",
  "title": "\"난 힘들 때\n'하늘'을 본다\"", "cap": str(O / "cap_y1.png"),
  "caption": "양홍원 인스타그램 게시물", "label": "\"내 직업은 적어도 변호사나 기자만큼 존경받아 마땅\"",
  "lines": ["\"아직 니들은 내가 어떤 마음인지 모른다\""], "cap_max_h": 520},
 {"out": str(O / "c_y2.jpg"), "sub": "양홍원 · 같은 글 후반부",
  "title": "\"죽여놨던 색기도\n곧 '되살아나리라'\"", "cap": str(O / "cap_y2.png"),
  "caption": "양홍원 인스타그램 게시물", "label": "마지막 한마디는 \"나야 나, 사나이\"",
  "lines": ["#사나이 해시태그로 끝", "아내·이혼에 대한 언급은 없었다"], "cap_max_h": 460},
 {"out": str(O / "c_issue.jpg"), "sub": "8년 열애의 끝", "box_bg": Wc,
  "title": "결혼식 5일 만에 불륜설\n37일 만에 '파경'", "cap": str(O / "cap_issue.png"),
  "caption": "스포티비뉴스 기사 캡처", "label": "2023년 혼인신고 · 2024년 딸 출산",
  "lines": ["10월 18일 뒤늦게 결혼식(사회 스윙스)", "10월 23일 지인 A씨가 '모텔 동행' 폭로"], "cap_max_h": 330},
 {"out": str(O / "c_newsis.jpg"), "sub": "불륜 의혹은 어떻게 됐나", "box_bg": Wc,
  "title": "소속사 \"애정 행위 없었다\"\n폭로자도 \"직접 못 봤다\"", "cap": str(O / "cap_newsis.png"),
  "caption": "뉴시스 기사 캡처", "label": "모텔 동행 사실 자체는 인정",
  "lines": ["소속사는 폭로자를 공갈·명예훼손 등으로 고소", "폭로자 A씨는 이후 입장을 바꿨다"], "cap_max_h": 330},
 {"out": str(O / "c_why.jpg"), "sub": "\"이혼 잘했다\" 반응이 나온 이유", "box_bg": Wc,
  "title": "한 사람은 '폭주'\n한 사람은 '침묵'", "cap": str(O / "cap_why.png"),
  "caption": "톱스타뉴스 기사 캡처(11.19)", "label": "의혹 해명 없이 자극적 게시물만 이어졌다",
  "lines": ["양홍원: \"가족 잃은 기분\" 신곡, 욕설·운전 중 흡연 영상", "원현주: 남편·딸 사진만 지우고 침묵 → 짧은 입장문"], "cap_max_h": 360},
]
json.dump(spec, open(O / "caps.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "caps.json")], check=True, cwd=R)

cap = """[결혼식 37일 만에 이혼한 양홍원·원현주, 두 사람이 SNS에 남긴 글]

원현주는 24일 인스타그램 스토리에 짧고 정중한 입장문으로 이혼 소식을 알렸습니다. 하루 전인 23일 양홍원은 "난 힘들 때 하늘을 본다"로 시작해 "내 직업은 적어도 변호사나 기자만큼 존경받아 마땅하고", "아버지가 되려고 죽여놨던 색기도 곧 되살아나리라 믿는다", "나야 나, 나야 나. 사나이"로 끝나는 장문의 글을 올렸습니다. 아내나 이혼에 대한 언급은 없었습니다.

원현주는 24일 자신의 SNS에 "현재 원만하게 합의하여 이혼 절차를 거의 종료했다"고 밝혔습니다. "개인적인 일인 만큼 자세한 이야기는 드리기 어려운 점 너그러이 이해해 달라"며 구체적인 사유와 합의 내용은 공개하지 않았습니다.

두 사람은 약 8년간 교제한 끝에 2023년 혼인신고를 했고 2024년 딸을 얻었습니다. 지난 10월 18일 뒤늦게 결혼식을 올렸지만, 닷새 뒤 지인 A씨가 양홍원이 다른 여성과 모텔에 동행했다고 폭로하면서 불륜 의혹이 불거졌습니다.

당시 소속사는 모텔 동행 사실은 인정하면서도 만취 상태에서 잠을 자기 위한 것이었고 객실 내 애정 행위는 없었다고 해명했으며, 폭로자를 공갈·명예훼손 등의 혐의로 고소했습니다. A씨는 이후 불륜 장면을 직접 목격하지 못했다고 입장을 바꿨습니다(뉴시스).

의혹 이후 양홍원은 해명 없이 신곡과 함께 "가족 잃은 기분 아무도 모를 거야"라는 글을 올렸고, 욕설 문구와 운전 중 흡연 장면이 담긴 영상도 공개했습니다(톱스타뉴스). 반면 원현주는 말을 아낀 채 SNS에서 양홍원과 딸의 사진을 정리했고, 이혼 발표도 짧은 입장문으로 마무리했습니다. 이혼 발표 뒤 두 사람의 대조적인 대응이 다시 주목받고 있습니다.

의혹 이후 두 사람은 서로의 SNS를 언팔로우했고, 원현주는 게시물을 비공개로 돌렸다가 양홍원과 결혼 생활 관련 게시물을 삭제한 뒤 계정을 다시 열었습니다. 양홍원은 이혼 발표 하루 전 SNS에 가족과 자신의 삶에 관한 장문의 글을 올렸지만 두 사람의 관계는 언급하지 않았습니다.

※ 이혼 사유는 당사자가 밝히지 않았으며, 불륜 의혹은 소속사가 부인한 상태입니다."""
d = [{
 "id": "20261124-yhwdivorce", "slot": "dinner", "mode": "render",
 "topic": "양홍원·원현주 결혼식 37일 만에 이혼 발표(원현주 SNS 11.24). 10.23 모텔 동행 폭로·소속사 부인·폭로자 입장 번복, 언팔·게시물 삭제. 10.24 불륜설 게시물 후속",
 "category": "연예",
 "images": ["cover_people.jpg", "c_won.jpg", "c_y1.jpg", "c_y2.jpg", "c_why.jpg", "c_issue.jpg", "c_newsis.jpg"],
 "slides": [
  {"lay": "one", "t": "\"원현주 이혼 잘했다\"\n반응 쏟아진 '진짜 이유'"},
  {"raw": True}, {"raw": True}, {"raw": True}, {"raw": True}, {"raw": True}, {"raw": True}
 ],
 "caption": cap,
 "hashtags": ["양홍원", "원현주", "이혼", "연예뉴스", "래퍼"],
 "sources": [
  {"publisher": "원현주 인스타그램", "date": "2026.11.24"},
  {"publisher": "스포티비뉴스", "date": "2026.11.24"},
  {"publisher": "뉴시스", "date": "2026.11.24"},
  {"publisher": "톱스타뉴스", "date": "2026.11.19"}
 ],
 "photo_credits": ["원현주 인스타그램 스토리, 스포티비뉴스·뉴시스·톱스타뉴스 화면"]
}]
json.dump(d, open(D / "draft.json", "w"), ensure_ascii=False, indent=1)
