// 얼굴: 매 프레임 숫자(파라미터)로 캔버스에 직접 그린다. 사진 바꿔 끼우기 없음.
import * as THREE from 'three';
export const INK = '#2A1D17';

// 파라미터: eye(뜸 0~1.3), lid(눈꺼풀 기울기 -1~1, +면 처짐), px,py(동공 -1~1), pupil(동공 크기), star(별눈 0/1)
// brow(눈썹 높이 -1~1), browA(기울기 +면 화남 모양), browC(굽음), mw(입 너비 0~1.4), mo(입 벌림 0~1), sm(웃음 -1~1),
// teeth(0~1), tongue(0~1), blush(0~1), sweat(0~1), squint(0~1)
const BASE = { eye: 1, lid: 0, px: 0, py: 0, pupil: 1, star: 0, brow: 0, browA: 0, browC: 0.3, mw: 0.5, mo: 0, sm: 0.15, teeth: 0, tongue: 0, blush: 0, sweat: 0, squint: 0 };
export const EXPR = {
  neutral: {},
  bored: { eye: 0.55, lid: 0.2, brow: -0.3, browC: 0.1, mw: 0.35, sm: -0.1 },
  smug: { eye: 0.6, lid: -0.3, brow: 0.2, browA: -0.3, sm: 0.6, mw: 0.6, px: 0.4 },
  skeptical: { eye: 0.8, brow: 0.1, browA: 0.5, sm: -0.2, mw: 0.35, px: -0.5 },
  shock: { eye: 1.3, pupil: 0.55, brow: 1, browC: 0.6, mo: 0.9, mw: 0.45, sm: 0, teeth: 0.4 },
  scared: { eye: 1.2, pupil: 0.6, brow: 0.8, browA: -0.6, mo: 0.4, mw: 0.7, sm: -0.6, teeth: 1, sweat: 1 },
  starstruck: { eye: 1.15, star: 1, brow: 0.8, mo: 0.6, mw: 0.7, sm: 0.8, blush: 1, tongue: 0.4 },
  sad: { eye: 0.85, lid: 0.5, py: 0.4, brow: 0.3, browA: -0.8, sm: -0.6, mw: 0.45 },
  angry: { eye: 0.9, lid: -0.6, pupil: 0.8, brow: -0.6, browA: 0.9, mo: 0.35, mw: 0.8, sm: -0.5, teeth: 1 },
  happy: { eye: 0.9, squint: 0.5, brow: 0.35, sm: 0.85, mw: 0.75, mo: 0.35, teeth: 0.6, blush: 0.6 },
  slurp: { eye: 0.35, squint: 0.8, brow: 0.4, mo: 0.55, mw: 0.35, sm: 0.3, blush: 0.5 },   // 국물 들이켜기
  thirsty: { eye: 1.1, pupil: 0.7, brow: 0.7, browA: -0.4, mo: 0.75, mw: 0.6, sm: -0.3, tongue: 1, sweat: 1 },
  panic: { eye: 1.25, pupil: 0.5, brow: 1, browA: -0.5, mo: 1, mw: 0.75, sm: -1.1, teeth: 1, sweat: 1 },
  determined: { eye: 0.9, lid: -0.4, brow: -0.2, browA: 0.6, sm: 0.2, mw: 0.5 },
  defeated: { eye: 0.5, lid: 0.6, py: 0.6, brow: -0.2, browA: -0.6, sm: -0.4, mw: 0.4 },
  whistle: { eye: 0.7, px: 0.6, py: -0.6, brow: 0.5, mo: 0.25, mw: 0.12, sm: 0 },
  stunned: { eye: 1.05, pupil: 0.45, brow: 0.2, mo: 0.15, mw: 0.25, sm: 0 },
  relieved: { eye: 0.4, squint: 0.7, brow: 0.3, browA: -0.3, sm: 0.5, mw: 0.55, blush: 0.4 },
  disgust: { eye: 0.7, lid: -0.2, brow: -0.3, browA: 0.4, sm: -0.8, mw: 0.6, mo: 0.2, teeth: 1 },
  wink: { eye: 0.9, sm: 0.7, mw: 0.6, brow: 0.3, blush: 0.4 },
};
export function face(name, over = {}) { return { ...BASE, ...(EXPR[name] || {}), ...over }; }
export function mix(a, b, t) { const o = {}; for (const k in BASE) o[k] = a[k] + (b[k] - a[k]) * t; return o; }
// 눈썹이 먼저, 입이 뒤따름. 2프레임 기대(반대로 살짝), 10% 오버슈트, 안착.
export function morph(a, b, t /*0..1 정도 경과(초 단위 아님)*/) {
  const ease = (x) => { if (x <= 0) return 0; if (x >= 1) return 1; const s = 1.70158 * 0.6; return 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2); };
  const o = {};
  for (const k in BASE) {
    const lead = /brow|eye|lid|px|py|pupil|squint|star/.test(k) ? 0 : 0.18;
    let x = (t - lead) / (1 - lead);
    const ant = x < 0 && x > -0.25 ? -0.08 * Math.sin((-x / 0.25) * Math.PI) : 0; // 기대 동작
    o[k] = a[k] + (b[k] - a[k]) * (x < 0 ? ant : ease(x));
  }
  return o;
}

