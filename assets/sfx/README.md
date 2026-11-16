# 효과음

## 2026.11.13 later 추가 (사용자 요청 "유튜브 채널들에도 이 소리 쓸 수 있게")
- `later` = 스폰지밥 "1시간 뒤" 시간 경과 내레이션(약 2초). 쓰임: 시간이 흘렀음을 보여주는 장면 전환·썰 전개.
- 출처: 구글 드라이브 '카테고리별 릴스 효과음 모음집'(01_화면전환/스폰지밥(1시간뒤]).MP3). 원작은 니켈로디언 애니메이션 음원 — CC0·Pixabay와 달리 저작권 있는 소리. 사용자 판단(밈으로 널리 쓰임)으로 사용. 유튜브 Content ID 클레임(수익 배분·음소거) 가능성은 남아 있음.
- 처리: 앞뒤 무음 제거, 최고 음량 -10.5dB 기준으로 맞춤.

## 2026.11.11 Pixabay 효과음 45개 추가·6개 교체 (사용자 "합성음 같다, 릴스에서 쓰는 소리 그대로")
- 출처: Pixabay Sound Effects(Pixabay Content License — 무료, 상업·수익화 가능, 출처 표기 불필요). 사용자 Pixabay 계정으로 크롬에서 받음.
- 원본 파일·작성자·페이지 주소: `pixabay_sources_1111.csv`(정지·이의제기 근거로 보관).
- 처리: 앞뒤 무음 제거, 최고 음량 -10.5dB로 통일(기존 투머치 기준), 긴 소리(타자·귀뚜라미 2.5초, 심장·웃음 3초)는 자르고 끝 0.25초 페이드.
- **교체(옛 파일은 old_1111/)**: pop, whoosh, ding, boing, thud(ground impact), heart(심장 1번)
- **새 이름** (2 붙은 것은 대체 후보):
  - 강조·등장: boom(바인 붐) · boom2(시네마틱 붐) · impact(묵직한 충격) · dun(둥)
  - 전환: whoosh2 · swoosh · swoosh2 · swipe · glitch · glitch2 · riser · riser2(긴장 상승)
  - 귀여움·포인트: pop2 · bubble · bubble2 · ding2 · boing2
  - 반전·황당: scratch(레코드 긁기) · scratch2 · cricket(정적·썰렁)
  - 정답·오답: correct · correct2 · wrong(부저) · wrong2
  - 돈·숫자: cash(카칭) · cash2 · coin · coin2
  - 기타: shutter · shutter2(사진) · heartbeat(긴장 심장 3초) · laugh · laugh2(시트콤 웃음) · click · click2 · typing · typing2 · notif · notif2(알림)
- 그대로 둔 것(Freesound CC0): dundun, sparkle, fail, tada, question, sneak, shock, squeak, slide, tick, poof, nom
- 되돌리기: old_1111/의 파일을 assets/sfx/로 옮기면 됨.

## 이전 기록
### (이전 제목) 효과음 (직접 합성 scripts/sfx/make_sfx.py + 실제 녹음 4종 — 모두 저작권 걱정 없음)

2026.10.20 교체(Freesound CC0, 출처 표기 불필요, 수익화 가능 — 다운로드 수 많은 것 위주):
- boing 띠용 = Cartoon Boing (reelworldstudio, freesound 161122)
- sparkle 삐로롱 = cartoon_wink_magic_sparkle (MLaudio, freesound 511485)
- thud 퉁 = Bonk Sound effect (thecoolcookie17, freesound 573047)
- dundun 두둥 = Dramatic Hit (qubodup, freesound 222517, 앞 2.5초)

2026.10.20 2차 교체(나머지 14종도 Freesound CC0 실제 녹음, 출처 표기 불필요):
pop=Cartoon Pop(unfa 245645) · whoosh=Whoosh(qubodup 60013) · ding=Ding! idea(Saya13 407258) · fail=horn_fail_wahwah_3(TaranP 362204) · tada=Tada Fanfare A(plasterbrain 397355) · question=Slide Whistle 상승(sheepfilms 202753) · sneak=The Doofus Sneaks Around 앞 1.8초(dominictreis 423321) · heart=Heartbeat 97 BPM(Cloud-10 688735) · shock=Shocked gasp(GentlemanWalrus 180005) · squeak=Squeaky Toy #1(Breviceps 468443) · slide=classic dizzy take slide whistle(martian 403002) · tick=Loopable Ticking Clock(OwlStorm 212181) · poof=Poof of Smoke(Planman 208111) · nom=Munching Food(Kodack 256311)
이제 18종 모두 실제 녹음. 같은 날 '투머치' 피드백으로 전부 음량을 낮추고(최고 -10.5dB) 긴 소리(빠밤·두근두근·째깍·두둥 등)를 1~1.6초로 줄임. 아래 표의 길이는 예전 합성음 기준이라 실제와 다를 수 있음.

원래 합성음으로 되돌리기: python3 scripts/sfx/make_sfx.py 로 다시 만들거나 git 기록에서 복원.

원고: 장면 `"sfx": [{"f": "pop", "at": 0.4, "vol": 1.0}]` 또는 위치 자막에 `"s": "pop"`.

| 이름 | 쓰임 | 길이 |
|---|---|---|
| pop | 뿅(등장·깨달음) | 0.12초 |
| boing | 띠용(황당·튕김) | 1.04초 |
| whoosh | 휙(빠른 움직임·장면 전환) | 0.45초 |
| ding | 띵(정답·아이디어) | 1.20초 |
| thud | 퉁·봉크(맞음·넘어짐) | 1.23초 |
| dundun | 두둥(등장·긴장) | 2.53초 |
| sparkle | 삐로롱·반짝(귀여움·윙크) | 1.31초 |
| fail | 빠밤(실패·허무) | 2.12초 |
| tada | 짠(성공·공개) | 1.10초 |
| question | 갸우뚱(?·의아) | 0.40초 |
| sneak | 살금살금(몰래·조심) | 1.32초 |
| heart | 두근두근(설렘·긴장) | 1.00초 |
| shock | 헉(충격·반전) | 0.60초 |
| squeak | 뾱뾱(장난감·귀여움) | 0.28초 |
| slide | 쭈욱·날름(늘어남·핥기) | 0.35초 |
| tick | 째깍째깍(기다림) | 1.00초 |
| poof | 펑(사라짐·터짐) | 0.25초 |
| nom | 냠냠(먹기) | 0.64초 |
