"""띠형 가로 영상 릴스(2026.10.31 사용자 확정, 2026.11.06 상하단 검정 배경). 저장소 루트에서 실행: python3 scripts/landscape_reel/band_build.py
사용: 아래 top()의 tag·L(제목 3줄)과 S(장면 목록: src, ss, dur, 띠 crop, 자막[(시작,끝,작은줄,굵은1,굵은2)])만 바꾼다. 결과는 work/reel.mp4.
"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
R='/tmp/h/work'; os.makedirs(R,exist_ok=True); M='media'
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
def top():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); h=46; lg=lg.resize((int(lg.width*h/lg.height),h)); im.alpha_composite(lg,(70,238))
    f=ImageFont.truetype(FX,34); tag='재향군인의 날 · 미국 알링턴'; tw=d.textlength(tag,font=f)
    d.rounded_rectangle((70,310,70+tw+36,362),radius=8,fill=Y); d.text((88,336),tag,font=f,fill=(0,0,0),anchor='lm')
    f=ImageFont.truetype(FB,78); L=['미 국방장관 일행','기념사진 찍다가',"초병에게 '호통'"]
    for i,l in enumerate(L): d.text((70,433+i*88),l,font=f,fill=Y if i==2 else (255,255,255),anchor='ls')
    im.save(f'{R}/top.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,1450),small,font=ImageFont.truetype(FM,38),fill=(225,225,225),anchor='ls')
    f=ImageFont.truetype(FB,68)
    d.text((70,1540),b1,font=f,fill=(255,255,255),anchor='ls'); d.text((70,1625),b2,font=f,fill=Y,anchor='ls')
    im.save(f'{R}/cap{i}.png')
top()
S=[
 ('media/20261112-hegseth-reel/video/v2.mp4',12,3.5,'1080:720:100:0',[(0,3.5,'11월 11일 · 미국 알링턴 국립묘지','재향군인의 날 헌화 뒤','헤그세스 국방장관 부부')]),
 ('media/20261112-hegseth-reel/video/v1.mp4',1,3.5,'1500:1000:420:80',[(0,3.5,'장관 부부·비서실장·보좌관','무명용사의 묘 앞에서','기념사진')]),
 ('media/20261112-hegseth-reel/video/v1.mp4',56,9.5,'1500:1000:420:80',[(0,5.7,'사진을 찍고 흩어지던 순간','일행 중 누군가','크게 웃음을 터뜨렸다'),(5.7,9.5,'묘를 지키던 미 육군 초병','"모든 방문객은 항상','정숙과 존중을 지켜라!"')]),
 ('media/20261112-hegseth-reel/video/v1.mp4',65.5,3.5,'1500:1000:420:80',[(0,3.5,'걸음을 멈추고 돌아서서','장관 일행을 향해','그 자리에서 호통')]),
 ('media/20261112-hegseth-reel/video/v1.mp4',69,3.4,'1500:1000:420:80',[(0,3.4,'24시간 묘를 지키는 초병들','관람객 제지는','하루 2~3번 있는 일')]),
 ('media/20261112-hegseth-reel/video/v2.mp4',13,3.5,'1080:720:100:0',[(0,3.5,'미국 국방부 대변인','"병사가 올바르고','정중하게 상기시켰다"')]),
]
segs=[]; ci=0
for k,(src,ss,dur,crop,caps) in enumerate(S):
    inputs=['-ss',str(ss),'-t',str(dur),'-i',src,'-i',f'{R}/top.png']; fc=(f"[0:v]split[s1][s2];[s1]crop={crop},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,drawbox=c=black:t=fill[bg];"
        f"[s2]crop={crop},scale=1080:{BH},setsar=1[fg];[bg][fg]overlay=0:{BY0}[b0];[b0][1:v]overlay[b1]")
    last='b1'
    for j,(t0,t1,s,b1,b2) in enumerate(caps):
        cap(ci,s,b1,b2); inputs+=['-i',f'{R}/cap{ci}.png']; n=2+j
        fc+=f";[{last}][{n}:v]overlay=enable='between(t,{t0},{t1})'[c{j}]"; last=f'c{j}'; ci+=1
    out=f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc+f";[{last}]setsar=1[vo]",'-map','[vo]','-map','0:a?','-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','2','-b:a','160k',out],check=True)
    segs.append(out)
open(f'{R}/list.txt','w').write(''.join(f"file '{s}'\n" for s in segs))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{R}/list.txt','-af','loudnorm=I=-16:TP=-1.5','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',f'{R}/reel.mp4'],check=True)
print('done')
