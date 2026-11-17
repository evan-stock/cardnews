"""윤도영 강사 AI 부정행위 입장 발언 띠형 릴스(2026.11.17). 저장소 루트에서: python3 media/20261117-yoondy-reel/build.py
scripts/landscape_reel/band_build.py 틀. 대사는 transcribe 워크플로(faster-whisper small) 단어 타임스탬프로 맞춤.
"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D='media/20261117-yoondy-reel'; V='media/20261117-yoondy2/video'; R=f'{D}/work'; os.makedirs(R,exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
TAG='수능 AI 부정행위'; L=['일타강사, 대통령에','"해외 있다고 해서','일 못 하는 건 아냐"']
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
CY='960:640:220:40'   # 원본 1280x720, 인물 가운데
S=[ # src, ss, dur, crop, [(t0,t1,small,b1,b2)]
 (f'{V}/y1.mp4',80.7,20.8,CY,[(0,5.6,'과학 일타강사 윤도영 · 16일 유튜브','"성공해서 의대 가면','남은 일생이 보장되고"'),
                             (5.6,10.4,'과학 일타강사 윤도영 · 16일 유튜브','"실패해도 처벌은','솜방망이"'),
                             (10.4,17.9,'세무사 수석 AI 부정행위 자백 다음 날','"도덕적 기준 없는 사람은','시도 안 할 이유가 없다"'),
                             (17.9,20.8,'세무사 수석 AI 부정행위 자백 다음 날','"수학으로 말하면','기댓값이 양수"')]),
 (f'{V}/y1.mp4',398.1,10.9,CY,[(0,6.6,'해외 순방 중인 대통령을 향해','"대통령이 이 사안을','얼마나 심각하게 보는지"'),
                              (6.6,10.9,'해외 순방 중인 대통령을 향해','"조금','의구심이 듭니다"')]),
 (f'{V}/y1.mp4',423.6,7.1,CY,[(0,7.1,'수능은 19일, 사흘 앞','"해외에 있다고 해서','일을 못하는 건 아니잖아요"')]),
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
# 커버: 검정 바탕 + 가운데 위 띠 + 아래 격자 통일형 큰 제목
subprocess.run(['ffmpeg','-v','error','-y','-ss','99.5','-i',f'{V}/y1.mp4','-frames:v','1','-vf',f'crop={CY},scale=1080:{BH}',f'{R}/cov_band.jpg'],check=True)
bg=Image.new('RGB',(1080,1920),(0,0,0)); bg.paste(Image.open(f'{R}/cov_band.jpg'),(0,330)); bg.save(f'{R}/cov_bg.jpg',quality=95)
subprocess.run(['python3','scripts/reel_overlay.py',f'{D}/cand/overlay.png','일타강사\n"부정행위\n기댓값이 양수"','',f'{R}/cov_bg.jpg',f'{D}/reel_cover.jpg'],check=True)
print('done')
