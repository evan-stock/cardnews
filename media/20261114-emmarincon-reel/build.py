import subprocess, os, sys
sys.path.insert(0,'scripts/landscape_reel')
from PIL import Image, ImageDraw, ImageFont
R='/home/claude/work/r'; os.makedirs(R,exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
V='media/20261114-emmarincon/video/v1.mp4'; SS=6.0; DUR=35.2
def top():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); h=46; lg=lg.resize((int(lg.width*h/lg.height),h)); im.alpha_composite(lg,(70,238))
    f=ImageFont.truetype(FX,34); tag='루비오 미 국무장관'; tw=d.textlength(tag,font=f)
    d.rounded_rectangle((70,310,70+tw+36,362),radius=8,fill=Y); d.text((88,336),tag,font=f,fill=(0,0,0),anchor='lm')
    f=ImageFont.truetype(FB,78); L=['루비오가 본','김정은의','진짜 속마음']
    for i,l in enumerate(L): d.text((70,433+i*88),l,font=f,fill=Y if i==2 else (255,255,255),anchor='ls')
    im.save(f'{R}/top.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,1490),small,font=ImageFont.truetype(FM,38),fill=(200,200,200),anchor='ls')
    f=ImageFont.truetype(FB,64)
    d.text((70,1580),b1,font=f,fill=(255,255,255),anchor='ls'); d.text((70,1662),b2,font=f,fill=Y,anchor='ls')
    im.save(f'{R}/cap{i}.png')
# (원본초 시작,끝, 작은줄, 굵은1, 굵은2)
C=[(6.0,8.3,'이란 얘기를 하다가','"이란이 핵무기까지','가졌다고 생각해 보세요"'),
 (8.3,14.2,'루비오 국무장관 · 11월 13일 워싱턴 연설','"중동 전체를 인질로 잡고','미국까지 인질로 잡을 겁니다"'),
 (14.2,19.0,'그러다 북한 얘기로','"북한을 보세요. 북한은 그냥','좀... 그런 사람이 다스리죠"'),
 (19.0,21.8,'','(말끝을 흐리며','손을 휘휘 젓는 루비오)'),
 (21.8,26.0,'','"아니 아니, 제 말은','일본 정복엔 관심 없다는 거예요"'),
 (26.0,29.0,'','"그냥 자기 정권이','살아남길 바랄 뿐입니다"'),
 (29.0,33.0,'','"거기서 벌어진 끔찍한 일을','감싸는 건 아닙니다"'),
 (33.0,38.3,'','"팽창주의자가 아니에요. 일본이나','중국을 침공할 생각이 없죠"'),
 (38.3,41.2,'','"이 사람들(이란)은 팽창주의자,','혁명가들입니다"')]
top()
inputs=['-ss',str(SS),'-t',str(DUR),'-i',V,'-i',f'{R}/top.png']
crop='1500:1000:210:80'
fc=(f"[0:v]crop={crop},scale=1080:{BH},setsar=1[fg];color=black:s=1080x1920:r=30:d={DUR}[bg];[bg][fg]overlay=0:{BY0}:shortest=1[b0];[b0][1:v]overlay[b1]")
last='b1'
for j,(t0,t1,s,b1,b2) in enumerate(C):
    cap(j,s,b1,b2); inputs+=['-i',f'{R}/cap{j}.png']
    fc+=f";[{last}][{2+j}:v]overlay=enable='between(t,{t0-SS},{t1-SS-0.001})'[c{j}]"; last=f'c{j}'
out=sys.argv[1] if len(sys.argv)>1 else f'{R}/reel.mp4'
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc+f";[{last}]setsar=1[vo]",'-map','[vo]','-map','0:a','-r','30','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-af','loudnorm=I=-16:TP=-1.5','-c:a','aac','-ar','44100','-b:a','160k','-movflags','+faststart',out],check=True)
print('done')
