"""트럼프 '머스크 80% 천재' 릴스 압축판(약 16초). 머스크 'I'm not MAGA'(CNBC 텔레비전 유튜브, 2026.11.18 뉴욕타임스 딜북 서밋) →
트럼프 발언(CBS뉴스 영상, 11.22 '트럼프 코인' 만찬). 대사는 transcribe(faster-whisper small) + 음량 그래프로 구간 확인.
저장소 루트에서: python3 media/20261126-trump80-reel/build2.py  (틀: build.py)"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = 'media/20261126-trump80-reel'; VT = f'{D}/video/v1.mp4'; VM = 'media/20261126-muskmaga/video/y2.mp4'
R = f'{D}/work2'; os.makedirs(R, exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
YE = (255, 216, 77); BY0 = 660
TAG = '트럼프 × 머스크'; L = ["'MAGA 아니다' 머스크에", '트럼프 "80% 천재"', '나머지 20%는?']
PM = '일론 머스크 · 11월 18일 뉴욕타임스 딜북 서밋'; PT = '트럼프 대통령 · 11월 22일 만찬'


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
SPLIT = 'crop=828:552:972:180,scale=1080:720'     # 소킨·머스크 나란히 화면에서 머스크 칸만(아래 CNBC 띠 제외)
MUSK = 'crop=1110:740:300:30,scale=1080:720'       # 머스크 단독 화면(아래 CNBC 띠 제외)
TRUMP = 'crop=1350:900:150:170,scale=1080:720'     # CBS 로고·날짜 줄 제외
S = [  # (영상, 시작, 끝, 화면, [(원본 시각 시작, 끝, 누가, 줄1, 줄2)])
    (VM, 132.65, 133.88, SPLIT, [(132.65, 133.88, PM, '"내 말은,', '나는 MAGA가 아니야"')]),
    (VM, 133.88, 134.75, MUSK, [(133.88, 134.75, PM, '"내 말은,', '나는 MAGA가 아니야"')]),
    (VT, 0.0, 6.5, TRUMP, [(0.0, 3.3, PT, '내가 늘 하는 말인데', "그는 '80%'가 슈퍼 천재"), (3.3, 6.5, PT, '나머지 20%는', '뭔지 말 안 하겠어')]),
    (VT, 8.2, 11.4, TRUMP, [(8.2, 11.4, PT, '이 말은 그한테도', '직접 해')]),
    (VT, 28.8, 31.6, TRUMP, [(28.8, 31.6, PT, '일론은 좋은 사람이야', '진짜로')]),
]
segs = []; ci = 0
for k, (V, a, b, crop, caps) in enumerate(S):
    dur = b - a
    inputs = ['-ss', str(a), '-t', f'{dur:.3f}', '-i', V, '-i', f'{R}/top.png']
    fc = f"[0:v]{crop},setsar=1,pad=1080:1920:0:{BY0}:black,fps=30[b0];[b0][1:v]overlay[b1]"; last = 'b1'; n = 2
    for (t0, t1, who, l1, l2) in caps:
        cap(ci, who, l1, l2); inputs += ['-i', f'{R}/cap{ci}.png']
        fc += f";[{last}][{n}:v]overlay=enable='between(t,{t0 - a:.2f},{t1 - a:.2f})'[c{n}]"; last = f'c{n}'; ci += 1; n += 1
    fc += f";[{last}]setsar=1[vo];[0:a]afade=t=in:d=0.03,afade=t=out:st={dur - 0.06:.2f}:d=0.06,aresample=44100[ao]"
    out = f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[vo]', '-map', '[ao]', '-t', f'{dur:.3f}', '-r', '30',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k', out], check=True)
    segs.append(os.path.abspath(out))
open(f'{R}/list.txt', 'w').write(''.join(f"file '{s}'\n" for s in segs))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/list.txt', '-c:v', 'copy', '-af', 'loudnorm=I=-16:TP=-1.5',
                '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', f'{D}/reel.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '2.5', '-i', VT, '-frames:v', '1', '-vf', TRUMP, f'{R}/cov_band.jpg'], check=True)
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(Image.open(f'{R}/cov_band.jpg'), (0, 330)); bg.save(f'{R}/cov_bg.jpg', quality=95)
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{D}/cand/overlay.png', '트럼프가 본 머스크\n"80% 천재"', '', f'{R}/cov_bg.jpg', f'{D}/reel_cover.jpg'], check=True)
print('done', round(sum(b - a for _, a, b, _, _ in S), 1))
