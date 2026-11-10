"""정보 제공형 수정본(사용자 11.10 15:34 "정보 제공형으로"). 트럼프 '젠슨 믿는다' 띠형 릴스 (2026.11.10). 저장소 루트에서: python3 media/20261110-trumpjensen-reel/build.py
원본: 백악관 공식 중계(엑스 @amitisinvesting 게시, media/20261110-x2/video/v2.mp4), 사진: 11.09 jensenspy 후보(press06 topstarnews, press04 fnnews).
대사: transcribe 워크플로(faster-whisper small) 받아쓰기 → v2.srt"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D='media/20261110-trumpjensen-reel2'; W=f'{D}/work'; os.makedirs(W,exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
SRC='media/20261110-x2/video/v2.mp4'; SS=1.8; END=36.6; HOLD=2.6
def fit(d,t,f,maxw=940):
    s=f.size
    while d.textlength(t,font=f)>maxw: s-=2; f=ImageFont.truetype(f.path,s)
    return f
def top():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); h=46; lg=lg.resize((int(lg.width*h/lg.height),h)); im.alpha_composite(lg,(70,238))
    f=ImageFont.truetype(FX,34); tag='젠슨 황 스캔들'; tw=d.textlength(tag,font=f)
    d.rounded_rectangle((70,310,70+tw+36,362),radius=8,fill=Y); d.text((88,336),tag,font=f,fill=(0,0,0),anchor='lm')
    L=['트럼프 "젠슨과 통화했다"','"스파이인 줄 몰랐대"',"'나는 정말 믿는다'"]
    for i,l in enumerate(L): d.text((70,433+i*88),l,font=fit(d,l,ImageFont.truetype(FB,78)),fill=Y if i==2 else (255,255,255),anchor='ls')
    im.save(f'{W}/top.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,1450),small,font=fit(d,small,ImageFont.truetype(FM,38)),fill=(225,225,225),anchor='ls')
    d.text((70,1540),b1,font=fit(d,b1,ImageFont.truetype(FB,68)),fill=(255,255,255),anchor='ls')
    d.text((70,1625),b2,font=fit(d,b2,ImageFont.truetype(FB,68)),fill=Y,anchor='ls')
    im.save(f'{W}/cap{i}.png'); return f'{W}/cap{i}.png'
def photo(src,out,box=None):
    im=Image.open(src).convert('RGB')
    if box: im=im.crop(box)
    r=max(1080/im.width,720/im.height); im=im.resize((round(im.width*r),round(im.height*r)),Image.LANCZOS)
    x=(im.width-1080)//2; y=(im.height-720)//2; im.crop((x,y,x+1080,y+720)).save(out,quality=95); return out
top()
P1=photo('media/20261109-jensenspy/cand/press06.jpg',f'{W}/p1.jpg')   # 2024 타이베이 술자리 젠슨 황·앨리스 황
P2=photo('media/20261109-jensenspy/cand/press04.jpg',f'{W}/p2.jpg')   # 젠슨 황·트럼프
T=END-SS
# (시작,끝,작은줄,굵은1,굵은2) — 시간은 SS 기준. 대사는 v2.srt 그대로 번역
C=[(0,7.4,'11월 9일(현지) · 백악관 기자회견','기자 "5월 중국 갈 때','스파이 의혹 알았나요?"'),
   (7.4,9.3,'트럼프 대통령','트럼프 "아니,','그땐 못 들었다"'),
   (9.3,14.2,'사진: 2024년 타이베이, 젠슨 황과 앨리스 황','"많은 사람이 들었지만','젠슨은 완전히 부인한다"'),
   (14.2,18.2,'트럼프 대통령','"오늘 물어봤다. 오늘 통화했거든,','괜찮은지 보려고"'),
   (18.2,19.1,'트럼프 대통령','"어떻게 지내냐고 묻고,',''),
   (19.1,21.3,'트럼프 대통령','"그 얘기도','물어봤다"'),
   (21.3,27.9,'트럼프 대통령','"그 사람이 스파이인 줄','전혀 몰랐다고 하더라"'),
   (27.9,30.9,'트럼프 대통령','"내가 직접 물었다,','\'스파이인 줄 알았냐\'고"'),
   (30.9,33.2,'트럼프 대통령','"그 여자가 스파이인 줄','전혀 몰랐다고 하더라"'),
   (33.2,T,'트럼프 대통령','"그리고 나는','정말 그를 믿는다"'),
   (T,T+HOLD,'앞으로 남은 일','FBI는 조사 중,','하원은 18일 출석 요청')]
PH=[(P1,9.3,14.5),(P2,14.1,17.6)]
inputs=['-ss',str(SS),'-t',str(T),'-i',SRC,'-i',f'{W}/top.png']
fc=(f"[0:v]crop=1575:1050:385:20,scale=1080:{BH},setsar=1,tpad=stop_mode=clone:stop_duration={HOLD}[fg];"
    f"color=black:s=1080x1920:r=30:d={T+HOLD}[bg];[bg][fg]overlay=0:{BY0}:shortest=1[v0]")
n=2; last='v0'
FD=0.4  # 자료화면 들어오고 나갈 때 페이드 + 천천히 확대(켄 번스)
for k,(p,t0,t1) in enumerate(PH):
    d=t1-t0; nf=int(d*30)
    zx='iw/2-(iw/zoom/2)'; zy='ih/2-(ih/zoom/2)'
    z=f"1+0.10*on/{nf}" if k%2==0 else f"1.10-0.10*on/{nf}"
    inputs+=['-loop','1','-framerate','30','-t',str(d),'-i',p]
    fc+=(f";[{n}:v]scale=2160:1440,zoompan=z='{z}':x='{zx}':y='{zy}':d=1:s=1080x720:fps=30,format=rgba,"
         f"fade=in:st=0:d={FD}:alpha=1,fade=out:st={d-FD}:d={FD}:alpha=1,setpts=PTS+{t0}/TB[pz{k}]"
         f";[{last}][pz{k}]overlay=0:{BY0}:eof_action=pass[ph{k}]"); last=f'ph{k}'; n+=1
fc+=f";[{last}][1:v]overlay[t0]"; last='t0'
for i,(t0,t1,s,b1,b2) in enumerate(C):
    inputs+=['-loop','1','-t',str(T+HOLD),'-i',cap(i,s,b1,b2)]; fc+=f";[{last}][{n}:v]overlay=enable='between(t,{t0},{t1-0.001})'[c{i}]"; last=f'c{i}'; n+=1
fc+=f";[{last}]format=yuv420p[vo];[0:a]apad=whole_dur={T+HOLD},loudnorm=I=-16:TP=-1.5[ao]"
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc,'-map','[vo]','-map','[ao]','-t',str(T+HOLD),'-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-c:a','aac','-ar','44100','-b:a','160k','-movflags','+faststart',f'{D}/reel.mp4'],check=True)
# 커버: 검정 배경 + 가로 띠(y=330) + reel_overlay 큰 제목
import sys; sys.path.insert(0,'scripts'); from reel_overlay import overlay
subprocess.run(['ffmpeg','-v','error','-y','-ss','34.5','-i',SRC,'-frames:v','1',f'{W}/f.png'],check=True)
cv=Image.new('RGB',(1080,1920),(0,0,0)); fr=Image.open(f'{W}/f.png').convert('RGB').crop((385,20,385+1575,20+1050)).resize((1080,720),Image.LANCZOS)
cv.paste(fr,(0,330)); cv=cv.convert('RGBA'); cv.alpha_composite(overlay(['트럼프 "젠슨,','스파이인 줄','몰랐다더라"']))
cv.convert('RGB').save(f'{D}/cover.jpg',quality=93)
print('done')
