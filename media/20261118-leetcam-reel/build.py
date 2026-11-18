"""리트 만점자 자택 앞 인터뷰 '카메라 줌인' 띠형 릴스(2026.11.18). 저장소 루트에서: python3 media/20261118-leetcam-reel/build.py
원본: 유튜브 엠빅뉴스 '리트 만점자 이진우 "목요일에 다 말씀 드릴게요"'(2026.11.18 공개, 17일 밤 촬영, 맥북 yt_queue 20261118-leetcam2, 480p).
화제 계기: 엑스 @muuuaaa11 '카메라 감독 무빙' 글(25만 조회) + 유튜브 댓글 '8:19 카메라감독 사악함'.
대사는 transcribe(faster-whisper small) 시각. 따옴표는 받아쓰기로 확인한 실제 발언만. 틀: media/20261117-kangst-reel/build.py(pad 바탕, 깜박임 없음).
"""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D='media/20261118-leetcam-reel'; V='media/20261118-leetcam2/video'; R=f'{D}/work'; os.makedirs(R,exist_ok=True); os.makedirs(f'{D}/cand',exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
TAG='수능 D-1 · 리트 만점자'; L=['인터뷰 도중','카메라가 갑자기','줌인한 곳']
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
    for t in (b1,b2): assert d.textlength(t,font=f)<=950,t
    assert d.textlength(small,font=ImageFont.truetype(FM,38))<=950,small
    im.save(f'{R}/cap{i}.png')
top()
CW='720:480:0:0'    # 넓은 장면: 인물이 왼쪽
CY='720:480:67:0'   # 얼굴 장면(엠빅뉴스 로고는 오른쪽 위 x>787이라 잘려 나감)
K='17일 밤 · 자택 인근 · MBC 취재진'
S=[ # src, ss, dur, crop, [(t0,t1,small,b1,b2)]
 (f'{V}/y1.mp4',496.6,8.2,CW,[(0,1.9,K,'목요일에 해명할 의혹을','하나씩 꼽는 리트 만점자'),
                              (1.9,8.2,'손가락으로 하나씩 세는 순간 → 줌인','"리트, 수능, 성적표','스토킹, 욕설"')]),
 (f'{V}/y1.mp4',505.6,4.0,CY,[(0,4.0,'촬영 중인 걸 확인하더니','"혹시 화면도 나가네요?','동영상이 나가요?"')]),
 (f'{V}/y1.mp4',509.7,4.4,CY,[(0,4.4,'MBC 취재진','"원하시면 모자이크는','당연히 가능합니다"')]),
 (f'{V}/y1.mp4',514.1,5.3,CY,[(0,5.3,'오히려 범죄자처럼 보인다며','"모자이크','하지 마세요"')]),
 (f'{V}/y1.mp4',531.5,8.3,CY,[(0,8.3,'"AI는 하나도 안 썼냐"는 질문에','"얼마든지','조사에 응하겠습니다"')]),
 (f'{V}/y1.mp4',382.0,4.4,CY,[(0,4.4,'수척해진 얼굴','"이번 한 주 동안 힘들어요','몸도 많이 지치고"')]),
 (f'{V}/y1.mp4',397.4,6.2,CY,[(0,6.2,'수능 국어 생중계는 내일(19일)','"제가 도망갈','생각도 안 해요"')]),
]
segs=[]; ci=0
for k,(src,ss,dur,crop,caps) in enumerate(S):
    inputs=['-ss',str(ss),'-t',str(dur),'-i',src,'-i',f'{R}/top.png']
    fc=(f"[0:v]crop={crop},scale=1080:{BH},setsar=1,pad=1080:1920:0:{BY0}:black,fps=30[b0];[b0][1:v]overlay[b1]")
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
# 커버: 검정 바탕 + 위 띠(손가락 줌인 장면) + 아래 격자 통일형 큰 제목
subprocess.run(['ffmpeg','-v','error','-y','-ss','501.0','-i',f'{V}/y1.mp4','-frames:v','1','-vf',f'crop={CW},scale=1080:{BH}',f'{R}/cov_band.jpg'],check=True)
bg=Image.new('RGB',(1080,1920),(0,0,0)); bg.paste(Image.open(f'{R}/cov_band.jpg'),(0,330)); bg.save(f'{R}/cov_bg.jpg',quality=95)
subprocess.run(['python3','scripts/reel_overlay.py',f'{D}/cand/overlay.png','리트 만점자\n카메라 감독이\n줌인한 곳','',f'{R}/cov_bg.jpg',f'{D}/reel_cover.jpg'],check=True)
print('done')
