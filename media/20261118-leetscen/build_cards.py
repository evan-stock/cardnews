"""20261118-leetscen: 내일 리트 만점자 공개 검증 예상 시나리오 4가지 + 커뮤니티 '검증의 한계' 원문(X @kingwest0219, 치팅 수법 단계 부분은 제외).
'5m→20cm' 전파탐지기 수치는 기사 미확인이라 원문 인용 안에만 둠. 실명 안 씀."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
R = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(R / "scripts")); D = Path(__file__).parent; O = D / "cand"
from xpost_cards import W, H, P, FG, MU, YE, LN, BOX, F, wrap, rich, base, logo, head

def text_card(out, sub, title, label, paras, foot):
    im = base(); d = ImageDraw.Draw(im); y = head(d, sub, title, y=90) + 46
    x0, x1 = P - 20, W - P + 20; f = F("Medium", 29); fb = F("ExtraBold", 30)
    lines = []
    for kind, t in paras:
        for ln in wrap(d, t, fb if kind == 'h' else f, x1 - x0 - 60): lines.append((kind, ln))
        lines.append(('gap', ''))
    h = 40 + sum(42 if k != 'gap' else 14 for k, _ in lines) + 20
    d.rounded_rectangle((x0, y, x1, y + h), 24, fill=BOX, outline=LN, width=3)
    d.text((x0 + 30, y - 34), label, font=F("Medium", 24), fill=MU)
    ty = y + 30
    for k, t in lines:
        if k == 'gap': ty += 14; continue
        d.text((x0 + 30, ty), t, font=fb if k == 'h' else f, fill=YE if k == 'h' else FG); ty += 42
    rich(d, P, y + h + 40, foot, F("SemiBold", 32))
    logo(im); im.save(O / out, quality=93)

def list_card(out, sub, title, items, foot, foot2=""):
    im = base(); d = ImageDraw.Draw(im); y = head(d, sub, title, y=110)
    for lab, main, desc in items:
        d.rounded_rectangle((P, y, W - P, y + 200), 22, fill=BOX, outline=LN, width=2)
        d.text((P + 30, y + 28), lab, font=F("SemiBold", 28), fill=MU); rich(d, P + 30, y + 70, main, F("Black", 40))
        for k, ln in enumerate(wrap(d, desc, F("Medium", 29), W - 2 * P - 60)[:2]): d.text((P + 30, y + 128 + k * 38), ln, font=F("Medium", 29), fill=(205, 205, 212))
        y += 224
    rich(d, P, y + 30, foot, F("SemiBold", 32))
    if foot2: d.text((P, y + 80), foot2, font=F("Medium", 24), fill=MU)
    logo(im); im.save(O / out, quality=93)

list_card("c02.jpg", "지금까지 확인된 것", "본인은 \"목요일에\n'다 밝혀질 것'\"", [
    ("본인 입장(중앙일보·한국일보)", "\"차라리 '수사를 받겠다'\"", "AI는 한 번도 안 썼다, 조사가 시작되면 언제든 응하겠다"),
    ("19일(목)", "수능 국어 '공개 풀이'", "언론사 참관 아래 생중계로 풀겠다고 예고"),
    ("그 사이", "시대인재 '계약 해지'·고발 예정", "현직 변호사가 고발장을 내겠다고 밝힘")],
    "부정행위는 아직 '확인된 사실이 아님'", "중앙일보·한국일보·뉴시스(11.17~18)")
text_card("c03.jpg", "커뮤니티에서 나온 지적", "\"카메라만 막아선\n'부족하다'\"", "X @kingwest0219 게시물 원문 중 <검증의 한계>", [
    ('h', "1. 초소형 카메라가 핵심이 아님"),
    ('p', "지정 복장으로 환복시켜도 외부에서 정답을 송신해 준다면 내부에서 문제를 푸는 리트냥이가 굳이 직접 촬영할 이유가 없음."),
    ('h', "2. 귀·구강 검사만으로 충분할까?"),
    ('p', "시각·청각뿐 아니라 촉각을 이용한 수신 장치도 생각해 볼 수 있음. 신체에 부착하고 외부에서 식별하기 어렵게 은닉한다면 육안 검사만으로 찾아내기는 쉽지 않을 것임."),
    ('h', "3. 금속탐지기와 RF 탐지기도 만능이 아님"),
    ('p', "금속탐지기는 물체의 크기·재질·방향에 따라 탐지 성능이 달라짐. RF 탐지기도 주변 전파가 많은 환경에서는 특정 신호를 구별하기 어렵고, 간헐적인 신호는 탐지 순간을 놓칠 수 있음.")],
    "커뮤니티 주장, '확인된 사실 아님'")
list_card("c04.jpg", "내일 생중계 볼 때", "시청자들이 지켜볼\n의문점 '3가지'", [
    ("①", "답이 '밖에서' 들어올 틈은?", "통신이 완전히 막힌 곳에서 푸는지"),
    ("②", "몸·소지품 검사는 '누가'?", "본인 측이 아닌 제3자가 하는지"),
    ("③", "왜 꼭 '생중계'인가?", "생중계 환경이 전파를 못 막는 곳은 아닌지(커뮤니티 의문)")],
    "셋 다 막히면 '진짜 검증', 하나라도 빠지면 '논란 계속'")
list_card("c05.jpg", "내일 예상 시나리오", "어떻게 흘러갈까 '4가지'", [
    ("시나리오 ①", "'정면 돌파'", "예정대로 풀고 고득점. 그래도 \"풀이 과정을 설명하라\"는 요구는 남는다"),
    ("시나리오 ②", "'조건 싸움'", "시작 전 장소·감독·검사 방식을 두고 부딪힌다. 생중계가 늦어지거나 줄어든다"),
    ("시나리오 ③", "'연기'", "고발이 들어간 만큼 \"수사로 밝히겠다\"며 미룬다"),
    ("시나리오 ④", "'애매한 점수'", "만점은 아닌 고득점. 논란은 오히려 길어진다")],
    "")
ImageOps.fit(Image.open(O / "photo.jpg").convert("RGB"), (W, H), Image.LANCZOS, centering=(.64, .3)).save(O / "cover_bg.jpg", quality=95)
print("ok")
