// 사용: node geo.mjs <spec.json> <out geo.json>
// spec.map: { fit: [ISO숫자id...] 또는 bbox:[서경,남위,동경,북위], highlight:[ISO숫자id...], pad:[좌,상,우,하] }
// spec.cities: { 키: [경도, 위도] },  spec.map.labels: [[이름, 경도, 위도], ...]
import fs from 'fs';
import { feature } from 'topojson-client';
import { geoMercator, geoPath } from 'd3-geo';

const [specPath, outPath] = process.argv.slice(2);
const spec = JSON.parse(fs.readFileSync(specPath));
const m = spec.map || {};
// spec.map.geojson: 나라 대신 쓸 지도 파일(저장소 기준 경로, 예: 서울 구 경계 assets/geo/seoul_gu.json). 이때 fit·highlight는 properties.name(구 이름)으로 지정
let all;
if (m.geojson) {
  const gj = JSON.parse(fs.readFileSync(new URL('../../' + m.geojson, import.meta.url)));
  // d3-geo는 바깥 고리가 시계 방향이어야 함(반대면 지구 전체로 칠해짐) → 반시계면 뒤집는다
  const area = r => r.reduce((s, [x1, y1], i) => { const [x2, y2] = r[(i + 1) % r.length]; return s + (x2 - x1) * (y2 + y1); }, 0);
  const fix = poly => (area(poly[0]) < 0 ? poly.map(r => [...r].reverse()) : poly);
  all = gj.features.map(f => {
    const g = f.geometry;
    const geometry = g.type === 'Polygon' ? { ...g, coordinates: fix(g.coordinates) } : { ...g, coordinates: g.coordinates.map(fix) };
    return { ...f, geometry, id: f.properties.name };
  });
} else {
  const topo = JSON.parse(fs.readFileSync(new URL('./node_modules/world-atlas/countries-50m.json', import.meta.url)));
  all = feature(topo, topo.objects.countries).features;
}
const W = 1000, H = 880;
const pad = m.pad || [150, 40, 150, 30];
let fitObj;
if (m.bbox) {
  const [x0, y0, x1, y1] = m.bbox;
  fitObj = { type: 'MultiPoint', coordinates: [[x0, y0], [x1, y0], [x1, y1], [x0, y1]] };  // 다각형은 감는 방향 때문에 지구 전체로 잡혀서 점 4개로 맞춤
} else {
  const ids = (m.fit || m.highlight).map(String);
  fitObj = { type: 'FeatureCollection', features: all.filter(f => ids.includes(f.id)) };
}
const proj = geoMercator().fitExtent([[pad[0], pad[1]], [W - pad[2], H - pad[3]]], fitObj);
const path = geoPath(proj);
const hl = (m.highlight || []).map(String);
const out = {
  W, H,
  others: all.filter(f => !hl.includes(f.id)).map(f => path(f)).filter(Boolean),
  highlight: all.filter(f => hl.includes(f.id)).map(f => path(f)).filter(Boolean),
  pts: Object.fromEntries(Object.entries(spec.cities || {}).map(([k, v]) => [k, proj(v).map(n => +n.toFixed(1))])),
  labels: (m.labels || []).map(([n, lon, lat]) => [n, ...proj([lon, lat]).map(v => +v.toFixed(1))])
};
fs.writeFileSync(outPath, JSON.stringify(out));
console.log('지도 OK, 도시', Object.keys(out.pts).length, '개');
