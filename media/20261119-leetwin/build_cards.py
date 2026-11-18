"""시나리오 A: 리트냥이 생중계 검증 '정면 돌파 성공'(만점/고득점). 11.19 결과 나오면 CFG만 채우고 실행.
근거: IDA 공식 공지(11.16), 연합(법전원협의회), 주간경향(밀린 답), 위키트리(다른 과목도 풀겠다), @deoksu_kr 엑스 글."""
import json, subprocess, sys
exec(open(__import__('pathlib').Path(__file__).parent / "_common.py").read())

CFG = {
    "score": "○○",          # 예: "100" (만점이면 아래 perfect=True)
    "perfect": True,
    "common": "○○", "hwajak": "○○", "eonmae": "○○",   # 맞힌 문항 수
    "left_min": "○○",        # 남긴 시간(분)
    "live_shot": "lee_photo.jpg",   # 내일 생중계 화면 캡처로 교체(cand/ 안)
    "qa_shot": "lee_photo.jpg",     # 강사 질문 장면 캡처로 교체
    "qa_line": "막힘없이 '근거'를 댔다",   # 실제 장면 보고 고침
}
c = CFG
res = "'만점'" if c["perfect"] else f"'{c['score']}점'"

frame(("65분 · 56문항, 전 과정 생중계", f"리트냥이 수능 국어 {res}"),
      fit(op(O / c["live_shot"]), 940, 700, (.5, .2)),
      "귀 내시경·전파탐지 '통과'하고 받은 점수", "IDA입시연구소 유튜브 생중계(11.19)").save(O / "c02.jpg", quality=93)

frame(("일반 수험생보다 15분 덜 받고", "11문항 더 풀었다"),
      panel([("공통 34문항", f"'{c['common']}'개 맞힘"),
             ("화법과 작문 11문항", f"'{c['hwajak']}'개 맞힘"),
             ("언어와 매체 11문항", f"'{c['eonmae']}'개 맞힘"),
             ("65분 중 남긴 시간", f"'{c['left_min']}'분")], h=640),
      "국어 전문강사 직접 채점 · 교차 검산", "IDA입시연구소 생중계").save(O / "c03.jpg", quality=93)

frame(("마지막 관문, 1타 강사의 질문", "\"이 답, '왜' 골랐어요?\""),
      fit(op(O / c["qa_shot"]), 940, 700, (.5, .2)),
      c["qa_line"], "무작위 3~5문항 정답 근거·오답 제외 이유 설명").save(O / "c04.jpg", quality=93)

spec = [{"out": str(O / "c05.jpg"), "sub": "어젯밤 엑스", "title": "\"사기꾼 엔딩 말고\n'초천재의 탄생'이 보고 싶다\"",
         "cap": str(O / "cap_deoksu.jpg"), "cap_max_h": 620, "caption": "@deoksu_kr 게시물 캡처",
         "label": "통과하면 '10가지 미래'까지 예언",
         "lines": ["밀리언셀러부터 노벨상까지, 응원 섞인 농담이 돌았습니다."]}]
json.dump(spec, open(O / "cap_spec.json", "w"), ensure_ascii=False)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "cap_spec.json")], check=True)

frame(("실력은 증명했다, 그런데", "그래도 '남는 질문'"),
      panel([("주관사 IDA", "이번 결과로 과거 리트 의혹 '확정 못 해'"),
             ("리트 시험지", "25~29번 '밀린 답' 흔적은?"),
             ("법전원협의회", "\"시험 당시 적발 안 돼, 조사 사안 아냐\""),
             ("본인 예고", "\"수능 '다른 과목'도 풀겠다\"")], h=640),
      "오늘 증명한 건 '오늘의 실력'", "IDA 공지·주간경향·연합뉴스·위키트리").save(O / "c06.jpg", quality=93)

fit(op(O / c["live_shot"]), W, H, (.5, .2)).save(O / "cover_bg.jpg", quality=95)
print("ok")
