# 유튜브 쇼츠 자동 제작

채팅에서 대본을 쓰면 GitHub Actions가 **내레이션(TTS) → 실제 영상·사진·AI 장면 합성 → 제목·자막 → 텔레그램 미리보기**까지 만들고,
**[✅ 업로드]** 를 누르면 유튜브에 올라갑니다. API 비용은 0원이 기본입니다.

```
채팅: 소재 확인 → 영상(drafts/video.json)·사진(drafts/current.json collect) 모으기 → 대본 작성
  → drafts/shorts.json push → shorts.yml: TTS·합성 (약 1~3분)
  → 텔레그램: 미리보기 영상 + 제목·설명 + [✅ 업로드] [❌ 거절]
  → 승인 → 유튜브 업로드(예약 시각이 있으면 유튜브 예약 공개)
```

## 비용

| 항목 | 방법 | 비용 |
|---|---|---|
| 대본 | 채팅(Claude)에서 작성 | 0원 |
| 목소리 | 타입캐스트 API **무료 플랜**(월 30,000자 ≈ 45초 쇼츠 100개). 한도 근접·오류 시 **Edge TTS(무료)** 로 자동 전환 | 0원 |
| 영상 합성 | GitHub Actions(공개 저장소 무료) + ffmpeg | 0원 |
| 업로드 | YouTube Data API(하루 할당량 10,000 = 업로드 6건) | 0원 |
| AI 장면 | 실제 영상·사진이 모자랄 때만 채팅에서 Higgsfield로 생성 | 크레딧(선택) |

> 타입캐스트 무료 플랜 결과물의 상업적 이용(수익화 채널) 조건은 가입할 때 약관에서 한 번 확인하세요. 설명란에는 "음성: Typecast"가 자동으로 붙습니다.

## 1회 설정

### 1) 타입캐스트 API 키 (무료)
1. https://typecast.ai/developers/api 에서 가입 → API 콘솔 → **API Key 발급** (Free 플랜, 카드 등록 불필요)
2. GitHub 저장소 Settings → Secrets → `TYPECAST_API_KEY` 등록
3. Actions → **shorts** → Run workflow → `cmd: voices` → 텔레그램으로 목소리 목록(미리듣기 링크 포함)이 옵니다
4. 마음에 드는 목소리의 `tc_...` ID를 채팅에 알려주면 `config.yaml`의 `shorts.tts.voice_id`에 넣습니다

키가 없거나 목소리를 아직 안 골랐으면 Edge TTS(InJoon 남성 목소리)로 만들어집니다.

### 2) 유튜브 업로드 연결 (무료)
1. https://console.cloud.google.com → 새 프로젝트 → **YouTube Data API v3 사용 설정**
2. **OAuth 동의 화면**: 외부(External) → 앱 이름·이메일 입력 → 테스트 사용자에 채널 구글 계정 추가
   → 마지막에 **"앱 게시(프로덕션으로 푸시)"** 를 꼭 누르기 (테스트 상태로 두면 토큰이 7일마다 만료됨. 검증 신청은 필요 없음)
3. **사용자 인증 정보 → OAuth 클라이언트 ID → 데스크톱 앱** → 클라이언트 ID·보안 비밀 복사
4. 내 컴퓨터 터미널에서 (파이썬 + `pip install requests pyyaml`):
   ```
   python -m cardnews.youtube auth <클라이언트ID> <보안비밀>
   ```
   브라우저에서 **쇼츠를 올릴 채널 계정**으로 허용 → "확인되지 않은 앱" 경고가 나오면 고급 → 이동 → 출력된 refresh token 복사
5. Secrets 등록: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`
6. Actions → **shorts** → `cmd: yt-check` → 로그에 채널 이름이 나오면 성공

## 원고 형식 (drafts/shorts.json)

```json
{
 "id": "20261017-robot", "mode": "send", "topic": "중국 로봇 마라톤",
 "hook": {"tag": "실제 영상", "t": "사람보다 빨랐다\n로봇 마라톤\n'결승선 장면'"},
 "scenes": [
  {"say": "로봇이 마라톤에서 사람을 이겼습니다.", "video": {"src": "video/v1.mp4", "start": 12}},
  {"say": "21킬로미터를 '2시간 40분'에 완주했습니다.", "img": "cand/press03.jpg"},
  {"say": "출발 직전의 모습은 이랬습니다.", "img": "cand/url01.jpg", "label": "AI 참고 이미지"},
  {"say": "생각나는 친구에게 보내주세요. 구독하면 매일 화제 소식을 받아보실 수 있습니다.",
   "video": {"src": "video/v1.mp4", "start": 40}}
 ],
 "yt": {"title": "로봇이 사람을 이긴 마라톤 결승선 #shorts", "description": "본문 3문단…",
        "tags": ["로봇", "마라톤"], "privacy": "public"},
 "sources": [{"publisher": "로이터", "date": "2026.10.17", "url": "…"}], "photo_credits": ["로이터"],
 "publish_now": true
}
```

| 필드 | 설명 |
|---|---|
| `mode` | `render`(만들기만) / `send`(텔레그램 미리보기 + 승인 버튼) |
| `hook` | 영상 내내 위쪽에 고정되는 제목 2~3줄. `'작은따옴표'`는 노란 강조 |
| `scenes[].say` | 내레이션 문장(= 자막). 장면 길이는 이 문장 음성 길이 |
| `scenes[].video` | `src`(media/<id>/ 기준), `start`, `x`·`y`(자를 위치), `fit`(`auto`/`fill`/`fit`), `audio`(원본 소리 0~1) |
| `scenes[].img` | 사진. 세로는 꽉 채움, 가로는 제목 아래 띠로 + 흐린 배경. `zoom` 확대 정도 |
| `scenes[].label` | `"AI 참고 이미지"` 등 작은 표기. 있으면 업로드 때 '합성 콘텐츠'로 자동 신고 |
| `scenes[].sub` / `nosub` / `title:false` | 자막 따로 쓰기 / 자막 끄기 / 그 장면만 제목 숨기기 |
| `voice` | `{"voice_id","emotion","tempo","engine"}` 이번 영상만 목소리 바꾸기 |
| `bgm` | `assets/bgm/xxx.mp3` (유튜브 오디오 보관함 등 저작권 없는 곡만) |
| `publish_now` / `publish_at`+`approved` | 승인 즉시 공개 / 지정 시각 예약 공개 |

## 대본 작성 기준 (오늘의쓸모 v3 기준을 쇼츠에 맞춤)
- **길이 20~40초**(장면 4~7개, 대본 150~280자). 첫 문장 2초 안에 '와' 포인트나 결말 숫자를 말한다.
- 문장은 짧게, 어미는 **~습니다/~입니다**로 통일. 숫자는 읽히는 대로("1,600킬로미터").
- 장면 1은 가장 강한 실제 영상 장면. 마지막 장면은 공유·구독 유도 한 문장.
- 소재 선정·표지(제목) 후킹·사진/영상 원칙·정치 유보·출처 표기는 카드뉴스 v3 스킬 그대로 따른다.
- 타입캐스트로 만들면 단어별 시각(with-timestamps API)으로 자막이 정확히 맞고, `emotion: smart`가 앞뒤 장면 문장을 보고 억양을 정합니다. Edge로 대체되면 글자 수 비율로 맞춥니다.
- 원본 영상 소리는 기본 끔(내레이션이 '의미 있는 편집'). 현장음이 핵심이면 `"audio": 0.3`.
