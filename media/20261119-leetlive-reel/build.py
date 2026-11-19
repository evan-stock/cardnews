"""리트냥이 노쇼 생중계 현장, 노형석 리트강사 발언 릴스(2026.11.19). 저장소 루트에서 실행.
원본: 사용자 화면녹화 2개(IDA입시연구소 유튜브 생중계, 08:50·08:53). 대사는 transcribe(faster-whisper medium, ko) 받아쓰기로 확인.
알림 배너·재생바·제어센터 구간은 쓰지 않고, 시청자 수 표시는 크롭으로 잘라냄. 틀: media/20261118-leetcam-reel/build.py."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D='media/20261119-leetlive-reel'; R=f'{D}/work'
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
TAG='11.19 · 리트냥이 노쇼 생중계 현장'; L=['리트냥이 위해','룰루레몬 속옷까지 산','리트강사의 눈물']
def top():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); h=46; lg=lg.resize((int(lg.width*h/lg.height),h)); im.alpha_composite(lg,(70,238))
    f=ImageFont.truetype(FX,34); tw=d.textlength(TAG,font=f)
    d.rounded_rectangle((70,310,70+tw+36,362),radius=8,fill=Y); d.text((88,336),TAG,font=f,fill=(0,0,0),anchor='lm')
    f=ImageFont.truetype(FB,78)
    for l in L: assert d.textlength(l,font=f)<=950,l
    for i,l in enumerate(L): d.text((70,433+i*88),l,font=f,fill=Y if i==len(L)-1 else (255,255,255),anchor='ls')
    im.save(f'{R}/top.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,1450),small,font=ImageFont.truetype(FM,38),fill=(225,225,225),anchor='ls')
    f=ImageFont.truetype(FB,68)
    for t in (b1,b2): assert d.textlength(t,font=f)<=950,t
    d.text((70,1540),b1,font=f,fill=(255,255,255),anchor='ls'); d.text((70,1625),b2,font=f,fill=Y,anchor='ls')
    im.save(f'{R}/cap{i}.png')
top()
CR='1809:1206:361:0'
N='노형석 리트강사(메가로스쿨)'
S=[ # src(잘라둔 조각), ss(조각 기준), dur, caps
 (f'{R}/v2a.mp4',1.5,19.5,[(0,4.8,'검증용 옷을 직접 사 왔다는 리트강사','"옷도 되게 좋은 거 샀어요','편안하게 풀라고"'),
                           (4.8,8.1,N,'"옷도 되게 좋은 거 샀어요','편안하게 풀라고"'),
                           (8.1,17.0,N,'"속옷도, 저는 못 사 입는','룰루레몬 4만 원짜리"'),
                           (17.0,19.5,N,'"와서 아무것도 불편한 거 없이','편안하게 하라고"')]),
 (f'{R}/v1a.mp4',2.7,28.8,[(0,6.4,'그런데 리트냥이는 오지 않았다','"제가 하는 일이','너무 우롱당하는 느낌"'),
                           (6.4,17.0,N,'"그 사람이 대단한 천재라면','천재가 내 일을 우롱하는 느낌"'),
                           (17.0,24.2,N,'"거짓말이라면','거짓말쟁이가 우롱하는 느낌"'),
                           (24.2,28.8,N,'"이러나 저러나','되게 속상하더라고요"')]),
 (f'{R}/v1b.mp4',2.4,7.5,[(0,7.5,'이번 주 수업 중에도','"학생들 앞에서도','감정이 격해져서"')]),
]
segs=[]; ci=0
for k,(src,ss,dur,caps) in enumerate(S):
    inputs=['-ss',str(ss),'-t',str(dur),'-i',src,'-i',f'{R}/top.png']
    fc=(f"[0:v]crop={CR},scale=1080:{BH},setsar=1,pad=1080:1920:0:{BY0}:black,fps=30[b0];[b0][1:v]overlay[b1]")
    last='b1'
    for j,(t0,t1,s,b1,b2) in enumerate(caps):
        cap(ci,s,b1,b2); inputs+=['-i',f'{R}/cap{ci}.png']; n=2+j
        fc+=f";[{last}][{n}:v]overlay=enable='between(t,{t0},{t1})'[c{j}]"; last=f'c{j}'; ci+=1
    out=f'{R}/s{k}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc+f";[{last}]setsar=1[vo];[0:a]afade=t=in:d=0.08,afade=t=out:st={dur-0.12}:d=0.12[ao]",
        '-map','[vo]','-map','[ao]','-t',str(dur),'-r','30','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','2','-b:a','160k',out],check=True)
    segs.append(os.path.abspath(out))
open(f'{R}/list.txt','w').write(''.join(f"file '{s}'\n" for s in segs))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{R}/list.txt','-af','loudnorm=I=-16:TP=-1.5','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',f'{D}/reel.mp4'],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-ss','10.5','-i',f'{R}/v2a.mp4','-frames:v','1','-vf',f'crop={CR},scale=1080:{BH}',f'{R}/cov_band.jpg'],check=True)
bg=Image.new('RGB',(1080,1920),(0,0,0)); bg.paste(Image.open(f'{R}/cov_band.jpg'),(0,330)); bg.save(f'{R}/cov_bg.jpg',quality=95)
subprocess.run(['python3','scripts/reel_overlay.py',f'{D}/cand/overlay.png',"\n".join(L),'',f'{R}/cov_bg.jpg',f'{D}/reel_cover.jpg'],check=True)
print('done')
