"""(2026.11.27 다시 만듦: TTS 빼고 닥신TV 원본 쇼츠 화질·원본 소리, 대사는 transcribe small로 확인)
마라톤 참가자들이 사이렌 울린 119 구급차 앞을 지나간 영상(유튜브 '닥신TV' 11.16 원본, SBS 11.26 보도 화면) 오늘의쓸모 띠형 릴스.
내레이션: Gemini TTS Fenrir(state/tts_test/gemini_Fenrir_marathon_0.mp3). 뉴스 원래 소리(앵커 내레이션)는 끔.
사실: SBS·아시아경제·파이낸셜뉴스(11.25~26), 한겨레(서울 마라톤 2021 50개→2025 154개, 120민원 40건→411건), 연합뉴스(서울시 내년 일정·코스 검토).
저장소 루트에서: python3 media/20261126-marathon-reel/build.py  (틀: media/20261126-trump80-reel/build2.py)"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = 'media/20261126-marathon-reel'; V = 'media/20261126-marathon6/video/y1.mp4'
R = f'{D}/work'; os.makedirs(R, exist_ok=True); os.makedirs(f'{D}/cand', exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
YE = (255, 216, 77); BY0 = 660
TAG = '마라톤 논란'; L = ['사이렌 울리는 구급차', '앞을 그냥 달린', '마라톤 참가자들']
S1 = "유튜브 '닥신TV' 신제욱 씨(내과 전문의) · 11월 16일"; S4 = '아시아경제·SBS(11.26)'; S2 = '한겨레 · 마라톤 온라인·120다산콜센터 집계'; S3 = '연합뉴스'


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
B = 'crop=720:480:0:310,scale=1080:720'   # 세로 원본에서 도로 부분(위 영상 제목·아래 원본 자막 제외)
SEG = [(97.0, 108.3), (24.0, 29.5), (37.0, 45.5), (30.0, 37.0)]
CAPS = [  # 릴스 시각 기준 (시작, 끝, 작은 줄, 줄1, 줄2)
    (0.0, 3.2, S1, '"119가 유턴을', '해야 되는데"'),
    (3.2, 6.1, S1, '"119가 유턴할 땐', '잠깐 멈춰야 되지 않을까"'),
    (6.1, 8.7, S1, '"마라톤 여론이', '좋지 않은 것도"'),
    (8.7, 11.3, S1, '"분명히 그 이유도', '있었던 것 같다"'),
    (11.3, 16.8, S4, '구급차는 약 30명이 지나간 뒤', '겨우 유턴, 10초 넘게'),
    (16.8, 21.3, S4, '건국대병원 앞 건대입구역', '길 건너는 방법을 묻자'),
    (21.3, 25.3, '자원봉사자로 추정되는 남성', '"틈 나면', '같이 뛰면서 건너라"'),
    (25.3, 28.8, S2, '서울 마라톤 대회 4년 새', '50개 → 154개'),
    (28.8, 31.0, S2, '마라톤 교통 민원', '40건 → 411건'),
    (31.0, 32.3, '오늘의쓸모', '생명보다 기록?', '여러분 생각은?'),
]
segs = []
for k, (a, b) in enumerate(SEG):
    out = f'{R}/v{k}.mp4'; dur = b - a
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', f'{dur:.3f}', '-i', V, '-filter_complex',
                    f'[0:v]{B},setsar=1,fps=30[v];[0:a]afade=t=in:d=0.04,afade=t=out:st={dur - 0.06:.2f}:d=0.06,aresample=44100[a]',
                    '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k', out], check=True)
    segs.append(os.path.abspath(out))
open(f'{R}/list.txt', 'w').write(''.join(f"file '{x}'\n" for x in segs))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/list.txt', '-c', 'copy', f'{R}/band.mp4'], check=True)
TOT = round(sum(b - a for a, b in SEG), 2)
inputs = ['-i', f'{R}/band.mp4', '-i', f'{R}/top.png']
fc = f"[0:v]pad=1080:1920:0:{BY0}:black[b0];[b0][1:v]overlay[b1]"; last = 'b1'; n = 2
for ci, c in enumerate(CAPS):
    if len(c) == 5: t0, t1, sm, l1, l2 = c
    cap(ci, sm, l1, l2); inputs += ['-i', f'{R}/cap{ci}.png']
    fc += f";[{last}][{n}:v]overlay=enable='between(t,{t0:.2f},{t1:.2f})'[c{n}]"; last = f'c{n}'; n += 1
fc += f";[{last}]setsar=1[vo];[0:a]loudnorm=I=-16:TP=-1.5,aresample=44100[ao]"
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[vo]', '-map', '[ao]', '-t', f'{TOT:.2f}', '-r', '30',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k',
                '-movflags', '+faststart', f'{D}/reel.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '99.5', '-i', V, '-frames:v', '1', '-vf', B, f'{R}/cov_band.jpg'], check=True)
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(Image.open(f'{R}/cov_band.jpg'), (0, 330)); bg.save(f'{R}/cov_bg.jpg', quality=95)
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{D}/cand/overlay.png', '구급차 앞을\n그냥 달렸다', '', f'{R}/cov_bg.jpg', f'{D}/reel_cover.jpg'], check=True)
print('done', TOT)
