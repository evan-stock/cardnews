"""20261109-jensenletter: 젠슨 황 사내 사과 메일 장별 카드(메일 원문 일부 + 번역 + 해설). 1080x1350, 디자인 v2 색·글꼴.
원문: Axios·NBC·Tom's Hardware 공개(2026.11.08 현지). 번역 오늘의쓸모.
사용: python media/20261109-jensenletter/build_cards.py
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "scripts"))
from xpost_cards import W, H, P, BG, FG, MU, YE, LN, BOX, F, wrap, rich, logo, head  # noqa: E402

OUT = Path(__file__).resolve().parent / "cand"
SRC = "메일 원문 일부 · 출처 Axios·NBC 공개 · 번역 오늘의쓸모"


def rich_lines(d, x, y, lines, font, lh):
    """줄바꿈을 넘어가는 '강조'도 노랗게(따옴표 상태를 줄 사이에 이어 감)."""
    hl = False
    for ln in lines:
        cx = x
        for ch_part in _split_q(ln):
            if ch_part == "'":
                hl = not hl
                continue
            d.text((cx, y), ch_part, font=font, fill=YE if hl else FG)
            cx += d.textlength(ch_part, font=font)
        y += lh
    return y


def _split_q(s):
    out, buf = [], ""
    for c in s:
        if c == "'":
            if buf:
                out.append(buf)
            out.append("'")
            buf = ""
        else:
            buf += c
    if buf:
        out.append(buf)
    return out


def mail_box(im, d, y, en, ko, en_size=36):
    x0, x1 = P, W - P
    inner = x1 - x0 - 72
    fen, fko = F("Medium", en_size), F("SemiBold", 36)
    en_l = wrap(d, en, fen, inner)
    ko_l = wrap(d, ko, fko, inner)
    lh_en, lh_ko = int(en_size * 1.4), 54
    h = 34 + 40 + 24 + 2 + 28 + len(en_l) * lh_en + 26 + 2 + 26 + len(ko_l) * lh_ko + 30
    d.rounded_rectangle((x0, y, x1, y + h), 28, fill=BOX, outline=LN, width=3)
    cx, cy = x0 + 36, y + 34
    # 메일 머리: 보낸 사람 · 받는 사람
    d.text((cx, cy), "From", font=F("SemiBold", 26), fill=MU)
    d.text((cx + 82, cy), "Jensen Huang", font=F("Black", 28), fill=FG)
    tw = d.textlength("To  NVIDIA 전 직원", font=F("SemiBold", 26))
    d.text((x1 - 36 - tw, cy), "To  NVIDIA 전 직원", font=F("SemiBold", 26), fill=MU)
    ty = cy + 40 + 24
    d.line((cx, ty, x1 - 36, ty), fill=LN, width=2)
    ty += 28
    for ln in en_l:
        d.text((cx, ty), ln, font=fen, fill=(205, 208, 214))
        ty += lh_en
    ty += 26
    d.rectangle((cx, ty, cx + 56, ty + 3), fill=YE)
    ty += 2 + 26
    rich_lines(d, cx, ty, ko_l, fko, lh_ko)
    return y + h


def letter_card(name, sub, title, en, ko, label, lines, en_size=36, top=110):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    y = head(d, sub, title, y=top)
    y = mail_box(im, d, y + 6, en, ko, en_size)
    d.text((P, y + 16), SRC, font=F("Medium", 24), fill=MU)
    y += 84
    d.text((P, y), label, font=F("SemiBold", 32), fill=YE)
    y += 56
    for ln in lines:
        y = rich_lines(d, P, y, wrap(d, ln, F("Medium", 34), W - 2 * P), F("Medium", 34), 52)
    if y > H - 100:
        print("경고: 로고와 겹침", name, y)
    logo(im)
    im.save(OUT / f"{name}.jpg", quality=93)
    print(name, "bottom", y)


def missing_card():
    """우리 편집 장: 메일에 없던 3가지."""
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    y = head(d, "메일 전체를 읽어 보면", "사과 메일에 '없던' 것\n세 가지", y=120)
    y += 10
    rows = [
        ("01", "상대 이름", "'앨리스 황'이라는 이름은 한 번도 나오지 않습니다."),
        ("02", "'중국'이라는 단어", "스파이 의혹은 '언론이 제기한 국가안보 우려'로만 적었습니다."),
        ("03", "'물러나겠다'는 말", "대신 '엔비디아에 전적으로 헌신하겠다'고 썼습니다."),
    ]
    for num, head_t, body in rows:
        d.rounded_rectangle((P, y, W - P, y + 236), 26, fill=BOX, outline=LN, width=3)
        d.text((P + 36, y + 30), num, font=F("Black", 64), fill=YE)
        d.text((P + 150, y + 40), head_t, font=F("Black", 46), fill=FG)
        by = y + 118
        rich_lines(d, P + 150, by, wrap(d, body, F("Medium", 32), W - 2 * P - 186), F("Medium", 32), 46)
        y += 236 + 26
    d.text((P, y + 4), "기준: Axios·NBC·Tom's Hardware가 공개한 메일 원문", font=F("Medium", 24), fill=MU)
    logo(im)
    im.save(OUT / "missing3.jpg", quality=93)
    print("missing3 bottom", y)


def cover_crop():
    src = Image.open(OUT / "press20.jpg").convert("RGB")  # 1920x1080, 인물은 오른쪽
    w, h = src.size
    cw = round(h * 4 / 5)
    cx = int(w * 0.64)
    x0 = max(0, min(w - cw, cx - cw // 2))
    im = src.crop((x0, 0, x0 + cw, h)).resize((1080, 1350), Image.LANCZOS)
    im.save(OUT / "cover.jpg", quality=94)
    src2 = Image.open(OUT / "press24.jpg").convert("RGB")
    ImageOps.fit(src2, (1080, 1350), centering=(0.4, 0.3)).save(OUT / "cta_bg.jpg", quality=92)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    cover_crop()
    letter_card(
        "l1_american", "답: 메일 끝에서 두 번째 문단",
        "\"미국인인 것이\n'자랑스럽고 감사합니다'\"",
        "I love our country and our company, and I am committed to protecting NVIDIA "
        "and supporting America's national security. I am proud and grateful to be an American.",
        "나는 우리나라와 회사를 사랑하고, 엔비디아를 지키고 미국의 국가안보를 돕겠습니다. "
        "'미국인인 것이 자랑스럽고 감사합니다.'",
        "왜 눈에 띄나",
        ["불륜 상대는 미 정보당국이 '중국 스파이'로 보는 인물입니다.",
         "이 문장 바로 앞에서 이사회 조사에 '전적으로 협조'하겠다고 썼습니다."],
    )
    letter_card(
        "l2_admit", "메일 원문 ① · 8일(현지) 전 직원에게",
        "\"아내에게 '불충실'했습니다\"",
        "I owe my family and all of you an apology. I was unfaithful to my wife. "
        "My actions hurt her and our children. There is no excuse for what I did.",
        "저는 가족과 여러분 모두에게 사과해야 합니다. 저는 아내에게 불충실했습니다. "
        "제 행동은 아내와 아이들에게 상처를 줬습니다. '변명의 여지가 없습니다.'",
        "첫 문단부터 인정",
        ["메일은 돌려 말하지 않고 '불충실'이라는 단어로 시작합니다.",
         "상대가 누구인지는 메일 어디에도 쓰지 않았습니다."],
        en_size=38, top=200,
    )
    letter_card(
        "l3_family", "메일 원문 ② · 아내와 가족에게",
        "\"사과로 되돌릴 수 없다는 걸\n'압니다'\"",
        "To my wife and family: I love you. I know an apology cannot undo what I have done. "
        "I hope our family will heal and that, over time, I can earn back your trust.",
        "아내와 가족에게. 사랑합니다. 사과로 제가 한 일을 되돌릴 수 없다는 걸 압니다. "
        "시간이 걸려도 '신뢰를 되찾고' 싶습니다.",
        "직원 전체 메일에 쓴 가족 편지",
        ["4만여 명이 받는 회사 메일에", "아내에게 하는 말을 그대로 넣었습니다."],
        top=150,
    )
    letter_card(
        "l4_company", "메일 원문 ③ · 직원·이사회·주주에게",
        "\"엔비디아를 이끄는 건\n내 인생의 '특권'\"",
        "You deserve better from me. Leading NVIDIA is the privilege of my life. "
        "I am fully committed to NVIDIA and will work to earn back your confidence.",
        "여러분은 저에게서 더 나은 모습을 볼 자격이 있습니다. 엔비디아를 이끄는 건 제 인생의 특권입니다. "
        "'엔비디아에 전적으로 헌신'하겠습니다.",
        "물러난다는 말은 없다",
        ["책임에 '미치지 못했다'고 했지만, 자리는 지키겠다는 뜻입니다.",
         "이사회도 그가 CEO를 계속 맡는다고 밝혔습니다."],
    )
    letter_card(
        "l5_privacy", "메일 원문 ④ · 마지막 문단",
        "\"가족에겐 아무 '책임'이\n없습니다\"",
        "My family bears no responsibility for my choices. I do. Please give them privacy.",
        "가족은 제 선택에 아무 책임이 없습니다. 책임은 저에게 있습니다. "
        "'가족의 사생활을 지켜 주십시오.'",
        "메일의 마지막 부탁",
        ["모든 책임은 자신에게 있다며, 가족을 향한 관심을 거둬 달라고 했습니다.",
         "서명은 'Jensen' 한 단어였습니다."],
        en_size=40, top=210,
    )
    missing_card()
