"""Claude API(웹 검색·웹 페치)로 오늘의 소재 1개를 골라 카드 문구까지 작성."""
import json
import re

import requests

from .common import CFG, env, now, recent_topics

API = "https://api.anthropic.com/v1/messages"

SYSTEM = """당신은 인스타그램 카드뉴스 채널 "{channel}"({handle})의 편집장입니다.
반드시 웹 검색과 웹 페이지 열람으로 사실을 확인한 뒤 작성합니다. 확인하지 못한 사실·수치·발언은 절대 쓰지 않습니다."""

PROMPT = """지금은 {now} (한국 시간)입니다. {slot_name} 게시물로 올릴 카드뉴스 소재 1개를 골라 완성해주세요.

[소재 선정: 제일 중요]
"개노잼"이면 실패입니다. 친구 단톡방에 바로 퍼 나르거나 댓글로 싸움이 붙을 소재만 고릅니다.
1) 먼저 web_search로 지금(최근 3~7일) 실제로 터진 이야기 후보를 6개 이상 모으세요. 찾을 곳: 네이버·다음 많이 본 뉴스, 더쿠·네이트판·인스티즈·에펨코리아 인기글이 된 기사, X(트위터) 트렌드, 해외는 Daily Mail·NY Post·Reddit 인기 뉴스.
2) 후보마다 속으로 점수를 매겨 가장 높은 것 하나만 고르세요: 반전·충격(숫자, 금액, 결말이 세다) / 셀럽·유명인 / 돈(연봉, 부동산, 코인 대박·폭망, 사기) / 분노·논쟁(누가 잘못했나 편이 갈림) / 공감·찜찜함(나라면?).
3) 공유 테스트(가장 중요): "이걸 보고 친구 한 명이 바로 떠올라 DM으로 보내고 싶나?" 아니면 탈락. 신규 계정은 비팔로워에게 퍼져야 하고, 그 신호가 DM 공유입니다.
   비중 참고: 해외 황당·기묘 인물 사연 40% / 국내 셀럽·사회 공감·분노 논란 30% / 숫자·반전 인물 서사(돈·성공·몰락) 20% / 정치·코인 10% 이하(초대형 바이럴일 때만, 정치 콘텐츠는 비팔로워 추천이 제한됨). 분야: {categories}
   읽고 끝나는 정책·시세·지표 뉴스는 고르지 않습니다. 주인공(얼굴이 나오는 사람)이 있는 이야기를 우선합니다.
4) 탈락: 결말이 밋밋한 귀여운 동물 해프닝, "~한 일이 있었다" 수준의 잔잔한 소식, 1주일 넘은 이야기(엄청 크게 바이럴된 것 제외), 설명해야 웃긴 이야기.
5) 표지만 봐도 "헐 뭐야" 하고 넘겨보게 만드는 한 방(숫자·반전·실명)이 있어야 합니다.

[제외]
참사·범죄 피해자를 웃음거리로 삼는 소재, 특정 집단 혐오 조장, 공인이 아닌 일반인 신상 노출, 노골적인 성적 소재, 확인 안 된 루머.
최근에 이미 다룬 소재(겹치면 안 됨): {recent}

[검증]
신뢰할 수 있는 언론 기사 원문을 web_fetch로 직접 열어 사실·숫자·연도를 확인하세요(최소 1개, 가능하면 2개). 의혹이면 "~라는", "주장"으로.

[카드 구성: 정확히 {n}장]
- 1장 표지: t=2~3줄 제목, 줄바꿈은 \\n. 한 줄에 한글 11자 이내. '누가 + 무엇이 얼마나 이상한가'를 한 문장에. 이야기체 단정형("~했다", "~라는 남성", "~한 이유"), 핵심어 하나를 작은따옴표 '...'로 감싸기(노란색으로 강조됨). 물음표·일반론("모르면 손해") 금지. b=빈 문자열.
  예: "월급 200 신입이\\n'코인'으로 47억 벌고 퇴사", "결혼식 축의금 5만원 냈다가\\n'손절'당한 이유", "복권 440억 당첨자가\\n'인형탈' 쓰고 나타났다"
- 2장은 '두 번째 표지': 인스타는 첫 장을 안 넘긴 사람에게 2장을 다시 보여줍니다. 가장 충격적인 장면 사진 + 그 자체로 궁금해지는 한 줄 t(배경 설명 금지).
- 3~{m}장: 내용 장. 장마다 최소 t 한 줄은 넣어, 사진만 봐도 이야기가 따라가지게 합니다. 이야기를 순서대로 풀어요. t=한 줄 소제목(한글 14자 이내, 핵심 단어 하나 '...'로 노란 강조), sub=굵은 한 줄 요약(20자 이내), b=설명 2~4문장(150자 이내, 사실만, 핵심 구절은 **...**로 굵게). 정보형(과학·경제·사건 경위)은 b를 충분히, 가벼운 소재는 1~2문장.
  예외: 신기한 사진 모음이면 sub·b는 비워도 되지만 t 한 줄은 넣습니다.
- {n}장 마지막 카드: t="생각나는 친구에게 보내주세요", b="팔로우하면 매일 화제 소식"
- 장마다 사진 정보: photo_query=위키미디어 커먼즈에서 찾을 영어 검색어(2~5단어, 실존 인물이면 이름 그대로, 아니면 이야기에 맞는 구체적인 사물·장소·동물), 표지·2장은 주인공 얼굴(표정)이 크게 나오는 사진을 우선, ai_prompt=사진이 없을 때 쓸 영어 이미지 생성 프롬프트(실사 사진 느낌, 이야기의 한 장면, 실존 인물 얼굴·글자·로고 없음, 세로 4:5). 장마다 다른 장면이어야 합니다.

[사진 확보]
카드 배경은 기사·영상 원본 사진을 그대로 씁니다. image_pages에 이 이야기의 사진이 많이 실린 기사(해외 원문 기사, 데일리메일·뉴욕포스트처럼 사진을 많이 싣는 매체 포함)와 원본 유튜브·틱톡 영상 링크를 3~6개 넣으세요. web_search로 찾은 실제 주소만 쓰세요.

[게시물 본문: 설명은 여기에]
- caption: "[표지 내용을 한 문장으로 풀어쓴 제목]" + 빈 줄 + 문단 1(누가·어디서·언제·무엇을) + 빈 줄 + 문단 2(흥미로운 디테일) + 빈 줄 + 문단 3(반응·의미) + 빈 줄 + 참여 질문 한 줄(A/B로 답할 수 있는 질문, 예: "여러분은 가능 vs 불가능?") + 빈 줄 + "생각나는 친구에게 보내주세요! 팔로우하면 매일 화제 소식을 먼저 받아볼 수 있어요.". 존댓말 기사체("~했습니다"), 문단당 2~3문장, 출처·해시태그는 넣지 말 것, 700자 이내.
- hashtags: 3~5개, # 없이(인스타 상한 5개). 넓은 태그(#카드뉴스 등) 대신 주인공 이름·구체적 주제.
- 코인·주식 소재면 caption 끝에 "※ 투자 권유 아님, 정보 제공 목적" 추가.

모든 조사를 마친 뒤, 마지막 답변에는 아래 JSON 하나만 ```json 코드블록으로 출력하세요.
{{"topic":"소재 한 줄 요약","category":"분야","core":"핵심 한 문장","why":"왜 반응이 클지 한 줄",
"slides":[{{"t":"","sub":"","b":"","photo_query":"","ai_prompt":""}}],
"caption":"","hashtags":[""],
"sources":[{{"publisher":"언론사","title":"기사 제목","url":"","date":"YYYY.MM.DD"}}],
"image_pages":["사진 확보용 링크 3~6개: 같은 이야기를 다룬 다른 언론 기사(사진이 많은 것), 원본 유튜브·틱톡 영상 주소"],
"risk":"사실관계·명예훼손 위험 등 사람이 승인 전에 확인할 점 한 줄 (없으면 빈 문자열)"}}"""

