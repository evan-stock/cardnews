"""20261102-xreel 플로리다 리어젯 추락 블랙박스 릴스(띠형). 저장소 루트에서: python3 media/20261102-xreel/build_reel.py"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
ID = '20261102-xreel'
M = f'media/{ID}'; R = f'{M}/work'; os.makedirs(R, exist_ok=True); os.makedirs(f'{M}/cand', exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
Y = (255, 216, 77); BY0, BH = 660, 720
SRC = f'{M}/video/v1.mp4'
CROP = '960:640:320:0'  # 아래 계기판·블랙박스 시각 표시는 잘라냄
TAG = '미국 플로리다 제트기 추락'
L = ['폭우 속 블랙박스 앞', '제트기가 떨어졌다', '탑승자 9명 전원 사망']
CAPS = [
    (0, 2.0, '11월 1일 낮 · 미국 플로리다 그리낙스', '비 내리는 왕복 도로,', '앞차 너머 하늘에서'),
    (2.0, 6.5, '리어젯 60 비즈니스 제트기', '도로 위로 그대로 추락,', '거대한 불덩이'),
    (6.5, 10.5, '플로리다 주지사', '"미사일이 떨어지는', '것 같았다"'),
    (10.5, 14.1, '텍사스 오스틴 → 바하마 가던 길', '주택가 코앞 도로,', '원인은 조사 중'),
]


def top():
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lg = Image.open('brand/logo_typo_A.png').convert('RGBA'); h = 46; lg = lg.resize((int(lg.width * h / lg.height), h)); im.alpha_composite(lg, (70, 238))
    f = ImageFont.truetype(FX, 34); tw = d.textlength(TAG, font=f)
    d.rounded_rectangle((70, 310, 70 + tw + 36, 362), radius=8, fill=Y); d.text((88, 336), TAG, font=f, fill=(0, 0, 0), anchor='lm')
    f = ImageFont.truetype(FB, 78)
    for i, l in enumerate(L):
        d.text((70, 433 + i * 88), l, font=f, fill=Y if i == len(L) - 1 else (255, 255, 255), anchor='ls')
    im.save(f'{R}/top.png')


def cap(i, small, b1, b2):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((70, 1450), small, font=ImageFont.truetype(FM, 38), fill=(225, 225, 225), anchor='ls')
    f = ImageFont.truetype(FB, 68)
    d.text((70, 1540), b1, font=f, fill=(255, 255, 255), anchor='ls'); d.text((70, 1625), b2, font=f, fill=Y, anchor='ls')
    im.save(f'{R}/cap{i}.png')


top()
inputs = ['-i', SRC, '-i', f'{R}/top.png']
fc = (f"[0:v]split[s1][s2];[s1]crop={CROP},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.28[bg];"
      f"[s2]crop={CROP},scale=1080:{BH},setsar=1[fg];[bg][fg]overlay=0:{BY0}[b0];[b0][1:v]overlay[b1]")
last = 'b1'
for j, (t0, t1, s, b1, b2) in enumerate(CAPS):
    cap(j, s, b1, b2); inputs += ['-i', f'{R}/cap{j}.png']
    fc += f";[{last}][{2 + j}:v]overlay=enable='between(t,{t0},{t1})'[c{j}]"; last = f'c{j}'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc + f";[{last}]setsar=1[vo]", '-map', '[vo]', '-map', '0:a?',
                '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p',
                '-af', 'loudnorm=I=-16:TP=-1.5', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k', '-movflags', '+faststart', f'{M}/reel.mp4'], check=True)

# 커버: 흐린 배경 + 가로 띠(y=330) + 격자 통일형 큰 제목(reel_overlay 양식)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '3.4', '-i', SRC, '-frames:v', '1', '-vf', f'crop={CROP}', f'{R}/cover_frame.png'], check=True)
fr = Image.open(f'{R}/cover_frame.png').convert('RGB')
from PIL import ImageFilter, ImageEnhance
bg = fr.resize((int(fr.width * 1920 / fr.height), 1920), Image.LANCZOS)
bg = bg.crop(((bg.width - 1080) // 2, 0, (bg.width - 1080) // 2 + 1080, 1920)).filter(ImageFilter.GaussianBlur(40))
bg = ImageEnhance.Brightness(bg).enhance(0.6)
bg.paste(fr.resize((1080, 720), Image.LANCZOS), (0, 330))
bg.save(f'{M}/cand/cover_bg.jpg', quality=95)
import sys
sys.path.insert(0, 'scripts')
from reel_overlay import overlay
ov = overlay(['블랙박스 앞', '도로 위로', '제트기 추락'])
Image.alpha_composite(bg.convert('RGBA'), ov).convert('RGB').save(f'{M}/reel_cover.jpg', quality=93)
print('done')
