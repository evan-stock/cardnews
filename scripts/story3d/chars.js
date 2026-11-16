// 캐릭터: 이 남자(후드 집업 + 사원증), 뇌 관제실장, 콩팥 공장장.
// 공통: 큰 공 머리가 목 없이 몸통 위에, 벙어리장갑 손, 옷 디테일은 평면 페인트 패널(캔버스 텍스처).
import * as THREE from 'three';
import { makeFace, face, INK } from './face.js';

const C = (h) => new THREE.Color(h);
const mat = (c, r = 0.8, extra = {}) => new THREE.MeshStandardMaterial({ color: C(c), roughness: r, ...extra });
const grp = (p, x = 0, y = 0, z = 0) => { const g = new THREE.Group(); g.position.set(x, y, z); p && p.add(g); return g; };
const mesh = (geo, m, p, x = 0, y = 0, z = 0) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; p && p.add(o); return o; };
function canvasTex(w, h, fn) { const c = document.createElement('canvas'); c.width = w; c.height = h; fn(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; }

// 벙어리장갑 손
function mitten(p, m) { const h = grp(p); mesh(new THREE.SphereGeometry(0.11, 20, 16), m, h).scale.set(1, 1.15, 0.8); const th = mesh(new THREE.SphereGeometry(0.05, 12, 10), m, h, 0.075, 0.03, 0.03); th.scale.set(0.9, 1.3, 0.9); return h; }
function limb(p, len, r0, r1, m) { const g = grp(p); const o = mesh(new THREE.CylinderGeometry(r1, r0, len, 16), m, g, 0, -len / 2, 0); mesh(new THREE.SphereGeometry(r0, 16, 12), m, g); return g; }

// 팔: 어깨 그룹(sh) → 팔꿈치(el) → 손(hand)
function arm(parent, side, m, skin, L = 0.36) {
  const sh = grp(parent, side * 0.42, 0.62, 0);
  const up = limb(sh, L, 0.1, 0.09, m);
  const el = grp(sh, 0, -L, 0); mesh(new THREE.SphereGeometry(0.09, 14, 12), m, el);
  limb(el, L * 0.9, 0.09, 0.085, m);
  const cuff = mesh(new THREE.TorusGeometry(0.085, 0.022, 8, 20), m, el, 0, -L * 0.9, 0); cuff.rotation.x = Math.PI / 2;
  const hand = grp(el, 0, -L * 0.9 - 0.08, 0); mitten(hand, skin); hand.scale.x = side;
  return { sh, el, hand };
}
function leg(parent, side, m, shoe, L = 0.5) {
  const hp = grp(parent, side * 0.17, 0, 0);
  limb(hp, L * 0.5, 0.12, 0.11, m);
  const kn = grp(hp, 0, -L * 0.5, 0); limb(kn, L * 0.5, 0.11, 0.105, m);
  const ft = grp(kn, 0, -L * 0.5, 0); const s = mesh(new THREE.SphereGeometry(0.14, 18, 12), shoe, ft, 0, -0.02, 0.06); s.scale.set(0.85, 0.55, 1.35);
  const sole = mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.03, 20), mat('#f2f2f2', 0.6), ft, 0, -0.08, 0.06); sole.scale.set(1, 1, 1.55);
  return { hp, kn, ft };
}

// 공통 포즈 적용: P = {lean, twist, headT(tilt x), headY, headZ, armL:[x,y,z,elbow], armR:[...], legL:[x,knee], legR:[...], bob}
function applyPose(R, P) {
  const g = (v, d = 0) => (v === undefined ? d : v);
  R.hips.position.y = R.hipY + g(P.bob);
  R.torso.rotation.set(g(P.lean), g(P.twist), g(P.side));
  R.head.rotation.set(g(P.headT), g(P.headY), g(P.headZ));
  for (const [k, side] of [['armL', 1], ['armR', -1]]) {
    const a = P[k] || [0, 0, 0, 0], A = R[k];
    A.sh.rotation.set(a[0], a[1] * side, side * (0.12 + a[2]));
    A.el.rotation.set(a[3] || 0, 0, 0);
  }
  for (const [k] of [['legL'], ['legR']]) {
    const l = P[k] || [0, 0], L = R[k];
    L.hp.rotation.set(l[0], 0, 0); L.kn.rotation.set(l[1], 0, 0); L.ft.rotation.set(-(l[0] + l[1]) * 0.5, 0, 0);
  }
}

