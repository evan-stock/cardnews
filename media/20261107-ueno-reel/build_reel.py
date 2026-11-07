"""20261107-ueno-reel: 띠형 릴스(band_build.py 틀 그대로, 사진 장면 추가). 저장소 루트에서 실행."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
ID = 'media/20261107-ueno-reel'
R = f'{ID}/work'; os.makedirs(R, exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
Y = (255, 216, 77); BY0, BH = 660, 720
TAG = '파라과이 은행 붕괴'
L = ['은행 하나 무너지자', '대통령이 쫓겨났다', "'나무위키'도 위험?"]


def top():
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lg = Image.open('brand/logo_typo_A.png').convert('RGBA'); h = 46
    lg = lg.resize((int(lg.width * h / lg.height), h)); im.alpha_composite(lg, (70, 238))
    f = ImageFont.truetype(FX, 34); tw = d.textlength(TAG, font=f)
    d.rounded_rectangle((70, 310, 70 + tw + 36, 362), radius=8, fill=Y); d.text((88, 336), TAG, font=f, fill=(0, 0, 0), anchor='lm')
    f = ImageFont.truetype(FB, 78)
    for i, l in enumerate(L):
        txt = l.replace("'", '')
        d.text((70, 433 + i * 88), txt, font=f, fill=Y if i == 2 else (255, 255, 255), anchor='ls')
    im.save(f'{R}/top.png')


def cap(i, small, b1, b2):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((70, 1450), small, font=ImageFont.truetype(FM, 38), fill=(225, 225, 225), anchor='ls')
    f = ImageFont.truetype(FB, 68)
    d.text((70, 1540), b1, font=f, fill=(255, 255, 255), anchor='ls'); d.text((70, 1625), b2, font=f, fill=Y, anchor='ls')
    im.save(f'{R}/cap{i}.png')


def still(src, box, marks, out, dur):
    """스크린샷을 3:2로 잘라 노란 형광펜 표시 후 무음 mp4로."""
    im = Image.open(src).convert('RGB').crop(box).resize((1080, 720), Image.LANCZOS)
    sx = 1080 / (box[2] - box[0]); sy = 720 / (box[3] - box[1])
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for (x0, y0, x1, y1) in marks:
        d.rectangle(((x0 - box[0]) * sx, (y0 - box[1]) * sy, (x1 - box[0]) * sx, (y1 - box[1]) * sy), fill=(255, 216, 77, 110))
    im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'); png = out.replace('.mp4', '.png'); im.save(png)
    # 살짝 확대(켄번스)로 정지 화면 느낌을 줄인다
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', png, '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
                    '-t', str(dur), '-vf', f"scale=2160:1440,zoompan=z='1+0.0015*on':x='0':y='0':d={int(dur*30)}:s=1080x720:fps=30",
                    '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)


top()
C = f'{ID}/cand'
still(f'{C}/namu_ueno.jpg', (0, 110, 800, 643), [(16, 135, 220, 185)], f'{R}/st_namu.mp4', 3.5)
still(f'{C}/umanle_notice.jpg', (0, 140, 800, 673), [(56, 300, 640, 362), (56, 552, 670, 600)], f'{R}/st_notice1.mp4', 4)
still(f'{C}/umanle_notice.jpg', (0, 580, 800, 1113), [(56, 920, 700, 1000)], f'{R}/st_notice2.mp4', 4)

V = f'{ID}/video'
S = [  # src, ss, dur, crop(w:h:x:y) 3:2, captions [(t0,t1,small,b1,b2)]
    (f'{V}/v3.mp4', 0, 3.5, '720:480:0:220', [(0, 3.5, '11월 4일 밤 · 파라과이 아순시온', '"대통령 물러나라"', '거리 메운 예금자들')]),
    (f'{V}/v1.mp4', 0, 4.6, '540:360:230:0', [(0, 4.6, '시위 현장 인터뷰 (원본 영상 자막 번역)', '"돈도 다 빼앗더니', '이젠 우릴 죽이려 해"')]),
    (f'{V}/v1.mp4', 10.6, 4, '600:400:0:60', [(0, 4, '진압 경찰 저지선 앞', '휠체어 탄 노인까지', '거리로 나왔다')]),
    (f'{V}/v4.mp4', 66, 4, '1620:1080:150:0', [(0, 4, '5일 사표 제출 → 6일 상원 44 대 0', '은행 붕괴 나흘 만에', '대통령 탄핵·파면')]),
    (f'{R}/st_namu.mp4', 0, 3.5, '1080:720:0:0', [(0, 3.5, '그런데 이 은행, 한국과도 엮였다', '나무위키 운영사의', '거래 은행이었다')]),
    (f'{R}/st_notice1.mp4', 0, 4, '1080:720:0:0', [(0, 4, '운영사 우만레 공지 · 11월 3일', '송금 일시 중단,', '대금 지급 지연')]),
    (f'{R}/st_notice2.mp4', 0, 4, '1080:720:0:0', [(0, 4, '협력업체에 보낸 부탁', '"서비스는 계속', '유지해 달라"')]),
]
segs = []; ci = 0
for k, (src, ss, dur, crop, caps) in enumerate(S):
    inputs = ['-ss', str(ss), '-t', str(dur), '-i', src, '-i', f'{R}/top.png']
    fc = (f"[0:v]crop={crop},scale=1080:{BH},setsar=1[fg];color=c=black:s=1080x1920:d={dur}:r=30[bg];"
          f"[bg][fg]overlay=0:{BY0}:shortest=1[b0];[b0][1:v]overlay[b1]")
    last = 'b1'
    for j, (t0, t1, s, b1, b2) in enumerate(caps):
        cap(ci, s, b1, b2); inputs += ['-i', f'{R}/cap{ci}.png']; n = 2 + j
        fc += f";[{last}][{n}:v]overlay=enable='between(t,{t0},{t1})'[c{j}]"; last = f'c{j}'; ci += 1
    out = f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc + f";[{last}]setsar=1[vo]", '-map', '[vo]', '-map', '0:a?',
                    '-t', str(dur), '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k', out], check=True)
    segs.append(out)
open(f'{R}/list.txt', 'w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/list.txt', '-af', 'loudnorm=I=-16:TP=-1.5',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', f'{ID}/reel.mp4'], check=True)
print('done')
