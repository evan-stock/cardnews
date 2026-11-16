// ==UserScript==
// @name         엑스 피드 급상승 표시 (오늘의쓸모)
// @namespace    https://github.com/evan-stock/cardnews
// @version      0.1
// @description  엑스 피드의 글마다 '시간당 조회수'를 계산해 붙이고, 올린 지 얼마 안 됐는데 빠르게 오르는 글을 색으로 표시한다.
// @match        https://x.com/*
// @match        https://twitter.com/*
// @grant        none
// @run-at       document-idle
// ==/UserScript==
(function () {
  'use strict';
  // ---- 기준(여기 숫자만 바꾸면 된다) ----
  const MAX_AGE_H = 12;      // 이 시간 안에 올린 글만 강조
  const HOT_VPH = 100000;    // 시간당 조회 이 이상 = 빨강(급상승)
  const WARM_VPH = 30000;    // 시간당 조회 이 이상 = 노랑(눈여겨볼 글)
  const HIDE_COLD = false;   // true 면 기준 아래 글의 표시를 숨긴다
  const KEY = 'worthyRadarSeen';

  const UNIT = { '천': 1e3, '만': 1e4, '억': 1e8, k: 1e3, m: 1e6, b: 1e9 };
  function num(s) {
    const m = /(\d[\d,.]*)\s*(천|만|억|[kKmMbB])?/.exec(s || '');
    if (!m) return null;
    const u = m[2] ? UNIT[m[2].toLowerCase()] || UNIT[m[2]] : 1;
    const n = parseFloat(u === 1 ? m[1].replace(/[,.]/g, '') : m[1].replace(/,/g, ''));
    return isNaN(n) ? null : n * u;
  }
  function man(n) {
    if (n >= 1e8) return (n / 1e8).toFixed(1) + '억';
    if (n >= 1e5) return Math.round(n / 1e4) + '만';
    if (n >= 1e4) return (n / 1e4).toFixed(1) + '만';
    return Math.round(n).toLocaleString();
  }
  function ageStr(h) { return h < 1 ? Math.round(h * 60) + '분 전' : h.toFixed(1) + '시간 전'; }

  let seen = {};
  try { seen = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { seen = {}; }
  function saveSeen() {
    const ids = Object.keys(seen);
    if (ids.length > 3000) ids.sort((a, b) => seen[a][0] - seen[b][0]).slice(0, ids.length - 2000).forEach((i) => delete seen[i]);
    try { localStorage.setItem(KEY, JSON.stringify(seen)); } catch (e) { /* 저장 못 해도 표시는 계속 */ }
  }

  function read(article) {
    const time = article.querySelector('a[href*="/status/"] time[datetime]');
    if (!time) return null; // 광고 등
    const id = (/\/status\/(\d+)/.exec(time.closest('a').getAttribute('href')) || [])[1];
    const stat = article.querySelector('a[href$="/analytics"]');
    let views = stat ? num(stat.getAttribute('aria-label')) : null;
    if (views == null && stat) views = num(stat.textContent);
    if (views == null) {
      const g = article.querySelector('[role="group"][aria-label]');
      const m = g && /(?:조회수\s*([\d,.]+\s*[천만억]?))|(?:([\d,.]+\s*[kKmMbB]?)\s*views)/.exec(g.getAttribute('aria-label'));
      if (m) views = num(m[1] || m[2]);
    }
    if (!id || views == null) return null;
    const ageH = Math.max((Date.now() - new Date(time.getAttribute('datetime')).getTime()) / 36e5, 0.05);
    return { id, views, ageH };
  }

  function paint(article) {
    const d = read(article);
    if (!d) return;
    const now = Date.now();
    let nowVph = null;
    const first = seen[d.id];
    if (!first) seen[d.id] = [now, d.views];
    else if (now - first[0] >= 5 * 60e3) nowVph = Math.max(d.views - first[1], 0) / ((now - first[0]) / 36e5);
    const avg = d.views / d.ageH;
    const vph = nowVph != null ? nowVph : avg;
    const fresh = d.ageH <= MAX_AGE_H;
    const level = fresh && vph >= HOT_VPH ? 'hot' : fresh && vph >= WARM_VPH ? 'warm' : 'cold';

    let b = article.querySelector(':scope .worthy-radar');
    if (!b) {
      b = document.createElement('div');
      b.className = 'worthy-radar';
      b.style.cssText = 'font:700 12px/1.6 system-ui,sans-serif;padding:1px 10px;margin:4px 12px 0;border-radius:10px;display:inline-block;align-self:flex-start;';
      article.prepend(b);
    }
    const color = { hot: ['#e0245e', '#fff'], warm: ['#ffd400', '#111'], cold: ['transparent', '#8899a6'] }[level];
    b.style.background = color[0];
    b.style.color = color[1];
    b.style.display = level === 'cold' && HIDE_COLD ? 'none' : 'inline-block';
    b.textContent = (level === 'hot' ? '🚀 급상승 · ' : level === 'warm' ? '👀 ' : '')
      + '시간당 +' + man(vph) + (nowVph != null ? ' (지금)' : ' (평균)')
      + ' · 조회 ' + man(d.views) + ' · ' + ageStr(d.ageH);
    article.style.boxShadow = level === 'hot' ? 'inset 4px 0 0 #e0245e' : level === 'warm' ? 'inset 4px 0 0 #ffd400' : '';
  }

  function scan() {
    document.querySelectorAll('article[data-testid="tweet"]').forEach((a) => {
      try { paint(a); } catch (e) { /* 화면 구조가 바뀌면 그 글만 건너뜀 */ }
    });
    saveSeen();
  }
  setInterval(scan, 2000);
  scan();
})();
