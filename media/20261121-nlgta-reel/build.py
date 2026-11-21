"""뉴럴링크 임상 참가자의 GTA6 플레이(뉴럴링크 공식 X 2026-11-20, 'Playing GTA VI with a Neuralink') 오늘의쓸모 띠형 릴스(TTS 없음, 원본 소리).
저장소 루트에서: python3 media/20261121-nlgta-reel/build.py
틀: media/20261121-teddy-reel/build.py. 대사는 transcribe(faster-whisper small)로 확인 후 번역. 참가자 이름은 쓰지 않음."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = 'media/20261121-nlgta-reel'; V = 'media/20261121-nlgta2/video/v1.mp4'
R = f'{D}/work'; os.makedirs(R, exist_ok=True); os.makedirs(f'{D}/cand', exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
YE = (255, 216, 77); BY0, BH = 660, 720
TAG = '뉴럴링크'; L = ['뇌에 칩 심은 환자가', 'GTA6를 해봤다', '손 하나 안 쓰고']
P = '뉴럴링크 임상 참가자'; N = '뉴럴링크 공식 영상 (11.20)'


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
WIDE = 'scale=1080:608,pad=1080:720:0:56:black'   # 위쪽 참가자 화면·가상 컨트롤러까지 다 보이게(확대 안 함)
S = [  # (시작, 끝, 화면, [(원본 시각 시작, 끝, 누가, 줄1, 줄2)])
    (0.0, 5.4, WIDE, [(0.0, 5.4, N, 'GTA6 출시 다음 날', '뉴럴링크가 공개한 영상')]),
    (25.7, 28.0, WIDE, [(25.7, 28.0, P, '바늘구멍 통과!', '봐봐')]),
    (42.6, 51.1, WIDE, [(42.6, 47.0, P, '지금 약지만', '톡톡 치는 중'), (47.0, 51.1, P, '짠, 약지 하나로', 'GTA에서 이 정도')]),
    (62.0, 66.0, WIDE, [(62.0, 66.0, N, '수상비행기까지', '이륙 성공')]),
    (66.4, 72.0, WIDE, [(66.4, 72.0, P, '기수를 올리려면 오른손을', '앞으로 미는 느낌')]),
    (92.9, 102.0, WIDE, [(92.9, 97.9, P, '칩 수술 전엔', '입에 막대를 물고 아이패드를 썼어'), (97.9, 102.0, P, '새가 쪼듯이', '아이패드를 쪼았지')]),
    (108.0, 118.9, WIDE, [(108.0, 111.9, P, '칩을 받고 나니', '이걸로 뭘 할 수 있나 싶었는데'), (111.9, 118.9, P, '컴퓨터를 다루자마자', '세상으로 가는 문이 다시 열렸어')]),
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
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '64.5', '-i', V, '-frames:v', '1', '-vf', WIDE, f'{R}/cov_band.jpg'], check=True)
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(Image.open(f'{R}/cov_band.jpg'), (0, 330)); bg.save(f'{R}/cov_bg.jpg', quality=95)
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{D}/cand/overlay.png', '뇌에 칩 심고\nGTA6 하는 환자', '', f'{R}/cov_bg.jpg', f'{D}/reel_cover.jpg'], check=True)
print('done', round(sum(b - a for a, b, _, _ in S), 1))
