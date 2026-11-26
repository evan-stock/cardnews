"""영상·커뮤니티 캡처 카드 (2026.11.26, 참고 B: ho.ongs_ '닥터 프로스트 이종범' 게시물 안쪽 장 구조를 우리 브랜드로 옮김).
1080x1350. spec.json(리스트)을 받아 장마다 렌더한다. 사용: python scripts/video_cap_card.py spec.json

두 가지 틀
1) "stack" = 영상 두 장면 위아래 꽉 채움(참고 B 2~11장, 특히 8장).
   - 장면 하나 = 1080x675(16:10). 위 0~675, 아래 675~1350, 사이 틈 없음.
   - 말자막: 가운데 정렬, Pretendard ExtraBold 58, 흰 글씨 + 검은 외곽선 3px + 옅은 그림자, 줄간격 78,
     마지막 줄 글자 바닥이 장면 아래에서 55px 위(위 장면 y=620, 아래 장면 y=1295). 한 줄 최대 940px(넘으면 자동 줄바꿈).
     '작은따옴표'는 노랑(#FFD84D) 강조.
   - 출처: 위 장면 오른쪽 아래(오른쪽 여백 30, 글자 바닥 y=655), Pretendard SemiBold 22, 흰색 70% 투명.
   - 로고: today.worthy 왼쪽 위(x=44, y=40, 높이 34, 85% 불투명). 아래 가운데는 자막 자리라 비운다.
   - 장면 아래쪽 1/3에 옅은 검은 그라데이션(자막 가독성).
   - 장면이 하나뿐이면 "stack"에 frames 1개 → 위쪽에만 넣고 아래는 single 틀을 쓰는 게 낫다(경고만 출력).
2) "single" = 캡처 한 장 + 출처 + 굵은 두 줄(참고 B 12장). 영상 한 장면 또는 커뮤니티 글 캡처.
   - 바탕 검정(12,12,14). 캡처 상자 가로 860(x=110~970), 기본 높이 537(영상이면 16:10에 가깝게 잘라 채움).
   - 커뮤니티 캡처(fit "contain"): 가로 860에 맞추고 cap_max_h(기본 640)를 넘으면 위에서부터 자른다. 흰 바탕 캡처면 box_bg 흰색.
   - 모서리 둥글기 18, 테두리 2px (56,58,64). 참고 B는 흰 바탕 + 그림자 + 각진 모서리였지만 검은 바탕에서는 그림자가 안 보여 테두리로 바꿈.
   - 출처: 상자 아래 14px, 오른쪽 정렬(상자 오른쪽 끝 -10), Pretendard Medium 22, 회색(150,156,164).
   - 굵은 줄: 상자 아래 80px부터, 가운데 정렬 Pretendard Black 54, 줄간격 73, 최대 2~3줄. '작은따옴표' 노랑.
   - 영상 한 장면이면 "video"+"t"(+crop), 장면 안 말자막은 "cap_sub"(ExtraBold 46, 바닥 여백 40).
   - 선택 sub: 상자 위 노란 소제목(SemiBold 32, 가운데) — 참고 B엔 없지만 우리 캡처 카드와 맞추려 넣을 수 있게 함.
   - 상자+출처+글 묶음을 세로 가운데(기준 y=675)에 둔다. 로고는 아래 가운데 40px(우리 본문 장과 같음).

spec 예시
[{"kind":"stack","out":"media/x/03.jpg","src":"영상: CBS뉴스(11.22)",
  "frames":[{"video":"media/x/video/v1.mp4","t":2.4,"crop":[150,170,1590,1070],"sub":"그는 '80%'가 슈퍼 천재"},
            {"img":"cand/b.jpg","sub":"나머지 '20%'는\\n말 안 하겠다"}]},
 {"kind":"single","out":"media/x/04.jpg","cap":"cand/tqhot.jpg","cap_crop":[0,1050,860,1360],"fit":"contain",
  "box_bg":[255,255,255],"src":"출처: 더쿠 HOT 게시판(11.25) 화면","title":"줄1\\n'강조' 줄2"}]
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xpost_cards import W, H, BG, MU, YE, LN, F, R  # noqa: E402

FW, FH = 1080, 675  # stack 장면 크기(16:10)
WHITE = (255, 255, 255)


def parts(text):
    """'강조' 조각 나누기 → [(글, 노랑여부)]"""
    import re
    out = []
    for p in re.split(r"('[^']*')", text):
        if p:
            out.append((p.strip("'"), True) if p.startswith("'") and p.endswith("'") and len(p) > 1 else (p, False))
    return out


def plain(text):
    return "".join(p for p, _ in parts(text))


def wrap(d, text, font, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if not cur or d.textlength(plain(t), font=font) <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def fix_quotes(lines):
    """줄바꿈으로 '강조'가 두 줄로 나뉘면 각 줄에서 다시 닫고 연다."""
    out, open_ = [], False
    for ln in lines:
        s = ("'" if open_ else "") + ln
        if s.count("'") % 2 == 1:
            s += "'"
            open_ = True
        else:
            open_ = False
        out.append(s)
    return out


def draw_rich_center(d, cx, y, text, font, stroke=0, base=WHITE):
    w = d.textlength(plain(text), font=font)
    x = cx - w / 2
    for p, hl in parts(text):
        d.text((x, y), p, font=font, fill=YE if hl else base,
               stroke_width=stroke, stroke_fill=(0, 0, 0) if stroke else None)
        x += d.textlength(p, font=font)


def frame_img(fr, size):
    """장면 이미지 얻기: video+t(ffmpeg로 한 장면) 또는 img. crop은 원본 좌표."""
    if fr.get("video"):
        tmp = Path(tempfile.mkdtemp()) / "f.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(fr.get("t", 0)), "-i", fr["video"],
                        "-frames:v", "1", str(tmp)], check=True)
        im = Image.open(tmp).convert("RGB")
    else:
        im = Image.open(fr["img"]).convert("RGB")
    if fr.get("crop"):
        im = im.crop(tuple(fr["crop"]))
    fy = fr.get("fy", 0.5)
    return ImageOps.fit(im, size, Image.LANCZOS, centering=(fr.get("fx", 0.5), fy))


def shade(im, start=0.55, alpha=150):
    """장면 아래쪽 옅은 그라데이션"""
    w, h = im.size
    g = Image.new("L", (1, h), 0)
    for y in range(h):
        v = 0 if y < h * start else int(alpha * ((y - h * start) / (h * (1 - start))) ** 1.3)
        g.putpixel((0, y), v)
    g = g.resize((w, h))
    black = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(black, im, g)


def subtitle(im, text, bottom, size=58):
    """장면 위 말자막: 마지막 줄 글자 바닥이 bottom에 오게. single 틀에서는 size 46·줄간격 비례."""
    d = ImageDraw.Draw(im)
    f = F("ExtraBold", size)
    cx = im.width / 2
    lines = fix_quotes(wrap(d, text, f, im.width - 140))
    pitch = round(size * 78 / 58)
    asc = f.getbbox("가")[3]  # 글자 바닥까지 높이
    y0 = bottom - asc - pitch * (len(lines) - 1)
    # 옅은 그림자
    sh = Image.new("L", im.size, 0)
    sd = ImageDraw.Draw(sh)
    for i, ln in enumerate(lines):
        w = sd.textlength(plain(ln), font=f)
        sd.text((cx - w / 2, y0 + i * pitch + 3), plain(ln), font=f, fill=150, stroke_width=6, stroke_fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    im.paste(Image.new("RGB", im.size, (0, 0, 0)), (0, 0), sh)
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        draw_rich_center(d, cx, y0 + i * pitch, ln, f, stroke=3)


def logo(im, x, y, h, alpha=0.85, center=False):
    lg = Image.open(R / "brand/logo_typo_A.png").convert("RGBA")
    lg = lg.resize((round(lg.width * h / lg.height), h), Image.LANCZOS)
    lg.putalpha(lg.split()[3].point(lambda v: int(v * alpha)))
    if center:
        x = (W - lg.width) // 2
    im.paste(lg, (x, y), lg)


def stack(s):
    im = Image.new("RGB", (W, H), BG)
    frs = s["frames"]
    if len(frs) == 1:
        print("경고: 장면이 하나면 single 틀이 낫다")
    for i, fr in enumerate(frs[:2]):
        f = shade(frame_img(fr, (FW, FH)), alpha=fr.get("shade", 150))
        if fr.get("sub"):
            subtitle(f, fr["sub"], FH - 55)
        im.paste(f, (0, i * FH))
    d = ImageDraw.Draw(im)
    if s.get("src"):
        fs = F("SemiBold", 22)
        tw = d.textlength(s["src"], font=fs)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).text((W - 30 - tw, 655 - fs.getbbox("가")[3]), s["src"], font=fs,
                                fill=(255, 255, 255, 180), stroke_width=1, stroke_fill=(0, 0, 0, 120))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    logo(im, 44, 40, 34)
    return im


def single(s):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    bx, bw = 110, 860
    if s.get("video"):
        cap = frame_img(s, (bw, s.get("box_h", 537)))
        if s.get("cap_sub"):  # 참고 B 12장처럼 장면 안 말자막
            cap = shade(cap, alpha=130)
            subtitle(cap, s["cap_sub"], cap.height - 40, size=46)
    else:
        cap = Image.open(s["cap"]).convert("RGB")
        if s.get("cap_crop"):
            cap = cap.crop(tuple(s["cap_crop"]))
        if s.get("fit", "contain") == "cover":
            cap = ImageOps.fit(cap, (bw, s.get("box_h", 537)), Image.LANCZOS)
        else:
            pad = s.get("pad", 0)
            cw = bw - 2 * pad
            ch = round(cap.height * cw / cap.width)
            cap = cap.resize((cw, ch), Image.LANCZOS)
            mh = s.get("cap_max_h", 640)
            if ch + 2 * pad > mh:
                cap = cap.crop((0, 0, cw, mh - 2 * pad))
            box = Image.new("RGB", (bw, cap.height + 2 * pad), tuple(s.get("box_bg", BG)))
            box.paste(cap, (pad, pad))
            cap = box
    bh = cap.height
    ft = F("Black", 54)
    tl = fix_quotes(wrap(d, s.get("title", ""), ft, 900)) if s.get("title") else []
    fsub = F("SemiBold", 32)
    sub_h = 58 if s.get("sub") else 0
    src_h = 14 + 24
    group = sub_h + bh + src_h + (80 - src_h if tl else 0) + (73 * (len(tl) - 1) + 52 if tl else 0)
    y = s.get("top") or round(675 - group / 2)
    if s.get("sub"):
        w = d.textlength(s["sub"], font=fsub)
        d.text((W / 2 - w / 2, y), s["sub"], font=fsub, fill=YE)
        y += sub_h
    r = s.get("radius", 18)
    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, bw - 1, bh - 1), r, fill=255)
    im.paste(cap, (bx, y), mask)
    d.rounded_rectangle((bx, y, bx + bw - 1, y + bh - 1), r, outline=LN, width=2)
    by = y + bh
    if s.get("src"):
        fs = F("Medium", 22)
        tw = d.textlength(s["src"], font=fs)
        d.text((bx + bw - 10 - tw, by + 14), s["src"], font=fs, fill=MU)
    y = by + 80
    for i, ln in enumerate(tl):
        draw_rich_center(d, W / 2, y + i * 73, ln, ft)
    end = y + 73 * (len(tl) - 1) + 52 if tl else by + 40
    if end > H - 100:
        print("경고: 글이 로고와 겹칠 수 있음", end)
    logo(im, 0, H - 78, 40, center=True)
    return im


def main():
    for s in json.load(open(sys.argv[1], encoding="utf-8")):
        im = stack(s) if s.get("kind", "single") == "stack" else single(s)
        Path(s["out"]).parent.mkdir(parents=True, exist_ok=True)
        im.save(s["out"], quality=93)
        print(s["out"])


if __name__ == "__main__":
    main()
