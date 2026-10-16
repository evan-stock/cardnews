# 오늘의쓸모 카드뉴스 자동화

매일 **점심 1시, 저녁 6시**에 화제 뉴스 카드뉴스를 만들어 **텔레그램으로 승인받은 뒤 인스타그램에 자동 게시**합니다.

```
11:15  소재 조사(Claude, 웹 검색·원문 확인) → 장마다 다른 사진(위키미디어 공개 사진, 없으면 AI 생성)
       → 카드 7장 렌더링(1080×1350 JPEG) → 텔레그램으로 미리보기 + [✅ 승인] [❌ 거절]
13:00  승인됐으면 인스타그램 캐러셀로 게시 → 텔레그램으로 게시 링크 알림
       (승인이 1시 이후면 승인 직후 10분 안에 게시, 4시까지 승인 없으면 만료)
16:15 / 18:00  저녁 게시물도 같은 방식
```

모든 작업은 GitHub Actions(무료)에서 돌아가서, 컴퓨터를 켜둘 필요가 없어요.

---

## 1. 준비물

| 항목 | 용도 | 비용 |
|---|---|---|
| GitHub 계정 | 자동 실행 + 카드 이미지 보관 | 무료 |
| Anthropic API 키 | 소재 조사·카드 문구 작성 | 하루 2건 기준 월 몇천 원 수준(사용량 과금) |
| 텔레그램 | 승인 버튼 | 무료 |
| 인스타그램 프로페셔널 계정 + 메타 개발자 앱 | 자동 게시 | 무료 |
| (선택) OpenAI API 키 | 공개 사진이 없을 때 AI 이미지 생성 | 장당 과금 |

## 2. GitHub 저장소 만들기

1. GitHub에서 **New repository** → 이름 예: `cardnews` → **Public**으로 생성
   - 인스타그램이 카드 이미지를 공개 주소에서 가져가야 해서 공개 저장소를 씁니다. API 키 등 비밀값은 Secrets에 들어가서 공개되지 않아요.
2. 이 폴더의 파일을 전부 업로드합니다. (웹에서 **Add file → Upload files**로 폴더째 끌어다 놓기. `.github` 폴더도 꼭 포함)
3. **Settings → Actions → General → Workflow permissions**에서 **Read and write permissions** 선택 후 저장

## 3. 텔레그램 봇 만들기

1. 텔레그램에서 **@BotFather** 검색 → `/newbot` → 이름 정하기 → **봇 토큰**(예: `123456:ABC...`)을 복사
2. 방금 만든 봇과의 대화창을 열고 아무 메시지나 보내기
3. 브라우저에서 `https://api.telegram.org/bot<봇토큰>/getUpdates` 를 열면 나오는 `"chat":{"id":숫자` 의 숫자가 **채팅 ID**

## 4. 인스타그램 API 연결

1. 인스타그램 앱 → 설정 → 계정 유형 → **프로페셔널 계정**(크리에이터 또는 비즈니스)으로 전환
2. https://developers.facebook.com 에서 앱 만들기 → 사용 사례에서 **Instagram API** 관련 항목 선택
3. **Instagram 로그인을 통한 API 설정** 화면에서 오늘의쓸모 계정을 추가하고 **액세스 토큰 생성**
   - 권한: `instagram_business_basic`, `instagram_business_content_publish`
   - 여기서 나온 토큰(장기 토큰, 60일)과 **Instagram 사용자 ID**(숫자)를 복사
4. 메타 화면 구성은 자주 바뀌어요. 막히면 화면 캡처를 Claude에게 보여주세요.

## 5. Secrets 등록

저장소 **Settings → Secrets and variables → Actions → New repository secret**

| 이름 | 값 |
|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com 에서 발급한 키 |
| `TELEGRAM_BOT_TOKEN` | 3단계 봇 토큰 |
| `TELEGRAM_CHAT_ID` | 3단계 채팅 ID |
| `IG_USER_ID` | 4단계 Instagram 사용자 ID |
| `IG_ACCESS_TOKEN` | 4단계 액세스 토큰 |
| `OPENAI_API_KEY` | (선택) AI 이미지용 |
| `GH_PAT` | (선택, 권장) 인스타 토큰 자동 갱신용. GitHub → Settings → Developer settings → Fine-grained token → 이 저장소의 **Secrets: Read and write** 권한 |

