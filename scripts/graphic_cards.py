"""장 유형별 그래픽 카드 (2026.11.26, 사용자 선택: ho.ongs_ '로리 황 입장문' 게시물 디자인 방향).
1080x1350. 공통 틀: 배경(표지 사진 흑백·흐리고 아주 어둡게, 없으면 검정) → 가운데 노란 꼬리표(sub) → 그래픽 →
가운데 결론 1~2줄(title, '강조' 노랑) → 회색 각주(note) → 하단 로고. 내용 묶음은 세로 가운데로 자동 배치.
우리 브랜드로 바꾼 점: 강조색은 노랑(#FFD84D)만(빨강·주황 안 씀), Pretendard, today.worthy 로고.
사용: python scripts/graphic_cards.py spec.json   (spec = 장 리스트)

유형(kind)과 필드
- number   : 큰 숫자.        big("30"), unit("배", 노랑, 선택), desc(회색 설명 줄, 선택)
- versus   : 두 칸 비교.      left{"h","items","mark"}, right{"h","items","mark"} (왼쪽 노랑 윗줄, 오른쪽 회색)
- bars     : 막대 비교.       bars:[{"label","value_text","ratio":0~1}] (첫 막대 노랑, 나머지 회색)
- timeline : 타임라인.        head(왼쪽 큰 제목), rows:[{"d","t","s"}], 마지막 d가 "지금"이면 회색
- quote    : 말풍선 인용.     bubbles:[{"who","t"} 또는 "발언"] 최대 2(지그재그), face/face_crop/name/role(선택, 얼굴 사진)
- reports  : 보도 목록.       rows:[{"m":"매체\\n11.25","t":"요약 제목","s":"회색 한 줄"}] (최대 4)
- capture  : 캡처 + 딱지.     cap, cap_crop(선택), stamp(노란 테두리 딱지 글)
공통: out, bg(배경 사진), sub, title, note
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xpost_cards import W, H, BG, MU, YE, LN, F  # noqa: E402
from video_cap_card import parts, plain, wrap, fix_quotes, draw_rich_center, logo  # noqa: E402

WHITE = (255, 255, 255)
DIM = (110, 114, 122)
PANEL = (24, 25, 28, 235)
CX = W // 2


def background(path):
    if not path:
        return Image.new("RGB", (W, H), BG)
    im = ImageOps.fit(Image.open(path).convert("RGB"), (W, H), centering=(0.5, 0.3))
    im = ImageOps.grayscale(im).convert("RGB").filter(ImageFilter.GaussianBlur(4))
    return Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), 0.84)


def tag(d, y, text):
    f = F("Black", 30)
    w = d.textlength(text, font=f)
    d.rounded_rectangle((CX - w / 2 - 20, y, CX + w / 2 + 20, y + 52), 6, fill=YE)
    d.text((CX - w / 2, y + 7), text, font=f, fill=(12, 12, 14))
    return y + 52


def rich_left(d, x, y, text, font, base=WHITE):
    for p, hl in parts(text):
        d.text((x, y), p, font=font, fill=YE if hl else base)
        x += d.textlength(p, font=font)


def face_img(path, size, crop=None, border=YE):
    im = Image.open(path).convert("RGB")
    if crop:
        im = im.crop(tuple(crop))
    im = ImageOps.fit(im, (size, size), Image.LANCZOS)
    out = Image.new("RGB", (size + 8, size + 8), border)
    out.paste(im, (4, 4))
    return out


def panel(im, box, r=14, fill=PANEL):
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle(box, r, fill=fill)
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def footer(im, s, y):
    d = ImageDraw.Draw(im)
    if s.get("title"):
        f = F("Black", 52)
        for i, ln in enumerate(fix_quotes(wrap(d, s["title"], f, 900))):
            draw_rich_center(d, CX, y + i * 70, ln, f)
            last = y + i * 70 + 60
        y = last + 18
    if s.get("note"):
        f = F("Medium", 24)
        w = d.textlength(s["note"], font=f)
        d.text((CX - w / 2, y), s["note"], font=f, fill=DIM)
        y += 36
    if y > H - 100:
        print("경고: 로고와 겹칠 수 있음", s["out"], y)
    return y


def k_number(im, s):
    d = ImageDraw.Draw(im)
    y = tag(d, s["_y0"], s["sub"]) + 60
    sz = 190
    while True:
        fb, fu = F("Black", sz), F("Black", round(sz * 0.58))
        wb = d.textlength(s["big"], font=fb)
        wu = d.textlength(s.get("unit", ""), font=fu) + (24 if s.get("unit") else 0)
        if wb + wu <= 920 or sz <= 90:
            break
        sz -= 6
    x = CX - (wb + wu) / 2
    d.text((x, y), s["big"], font=fb, fill=WHITE)
    if s.get("unit"):
        d.text((x + wb + 24, y + round(sz * 0.33)), s["unit"], font=fu, fill=YE)
    y += round(sz * 1.2) + 10
    if s.get("desc"):
        f = F("Medium", 34)
        w = d.textlength(s["desc"], font=f)
        d.text((CX - w / 2, y), s["desc"], font=f, fill=MU)
        y += 70
    return im, footer(im, s, y + 20)


def k_versus(im, s):
    d = ImageDraw.Draw(im)
    y = tag(d, s["_y0"], s["sub"]) + 40
    if s.get("face"):
        fc = face_img(s["face"], 150, s.get("face_crop"))
        im.paste(fc, (CX - fc.width // 2, y))
        d = ImageDraw.Draw(im)
        y += fc.height + 14
        for txt, f, c in ((s.get("name", ""), F("Black", 32), WHITE), (s.get("role", ""), F("Medium", 24), MU)):
            if txt:
                w = d.textlength(txt, font=f)
                d.text((CX - w / 2, y), txt, font=f, fill=c)
                y += 42
        y += 16
    cw, gap, x0 = 440, 20, (W - 2 * 440 - 20) // 2
    rows = max(len(s["left"]["items"]), len(s["right"]["items"]))
    ch = 90 + rows * 62 + 20
    for i, (side, col, mark) in enumerate(((s["left"], YE, "O"), (s["right"], DIM, "?"))):
        x = x0 + i * (cw + gap)
        im = panel(im, (x, y, x + cw, y + ch))
        d = ImageDraw.Draw(im)
        d.rectangle((x, y, x + cw, y + 7), fill=col)
        d.text((x + 28, y + 26), side["h"], font=F("Black", 36), fill=col)
        for j, it in enumerate(side["items"]):
            yy = y + 96 + j * 62
            d.text((x + 28, yy), side.get("mark", mark), font=F("Black", 30), fill=col)
            rich_left(d, x + 68, yy, it, F("SemiBold", 30))
    return im, footer(im, s, y + ch + 50)


def k_bars(im, s):
    d = ImageDraw.Draw(im)
    y = tag(d, s["_y0"], s["sub"]) + 70
    x0, x1 = 110, 970
    for i, b in enumerate(s["bars"]):
        col = YE if i == 0 else (150, 156, 164)
        d.text((x0, y), b["label"], font=F("SemiBold", 32), fill=WHITE)
        f = F("Black", 34)
        w = d.textlength(b["value_text"], font=f)
        d.text((x1 - w, y - 2), b["value_text"], font=f, fill=col)
        y += 56
        im = panel(im, (x0, y, x1, y + 60), r=6, fill=(255, 255, 255, 28))
        d = ImageDraw.Draw(im)
        bw = max(18, round((x1 - x0) * b["ratio"]))
        d.rounded_rectangle((x0, y, x0 + bw, y + 60), 6, fill=col)
        y += 60 + 44
    return im, footer(im, s, y + 30)


def k_timeline(im, s):
    d = ImageDraw.Draw(im)
    y = s["_y0"]
    rich_left(d, 110, y, s["head"], F("Black", 58))
    y += 120
    n = len(s["rows"])
    step = 120
    lx = 250
    d.line((lx, y + 20, lx, y + 20 + step * (n - 1)), fill=LN, width=3)
    for r in s["rows"]:
        col = DIM if r["d"] == "지금" else YE
        d.text((110, y), r["d"], font=F("Black", 32), fill=col)
        d.ellipse((lx - 9, y + 11, lx + 9, y + 29), fill=col)
        d.text((290, y - 2), r["t"], font=F("Black", 36), fill=WHITE)
        if r.get("s"):
            d.text((290, y + 46), r["s"], font=F("Medium", 26), fill=MU)
        y += step
    end = y - step + 80
    if s.get("note"):
        end = footer(im, {"note": s["note"], "out": s["out"]}, y + 10)
    return im, end


def bubble(im, x, y, w, text, tail_left=True):
    d = ImageDraw.Draw(im)
    f = F("Black", 38)
    lines = fix_quotes(wrap(d, text, f, w - 70))
    h = 50 + 54 * len(lines)
    d.rounded_rectangle((x, y, x + w, y + h), 10, fill=WHITE)
    tx = x + 60 if tail_left else x + w - 60
    d.polygon([(tx - 18, y), (tx + 18, y), (tx, y - 26)], fill=WHITE)
    for i, ln in enumerate(lines):
        xx = x + 36
        for p, hl in parts(ln):
            d.text((xx, y + 24 + i * 54), p, font=f, fill=(200, 150, 0) if hl else (12, 12, 14))
            xx += d.textlength(p, font=f)
    return y + h


def k_quote(im, s):
    d = ImageDraw.Draw(im)
    y = tag(d, s["_y0"], s["sub"]) + 60
    b = [x if isinstance(x, dict) else {"t": x} for x in s["bubbles"]]
    if s.get("face"):
        fc = face_img(s["face"], 200, s.get("face_crop"))
        im.paste(fc, (110, y))
        d = ImageDraw.Draw(im)
        d.text((110, y + fc.height + 14), s["name"], font=F("Black", 34), fill=WHITE)
        if s.get("role"):
            d.text((110, y + fc.height + 58), s["role"], font=F("Medium", 24), fill=MU)
        by = bubble(im, 370, y + 40, 600, b[0]["t"])
        end = max(by, y + fc.height + 100)
        if len(b) > 1:
            end = bubble(im, 110, end + 60, 680, b[1]["t"], tail_left=False)
    else:
        end = y - 30
        for i, q in enumerate(b[:2]):
            left = i % 2 == 0
            x = 110 if left else 250
            if q.get("who"):
                d = ImageDraw.Draw(im)
                f = F("Black", 30)
                tw = d.textlength(q["who"], font=f)
                wx = x + 40 if left else x + 720 - 40 - tw
                d.text((wx, end + 30), q["who"], font=f, fill=YE)
                end += 44
            end = bubble(im, x, end + 50, 720, q["t"], tail_left=left)
    return im, footer(im, s, end + 60)


def k_reports(im, s):
    d = ImageDraw.Draw(im)
    y = tag(d, s["_y0"], s["sub"]) + 50
    for r in s["rows"]:
        h = 132
        im = panel(im, (90, y, 990, y + h), r=10)
        d = ImageDraw.Draw(im)
        for i, ln in enumerate(r["m"].split("\n")):
            d.text((122, y + 34 + i * 38), ln, font=F("Black", 28), fill=YE)
        d.text((300, y + 30), r["t"], font=F("Black", 34), fill=WHITE)
        if r.get("s"):
            d.text((300, y + 80), r["s"], font=F("Medium", 24), fill=MU)
        y += h + 18
    return im, footer(im, s, y + 40)


def k_capture(im, s):
    d = ImageDraw.Draw(im)
    y = tag(d, s["_y0"], s["sub"]) + 40
    cap = Image.open(s["cap"]).convert("RGB")
    if s.get("cap_crop"):
        cap = cap.crop(tuple(s["cap_crop"]))
    bw = s.get("cap_w", 860)  # 긴 캡처를 통째로 넣을 땐 폭을 줄인다
    cap = cap.resize((bw, round(cap.height * bw / cap.width)), Image.LANCZOS)
    cap = cap.crop((0, 0, bw, min(cap.height, s.get("cap_max_h", 620))))
    mask = Image.new("L", cap.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, cap.width - 1, cap.height - 1), 14, fill=255)
    cx0 = (W - bw) // 2
    im.paste(cap, (cx0, y), mask)
    if s.get("stamp"):
        f = F("Black", 34)
        w = round(ImageDraw.Draw(im).textlength(s["stamp"], font=f)) + 44
        st = Image.new("RGBA", (w, 66), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rounded_rectangle((0, 0, w - 1, 65), 8, fill=(12, 12, 14, 235), outline=YE, width=4)
        sd.text((22, 10), s["stamp"], font=f, fill=YE)
        st = st.rotate(6, expand=True, resample=Image.BICUBIC)
        im.paste(st, (cx0 + bw - st.width + 30, y - 34), st)
    return im, footer(im, s, y + cap.height + 60)


KINDS = {"number": k_number, "versus": k_versus, "bars": k_bars, "timeline": k_timeline,
         "quote": k_quote, "reports": k_reports, "capture": k_capture}


def main():
    for s in json.load(open(sys.argv[1], encoding="utf-8")):
        s["_y0"] = 200  # 1차로 그려 높이를 잰 뒤 세로 가운데로 다시 그림
        _, end = KINDS[s["kind"]](background(s.get("bg")), s)
        s["_y0"] = max(90, round((1250 - (end - 200)) / 2))
        im, _ = KINDS[s["kind"]](background(s.get("bg")), s)
        logo(im, 0, H - 78, 40, center=True)
        Path(s["out"]).parent.mkdir(parents=True, exist_ok=True)
        im.save(s["out"], quality=93)
        print(s["out"])


if __name__ == "__main__":
    main()