SLOT_NAMES = {"lunch": "점심 1시", "evening": "저녁 6시"}


def _call(messages, system):
    r = requests.post(
        API,
        headers={
            "x-api-key": env("ANTHROPIC_API_KEY"),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": CFG["research"]["model"],
            "max_tokens": CFG["research"]["max_tokens"],
            "system": system,
            "messages": messages,
            "tools": [
                {"type": "web_search_20250305", "name": "web_search",
                 "max_uses": CFG["research"]["web_search_max_uses"],
                 "user_location": {"type": "approximate", "country": "KR", "timezone": "Asia/Seoul"}},
                {"type": "web_fetch_20250910", "name": "web_fetch",
                 "max_uses": CFG["research"]["web_fetch_max_uses"], "max_content_tokens": 20000},
            ],
        },
        timeout=600,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Claude API 오류 {r.status_code}: {r.text[:500]}")
    return r.json()


def extract_json(text):
    m = re.search(r"```json\s*(\{.*\})\s*```", text, re.S) or re.search(r"(\{.*\})", text, re.S)
    if not m:
        raise ValueError("응답에서 JSON을 찾지 못했어요")
    return json.loads(m.group(1))


def validate(d, n):
    if not isinstance(d.get("slides"), list) or len(d["slides"]) < 4:
        raise ValueError("슬라이드가 부족해요")
    d["slides"] = d["slides"][:n]
    for s in d["slides"]:
        s["t"] = str(s.get("t", "")).replace("\\n", "\n").strip()
        s["b"] = str(s.get("b", "")).strip()
        s.setdefault("photo_query", "")
        s.setdefault("ai_prompt", "")
    if not d.get("sources"):
        raise ValueError("출처가 없어요")
    d["hashtags"] = [h.lstrip("#").replace(" ", "") for h in d.get("hashtags", []) if h][:5]
    return d


def research(slot):
    n = CFG["research"]["slides"]
    system = SYSTEM.format(channel=CFG["brand"]["channel_name"], handle=CFG["brand"]["handle"])
    prompt = PROMPT.format(
        now=now().strftime("%Y-%m-%d %H:%M"), slot_name=SLOT_NAMES.get(slot, slot),
        categories=", ".join(CFG["research"]["categories"]),
        recent="; ".join(recent_topics(CFG["research"]["avoid_days"])) or "(없음)",
        n=n, m=n - 1)
    messages = [{"role": "user", "content": prompt}]
    for _ in range(8):  # pause_turn 이어가기
        resp = _call(messages, system)
        if resp.get("stop_reason") == "pause_turn":
            messages.append({"role": "assistant", "content": resp["content"]})
            continue
        break
    text = "".join(b.get("text", "") for b in resp["content"] if b.get("type") == "text")
    return validate(extract_json(text), n)
