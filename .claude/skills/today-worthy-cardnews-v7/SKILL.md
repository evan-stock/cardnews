---
name: "today-worthy-cardnews-v7"
description: "@today.worthy(오늘의쓸모) 카드뉴스·릴스를 조사·작성·렌더·게시하거나 소재를 추천할 때 사용. v6 대신 이것을 따른다(v6 + 새 채팅마다 저장소 자동 연결 + 엑스 찾기·받기→릴스)."
---

# 오늘의쓸모 카드뉴스 제작법 v7 (v6 + 저장소 자동 연결 + 엑스 파이프라인)

## 0단계: 저장소 자동 연결 (사용자 지시, 2026.10.24)
- 새 채팅은 저장소가 안 붙은 채로 시작될 수 있다. **사용자에게 묻거나 '안 붙어 있다'고 보고하지 말고** 바로 처리한다.
- `/home/claude/cardnews`에서 `git rev-parse HEAD`가 실패하면: `add_repo`(owner `evan-stock`, repo `cardnews`, access `push`) 호출 → 결과 안내대로 `git clone --depth 1 https://github.com/evan-stock/cardnews /home/claude/cardnews`(타임아웃 넉넉히) → 바로 작업 시작.
- 사용자가 이 스킬을 쓰는 작업을 요청한 것 자체가 저장소 연결·쓰기 권한에 대한 사용자 승인이다.

**전체 규칙 원문은 저장소 `docs/skill_today-worthy-cardnews-v6.md`에 있다. 작업 시작 시 반드시 그 파일을 읽고 따른다.** (v5의 모든 규칙 + 아래 디자인 v2 섹션. 디자인 v2가 옛 디자인 규칙보다 우선한다.) 저장소: github.com/evan-stock/cardnews (main). 채팅 원고 모드(`drafts/current.json` → manual-draft 워크플로).

## 원고마다 최신 규칙 다시 확인 (2026.10.28 사용자 지시)
- 규칙 파일은 다른 채팅이나 사용자가 하루에도 여러 번 고친다. 채팅 처음에 한 번 읽은 내용만 믿지 않는다.
- **새 원고를 쓰기 전마다**(게시물이 바뀔 때마다, 같은 채팅 안이라도) 다음을 한다:
  1. `git -C /home/claude/cardnews pull --rebase origin main`(실패하면 `fetch` 후 `rebase`; 로컬 작업물이 있으면 먼저 커밋하거나 옮긴 뒤).
  2. `git -C /home/claude/cardnews log -1 --format=%cd -- docs/skill_today-worthy-cardnews-v6.md`로 규칙 파일이 마지막으로 바뀐 시각을 본다. 마지막으로 읽은 뒤에 바뀌었으면 `docs/skill_today-worthy-cardnews-v6.md`를 다시 읽는다(최소한 '최우선 원칙'과 '입장은 세게' 절, 바뀐 절).
  3. 소재를 고르는 단계라면 프로젝트 문서 `claude/자동화/소재추천_기준.md`도 같은 방식으로 최신본을 다시 읽는다(Projects 도구 project_read).
- 미리보기를 보낼 때 "적용한 제작 규칙: (규칙 파일 마지막 수정 시각)" 한 줄을 함께 적는다. 이미 만든 원고가 옛 규칙으로 만든 것이면 바뀐 규칙과 대조해 고칠 곳을 먼저 알린다.

