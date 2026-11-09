---
name: "sns-auto-posting-pipeline"
description: "SNS 자동 게시 파이프라인(인스타·스레드·쿠팡파트너스 글 등)을 GitHub Actions 무료 실행 + 텔레그램 승인 + 채팅 원고 모드로 처음부터 구축할 때 사용."
---

# SNS 자동 게시 파이프라인 구축법

'오늘의쓸모' 인스타 카드뉴스 자동화(github.com/evan-stock/cardnews)를 만들며 검증한 구조. 스레드, 쿠팡파트너스 글 자동 게시 등 새 채널에 그대로 재사용한다.

## 1. 전체 구조 (컴퓨터 안 켜도 돌아가게)
- **실행:** GitHub Actions. 공개 저장소면 무료. cron은 UTC 기준(한국시간 −9시간).
- **상태 저장:** 저장소 안 `state/posts/{YYYYMMDD-slot}.json`. 실행 끝에 `git add state media && commit && pull --rebase && push`.
- **미디어 공개 주소:** `raw.githubusercontent.com/{owner}/{repo}/main/media/...`. 인스타·스레드 API는 공개 URL의 이미지를 가져가므로 공개 저장소가 가장 간단하다.
- **비밀값:** 전부 GitHub Secrets. 토큰을 채팅에 붙여넣게 하지 않는다. Secrets 화면에서 Name은 대문자 키(예: `IG_ACCESS_TOKEN`), Secret에 실제 값을 넣는다고 명확히 안내한다.
- **승인:** 텔레그램 봇. sendMediaGroup으로 미리보기와 인라인 버튼(✅ `ok:id`, ❌ `no:id`)을 보내고, getUpdates로 결정을 폴링한다. offset은 state 파일에 저장하고, 내 TELEGRAM_CHAT_ID만 허용한다. 승인과 거절 모두 텔레그램으로 확인 메시지를 보낸다(안 보내면 사용자는 "눌렀는데 반응 없음"으로 느낀다).
- **명령 구조:** `prepare`(조사 → 미디어 → 렌더 → 미리보기), `tick`(승인 반영, 시간 되면 게시, 만료), `watch`(tick을 1분마다, 대기 게시물이 없으면 종료), `publish --id`(수동 즉시 게시), `ping`(연결 테스트).

## 2. 반드시 넣을 것 (실제로 터진 문제들)
1. **GitHub 예약 실행은 믿지 말 것.** `*/10` 같은 잦은 cron은 새 저장소에서 몇 시간씩 안 돈다. 해결: prepare 직후 같은 job에서 `watch`를 돌려 게시가 끝날 때까지 1분 간격으로 확인한다(timeout-minutes 360). 예비 cron은 3시간 간격 정도만 둔다.
2. **concurrency 그룹을 분리한다.** 게시 감시(watch)가 길게 도니까, 채팅 원고 렌더 워크플로는 다른 그룹을 쓴다. 대기 중인 run은 새 run에 밀려 취소될 수 있다는 점도 고려한다.
3. **수동 실행은 강제 재생성(--force).** 같은 슬롯에 이미 게시물이 있으면 prepare가 조용히 건너뛰어 "알림이 안 온다"는 오해가 생긴다. workflow_dispatch일 때만 force를 준다.
4. **실패하면 텔레그램으로 알린다.** 에러 앞 500자 + "Actions 로그 확인" 안내.
5. **Pillow는 requirements에 명시한다.** ImportError를 except로 삼키면 이미지가 전부 조용히 탈락한다. 예외는 로그로 남긴다.
6. **로그 확인:** `gh run view --log`가 막히면 결과를 state/media 파일로 커밋해서 확인한다. 디버그 전용 워크플로(파일 push로 트리거)가 유용하다.
7. **gh CLI의 GraphQL이 막힌 환경:** workflow 실행은 `gh api -X POST repos/{o}/{r}/actions/workflows/{file}/dispatches -f ref=main -f 'inputs[cmd]=...'`로 한다.

