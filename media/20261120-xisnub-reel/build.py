"""시진핑 '같은 날 다른 대접'(트럼프 vs 다카이치) 띠형 릴스(2026.11.20, 오늘의쓸모, TTS 없음). 저장소 루트에서: python3 media/20261120-xisnub-reel/build.py
틀: media/20261117-kangst-reel/build.py(띠형, 움직임·깜박임 없음). 원본: Viory(X @ThayzzySmith 공유) 트럼프·시진핑 악수 v3·에스컬레이터 v2,
SBS D리포트 '중, 다카이치 대놓고 냉대'(y1, 박힌 자막·로고는 잘라냄). 사실: 뉴스핌·아주경제·서울신문·경향신문·SBS 11.19~20. 따옴표 없음.
소리: 배경음악 + Viory 장면만 현장음(SBS 장면 소리 끔)."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = 'media/20261120-xisnub-reel'; V = 'media/20261120-feed-xisnub/video'; Y = 'media/20261120-feed-xisnub3/video/y1.mp4'
R = f'{D}/work'; os.makedirs(R, exist_ok=True); os.makedirs(f'{D}/cand', exist_ok=True)
FB = 'assets/fonts/Pretendard-Black.otf'; FM = 'assets/fonts/Pretendard-Medium.otf'; FX = 'assets/fonts/Pretendard-ExtraBold.otf'
YE = (255, 216, 77); BY0, BH = 660, 720
TAG = '선전 APEC'; L = ['같은 날 시진핑의', '트럼프는 환대', '다카이치는 냉대']


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
    f = ImageFont.truetype(FB, 68)
    d.text((70, 1540), b1, font=f, fill=(255, 255, 255), anchor='ls'); d.text((70, 1625), b2, font=f, fill=YE, anchor='ls')
    for t in (b1, b2): assert d.textlength(t, font=f) <= 950, t
    assert d.textlength(small, font=ImageFont.truetype(FM, 38)) <= 950, small
    im.save(f'{R}/cap{i}.png')


top()
CV = 'crop=1530:1020:150:60'      # Viory 1920x1080: 오른쪽 위 로고 밖으로
CY = 'crop=840:560:220:0'        # SBS 1280x720: 아래 박힌 자막·오른쪽 위 로고 잘라냄
SV, SS = '영상: Viory', '영상: SBS D리포트'
S = [  # 환대 vs 냉대만 번갈아 대비 (src, ss, dur, crop, 소리 살림, (small, b1, b2))
    (Y, 21.0, 3.0, CY, False, (f'환대 · 트럼프 공항 도착 · {SS}', '시진핑이', '직접 마중')),
    (Y, 0.5, 3.4, CY, False, (f'냉대 · 다카이치 공항 도착 · {SS}', '시진핑 없이', '의전 대사만')),
    (f'{V}/v2.mp4', 1.2, 4.6, 'crop=1380:920:200:150', True, (f'환대 · 트럼프 · {SV}', '손 내밀자', '바로 잡았다')),
    (Y, 6.2, 3.6, CY, False, (f'냉대 · 다카이치 · {SS}', '의장대 10명 남짓', '꽃도 음악도 없이')),
    (f'{V}/v3.mp4', 0.3, 4.2, CV, True, (f'환대 · 트럼프 · {SV}', '웃으며', '오래 악수')),
    (Y, 77.4, 3.6, CY, False, (f'냉대 · 다카이치 · 중화권 매체 보도 · {SS}', '악수만 하고', '대화 없이')),
    (f'{V}/v3.mp4', 11.0, 4.0, CV, True, ('18일 선전 APEC', '같은 날, 같은 시진핑', '환대 vs 냉대')),
]
segs = []
for k, (src, ss, dur, crop, snd, (sm, b1, b2)) in enumerate(S):
    cap(k, sm, b1, b2)
    inputs = ['-ss', str(ss), '-t', str(dur), '-i', src, '-i', f'{R}/top.png', '-i', f'{R}/cap{k}.png', '-f', 'lavfi', '-t', str(dur), '-i', 'anullsrc=r=44100:cl=stereo']
    fc = (f"[0:v]{crop},scale=1080:{BH}:flags=lanczos,setsar=1,pad=1080:1920:0:{BY0}:black,fps=30[b0];[b0][1:v]overlay[b1];[b1][2:v]overlay,setsar=1[vo]")
    fc += (f";[0:a]volume=0.8,afade=t=in:d=0.08,afade=t=out:st={dur - 0.12}:d=0.12,aresample=44100[ao]" if snd else ";[3:a]anull[ao]")
    out = f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[vo]', '-map', '[ao]', '-t', str(dur), '-r', '30',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k', out], check=True)
    segs.append(os.path.abspath(out))
open(f'{R}/list.txt', 'w').write(''.join(f"file '{s}'\n" for s in segs))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{R}/list.txt', '-c', 'copy', f'{R}/body.mp4'], check=True)
TOT = sum(x[2] for x in S)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{R}/body.mp4', '-ss', '8', '-i', 'assets/bgm/worthy/plans_in_motion.mp3', '-filter_complex',
                f"[1:a]volume=0.32,afade=t=out:st={TOT - 0.8:.2f}:d=0.8[m];[0:a][m]amix=inputs=2:normalize=0,alimiter=limit=0.95,atrim=0:{TOT:.2f},loudnorm=I=-16:TP=-1.5[a]",
                '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', f'{D}/reel.mp4'], check=True)
# 커버: 트럼프·시진핑 악수 띠 + 격자 통일형 큰 제목
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1.5', '-i', f'{V}/v3.mp4', '-frames:v', '1', '-vf', f'{CV},scale=1080:{BH}', f'{R}/cov_band.jpg'], check=True)
bg = Image.new('RGB', (1080, 1920), (0, 0, 0)); bg.paste(Image.open(f'{R}/cov_band.jpg'), (0, 330)); bg.save(f'{R}/cov_bg.jpg', quality=95)
subprocess.run(['python3', 'scripts/reel_overlay.py', f'{D}/cand/overlay.png', '트럼프는 환대\n다카이치는 냉대', '', f'{R}/cov_bg.jpg', f'{D}/reel_cover.jpg'], check=True)
print('done', round(TOT, 1))
