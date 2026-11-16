"""20261116-scan528: 국가자격시험 528개 전수조사 기준 (서울경제·헤럴드경제 캡처). 표지·CTA lay one, 2~6 캡처 카드."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
W, H = 1080, 1350


def vstack(parts, w=1120, gap=0, bg=(255, 255, 255)):
    parts = [p.resize((w, round(p.height * w / p.width)), Image.LANCZOS) for p in parts]
    out = Image.new("RGB", (w, sum(p.height for p in parts) + gap * (len(parts) - 1)), bg); y = 0
    for p in parts: out.paste(p, (0, y)); y += p.height + gap
    return out


L = lambda n: Image.open(O / n).convert("RGB")
vstack([L("sed_head.png").crop((0, 0, 1568, 240)), L("her_p_scope.png")], gap=30).save(O / "cap2.png")

specs = [
 {"out": str(O / "c02.jpg"), "sub": "서울경제 · 헤럴드경제 · 11월 16일",
  "title": "올해 치른 자격시험 '528개'\n응시자 '400만 명'", "cap": str(O / "cap2.png"), "cap_max_h": 560, "box_bg": [255, 255, 255],
  "caption": "서울경제·헤럴드경제 기사 캡처", "label": "세무사 수석 자수 다음 날 발표",
  "lines": ["소방설비기사·정보처리기사·전기기사부터", "세무사·공인노무사·감정평가사까지 전부"]},
 {"out": str(O / "c03.jpg"), "sub": "서울경제 · 11월 16일",
  "title": "점수가 '튀어도'\n온라인에 '의혹'만 있어도", "cap": str(O / "sed_p2.png"), "cap_max_h": 520, "box_bg": [255, 255, 255],
  "caption": "서울경제 기사 캡처", "label": "조사 대상 4가지",
  "lines": ["1. 3년 평균보다 크게 높은 점수   2. 석차 간 큰 점수 차", "3. 과목 간 큰 점수 편차   4. 커뮤니티 의혹·제보"]},
 {"out": str(O / "c04.jpg"), "sub": "헤럴드경제 · 11월 16일",
  "title": "수석·차석 점수 차\n'한 번에 합격'도 본다", "cap": str(O / "her_p_crit.png"), "cap_max_h": 500, "box_bg": [255, 255, 255],
  "caption": "헤럴드경제 기사 캡처", "label": "'생동차'란",
  "lines": ["처음 응시한 해에 1·2차를 모두 통과한 경우", "합격선이 낮은 시험에서 이런 합격이 나오면 들여다봅니다"]},
 {"out": str(O / "c05.jpg"), "sub": "헤럴드경제 · 서울경제 · 11월 16일",
  "title": "주관식 답안은\n'AI 말투'를 찾는다", "cap": str(O / "her_p_ans.png"), "cap_max_h": 500, "box_bg": [255, 255, 255],
  "caption": "헤럴드경제 기사 캡처", "label": "이미 잡힌 것",
  "lines": ["공단은 올해 소방설비기사·정보처리기사 등에서", "스마트안경 부정행위 '12건'을 적발해 수사 의뢰"]},
 {"out": str(O / "c06.jpg"), "sub": "헤럴드경제 그래픽 · 자료 고용노동부·한국산업인력공단",
  "title": "그런데 '합격선 근처'는\n점수로 못 잡는다", "cap": str(O / "her_table.png"), "cap_max_h": 560, "box_bg": [255, 255, 255],
  "caption": "헤럴드경제 그래픽 캡처 (맨 아래 '조사의 한계')", "label": "그리고 빠진 시험",
  "lines": ["528개는 산업인력공단 시험만, 수능·리트는 '대상 아님'"]},
]
sp = Path("/tmp/scan_specs.json"); sp.write_text(json.dumps(specs, ensure_ascii=False))
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sp)], check=True)

# 표지 배경: 사용자가 만든 AI 이미지(cand/ai_cover_src.png). 모니터 제목 '2024' 오기·깨진 글자를 '2026 국가자격시험 점수 분포'로 덮고, 오른쪽 아래 생성 표시 흐림.
from PIL import ImageFont
im = Image.open(O / "ai_cover_src.png").convert("RGB"); col = im.getpixel((575, 97))
d = ImageDraw.Draw(im); d.rectangle((582, 82, 805, 111), fill=col)
f = ImageFont.truetype(str(R / "assets/fonts/Pretendard-SemiBold.otf"), 17); t = "2026 국가자격시험 점수 분포"
d.text((695 - d.textlength(t, font=f) / 2, 96), t, font=f, fill=(240, 240, 240), anchor="lm")
b = (770, 1000, 850, 1075); im.paste(im.crop(b).filter(ImageFilter.GaussianBlur(10)), b[:2])
im = im.resize((W, round(1152 * W / 928)), Image.LANCZOS)
cv = Image.new("RGB", (W, H)); cv.paste(im, (0, 0)); cv.paste(im.crop((0, im.height - 10, W, im.height)).resize((W, H - im.height)), (0, im.height))
cv.filter(ImageFilter.UnsharpMask(2, 50, 2)).save(O / "cover_bg.jpg", quality=95)
print("ok")
