# 댓글로 키우는 아이 — 캐릭터 시안 비교판 (2026.10.23). 시안마다 아기·초등학생·어른 3단계 + 우는 얼굴.
import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import life_sprites as L
from life_sprites import OL, eyes, mouth, face, svg

EXTRA = """<defs>
 <radialGradient id="bear" cx="42%" cy="38%" r="70%"><stop offset="0" stop-color="#d8a679"/><stop offset="1" stop-color="#a8703f"/></radialGradient>
 <radialGradient id="mochi" cx="40%" cy="30%" r="75%"><stop offset="0" stop-color="#ffffff"/><stop offset=".75" stop-color="#fbf4ec"/><stop offset="1" stop-color="#ecdccb"/></radialGradient>
 <linearGradient id="shirtY" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe27a"/><stop offset="1" stop-color="#ffc83d"/></linearGradient>
</defs>"""

def body(kind, cx=200, top=318):
    if kind == "baby":
        return (f'<path d="M62 {top+12} Q40 {top+182} {cx} {top+202} Q360 {top+182} 338 {top+12} Q{cx} {top-28} 62 {top+12}Z" fill="url(#mint)" stroke="{OL}" stroke-width="6"/>'
                f'<path d="M80 {top+54} Q{cx} {top+122} 322 {top+42}" stroke="#5fb9a1" stroke-width="6" fill="none" stroke-linecap="round"/>')
    if kind == "kid":
        s = f'<path d="M80 {top+210} Q70 {top+20} {cx} {top} Q330 {top+20} 320 {top+210}Z" fill="url(#shirtY)" stroke="{OL}" stroke-width="6"/>'
        for y in (top + 70, top + 130):
            s += f'<path d="M86 {y} Q{cx} {y+14} 314 {y}" stroke="#ff9f43" stroke-width="12" fill="none"/>'
        s += f'<path d="M110 {top+10} L110 {top+210} M290 {top+10} L290 {top+210}" stroke="#4f8ef7" stroke-width="18"/>'  # 책가방 끈
        return s
    return (f'<path d="M60 {top+222} Q48 {top+20} {cx} {top} Q352 {top+20} 340 {top+222}Z" fill="url(#navy)" stroke="{OL}" stroke-width="6"/>'
            f'<path d="M150 {top+4} L{cx} {top+90} L250 {top+4}Z" fill="#fff" stroke="{OL}" stroke-width="5"/><path d="M{cx} {top+20} L186 {top+40} L{cx} {top+140} L214 {top+40}Z" fill="#e8455e" stroke="{OL}" stroke-width="4"/>')

def bear_face(expr, cx=200, cy=200):
    s = ""
    for sx in (-1, 1):
        s += f'<circle cx="{cx+sx*112}" cy="{cy-112}" r="50" fill="url(#bear)" stroke="{OL}" stroke-width="6"/><circle cx="{cx+sx*112}" cy="{cy-112}" r="24" fill="#f3c9a2"/>'
    s += f'<ellipse cx="{cx}" cy="{cy}" rx="152" ry="140" fill="url(#bear)" stroke="{OL}" stroke-width="6"/>'
    s += f'<ellipse cx="{cx-60}" cy="{cy-70}" rx="40" ry="20" fill="#fff" opacity=".3" transform="rotate(-20 {cx-60} {cy-70})"/>'
    s += f'<ellipse cx="{cx}" cy="{cy+62}" rx="66" ry="50" fill="#f6dcc0" stroke="{OL}" stroke-width="5"/>'
    s += eyes(expr, cx, cy - 5) + f'<ellipse cx="{cx}" cy="{cy+40}" rx="18" ry="12" fill="#3b2a22"/>' + mouth(expr, cx, cy + 70)
    for sx in (-1, 1):
        s += f'<ellipse cx="{cx+sx*100}" cy="{cy+42}" rx="24" ry="14" fill="#ff8e9c" opacity=".5"/>'
    return s

def toon_face(expr, cx=200, cy=210):
    # 웹툰 2등신: 덥수룩한 앞머리 + 큰 눈
    s = f'<ellipse cx="{cx}" cy="{cy}" rx="140" ry="135" fill="url(#skin)" stroke="{OL}" stroke-width="6"/>'
    s += (f'<path d="M{cx-150} {cy+10} Q{cx-170} {cy-170} {cx} {cy-160} Q{cx+175} {cy-170} {cx+150} {cy+10} '
          f'L{cx+120} {cy-40} L{cx+90} {cy-10} L{cx+60} {cy-60} L{cx+20} {cy-20} L{cx-20} {cy-70} L{cx-60} {cy-20} L{cx-100} {cy-60} L{cx-125} {cy-5}Z" '
          f'fill="#2b2b3a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>')
    s += f'<path d="M{cx+20} {cy-158} q30 -50 70 -30" stroke="#2b2b3a" stroke-width="16" fill="none" stroke-linecap="round"/>'
    if expr in ("happy", "o"):
        for sx in (-1, 1):
            x = cx + sx * 55
            s += (f'<ellipse cx="{x}" cy="{cy+20}" rx="26" ry="34" fill="#2b2b3a"/><ellipse cx="{x}" cy="{cy+30}" rx="18" ry="20" fill="#6a5acd" opacity=".6"/>'
                  f'<circle cx="{x-8}" cy="{cy+8}" r="10" fill="#fff"/><circle cx="{x+9}" cy="{cy+34}" r="4" fill="#fff"/>')
    else:
        s += eyes(expr, cx, cy + 20)
    s += mouth(expr, cx, cy + 78)
    for sx in (-1, 1):
        s += f'<path d="M{cx+sx*95-18} {cy+62} l12 -10 M{cx+sx*95-4} {cy+64} l12 -10 M{cx+sx*95+10} {cy+66} l12 -10" stroke="#ff7b8b" stroke-width="5" stroke-linecap="round"/>'
    return s

