"""띠형 가로 영상 릴스 — 샌더스 AI 중단 영상 + 한글 자막 (20261106-xr1). 저장소 루트에서 실행."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
R='/tmp/band_work'; os.makedirs(R,exist_ok=True); M='media'; ID='20261106-xr1'
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
TAG='미국 AI 규제'
L=['샌더스 "민주당은','AI 데이터센터 중단,','초지능 금지"']
def top():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); h=46; lg=lg.resize((int(lg.width*h/lg.height),h)); im.alpha_composite(lg,(70,238))
    f=ImageFont.truetype(FX,34); tw=d.textlength(TAG,font=f)
    d.rounded_rectangle((70,310,70+tw+36,362),radius=8,fill=Y); d.text((88,336),TAG,font=f,fill=(0,0,0),anchor='lm')
    f=ImageFont.truetype(FB,78)
    for i,l in enumerate(L): d.text((70,433+i*88),l,font=f,fill=Y if i==2 else (255,255,255),anchor='ls')
    im.save(f'{R}/top.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,1450),small,font=ImageFont.truetype(FM,38),fill=(225,225,225),anchor='ls')
    f=ImageFont.truetype(FB,68)
    d.text((70,1540),b1,font=f,fill=(255,255,255),anchor='ls'); d.text((70,1625),b2,font=f,fill=Y,anchor='ls')
    im.save(f'{R}/cap{i}.png')
top()
SRC=f'{M}/{ID}/video/v3.mp4'
CROP='840:560:220:0'
S=[
 (SRC,0,12.4,CROP,[(0,12.4,'샌더스 상원의원 영상 · 11월 5일 공개','AI 데이터센터 중단,','초지능은 금지')]),
 (SRC,12.4,14.8,CROP,[(0,14.8,'어제 선거 결과를 언급하며 (샌더스 주장)','수십 개 지역 주민들','데이터센터 중단에 찬성')]),
 (SRC,27.2,6.64,CROP,[(0,6.64,'샌더스 주장 정리','데이터센터 중단,','국민이 원하는 것')]),
]
SUBS=[(0.4,5.9,'민주당은 AI 데이터센터를\n전국적으로 일시 중단시키고'),
      (5.9,12.0,'첨단 AI 개발을 멈추고\n초지능을 금지해야 합니다'),
      (12.5,17.0,'덧붙이자면, 어제 치러진 선거에서'),
      (17.0,21.5,'미국 전역 수십 개 지역의 시민들이'),
      (21.5,27.2,'데이터센터 건설 중단에\n찬성표를 던졌습니다'),
      (27.2,33.9,'다시 말해, 데이터센터 건설 중단은\n바로 미국 국민이 원하는 것입니다')]
segs=[]; ci=0
for k,(src,ss,dur,crop,caps) in enumerate(S):
    inputs=['-ss',str(ss),'-t',str(dur),'-i',src,'-i',f'{R}/top.png']
    fc=(f"[0:v]split[s1][s2];[s1]crop={crop},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.28[bg];"
        f"[s2]crop={crop},scale=1080:{BH},setsar=1[fg];[bg][fg]overlay=0:{BY0}[b0];[b0][1:v]overlay[b1]")
    last='b1'
    for j,(t0,t1,s,b1,b2) in enumerate(caps):
        cap(ci,s,b1,b2); inputs+=['-i',f'{R}/cap{ci}.png']; n=2+j
        fc+=f";[{last}][{n}:v]overlay=enable='between(t,{t0},{t1})'[c{j}]"; last=f'c{j}'; ci+=1
    out=f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc+f";[{last}]setsar=1[vo]",'-map','[vo]','-map','0:a?','-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','2','-b:a','160k',out],check=True)
    segs.append(out)
open(f'{R}/list.txt','w').write(''.join(f"file '{s}'\n" for s in segs))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{R}/list.txt','-c:v','copy','-c:a','aac','-b:a','160k',f'{R}/reel_nosub.mp4'],check=True)
# 한글 자막(띠 아래쪽 안, 시간별)
fnt=ImageFont.truetype(FB,44); sub_inputs=[]; fc=[]; prev='0:v'
for i,(a,b,t) in enumerate(SUBS):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    lines=t.split('\n'); lh=58
    ww=max(d.textlength(x,font=fnt) for x in lines); x0=(1080-ww)/2-34; bh=lh*len(lines)+20
    y0=1358-bh
    d.rounded_rectangle((x0,y0,x0+ww+68,y0+bh),radius=14,fill=(0,0,0,175))
    for k,x in enumerate(lines): d.text((540,y0+10+lh*k+lh/2),x,font=fnt,fill=(255,255,255),anchor='mm')
    im.save(f'{R}/sub{i}.png'); sub_inputs+=['-i',f'{R}/sub{i}.png']
    fc.append(f"[{prev}][{i+1}:v]overlay=enable='between(t,{a},{b})'[v{i}]"); prev=f'v{i}'
subprocess.run(['ffmpeg','-v','error','-y','-i',f'{R}/reel_nosub.mp4',*sub_inputs,'-filter_complex',';'.join(fc),'-map',f'[{prev}]','-map','0:a?','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',f'{R}/reel.mp4'],check=True)
print('done')
