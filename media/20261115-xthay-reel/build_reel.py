"""머스크 외계인·거대한 필터 띠형 릴스 (JRE #1609, 2021.2.11). 저장소 루트에서 실행."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
ID='20261115-xthay-reel'; R=f'media/{ID}/work'; os.makedirs(R,exist_ok=True)
SRC='media/20261115-xthay/video/v1.mp4'
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720; CROP='1080:720:100:0'
TAG='조 로건 팟캐스트 · 2021'; L=['머스크가 말한','외계인이 안 오는','소름 돋는 이유']
def top():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); h=46; lg=lg.resize((int(lg.width*h/lg.height),h)); im.alpha_composite(lg,(70,238))
    f=ImageFont.truetype(FX,34); tw=d.textlength(TAG,font=f)
    d.rounded_rectangle((70,310,70+tw+36,362),radius=8,fill=Y); d.text((88,336),TAG,font=f,fill=(0,0,0),anchor='lm')
    f=ImageFont.truetype(FB,78)
    for i,l in enumerate(L): d.text((70,433+i*88),l,font=f,fill=Y if i==len(L)-1 else (255,255,255),anchor='ls')
    im.save(f'{R}/top.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,1450),small,font=ImageFont.truetype(FM,38),fill=(225,225,225),anchor='ls')
    f=ImageFont.truetype(FB,68)
    for t,yy,c in ((b1,1540,(255,255,255)),(b2,1625,Y)):
        if t:
            assert d.textlength(t,font=f)<=940, t
            d.text((70,yy),t,font=f,fill=c,anchor='ls')
    im.save(f'{R}/cap{i}.png')
M='일론 머스크'
# 장면: (시작, 끝, [(t0,t1,작은줄,굵은1,굵은2)])  t는 장면 안 상대 시각
S=[
 (170.7,172.0,[(0,1.3,M,'칼 세이건이 그랬지,','')]),
 (175.5,182.7,[(0,3.0,M,'외계인이 엄청 많든','아예 없든'),(3.0,7.2,M,'둘 다 똑같이','소름 끼친다고')]),
 (200.6,211.0,[(0,3.9,M+' · 외계인이 많다면','외계 문명은 우리를','벌레 떼로 볼 수도 있어'),
               (3.9,7.2,M,'"떠날 땐 멀쩡했는데','벌레가 득실대네?"'),
               (7.2,10.4,M,'"가서 싹 방역해"','우리가 집 소독하듯이')]),
 (214.9,221.2,[(0,2.3,M,'근데 외계인이','아예 없다면?'),(2.3,6.3,M,'모든 문명이 우주로 가기 전에','전부 망한 걸 수도')]),
 (22.2,26.9,[(0,4.7,'거대한 필터 = 문명을 걸러내는 관문 가설','그래서 진짜 중요한 건','')]),
 (27.9,31.7,[(0,3.8,'거대한 필터 = 문명을 걸러내는 관문 가설','"거대한 필터"를','넘느냐 마느냐야')]),
 (34.5,41.6,[(0,7.1,M+' · 화성 이주 얘기 중','지구발 우주선이 끊겨도','화성에서 버틸 수 있나')]),
 (63.7,72.0,[(0,4.7,M,'우주선이 끊기는 이유,','3차 세계대전일 수도'),(4.7,8.3,M,'아니면 문명이','서서히 무너지거나')]),
 (72.0,76.3,[(0,4.3,'지구 문명의 끝은',"한 방에 '쾅' 끝나든",'조용히 저물든')]),
]
top(); segs=[]; ci=0
for k,(a,b,caps) in enumerate(S):
    dur=round(b-a,2); inputs=['-ss',str(a),'-t',str(dur),'-i',SRC,'-i',f'{R}/top.png']
    fc=(f"color=c=black:s=1080x1920:r=30:d={dur}[bg];[0:v]crop={CROP},scale=1080:{BH},setsar=1[fg];"
        f"[bg][fg]overlay=0:{BY0}:shortest=1[b0];[b0][1:v]overlay[b1]")
    last='b1'
    for j,(t0,t1,s,b1,b2) in enumerate(caps):
        cap(ci,s,b1,b2); inputs+=['-i',f'{R}/cap{ci}.png']; n=2+j
        fc+=f";[{last}][{n}:v]overlay=enable='between(t,{t0},{t1})'[c{j}]"; last=f'c{j}'; ci+=1
    out=f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc+f";[{last}]setsar=1[vo];[0:a]afade=t=in:d=0.04,afade=t=out:st={dur-0.06}:d=0.06[ao]",
        '-map','[vo]','-map','[ao]','-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','2','-b:a','160k',out],check=True)
    segs.append(os.path.abspath(out))
open(f'{R}/list.txt','w').write(''.join(f"file '{s}'\n" for s in segs))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{R}/list.txt','-af','loudnorm=I=-16:TP=-1.5','-c:v','libx264','-preset','veryfast','-crf','20','-c:a','aac','-b:a','160k','-movflags','+faststart',f'media/{ID}/reel.mp4'],check=True)
print('done')