// 얼굴 캔버스 → 머리 앞쪽 구면 조각에 붙인다
export function makeFace(headR, opts = {}) {
  const S = 512, cv = document.createElement('canvas'); cv.width = cv.height = S;
  const g = cv.getContext('2d'); const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const span = opts.span || 1.25; // 라디안 범위
  const geo = new THREE.SphereGeometry(headR * 1.004, 48, 48, Math.PI / 2 - span / 2, span, Math.PI / 2 - span / 2, span);
  const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map: tex, transparent: true, roughness: 0.9, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2 }));
  mesh.renderOrder = 2;
  let last = '';
  function draw(p, t = 0, blinkAmt = 0) {
    const key = JSON.stringify(p) + blinkAmt.toFixed(2);
    if (key === last) return; last = key;
    g.clearRect(0, 0, S, S);
    const cx = S / 2, eyeY = S * 0.43 + (opts.eyeY || 0), ex = S * (opts.eyeGap || 0.155);
    g.lineCap = 'round'; g.lineJoin = 'round';
    // 홍조
    if (p.blush > 0.01) for (const sx of [-1, 1]) { const r = g.createRadialGradient(cx + sx * S * 0.27, S * 0.6, 2, cx + sx * S * 0.27, S * 0.6, S * 0.09);
      r.addColorStop(0, `rgba(255,110,120,${0.55 * p.blush})`); r.addColorStop(1, 'rgba(255,110,120,0)'); g.fillStyle = r; g.fillRect(0, 0, S, S); }
    // 눈
    const eh = S * 0.075 * Math.max(0.05, p.eye) * (1 - p.squint * 0.6) * (1 - blinkAmt * 0.95), ew = S * 0.06 * (0.85 + p.eye * 0.15);
    for (const sx of [-1, 1]) {
      const x = cx + sx * ex, y = eyeY;
      g.save(); g.beginPath(); g.ellipse(x, y, ew, eh, 0, 0, Math.PI * 2); g.fillStyle = '#fff'; g.fill();
      g.clip();
      // 동공
      const pr = S * 0.032 * p.pupil, pxx = x + p.px * ew * 0.45, pyy = y + p.py * eh * 0.4;
      if (p.star > 0.5) { star(g, pxx, pyy, pr * 1.6, INK); } else { g.beginPath(); g.arc(pxx, pyy, pr, 0, Math.PI * 2); g.fillStyle = INK; g.fill();
        g.beginPath(); g.arc(pxx + pr * 0.35, pyy - pr * 0.4, pr * 0.32, 0, Math.PI * 2); g.fillStyle = '#fff'; g.fill(); }
      // 눈꺼풀(기울기)
      // 눈꺼풀: 슬픔(lid>0)은 바깥쪽이, 화남(lid<0)은 안쪽이 내려옴
      const inX = x - sx * ew * 1.2, outX = x + sx * ew * 1.2;
      const cIn = Math.max(0, -p.lid) * 0.75, cOut = Math.max(0, p.lid) * 0.75;
      if (cIn + cOut > 0.01) {
        g.beginPath(); g.moveTo(inX, y - eh * 1.3); g.lineTo(outX, y - eh * 1.3);
        g.lineTo(outX, y - eh + 2 * eh * cOut); g.lineTo(inX, y - eh + 2 * eh * cIn); g.closePath();
        g.fillStyle = opts.skin || '#f6dcc6'; g.fill();
        g.beginPath(); g.moveTo(outX, y - eh + 2 * eh * cOut); g.lineTo(inX, y - eh + 2 * eh * cIn); g.strokeStyle = INK; g.lineWidth = S * 0.014; g.stroke();
      }
      g.restore();
      g.beginPath(); g.ellipse(x, y, ew, eh, 0, 0, Math.PI * 2); g.strokeStyle = INK; g.lineWidth = S * 0.012; g.stroke();
      // 눈썹
      const by = eyeY - S * 0.125 - p.brow * S * 0.05, bw = S * 0.075;
      const inBx = x - sx * bw, outBx = x + sx * bw, inBy = by + p.browA * S * 0.035, outBy = by - p.browA * S * 0.035;
      g.beginPath(); g.moveTo(inBx, inBy); g.quadraticCurveTo(x, by - p.browC * S * 0.05, outBx, outBy);
      g.strokeStyle = INK; g.lineWidth = S * 0.026; g.stroke();
    }
    // 입
    const my = S * 0.66 + (opts.mouthY || 0), mw = S * 0.13 * p.mw, mo = S * 0.13 * p.mo, sm = p.sm * S * 0.05;
    if (p.mo < 0.06) { g.beginPath(); g.moveTo(cx - mw, my - sm); g.quadraticCurveTo(cx, my + sm * 1.6, cx + mw, my - sm); g.strokeStyle = INK; g.lineWidth = S * 0.018; g.stroke(); }
    else {
      g.beginPath(); g.moveTo(cx - mw, my - sm); g.quadraticCurveTo(cx, my - sm * 0.2 - mo * 0.15, cx + mw, my - sm);
      g.quadraticCurveTo(cx + mw * 0.6, my + mo + sm * 0.4, cx, my + mo * 1.05 + sm * 0.6); g.quadraticCurveTo(cx - mw * 0.6, my + mo + sm * 0.4, cx - mw, my - sm);
      g.closePath(); g.fillStyle = '#5a1f22'; g.fill();
      g.save(); g.clip();
      if (p.teeth > 0.05) { g.fillStyle = '#fff'; g.globalAlpha = p.teeth; g.fillRect(cx - mw, my - sm - mo * 0.3, mw * 2, mo * 0.32 + S * 0.012); g.globalAlpha = 1; }
      if (p.tongue > 0.05) { g.beginPath(); g.ellipse(cx, my + mo * 0.95, mw * 0.55, mo * 0.45 * p.tongue + 2, 0, 0, Math.PI * 2); g.fillStyle = '#e8737c'; g.fill(); }
      g.restore();
      g.strokeStyle = INK; g.lineWidth = S * 0.016; g.stroke();
    }
    // 땀
    if (p.sweat > 0.05) { const x = cx + S * 0.33, y = S * 0.3; g.globalAlpha = p.sweat; g.beginPath(); g.moveTo(x, y - S * 0.05);
      g.quadraticCurveTo(x + S * 0.035, y + S * 0.01, x, y + S * 0.03); g.quadraticCurveTo(x - S * 0.035, y + S * 0.01, x, y - S * 0.05);
      g.fillStyle = '#9fd3ff'; g.fill(); g.strokeStyle = INK; g.lineWidth = S * 0.008; g.stroke(); g.globalAlpha = 1; }
    tex.needsUpdate = true;
  }
  return { mesh, draw };
}
function star(g, x, y, r, c) { g.beginPath(); for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r; g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } g.closePath(); g.fillStyle = '#ffc93c'; g.fill(); g.strokeStyle = c; g.lineWidth = r * 0.18; g.stroke(); }
