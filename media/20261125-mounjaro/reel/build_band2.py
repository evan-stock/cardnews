"""20261125-mounjaro 릴스(띠형, 오쓸 양식): 대마도 야마토운수 줄 영상 + 기사 캡처. 저장소 루트에서 실행."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageOps
D='media/20261125-mounjaro'; R=f'{D}/reel'; SRC=f'{D}/video/v1.mp4'
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
def fit(d,t,path,size,maxw):
    while size>40:
        f=ImageFont.truetype(path,size)
        if d.textlength(t,font=f)<=maxw: return f
        size-=2
    return ImageFont.truetype(path,size)
def top():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); h=46; lg=lg.resize((int(lg.width*h/lg.height),h)); im.alpha_composite(lg,(70,238))
    f=ImageFont.truetype(FX,34); tag='비만치료제 원정 구매'; tw=d.textlength(tag,font=f)
    d.rounded_rectangle((70,310,70+tw+36,362),radius=8,fill=Y); d.text((88,336),tag,font=f,fill=(0,0,0),anchor='lm')
    L=['마운자로 반값에 사려고','대마도로','원정 간 한국인들']
    for i,l in enumerate(L): d.text((70,433+i*88),l,font=fit(d,l,FB,78,940),fill=Y if i==2 else (255,255,255),anchor='ls')
    im.save(f'{R}/top.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,1450),small,font=fit(d,small,FM,38,940),fill=(225,225,225),anchor='ls')
    d.text((70,1540),b1,font=fit(d,b1,FB,68,940),fill=(255,255,255),anchor='ls'); d.text((70,1625),b2,font=fit(d,b2,FB,68,940),fill=Y,anchor='ls')
    im.save(f'{R}/cap{i}.png')
def band_img(src,out,photo=False):
    cv=Image.new('RGB',(1080,1920),(0,0,0))
    if photo: cv.paste(ImageOps.fit(Image.open(src).convert('RGB'),(1080,BH),Image.LANCZOS,centering=(0.5,0.4)),(0,BY0))
    else:
        c=Image.open(src).convert('RGB'); cw=1000; ch=round(c.height*cw/c.width)
        if ch>BH-30: cw,ch=round(c.width*(BH-30)/c.height),BH-30
        c=c.resize((cw,ch),Image.LANCZOS); m=Image.new('L',c.size,0); ImageDraw.Draw(m).rounded_rectangle((0,0,*c.size),22,fill=255)
        cv.paste(c,((1080-cw)//2,BY0+(BH-ch)//2),m)
    cv.save(out,quality=95)
top()
S=[('video',6.6,('대마도 야마토운수 영업소 앞 · 11월 24일','마운자로 받으려고','1시간 줄 섰다')),
   (f'{D}/cand/a_fn.png',3.6,('11월 12일부터 해외 처방약 3개월분 반입 허용','한국 4주분 30만원 넘는데','일본은 절반 이하')),
   (f'{D}/cand/a_in1.png',3.6,('당일치기 다녀온 유튜버 계산','약 12개 + 왕복 배','총 34만원')),
   (f'{D}/cand/a_in2.png',3.6,('줄이 너무 길어서','택배 받고 뛰었는데','귀국 배 놓쳤다')),
   (f'{D}/cand/q5.png',3.8,('주의','현지 약국에선 못 산다','일본 병원 처방 필수'))]
segs=[]
for k,(src,dur,(s,b1,b2)) in enumerate(S):
    cap(k,s,b1,b2)
    if src=='video':
        inputs=['-t',str(dur),'-i',SRC,'-i',f'{R}/top.png','-i',f'{R}/cap{k}.png']
        fc=f"[0:v]scale=1080:-2,crop=1080:{BH}:0:(ih-{BH})*0.42,setsar=1,pad=1080:1920:0:{BY0}:black[b0];[b0][1:v]overlay[b1];[b1][2:v]overlay,setsar=1[vo]"
        amap=['-map','0:a']
    else:
        bi=f'{R}/bg{k}.jpg'; band_img(src,bi,photo=src.endswith('q5.png'))
        inputs=['-loop','1','-t',str(dur),'-i',bi,'-i',f'{R}/top.png','-i',f'{R}/cap{k}.png','-f','lavfi','-t',str(dur),'-i','anullsrc=r=44100:cl=stereo']
        fc="[0:v][1:v]overlay[b1];[b1][2:v]overlay,setsar=1[vo]"; amap=['-map','3:a']
    out=f'{R}/seg{k}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc,'-map','[vo]',*amap,'-t',str(dur),'-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','2','-b:a','160k',out],check=True)
    segs.append(out)
open(f'{R}/list.txt','w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{R}/list.txt','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',f'{D}/reel.mp4'],check=True)
# 커버: 검정 + 띠(y=330) + reel_overlay 큰 제목
cv=Image.new('RGB',(1080,1920),(0,0,0)); cv.paste(ImageOps.fit(Image.open(f'{D}/cand/q3.png').convert('RGB'),(1080,720),Image.LANCZOS,centering=(0.5,0.4)),(0,330)); cv.save(f'{R}/cover_bg.jpg',quality=95)
subprocess.run(['python3','scripts/reel_overlay.py',f'{R}/overlay.png','마운자로 반값에\n대마도 원정 간\n한국인들 근황'],check=True)
c=cv.convert('RGBA'); c.alpha_composite(Image.open(f'{R}/overlay.png')); c.convert('RGB').save(f'{D}/reel_cover.jpg',quality=94)
print('done')
