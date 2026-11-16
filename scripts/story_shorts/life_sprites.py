# 댓글로 키우는 아이 — 캐릭터·배경 SVG 원본 (2026.10.23 v2: 투박하다는 피드백으로 SVG 그라데이션·그림자 방식)
# 모든 화가 이 파일을 같이 써서 김댓글 얼굴이 항상 같다. 그림은 ffmpeg(librsvg)로 PNG로 바꾼다.
import os, subprocess
from PIL import Image

OL = "#5b3a29"   # 외곽선(따뜻한 갈색)
DEFS = f"""<defs>
 <radialGradient id="skin" cx="42%" cy="38%" r="70%"><stop offset="0" stop-color="#fff3e8"/><stop offset=".7" stop-color="#ffdcc4"/><stop offset="1" stop-color="#f4bf9c"/></radialGradient>
 <linearGradient id="mint" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c8f3e6"/><stop offset="1" stop-color="#86d3bd"/></linearGradient>
 <linearGradient id="navy" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4f6fae"/><stop offset="1" stop-color="#344d85"/></linearGradient>
 <linearGradient id="coral" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffab95"/><stop offset="1" stop-color="#f2826c"/></linearGradient>
 <linearGradient id="jeo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff2a8"/><stop offset="1" stop-color="#ffd86a"/></linearGradient>
 <linearGradient id="chima" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff8fb1"/><stop offset="1" stop-color="#ec5f8c"/></linearGradient>
 <linearGradient id="hairB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5e4334"/><stop offset="1" stop-color="#3a271e"/></linearGradient>
 <filter id="sh" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#6b3b20" flood-opacity=".22"/></filter>
</defs>"""

