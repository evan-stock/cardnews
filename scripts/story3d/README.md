# 3D 원리 쇼츠 (보통씨 + 몸속 직원들)

Boris식 렌더: three.js 로 세계를 한 번 짓고, 헤드리스 크롬(Playwright, SwiftShader)에서 프레임마다 찍어 ffmpeg 로 묶는다. AI 이미지·영상·스톡 모델 없음.

- `face.js` 얼굴을 매 프레임 숫자로 그림(표정 20종, 눈썹 먼저·입 뒤따름 모핑)
- `chars.js` 이 남자(청록 후드 집업 + 사원증 '박보통'), 뇌 관제실장, 콩팥 공장장
- `full.html` 1편 「라면 국물까지 다 마시면 몸에서 생기는 일」 전체 장면·자막·출처 줄 (38.4초)
- `pilot.html` 10초 시안, `sheet.html` 캐릭터 시트
- `frames.js` 프레임 캡처: `node frames.js full.html out 30 38.4` (three 0.170.0 을 node_modules 에 설치)
- `snap.js` 한 장 렌더: `node snap.js sheet.html sheet.png 1800 1200`
- 목소리: drafts/gemini_tts_test.json(Fenrir) → state/tts_test/gemini_Fenrir_ramen.mp3, 무음 0.2초 넘는 구간을 0.14초로 줄이고 1.08배
- 효과음: sfx/ (Pixabay Content License, CREDITS.md)
