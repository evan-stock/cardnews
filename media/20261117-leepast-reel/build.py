"""리트 만점자 과거 인터뷰 발언 모음 띠형 릴스(2026.11.17). 저장소 루트에서: python3 media/20261117-leepast-reel/build.py
소스: 지금백지연 공개분(media/20261117-leesearch, 맥북 도우미), 미미미누 인터뷰(X @MungmungKi73338, media/20261117-leepast),
DreamSchool 이윤규 인터뷰 2개(X @eom0x media/20261116-leetx, lime.now 재게시 media/20261116-kk-leet). 대사는 transcribe(faster-whisper).
scripts/landscape_reel/band_build.py 틀. 대사는 transcribe 워크플로(faster-whisper small) 단어 타임스탬프로 맞춤.
"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D='media/20261117-leepast-reel'; M='media'; R=f'{D}/work'; os.makedirs(R,exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
TAG='리트 만점자 의혹'; L=['리트 만점자','과거 인터뷰 발언','모아 보니']
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
BJ=f'{M}/20261117-leesearch/video/y1.mp4'; MI=f'{M}/20261117-leepast/video/v1.mp4'; TX=f'{M}/20261116-leetx/video/v1.mp4'; KK=f'{M}/20261116-kk-leet/video/v1.mp4'
CBJ='810:540:235:0'          # 백지연(1280x720): 아래 박힌 자막 잘라냄
CMI='708:472:0:80'           # 미미미누(708x720): 아래 박힌 자막 잘라냄
CTX='900:600:360:20'         # DreamSchool 화면녹화(1260x712): 아래 자막·플레이어 잘라냄
CKK='delogo=x=296:y=424:w=128:h=44,crop=660:440:30:200'  # lime.now 재게시본: 위 출처·아래 남의 글씨 잘라내고 'enter' 워터마크 지움
S=[ # src, ss, dur, crop, [(t0,t1,small,b1,b2)]
 (BJ,21.3,13.6,CBJ,[(0,5.3,'유튜브 지금백지연 인터뷰(11월 11일 녹화)','"디지털 디톡스를','하게 된 거죠"'),
                     (5.3,9.6,'리트 만점 비결을 묻자','"깊게 잘 자고','다음 날 또 걷고"'),
                     (9.6,13.6,'리트 만점 비결을 묻자','"그때 머리가','굉장히 맑아졌어요"')]),
 (BJ,51.1,3.9,CBJ,[(0,3.9,'비결은 디지털 디톡스·설탕 끊기·걷기','"모든 요소가 3주 동안','완벽하게 지켜졌거든요"')]),
 (MI,4.2,2.3,CMI,[(0,2.3,'유튜브 미미미누 인터뷰 · 리트 쉬는 시간','"쉬는 시간에 나가서','뛰고 왔어요"')]),
 (MI,15.3,2.7,CMI,[(0,2.7,'유튜브 미미미누 인터뷰 · 리트 쉬는 시간','"빠른 걷기도 아니고 뛰어요?"','"네, 전력질주"')]),
 (MI,26.0,2.9,CMI,[(0,2.9,'유튜브 미미미누 인터뷰 · 리트 쉬는 시간','"근력운동을 하면','멘탈이 세지거든요"')]),
 (KK,15.0,10.3,CKK,[(0,2.3,'유튜브 DreamSchool 이윤규 변호사 인터뷰','"종이사전 이런 거','보신 건가요?" "네"'),
                     (2.3,6.0,'유튜브 DreamSchool 이윤규 변호사 인터뷰','"종이사전?','이거 너무 엉뚱한데"'),
                     (6.0,10.3,'유튜브 DreamSchool 이윤규 변호사 인터뷰','"당연히 인터넷을','찾아볼 줄 알았는데"')]),
 (TX,14.4,6.55,CTX,[(0,2.0,'같은 인터뷰 · 시험 중 고친 답을 묻자','"답을 바꾼 문제는','없으셨어요?"'),
                     (2.0,4.9,'MBC 보도: 시험지엔 25~29번 답을 연달아 고친 흔적','"23번이요"','"그게 유일해요?"'),
                     (4.9,6.55,'MBC 보도: 시험지엔 25~29번 답을 연달아 고친 흔적','"바꿔서 만점 받은 거예요?"','"네"')]),
]
segs=[]; ci=0
for k,(src,ss,dur,crop,caps) in enumerate(S):
    inputs=['-ss',str(ss),'-t',str(dur),'-i',src,'-i',f'{R}/top.png']
    # 2026.11.17: 검정 color 소스 위에 overlay 하면 장면 첫 프레임이 검게 비어 깜박였다 → 영상 자체를 pad로 키워 바탕을 만든다
    fc=(f"[0:v]{crop if '=' in crop else 'crop='+crop},scale=1080:{BH},setsar=1,pad=1080:1920:0:{BY0}:black,fps=30[b0];[b0][1:v]overlay[b1]")
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
# 커버: 검정 바탕 + 가운데 위 띠 + 아래 격자 통일형 큰 제목
subprocess.run(['ffmpeg','-v','error','-y','-ss','16.7','-i',TX,'-frames:v','1','-vf',f'crop={CTX},scale=1080:{BH}',f'{R}/cov_band.jpg'],check=True)
bg=Image.new('RGB',(1080,1920),(0,0,0)); bg.paste(Image.open(f'{R}/cov_band.jpg'),(0,330)); bg.save(f'{R}/cov_bg.jpg',quality=95)
subprocess.run(['python3','scripts/reel_overlay.py',f'{D}/cand/overlay.png','리트 만점자\n"답 바꾼 건\n23번 하나"','',f'{R}/cov_bg.jpg',f'{D}/reel_cover.jpg'],check=True)
print('done')
