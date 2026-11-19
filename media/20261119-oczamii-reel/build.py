"""국회 본회의장 수능 위급재난문자 띠형 릴스(2026.11.19). 저장소 루트에서: python3 media/20261119-oczamii-reel/build.py
원본: @oczamii X 영상(제주MBC 현장영상 화면) 1280x590. 띠 crop 780x520(+170+70)로 방송사 로고·자막·수어 원을 잘라내고,
앞 3.6초 의안 자막띠는 흐림 처리. 한 구간으로 렌더해 컷 사이 깜박임 없음.
"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = 'media/20261119-oczamii-reel'; SRC = 'media/20261119-oczamii/video/v1.mp4'; W = f'{D}/work'
os.makedirs(W, exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
Y = (255, 216, 77); BY0, BH = 660, 720
CROP = '780:520:170:70'
TAG = '2027 수능 위급재난문자'
L = ['수능 커닝 잡는 경보,', '국회 본회의장에서도', "'삐-' 울렸다"]
CAPS = [
    (0, 3.6, '11월 19일 오후 2시 21분 · 국회 본회의', 'EBS 결산안 가결 선포,', '의사봉 들던 그 순간'),
    (3.6, 7.0, '수능 부정행위 방지 2차 위급재난문자', "의사봉 '탕탕탕'과 함께", "본회의장에 '삐-'"),
    (7.0, 12.4, '술렁이는 장내를 본 조정식 국회의장', '의장도 결국', '참지 못한 미소'),
    (12.4, 18.6, '무음·진동이어도 최대 음량으로 10.5초', '의원들 일제히', '휴대폰 꺼내 확인'),
    (18.6, 26, '수신 거부 불가 · 국회의원도 예외 없음', 'AI 커닝 잡으려 보낸 문자,', '국회도 못 피했다'),
]


def top():
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lg = Image.open('brand/logo_typo_A.png').convert('RGBA'); h = 46
    lg = lg.resize((int(lg.width * h / lg.height), h), Image.LANCZOS); im.alpha_composite(lg, (70, 238))
    f = ImageFont.truetype(FX, 34); tw = d.textlength(TAG, font=f)
    d.rounded_rectangle((70, 310, 70 + tw + 36, 362), radius=8, fill=Y); d.text((88, 336), TAG, font=f, fill=(0, 0, 0), anchor='lm')
    f = ImageFont.truetype(FB, 78)
    for i, l in enumerate(L):
        d.text((70, 433 + i * 88), l, font=f, fill=Y if i == len(L) - 1 else (255, 255, 255), anchor='ls')
    im.save(f'{W}/top.png')


def cap(i, small, b1, b2):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((70, 1450), small, font=ImageFont.truetype(FM, 38), fill=(225, 225, 225), anchor='ls')
    f = ImageFont.truetype(FB, 68)
    d.text((70, 1540), b1, font=f, fill=(255, 255, 255), anchor='ls'); d.text((70, 1625), b2, font=f, fill=Y, anchor='ls')
    im.save(f'{W}/cap{i}.png')


top()
for i, c in enumerate(CAPS):
    cap(i, *c[2:])
inputs = ['-i', SRC, '-i', f'{W}/top.png'] + sum([['-i', f'{W}/cap{i}.png'] for i in range(len(CAPS))], [])
# 의안 자막띠(원본 y495~525, x230~956) → crop 기준 y425~455, x60~786 → 앞 3.6초 흐림
fc = (f"[0:v]crop={CROP},split[a][b];[b]crop=780:44:0:419,boxblur=10:2[bl];[a][bl]overlay=0:419:enable='lt(t,3.6)',"
      f"scale=1080:{BH}:flags=lanczos,setsar=1,pad=1080:1920:0:{BY0}:black[v0];[v0][1:v]overlay[v1]")
last = 'v1'
for i, (t0, t1, *_r) in enumerate(CAPS):
    fc += f";[{last}][{i + 2}:v]overlay=enable='between(t,{t0},{t1})'[c{i}]"; last = f'c{i}'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc + f";[{last}]format=yuv420p[vo]",
                '-map', '[vo]', '-map', '0:a', '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19',
                '-af', 'loudnorm=I=-16:TP=-1.5', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k',
                '-movflags', '+faststart', f'{D}/reel.mp4'], check=True)

# 커버: 검정 바탕 + 가로 띠(1080x720, y=330)에 미소 장면 + reel_overlay 큰 제목(기준선 1675)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '9', '-i', SRC, '-frames:v', '1', '-vf', f'crop={CROP},scale=1080:{BH}:flags=lanczos', f'{W}/cov_band.png'], check=True)
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(Image.open(f'{W}/cov_band.png').convert('RGB'), (0, 330))
bg.save(f'{W}/cover_bg.jpg', quality=95)
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{W}/overlay.png', "국회 본회의장에\n울린 '수능 경보'", '', f'{W}/cover_bg.jpg', f'{D}/reel_cover.jpg'], check=True)
print('done')
