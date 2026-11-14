import subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
os.chdir('/home/claude/cardnews'); sys.path.insert(0,'scripts')
from reel_overlay import overlay
R='/home/claude/work/n2'; os.makedirs(R,exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; Y=(255,216,77)
V='media/20261115-xpair/video/'
TITLE=['13일 금요일','유람선 덮친 유조선']
ov=overlay(TITLE); ov.save(f'{R}/title.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    for y in range(0,560): d.line([(0,y),(1080,y)],fill=(0,0,0,int(170*max(0,1-y/560))))
    sh=Image.new('RGBA',(1080,1920),(0,0,0,0)); ds=ImageDraw.Draw(sh)
    fm=ImageFont.truetype(FM,40); fb=ImageFont.truetype(FB,64)
    items=[]
    if small: items.append((70,250,small,fm,(230,230,230)))
    items+= [(70,340,b1,fb,(255,255,255)),(70,424,b2,fb,Y)]
    for x,y,t,f,c in items: ds.text((x+3,y+3),t,font=f,fill=(0,0,0,200),anchor='ls')
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    for x,y,t,f,c in items: d.text((x,y),t,font=f,fill=c,anchor='ls')
    im.save(f'{R}/cap{i}.png')
# src, ss, dur, captions[(t0,t1,small,b1,b2)]
V2='media/20261115-nola2/video/'
S=[(V2+'v1.mp4',4.3,8.2,[(0,4.0,'11월 13일 · 미국 뉴올리언스','유람선이 뒤집혀','강물에 빠진 승객'),(4.0,8.2,'구명조끼 입고 직접 찍은 영상','바로 뒤엔','유람선을 덮친 유조선')]),
   (V2+'v1.mp4',0.0,4.3,[(0,4.3,'같은 승객 영상 앞부분','유람선 바로 옆까지','밀고 들어온 유조선')]),
   (V+'v2.mp4',3.5,5.5,[(0,5.5,'부두에서 찍힌 충돌 직후','승객 129명 태운 유람선,','그대로 옆으로 넘어갔다')]),
   (V+'v2.mp4',46.5,6.5,[(0,3.2,'구명조끼 입고 떠 있는 사람들','결과는?','32명 병원 이송'),(3.2,6.5,'루이지애나 주지사','탑승자 전원 구조,','"미시시피의 기적"')])]
segs=[]; ci=0
for k,(src,ss,dur,caps) in enumerate(S):
    inputs=['-ss',str(ss),'-t',str(dur),'-i',src,'-i',f'{R}/title.png']
    fc="[0:v]setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"+""+"[b0];[b0][1:v]overlay[b1]"; last='b1'
    for j,(t0,t1,s,b1,b2) in enumerate(caps):
        cap(ci,s,b1,b2); inputs+=['-i',f'{R}/cap{ci}.png']
        fc+=f";[{last}][{2+j}:v]overlay=enable='between(t,{t0},{t1-0.001})'[c{j}]"; last=f'c{j}'; ci+=1
    out=f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc+f";[{last}]setsar=1,fps=30[vo]",'-map','[vo]','-map','0:a','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','2','-b:a','160k',out],check=True)
    segs.append(out)
open(f'{R}/list.txt','w').write(''.join(f"file '{s}'\n" for s in segs))
os.makedirs('media/20261115-nola-reel2',exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{R}/list.txt','-af','loudnorm=I=-16:TP=-1.5','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart','media/20261115-nola-reel2/reel.mp4'],check=True)
# cover: frame of v1 at ~9s (ship close)
subprocess.run(['ffmpeg','-v','error','-y','-ss','10.3','-i',V2+'v1.mp4','-frames:v','1',f'{R}/cbg.png'],check=True)
bg=Image.open(f'{R}/cbg.png').convert('RGB'); r=max(1080/bg.width,1920/bg.height); bg=bg.resize((int(bg.width*r),int(bg.height*r)),Image.LANCZOS)
bg=bg.crop(((bg.width-1080)//2,0,(bg.width-1080)//2+1080,1920)).convert('RGBA')
Image.alpha_composite(bg,ov).convert('RGB').save('media/20261115-nola-reel2/reel_cover.jpg',quality=93)
print('done')
