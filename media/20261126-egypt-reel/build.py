"""이집트 기자 순환도로 유조차 전복·화재(2026.11.25 현지, 31명 사망·21명 부상·차량 27대) 오늘의쓸모 띠형 릴스.
영상: 현지 SNS 확산 영상(원 게시자 미상, 엑스에서 받음 → 출처로 쓰지 않음). 원본 소리 그대로(오늘의쓸모 릴스는 TTS 안 씀).
사실: CNN·CBC·UPI·아샤르크 알아우사트(11.25~26), 이집트 보건부 최종 집계 31명 사망·21명 부상, 검찰 차량 27대 소실·원인 조사·DNA 신원 확인.
저장소 루트에서: python3 media/20261126-egypt-reel/build.py  (틀: media/20261126-marathon-reel/build.py)"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = 'media/20261126-egypt-reel'; V = 'media/20261126-egypt/video/v1.mp4'
R = f'{D}/work'; os.makedirs(R, exist_ok=True); os.makedirs(f'{D}/cand', exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
YE = (255, 216, 77); BY0 = 660
TAG = '이집트 참사'; L = ['유조차가 뒤집히자', '도로 위 차 27대가', '불길에 휩싸였다']
S1 = '현지 SNS 확산 영상(원 게시자 미상)'; S2 = '이집트 보건부 · CNN'; S3 = '이집트 검찰 · 외신 종합'


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
BAND = 'crop=720:480:0:40,scale=1080:720'        # 첫 영상(세로)에서 불길이 번지는 도로 부분
V2 = 'media/20261126-egypt/video/v2.mp4'          # 두 번째 현장 영상(360x640, 가운데 아랍어 자막 박힘). 앞 25초(불길 속 사람)는 쓰지 않음
BAND2 = 'crop=360:240:0:170,scale=1080:720'      # 아랍어 자막 위쪽만
SEG = [(V, 0.0, 20.4, BAND), (V2, 26.0, 31.5, BAND2), (V2, 35.0, 37.5, BAND2), (V2, 42.0, 45.0, BAND2)]
TOT = round(sum(b - a for _, a, b, _ in SEG), 2)
S4 = '다른 각도 현장 영상(원 게시자 미상)'
CAPS = [  # 릴스 시각 기준
    (0.0, 3.0, S1, '이집트 카이로 근처', '기자 순환도로, 25일(현지)'),
    (3.0, 6.0, S1, '기름 실은 유조차가', '뒤집히며 불이 붙었다'),
    (6.0, 9.5, S1, '불길은 도로를 따라', '주변 차들로 번졌다'),
    (9.5, 13.0, S2, '31명 사망', '21명 부상'),
    (13.0, 16.5, '이집트 검찰', '불에 탄 차량', '27대'),
    (16.5, 20.4, '이집트 보건부', '현장에 출동한 구급차', '39대'),
    (20.4, 25.9, S4, '도로 위로 이어진 불길', '지켜보는 시민들'),
    (25.9, 28.4, S3, '검찰은', '정확한 사고 원인 조사 중'),
    (28.4, TOT, S3, '희생자 신원은', 'DNA 검사로 확인 중'),
]
segs = []
for k, (src, a, b, crop) in enumerate(SEG):
    out = f'{R}/v{k}.mp4'; dur = b - a
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', f'{dur:.3f}', '-i', src, '-filter_complex',
                    f'[0:v]{crop},setsar=1,fps=30[v];[0:a]afade=t=in:d=0.05,afade=t=out:st={dur - 0.08:.2f}:d=0.08,aresample=44100[a]',
                    '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k', out], check=True)
    segs.append(os.path.abspath(out))
open(f'{R}/list.txt', 'w').write(''.join(f"file '{x}'\n" for x in segs))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/list.txt', '-c', 'copy', f'{R}/band.mp4'], check=True)
inputs = ['-i', f'{R}/band.mp4', '-i', f'{R}/top.png']
fc = f"[0:v]pad=1080:1920:0:{BY0}:black[b0];[b0][1:v]overlay[b1]"; last = 'b1'; n = 2
for ci, (t0, t1, s_, l1, l2) in enumerate(CAPS):
    cap(ci, s_, l1, l2); inputs += ['-i', f'{R}/cap{ci}.png']
    fc += f";[{last}][{n}:v]overlay=enable='between(t,{t0:.2f},{t1:.2f})'[c{n}]"; last = f'c{n}'; n += 1
fc += f";[{last}]setsar=1[vo];[0:a]loudnorm=I=-16:TP=-1.5,aresample=44100[ao]"
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[vo]', '-map', '[ao]', '-t', f'{TOT:.2f}', '-r', '30',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k',
                '-movflags', '+faststart', f'{D}/reel.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '9.0', '-i', V, '-frames:v', '1', '-vf', BAND, f'{R}/cov_band.jpg'], check=True)
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(Image.open(f'{R}/cov_band.jpg'), (0, 330)); bg.save(f'{R}/cov_bg.jpg', quality=95)
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{D}/cand/overlay.png', '유조차 화재로\n31명 사망', '', f'{R}/cov_bg.jpg', f'{D}/reel_cover.jpg'], check=True)
print('done', TOT)
