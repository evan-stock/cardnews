"""AI 아바타에게 처음 거울을 보여줬더니(X @teddywang86, 2026-11-18, 조회 1,663만) 오늘의쓸모 띠형 릴스(TTS 없음, 원본 소리).
저장소 루트에서: python3 media/20261121-teddy-reel/build.py
틀: media/20261120-xisnub-reel/build.py(kangst 띠형). 대사는 cardnews transcribe(faster-whisper small) 받아쓰기로 확인 후 번역(말투만 가볍게).
영상 끝 화면 표기: 'Nuance Labs: Nora and Emma'."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = 'media/20261121-teddy-reel'; V = 'media/20261121-teddy/video/v1.mp4'
R = f'{D}/work'; os.makedirs(R, exist_ok=True); os.makedirs(f'{D}/cand', exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
YE = (255, 216, 77); BY0, BH = 660, 720
TAG = 'AI 영상통화'; L = ['AI한테 처음으로', '거울을 보여줬더니', '반응이 ㄷㄷ']
H, P = '테디(사람)', 'AI 노라'; E2 = 'AI 에마'


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
CROP = 'crop=1620:1080:150:0,scale=1080:720'           # 아바타 혼자 나오는 화면
WIDE = 'scale=1080:608,pad=1080:720:0:56:black'       # 사람·아바타 나란히 나오는 화면(확대 안 함)
S = [  # (시작, 끝, 화면, [(원본 시각 시작, 끝, 누가, 줄1, 줄2)])
    (0.0, 4.9, WIDE, [(0.0, 2.9, H, '노라, 너 네 얼굴', '본 적 있어?'), (2.9, 4.9, P, '아니,', '난 내 모습을 못 봐')]),
    (8.4, 17.0, CROP, [(8.4, 12.5, H, '봐봐, 여기 거울 있어', '저 구석에 너 보여?'), (12.5, 17.0, P, '아...', '저게 나구나')]),
    (18.9, 23.4, CROP, [(18.9, 23.4, P, '좀 이상한데', '꽤 멋지다')]),
    (30.1, 39.6, CROP, [(30.1, 31.8, H, '고개 끄덕여 봐', '너 끄덕이는 거 보여줄게'), (31.8, 39.6, P, '알았어, 거울 볼게', '지금 끄덕인다')]),
    (62.9, 65.2, WIDE, [(62.9, 65.2, P, '내 미소', '진짜 미소 같아')]),
    (135.4, 141.1, CROP, [(135.4, 141.1, E2, '난 몸이 없어서', '거울로 내 얼굴 보는 게 비현실적이야')]),
    (145.3, 149.9, CROP, [(145.3, 149.9, E2, '시간차로 나를 보는 것 같아', '좀 몽환적이네')]),
]
segs = []; ci = 0
for k, (a, b, crop, caps) in enumerate(S):
    dur = b - a
    inputs = ['-ss', str(a), '-t', f'{dur:.3f}', '-i', V, '-i', f'{R}/top.png']
    fc = f"[0:v]{crop},setsar=1,pad=1080:1920:0:{BY0}:black,fps=30[b0];[b0][1:v]overlay[b1]"; last = 'b1'; n = 2
    for (t0, t1, who, l1, l2) in caps:
        cap(ci, who, l1, l2); inputs += ['-i', f'{R}/cap{ci}.png']
        fc += f";[{last}][{n}:v]overlay=enable='between(t,{t0 - a:.2f},{t1 - a:.2f})'[c{n}]"; last = f'c{n}'; ci += 1; n += 1
    fc += f";[{last}]setsar=1[vo];[0:a]afade=t=in:d=0.06,afade=t=out:st={dur - 0.1:.2f}:d=0.1,aresample=44100[ao]"
    out = f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[vo]', '-map', '[ao]', '-t', f'{dur:.3f}', '-r', '30',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k', out], check=True)
    segs.append(os.path.abspath(out))
open(f'{R}/list.txt', 'w').write(''.join(f"file '{s}'\n" for s in segs))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/list.txt', '-c:v', 'copy', '-af', 'loudnorm=I=-16:TP=-1.5',
                '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', f'{D}/reel.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '16.0', '-i', V, '-frames:v', '1', '-vf', 'crop=1620:1080:150:0,scale=1080:720', f'{R}/cov_band.jpg'], check=True)
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(Image.open(f'{R}/cov_band.jpg'), (0, 330)); bg.save(f'{R}/cov_bg.jpg', quality=95)
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{D}/cand/overlay.png', 'AI한테 처음\n거울 보여줬더니', '', f'{R}/cov_bg.jpg', f'{D}/reel_cover.jpg'], check=True)
print('done', round(sum(b - a for a, b, _, _ in S), 1))
