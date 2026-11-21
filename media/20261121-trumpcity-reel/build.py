"""트럼프 '선전은 깨끗, 미국 도시는 더럽고 역겹다' 백악관 브리핑 발언(X @clashreport 2026-11-20 공유) 오늘의쓸모 띠형 릴스(TTS 없음, 원본 소리).
저장소 루트에서: python3 media/20261121-trumpcity-reel/build.py
틀: media/20261121-teddy-reel(띠형). 대사는 transcribe(faster-whisper small)로 확인 후 번역. 소리는 발언 원본 35초 그대로,
선전 이야기 구간에만 선전 APEC 화면(SBS D리포트 배경 화면·Viory 회의장)을 끼움(소리는 발언 유지)."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = 'media/20261121-trumpcity-reel'; V = 'media/20261121-clash/video/v1.mp4'
Y = 'media/20261120-feed-xisnub3/video/y1.mp4'; VI = 'media/20261120-feed-xisnub/video/v2.mp4'
R = f'{D}/work'; os.makedirs(R, exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
YE = (255, 216, 77); BY0, BH = 660, 720
TAG = '선전 다녀온 트럼프'; L = ['중국 칭찬하던 트럼프', '"미국 도시는', '더럽고 역겹다"']
P = '트럼프 · 백악관 브리핑'


def top():
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lg = Image.open('brand/logo_typo_A.png').convert('RGBA'); h = 46; lg = lg.resize((int(lg.width * h / lg.height), h)); im.alpha_composite(lg, (70, 238))
    f = ImageFont.truetype(FX, 34); tw = d.textlength(TAG, font=f)
    d.rounded_rectangle((70, 310, 70 + tw + 36, 362), radius=8, fill=YE); d.text((88, 336), TAG, font=f, fill=(0, 0, 0), anchor='lm')
    f = ImageFont.truetype(FB, 78)
    for l in L: assert d.textlength(l, font=f) <= 950, l
    for i, l in enumerate(L): d.text((70, 433 + i * 88), l, font=f, fill=YE if i == len(L) - 1 else (255, 255, 255), anchor='ls')
    im.save(f'{R}/top.png')


def cap(i, small, b1, b2):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((70, 1450), small, font=ImageFont.truetype(FM, 38), fill=(225, 225, 225), anchor='ls')
    f = ImageFont.truetype(FB, 64)
    d.text((70, 1540), b1, font=f, fill=(255, 255, 255), anchor='ls'); d.text((70, 1622), b2, font=f, fill=YE, anchor='ls')
    for t in (b1, b2): assert d.textlength(t, font=f) <= 950, t
    im.save(f'{R}/cap{i}.png')


top()
TR = 'crop=1290:860:315:0,scale=1080:720'                                     # 브리핑: 아래 백악관 안내 띠 잘라냄
SKY = 'crop=1000:470:100:85,scale=1080:508,pad=1080:720:0:106:black'           # SBS 선전 전경 배경 화면(로고·자막 밖)
HALL = 'crop=1380:920:200:150,scale=1080:720'                                 # Viory 회의장(로고·지명 밖)
VID = [  # (원본, 시작, 길이, 화면) — 합 = 35.0초
    (V, 0.0, 5.1, TR), (Y, 40.2, 1.6, SKY), (VI, 0.5, 2.9, HALL), (V, 9.6, 25.4, TR),
]
CAPS = [  # (시작, 끝, 누가, 줄1, 줄2) — 발언 원본 시각
    (0.0, 5.1, P, '시진핑이 해낸 일 좀 봐', '깨끗하고 티끌 하나 없어'),
    (5.1, 9.6, '선전 · 영상: SBS D리포트, Viory', '40년 전엔 어촌 마을이었는데', '짧은 기간에 지었어'),
    (9.6, 14.1, P, '특히 지난 20년 동안', '나라를 위해 정말 잘했어'),
    (14.1, 19.1, P, '그런데 우리 도시를 보면 더러워', '대부분 민주당 지역이지만'),
    (19.1, 24.2, P, '도로는 더럽고', '사방이 포트홀 천지'),
    (24.2, 29.7, P, '난간은 무너지고', '다 녹슬고 역겨워'),
    (29.7, 35.0, P, '범죄율은 치솟고… 물론 범죄 통계는', '역사상 최고지만'),
]
segs = []
for k, (src, ss, dur, vf) in enumerate(VID):
    out = f'{R}/v{k}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss), '-t', f'{dur:.3f}', '-i', src, '-vf', f'{vf},setsar=1,fps=30', '-an',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', out], check=True)
    segs.append(os.path.abspath(out))
open(f'{R}/list.txt', 'w').write(''.join(f"file '{s}'\n" for s in segs))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/list.txt', '-c', 'copy', f'{R}/band.mp4'], check=True)
TOT = sum(x[2] for x in VID)
inputs = ['-i', f'{R}/band.mp4', '-ss', '0', '-t', f'{TOT:.2f}', '-i', V, '-i', f'{R}/top.png']
fc = f"[0:v]pad=1080:1920:0:{BY0}:black[b0];[b0][2:v]overlay[b1]"; last = 'b1'; n = 3
for i, (t0, t1, who, l1, l2) in enumerate(CAPS):
    cap(i, who, l1, l2); inputs += ['-i', f'{R}/cap{i}.png']
    fc += f";[{last}][{n}:v]overlay=enable='between(t,{t0:.2f},{t1 - 0.02:.2f})'[c{n}]"; last = f'c{n}'; n += 1
fc += f";[{last}]setsar=1,format=yuv420p[vo];[1:a]afade=t=out:st={TOT - 0.3:.2f}:d=0.3,loudnorm=I=-16:TP=-1.5[ao]"
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[vo]', '-map', '[ao]', '-t', f'{TOT:.2f}', '-r', '30',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', f'{D}/reel.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '26.0', '-i', V, '-frames:v', '1', '-vf', TR, f'{R}/cov_band.jpg'], check=True)
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(Image.open(f'{R}/cov_band.jpg'), (0, 330)); bg.save(f'{R}/cov_bg.jpg', quality=95)
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{D}/cand/overlay.png', '트럼프\n"미국 도시는\n더럽고 역겹다"', '', f'{R}/cov_bg.jpg', f'{D}/reel_cover.jpg'], check=True)
print('done', TOT)
