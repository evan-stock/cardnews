"""20261107-gamdong-reel: 띠형 릴스. 저장소 루트에서 실행. 원본: 유튜브 감동란TV 4.0 화면 녹화(스레드 @polypoid23)."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
ID = 'media/20261107-gamdong-reel'; V = f'{ID}/video/v1.mp4'
R = f'{ID}/work'; os.makedirs(R, exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
Y = (255, 216, 77); BY0, BH = 660, 720
TAG = '감동란 유튜브 라이브'
L = ['공산주의 언급하자', '방송이 바로', '끊겼다']
CUT = 27.8  # 라이브 화면이 끝나는 시각


def top():
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lg = Image.open('brand/logo_typo_A.png').convert('RGBA'); h = 46
    lg = lg.resize((int(lg.width * h / lg.height), h)); im.alpha_composite(lg, (70, 238))
    f = ImageFont.truetype(FX, 34); tw = d.textlength(TAG, font=f)
    d.rounded_rectangle((70, 310, 70 + tw + 36, 362), radius=8, fill=Y); d.text((88, 336), TAG, font=f, fill=(0, 0, 0), anchor='lm')
    f = ImageFont.truetype(FB, 78)
    for i, l in enumerate(L):
        d.text((70, 433 + i * 88), l, font=f, fill=Y if i == 2 else (255, 255, 255), anchor='ls')
    im.save(f'{R}/top.png')


def cap(i, small, b1, b2, label=None):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if label:
        f = ImageFont.truetype(FX, 52); tw = d.textlength(label, font=f); cy = BY0 + BH // 2
        d.rounded_rectangle((540 - tw / 2 - 40, cy - 52, 540 + tw / 2 + 40, cy + 52), radius=14, fill=(0, 0, 0, 200), outline=(255, 255, 255, 230), width=3)
        d.text((540, cy), label, font=f, fill=(255, 255, 255), anchor='mm')
    d.text((70, 1450), small, font=ImageFont.truetype(FM, 38), fill=(225, 225, 225), anchor='ls')
    f = ImageFont.truetype(FB, 68)
    d.text((70, 1540), b1, font=f, fill=(255, 255, 255), anchor='ls'); d.text((70, 1625), b2, font=f, fill=Y, anchor='ls')
    im.save(f'{R}/cap{i}.png')


# 장면: (시작, 길이, 크롭 w:h:x:y, 가릴 영역[(x,y,w,h) 크롭 기준], 전체 흐림, 자막)
S = [
    (20.7, 7.1, '660:440:520:55', [(0, 0, 55, 440), (590, 0, 70, 230)], False,
     ('유튜버 감동란 라이브 중 (원본 음성)', '"이런 사회를 만들어…', '공산주의 사회주의"')),
    (CUT, 3.2, '660:440:520:55', [], True,
     ('그 단어가 나온 직후', '라이브 화면이', '그대로 꺼졌다')),
    (31.0, 5.3, '660:440:520:55', [], True,
     ('다시 보던 방송 (원본 음성)', '"딱 공산주의 사회주의', '언급하잖아"')),
    (36.3, 3.5, '1280:720:0:0', [], True,
     ('그리고 몇 초 뒤', '이 장면을 다시 틀던', '방송 화면도 꺼졌다')),
]
top()
segs = []
for k, (ss, dur, crop, boxes, blur_all, (s, b1, b2)) in enumerate(S):
    cap(k, s, b1, b2, '■ 라이브 화면 종료' if k in (1, 2) else ('■ 다시 보던 방송도 종료' if k == 3 else None))
    vf = f"[0:v]crop={crop}"
    if blur_all:
        vf += ",boxblur=18:2,eq=brightness=-0.12"
    vf += "[c0]"
    last = 'c0'
    for j, (x, y, w, h) in enumerate(boxes):
        vf += f";[{last}]split[sa{j}][sb{j}];[sb{j}]crop={w}:{h}:{x}:{y},boxblur=luma_radius=12:luma_power=3:chroma_radius=6:chroma_power=3[bl{j}];[sa{j}][bl{j}]overlay={x}:{y}[c{j+1}]"
        last = f'c{j+1}'
    vf += (f";[{last}]scale=1080:{BH},setsar=1[fg];color=c=black:s=1080x1920:d={dur}:r=30[bg];"
           f"[bg][fg]overlay=0:{BY0}:shortest=1[b0];[b0][1:v]overlay[b1];[b1][2:v]overlay[vo]")
    out = f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss), '-t', str(dur), '-i', V, '-i', f'{R}/top.png', '-i', f'{R}/cap{k}.png',
                    '-filter_complex', vf, '-map', '[vo]', '-map', '0:a', '-t', str(dur), '-r', '30', '-c:v', 'libx264',
                    '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-ac', '2', out], check=True)
    segs.append(out)

# 마지막: 글자 장면(무음 2.5초) — 이유는 아직 모른다 / 과연 우연일까
dur = 2.8
im = Image.new('RGB', (1080, 720), (14, 14, 16)); d = ImageDraw.Draw(im)
d.text((540, 300), '끊긴 이유는 아직 확인되지 않았습니다', font=ImageFont.truetype(FM, 44), fill=(200, 200, 200), anchor='mm')
d.text((540, 420), '과연 우연일까요?', font=ImageFont.truetype(FB, 92), fill=Y, anchor='mm')
im.save(f'{R}/end.png'); cap(9, '신고 누적·자동 조치·기술 문제 모두 가능', '판단은', '여러분 몫입니다')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', str(dur), '-i', f'{R}/end.png', '-i', f'{R}/top.png', '-i', f'{R}/cap9.png',
                '-f', 'lavfi', '-t', str(dur), '-i', 'anullsrc=r=44100:cl=stereo',
                '-filter_complex', f"[0:v]scale=1080:{BH},setsar=1[fg];color=c=black:s=1080x1920:d={dur}:r=30[bg];[bg][fg]overlay=0:{BY0}:shortest=1[b0];[b0][1:v]overlay[b1];[b1][2:v]overlay[vo]",
                '-map', '[vo]', '-map', '3:a', '-t', str(dur), '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-ar', '44100', '-ac', '2', f'{R}/s9.mp4'], check=True)
segs.append(f'{R}/s9.mp4')
open(f'{R}/list.txt', 'w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/list.txt', '-af', 'loudnorm=I=-16:TP=-1.5',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', f'{ID}/reel.mp4'], check=True)

# 커버: 말하는 순간 프레임(계좌·후원 목록 가림) + 큰 제목
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '24.5', '-i', V, '-frames:v', '1', '-vf',
                "crop=660:440:520:55,split[a][b];[b]crop=70:230:590:0,boxblur=luma_radius=12:luma_power=3:chroma_radius=6:chroma_power=3[bl];[a][bl]overlay=590:0,scale=1080:720", f'{R}/cover_band.png'], check=True)
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(Image.open(f'{R}/cover_band.png').convert('RGB'), (0, 330)); bg.save(f'{R}/cover_bg.png')
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{R}/overlay.png', '공산주의 말하자\\n방송이 바로\\n끊겼다', '', f'{R}/cover_bg.png', f'{ID}/reel_cover.jpg'], check=True)
print('done')
