"""트럼프, 젠슨 황 발언 모음 띠형 릴스(2026.11.16). 저장소 루트에서: python3 media/20261116-trumpjh-reel/build.py
scripts/landscape_reel/band_build.py 틀. 대사는 transcribe 워크플로(faster-whisper small) 단어 타임스탬프로 맞춤.
"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D='media/20261116-trumpjh-reel'; V=f'{D}/video'; R=f'{D}/work'; os.makedirs(R,exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
TAG='트럼프 순방 직전 발언'; L=['트럼프 "젠슨 복귀,','나쁘지 않아"','"김정은도 만날 수도"']
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
    d.text((70,1540),b1,font=f,fill=(255,255,255),anchor='ls'); d.text((70,1625),b2,font=f,fill=Y,anchor='ls')
    for t,y in ((b1,1540),(b2,1625)): assert d.textlength(t,font=f)<=950,t
    assert d.textlength(small,font=ImageFont.truetype(FM,38))<=950,small
    im.save(f'{R}/cap{i}.png')
top()
C4='1440:960:300:60'   # v4 정면 클로즈업(1920x1080)
C3='1260:840:600:80'
C2='1440:960:240:60'   # v2 순방 일정 발언
C5='delogo=x=374:y=636:w=160:h=114,delogo=x=540:y=696:w=296:h=50,crop=1290:860:330:60'  # v5 마린원 앞: 텔레그램 워터마크 지우고, 왼쪽 위 MAGNO 로고·아래 자막띠는 잘라냄   # v3: 왼쪽 위 젠슨 황 작은 사진(작성자 편집) 잘라냄
S=[ # src, ss, dur, crop, [(t0,t1,small,b1,b2)]
 (f'{V}/v4.mp4',2.5,14.4,C4,[(0,1.9,"루비오 장관이 '스파이' 경고했다는 보도에",'"누가 그래?','누가 그랬는데?"'),
                             (1.9,4.0,"루비오 장관이 '스파이' 경고했다는 보도에",'"그런 얘기','못 들었어"'),
                             (4.0,6.2,'젠슨 황과 만난 중국계 여성 앨리스 황','"그 여자가 스파이인지','난 모르겠어"'),
                             (6.2,10.7,'트럼프 대통령 · 16일 백악관','"보통 이 나라에 오는','중국 미녀는"'),
                             (10.7,14.4,'트럼프 대통령 · 16일 백악관','"다들 스파이라고','하더라고"')]),
 (f'{V}/v5.mp4',7.6,8.0,C5,[(0,4.5,'"젠슨 황이 중국 스파이와 불륜했다고 믿나?"','"스파이인지 전혀 몰라,','아무도 증명 못 했어"'),
                            (4.5,8.0,'출발 직전 마린원 앞에서','"사적으로 그런 일은','하지 말았어야겠지"')]),
 (f'{V}/v5.mp4',19.25,4.45,C5,[(0,4.45,'출발 직전 마린원 앞에서','"스파이라는 증거 없어,','스파이가 아닐 수도 있어"')]),
 (f'{V}/v3.mp4',1.6,3.3,C3,[(0,3.3,'12일 불륜 보도 뒤 CEO 사임한 젠슨 황 복귀론에','"복귀? 난','전혀 상관없어"')]),
 (f'{V}/v4.mp4',54.3,5.6,C4,[(0,5.6,"일론 머스크도 '젠슨은 대체 불가' 글에 동의",'"젠슨이 돌아와야 한다는데,','나쁜 생각 아니야"')]),
 (f'{V}/v2.mp4',20.35,7.4,C2,[(0,3.6,'같은 자리 · 18일 중국 APEC 앞두고 순방 출발','"시진핑에 이어','푸틴 대통령과도 만나고"'),
                              (3.6,7.4,'10월엔 김정은 회동에 "모르겠다"던 트럼프','"김정은도','만날 수도 있어"')]),
]
segs=[]; ci=0
for k,(src,ss,dur,crop,caps) in enumerate(S):
    inputs=['-ss',str(ss),'-t',str(dur),'-i',src,'-i',f'{R}/top.png']
    fc=(f"[0:v]{crop if '=' in crop else 'crop='+crop},scale=1080:{BH},setsar=1[fg];color=c=black:s=1080x1920:d={dur}:r=30[bg];"
        f"[bg][fg]overlay=0:{BY0}:shortest=1[b0];[b0][1:v]overlay[b1]")
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
# 커버: 검정 바탕 + 가운데 위 띠(가장 센 장면) + 아래 격자 통일형 큰 제목
subprocess.run(['ffmpeg','-v','error','-y','-ss','25.0','-i',f'{V}/v2.mp4','-frames:v','1','-vf',f'crop={C2},scale=1080:{BH}',f'{R}/cov_band.jpg'],check=True)
bg=Image.new('RGB',(1080,1920),(0,0,0)); bg.paste(Image.open(f'{R}/cov_band.jpg'),(0,330)); bg.save(f'{R}/cov_bg.jpg',quality=95)
subprocess.run(['python3','scripts/reel_overlay.py',f'{D}/cand/overlay.png','트럼프\n"김정은도\n만날 수도"','',f'{R}/cov_bg.jpg',f'{D}/reel_cover.jpg'],check=True)
print('done')