## 3. 비용 0원 '채팅 원고 모드' (주력으로 쓰기)
자동 조사(Claude API + web_search)는 회당 약 $0.3~0.6이 든다. 퀄리티를 다듬는 단계에서는 채팅에서 직접 만든다.
- Claude가 채팅에서 조사하고 문구를 쓴 뒤 `drafts/current.json`(여러 개면 목록)을 push → `manual-draft` 워크플로가 렌더링(API 비용 없음).
- mode 단계:
  - `collect`: 기사 페이지에서 후보 사진을 모아 번호 붙인 모아보기(candidates.jpg)를 만든다. `read_pages`로 본문 텍스트도 저장한다(네이버처럼 직접 못 여는 사이트용, r.jina.ai 대체 경로 포함).
  - `render`: 장마다 지정한 사진(후보 번호, 이미지 URL, 이전 커밋의 raw URL)으로 렌더한다.
  - `send`: 텔레그램 전송 + 게시 대기. `publish_now: true`면 승인 없이 바로 게시한다.
- Claude는 모아보기 이미지를 직접 보고 사진을 고르고, 결과 카드도 직접 보고 확인한 뒤 사용자에게 보여준다.
- 사이트가 막혀 사진을 못 받으면(아카라이브 등) 참고 이미지를 쓰고 본문에 "참고 이미지"라고 밝히거나, 사용자에게 사진을 올려달라고 한다.

## 4. 플랫폼별 메모
- **인스타그램 (Instagram API with Instagram Login):** `graph.instagram.com/v25.0`. 항목 컨테이너(image_url, is_carousel_item) → CAROUSEL 컨테이너 → status_code가 FINISHED가 될 때까지 폴링 → media_publish → permalink. 토큰은 60일이라 `refresh_access_token`을 주기적으로 호출하고, 갱신 값을 `gh secret set`으로 저장한다(GH_PAT 필요). 메타 앱에서 계정을 '관리자'가 아니라 **Instagram 테스터**로 초대한 뒤, 인스타 앱에서 초대를 수락하고 토큰을 생성한다. 계정은 프로페셔널이어야 한다. 올린 게시물의 사진은 API로도 앱으로도 교체할 수 없고 삭제도 API로는 안 된다(본문만 수정 가능).
- **스레드 (Threads API):** 구조가 인스타와 거의 같다. `graph.threads.net/v1.0/{user-id}/threads`에 컨테이너 생성(media_type TEXT/IMAGE/CAROUSEL, text, image_url) → `threads_publish`. 글자 수 500자 제한, 24시간 게시 한도가 있다. 시작 전에 최신 공식 문서로 엔드포인트와 권한(threads_basic, threads_content_publish)을 확인한다.
- **쿠팡파트너스 글:** 게시물마다 "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다." 같은 대가성 문구가 들어가야 한다(공정위 추천·보증 심사지침). 링크와 가격은 생성 시점 기준이라 오래된 가격을 단정하지 않는다. 쿠팡 파트너스 API 사용 조건과 플랫폼의 제휴 링크 정책을 시작 전에 확인한다.

## 5. 설치 안내 순서 (사용자에게 한 번에)
1. GitHub 저장소(공개) 생성 → Claude GitHub App 설치 → Settings > Actions > Workflow permissions를 Read and write로.
2. 텔레그램 BotFather에서 봇 토큰 → 봇에게 메시지 → getUpdates로 chat id 확인.
3. 플랫폼 API 토큰과 사용자 ID 발급.
4. Secrets 등록(Name/Secret 구분 안내). GH_PAT는 github.com/settings/personal-access-tokens/new에서 해당 저장소, Secrets 권한 Read and write.
5. Anthropic 콘솔 사용 한도 설정($5~10).
6. `ping` → `prepare` → ✅ → `publish` 순서로 시험.

## 6. 소재 알림
매일 소재 추천은 Claude 예약 작업(scheduled task)으로 돌린다. API 비용이 들지 않고 앱 푸시로 알림이 오며, 결과는 프로젝트 문서로 저장된다. 날짜는 반드시 KST로 적게 지시한다(안 그러면 UTC 날짜로 저장돼 하루 밀려 보인다). 게시 시간보다 4~5시간 앞에 돌린다.