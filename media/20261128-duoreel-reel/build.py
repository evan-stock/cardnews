"""아이폰 듀오 라이브 파손 띠형 릴스. 저장소 루트에서: python3 media/20261128-duoreel-reel/build.py"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D='media/20261128-duoreel-reel'; W=f'{D}/cand'; os.makedirs(W,exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
SRC=f'{D}/video/v1.mp4'
CROP='1011:674:180:0'          # 왼쪽 후원자 닉네임 목록 잘라냄
BLUR=(700,30,300,115)           # 크롭 좌표계: 오른쪽 위 별풍선 집계 박스 흐림 (x,y,w,h)
TAG='아이폰 듀오 또 파손'
L=['라이브 방송 중','아이폰 듀오 펼치자',"화면이 '쫙'"]
CAPS=[(0,6.5,'11월 28일 · 개인방송 라이브 중','떨어뜨린 것도 아닌데','그냥 펼쳤을 뿐'),
      (6.5,11.5,'펼치자마자 접히는 자리에','화면 가운데','하얀 줄이 쫙'),
      (11.5,17.3,'애플 "일부 기기 안쪽 화면 문제 인지"','1,999달러 폴더블,','출시 한 달 만에 또')]
def top():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); h=46; lg=lg.resize((int(lg.width*h/lg.height),h)); im.alpha_composite(lg,(70,238))
    f=ImageFont.truetype(FX,34); tw=d.textlength(TAG,font=f)
    d.rounded_rectangle((70,310,70+tw+36,362),radius=8,fill=Y); d.text((88,336),TAG,font=f,fill=(0,0,0),anchor='lm')
    f=ImageFont.truetype(FB,78)
    for i,l in enumerate(L):
        x=70
        for k,part in enumerate(l.split("'")):   # '강조' 노랑
            col=Y if (k%2==1 or i==len(L)-1) else (255,255,255)
            d.text((x,433+i*88),part,font=f,fill=col,anchor='ls'); x+=d.textlength(part,font=f)
    im.save(f'{W}/top.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,1450),small,font=ImageFont.truetype(FM,38),fill=(225,225,225),anchor='ls')
    f=ImageFont.truetype(FB,68); d.text((70,1540),b1,font=f,fill=(255,255,255),anchor='ls'); d.text((70,1625),b2,font=f,fill=Y,anchor='ls')
    im.save(f'{W}/cap{i}.png')
top()
inputs=['-i',SRC,'-i',f'{W}/top.png']
bx,by,bw,bh=BLUR
fc=(f"[0:v]setpts=PTS-STARTPTS,crop={CROP},delogo=x={bx}:y={by}:w={bw}:h={bh}[cl];"
    f"[cl]scale=1080:{BH},setsar=1,pad=1080:1920:0:{BY0}:black[b0];[b0][1:v]overlay[l0]")
last='l0'
for j,(t0,t1,s,b1,b2) in enumerate(CAPS):
    cap(j,s,b1,b2); inputs+=['-i',f'{W}/cap{j}.png']
    fc+=f";[{last}][{2+j}:v]overlay=enable='between(t,{t0},{t1})'[c{j}]"; last=f'c{j}'
fc+=f";[{last}]format=yuv420p[vo];[0:a]asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5,aresample=48000[ao]"
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc,'-map','[vo]','-map','[ao]','-r','30','-c:v','libx264','-preset','medium','-crf','19',
  '-c:a','aac','-ar','48000','-ac','2','-b:a','160k','-use_editlist','0','-movflags','+faststart',f'{D}/reel.mp4'],check=True)
# 커버: 검정 바탕 + 띠(y=330)에 깨진 화면 프레임 + 큰 제목(reel_overlay 양식)
subprocess.run(['ffmpeg','-v','error','-y','-ss','8.0','-i',SRC,'-frames:v','1','-vf',
  f"crop={CROP},delogo=x={bx}:y={by}:w={bw}:h={bh},scale=1080:{BH}",f'{W}/cover_frame.jpg'],check=True)
import sys; sys.path.insert(0,'scripts'); from reel_overlay import overlay
bg=Image.new('RGB',(1080,1920),(0,0,0)); bg.paste(Image.open(f'{W}/cover_frame.jpg'),(0,330))
ov=overlay(['펼치기만 했는데','화면이 쫙'])
out=Image.alpha_composite(bg.convert('RGBA'),ov).convert('RGB'); out.save(f'{W}/reel_cover_final.jpg',quality=93); out.save(f'{D}/reel_cover.jpg',quality=93)
print('done')