// ───── 이 남자 ─────
export function makeMan(opts = {}) {
  const SK = '#f6dcc6', HOOD = opts.hood || '#2a9d8f', PANTS = '#2f3a52';
  const skin = mat(SK, 0.75), hood = mat(HOOD, 0.85), pants = mat(PANTS, 0.8), shoe = mat('#3b3f48', 0.6);
  const root = new THREE.Group(); const hipY = 0.52;
  const hips = grp(root, 0, hipY, 0);
  const torso = grp(hips, 0, 0, 0);
  // 몸통: 둥근 병 모양(선반) + 옷 디테일 패널
  const prof = [[0.0, -0.02], [0.3, 0.0], [0.4, 0.08], [0.44, 0.25], [0.45, 0.45], [0.43, 0.62], [0.36, 0.74], [0.22, 0.8], [0.0, 0.82]].map(([x, y]) => new THREE.Vector2(x, y));
  const tex = canvasTex(1024, 512, (g, w, h) => {
    g.fillStyle = HOOD; g.fillRect(0, 0, w, h);
    const cx = w / 2;
    // 밑단 고무단
    g.fillStyle = '#1f7d72'; g.fillRect(0, h * 0.86, w, h * 0.14);
    for (let x = 0; x < w; x += 10) { g.fillStyle = 'rgba(0,0,0,.08)'; g.fillRect(x, h * 0.86, 3, h * 0.14); }
    // 안에 입은 흰 티(목 부분)
    g.fillStyle = '#f4f2ec'; g.beginPath(); g.moveTo(cx - 70, 0); g.lineTo(cx + 70, 0); g.lineTo(cx + 22, h * 0.2); g.lineTo(cx - 22, h * 0.2); g.closePath(); g.fill();
    // 지퍼
    g.strokeStyle = '#1b5e56'; g.lineWidth = 7; g.beginPath(); g.moveTo(cx, h * 0.2); g.lineTo(cx, h * 0.86); g.stroke();
    g.fillStyle = '#c9ced4'; g.fillRect(cx - 7, h * 0.22, 14, 26);
    // 칼라(후드 깃) 테두리
    g.strokeStyle = '#1f7d72'; g.lineWidth = 12; g.beginPath(); g.moveTo(cx - 80, 0); g.lineTo(cx - 6, h * 0.22); g.moveTo(cx + 80, 0); g.lineTo(cx + 6, h * 0.22); g.stroke();
    // 주머니
    g.strokeStyle = '#1f7d72'; g.lineWidth = 8;
    for (const s of [-1, 1]) { g.beginPath(); g.moveTo(cx + s * 40, h * 0.58); g.lineTo(cx + s * 150, h * 0.6); g.lineTo(cx + s * 165, h * 0.82); g.stroke(); }
    // 끈
    g.strokeStyle = '#eaeaea'; g.lineWidth = 6; for (const s of [-1, 1]) { g.beginPath(); g.moveTo(cx + s * 34, h * 0.05); g.lineTo(cx + s * 40, h * 0.34); g.stroke(); }
  });
  const body = mesh(new THREE.LatheGeometry(prof, 40, Math.PI), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.85 }), torso);
  // 머리
  const HR = 0.6;
  const head = grp(torso, 0, 0.8 + HR * 0.88, 0);
  mesh(new THREE.SphereGeometry(HR, 48, 36), skin, head);
  for (const s of [-1, 1]) mesh(new THREE.SphereGeometry(0.12, 16, 12), skin, head, s * HR * 0.98, -0.02, 0).scale.set(0.6, 1, 0.8);
  // 머리카락: 위를 덮는 캡 + 옆가르마 앞머리
  const hairM = mat('#1f1a19', 0.6);
  const cap = mesh(new THREE.SphereGeometry(HR * 1.03, 40, 24, 0, Math.PI * 2, 0, 1.2), hairM, head); cap.rotation.x = -0.42;
  const fr = mesh(new THREE.SphereGeometry(0.2, 20, 12), hairM, head, -0.2, HR * 0.72, HR * 0.5); fr.scale.set(1.6, 0.55, 0.7); fr.rotation.z = 0.35;
  const fr2 = mesh(new THREE.SphereGeometry(0.14, 16, 10), hairM, head, 0.18, HR * 0.8, HR * 0.4); fr2.scale.set(1.5, 0.5, 0.7);
  // 얼굴
  const F = makeFace(HR, { skin: SK, span: 1.75, eyeGap: 0.135, eyeY: 4 }); head.add(F.mesh);
  // 사원증(목걸이 줄 + 카드). 카드 글자는 장면마다 바꿀 수 있음.
  const strapM = mat('#2d6cdf', 0.6);
  const curve = new THREE.CatmullRomCurve3([new THREE.Vector3(-0.2, 0.8, 0.12), new THREE.Vector3(-0.12, 0.64, 0.39), new THREE.Vector3(0, 0.5, 0.475), new THREE.Vector3(0.12, 0.64, 0.39), new THREE.Vector3(0.2, 0.8, 0.12)]);
  mesh(new THREE.TubeGeometry(curve, 40, 0.012, 6), strapM, torso);
  let cardText = opts.card || '사원증';
  const cardCanvas = document.createElement('canvas'); cardCanvas.width = 256; cardCanvas.height = 320;
  const cardTex = new THREE.CanvasTexture(cardCanvas); cardTex.colorSpace = THREE.SRGBColorSpace;
  function drawCard(txt, sub) { const g = cardCanvas.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, 256, 320); g.fillStyle = '#2d6cdf'; g.fillRect(0, 0, 256, 60);
    g.fillStyle = '#fff'; g.font = '900 34px "Noto Sans CJK KR"'; g.textAlign = 'center'; g.fillText('주식회사 보통', 128, 42);
    g.fillStyle = '#dfe6f2'; g.fillRect(70, 80, 116, 120); g.fillStyle = INK; g.beginPath(); g.arc(128, 125, 30, 0, 7); g.fill(); g.fillRect(90, 160, 76, 40);
    g.fillStyle = INK; g.font = `900 ${txt.length > 5 ? 40 : 52}px "Noto Sans CJK KR"`; g.fillText(txt, 128, 262); if (sub) { g.font = '700 26px "Noto Sans CJK KR"'; g.fillText(sub, 128, 302); } cardTex.needsUpdate = true; }
  drawCard(cardText);
  const card = mesh(new THREE.BoxGeometry(0.25, 0.31, 0.012), [mat('#fff'), mat('#fff'), mat('#fff'), mat('#fff'), new THREE.MeshStandardMaterial({ map: cardTex, roughness: 0.5 }), mat('#fff')], torso, 0, 0.36, 0.47);
  card.rotation.x = -0.12;
  // 팔다리
  const armL = arm(torso, 1, hood, skin), armR = arm(torso, -1, hood, skin);
  const legL = leg(hips, 1, pants, shoe), legR = leg(hips, -1, pants, shoe);
  const R = { root, hips, hipY, torso, head, armL, armR, legL, legR };
  let cur = face('neutral');
  return {
    root, R, head, face: F, card, drawCard,
    pose: (P) => applyPose(R, P),
    setFace: (p, blink = 0) => { cur = p; F.draw(p, 0, blink); },
    handR: armR.hand, handL: armL.hand,
  };
}