def eyes(expr, cx=200, cy=205):
    out = ""
    for s in (-1, 1):
        x = cx + s * 58
        if expr in ("happy", "o", "proud"):
            out += (f'<ellipse cx="{x}" cy="{cy}" rx="19" ry="24" fill="#3b2a22"/>'
                    f'<circle cx="{x-6}" cy="{cy-9}" r="7.5" fill="#fff"/><circle cx="{x+7}" cy="{cy+8}" r="3.5" fill="#fff" opacity=".85"/>')
        elif expr == "blink":
            out += f'<path d="M{x-20} {cy+2} Q{x} {cy+16} {x+20} {cy+2}" stroke="#3b2a22" stroke-width="7" fill="none" stroke-linecap="round"/>'
        elif expr == "cry":
            d = -s
            out += (f'<path d="M{x-d*18} {cy-14} L{x+d*16} {cy} L{x-d*18} {cy+14}" stroke="#3b2a22" stroke-width="8" '
                    f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return out

def mouth(expr, cx=200, cy=262):
    if expr in ("happy", "blink"):
        return f'<path d="M{cx-18} {cy} Q{cx} {cy+22} {cx+18} {cy}" stroke="#3b2a22" stroke-width="7" fill="none" stroke-linecap="round"/>'
    if expr == "proud":
        return f'<path d="M{cx-26} {cy-4} Q{cx} {cy+34} {cx+26} {cy-4} Z" fill="#c9484f" stroke="#3b2a22" stroke-width="5" stroke-linejoin="round"/><ellipse cx="{cx}" cy="{cy+14}" rx="12" ry="6" fill="#ff8f8f"/>'
    if expr == "o":
        return f'<ellipse cx="{cx}" cy="{cy+6}" rx="12" ry="15" fill="#7a2f35" stroke="#3b2a22" stroke-width="5"/>'
    if expr == "cry":
        return (f'<path d="M{cx-34} {cy-6} Q{cx} {cy-20} {cx+34} {cy-6} Q{cx+30} {cy+42} {cx} {cy+44} Q{cx-30} {cy+42} {cx-34} {cy-6}Z" fill="#b93a45" stroke="#3b2a22" stroke-width="6" stroke-linejoin="round"/>'
                f'<ellipse cx="{cx}" cy="{cy+28}" rx="18" ry="10" fill="#ff8a8a"/>'
                f'<path d="M118 228 q-14 30 -2 44 q14 -6 2 -44z" fill="#8fd3ff" stroke="#3b8fc9" stroke-width="3"/>'
                f'<path d="M282 228 q14 30 2 44 q-14 -6 -2 -44z" fill="#8fd3ff" stroke="#3b8fc9" stroke-width="3"/>')
    return ""

def face(expr, hair="baby", cx=200, cy=200):
    hb = hf = ""
    if hair == "mom":
        hb = (f'<circle cx="{cx+92}" cy="{cy-128}" r="44" fill="url(#hairB)" stroke="{OL}" stroke-width="6"/>'
              f'<path d="M{cx-160} {cy+40} Q{cx-175} {cy-150} {cx} {cy-150} Q{cx+175} {cy-150} {cx+160} {cy+40} Q{cx+150} {cy+90} {cx+120} {cy+80} L{cx-120} {cy+80} Q{cx-150} {cy+90} {cx-160} {cy+40}Z" fill="url(#hairB)" stroke="{OL}" stroke-width="6"/>')
        hf = f'<path d="M{cx-140} {cy-30} Q{cx-110} {cy-140} {cx+10} {cy-130} Q{cx-40} {cy-80} {cx-140} {cy-30}Z" fill="url(#hairB)"/><path d="M{cx+140} {cy-30} Q{cx+110} {cy-140} {cx-10} {cy-130} Q{cx+60} {cy-70} {cx+140} {cy-30}Z" fill="url(#hairB)"/>'
    out = hb
    for s in (-1, 1):  # 귀
        out += f'<circle cx="{cx+s*146}" cy="{cy+18}" r="30" fill="#ffd6bd" stroke="{OL}" stroke-width="6"/>'
    out += f'<ellipse cx="{cx}" cy="{cy}" rx="152" ry="140" fill="url(#skin)" stroke="{OL}" stroke-width="6"/>'
    out += f'<ellipse cx="{cx-60}" cy="{cy-70}" rx="44" ry="22" fill="#fff" opacity=".45" transform="rotate(-20 {cx-60} {cy-70})"/>'
    if hair == "baby":  # 정수리 한 가닥 = 김댓글 트레이드마크
        out += (f'<path d="M{cx-6} {cy-136} C{cx-30} {cy-185} {cx+40} {cy-205} {cx+38} {cy-165} C{cx+36} {cy-140} {cx+8} {cy-148} {cx+16} {cy-166}" '
                f'stroke="{OL}" stroke-width="8" fill="none" stroke-linecap="round"/>')
    elif hair == "dad":
        out += (f'<path d="M{cx-150} {cy-10} Q{cx-160} {cy-150} {cx} {cy-148} Q{cx+165} {cy-150} {cx+150} {cy-10} Q{cx+120} {cy-80} {cx+40} {cy-88} Q{cx-60} {cy-60} {cx-120} {cy-90} Q{cx-140} {cy-60} {cx-150} {cy-10}Z" '
                f'fill="url(#hairB)" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>')
    out += hf + eyes(expr, cx, cy + 5) + mouth(expr, cx, cy + 62)
    for s in (-1, 1):
        out += f'<ellipse cx="{cx+s*92}" cy="{cy+50}" rx="27" ry="16" fill="#ff8e9c" opacity=".55"/>'
    if hair == "dad":  # 안경
        for s in (-1, 1):
            out += f'<rect x="{cx+s*58-34}" y="{cy-22}" width="68" height="58" rx="22" fill="none" stroke="#3b2a22" stroke-width="6"/>'
        out += f'<path d="M{cx-24} {cy+2} Q{cx} {cy-8} {cx+24} {cy+2}" stroke="#3b2a22" stroke-width="6" fill="none"/>'
    return out

def svg(w, h, body, vb=None):
    vb = vb or f"0 0 {w} {h}"
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}">{DEFS}{body}</svg>'

