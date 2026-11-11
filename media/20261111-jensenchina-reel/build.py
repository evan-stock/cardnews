"""불륜 터지기 한 달 전 젠슨 황이 '중국'에 대해 한 말 — 띠형 릴스 (2026.11.11). 저장소 루트에서 실행.
원본: Bloomberg 'The Circuit' 에밀리 창 인터뷰 (엑스 @business 2026.11.09 게시, 세로 1080x1920 원본).
세로 영상을 띠(3:2)로 잘라 아래 블룸버그 영어 자막·이름 자막을 뺌. 대사: transcribe 워크플로(faster-whisper small) v1.words.json."""
import subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
D='media/20261111-jensenchina-reel'; W=f'{D}/work'; os.makedirs(W,exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
SRC='media/20261111-t20/video/v1.mp4'
CROP='1080:720:0:340'
def fit(d,t,f,maxw=940):
    s=f.size
    while d.textlength(t,font=f)>maxw: s-=2; f=ImageFont.truetype(f.path,s)
    return f
def top():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); h=46; lg=lg.resize((int(lg.width*h/lg.height),h)); im.alpha_composite(lg,(70,238))
    f=ImageFont.truetype(FX,34); tag='블룸버그 인터뷰 · 엔비디아 CEO'; tw=d.textlength(tag,font=f)
    d.rounded_rectangle((70,310,70+tw+36,362),radius=8,fill=Y); d.text((88,336),tag,font=f,fill=(0,0,0),anchor='lm')
    L=['불륜 터지기 한 달 전','젠슨 황이',"'중국'에 대해 한 말"]
    for i,l in enumerate(L): d.text((70,433+i*88),l,font=fit(d,l,ImageFont.truetype(FB,78)),fill=Y if i==2 else (255,255,255),anchor='ls')
    im.save(f'{W}/top.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    if small: d.text((70,1450),small,font=fit(d,small,ImageFont.truetype(FM,38)),fill=(225,225,225),anchor='ls')
    if b1: d.text((70,1540),b1,font=fit(d,b1,ImageFont.truetype(FB,68)),fill=(255,255,255),anchor='ls')
    d.text((70,1625),b2,font=fit(d,b2,ImageFont.truetype(FB,68)),fill=Y,anchor='ls')
    p=f'{W}/cap{i}.png'; im.save(p); return p
top()
# 1막: 원본 소리 그대로. (원본 시작, 끝, [(원본 시각 a, b, 작은줄, 굵은1, 굵은2)])
P=[(47.8,54.7,[(47.8,54.7,'젠슨 황 · 엔비디아 CEO','"중국과 경쟁은 하지만','그들은 우리 적이 아닙니다"')]),
   (54.9,66.2,[(54.9,60.5,'젠슨 황','"AI로부터 세상의 안전을','진심으로 걱정한다면"'),
              (60.5,66.2,'젠슨 황','"당연히 대화를 열고','모든 방법으로 협력해야죠"')]),
   (28.4,37.9,[(28.4,34.9,'미국의 대중국 칩 수출 규제를 두고','"우린 실수를 했어요','되돌리기 어려운 실수죠"'),
              (34.9,37.9,'젠슨 황','"그래도 전 최선을 다했어요','그게 제가 할 수 있는 전부였죠"')]),
   (66.3,74.9,[(66.3,74.9,'진행자 에밀리 창','"중국이 뭘 하면','\'칩 팔지 말자\' 하시겠어요?"')]),
   (75.2,80.0,[(75.2,80.0,'젠슨 황','"이론적으론 많겠죠','그들은 실용적인 사람들이에요"')]),
   (89.5,93.9,[(89.5,93.9,'젠슨 황','"그들은 중국이 부자 되길 원해요','우린 그 열망을 존중해야 합니다"')])]
# 2막: 정보(소리 없음). (원본 시작, 길이, 작은줄, 굵은1, 굵은2)
A=[(0.3,4.3,'한 달도 안 돼 · 미 정보당국 판단 (외신 보도)','젠슨 황, 불륜 인정',"상대는 '중국 포섭' 의심 여성"),
   (83.5,4.6,'엔비디아 이사회 조사 · 젠슨 황 "전적으로 협조"',"'적이 아니다'던 그 중국이",'그를 노린 거라면?')]
segs=[]; n_=0
for pi,(a,b,cs) in enumerate(P):
    dur=b-a
    inputs=['-ss',str(a),'-t',str(dur),'-i',SRC,'-i',f'{W}/top.png']
    fc=f"[0:v]crop={CROP},setsar=1[fg];color=black:s=1080x1920:r=30:d={dur}[bg];[bg][fg]overlay=0:{BY0}:shortest=1[v0];[v0][1:v]overlay[t0]"
    n=2; last='t0'
    for (t0,t1,s_,b1,b2) in cs:
        n_+=1; x0,x1=t0-a,t1-a
        inputs+=['-loop','1','-t',str(dur),'-i',cap(n_,s_,b1,b2)]; fc+=f";[{last}][{n}:v]overlay=enable='between(t,{x0},{x1-0.001})'[c{n_}]"; last=f'c{n_}'; n+=1
    fc+=f";[{last}]format=yuv420p[vo];[0:a]aresample=44100,aformat=channel_layouts=stereo,afade=in:d=0.08,afade=out:st={dur-0.12}:d=0.12[ao]"
    out=f'{W}/a{pi}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc,'-map','[vo]','-map','[ao]','-t',str(dur),'-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-c:a','aac','-ar','44100','-ac','2','-b:a','160k',out],check=True)
    segs.append(out)
for k,(ss,dur,s,b1,b2) in enumerate(A):
    cp=cap(100+k,s,b1,b2)
    fc=(f"[0:v]crop={CROP},setsar=1,eq=saturation=0.6:brightness=-0.05[fg];color=black:s=1080x1920:r=30:d={dur}[bg];[bg][fg]overlay=0:{BY0}:shortest=1,fade=in:st=0:d=0.25[v0];"
        f"[v0][1:v]overlay[t0];[t0][2:v]overlay,format=yuv420p[vo]")
    out=f'{W}/s{k}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(ss),'-t',str(dur),'-i',SRC,'-i',f'{W}/top.png','-loop','1','-t',str(dur),'-i',cp,
        '-f','lavfi','-t',str(dur),'-i','anullsrc=r=44100:cl=stereo','-filter_complex',fc,'-map','[vo]','-map','3:a',
        '-t',str(dur),'-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-c:a','aac','-ar','44100','-ac','2','-b:a','160k',out],check=True)
    segs.append(out)
open(f'{W}/list.txt','w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{W}/list.txt','-af','loudnorm=I=-16:TP=-1.5','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',f'{D}/reel.mp4'],check=True)
# 커버: 세로 원본 클로즈업 꽉 + reel_overlay 큰 제목
sys.path.insert(0,'scripts'); from reel_overlay import overlay
subprocess.run(['ffmpeg','-v','error','-y','-ss','52.3','-i',SRC,'-frames:v','1',f'{W}/f.png'],check=True)
from PIL import ImageFilter
fr=Image.open(f'{W}/f.png').convert('RGB'); box=(0,1330,1080,1580)
fr.paste(fr.crop(box).filter(ImageFilter.GaussianBlur(40)).point(lambda v:int(v*0.35)),box[:2])  # 블룸버그 영어 자막 가림(검정 재킷 위)
cv=fr.convert('RGBA'); cv.alpha_composite(overlay(['불륜 터지기','한 달 전 젠슨 황이',"'중국'에 대해 한 말"],tag=None))
cv.convert('RGB').save(f'{D}/cover.jpg',quality=93)
print('done')
