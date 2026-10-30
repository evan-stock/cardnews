import fs from 'fs';
import { feature } from 'topojson-client';
import { geoMercator, geoPath } from 'd3-geo';

const topo = JSON.parse(fs.readFileSync('node_modules/world-atlas/countries-50m.json'));
const all = feature(topo, topo.objects.countries).features;
const italy = all.find(f => f.id === '380');
const W = 1000, H = 880;
// 이탈리아를 패널 가운데 약간 왼쪽에 크게(사진 카드 자리 확보는 장면별로)
const proj = geoMercator().fitExtent([[150, 40], [W - 150, H - 30]], italy);
const path = geoPath(proj);
const others = all.filter(f => f.id !== '380').map(f => path(f)).filter(Boolean);
const cities = {
  milano: [9.19, 45.464], torino: [7.686, 45.07], mestre: [12.24, 45.49], vicenza: [11.546, 45.548],
  ancona: [13.519, 43.616], roma: [12.496, 41.903], napoli: [14.268, 40.852], palermo: [13.361, 38.116],
  cosenza: [16.254, 39.298], pisa: [10.402, 43.716], livorno: [10.31, 43.548], trieste: [13.776, 45.65],
  bologna: [11.342, 44.494], aosta: [7.315, 45.737], ravenna: [12.2, 44.418], genova: [8.934, 44.405],
  bari: [16.87, 41.117], firenze: [11.256, 43.77], cagliari: [9.11, 39.223], catania: [15.087, 37.502],
  padova: [11.877, 45.406], verona: [10.992, 45.438], brescia: [10.211, 45.541], trento: [11.121, 46.067]
};
const pts = Object.fromEntries(Object.entries(cities).map(([k, v]) => [k, proj(v).map(n => +n.toFixed(1))]));
fs.writeFileSync('geo.json', JSON.stringify({ W, H, italy: path(italy), others, pts }));
console.log(pts);