def baby(expr):
    body = (f'<g filter="url(#sh)"><path d="M62 330 Q40 500 200 520 Q360 500 338 330 Q200 290 62 330Z" fill="url(#mint)" stroke="{OL}" stroke-width="6"/>'
            f'<path d="M80 372 Q200 440 322 360" stroke="#5fb9a1" stroke-width="6" fill="none" stroke-linecap="round"/>')
    for x, y in ((120, 450), (200, 470), (280, 445), (160, 410), (250, 415)):
        body += f'<path d="M{x} {y-10} L{x+3} {y-3} L{x+10} {y} L{x+3} {y+3} L{x} {y+10} L{x-3} {y+3} L{x-10} {y} L{x-3} {y-3}Z" fill="#fff" opacity=".85"/>'
    body += face(expr) + "</g>"
    return svg(400, 560, body, "0 -30 400 560")

def toddler(expr):
    b = '<g filter="url(#sh)">'
    b += f'<path d="M80 470 Q70 330 200 320 Q330 330 320 470 Q200 500 80 470Z" fill="url(#chima)" stroke="{OL}" stroke-width="6"/>'  # 아래
    b += f'<path d="M95 410 Q90 320 200 312 Q310 320 305 410 Q200 430 95 410Z" fill="url(#jeo)" stroke="{OL}" stroke-width="6"/>'  # 저고리
    b += f'<path d="M200 330 L170 390 M200 330 L230 390" stroke="{OL}" stroke-width="5"/><path d="M200 380 q-40 10 -30 40 M200 380 q40 10 30 40" stroke="#e8455e" stroke-width="9" fill="none" stroke-linecap="round"/>'
    # 왼팔(고정, 색동 소매)
    cols = ["#ff6b6b", "#ffd166", "#5ad19b", "#5aa9e6", "#c77dff"]
    for i, c in enumerate(cols):
        b += f'<rect x="{58+i*0}" y="{338+i*16}" width="52" height="16" fill="{c}"/>'
    b += f'<rect x="58" y="338" width="52" height="80" rx="10" fill="none" stroke="{OL}" stroke-width="6"/><circle cx="84" cy="430" r="22" fill="#ffdcc4" stroke="{OL}" stroke-width="6"/>'
    b += face(expr) + "</g>"
    return svg(400, 540, b, "0 -40 400 540")

def arm():  # 오른팔: (40,40) 어깨 기준, 오른쪽 아래로 뻗음 → 회전해서 씀
    cols = ["#ff6b6b", "#ffd166", "#5ad19b", "#5aa9e6", "#c77dff", "#ff6b6b"]
    b = '<g>'
    for i, c in enumerate(cols):
        b += f'<rect x="{30+i*26}" y="20" width="26" height="46" fill="{c}"/>'
    b += f'<rect x="30" y="20" width="156" height="46" rx="14" fill="none" stroke="{OL}" stroke-width="6"/><circle cx="208" cy="43" r="27" fill="url(#skin)" stroke="{OL}" stroke-width="6"/></g>'
    return svg(260, 90, b)

def adult(who, expr="happy"):
    b = '<g filter="url(#sh)">'
    if who == "dad":
        b += f'<path d="M50 640 Q40 400 200 380 Q360 400 350 640Z" fill="url(#navy)" stroke="{OL}" stroke-width="6"/>'
        b += f'<path d="M150 384 L200 470 L250 384Z" fill="#fff" stroke="{OL}" stroke-width="5"/><path d="M200 400 L186 420 L200 520 L214 420Z" fill="#e8455e" stroke="{OL}" stroke-width="4"/>'
        b += f'<path d="M150 384 L190 520 M250 384 L210 520" stroke="#25396a" stroke-width="6"/><rect x="262" y="450" width="42" height="12" rx="4" fill="#fff"/>'
        b += face(expr, "dad")
    else:
        b += f'<path d="M50 640 Q40 400 200 380 Q360 400 350 640Z" fill="url(#coral)" stroke="{OL}" stroke-width="6"/>'
        b += f'<path d="M110 430 Q200 410 290 430 L300 640 L100 640Z" fill="#fff" stroke="{OL}" stroke-width="5"/><rect x="160" y="500" width="80" height="56" rx="14" fill="#ffd166" stroke="{OL}" stroke-width="4"/>'
        b += f'<path d="M200 546 C170 524 168 506 186 504 C194 503 200 512 200 516 C200 512 206 503 214 504 C232 506 230 524 200 546Z" fill="#e8455e"/>'
        b += face(expr, "mom")
    b += "</g>"
    return svg(400, 680, b, "0 -40 400 680")

