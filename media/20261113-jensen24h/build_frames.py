"""20261113-jensen24h 2~4장: 검은 바탕 틀(frame) — kress/build_cards.py의 frame() 재사용."""
from pathlib import Path
from PIL import Image, ImageOps
D = Path(__file__).parent; J = D / "cand"
src = (D.parent / "20261113-kress/build_cards.py").read_text().split("# 표지 배경")[0]
ns = {"__file__": str((D.parent / "20261113-kress/build_cards.py").resolve())}; exec(src, ns)
frame, fit = ns["frame"], ns["fit"]

# 표지·CTA 배경: 웃는 젠슨 황(위키트리) 세로 크롭
fit(J / "press19.jpg", 1080, 1350, (.42, .3)).save(J / "cover_bg.jpg", quality=95)

frame(("① 물러난 그날, 로이터 보도", "'세 번째' 여성 의혹"), J / "press09.jpg",
      "엔비디아 사내 또 다른 직원과 내연 관계", sub="앨리스 황·킴벌리 파월 부사장에 이어 세 번째 · 엔비디아는 논평 거부",
      focus=(.6, .35)).save(J / "f02.jpg", quality=95)

# 트럼프 + 팀 쿡 나란히
a = fit(J / "press12.jpg", 463, 760, (.45, .3)); b = fit(J / "cook_crop.jpg", 463, 760, (.5, .3))
pair = Image.new("RGB", (940, 760), (10, 10, 12)); pair.paste(a, (0, 0)); pair.paste(b, (477, 0))
frame(("② 트럼프가 트루스소셜에", "\"후임은 '팀 쿡'뿐\""), pair,
      "\"전설이 또 다른 전설을 대체한다\"", sub="애플 전 CEO 팀 쿡 공개 추천 · 선임 권한은 엔비디아 이사회").save(J / "f03.jpg", quality=95)

frame(("③ 물러나도 끝이 아니다", "18일 '선서'하고 증언대에"), J / "press04.jpg",
      "\"안 나오면 소환장\" — 하원 외교위원장", sub="상원은 러트닉 상무장관까지 출석 요구 · 백악관은 교체 논의(로이터)",
      focus=(.5, .3)).save(J / "f04.jpg", quality=95)
print("ok")
