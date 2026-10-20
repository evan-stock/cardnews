# 효과음 (직접 합성 scripts/sfx/make_sfx.py + 실제 녹음 4종 — 모두 저작권 걱정 없음)

2026.10.20 교체(Freesound CC0, 출처 표기 불필요, 수익화 가능 — 다운로드 수 많은 것 위주):
- boing 띠용 = Cartoon Boing (reelworldstudio, freesound 161122)
- sparkle 삐로롱 = cartoon_wink_magic_sparkle (MLaudio, freesound 511485)
- thud 퉁 = Bonk Sound effect (thecoolcookie17, freesound 573047)
- dundun 두둥 = Dramatic Hit (qubodup, freesound 222517, 앞 2.5초)

2026.10.20 2차 교체(나머지 14종도 Freesound CC0 실제 녹음, 출처 표기 불필요):
pop=Cartoon Pop(unfa 245645) · whoosh=Whoosh(qubodup 60013) · ding=Ding! idea(Saya13 407258) · fail=horn_fail_wahwah_3(TaranP 362204) · tada=Tada Fanfare A(plasterbrain 397355) · question=Slide Whistle 상승(sheepfilms 202753) · sneak=The Doofus Sneaks Around 앞 1.8초(dominictreis 423321) · heart=Heartbeat 97 BPM(Cloud-10 688735) · shock=Shocked gasp(GentlemanWalrus 180005) · squeak=Squeaky Toy #1(Breviceps 468443) · slide=classic dizzy take slide whistle(martian 403002) · tick=Loopable Ticking Clock(OwlStorm 212181) · poof=Poof of Smoke(Planman 208111) · nom=Munching Food(Kodack 256311)
이제 18종 모두 실제 녹음. 아래 표의 길이는 예전 합성음 기준이라 실제와 다를 수 있음.

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
