---
name: "life-comment-shorts"
description: "'인생 댓글로 정함'(김댓글, 댓글 1등대로 사는 아기) 유튜브 쇼츠의 투표 결과 확인·다음 화 대본·3D 장면 렌더·목소리·새 봇 발송·업로드를 할 때 사용."
---

# 인생 댓글로 정함 쇼츠 제작법 (v1.1, 2026.10.24)

답변은 항상 한국어 존댓말. **사용자를 '형'·'형님'이라고 부르지 않는다**(사용자가 두 번 지적함). 호칭 없이 말한다.
사용자가 직접 해야 하는 일(로그인, 권한 허용, 비밀값 등록, 텔레그램 버튼)만 요청하고 나머지는 Claude가 한다. 설명은 아주 쉽게, 복사·붙여넣기 할 수 있게.
결정 기록: 프로젝트 문서 `claude/댓글로키우는아이_결정사항.md` (있으면 먼저 읽는다).

## 채널
- 채널: **인생 댓글로 정함** (@인생댓글로정함), 새 구글 계정. 저장소 키 `life`. 1화: https://youtube.com/shorts/f2xDoYC2BBU (2026.10.23 게시).
- 주인공 **김댓글**: 3D 동글 아기, 트레이드마크 = 정수리에 돌돌 말린 머리 한 가닥(모든 나이에서 유지).
- 가족: 아빠 회사원(안경·정장), 엄마 분식집 사장(똥머리·앞치마), 통장 87만 원.
- 매일 1화. 매 화 끝에 갈림길(선택지 2~3개) → 다음 날 **저녁 7시(19:00)** 마감 → 댓글 1등대로 다음 화(2026.10.24 사용자 결정).

## 톤 (사용자 결정)
- **웃기고 어그로 끄는 예능 톤.** 잔잔한 이야기·동화 내레이션 금지.
- 해설 = 타입캐스트 '박창수' **느낌**: 무뚝뚝하고 시큰둥한 아저씨가 정색하고 툭툭 던짐. **사투리는 쓰지 않는다**(표준어).
- 귀여운 아기 vs 시큰둥한 해설의 대비가 웃음 포인트.
- 대본 예(1화): "애가 하나 태어났습니다. 근데 이 애 인생, 이제 댓글 단 사람들이 정한대요." / "이름은 김댓글. 이름부터 망했네요." / "통장엔 87만 원. 네, 그게 다예요." / "안 정하면 그냥 아무거나 잡혀요."
- 한 화 20~30초, 장면 5개 안팎, 문장 짧게. 숫자는 say 에는 읽는 대로("팔십칠만"), sub 에는 숫자("87만").
- 갈림길 소재는 한국식 인생 이벤트 위주(돌잡이, 어린이집, 초등 입학, 수능, 군대, 취업, 결혼, 환갑…). 과거 선택이 나중에 돌아오는 복선을 넣는다.

## 댓글 투표 규칙 (사용자 확정)
- **선택지를 말한 댓글 중 좋아요가 가장 많은 댓글 1개**가 이긴다(설명란 "댓글 1등(좋아요 가장 많은 댓글)"과 같음).
- 동률이면 그 선택지 전체 지지(그 선택지 댓글 수 + 좋아요 합)가 큰 쪽, 그래도 같으면 먼저 쓴 댓글.
- 선택지를 말하지 않은 댓글은 후보 아님. 욕설·혐오·성적·링크·도배 댓글은 자동 제외(`cardnews/life_vote.py` BAD, 원고 `vote.ban` 으로 추가).
- 채널 주인 댓글·같은 사람 두 번째 댓글 제외.
- 선택지 댓글이 없으면 김댓글이 직접 고르는 편.
- 사용자가 "2등으로 가" / "n번으로 바꿔"라고 하면 그대로 따른다(최종 결정은 사용자).
- 자동 집계: `.github/workflows/life-vote.yml` 매일 19:00 KST → 새 봇으로 결과, `state/life_votes/<id>.json` (winner.comment = 글·닉네임·좋아요). 수동: life-vote 워크플로 dispatch (`gh api -X POST repos/evan-stock/cardnews/actions/workflows/life-vote.yml/dispatches -f ref=main`, id 입력 가능).

