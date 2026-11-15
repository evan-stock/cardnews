# 유조선(20261115-nola-reel2) 양식: 아래 고정 제목 2줄 + 위 장면별 자막(작은 줄 + 굵은 2줄, 둘째 줄 노랑)
import subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
os.chdir('/home/claude/cardnews'); sys.path.insert(0,'scripts')
from reel_overlay import overlay
ID='20261115-shipcatch-reel'; R='/home/claude/work/ship'; os.makedirs(R,exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; Y=(255,216,77)
SRC='media/20261115-shipcatch4k/video/v1.mp4'   # SpaceX X 원본 4K (x.com/SpaceX/status/2121715216597827756)
SS,DUR=55,31
CROP="crop=1020:1814:1958-510:0,scale=1080:1920:flags=lanczos,setsar=1"  # 아래 SpaceX 시간 표시 잘라냄
TITLE=['SpaceX 우주선','본체 회수 성공']
ov=overlay(TITLE); ov.save(f'{R}/title.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    for y in range(0,560): d.line([(0,y),(1080,y)],fill=(0,0,0,int(170*max(0,1-y/560))))
    sh=Image.new('RGBA',(1080,1920),(0,0,0,0)); ds=ImageDraw.Draw(sh)
    fm=ImageFont.truetype(FM,40); fb=ImageFont.truetype(FB,64)
    items=[]
    if small: items.append((70,250,small,fm,(230,230,230)))
    items+=[(70,340,b1,fb,(255,255,255)),(70,424,b2,fb,Y)]
    for x,y,t,f,c in items: ds.text((x+3,y+3),t,font=f,fill=(0,0,0,200),anchor='ls')
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    for x,y,t,f,c in items:
        assert d.textlength(t,font=f)<=940,t
        d.text((x,y),t,font=f,fill=c,anchor='ls')
    im.save(f'{R}/cap{i}.png')
CAPS=[(0,3.02,'11월 14일 · 미국 텍사스 스타베이스','지구 14바퀴 돌고','돌아온 우주선'),
      (3.02,7.0,'22시간 만의 귀환','길이 52m 스타십이','엔진 켜고 몸을 세운다'),
      (7.0,10.87,'바다 대신 발사탑으로','그대로 발사탑 옆에','정확히 내려앉는다'),
      (10.87,15.77,'발사탑 카메라 영상','거대한 로봇 팔 두 개가','공중에서 붙잡았다'),
      (15.77,23.0,'SpaceX 공식 영상','우주선 본체 회수는','이번이 처음'),
      (23.0,DUR,'하루 전 발사 직후','같이 잡으려던 부스터는','회수 취소 후 폭발')]
inputs=['-ss',str(SS),'-t',str(DUR),'-i',SRC,'-i',f'{R}/title.png']
fc=f"[0:v]setpts=PTS-STARTPTS,{CROP}[b0];[b0][1:v]overlay[b1]"; last='b1'
for j,(t0,t1,s,b1,b2) in enumerate(CAPS):
    cap(j,s,b1,b2); inputs+=['-i',f'{R}/cap{j}.png']
    fc+=f";[{last}][{2+j}:v]overlay=enable='between(t,{t0},{t1-0.001})'[c{j}]"; last=f'c{j}'
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc+f";[{last}]fps=30,format=yuv420p[vo]",'-map','[vo]','-map','0:a','-af','loudnorm=I=-16:TP=-1.5','-c:v','libx264','-preset','veryfast','-crf','18','-c:a','aac','-ar','44100','-b:a','160k','-movflags','+faststart',f'media/{ID}/reel.mp4'],check=True)
# 커버: 엔진 켜고 발사탑 옆에 내려오는 장면 + 같은 제목
subprocess.run(['ffmpeg','-v','error','-y','-ss','64','-i',SRC,'-frames:v','1','-vf',CROP,f'{R}/cbg.png'],check=True)
bg=Image.open(f'{R}/cbg.png').convert('RGBA')
Image.alpha_composite(bg,ov).convert('RGB').save(f'media/{ID}/reel_cover.jpg',quality=93)
print('done')