// ───── 장기 캐릭터 공통 몸(작은 팔다리) ─────
function smallLimbs(parent, m, sy, w) {
  const armL = arm(parent, 1, m, m, 0.22), armR = arm(parent, -1, m, m, 0.22);
  armL.sh.position.set(w, sy, 0); armR.sh.position.set(-w, sy, 0);
  return { armL, armR };
}

// ───── 뇌 관제실장 ─────
export function makeBrain() {
  const PINK = '#f29db0';
  const root = new THREE.Group();
  const hipY = 0.32; const hips = grp(root, 0, hipY, 0); const torso = grp(hips);
  const geo = new THREE.SphereGeometry(0.62, 96, 64);
  const pos = geo.attributes.position, v = new THREE.Vector3();
  for (let i = 0; i < pos.count; i++) {
    v.fromBufferAttribute(pos, i); const n = v.clone().normalize();
    let d = 0.035 * Math.sin(n.x * 18 + Math.sin(n.y * 9) * 2) * Math.sin(n.y * 15 + Math.cos(n.z * 11) * 2) + 0.02 * Math.sin(n.z * 23 + n.x * 7);
    d -= 0.09 * Math.exp(-Math.pow(n.x / 0.06, 2)) * Math.max(0, n.y + 0.2); // 가운데 골
    if (n.z > 0.55 && Math.abs(n.y) < 0.55) d *= 0.25; // 얼굴 자리는 매끈하게
    v.multiplyScalar(1 + d); pos.setXYZ(i, v.x, v.y, v.z);
  }
  geo.computeVertexNormals();
  const head = grp(torso, 0, 0.62, 0);
  const b = mesh(geo, mat(PINK, 0.55), head); b.scale.set(1.12, 0.92, 1);
  const F = makeFace(0.62, { skin: PINK, span: 1.05, eyeY: 10 }); F.mesh.scale.set(1.12, 0.92, 1); head.add(F.mesh);
  // 헤드셋(관제실장)
  const hs = mat('#2b2f36', 0.4);
  const band = mesh(new THREE.TorusGeometry(0.66, 0.035, 10, 40, Math.PI), hs, head, 0, 0.02, 0); band.scale.set(1.12, 0.95, 1);
  for (const s of [-1, 1]) mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.08, 20), hs, head, s * 0.72, 0, 0).rotation.z = Math.PI / 2;
  const mic = new THREE.CatmullRomCurve3([new THREE.Vector3(-0.74, -0.02, 0.04), new THREE.Vector3(-0.66, -0.3, 0.3), new THREE.Vector3(-0.3, -0.42, 0.52)]);
  mesh(new THREE.TubeGeometry(mic, 20, 0.018, 6), hs, head); mesh(new THREE.SphereGeometry(0.05, 12, 10), mat('#e04a3c', 0.4), head, -0.3, -0.42, 0.52);
  const { armL, armR } = smallLimbs(torso, mat(PINK, 0.6), 0.32, 0.55);
  const legL = leg(hips, 1, mat(PINK, 0.6), mat('#3b3f48', 0.6), 0.32), legR = leg(hips, -1, mat(PINK, 0.6), mat('#3b3f48', 0.6), 0.32);
  const R = { root, hips, hipY, torso, head, armL, armR, legL, legR };
  return { root, R, head, face: F, pose: (P) => applyPose(R, P), setFace: (p, bl = 0) => F.draw(p, 0, bl) };
}

