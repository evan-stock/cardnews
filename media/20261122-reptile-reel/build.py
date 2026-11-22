"""뉴욕시장실 행사(11.20 '라이커스섬 교도소 폐쇄' 발표) 영상 속 남성 눈 반사 장면 → X에서 '랩틸리언' 음모론. 오늘의쓸모 띠형 릴스(원본 무음, 음악·TTS 없음).
원본: X @truthfairy131 (RT·Project America 재편집본). 로고·워터마크는 delogo로 가림. 틀: 20261121-nlgta-reel/build.py."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = 'media/20261122-reptile-reel'; V = 'media/20261122-reptile/video/v1.mp4'
R = f'{D}/work'; os.makedirs(R, exist_ok=True); os.makedirs(f'{D}/cand', exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
YE = (255, 216, 77); BY0, BH = 660, 720
TAG = '음모론'; L = ['뉴욕시장 행사 영상에', '"랩틸리언 찾았다"', '난리 난 장면']
N = '뉴욕시장실 행사 (11.20)'; X = '엑스 반응'


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
LOGO = 'delogo=x=1540:y=40:w=340:h=120,delogo=x=60:y=60:w=200:h=180,delogo=x=30:y=990:w=290:h=75,delogo=x=1590:y=1045:w=320:h=34'
WIDE = LOGO + ',scale=1080:608,pad=1080:720:0:56:black'   # 확대 안 함
S = [  # (시작, 끝, 화면, [(원본 시각 시작, 끝, 누가, 줄1, 줄2)])
    (0.0, 2.0, WIDE, [(0.0, 2.0, N, '뉴욕시장 기자회견', '뒷줄에 선 한 남성')]),
    (2.0, 16.0, WIDE, [(2.0, 9.0, N, '맘다니 뉴욕시장의', '라이커스섬 교도소 폐쇄 발표'), (9.0, 16.0, X, '그런데 사람들이 본 건', '시장이 아니라 뒤쪽 남성')]),
    (16.0, 24.0, WIDE, [(16.0, 24.0, X, '확대해서 보면', '눈이 번쩍?')]),
    (24.0, 30.09, WIDE, [(24.0, 27.0, X, '"와, 이거 진짜네"', '"앞줄 오른쪽 남자도 봐"'), (27.0, 30.09, X, '도마뱀 인간 \'랩틸리언\'', '음모론까지 등장')]),
]
segs = []; ci = 0
for k, (a, b, crop, caps) in enumerate(S):
    dur = b - a
    inputs = ['-ss', str(a), '-t', f'{dur:.3f}', '-i', V, '-f', 'lavfi', '-t', f'{dur:.3f}', '-i', 'anullsrc=r=44100:cl=stereo', '-i', f'{R}/top.png']
    fc = f"[0:v]{crop},setsar=1,pad=1080:1920:0:{BY0}:black,fps=30[b0];[b0][2:v]overlay[b1]"; last = 'b1'; n = 3
    for (t0, t1, who, l1, l2) in caps:
        cap(ci, who, l1, l2); inputs += ['-i', f'{R}/cap{ci}.png']
        fc += f";[{last}][{n}:v]overlay=enable='between(t,{t0 - a:.2f},{t1 - a:.2f})'[c{n}]"; last = f'c{n}'; ci += 1; n += 1
    fc += f";[{last}]setsar=1[vo];[1:a]aresample=44100[ao]"
    out = f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[vo]', '-map', '[ao]', '-t', f'{dur:.3f}', '-r', '30',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k', out], check=True)
    segs.append(os.path.abspath(out))
open(f'{R}/list.txt', 'w').write(''.join(f"file '{s}'\n" for s in segs))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/list.txt', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', f'{D}/reel.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '25.6', '-i', V, '-frames:v', '1', '-vf', WIDE, f'{R}/cov_band.jpg'], check=True)
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(Image.open(f'{R}/cov_band.jpg'), (0, 330)); bg.save(f'{R}/cov_bg.jpg', quality=95)
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{D}/cand/overlay.png', '뉴욕시장 행사에\n랩틸리언?', '', f'{R}/cov_bg.jpg', f'{D}/reel_cover.jpg'], check=True)
print('done', round(sum(b - a for a, b, _, _ in S), 1))
