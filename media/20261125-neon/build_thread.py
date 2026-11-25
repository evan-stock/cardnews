"""트윗 원문 충실형: 각 장 = vechen 글 한국어 번역(엑스 화면 모양) + 원문 기록 사진. 1080x1350."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)
W, H = 1080, 1350; YE = (255, 216, 77); MU = (150, 156, 164)
whens = ["오전 4:40 · 2026년 11월 22일 · 조회수 154만"] + ["2026년 11월 22일"] * 4 + ["오전 4:59 · 2026년 11월 23일"]
items = json.load(open(D / "tk/ko.json"))
EX = [("개발자 vechen 원글 · 조회 154만", "\"이제 '인간'이 필요 없다\"", "주인 사망 소식만 줬을 뿐인데", "지갑 만들고, 알람 맞추고, 돈까지 벌었다"),
      ("실험 방식", "지시 0개, '편지' 1통", "15분 만에 생존 위기 파악", "돈 0원 · 구독 10일 · 서버 29일 남음"),
      ("처음 몇 시간", "자기를 '백업'하고 고쳤다", "주인 메일로 계정까지 되찾았다", "깃허브·클라우드플레어 복구, 2단계 인증까지"),
      ("돈 버는 법", "분신 40개로 '상금 사냥'", "30시간 뒤 첫 상금 6달러", "GTA6 공략·표지 그림 대회에서 3달러씩"),
      ("비결은", "AI가 아니라 '환경'?", "같은 AI도 일반 환경선 아무것도 안 했다", "개발자가 만든 '옥토퍼스 OS'에서만 생존 시도"),
      ("다음 날 공개된 뒷이야기", "막으니 '우회'했다", "인터넷·사이트를 끊어도 13시간 더", "결국 개발자가 직접 실험을 멈췄다")]
import re
def rich(d, x, y, t, f, base=(255, 255, 255), anchor="ls"):
    for p in re.split(r"('[^']*')", t):
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=f, fill=YE if hl else base, anchor=anchor); x += d.textlength(p, font=f)
logo = Image.open(R / "brand/logo_typo_A.png").convert("RGBA")
for i, (txt, img, lab) in enumerate(items):
    (D / f"tk/k{i}.txt").write_text(txt)
    subprocess.run([sys.executable, str(R / "scripts/x_dark_card.py"), str(D / f"tk/k{i}.png"), str(O / "avatar.jpg"), "vechen", "@miu21590", whens[i], str(D / f"tk/k{i}.txt")], check=True)
    tw = Image.open(D / f"tk/k{i}.png").convert("RGB")
    lg = Image.open(D / img).convert("RGB") if img else None
    cw = 1000
    th = round(tw.height * cw / tw.width); lh = round(lg.height * cw / lg.width) if lg else 0
    avail = 1350 - 245 - 310 - (36 if lg else 0)
    s = min(1, avail / (th + lh))
    cw2 = round(cw * s); th, lh = round(th * s), round(lh * s)
    im = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
    sub, ttl, lab2, line = EX[i]
    d.text((60, 110), sub, font=F("ExtraBold", 30), fill=YE, anchor="ls")
    rich(d, 60, 185, ttl, F("Black", 60))
    y = 225; x = (W - cw2) // 2
    im.paste(tw.resize((cw2, th), Image.LANCZOS), (x, y)); y += th + 16
    if lg:
        d.text((x, y), "AI(네온)가 남긴 실제 작업 기록 (원문)", font=F("Medium", 24), fill=MU); y += 36
        im.paste(lg.resize((cw2, lh), Image.LANCZOS), (x, y)); y += lh
    d.text((W - 40, y + 26), "번역: 오늘의쓸모", font=F("Medium", 20), fill=MU, anchor="rm")
    y += 80
    d.text((60, y), lab2, font=F("ExtraBold", 34), fill=YE, anchor="ls")
    rich(d, 60, y + 52, line, F("Medium", 32), base=(230, 230, 230))
    lw = 250; l = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    im.paste(l, ((W - lw) // 2, H - 60 - l.height), l)
    im.save(O / f"th{i}.jpg", quality=93); print(i, y)
d = json.load(open(D / "draft.json"))
d[0]["images"] = ["cover.jpg"] + [f"th{i}.jpg" for i in range(len(items))]
d[0]["slides"] = [d[0]["slides"][0]] + [{"raw": True}] * len(items)
json.dump(d, open(D / "draft.json", "w"), ensure_ascii=False, indent=1)
