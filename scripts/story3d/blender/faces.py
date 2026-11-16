# 얼굴 텍스처(PIL): face.js 와 같은 파라미터로 고해상도 PNG 를 그린다(투명 배경).
from PIL import Image, ImageDraw, ImageFilter
INK = (42, 29, 23, 255)
BASE = dict(eye=1, lid=0, px=0, py=0, pupil=1, brow=0, browA=0, browC=0.3, mw=0.5, mo=0, sm=0.15, teeth=0, tongue=0, blush=0, sweat=0, squint=0)
EXPR = {
  'neutral': {}, 'determined': dict(eye=0.9, lid=-0.4, brow=-0.2, browA=0.6, sm=0.2, mw=0.5),
  'slurp': dict(eye=0.35, squint=0.8, brow=0.4, mo=0.55, mw=0.32, sm=0.25, blush=0.6),
  'panic': dict(eye=1.25, pupil=0.5, brow=1, browA=-0.5, mo=1, mw=0.75, sm=-1.1, teeth=1, sweat=1),
}
def face(name, **o): d = dict(BASE); d.update(EXPR.get(name, {})); d.update(o); return d

def quad(p0, c, p1, n=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]) for t in [i / n for i in range(n + 1)]]

def draw(p, path, S=2048, skin=(246, 220, 198), eye_gap=0.135, eye_y=0.43, mouth_y=0.66):
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); bl = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    g = ImageDraw.Draw(im); gb = ImageDraw.Draw(bl)
    cx = S / 2; ey = S * eye_y; ex = S * eye_gap
    if p['blush'] > 0.01:
        for sx in (-1, 1):
            x, y, r = cx + sx * S * 0.25, S * 0.6, S * 0.07
            gb.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(255, 110, 120, int(150 * p['blush'])))
        bl = bl.filter(ImageFilter.GaussianBlur(S * 0.02)); im = Image.alpha_composite(bl, im); g = ImageDraw.Draw(im)
    lw = int(S * 0.012)
    eh = S * 0.075 * max(0.05, p['eye']) * (1 - p['squint'] * 0.6); ew = S * 0.06 * (0.85 + p['eye'] * 0.15)
    for sx in (-1, 1):
        x, y = cx + sx * ex, ey
        if eh < S * 0.02:  # 감은 눈: 곡선
            g.line(quad((x - ew, y), (x, y - eh * 3), (x + ew, y)), fill=INK, width=lw * 2, joint='curve')
        else:
            g.ellipse([x - ew, y - eh, x + ew, y + eh], fill=(255, 255, 255, 255), outline=INK, width=lw)
            pr = S * 0.032 * p['pupil']; px, py = x + p['px'] * ew * 0.45, y + p['py'] * eh * 0.4
            g.ellipse([px - pr, py - pr, px + pr, py + pr], fill=INK)
            hr = pr * 0.33; g.ellipse([px + pr * 0.35 - hr, py - pr * 0.4 - hr, px + pr * 0.35 + hr, py - pr * 0.4 + hr], fill=(255, 255, 255, 255))
            cIn, cOut = max(0, -p['lid']) * 0.75, max(0, p['lid']) * 0.75
            if cIn + cOut > 0.01:
                inX, outX = x - sx * ew * 1.2, x + sx * ew * 1.2
                g.polygon([(inX, y - eh * 1.3), (outX, y - eh * 1.3), (outX, y - eh + 2 * eh * cOut), (inX, y - eh + 2 * eh * cIn)], fill=skin + (255,))
                g.line([(outX, y - eh + 2 * eh * cOut), (inX, y - eh + 2 * eh * cIn)], fill=INK, width=lw)
        by = ey - S * 0.125 - p['brow'] * S * 0.05; bw = S * 0.075
        inB = (x - sx * bw, by + p['browA'] * S * 0.035); outB = (x + sx * bw, by - p['browA'] * S * 0.035)
        g.line(quad(inB, (x, by - p['browC'] * S * 0.05), outB), fill=INK, width=int(S * 0.026), joint='curve')
    my = S * mouth_y; mw = S * 0.13 * p['mw']; mo = S * 0.13 * p['mo']; sm = p['sm'] * S * 0.05
    if p['mo'] < 0.06:
        g.line(quad((cx - mw, my - sm), (cx, my + sm * 1.6), (cx + mw, my - sm)), fill=INK, width=int(S * 0.018), joint='curve')
    else:
        top = quad((cx - mw, my - sm), (cx, my - sm * 0.2 - mo * 0.15), (cx + mw, my - sm))
        bot = quad((cx + mw, my - sm), (cx, my + mo * 1.6 + sm * 0.6), (cx - mw, my - sm))
        g.polygon(top + bot, fill=(90, 31, 34, 255))
        if p['teeth'] > 0.05: g.rectangle([cx - mw * 0.7, my - sm - mo * 0.1, cx + mw * 0.7, my - sm + mo * 0.25], fill=(255, 255, 255, 255))
        if p['tongue'] > 0.05: g.ellipse([cx - mw * 0.5, my + mo * 0.6, cx + mw * 0.5, my + mo * 1.2], fill=(232, 115, 124, 255))
        g.line(top + bot + [top[0]], fill=INK, width=int(S * 0.016), joint='curve')
    if p['sweat'] > 0.05:
        x, y = cx + S * 0.33, S * 0.3
        g.polygon(quad((x, y - S * 0.05), (x + S * 0.05, y + S * 0.02), (x, y + S * 0.03)) + quad((x, y + S * 0.03), (x - S * 0.05, y + S * 0.02), (x, y - S * 0.05)), fill=(159, 211, 255, 255), outline=INK)
    im.save(path)
