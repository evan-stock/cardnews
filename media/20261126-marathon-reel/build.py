"""마라톤 참가자들이 사이렌 울린 119 구급차 앞을 지나간 영상(유튜브 '닥신TV' 11.16 원본, SBS 11.26 보도 화면) 오늘의쓸모 띠형 릴스.
내레이션: Gemini TTS Fenrir(state/tts_test/gemini_Fenrir_marathon_0.mp3). 뉴스 원래 소리(앵커 내레이션)는 끔.
사실: SBS·아시아경제·파이낸셜뉴스(11.25~26), 한겨레(서울 마라톤 2021 50개→2025 154개, 120민원 40건→411건), 연합뉴스(서울시 내년 일정·코스 검토).
저장소 루트에서: python3 media/20261126-marathon-reel/build.py  (틀: media/20261126-trump80-reel/build2.py)"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = 'media/20261126-marathon-reel'; V = 'media/20261126-marathon/video/y3.mp4'; A = 'state/tts_test/gemini_Fenrir_marathon_0.mp3'
R = f'{D}/work'; os.makedirs(R, exist_ok=True); os.makedirs(f'{D}/cand', exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
YE = (255, 216, 77); BY0 = 660
TAG = '마라톤 논란'; L = ['사이렌 울리는 구급차', '앞을 그냥 달린', '마라톤 참가자들']
S1 = "유튜브 '닥신TV' 영상 · SBS 보도 화면"; S2 = '한겨레 · 마라톤 온라인·120다산콜센터 집계'; S3 = '연합뉴스'


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
def AMB(y): return f'crop=600:400:660:{y},scale=1080:720'   # 세로 원본(가운데)에서 구급차·참가자 부분(양옆 흐림·아래 SBS 자막 띠 제외)
CROSS = AMB(110)                                  # 횡단보도 위 참가자들
WIDE = 'crop=1230:820:345:0,scale=1080:720'      # 가로 화면(출발 장면), 아래 자막 띠 제외
SEG = [(33.6, 36.9, AMB(180)), (36.9, 40.4, AMB(200)), (40.4, 44.8, AMB(200)), (44.8, 49.1, AMB(180)), (50.5, 55.3, WIDE), (22.0, 27.0, CROSS), (28.0, 31.9, AMB(330)), (36.0, 40.1, AMB(200))]
CAPS = [  # 릴스 시각 기준 (시작, 끝, 작은 줄, 줄1, 줄2) — 내레이션 문장 경계(silencedetect)에 맞춤
    (0.0, 3.3, S1, '사이렌 켠 119 구급차', '유턴하려는데'),
    (3.3, 6.8, S1, '마라톤 참가자들은', '멈추지 않았다'),
    (6.8, 11.2, S1, '약 30명이 지나간 뒤에야', '겨우 유턴, 10초 넘게'),
    (11.2, 15.5, S1, '건국대병원 앞 건대입구역 근처', '하프마라톤이 열린 날'),
    (15.5, 20.3, S2, '서울 마라톤 대회', '2021년 50개 → 2025년 154개'),
    (20.3, 25.3, S2, '마라톤 교통 불편 민원', '40건 → 411건, 10배'),
    (25.3, 29.2, S3, '서울시는 내년 대회', '일정·코스 다시 검토'),
    (29.2, 33.4, '오늘의쓸모', '생명보다 기록?', '여러분 생각은?'),
]
segs = []
for k, (a, b, crop) in enumerate(SEG):
    out = f'{R}/v{k}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', f'{b - a:.3f}', '-i', V, '-vf', f'{crop},setsar=1,fps=30', '-an',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', out], check=True)
    segs.append(os.path.abspath(out))
open(f'{R}/list.txt', 'w').write(''.join(f"file '{s}'\n" for s in segs))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/list.txt', '-c', 'copy', f'{R}/band.mp4'], check=True)
TOT = sum(b - a for a, b, _ in SEG)
inputs = ['-i', f'{R}/band.mp4', '-i', A, '-i', f'{R}/top.png']
fc = f"[0:v]pad=1080:1920:0:{BY0}:black[b0];[b0][2:v]overlay[b1]"; last = 'b1'; n = 3
for ci, (t0, t1, s, l1, l2) in enumerate(CAPS):
    cap(ci, s, l1, l2); inputs += ['-i', f'{R}/cap{ci}.png']
    fc += f";[{last}][{n}:v]overlay=enable='between(t,{t0:.2f},{t1:.2f})'[c{n}]"; last = f'c{n}'; n += 1
fc += f";[{last}]setsar=1[vo];[1:a]apad,atrim=0:{TOT:.2f},loudnorm=I=-15:TP=-1.5,aresample=44100[ao]"
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[vo]', '-map', '[ao]', '-t', f'{TOT:.2f}', '-r', '30',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k',
                '-movflags', '+faststart', f'{D}/reel.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '38.0', '-i', V, '-frames:v', '1', '-vf', AMB(200), f'{R}/cov_band.jpg'], check=True)
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(Image.open(f'{R}/cov_band.jpg'), (0, 330)); bg.save(f'{R}/cov_bg.jpg', quality=95)
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{D}/cand/overlay.png', '구급차 앞을\n그냥 달렸다', '', f'{R}/cov_bg.jpg', f'{D}/reel_cover.jpg'], check=True)
print('done', round(TOT, 1))
