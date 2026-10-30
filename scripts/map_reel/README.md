# 지도 애니메이션 릴스 틀 (2026.10.30, 첫 시안: 이탈리아 총파업)

pickd 지도 릴스 구조(위 제목 고정 + 가운데 지도 + 아래 2줄 자막, 장면마다 핀이 쌓임)를 오늘의쓸모 브랜드(today.worthy 로고, 노랑 #FFD84D, Pretendard)로 다시 만든 틀.

## 만드는 법
1. `geo.mjs`: 나라(world-atlas countries-50m, ISO 숫자 id)와 도시 좌표 → `geo.json` (`npm i world-atlas@2 topojson-client d3-geo` 후 `node geo.mjs`)
2. `data.js`: 장면 목록(핀 k·이름·left/below, 카드 사진·위치·설명 또는 stat 숫자 카드, 하단 ctx/l1/l2, 시각 t), 정리 장면 점(dots), CTA 시각, 전체 길이
3. 작업 폴더에 `fonts/`(Pretendard Black·Medium·SemiBold), `logo.png`(brand/logo_typo_A.png), `ph/`(사진) 복사
4. `node render.js shots 1,4.5,...`로 미리보기 → `node render.js frames 30` → ffmpeg로 mp4
   (playwright는 작업공간 기본 설치본 사용, 새로 설치하지 않는다)

- 장면당 약 3.3초, 핀 → 점선 → 사진 카드(0.45초 뒤), 하단 자막은 밀어 올리며 교체
- 첫 프레임에 제목·자막이 다 보이게(인트로 자막은 페이드 없음) → 첫 프레임이 커버 역할
