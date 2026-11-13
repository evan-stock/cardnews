"""20261113-d19: 11월 19일 두 사람의 운명의 날 — 리트 만점자 수능 국어 생중계 / 세무사 수석 수습 집체교육. 틀: 검은 바탕 frame(kress/build_cards.py)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
D = Path(__file__).parent; O = D / "cand"
src = (D.parent / "20261113-kress/build_cards.py").read_text().split("# 표지 배경")[0]
ns = {"__file__": str((D.parent / "20261113-kress/build_cards.py").resolve())}; exec(src, ns)
frame, F, fit, YE = ns["frame"], ns["F"], ns["fit"], ns["YE"]

def quote(acc, lines, foot, w=940):
    h = 70 + 60 * len(lines) + 115
    im = Image.new("RGB", (w, h), (247, 247, 249)); d = ImageDraw.Draw(im)
    d.ellipse((40, 30, 84, 74), fill=(200, 200, 208)); d.text((100, 64), acc, font=F("SemiBold", 34), fill=(20, 20, 24), anchor="ls")
    y = 140
    for ln in lines:
        d.text((40, y), ln, font=F("Medium", 38), fill=(30, 30, 34), anchor="ls"); y += 60
    d.text((40, h - 34), foot, font=F("Medium", 28), fill=(130, 130, 140), anchor="ls")
    return im

def panel(rows, w=940):
    h = 60 + 150 * len(rows)
    im = Image.new("RGB", (w, h), (22, 22, 26)); d = ImageDraw.Draw(im)
    for i, (k, v) in enumerate(rows):
        y = 40 + i * 150
        d.rounded_rectangle((30, y, w - 30, y + 120), 18, fill=(36, 36, 42))
        d.text((64, y + 50), k, font=F("SemiBold", 32), fill=YE, anchor="ls")
        d.text((64, y + 98), v, font=F("Medium", 34), fill=(235, 235, 240), anchor="ls")
    return im

# 표지: 왼쪽 리트 만점자, 오른쪽 세무사 수석 합격 영상 장면
L = fit(O / "press04.jpg", 540, 1350, (.5, .3)).filter(ImageFilter.UnsharpMask(2, 50, 2))
R = fit(O / "tax_bg.jpg", 540, 1350, (.55, .4))
c = Image.new("RGB", (1080, 1350)); c.paste(L, (0, 0)); c.paste(R, (540, 0))
ImageDraw.Draw(c).rectangle((537, 0, 543, 1350), fill=(10, 10, 12)); c.save(O / "cover_bg.jpg", quality=95)

yt = Image.open(O / "src_yt.png").convert("RGB").crop((0, 0, 1142, 630)); yt = yt.resize((940, round(630 * 940 / 1142)), Image.LANCZOS)
frame(("리트 첫 만점자 이진우 · 19일 오전 11시", "수능 국어 '80분 생중계' 풀이"), yt,
      "\"편집 없이 원테이크로 생중계합니다\"", sub="감독·장소·채널은 16일까지 확정 (미미미누 채널 고정 댓글)").save(O / "c02.jpg", quality=95)

frame(("같은 날 세무사 수석은", "수습 '집체교육' 시작일"),
      quote("에펨코리아 인기글", ["세무사회 주관 수습세무사 집체교육 1개월", "합격자 모임은 노쇼해도 되지만", "이건 노쇼하면 세무사 등록이 안 됨", "그는 과연 11월 19일 집체교육에", "참석할 것인가"], "에펨코리아 · 11월 13일"),
      "빠지면 올해는 세무사 등록 불가", sub="시험 합격은 유지, 수습은 내년으로 미룰 수 있음").save(O / "c03.jpg", quality=95)

frame(("그런데 커뮤니티엔 이런 글까지", "\"수습 '안 하겠다'고 선언?\""),
      quote("엠봉 이용자 글", ["협회가 조사하려고 불렀는데", "조사 거부하면서 잠수하는 중", "수습? 집체교육?", "그냥 싹 다 안 한다고 선언"], "엠봉 · 11월 13일"),
      "본인은 \"소거법으로 풀었다\"며 의혹 부인", sub="언론 인터뷰 (이투데이 보도)").save(O / "c04.jpg", quality=95)

frame(("기관은 지금", "국세청 '진상 파악', 공단은 '물증이 먼저'"),
      panel([("국세청", "논란 커지자 진상 파악 착수"), ("한국산업인력공단", "물증 없이 재시험·소환은 어렵다"), ("세무사회", "진상조사 촉구, 단정·명예훼손은 경계")]),
      "부정행위 확인되면 시험 무효 + 5년 응시 정지", sub="세무사법 (파이낸셜뉴스·세정일보·조세금융신문)").save(O / "c05.jpg", quality=95)
print("ok")

# ── 2판(09:44 사용자 참고: @happygram.kr 3장 — 표지 '협회 조사 거부 후 잠수' → 조세일보 '연락두절'+블라인드 댓글 → '끝까지 수습 안 하면 재인')
def news(lines, foot, w=940):
    h = 60 + 62 * len(lines) + 125
    im = Image.new("RGB", (w, h), (255, 255, 255)); d = ImageDraw.Draw(im)
    d.text((w // 2, 62), "조세일보", font=F("Black", 40), fill=(20, 20, 24), anchor="ms")
    d.line((30, 92, w - 30, 92), fill=(225, 225, 230), width=3)
    y = 160
    for ln in lines:
        d.text((44, y), ln, font=F("Medium", 38), fill=(30, 30, 34), anchor="ls"); y += 62
    d.text((44, h - 30), foot, font=F("Medium", 28), fill=(130, 130, 140), anchor="ls")
    return im

frame(("세무사 수석 근황", "'연락 두절'"),
      news(["한 씨의 입장은 아직 확인되지 않았다.", "조세일보가 이날 오전 연락했지만", "한 씨는 \"지금은 대화가 어렵다\"고", "전해왔다. 한 씨의 개인 블로그는", "댓글 쓰기 기능이 막힌 상태다."], "조세일보 · 11월 12일"),
      "\"지금은 대화가 어렵다\"", sub="앞서 다른 인터뷰에선 \"소거법으로 풀었다\"며 부인 (이투데이)").save(O / "n02.jpg", quality=95)

frame(("직장인 커뮤니티 블라인드엔", "\"협회가 조사하려고 불렀는데 '잠수'\""),
      quote("블라인드 · 새회사 · D*****", ["일단 협회가 조사하려고 불렀는데", "잠수탐. 수습 안한다고 함.", "이후 행보가 궁금하지."], "블라인드 댓글"),
      "\"수습도 안 한다고 함\"", sub="세무사 합격 후 반드시 들어야 하는 교육").save(O / "n03.jpg", quality=95)

frame(("댓글 반응", "\"끝까지 수습 안 하면 '재인'이지\""),
      quote("커뮤니티 댓글", ["근데 63기에서 끝까지", "수습 안 하면 그냥 재인거지 ㅋㅋㅋ"], "커뮤니티 반응"),
      "수습 안 받으면 세무사 등록이 안 된다", sub="시험 합격은 유지, 수습은 내년 이후로 미룰 수 있음").save(O / "n04.jpg", quality=95)

c2 = fit(O / "glass_bg.jpg", 1080, 1350, (.5, .4)); c2.save(O / "cover2.jpg", quality=95)
print("v2 ok")