## 저장소·환경 (evan-stock/cardnews, main)
- 쓰기 필요: `add_repo` 로 access="push" 첨부 → `/home/claude/cardnews` 에 clone. 작업 공간은 인터넷이 막혀 Gemini·타입캐스트·유튜브를 직접 못 부른다. 목소리·업로드는 GitHub Actions 가 한다.
- 커밋 전 `git fetch origin main && git rebase origin/main`, 그다음 push.
- `gh workflow run` 은 GraphQL 이 막혀 안 됨 → `gh api -X POST repos/evan-stock/cardnews/actions/workflows/<file>/dispatches -f ref=main ...` 사용.

## 매일 자동으로 오는 것
- 매일 19:23 KST 예약 작업 '인생 댓글로 정함: 댓글 1등 알림 + 다음 화 원고 초안'이 투표 결과와 다음 화 원고 초안을 보내고, 프로젝트 문서 `claude/인생댓글로정함_원고/(날짜)_N화_초안.md` 에 저장한다(렌더·발송은 안 함).
- 사용자가 "N화 만들어"라고 하면 그 초안을 읽고 아래 순서 3번부터 진행한다(초안을 바꾸라는 말이 있으면 반영).

## 제작 순서 ("N화 만들어")
1. **투표 결과 확인**: `git pull` 후 `state/life_votes/<직전 id>.json` 읽기(없으면 life-vote 를 수동 실행). 1등 선택지·1등 댓글을 사용자에게 한 줄로 보여준다.
2. **대본**: 장면 1 = '어제 댓글 1등' 카드(댓글 글·닉네임·♥, 해설 "어제 댓글 1등, ♥32개. 마이크 잡았습니다."). 장면 2~4 = 그 선택의 결과(웃긴 반전). 마지막 장면 = 다음 갈림길 + 선택지 1·2·3 + "댓글 1등대로 갑니다".
3. **3D 스프라이트**: 필요한 캐릭터·소품만 렌더.
   - 아기: `python3 scripts/story_shorts/life_3d.py <폴더> 600` (표정 happy/blink/cry/o, 장당 약 1분)
   - 돌복 아이·아빠·엄마·소품: `python3 scripts/story_shorts/life_3d2.py <폴더> [이름…]` (tod_o tod_blink tod_proud dad dad_blink mom mom_blink pencil money mic)
   - 새 나이·옷·소품은 life_3d2.py 의 Char/Item 패턴으로 클래스를 추가한다. 같은 HEAD·EYE·CURL 을 써서 얼굴이 같게.
   - 2 vCPU 에서 오래 걸리면 두 프로세스로 나눠 백그라운드 실행.
4. **장면 영상**: `scripts/story_shorts/anim_life_ep1_v3.py` 를 본떠 `anim_life_epN.py` 작성(V1/V2 의 put·label·pill·bubble·breathe, 배경 bg_nursery/bg_living/bg_dol/bg_vote, 3D 스프라이트 load). 띠 아래 영역 1080×1490, 자막 자리 y≈760~1050 비움.
   - 파이프라인용은 `LIFE_HOLD=3` 으로 장면을 여유 있게 길게 렌더 → `media/<id>/video/s1.mp4…` 에 복사(실제 길이는 목소리에 맞춰 잘림).
   - 렌더 후 프레임을 직접 확인(글자 깨짐·겹침·잘림). 주아체에 없는 글자(₩, ·, →, ①)는 피한다.
