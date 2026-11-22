"""테슬라 FSD V15 배포 시작(2026-11-21~22) 오늘의쓸모 띠형 릴스. 틀: media/20261121-nlgta-reel/build.py.
영상: v7 테슬라 공식(X @SawyerMerritt 퍼옴), v1~v6 X @SawyerMerritt 실제 주행 화면. 소리: 테슬라 공식 영상(v7) 소리를 전체 배경으로(팬 영상 속 차량 음악은 끔).
사실: 테슬라 릴리스 노트(X @SawyerMerritt 11.22), 국내는 2025.11 감독형 FSD v14 배포(경향·한경)·V15 국내 시기 미정."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = 'media/20261122-fsd15-reel'; VD = 'media/20261122-fsd15/video'
R = f'{D}/work'; os.makedirs(R, exist_ok=True); os.makedirs(f'{D}/cand', exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
YE = (255, 216, 77); BY0, BH = 660, 720
TAG = '테슬라 FSD V15'; L = ['테슬라 자율주행', '화면이 이렇게', '바뀌었다']
T = '테슬라 공식 영상'; X = 'X @SawyerMerritt 주행 영상'


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
WIDE = 'scale=1080:608,pad=1080:720:0:56:black'
S = [  # (영상, 시작, 끝, [(원본 시각 시작, 끝, 출처, 줄1, 줄2)])
    ('v7', 2.0, 6.5, [(2.0, 6.5, T, '테슬라 FSD V15', '드디어 배포 시작')]),
    ('v1', 2.0, 8.0, [(2.0, 8.0, X, "새 화면 '리얼리티 뷰'", '차 위에서 내려다보듯')]),
    ('v3', 6.0, 12.0, [(6.0, 12.0, X, '어디로 꺾을지', '화면에 화살표로')]),
    ('v3', 26.0, 32.0, [(26.0, 32.0, X, '회전교차로도', '알아서 통과')]),
    ('v6', 1.5, 6.5, [(1.5, 6.5, X, '차선·노면 표시까지', '실시간으로 그린다')]),
    ('v4', 2.0, 9.0, [(2.0, 9.0, X, '주차는', '빈자리 골라서 척')]),
    ('v7', 7.0, 11.0, [(7.0, 11.0, T, '도로 위 낙하물·포트홀', '더 잘 피한다')]),
    ('v2', 8.0, 13.0, [(8.0, 13.0, X, '과속 카메라 앞에선', '알아서 감속')]),
    ('v7', 11.5, 15.5, [(11.5, 15.5, T, '위험 상황 대처', "'25배' 좋아졌다는 테슬라")]),
    ('v7', 38.5, 43.5, [(38.5, 43.5, T, '한국 배포는?', '아직 V14 단계, V15 시기 미정')]),
]
segs = []; ci = 0
for k, (vn, a, b, caps) in enumerate(S):
    dur = b - a; V = f'{VD}/{vn}.mp4'
    inputs = ['-ss', str(a), '-t', f'{dur:.3f}', '-i', V, '-i', f'{R}/top.png']
    fc = f"[0:v]{WIDE},setsar=1,pad=1080:1920:0:{BY0}:black,fps=30[b0];[b0][1:v]overlay[b1]"; last = 'b1'; n = 2
    for (t0, t1, who, l1, l2) in caps:
        cap(ci, who, l1, l2); inputs += ['-i', f'{R}/cap{ci}.png']
        fc += f";[{last}][{n}:v]overlay=enable='between(t,{t0 - a:.2f},{t1 - a:.2f})'[c{n}]"; last = f'c{n}'; ci += 1; n += 1
    fc += f";[{last}]setsar=1[vo]"
    out = f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[vo]', '-an', '-t', f'{dur:.3f}', '-r', '30',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', out], check=True)
    segs.append(os.path.abspath(out))
TOT = sum(b - a for _, a, b, _ in S)
open(f'{R}/list.txt', 'w').write(''.join(f"file '{s}'\n" for s in segs))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/list.txt', '-stream_loop', '-1', '-i', f'{VD}/v7.mp4',
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', f'atrim=0:{TOT:.2f},afade=t=out:st={TOT - 1.2:.2f}:d=1.2,loudnorm=I=-16:TP=-1.5',
                '-c:a', 'aac', '-b:a', '160k', '-t', f'{TOT:.2f}', '-movflags', '+faststart', f'{D}/reel.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '4.0', '-i', f'{VD}/v1.mp4', '-frames:v', '1', '-vf', WIDE, f'{R}/cov_band.jpg'], check=True)
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(Image.open(f'{R}/cov_band.jpg'), (0, 330)); bg.save(f'{R}/cov_bg.jpg', quality=95)
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{D}/cand/overlay.png', '테슬라 자율주행\n화면이 이렇게 바뀜', '', f'{R}/cov_bg.jpg', f'{D}/reel_cover.jpg'], check=True)
print('done', round(TOT, 1))