def mochi(age, expr):
    s = f'<g filter="url(#sh)"><path d="M48 520 C30 330 100 150 200 150 C300 150 370 330 352 520 Q200 548 48 520Z" fill="url(#mochi)" stroke="{OL}" stroke-width="6"/>'
    s += f'<path d="M200 152 q-6 -40 -40 -56 q34 -4 44 30 q10 -40 50 -40 q-20 30 -50 62" fill="#7ed6a7" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
    s += f'<ellipse cx="140" cy="230" rx="36" ry="18" fill="#fff" transform="rotate(-25 140 230)"/>'
    s += eyes(expr, 200, 345) + mouth(expr, 200, 395).replace('cy="', 'cy="')
    for sx in (-1, 1):
        s += f'<ellipse cx="{200+sx*95}" cy="{392}" rx="28" ry="16" fill="#ffb3bd" opacity=".75"/>'
    if age == "baby":
        s += f'<path d="M110 460 Q200 520 290 460 L290 500 Q200 530 110 500Z" fill="#8fd8c4" stroke="{OL}" stroke-width="5"/><circle cx="200" cy="482" r="10" fill="#fff"/>'
    elif age == "kid":
        s += f'<path d="M110 170 Q200 120 290 170 L300 200 Q200 170 100 200Z" fill="#ffd166" stroke="{OL}" stroke-width="5"/><rect x="40" y="380" width="40" height="110" rx="14" fill="#4f8ef7" stroke="{OL}" stroke-width="5"/><rect x="320" y="380" width="40" height="110" rx="14" fill="#4f8ef7" stroke="{OL}" stroke-width="5"/>'
    else:
        s += f'<path d="M200 440 L184 462 L200 530 L216 462Z" fill="#e8455e" stroke="{OL}" stroke-width="4"/><path d="M170 432 h60" stroke="#fff" stroke-width="14" stroke-linecap="round"/>'
    return svg(400, 560, s + "</g>", "0 0 400 560")

def human(face_fn, age, expr):
    top = {"baby": 318, "kid": 318, "adult": 318}[age]
    b = '<g filter="url(#sh)">' + body(age, top=top) + face_fn(expr) + "</g>"
    return svg(400, 560, b, "0 -20 400 560")

def a_face(expr): return face(expr, "baby")
OPTIONS = [
    ("A안 동글 아기 (지금)", lambda age, e: human(a_face, age, e) if age != "baby" else L.baby(e)),
    ("B안 아기 곰 '댓곰이'", lambda age, e: human(bear_face, age, e)),
    ("C안 찹쌀떡 '말랑이'", lambda age, e: mochi(age, e)),
    ("D안 웹툰 2등신", lambda age, e: human(toon_face, age, e)),
]

def main(out):
    os.makedirs(out, exist_ok=True)
    font = ImageFont.truetype(os.path.join(L.__file__.rsplit("/scripts", 1)[0], "assets/fonts/Jua-Regular.ttf"), 58)
    small = ImageFont.truetype(os.path.join(L.__file__.rsplit("/scripts", 1)[0], "assets/fonts/Jua-Regular.ttf"), 40)
    cw, ch = 300, 420
    sheet = Image.new("RGB", (80 + 4 * cw, 140 + len(OPTIONS) * (ch + 90)), (255, 249, 238)); d = ImageDraw.Draw(sheet)
    for j, lab in enumerate(("아기", "초등학생", "어른", "울 때")):
        d.text((80 + j * cw + cw / 2, 70), lab, font=small, fill=(140, 110, 90), anchor="mm")
    for i, (name, fn) in enumerate(OPTIONS):
        y0 = 120 + i * (ch + 90)
        d.text((40, y0 + 20), name, font=font, fill=(91, 58, 41), anchor="lm")
        for j, (age, e) in enumerate((("baby", "happy"), ("kid", "happy"), ("adult", "happy"), ("baby", "cry"))):
            p = f"{out}/opt{i}_{j}.svg"; open(p, "w", encoding="utf-8").write(EXTRA.join(fn(age, e).split("<defs>", 1)).replace("</defs>", "", 1) if False else fn(age, e).replace("</defs>", EXTRA[6:-7] + "</defs>", 1))
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-width", "400", "-height", "560", "-i", p, "-frames:v", "1", p[:-4] + ".png"], check=True)
            im = Image.open(p[:-4] + ".png").convert("RGBA"); im.thumbnail((cw - 20, ch - 20))
            sheet.paste(im, (int(80 + j * cw + (cw - im.width) / 2), y0 + 60), im)
    sheet.save(f"{out}/options.png")

if __name__ == "__main__":
    main(sys.argv[1])
