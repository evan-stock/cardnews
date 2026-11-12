"""20261113-jensenout 4~6장: 3장(크레스)과 같은 '검은 바탕 위 2줄 + 가운데 사진 + 아래 노란 줄' 틀. kress/build_cards.py의 함수 재사용."""
from pathlib import Path
from PIL import ImageFont
D = Path(__file__).parent; J = D / "cand"
src = (D.parent / "20261113-kress/build_cards.py").read_text().split("# 표지 배경")[0]
ns = {"__file__": str((D.parent / "20261113-kress/build_cards.py").resolve())}; exec(src, ns)
frame = ns["frame"]
frame(("나흘 동안 무슨 일이", "8일 '불륜 인정' → 12일 '사임'"), J / "press11.jpg",
      "11일 NYT, 부하 임원과 두 번째 불륜 보도", sub="8일엔 이사회가 '신뢰' 표명 → 하루 만에 해임 논의",
      focus=(.55, .3)).save(J / "f04.jpg", quality=95)
frame(("시장 반응 · 현지 12일 개장 직후", "주가 '14%' 폭락"), J / "hq_old.jpg",
      "시총 최대 6,010억 달러 증발", sub="그대로 마감하면 한 종목 하루 손실 역대 최대 (블룸버그)",
      focus=(.5, .5)).save(J / "f05.jpg", quality=95)
frame(("의혹의 핵심 · 앨리스 황 회사 메가스피드", "엔비디아 칩 '46억 달러'어치"), J / "alice.jpg",
      "알리바바 등 중국 기업에 대여 (무역 기록)", sub="젠슨 황은 국가안보·기밀 훼손 의혹은 부인",
      focus=(.5, .4)).save(J / "f06.jpg", quality=95)
print("ok")
from PIL import Image
cap = Image.open(J / "src_nvpr.png").convert("RGB"); cap = cap.resize((940, round(cap.height * 940 / cap.width)), Image.LANCZOS)
top = ns["fit"](J / "press10.jpg", 940, 400, (.5, .35))
combo = Image.new("RGB", (940, 400 + 14 + cap.height), (10, 10, 12)); combo.paste(top, (0, 0)); combo.paste(cap, (0, 414)); cap = combo
frame(("엔비디아 공식 발표 · 현지 11월 12일", "사장·CEO·이사직 '즉시' 사임"), cap,
      "이사회는 사임 이유를 밝히지 않았다", sub="엔비디아 뉴스룸 보도자료 캡처").save(J / "f02.jpg", quality=95)
