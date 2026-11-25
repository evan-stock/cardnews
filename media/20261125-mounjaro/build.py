import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350; YE = (255, 216, 77); FG = (255, 255, 255)
F = lambda w, s: ImageFont.truetype(str(R / f"assets/fonts/Pretendard-{w}.otf"), s)


def rich_center(d, y, text, font, base):
    parts = re.split(r"('[^']*')", text); tw = sum(d.textlength(p.strip("'"), font=font) for p in parts if p)
    x = (W - tw) / 2
    for p in parts:
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base, anchor="ls"); x += d.textlength(p, font=font)


def rich(d, x, y, text, font, base=FG):
    for p in re.split(r"('[^']*')", text):
        if not p: continue
        hl = p.startswith("'"); p = p.strip("'")
        d.text((x, y), p, font=font, fill=YE if hl else base); x += d.textlength(p, font=font)


def logo(im):
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA"); lh = 40; lw = int(lg.width * lh / lg.height)
    lg = lg.resize((lw, lh), Image.LANCZOS); im.paste(lg, ((W - lw) // 2, H - 62 - lh), lg)


def frame(top, photo, bottom, sub=None):
    im = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(im)
    rich_center(d, 168, top[0], F("Medium", 46), FG); rich_center(d, 236, top[1], F("Black", 54), FG)
    p = photo
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 18, fill=255)
    im.paste(p, ((W - p.width) // 2, 300), m)
    d = ImageDraw.Draw(im); y = 300 + p.height + 92
    rich_center(d, y, bottom, F("Black", 46), YE)
    if sub: rich_center(d, y + 62, sub, F("Medium", 32), (190, 190, 198))
    logo(im); return im



def art(pub, head, paras, out, hl=()):
    """기사 본문을 흰 바탕 기사 화면처럼 그린다(기사 원문 그대로)."""
    Wd, P = 900, 34
    fh, fb, fl = ImageFont.truetype(str(R / "assets/fonts/noto/NotoSansCJK-Bold.ttc"), 33, index=1), F("Medium", 25), F("ExtraBold", 18)
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    def wrap(t, f, w):
        out_, line = [], ""
        for ch in t:
            if d0.textlength(line + ch, font=f) > w: out_.append(line); line = ch
            else: line += ch
        return out_ + [line]
    hl_ = wrap(head, fh, Wd - 2 * P); pl = [wrap(p, fb, Wd - 2 * P) for p in paras]
    H_ = P + 28 + len(hl_) * 48 + 18 + sum(len(x) * 42 + 18 for x in pl) + P
    im = Image.new("RGB", (Wd, H_), "white"); d = ImageDraw.Draw(im); y = P
    d.text((P, y), pub + " · 2026.11.24", font=fl, fill=(200, 0, 0)); y += 32
    for l in hl_: d.text((P, y), l, font=fh, fill=(17, 17, 17)); y += 48
    y += 14
    for x in pl:
        for l in x:
            if any(h in l for h in hl):
                d.rectangle((P - 4, y - 2, P + d.textlength(l, font=fb) + 4, y + 36), fill=(255, 240, 150))
            d.text((P, y), l, font=fb, fill=(34, 34, 34)); y += 42
        y += 18
    im.save(out)

if __name__ == "__main__":
    T = json.load(open(O.parent / "press/text.json"))
    q3 = Image.open(O / "q3.png").convert("RGB"); q5 = Image.open(O / "q5.png").convert("RGB")
    ImageOps.fit(q3, (1080, 1350), Image.LANCZOS, centering=(0.5, 0.35)).save(O / "cover.jpg", quality=95)
    SRC = "온라인 커뮤니티 확산 영상(원 게시자 미상)"
    frame(("대마도 택배 영업소 앞", "마운자로 받으려 '1시간' 줄"), ImageOps.fit(q5, (940, 700), Image.LANCZOS, centering=(0.5, 0.3)),
          "줄이 길어 '귀국 배'를 놓친 사람도", SRC).save(O / "c02.jpg", quality=93)
    art("머니투데이", T["mt"]["h"], T["mt"]["ps"][:2], O / "a_mt.png", hl=("1시간은", "11~16%"))
    art("파이낸셜뉴스", T["fn"]["h"], T["fn"]["ps"][1:3], O / "a_fn.png", hl=("3개월분", "30만원", "절반"))
    art("아이뉴스24", T["inews"]["h"], T["inews"]["ps"][2:5], O / "a_in1.png", hl=("34만원", "반값"))
    art("아이뉴스24", T["inews"]["h"], T["inews"]["ps"][:2], O / "a_in2.png", hl=("배를 놓",))
    spec = [
     {"out": str(O / "c03.jpg"), "sub": "11월 12일부터 바뀐 것", "title": "해외 처방약\n'3개월분' 들고 온다", "cap": str(O / "a_fn.png"), "box_bg": [255, 255, 255],
      "cap_max_h": 560, "caption": "파이낸셜뉴스 기사 캡처(11.24)", "label": "한국 30만원+ vs 일본 '절반 이하'",
      "lines": ["마운자로 2.5mg 4주분 기준", "일본 병원 온라인 진료 → 대마도 택배로 수령"]},
     {"out": str(O / "c04.jpg"), "sub": "실제로 다녀온 유튜버 계산", "title": "약 12개 + 왕복 배\n총 '34만원'", "cap": str(O / "a_in1.png"), "box_bg": [255, 255, 255],
      "cap_max_h": 560, "caption": "아이뉴스24 기사 캡처(11.24)", "label": "\"1박 해도 한국 '반값'도 안 된다\"",
      "lines": ["부산에서 배로 약 1시간, 당일치기 가능"]},
     {"out": str(O / "c05.jpg"), "sub": "몰려든 사람들", "title": "줄 서다 '배 놓치고'\n일본 병원은 '값 인상'", "cap": str(O / "a_in2.png"), "box_bg": [255, 255, 255],
      "cap_max_h": 520, "caption": "아이뉴스24 기사 캡처(11.24)", "label": "\"이미 직원이랑 싸우는 사람 있었다\"",
      "lines": ["후쿠오카 한 병원은 마운자로 값 11~16% 인상(머니투데이)", "신조어까지 등장: 스시 + 마운자로 = '스시자로'"]},
    ]
    json.dump(spec, open(O / "caps.json", "w"), ensure_ascii=False)
    subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "caps.json")], check=True, cwd=R)
    frame(("가기 전에 꼭 확인", "현지 약국선 '못' 산다"), ImageOps.fit(q3, (940, 600), Image.LANCZOS, centering=(0.5, 0.6)),
          "일본 병원 '처방'이 있어야 반입 가능",
          "본인 치료용 · 직접 휴대 · 용법상 3개월분(주 1회 펜 12개)까지").save(O / "c06.jpg", quality=93)
    cap = """[마운자로 사러 대마도까지 간 한국인들, 택배 영업소 앞 1시간 줄]

식품의약품안전처와 관세청이 11월 12일부터 해외에서 정상 처방받아 구매한 자가 치료용 의약품의 국내 휴대 반입을 허용하면서, 비만치료제 마운자로를 사러 일본 대마도로 가는 한국인이 늘고 있습니다. 마운자로·위고비 같은 비만치료제는 용법상 3개월분까지 들여올 수 있습니다(파이낸셜뉴스).

국내에서 마운자로 2.5mg 4주분 처방에는 30만원 이상이 들지만 일본에서는 절반 이하에 살 수 있는 것으로 전해졌습니다. 일본 병원의 온라인 진료로 처방받은 약을 대마도 택배 영업소로 보내 받는 방식입니다. 한 유튜버는 마운자로 12개와 배송비 약 25만원, 왕복 교통비를 더해 총 약 34만원이 들었다고 밝혔습니다(아이뉴스24).

대마도 야마토운수 영업소 앞에는 "1시간은 기다려야 받을 것 같다"는 긴 줄이 생겼고, 줄이 길어 귀국 배를 놓쳤다는 사연도 전해졌습니다. 후쿠오카의 한 의료기관은 마운자로 가격을 용량에 따라 11~16%가량 올린 것으로 알려졌습니다(머니투데이).

※ 대마도 현지 약국에서는 처방 없이 살 수 없고, 본인 치료 목적·직접 휴대·3개월분 이내 조건을 지켜야 합니다. 비만치료제는 부작용이 있을 수 있어 의사 진료가 필요합니다."""
    d = [{"id": "20261125-mounjaro", "slot": "lunch", "mode": "render",
          "topic": "마운자로 대마도 원정 구매(11.12 해외 처방약 3개월분 휴대 반입 허용, 한국 30만원+ vs 일본 절반, 총 34만원, 야마토 1시간 줄, 배 놓침, 후쿠오카 11~16% 인상)",
          "category": "생활", "images": ["cover.jpg", "c02.jpg", "c03.jpg", "c04.jpg", "c05.jpg", "c06.jpg"],
          "slides": [{"lay": "one", "t": "마운자로 반값에 사려고\n대마도로 '원정' 간 한국인들"}] + [{"raw": True}] * 5,
          "caption": cap, "hashtags": ["마운자로", "대마도", "스시자로", "비만치료제", "원정구매"],
          "sources": [{"publisher": "파이낸셜뉴스", "date": "2026.11.24"}, {"publisher": "아이뉴스24", "date": "2026.11.24"}, {"publisher": "머니투데이", "date": "2026.11.24"}],
          "photo_credits": ["온라인 커뮤니티 확산 영상(원 게시자 미상), 각 언론사 기사 캡처"]}]
    json.dump(d, open(O.parent / "draft.json", "w"), ensure_ascii=False, indent=1)
    print("ok")
