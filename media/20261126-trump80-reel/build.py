"""트럼프 '머스크는 80% 슈퍼 천재, 20%는 말 안 하겠다'(2026.11.22 버지니아 스털링 '트럼프 코인' 만찬, CBS뉴스 영상) 오늘의쓸모 띠형 릴스(원본 소리).
저장소 루트에서: python3 media/20261126-trump80-reel/build.py
틀: media/20261121-nlgta-reel/build.py(git f70d99b 이전). 대사는 transcribe(faster-whisper small)로 확인 후 번역. CBS 로고·날짜 줄은 위를 잘라 뺌."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = 'media/20261126-trump80-reel'; V = f'{D}/video/v1.mp4'
R = f'{D}/work'; os.makedirs(R, exist_ok=True); os.makedirs(f'{D}/cand', exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
YE = (255, 216, 77); BY0 = 660
TAG = '트럼프 × 머스크'; L = ["'MAGA 아니다' 머스크에", '트럼프 "80% 천재"', '나머지 20%는?']
P = '트럼프 대통령 · 11월 22일 만찬'; N = '나흘 전 머스크(뉴욕타임스 딜북 서밋)'


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
BAND = 'crop=1920:900:0:170,scale=1080:506,pad=1080:720:0:107:black'  # 위 CBS 로고·날짜 줄을 잘라냄
CAPS = [  # (시작, 끝, 누가, 줄1, 줄2) — 받아쓰기 a.srt 기준
    (0.0, 3.3, P, '내가 늘 하는 말인데', "그는 '80%'가 슈퍼 천재"),
    (3.3, 6.5, P, '나머지 20%는', '뭔지 말 안 하겠어'),
    (6.5, 8.2, N, '나흘 전 머스크', '"난 MAGA가 아니다"'),
    (8.2, 11.8, P, '이 말은 그한테도', '직접 해'),
    (11.8, 15.9, P, '그래도 아주 특이한 사람이고', '좋은 사람이야'),
    (15.9, 19.9, P, '꽤 보수적이야', '사람은 안 바뀌어'),
    (19.9, 24.4, P, '선거 때문에', '바꿔 보려는 사람들 있지'),
    (24.4, 28.8, P, '보수든 진보든 결국', '원래 자리로 돌아가'),
    (28.8, 31.6, P, '일론은 좋은 사람이야', '진짜로'),
]
DUR = 31.6
inputs = ['-t', f'{DUR}', '-i', V, '-i', f'{R}/top.png']
fc = f"[0:v]{BAND},setsar=1,pad=1080:1920:0:{BY0}:black,fps=30[b0];[b0][1:v]overlay[b1]"; last = 'b1'; n = 2
for ci, (t0, t1, who, l1, l2) in enumerate(CAPS):
    cap(ci, who, l1, l2); inputs += ['-i', f'{R}/cap{ci}.png']
    fc += f";[{last}][{n}:v]overlay=enable='between(t,{t0:.2f},{t1:.2f})'[c{n}]"; last = f'c{n}'; n += 1
fc += f";[{last}]setsar=1[vo];[0:a]afade=t=out:st={DUR - 0.4:.2f}:d=0.4,loudnorm=I=-16:TP=-1.5,aresample=44100[ao]"
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[vo]', '-map', '[ao]', '-t', f'{DUR}', '-r', '30',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k',
                '-movflags', '+faststart', f'{D}/reel.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '2.5', '-i', V, '-frames:v', '1', '-vf', BAND, f'{R}/cov_band.jpg'], check=True)
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(Image.open(f'{R}/cov_band.jpg'), (0, 330)); bg.save(f'{R}/cov_bg.jpg', quality=95)
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{D}/cand/overlay.png', '트럼프가 본 머스크\n"80% 천재"', '', f'{R}/cov_bg.jpg', f'{D}/reel_cover.jpg'], check=True)
print('done')
