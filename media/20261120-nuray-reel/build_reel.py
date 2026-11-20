"""20261120-nuray-reel: 띠형 릴스. 원본 = Talks International 인터뷰(2025), @sovyre 엑스 게시(2026.11.19, 661만 조회) 3분 영상.
원본 영어 자막(영상 아래쪽)과 오른쪽 위 채널 로고는 띠 크롭 밖으로 뺀다. 아래 자막은 우리 번역.
저장소 루트에서: python3 media/20261120-nuray-reel/build_reel.py
"""
import subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
D = 'media/20261120-nuray-reel'; R = f'{D}/work'; os.makedirs(R, exist_ok=True)
SRC = 'media/20261120-nuray/video/v1.mp4'
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
Y = (255, 216, 77); BY0, BH = 660, 720
TAG = '일본 AV 배우 출신 인터뷰'
L = ['AV 배우 6년 하다', '히잡 쓴 일본 여성', '"후회는 없어요"']


def top():
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lg = Image.open('brand/logo_typo_A.png').convert('RGBA'); h = 46; lg = lg.resize((int(lg.width * h / lg.height), h)); im.alpha_composite(lg, (70, 238))
    f = ImageFont.truetype(FX, 34); tw = d.textlength(TAG, font=f)
    d.rounded_rectangle((70, 310, 70 + tw + 36, 362), radius=8, fill=Y); d.text((88, 336), TAG, font=f, fill=(0, 0, 0), anchor='lm')
    f = ImageFont.truetype(FB, 78)
    for i, l in enumerate(L): d.text((70, 433 + i * 88), l, font=f, fill=Y if i == 2 else (255, 255, 255), anchor='ls')
    im.save(f'{R}/top.png')


def cap(i, small, b1, b2):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if small: d.text((70, 1450), small, font=ImageFont.truetype(FM, 38), fill=(225, 225, 225), anchor='ls')
    f = ImageFont.truetype(FB, 68)
    d.text((70, 1540), b1, font=f, fill=(255, 255, 255), anchor='ls'); d.text((70, 1625), b2, font=f, fill=Y, anchor='ls')
    im.save(f'{R}/cap{i}.png')


top()
CROP = '1170:780:470:90'  # 3:2, 아래 원본 자막(y≈880~)·위 로고(y<40) 제외
S = [  # (시작, 길이, [(t0, t1, 작은줄, 굵은1, 굵은2)])
    (0.0, 11.8, [(0, 3.0, '진행자 질문', '"인생에 후회', '있나요?"'),
                 (3.0, 11.8, '그녀의 대답', '"이 일 안 했다면', '이슬람 못 만났을 거예요"')]),
    (52.6, 10.3, [(0, 10.3, '개종하고 잃은 것', '"팔로워 수천 명 아니고', '수십만 명 잃었어요"')]),
    (65.3, 10.6, [(0, 4.2, '그리고 당연히', '"주 수입원도', '끊겼어요"'),
                  (4.2, 10.6, '마케팅이라는 말에', '"수입도 없는데', '이게 무슨 마케팅이죠?"')]),
    (99.6, 6.8, [(0, 6.8, '가장 크게 바뀐 것', '"저 아주 나쁜 딸이었어요', '부모님을 1년 차단했죠"')]),
    (167.6, 9.3, [(0, 6.6, '지금도 듣는 말', '"저 여자 거짓말이야"', '"근데 상관없어요"'),
                  (6.6, 9.3, '왜냐하면', '"나를 판단할 수 있는 건', '알라뿐이니까요"')]),
    (178.0, 3.9, [(0, 3.9, '', '"사람들의 인정은', '필요 없어요"')]),
]
segs = []; ci = 0
for k, (ss, dur, caps) in enumerate(S):
    inputs = ['-ss', str(ss), '-t', str(dur), '-i', SRC, '-i', f'{R}/top.png']
    fc = f"[0:v]crop={CROP},scale=1080:{BH},setsar=1[fg];[fg]pad=1080:1920:0:{BY0}:black[b0];[b0][1:v]overlay[b1]"
    last = 'b1'
    for j, (t0, t1, s, b1, b2) in enumerate(caps):
        cap(ci, s, b1, b2); inputs += ['-i', f'{R}/cap{ci}.png']; n = 2 + j
        fc += f";[{last}][{n}:v]overlay=enable='between(t,{t0},{t1})'[c{j}]"; last = f'c{j}'; ci += 1
    out = f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc + f";[{last}]setsar=1[vo]", '-map', '[vo]', '-map', '0:a?', '-r', '30',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k', out], check=True)
    segs.append(out)
open(f'{R}/list.txt', 'w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/list.txt', '-af', 'loudnorm=I=-16:TP=-1.5', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                '-movflags', '+faststart', f'{D}/reel.mp4'], check=True)

# 커버: 검정 바탕 + 가로 띠(기모노 / 모스크 앞 히잡, mothership 보도 사진) + 격자 통일형 큰 제목
src = Image.open('media/20261120-nuray/cand/press01.jpg').convert('RGB')
band = ImageOps.fit(src, (1080, 720), Image.LANCZOS, centering=(.5, .3))
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(band, (0, 330)); bg.save(f'{R}/cover_bg.jpg', quality=95)
os.makedirs(f'{D}/cand', exist_ok=True)
subprocess.run([sys.executable, 'scripts/reel_overlay.py', f'{D}/cand/overlay.png', 'AV 배우 6년\\n히잡 쓰고\\n"후회 없어요"', '', f'{R}/cover_bg.jpg', f'{D}/reel_cover.jpg'], check=True)
print('done')