`GH_PAT`가 없으면 60일마다 4단계에서 토큰을 새로 받아 `IG_ACCESS_TOKEN`을 직접 바꿔야 해요.

## 6. 첫 실행 테스트

1. **Actions** 탭 → 왼쪽 **cardnews** → **Run workflow** → `cmd: prepare`, `slot: lunch` → 실행
2. 몇 분 뒤 텔레그램에 카드 7장 + 본문 미리보기 + 승인 버튼이 와요
3. **✅ 승인** 누르기 → 다시 **Run workflow**에서 `cmd: tick` 실행
   - 오후 1시 전이면 1시까지 기다렸다가 다음 자동 실행(10분 간격) 때 게시돼요
   - 바로 올려보고 싶으면 `cmd: publish`, `id: 20261014-lunch`(텔레그램 메시지의 날짜-슬롯) 로 실행
4. 텔레그램에 "🎉 게시 완료" 와 인스타 링크가 오면 성공

이후로는 매일 자동으로 돌아가요.

## 7. 운영

- **승인/거절**: 텔레그램 버튼만 누르면 돼요. 거절하면 그 시간대는 쉬어갑니다.
- **⚠️ 확인할 점**: 미리보기에 사실관계·명예훼손 위험이 적혀 오면 출처 링크를 꼭 열어보고 승인하세요.
- **시간 바꾸기**: `config.yaml`의 `publish_at`과 `.github/workflows/pipeline.yml`의 cron(UTC 기준, 한국시간 −9시간)을 함께 수정
- **디자인**: `config.yaml`의 `style`(photo/bold/mag/min, 색상 0~3). 카드 디자인 자체는 `templates/renderer.html`(카드뉴스 메이커 앱과 동일)
- **실패 시**: 텔레그램으로 실패 알림이 와요. Actions 탭에서 해당 실행 로그를 확인하고 `prepare`를 다시 실행하면 됩니다.
- GitHub 예약 실행은 몇 분~수십 분 늦을 수 있어요.

## 8. 주의

- 카드 사진은 **출처 기사·유튜브·틱톡 원본 사진을 먼저** 쓰고, 부족하면 위키미디어 공개 사진 → AI 이미지 순으로 채워요. 게시물 본문에 '사진: 언론사' 출처가 자동 표기돼요. 언론 사진은 해당 언론사 저작물이라 신고·삭제 요청이 올 수 있어요. 끄려면 `config.yaml`의 `images.press: false`.
- 자극적인 소재일수록 사실 오류 하나가 계정 신고로 이어질 수 있어요. 승인 버튼은 그 마지막 안전장치예요.
- 인스타그램 API로는 하루 게시 수에 상한이 있지만 하루 2건은 문제없어요.

## 유튜브 쇼츠

대본 → TTS 내레이션 → 실제 영상·사진 합성 → 자막 → 텔레그램 승인 → 유튜브 업로드. 설정과 원고 형식은 [docs/SHORTS.md](docs/SHORTS.md).

## 폴더 구조

```
config.yaml                 설정(시간, 브랜드, 모델, 스타일)
cardnews/research.py        Claude API 웹 검색으로 소재 선정·문구 작성
cardnews/images.py          위키미디어 사진 검색 / AI 이미지
cardnews/render.py          카드 렌더링(Playwright)
cardnews/telegram_bot.py    미리보기 전송·승인 확인
cardnews/instagram.py       캐러셀 게시·토큰 갱신
cardnews/main.py            prepare / tick / publish 명령
cardnews/shorts.py          유튜브 쇼츠 합성(장면·자막·BGM)
cardnews/tts.py             타입캐스트(무료) → Edge TTS 자동 대체
cardnews/youtube.py         유튜브 업로드·예약
.github/workflows/          자동 실행 일정
state/  media/              게시물 상태와 카드 이미지(자동 저장, 7일 뒤 정리)
tests/test_flow.py          외부 API 없이 전체 흐름 점검
```