def item(kind):
    if kind == "pencil":
        b = (f'<g filter="url(#sh)" transform="rotate(-12 150 70)"><rect x="40" y="48" width="190" height="44" fill="#ffc94a" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="40" y="48" width="190" height="14" fill="#ffe08a"/><path d="M230 48 L282 70 L230 92Z" fill="#f6d3a8" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
             f'<path d="M266 63 L282 70 L266 77Z" fill="#3b2a22"/><rect x="14" y="48" width="30" height="44" rx="8" fill="#ff9fb3" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="40" y="48" width="12" height="44" fill="#c9c9d6" stroke="{OL}" stroke-width="4"/></g>')
        return svg(300, 150, b)
    if kind == "money":
        b = '<g filter="url(#sh)">'
        for i, (dx, dy, r) in enumerate(((0, 18, -8), (10, 8, 4), (0, 0, -2))):
            b += (f'<g transform="translate({dx} {dy}) rotate({r} 150 75)"><rect x="40" y="25" width="220" height="110" rx="14" fill="#a9e3a1" stroke="{OL}" stroke-width="6"/>'
                  f'<rect x="56" y="40" width="188" height="80" rx="10" fill="none" stroke="#5aa868" stroke-width="4"/><circle cx="150" cy="80" r="26" fill="#d9f5d4" stroke="#5aa868" stroke-width="4"/>'
                  f'<path d="M136 70 l6 22 l8-18 l8 18 l6-22 M134 82 h32" stroke="#3f8a4f" stroke-width="5" fill="none" stroke-linejoin="round"/></g>')
        return svg(300, 170, b + "</g>")
    b = (f'<g filter="url(#sh)" transform="rotate(18 150 110)"><rect x="132" y="110" width="36" height="110" rx="14" fill="#3b3b4a" stroke="{OL}" stroke-width="6"/>'
         f'<rect x="126" y="104" width="48" height="22" rx="8" fill="#ffd166" stroke="{OL}" stroke-width="5"/>'
         f'<circle cx="150" cy="66" r="50" fill="#c8ccd8" stroke="{OL}" stroke-width="6"/>'
         f'<path d="M108 50 h84 M104 70 h92 M110 90 h80 M130 22 v88 M150 18 v96 M170 22 v88" stroke="#9aa0b4" stroke-width="4"/>'
         f'<ellipse cx="132" cy="44" rx="14" ry="8" fill="#fff" opacity=".7"/></g>')
    return svg(300, 240, b)

def card(w, h, head_col):
    b = (f'<g filter="url(#sh)"><rect x="20" y="20" width="{w-40}" height="{h-40}" rx="36" fill="#fffdf8" stroke="{OL}" stroke-width="6"/>'
         f'<path d="M20 56 Q20 20 56 20 L{w-56} 20 Q{w-20} 20 {w-20} 56 L{w-20} 120 L20 120Z" fill="{head_col}" stroke="{OL}" stroke-width="6"/></g>')
    return svg(w, h, b)

# ---------- 배경 1080x1490 ----------
def _wall(top, bot, extra=""):
    return f'<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient>{extra}'