5. **원고** `drafts/life.json`:
   ```json
   {"id": "YYYYMMDD-lifeN", "mode": "render", "topic": "인생 댓글로 정함 N화",
    "hook": {"t": "인생 댓글로 정함 N화\n<짧은 한 줄, '강조'는 노랑>"},
    "voice": {"engine": "gemini", "gemini": {"voice": "Fenrir", "tempo": 1.25, "volume_db": 3.0,
      "style": "예능 자막 읽듯 툭툭 던지는 아저씨 말투. 빠르게, 쉬지 말고. 대부분은 시큰둥하게 정색하다가 마지막 질문은 도발하듯."}},
    "style": {"mascot": null},
    "scenes": [{"say": "…", "sub": "…(숫자 표기)", "video": {"src": "video/s1.mp4", "start": 0, "fit": "fill"}, "sfx": [{"f": "pop", "at": 0.4}]}],
    "vote": {"deadline": "다음 날 19:00", "options": [{"n": 1, "name": "…", "kw": ["…"]}, …]},
    "yt": {"title": "인생 댓글로 정함 N화: …", "description": "…선택지 1/2/3…\n내일 저녁 7시까지 댓글 1등(좋아요 가장 많은 댓글)대로 N+1화에서 …", "tags": ["인생댓글로정함", "김댓글", "댓글투표", …], "privacy": "public", "channel": "life"},
    "publish_now": true}
   ```
   - 먼저 `mode: render` 로 push → `life-shorts.yml` 이 렌더 → `media/<id>/short.mp4` 를 pull 해서 사용자에게 보여준다(SendUserFile).
   - 확인되면 `mode: send` 로 push → 새 봇으로 미리보기 + [✅ 업로드] → 사용자가 누르면 pipeline watch 가 새 채널에 업로드. 업로드 후 `mode: sent` 로 바꿔 재발송 방지.
   - 대사가 같으면 목소리 저장본을 재사용(Gemini 한도 절약). Gemini 무료 한도 하루 약 10회, 털뭉치 대체 목소리와 공유. 영상 1편 = 1회.
6. **확인 마지막**: `state/posts/<id>.json` 의 status·permalink 로 게시를 확인하고 링크를 알려준다.

## 화면
- 위 검정 띠 430px, 제목 2줄(1줄 노랑, 2줄 흰, '작은따옴표' 노랑). life 채널은 config `shorts.channels.life.style = {title_pad_bottom: 40, title_size: 76}` 으로 제목을 띠 아래쪽에 붙여 폰 상태바·검색 아이콘과 안 겹치게(2화부터).
- 자막 주아체, 마스코트 없음.
- 프로필은 큰 이정표(돌·초등·중학생·성인)에만 바꾼다. 배너는 성장 기록판으로 자주 바꿔도 된다.

## 운영 주의
- 승인 감시(pipeline watch)는 한 번에 하나, 최대 6시간. 새 봇 버튼이 안 먹히면 오래된 watch 실행이 옛 코드로 돌고 있는지 확인.
- GitHub 러너가 설치 단계에서 멈추는 날이 있다. 같은 워크플로가 한 번에 하나만 돌아서 뒤가 밀린다 → `gh api repos/evan-stock/cardnews/actions/runs?per_page=20` 로 멈춘 실행을 찾고, 사용자 허락을 받아 `gh api -X POST …/runs/<id>/cancel`.
- 텔레그램 봇: 게시물 yt.channel=life 이면 `TELEGRAM_BOT_TOKEN_LIFE`(새 봇)로 보낸다. 유튜브는 `YT_REFRESH_TOKEN_LIFE`. 토큰을 다시 받아야 하면 맥 터미널에 `curl -fsSL https://raw.githubusercontent.com/evan-stock/cardnews/main/scripts/yt_token.py -o /tmp/yt_token.py && python3 /tmp/yt_token.py` (구글 클라우드 보안 비밀은 다시 볼 수 없어 Add secret 으로 새로 만든다. 기존 두 개는 털뭉치용이라 건드리지 않는다).
- AI 이미지·영상 생성은 쓰지 않는다(편당 크레딧 0원이 원칙). 블록·마인크래프트풍은 '직업도감'과 겹쳐 쓰지 않는다.

## 하지 않는 것
- '형' 호칭, 사투리, 잔잔한 동화 내레이션, 1등 댓글 원문 캡처 그대로 붙이기(댓글 모양으로 다시 그린다, 프로필 사진 없음), 욕설·혐오 댓글 소개, 투표 결과 임의 변경(사용자 지시 없이), 사용자 확인 없이 업로드.