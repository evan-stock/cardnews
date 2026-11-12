"""20261113-taxglass3: X @Tesla_Teslaway(11.12 21:27, 조회 43만) 사진 4장 흐름 — 디시 글 → 영상 장면·수기 → 댓글 → 결론. 코난 그림은 빼고 결론 글만 씀.
틀은 20261113-jensenout과 같은 '검은 바탕 위 2줄 + 가운데 사진 + 아래 노란 줄'(kress/build_cards.py frame 재사용)."""
from pathlib import Path
from PIL import Image
D = Path(__file__).parent; O = D / "cand"
src = (D.parent / "20261113-kress/build_cards.py").read_text().split("# 표지 배경")[0]
ns = {"__file__": str((D.parent / "20261113-kress/build_cards.py").resolve())}; exec(src, ns)
frame = ns["frame"]
def h(im, hh, maxw=940):
    r = min(hh / im.height, maxw / im.width); return im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
u = [Image.open(O / f"url0{i}.jpg").convert("RGB") for i in range(1, 5)]
# 표지: 두 손 + 휴대폰 장면
u[1].crop((40, 0, 1290, 1562)).resize((1080, 1350), Image.LANCZOS).save(O / "cover_bg.jpg", quality=95)
frame(("디시 세무사 갤러리 · 11월 12일 20:06", "\"지금 보니까 이거 '어케' 찍은 거임?\""), h(u[0].crop((0, 274, 1101, 2048)), 760),
      "두 손으로 정보 가리며 찍은 합격 확인 영상", sub="수석이 직접 올린 영상 장면").save(O / "c02.jpg", quality=95)
frame(("같은 영상의 다른 장면", "손은 '두 개', 폰은 책상 위"), h(u[1], 760),
      "\"1개 틀린 건 운 좋게 다 걸려준 느낌\"", sub="영상과 함께 올린 합격 수기 중").save(O / "c03.jpg", quality=95)
frame(("댓글 반응", "\"딱 '안경 위치'긴 하네ㅋㅋ\""), h(u[2], 760),
      "\"와 개소름.. 누가 찍고 있던 거지?\"", sub="디시 세무사 갤러리 댓글").save(O / "c04.jpg", quality=95)
frame(("커뮤니티가 내놓은 결론", "\"'AI 안경'으로 찍었을 것\""), (lambda a, b: (lambda c: (c.paste(a, (0, 0)), c.paste(b, (0, a.height + 14)), c)[2])(Image.new("RGB", (940, a.height + 14 + b.height), (10, 10, 12))))(ns["fit"](O / "url02.jpg", 940, 340, (.5, .35)), h(u[3].crop((0, 1530, 1291, 2048)), 999)),
      "엑스에서만 조회 43만", sub="X @Tesla_Teslaway · 11월 12일").save(O / "c05.jpg", quality=95)
print("ok")