def bg_nursery():
    b = f'<defs>{_wall("#fff1e2", "#ffe2cf")}</defs><rect width="1080" height="1490" fill="url(#wall)"/>'
    for y in range(40, 1150, 110):
        for x in range(30 + (y // 110 % 2) * 60, 1080, 120):
            b += f'<circle cx="{x}" cy="{y}" r="7" fill="#ffd2bd"/>'
    # 창문 + 구름
    b += (f'<rect x="680" y="60" width="330" height="300" rx="30" fill="#bfe6ff" stroke="#e8c3a8" stroke-width="14"/><path d="M845 60 v300 M680 210 h330" stroke="#e8c3a8" stroke-width="10"/>'
          f'<g fill="#fff"><circle cx="750" cy="150" r="26"/><circle cx="780" cy="140" r="34"/><circle cx="812" cy="152" r="24"/><circle cx="910" cy="290" r="22"/><circle cx="935" cy="282" r="28"/><circle cx="962" cy="292" r="20"/></g>')
    # 모빌
    b += f'<path d="M180 0 v80 M100 80 h160 M100 80 v50 M180 80 v80 M260 80 v40" stroke="#c9a08a" stroke-width="4"/>'
    for x, y, c in ((100, 140, "#ffd166"), (180, 170, "#8fd3ff"), (260, 130, "#ff9fb3")):
        b += f'<path d="M{x} {y-22} L{x+7} {y-7} L{x+23} {y-5} L{x+11} {y+6} L{x+14} {y+22} L{x} {y+14} L{x-14} {y+22} L{x-11} {y+6} L{x-23} {y-5} L{x-7} {y-7}Z" fill="{c}"/>'
    b += '<rect y="1130" width="1080" height="360" fill="#f3cfa9"/><rect y="1130" width="1080" height="14" fill="#e3b78e"/>'
    for x in range(0, 1080, 180):
        b += f'<path d="M{x} 1144 v346" stroke="#e8c09a" stroke-width="4"/>'
    return svg(1080, 1490, b)

def bg_living():
    b = f'<defs>{_wall("#effaf3", "#dff2e7")}</defs><rect width="1080" height="1490" fill="url(#wall)"/>'
    for x in range(0, 1080, 60):
        b += f'<rect x="{x}" y="0" width="30" height="1130" fill="#e6f6ec"/>'
    b += (f'<rect x="420" y="60" width="240" height="170" rx="16" fill="#fff" stroke="#c9b29a" stroke-width="12"/><path d="M440 210 l60 -70 l40 40 l40 -60 l60 90Z" fill="#9ed6a5"/><circle cx="610" cy="110" r="18" fill="#ffd166"/>'
          f'<rect y="1130" width="1080" height="360" fill="#e9c7a1"/><rect y="1130" width="1080" height="14" fill="#d8af84"/>')
    b += '<g><rect x="930" y="980" width="90" height="150" rx="18" fill="#f2a47c" stroke="#5b3a29" stroke-width="5"/><ellipse cx="975" cy="930" rx="70" ry="80" fill="#6cc78a"/><ellipse cx="940" cy="900" rx="34" ry="50" fill="#8fdba4"/></g>'
    return svg(1080, 1490, b)

def bg_dol():
    b = f'<defs>{_wall("#fff6dc", "#ffe9bf")}</defs><rect width="1080" height="1490" fill="url(#wall)"/>'
    cols = ["#ff8fa3", "#ffd166", "#7ed6a7", "#7cc4f5", "#c9a2ff"]
    for i, x in enumerate(range(-40, 1120, 120)):  # 색동 커튼 줄
        b += f'<rect x="{x}" y="0" width="60" height="1130" fill="{cols[i % 5]}" opacity=".16"/>'
    b += '<path d="M0 0 h1080 v40 ' + "".join(f'q-{45} 60 -90 0 ' for _ in range(12)) + 'Z" fill="#ff8fa3"/>'
    for i, x in enumerate(range(60, 1080, 120)):  # 가랜드
        b += f'<path d="M{x-34} 70 L{x+34} 70 L{x} 130Z" fill="{cols[i % 5]}" stroke="#fff" stroke-width="4"/>'
    for x, y, c in ((90, 330, "#ff8fa3"), (150, 260, "#ffd166"), (990, 300, "#7cc4f5"), (930, 380, "#c9a2ff")):  # 풍선
        b += f'<path d="M{x} {y+70} q-10 60 10 120" stroke="#c9a08a" stroke-width="3" fill="none"/><ellipse cx="{x}" cy="{y}" rx="52" ry="64" fill="{c}"/><ellipse cx="{x-18}" cy="{y-24}" rx="12" ry="18" fill="#fff" opacity=".5"/>'
    b += '<rect y="1130" width="1080" height="360" fill="#e8b98c"/><rect y="1130" width="1080" height="14" fill="#d39e6e"/>'
    return svg(1080, 1490, b)

def bg_vote():
    b = '<defs><radialGradient id="rg" cx="50%" cy="30%" r="80%"><stop offset="0" stop-color="#fff7d6"/><stop offset="1" stop-color="#ffd9a8"/></radialGradient></defs><rect width="1080" height="1490" fill="url(#rg)"/>'
    import random
    r = random.Random(4); cols = ["#ff8fa3", "#ffd166", "#7ed6a7", "#7cc4f5", "#c9a2ff"]
    for _ in range(70):
        x, y, a = r.randrange(1080), r.randrange(1490), r.randrange(180)
        b += f'<rect x="{x}" y="{y}" width="18" height="9" rx="3" fill="{r.choice(cols)}" transform="rotate({a} {x} {y})" opacity=".8"/>'
    return svg(1080, 1490, b)

def table():
    b = (f'<g filter="url(#sh)"><rect x="20" y="20" width="1000" height="70" rx="20" fill="#d9483f" stroke="{OL}" stroke-width="6"/>'
         f'<rect x="40" y="88" width="960" height="140" rx="16" fill="#c8823f" stroke="{OL}" stroke-width="6"/><rect x="40" y="88" width="960" height="20" fill="#b06e30"/>'
         f'<rect x="90" y="226" width="44" height="60" fill="#a8652d" stroke="{OL}" stroke-width="5"/><rect x="906" y="226" width="44" height="60" fill="#a8652d" stroke="{OL}" stroke-width="5"/></g>')
    return svg(1040, 300, b)

CACHE = None
def render_all(cache_dir):
    """모든 그림을 PNG로 만들어 dict 로 돌려준다(scale: 화면 기준 배율)."""
    os.makedirs(cache_dir, exist_ok=True)
    spec = {
        "baby_happy": (baby("happy"), 1.0), "baby_blink": (baby("blink"), 1.0), "baby_cry": (baby("cry"), 1.0), "baby_o": (baby("o"), 1.0),
        "tod_o": (toddler("o"), 1.0), "tod_blink": (toddler("blink"), 1.0), "tod_proud": (toddler("proud"), 1.0), "arm": (arm(), 1.0),
        "dad": (adult("dad"), 1.0), "dad_blink": (adult("dad", "blink"), 1.0), "mom": (adult("mom"), 1.0), "mom_blink": (adult("mom", "blink"), 1.0),
        "pencil": (item("pencil"), 1.0), "money": (item("money"), 1.0), "mic": (item("mic"), 1.0),
        "card_birth": (card(620, 560, "#ff9fae"), 1.0), "card_bank": (card(760, 330, "#7cc4f5"), 1.0), "table": (table(), 1.0),
        "bg_nursery": (bg_nursery(), 1.0), "bg_living": (bg_living(), 1.0), "bg_dol": (bg_dol(), 1.0), "bg_vote": (bg_vote(), 1.0),
    }
    out = {}
    for k, (s, _) in spec.items():
        p = os.path.join(cache_dir, k + ".svg"); png = p[:-4] + ".png"
        open(p, "w", encoding="utf-8").write(s)
        import re
        w, h = re.search(r'width="(\d+)" height="(\d+)"', s.split(">", 1)[0] + ">").groups()
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-width", w, "-height", h, "-i", p, "-frames:v", "1", png], check=True)
        out[k] = Image.open(png).convert("RGBA")
    return out
