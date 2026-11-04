import subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
os.chdir('/home/claude/cardnews')
R='/home/claude/build/w'; os.makedirs(R,exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
SRC='media/20261105-thiel-reel/video/v1.mp4'; CROP='720:480:243:8'
TAG='팔란티어 창업자 · 9월 인터뷰'
L=['피터 틸 두 달 전 예언','"중간선거 민주당 승리"','다음은 \'극좌 대통령\'?']
def fit(d,t,size,maxw,font=FB):
    while True:
        f=ImageFont.truetype(font,size)
        if d.textlength(t,font=f)<=maxw or size<40: return f
        size-=2
def top(path):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); h=46; lg=lg.resize((int(lg.width*h/lg.height),h)); im.alpha_composite(lg,(70,238))
    f=ImageFont.truetype(FX,34); tw=d.textlength(TAG,font=f)
    d.rounded_rectangle((70,310,70+tw+36,362),radius=8,fill=Y); d.text((88,336),TAG,font=f,fill=(0,0,0),anchor='lm')
    for i,l in enumerate(L):
        txt=l.replace("'","")
        f=fit(d,txt,78,940)
        d.text((70,433+i*88),txt,font=f,fill=Y if i==len(L)-1 else (255,255,255),anchor='ls')
    im.save(path)
def sub(path,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((540,1440),'피터 틸 · 9월 24일 인터뷰 (선거 6주 전)',font=ImageFont.truetype(FM,36),fill=(220,220,220),anchor='ms')
    b2=b2 if b2!='"' else ''
    if not b2: b1=b1+'"' if not b1.endswith('"') else b1
    ls=[b1]+([b2] if b2 else [])
    for i,t in enumerate(ls):
        f=fit(d,t,64,960)
        d.text((540,1535+i*84),t,font=f,fill=(255,255,255),anchor='ms',stroke_width=5,stroke_fill=(0,0,0))
    im.save(path)
def cap(path,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,1450),small,font=ImageFont.truetype(FM,38),fill=(225,225,225),anchor='ls')
    d.text((70,1540),b1,font=fit(d,b1,68,940),fill=(255,255,255),anchor='ls')
    d.text((70,1625),b2,font=fit(d,b2,68,940),fill=Y,anchor='ls')
    im.save(path)
top(f'{R}/top.png')
SM='피터 틸 · 독일 MD MEETS 인터뷰'
# (원본 시작, 길이, 자막들[(t0,t1,small,b1,b2)])
CAPS=[(0,3.25,'"이번 가을 중간선거에서','공화당이 참패하면"'),
 (3.25,6.25,'"그러면 민주당은','"'),
 (6.25,9.75,'"2028년엔 뭘 해도','이긴다고 생각할 거예요"'),
 (9.75,13.25,'"그러니 아마도','"'),
 (13.25,16,'"극좌를 막는 방어벽 역할을','제대로 못 할 겁니다"'),
 (16,18.5,'"민주사회주의자가','이기는 걸 막으려고"'),
 (18.5,21.5,'"총력을 다하진','않을 거란 얘기죠"'),
 (21.5,25.25,'"그래서 한 달 반 뒤','중간선거에서 민주당이"'),
 (25.25,29.25,'"꽤 선전할 거고','그러면 대선 후보가"'),
 (29.25,33.25,'"중도좌파든 극좌든','상관없게 될 거예요"'),
 (33.25,36.75,'"완전히 열린 판이','되는 거죠"')]
SS=13.5; DUR=36.75
inputs=['-ss',str(SS),'-t',str(DUR),'-i',SRC,'-i',f'{R}/top.png']
fc=(f"[0:v]split[s1][s2];[s1]crop={CROP},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.28[bg];"
    f"[s2]crop={CROP},scale=1080:{BH},setsar=1[fg];[bg][fg]overlay=0:{BY0}[b0];[b0][1:v]overlay[b1]")
last='b1'
for j,c in enumerate(CAPS):
    sub(f'{R}/c{j}.png',*c[2:]); inputs+=['-i',f'{R}/c{j}.png']
    fc+=f";[{last}][{j+2}:v]overlay=enable='between(t,{c[0]},{c[1]-0.01})'[c{j}]"; last=f'c{j}'
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc+f";[{last}]setsar=1[vo]",'-map','[vo]','-map','0:a','-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','2','-b:a','160k',f'{R}/s0.mp4'],check=True)
# 결말 장면 2개: 마지막 프레임 정지 + 자막
END=[('11월 3일 미국 중간선거 결과','민주당, 상원·하원','모두 뒤집었다',4),
     ('틸의 다음 경고','"극좌 대통령 후보 확률 50%"','"그건 미국의 끝"',4.5)]
subprocess.run(['ffmpeg','-v','error','-y','-ss',str(SS+30.5),'-i',SRC,'-frames:v','1',f'{R}/freeze.png'],check=True)
for k,(s,b1,b2,d) in enumerate(END):
    cap(f'{R}/e{k}.png',s,b1,b2)
    fc=(f"[0:v]crop={CROP},split[s1][s2];[s1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.28[bg];"
        f"[s2]scale=1080:{BH},setsar=1,eq=brightness=-0.12[fg];[bg][fg]overlay=0:{BY0}[b0];[b0][1:v]overlay[b1];[b1][2:v]overlay,setsar=1[vo]")
    subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-t',str(d),'-i',f'{R}/freeze.png','-i',f'{R}/top.png','-i',f'{R}/e{k}.png','-f','lavfi','-t',str(d),'-i','anullsrc=r=44100:cl=stereo',
        '-filter_complex',fc,'-map','[vo]','-map','3:a','-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','2','-b:a','160k','-shortest',f'{R}/e{k}.mp4'],check=True)
open(f'{R}/list.txt','w').write(''.join(f"file '{R}/{n}.mp4'\n" for n in ['s0','e0','e1']))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{R}/list.txt','-af','loudnorm=I=-16:TP=-1.5','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',f'{R}/reel.mp4'],check=True)
print('done')
