import subprocess, os
from PIL import Image, ImageDraw, ImageFont
os.chdir('/home/claude/cardnews'); R='/home/claude/reel3'; M='media'
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
def top():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); h=46; lg=lg.resize((int(lg.width*h/lg.height),h)); im.alpha_composite(lg,(70,150))
    f=ImageFont.truetype(FX,34); tag='폴란드 헌재 사태'; tw=d.textlength(tag,font=f)
    d.rounded_rectangle((70,222,70+tw+36,274),radius=8,fill=Y); d.text((88,248),tag,font=f,fill=(0,0,0),anchor='lm')
    f=ImageFont.truetype(FB,78); L=['좌파 친EU 총리','헌재 점거 시도','대통령 급히 귀국','쿠데타 저지 출동']
    for i,l in enumerate(L): d.text((70,345+i*88),l,font=f,fill=Y if i==3 else (255,255,255),anchor='ls')
    im.save(f'{R}/top.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,1450),small,font=ImageFont.truetype(FM,38),fill=(225,225,225),anchor='ls')
    f=ImageFont.truetype(FB,68)
    d.text((70,1540),b1,font=f,fill=(255,255,255),anchor='ls'); d.text((70,1625),b2,font=f,fill=Y,anchor='ls')
    im.save(f'{R}/cap{i}.png')
top()
S=[ # src, ss, dur, crop(w:h:x:y) for band (3:2), caption list [(t0,t1,small,b1,b2)]
 (f'{M}/20261031-polandcourt-reel3/video/v1.mp4',2,3,'930:620:520:150',[(0,3,'10월 30일 밤 · 폴란드 바르샤바','헌법재판소 앞,','진압 경찰과 정면 충돌')]),
 (f'{M}/20261031-polandcourt-reel2/video/v3.mp4',8,3.5,'1000:667:800:135',[(0,3.5,'헌재 철문 앞','쇠사슬 감은 문,','그라인더로 끊었다')]),
 (f'{M}/20261031-polandcourt-reel3/video/v2.mp4',4,3,'1620:1080:150:0',[(0,3,'밤새 이어진 시위','헌재 앞을 가득 메운','폴란드 국기')]),
 (f'{M}/20261031-polandcourt-reel2/video/v2.mp4',3,3,'720:480:0:500',[(0,3,'대통령 도착 직후','경찰 저지선 앞','일촉즉발 대치')]),
 (f'{M}/20261031-polandcourt-reel2/video/v1.mp4',12,12,'464:309:0:110',[(0,5,'31일 새벽 1시','급히 귀국한 대통령,','헌재 안으로 직접 진입'),(5,12,'정부 쪽 재판관들을 향해','대통령 "여러분은','재판관이 아닙니다"')]),
]
segs=[]; ci=0
for k,(src,ss,dur,crop,caps) in enumerate(S):
    inputs=['-ss',str(ss),'-t',str(dur),'-i',src,'-i',f'{R}/top.png']; fc=(f"[0:v]split[s1][s2];[s1]crop={crop},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.28[bg];"
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
