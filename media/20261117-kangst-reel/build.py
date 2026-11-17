"""강성태 '수능 AI 부정행위 막을 방법' 띠형 릴스(2026.11.17). 저장소 루트에서: python3 media/20261117-kangst-reel/build.py
원본: 유튜브 강성태 공부의 신 채널(맥북 도우미 yt_queue 20261117-kangst, 480p). 대사는 transcribe(faster-whisper small) 단어 시각.
media/20261117-yoondy-reel/build.py 틀(pad 바탕, 깜박임 없음). 토마토마 앱 소개 구간은 쓰지 않음. 따옴표는 실제 발언만.
"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D='media/20261117-kangst-reel'; V='media/20261117-kangst/video'; R=f'{D}/work'; os.makedirs(R,exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
TAG='수능 D-2'; L=['공부의 신 강성태가 낸','수능 AI 커닝','막는 법']
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
CY='720:480:67:0'   # 원본 854x480, 인물 가운데
K='공부의 신 강성태 · 17일 유튜브'
S=[ # src, ss, dur, crop, [(t0,t1,small,b1,b2)]
 (f'{V}/y1.mp4',31.8,5.4,CY,[(0,5.4,'AI 부정행위자 수 추정해 보니','"믿기 어려우시겠지만','9천 명입니다"')]),
 (f'{V}/y1.mp4',42.3,2.0,CY,[(0,2.0,'언론 보도 사례로 낸 자체 추정','"물론 이것은','최대 추정값입니다"')]),
 (f'{V}/y1.mp4',107.1,2.4,CY,[(0,2.4,K,'"커닝의 답은','시험장 안에서 나오지 않습니다"')]),
 (f'{V}/y1.mp4',113.8,2.3,CY,[(0,2.3,K,'"대부분은 밖에 있는','AI 서버에서 나와요"')]),
 (f'{V}/y1.mp4',116.6,7.4,CY,[(0,4.8,'대책 ① AI 회사가 답 막기','"챗GPT나 클로드 등이','시험지 사진에 답하지 않게"'),
                              (4.8,7.4,'대책 ① AI 회사가 답 막기','"수능 시간','딱 그 시간만요"')]),
 (f'{V}/y1.mp4',124.0,3.4,CY,[(0,3.4,'수능 듣기 평가 땐 항공기 이착륙도 통제','"비행기조차 뜨지 못하는데','충분히 가능합니다"')]),
 (f'{V}/y1.mp4',132.2,3.2,CY,[(0,3.2,'AI 공부 앱을 만드는 입장에서','"절대 어려운 일이 아니고','엄청나게 간단합니다"')]),
 (f'{V}/y1.mp4',140.1,1.7,CY,[(0,1.7,'AI 공부 앱을 만드는 입장에서','"한 줄 정도만','추가해도 됩니다"')]),
 (f'{V}/y1.mp4',143.6,4.5,CY,[(0,4.5,'대책 ② 사후 조사','수능 문제가 AI에','입력됐는지 확인')]),
 (f'{V}/y1.mp4',148.1,5.7,CY,[(0,5.7,'대책 ③ 출입 때 금속탐지기','몸에 숨긴 기기로','직접 돌리는 것도 차단')]),
 (f'{V}/y1.mp4',154.0,3.9,CY,[(0,3.9,'교육부가 말한 전파 차단은','"법으로 막혀 있어','쉽지 않을 것"')]),
 (f'{V}/y1.mp4',158.0,4.6,CY,[(0,2.0,K,'"저를 시켜주세요','제가 하겠습니다"'),
                              (2.0,4.6,K,'"교육부에서','일일 알바라도 하겠습니다"')]),
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
subprocess.run(['ffmpeg','-v','error','-y','-ss','118.5','-i',f'{V}/y1.mp4','-frames:v','1','-vf',f'crop={CY},scale=1080:{BH}',f'{R}/cov_band.jpg'],check=True)
bg=Image.new('RGB',(1080,1920),(0,0,0)); bg.paste(Image.open(f'{R}/cov_band.jpg'),(0,330)); bg.save(f'{R}/cov_bg.jpg',quality=95)
subprocess.run(['python3','scripts/reel_overlay.py',f'{D}/cand/overlay.png','강성태가 말한\n수능 AI 커닝\n막는 법','',f'{R}/cov_bg.jpg',f'{D}/reel_cover.jpg'],check=True)
print('done')
