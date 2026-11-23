"""20261123-harari 릴스(띠형): 하라리×술레이만 대담 클립(원 영상 72초) — 받아쓰기(faster-whisper small) 기반 번역 자막. 저장소 루트에서 실행."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
R='media/20261123-harari/cand'; SRC='media/20261123-harari/video/v1.mp4'
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
    f=ImageFont.truetype(FX,34); tag='『사피엔스』 유발 하라리'; tw=d.textlength(tag,font=f)
    d.rounded_rectangle((70,310,70+tw+36,362),radius=8,fill=Y); d.text((88,336),tag,font=f,fill=(0,0,0),anchor='lm')
    L=['AI 시대 인간은','결국 소·닭 신세','이해도 못 한 채 지배당한다']
    for i,l in enumerate(L): d.text((70,433+i*88),l,font=fit(d,l,FB,78,940),fill=Y if i==2 else (255,255,255),anchor='ls')
    im.save(f'{R}/top.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,1450),small,font=fit(d,small,FM,38,940),fill=(225,225,225),anchor='ls')
    d.text((70,1540),b1,font=fit(d,b1,FB,68,940),fill=(255,255,255),anchor='ls'); d.text((70,1625),b2,font=fit(d,b2,FB,68,940),fill=Y,anchor='ls')
    im.save(f'{R}/cap{i}.png')
top()
SM='하라리 × 마이크로소프트 AI CEO 술레이만 대담'
CROP='1080:720:100:0'
S=[ # ss, dur, captions (scene-relative)
 (4.4,22.4,[(0,6.3,SM,'제가 가장 두려운 건','어떤 특정한 시나리오가 아니에요'),
            (6.3,9.9,SM,'AI가 바이러스를 만들거나','살인 로봇이 나타나는 게 아니라'),
            (9.9,17.0,SM,'5년, 10년, 20년 뒤','모든 인간이 아무것도 모르게 되는 것'),
            (17.0,22.4,SM,'무슨 일이 벌어지는지 모른 채','현실이 그냥 무너지는 거예요')]),
 (38.6,15.3,[(0,5.2,SM,'금융도, 정치도, 과학도','우리는 이해하지 못하게 돼요'),
            (5.2,9.2,SM,'구름도 나무도 고양이도','여전히 그대로 있겠지만'),
            (9.2,15.3,SM,'세상을 움직이는 시스템은','우리 이해를 한참 넘어설 거예요')]),
 (54.4,15.4,[(0,5.2,'하라리의 비유','다른 동물들을 생각해 보세요','소, 닭, 말'),
            (5.2,9.0,'하라리의 비유','그들은 존재하는지도 모르는','시스템에 지배당해요'),
            (9.0,15.4,'하라리의 비유','금융 시스템과 시장이','수십억 마리 소와 닭의 삶을 좌우하죠')]),
]
segs=[]; ci=0
for k,(ss,dur,caps) in enumerate(S):
    inputs=['-ss',str(ss),'-t',str(dur),'-i',SRC,'-i',f'{R}/top.png']
    fc=(f"[0:v]crop={CROP},scale=1080:{BH},setsar=1,pad=1080:1920:0:{BY0}:black[b0];[b0][1:v]overlay[b1]")
    last='b1'
    for j,(t0,t1,s,b1,b2) in enumerate(caps):
        cap(ci,s,b1,b2); inputs+=['-i',f'{R}/cap{ci}.png']; n=2+j
        fc+=f";[{last}][{n}:v]overlay=enable='between(t,{t0},{t1})'[c{j}]"; last=f'c{j}'; ci+=1
    out=f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc+f";[{last}]setsar=1[vo]",'-map','[vo]','-map','0:a','-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','2','-b:a','160k',out],check=True)
    segs.append(out)
open(f'{R}/list.txt','w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{R}/list.txt','-af','loudnorm=I=-16:TP=-1.5','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart','media/20261123-harari/reel.mp4'],check=True)
# 커버: 검정 배경 + 띠(y=330) + 아래 제목(reel_overlay 양식)
fr=f'{R}/cover_frame.jpg'; subprocess.run(['ffmpeg','-v','error','-y','-ss','12','-i',SRC,'-frames:v','1',fr],check=True)
im=Image.open(fr).convert('RGB'); im=im.crop((100,0,1180,720)).resize((1080,720))
cv=Image.new('RGB',(1080,1920),(0,0,0)); cv.paste(im,(0,330)); cv.save(f'{R}/cover_bg.jpg',quality=95)
subprocess.run(['python3','scripts/reel_overlay.py',f'{R}/overlay.png','하라리 경고\n인간은 결국\n소·닭 신세 된다'],check=True)
ov=Image.open(f'{R}/overlay.png'); c=cv.convert('RGBA'); c.alpha_composite(ov); c.convert('RGB').save('media/20261123-harari/reel_cover.jpg',quality=94)
print('done')