// ───── 콩팥 공장장 ─────
export function makeKidney() {
  const RED = '#b5524a';
  const root = new THREE.Group(); const hipY = 0.32; const hips = grp(root, 0, hipY, 0); const torso = grp(hips);
  const geo = new THREE.SphereGeometry(0.55, 64, 48); const pos = geo.attributes.position, v = new THREE.Vector3();
  for (let i = 0; i < pos.count; i++) { v.fromBufferAttribute(pos, i); const n = v.clone().normalize();
    const dent = 0.3 * Math.exp(-Math.pow(n.y / 0.35, 2)) * Math.max(0, n.x - 0.15) * Math.max(0, 0.5 - n.z); // 안쪽(왼쪽) 오목
    v.multiplyScalar(1 - dent); pos.setXYZ(i, v.x, v.y, v.z); }
  geo.computeVertexNormals();
  const head = grp(torso, 0, 0.66, 0);
  const b = mesh(geo, mat(RED, 0.5), head); b.scale.set(0.95, 1.25, 0.85);
  const F = makeFace(0.55, { skin: RED, span: 1.05 }); F.mesh.scale.set(0.95, 1.25, 0.85); head.add(F.mesh);
  // 노란 안전모
  const hat = grp(head, 0.02, 0.6, 0); hat.rotation.z = -0.12;
  mesh(new THREE.SphereGeometry(0.33, 28, 16, 0, Math.PI * 2, 0, Math.PI / 2), mat('#ffc928', 0.35), hat);
  mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.03, 32), mat('#ffc928', 0.35), hat, 0, 0.0, 0.05);
  mesh(new THREE.BoxGeometry(0.06, 0.06, 0.66), mat('#f0b400', 0.35), hat, 0, 0.3, 0);
  const { armL, armR } = smallLimbs(torso, mat(RED, 0.55), 0.38, 0.5);
  const legL = leg(hips, 1, mat(RED, 0.55), mat('#3b3f48', 0.6), 0.32), legR = leg(hips, -1, mat(RED, 0.55), mat('#3b3f48', 0.6), 0.32);
  const R = { root, hips, hipY, torso, head, armL, armR, legL, legR };
  return { root, R, head, face: F, pose: (P) => applyPose(R, P), setFace: (p, bl = 0) => F.draw(p, 0, bl) };
}