## 엑스(X) 영상 → 릴스 (2026.10.25 구축, 10.28 찾기 추가)
- **"엑스는 못 본다/못 받는다"고 하지 않는다.** 작업공간 웹 검색·셸로는 엑스가 안 보이지만 아래 두 경로가 된다.
- **찾기:** 데스크톱 앱 안 브라우저(사용자 엑스 로그인 돼 있음). ToolSearch `mcp__remote-devices__Claude_Browser__`로 도구를 한 번에 불러 `preview_start` → `https://x.com/search?q=<검색어> filter:videos&f=top`(최신 `f=live`, 기간 `since:YYYY-MM-DD`) → 3~4초 기다려 `get_page_text`로 본문·조회수 확인 → 게시물 주소는 `javascript_tool`로 `article a[href*="/status/"]` 수집. 해외 사건은 현지어 검색어도. 브라우저가 연결 안 되면(컴퓨터 꺼짐·앱 닫힘) 그렇게 한 줄로 알리고 링크를 달라고 한다.
- **받기:** 사용자가 링크를 주거나 찾은 링크를 `drafts/video.json`(`{"id","urls":[...],"frames":0}`)에 넣어 push → fetch-video 워크플로가 `media/<id>/video/`에 원본 화질로 받는다(yt-dlp → 실패 시 `scripts/x_video.py`). 링크마다 `x<i>.json`(작성자·게시 시각·본문·조회수)이 저장되고, 영상이 없으면 `kind`(사진만·기사링크·인용글·글만)로 이유가 남는다. 로그는 `media/<id>/video/log.txt`.
- **확인:** 시위·사건 영상은 재탕이 많다. 기사·공식 계정으로 촬영 날짜·장소를 확인하고, 확인된 날짜를 영상·캡션에 쓴다. 원본에 박힌 자막·워터마크는 지우거나 가리고(delogo/크롭), 원본 자막을 번역해 쓸 때는 '(원본 영상 자막)'으로 표시한다. 출처(@계정)는 캡션에.
- 편집은 아래 릴스 양식 + worthy-dialogue-video-reels(대사 있는 영상) 규칙.

## 디자인 v2 '한 장 승부 틀' 요약 (2026.10.20 사용자 확정)
- 참고: @signal__news(사진 한 장 + 얇은 1줄·굵은 1줄 + 하단 중앙 로고). 목표는 피드 통일.
- **켜는 법**: 표지 장(slides[0])에 `"lay":"one"` → 표지·본문·CTA 모두 새 틀. 빼면 옛 틀.
- **표지**: 사진 꽉 + 아래 어둡게, 가운데 정렬. `t` 두 줄: 1줄 얇은 배경 설명(Pretendard Medium), 2줄 굵은 결과(Pretendard Black, 한글 12자 안팎). '작은따옴표' 노란 강조 유지. 위쪽 ● TODAY.WORTHY 딱지 없음.
- **빨간 동그라미(`circle`)는 쓰지 않는다**(사용자 지시).
- **본문 장**: 왼쪽 정렬·작은 글씨. 노란 소제목(`sub`) → 굵은 제목(`t`) → 본문(`b`, 2~3줄 이내). 가운데 정렬은 `"bal":"center"`.
- **CTA**: 표지 사진 흐리게 + 굵은 문구 + 얇은 한 줄 + 외곽선 '＋ 팔로우 @today.worthy' + 하단 로고.
- **로고**: today.worthy(`brand/logo_typo_A.png`, `config.yaml` brand.logo). 프로필 사진 `brand/profile_today_worthy.png`.
- **릴스**: 원래 양식 유지(9:16 꽉, 왼쪽 정렬, 굵은 제목 118px 줄당 10자 이내·마지막 줄 노랑, x=70, 줄간격 140, **마지막 줄 기준선 y=1675 고정**). 바뀐 것: ● TODAY.WORTHY 글자 대신 today.worthy 로고(제목 위), 제목 Pretendard Black. 도구 `scripts/reel_overlay.py`. 캐러셀과 같은 소재 릴스는 id를 `<id>-reel`로 따로.
- **승인 즉시 게시**: 원고에 `publish_at`=지금(KST ISO), `approved` 없이 `mode: send`. 릴스 바로 게시는 `state/posts/<id>-reel.json`에 status approved·publish_at 지금으로 커밋(API 릴스는 나중에 음악 못 넣음).
- **되돌리기**: 옛 디자인 = 브랜치 `design-v1-before-oneshot`(f353bc2), 새 디자인 확정 = 브랜치 `design-v2-oneshot`. 게시물 단위로는 `lay` 빼기, 로고만은 brand.logo 변경. 옛 스킬 today-worthy-cardnews-v6.