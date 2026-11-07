"""20261108-krakow-reel: 9:16 릴스(원래 양식). 저장소 루트에서 실행.
쓰러진 사람·부상자 장면, 일반인 얼굴이 크게 잡히는 구간은 잘라냄."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
ID = 'media/20261108-krakow-reel'; V = f'{ID}/video'
R = f'{ID}/work'; os.makedirs(R, exist_ok=True)
FM = 'assets/fonts/Pretendard-SemiBold.otf' if os.path.exists('assets/fonts/Pretendard-SemiBold.otf') else 'assets/fonts/Pretendard-Medium.otf'
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{R}/ov.png', '폴란드 관광지\\n광장서 총격\\n5명 사망', '속보'], check=True)


def note(i, text):
    """화면 위쪽 작은 상황 설명(인스타 상단 UI 아래)."""
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FM, 40); tw = d.textlength(text, font=f)
    d.rounded_rectangle((60, 250, 60 + tw + 40, 322), radius=12, fill=(0, 0, 0, 170))
    d.text((80, 286), text, font=f, fill=(255, 255, 255), anchor='lm')
    im.save(f'{R}/n{i}.png')


# (파일, 시작, 길이, 설명)
S = [
    ('v5.mp4', 0.0, 1.7, '7일 오후 · 크라쿠프 구시가지'),
    ('v5.mp4', 2.5, 1.3, '총소리에 건물 안으로 피신'),
    ('v1.mp4', 4.0, 6.5, '중앙광장 성모마리아 성당 앞'),
    ('v5.mp4', 7.0, 2.8, '범인은 경찰 총에 맞고 체포'),
    ('v5.mp4', 9.8, 3.1, '총리 "테러" · 범행 동기 조사 중'),
]
segs = []
for k, (f, ss, dur, txt) in enumerate(S):
    note(k, txt)
    fc = ("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v0];"
          "[v0][1:v]overlay[v1];[v1][2:v]overlay[vo]")
    out = f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss), '-t', str(dur), '-i', f'{V}/{f}', '-i', f'{R}/ov.png', '-i', f'{R}/n{k}.png',
                    '-filter_complex', fc, '-map', '[vo]', '-map', '0:a', '-t', str(dur), '-c:v', 'libx264', '-preset', 'veryfast',
                    '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-ac', '2', out], check=True)
    segs.append(out)
open(f'{R}/list.txt', 'w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/list.txt', '-af', 'loudnorm=I=-16:TP=-1.5',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', f'{ID}/reel.mp4'], check=True)
# 커버: 사람들이 뛰어오는 장면(얼굴 작게 보이는 0.8초)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.8', '-i', f'{V}/v5.mp4', '-frames:v', '1', f'{R}/cover_bg.png'], check=True)
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{R}/ov2.png', '폴란드 관광지\\n광장서 총격\\n5명 사망', '속보', f'{R}/cover_bg.png', f'{ID}/reel_cover.jpg'], check=True)
print('done')
