"""20261115-nowyeosi: 리트 만점자 시험지 '5문제 연속 답 고침' 온라인 주장 (온라인 커뮤니티 글 캡처, 엑스 @nowyeosi로 받음).
캡처는 원본 비율 기준(분수)으로 잘라 화질 상관없이 같은 영역을 씀."""
import json, shutil, subprocess, sys
from pathlib import Path
from PIL import Image

D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"; V = D / "video"
O.mkdir(exist_ok=True)
shutil.copy(R / "media/20261112-leetlive/cand/cover_bg.jpg", O / "cover_photo.jpg")


def src(i):
    for p in [V / f"page{i}.html", V / f"img{i}.jpg"]:
        if p.exists():
            try:
                return Image.open(p).convert("RGB")
            except Exception:
                pass


def cut(i, fy0, fy1, name):
    im = src(i)
    im.crop((0, round(im.height * fy0), im.width, round(im.height * fy1))).save(O / name)
    return str(O / name)


c1 = cut(1, 230 / 1200, 745 / 1200, "cap_post.png")      # 본문 + 25~29번 처음답/나중답
c2 = cut(2, 0, 380 / 1200, "cap_paper.png")              # 시험지 + '후반부로 갈수록 집중력이 떨어져' 자막
_im = Image.open(c2); _w = _im.width / 1079                  # 'N수의신' 로고 가림(원본 1079 기준 x195~390, y0~148)
_im.paste(Image.new("RGB", (round(240 * _w), round(148 * _w)), (244, 244, 244)), (round(178 * _w), 0)); _im.save(c2)
c3 = cut(3, 75 / 1200, 525 / 1200, "cap_cmt.png")        # 댓글

spec = [
    {"out": str(O / "c02.jpg"), "sub": "온라인 커뮤니티 글 · 11월 15일",
     "title": "\"AI 화면 답을\n'미뤄 쓴' 것 같다\"", "cap": c1, "cap_max_h": 600,
     "caption": "온라인 커뮤니티 글 캡처",
     "label": "25~29번, 다섯 문제 답이 한꺼번에?",
     "lines": ["지문이 다른 문제 5개의 답을 몰아서 고쳤다는 주장입니다."]},
    {"out": str(O / "c03.jpg"), "sub": "미미미누 유튜브에 공개된 실제 리트 시험지",
     "title": "본인 설명은\n\"'집중력'이 떨어져서\"", "cap": c2, "cap_max_h": 600,
     "caption": "유튜브 미미미누 영상 화면 (커뮤니티 글 첨부)",
     "label": "\"많이 지웠다가 다시 쓰는 그런 게…\"",
     "lines": ["영상에서 후반부로 갈수록 집중력이 떨어졌다고 말했습니다."]},
    {"out": str(O / "c04.jpg"), "sub": "댓글 반응",
     "title": "\"몇 문제를 한꺼번에\n'연속으로' 고치는 건 의아\"", "cap": c3, "cap_max_h": 600,
     "caption": "온라인 커뮤니티 댓글 캡처",
     "label": "반론도 있습니다",
     "lines": ["막판에 미뤄 둔 문제를 몰아 푸는 건 흔한 습관이라는 말도 나옵니다."]},
]
sj = D / "cap_spec.json"; sj.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(sj)], check=True)
