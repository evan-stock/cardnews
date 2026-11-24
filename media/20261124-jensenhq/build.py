"""20261124-jensenhq: 젠슨 황 본사 복귀 — 직원 영상 2개 + CNBC 캡처 2장."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; O.mkdir(exist_ok=True)
T = Path("/tmp/claude-tool-results/a493c683-e7b1-5bd7-9aa7-411f6fdd042e")
def shot(name, box, out):
    Image.open(T / f"mcp-claude-in-chrome-blob-{name}.jpg").convert("RGB").crop(box).save(O / out)
shot("1795476676520-o0t5wz-e9f95937", (35, 25, 840, 520), "cap_cnbc1.png")
shot("1795476687001-b34jqk-aecf658d", (35, 25, 840, 380), "cap_cnbc2.png")
# 표지·CTA 배경용 정지 화면(영상 첫 장면 4:5)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", str(D / "video/v1.mp4"), "-frames:v", "1",
                "-vf", "scale=1080:-2,crop=1080:1350:0:(in_h-1350)/2", str(O / "cover.jpg")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "9", "-i", str(D / "video/v2.mp4"), "-frames:v", "1",
                "-vf", "scale=1080:-2,crop=1080:1350:0:(in_h-1350)/2", str(O / "hug.jpg")], check=True)

W = [255, 255, 255]
spec = [
 {"out": str(O / "c_cnbc1.jpg"), "sub": "젠슨 황의 첫마디 · CNBC", "box_bg": W,
  "title": "\"두 번째 기회 고맙다\n'더 나은 CEO' 되겠다\"", "cap": str(O / "cap_cnbc1.png"),
  "caption": "CNBC 기사 캡처", "label": "사무실엔 'Jensen is back' 컵케이크",
  "lines": ["3개 층을 채운 직원들이 이름을 연호", "CNBC가 입수한 직원 영상 기준"], "cap_max_h": 520},
 {"out": str(O / "c_cnbc2.jpg"), "sub": "하지만 · 15년 넘게 일한 전 직원", "box_bg": W,
  "title": "\"이사회에겐\n'망신'스러운 일\"", "cap": str(O / "cap_cnbc2.png"),
  "caption": "CNBC 기사 캡처", "label": "\"이사회 일부가 물러나거나 교체될 듯\"",
  "lines": ["직원들 \"이사회가 너무 성급했다\"", "지난주 '복귀 없다'던 이사회에 시선 집중"], "cap_max_h": 400},
]
json.dump(spec, open(O / "caps.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "caps.json")], check=True, cwd=R)

cap = """[엔비디아 CEO로 복귀한 젠슨 황, 본사에 돌아온 날 직원들의 반응입니다]

이사회가 23일(현지시간) 젠슨 황을 CEO로 복귀시킨 당일, 그는 곧바로 캘리포니아 산타클라라 본사로 출근했습니다. CNBC가 입수한 영상에 따르면 3개 층을 가득 채운 직원들이 "젠슨"을 연호하며 그를 맞았고, 한 직원은 달려 나와 그를 껴안았습니다.

젠슨 황은 "두 번째 기회를 줘서 고맙다. 두 번째에는 더 나은 CEO가 되겠다"고 말했습니다. 사무실에는 "Jensen is back(젠슨이 돌아왔다)"이라고 적힌 컵케이크가 돌았다고 합니다.

반면 이사회를 향한 시선은 차갑습니다. 15년 넘게 엔비디아에서 일한 한 전 직원은 CNBC에 "이사회에겐 망신스러운 일"이라며 "이사회 일부가 물러나거나 교체될 가능성이 높다"고 말했습니다. 많은 직원이 "이사회가 너무 성급하게 움직였다"고 느꼈다고 합니다. 이사회는 불과 지난주 그의 복귀는 없다고 밝혔었습니다.

젠슨 황은 사임 11일 만에 돌아왔지만, 국가안보·수출통제 관련 조사와 다음 달 의회 증언은 아직 남아 있습니다.

※ 영상: 엔비디아 직원 Abir 촬영 영상, Alec Fong 게시 영상
생각나는 친구에게 보내주세요! 팔로우하면 의회 증언 소식도 이어서 받아보실 수 있습니다."""
d = [{
 "id": "20261124-jensenhq", "slot": "dinner", "mode": "render",
 "topic": "젠슨 황 복귀 당일 본사 출근, 3개 층 직원 환호·포옹, '더 나은 CEO 되겠다'(CNBC), 전 직원 '이사회 망신'",
 "category": "국제",
 "images": ["cover.jpg", "hug.jpg", "c_cnbc1.jpg", "c_cnbc2.jpg"],
 "slides": [
  {"lay": "one", "t": "11일 만에 돌아온 젠슨 황\n본사 직원들의 '반응'",
   "video": {"src": "video/v1.mp4", "start": 0, "dur": 15, "x": 0.5, "y": 0.5, "audio": True}},
  {"sub": "직원 영상 · 본사 로비", "t": "한 직원은 달려 나와\n'와락' 포옹",
   "video": {"src": "video/v2.mp4", "start": 5, "dur": 12, "x": 0.5, "y": 0.5, "audio": True}},
  {"raw": True}, {"raw": True}
 ],
 "caption": cap,
 "hashtags": ["젠슨황", "엔비디아", "미국주식", "엔비디아주가", "CEO"],
 "sources": [
  {"publisher": "CNBC", "date": "2026.11.23"},
  {"publisher": "엔비디아 직원 촬영 영상(Abir, Alec Fong 게시)", "date": "2026.11.23"}
 ],
 "photo_credits": ["영상: 엔비디아 직원 Abir 촬영, Alec Fong 게시", "CNBC 화면"]
}]
json.dump(d, open(D / "draft.json", "w"), ensure_ascii=False, indent=1)
