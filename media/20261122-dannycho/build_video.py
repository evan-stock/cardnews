"""20261122-dannycho 2장 영상: 펀치라인스 '로스트파티3'(2026.8.30 촬영) 대니초→과즙세연 로스트 클립(엑스 @kkozsom 공유, 원본 자막 유지)을 검은 바탕 틀(frame)에 넣는다."""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw
D = Path(__file__).parent; sys.path.insert(0, str(D))
from build_cards import frame, W, H
VW, VH, Y0 = 940, 744, 300
ph = Image.new("RGB", (VW, VH), (0, 0, 0))
bg = frame(("로스트파티3 무대, 과즙세연 바로 앞에서", "대니초의 '돌직구' 한 마디"), ph,
           "객석은 폭소, 과즙세연은 '웃어넘겼다'", "펀치라인스 '로스트파티3'(8.30 촬영) 공식 클립")
bg.save(D / "cand/v_bg.png")
# 둥근 모서리: 영상 위에 덮을 가면(안쪽 투명, 모서리만 바탕색)
m = Image.new("RGBA", (VW, VH), (10, 10, 12, 255)); ImageDraw.Draw(m).rounded_rectangle((0, 0, VW - 1, VH - 1), 18, fill=(0, 0, 0, 0))
m.save(D / "cand/v_mask.png")
src = D / "video/v1.mp4"
fc = (f"[0:v]crop=720:570:0:366,scale={VW}:{VH}:flags=lanczos,setsar=1[v];"
      f"[1:v][v]overlay={(W-VW)//2}:{Y0}[a];[a][2:v]overlay={(W-VW)//2}:{Y0},format=yuv420p[o]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-loop", "1", "-i", str(D / "cand/v_bg.png"), "-loop", "1", "-i", str(D / "cand/v_mask.png"),
                "-filter_complex", fc, "-map", "[o]", "-map", "0:a", "-t", "36.8", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(D / "cand/vroast.mp4")], check=True)
print("ok")
