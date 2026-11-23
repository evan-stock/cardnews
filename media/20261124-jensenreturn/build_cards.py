"""20261124-jensenreturn: 엔비디아 이사회 젠슨 황 CEO 복귀(11.23 현지) + 트럼프 '내가 성사' + 트루스소셜 피격사진 패러디 밈."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
D = Path(__file__).parent; R = D.parents[1]; O = D / "cand"
T = Path("/tmp/claude-tool-results/a493c683-e7b1-5bd7-9aa7-411f6fdd042e")
def shot(name, box, out):
    Image.open(T / name).convert("RGB").crop(box).save(O / out)
shot("mcp-claude-in-chrome-blob-1795455748348-xsezbn-4fa0066d.jpg", (10, 25, 1030, 465), "cap_pr.png")
shot("mcp-claude-in-chrome-blob-1795455752940-3uru14-ef59cc07.jpg", (10, 15, 790, 200), "cap_probe.png")
shot("mcp-claude-in-chrome-blob-1795455783994-dpo0ze-9271273a.jpg", (410, 225, 1150, 620), "cap_sema.png")
shot("mcp-claude-in-chrome-blob-1795455718292-2weji9-56d2da72.jpg", (120, 20, 1290, 610), "cap_cnbc.png")
shot("mcp-claude-in-chrome-blob-1795455766116-mvlgni-a2179f1a.jpg", (0, 12, 830, 440), "cap_musk.png")
# 트루스소셜 게시물(사용자 캡처): 날짜 줄 포함, 아래 여백만 정리
tr = Image.open("/mnt/user-data/uploads/4b301e16-image.jpg").convert("RGB")
tr.crop((0, 0, tr.width, 1478)).save(O / "cap_truth.png")
# 표지용 밈: 아래 검은 띠 잘라냄
mm = Image.open(O / "meme_src.jpg").convert("RGB"); mm.crop((0, 0, mm.width, 1090)).save(O / "meme.jpg", quality=95)

W_, H_ = 1080, 1350
bg = Image.new('RGB', (W_, H_), (18, 20, 18))
glow = Image.new('L', (W_, H_), 0); ImageDraw.Draw(glow).ellipse((-200, -300, 1280, 700), fill=100); glow = glow.filter(ImageFilter.GaussianBlur(160))
bg = Image.composite(Image.new('RGB', (W_, H_), (40, 70, 30)), bg, glow)
bg.save(O / 'plain_bg.jpg', quality=94)

W = [255, 255, 255]
spec = [
 {"out": str(O / "c02.jpg"), "sub": "트럼프 트루스소셜 · 11월 24일 새벽(한국시간)",
  "title": "2024년 '피격 사진'에\n젠슨 황을 합성해 올렸다", "cap": str(O / "cap_truth.png"),
  "caption": "도널드 트럼프 트루스소셜 게시물", "label": "치켜든 주먹엔 빨간 브래지어",
  "lines": ["불륜 스캔들로 물러났던 젠슨 황의 복귀를 이렇게 축하", "같은 날 \"젠슨은 위대한 애국자이자 국가의 보물\""], "cap_max_h": 600},
 {"out": str(O / "c03.jpg"), "sub": "엔비디아 공식 발표 · 11월 23일(현지)", "box_bg": W,
  "title": "사임 11일 만에\n이사회 '만장일치' 복귀", "cap": str(O / "cap_pr.png"),
  "caption": "엔비디아 뉴스룸 보도자료", "label": "사장·CEO·이사 모두 즉시 복귀",
  "lines": ["\"미국 정부 고위급의 의견을 들었고", "안보 위험은 없다고 확신한다\""], "cap_max_h": 500},
 {"out": str(O / "c04.jpg"), "sub": "세마포 단독 · 소식통", "box_bg": [248, 244, 216],
  "title": "발표 몇 시간 전\n트럼프가 이사회 회의에 '전화'", "cap": str(O / "cap_sema.png"),
  "caption": "세마포 기사 캡처", "label": "직접 회의에 들어가 복귀를 주장",
  "lines": ["이사회는 전날 밤 모여 만장일치로 의결", "백악관 \"트럼프가 전적으로 관여했다\""], "cap_max_h": 440},
 {"out": str(O / "c05.jpg"), "sub": "트럼프 · CNBC 전화 인터뷰", "box_bg": W,
  "title": "\"내가 설득했다\n'내가' 성사시켰다\"", "cap": str(O / "cap_cnbc.png"),
  "caption": "CNBC 기사 캡처", "label": "이사회가 '안보 보증'을 요구했고, 줬다",
  "lines": ["\"그가 있는 게 위협? 그를 잃는 게 위협\"", "복귀 확정 뒤 젠슨에게 \"딱 하나, 열심히 일하라\""], "cap_max_h": 470},
 {"out": str(O / "c06.jpg"), "sub": "일론 머스크 반응",
  "title": "\"오류가\n수정되었다\"", "cap": str(O / "cap_musk.png"),
  "caption": "일론 머스크 게시물", "label": "엔비디아 복귀 발표를 인용하며 한 줄",
  "lines": ["사임 직후 '젠슨 복귀' 청원에", "\"나도 서명한다\"고 했던 머스크"], "cap_max_h": 470},
 {"out": str(O / "c08.jpg"), "sub": "그래도 끝난 건 아니다", "box_bg": W,
  "title": "'외국 정보기관 표적' 조사\n결론 날 때까지 계속", "cap": str(O / "cap_probe.png"),
  "caption": "엔비디아 보도자료", "label": "워런 상원의원 \"무모한 결정\"",
  "lines": ["트럼프도 \"수출통제 내부 조사는 계속하라\"", "젠슨 황, 다음 달 의회 증언 예정(세마포)"], "cap_max_h": 330},
]
json.dump(spec, open(O / "caps.json", "w"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, str(R / "scripts/post_cap_card.py"), str(O / "caps.json")], check=True, cwd=R)
