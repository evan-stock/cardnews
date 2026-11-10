"""머스크에겐 미인계가 안 통하는 이유 띠형 릴스 (2026.11.10). 저장소 루트에서: python3 media/20261110-muskhoney-reel/build.py
원본: Lex Fridman Podcast #49(2019.11.12, youtube smK9dgdTl40) 장면. 맥북 응답이 없어 엑스 @tsla_bitcoin 게시 클립
(media/20261110-musk-honey/video/v1.mp4)을 쓰되, 남의 한국어 자막·출처 글씨·LEX 로고가 안 보이게 가운데만 잘라 씀.
대사: transcribe 워크플로(faster-whisper small) 받아쓰기 → v1.srt / v1.words.json, 화자는 화면으로 확인."""
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D='media/20261110-muskhoney-reel'; W=f'{D}/work'; os.makedirs(W,exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77); BY0,BH=660,720
SRC='media/20261110-musk-honey/video/v1.mp4'; SS=0.0; END=44.0
CROP='774:516:300:50'   # 위 출처 글씨(y<35)·아래 남의 자막(y>570)·오른쪽 아래 LEX 로고 제외
def fit(d,t,f,maxw=940):
    s=f.size
    while d.textlength(t,font=f)>maxw: s-=2; f=ImageFont.truetype(f.path,s)
    return f
def top():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); h=46; lg=lg.resize((int(lg.width*h/lg.height),h)); im.alpha_composite(lg,(70,238))
    f=ImageFont.truetype(FX,34); tag='젠슨 황 미인계 의혹 그 후'; tw=d.textlength(tag,font=f)
    d.rounded_rectangle((70,310,70+tw+36,362),radius=8,fill=Y); d.text((88,336),tag,font=f,fill=(0,0,0),anchor='lm')
    L=['중국 미인계가','머스크한테만',"'안 통하는' 이유"]
    for i,l in enumerate(L): d.text((70,433+i*88),l,font=fit(d,l,ImageFont.truetype(FB,78)),fill=Y if i==2 else (255,255,255),anchor='ls')
    im.save(f'{W}/top.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,1450),small,font=fit(d,small,ImageFont.truetype(FM,38)),fill=(225,225,225),anchor='ls')
    if b1: d.text((70,1540),b1,font=fit(d,b1,ImageFont.truetype(FB,68)),fill=(255,255,255),anchor='ls')
    d.text((70,1625),b2,font=fit(d,b2,ImageFont.truetype(FB,68)),fill=Y,anchor='ls')
    im.save(f'{W}/cap{i}.png'); return f'{W}/cap{i}.png'
def quote_card(out):
    """2025.10.23 머스크 엑스 글을 우리 디자인으로 옮긴 인용 카드(캡처 흉내 아님)."""
    im=Image.new('RGB',(1080,720),(18,20,24)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((60,60,1020,660),radius=36,outline=(70,74,80),width=3)
    d.text((110,150),'일론 머스크 · 엑스 · 2025.10.23',font=ImageFont.truetype(FM,36),fill=(170,175,182),anchor='ls')
    d.text((110,215),"'미인계 간첩' 보도 캡처에 단 한 줄",font=ImageFont.truetype(FM,36),fill=(170,175,182),anchor='ls')
    f=ImageFont.truetype(FB,74)
    d.text((110,350),'“If she’s a 10,',font=f,fill=(255,255,255),anchor='ls')
    d.text((110,440),'you’re an asset.”',font=f,fill=(255,255,255),anchor='ls')
    d.text((110,560),'10점짜리 미녀가 다가오면, 당신이 포섭 대상',font=fit(d,'10점짜리 미녀가 다가오면, 당신이 포섭 대상',ImageFont.truetype(FX,46),860),fill=Y,anchor='ls')
    im.save(out,quality=95); return out
top()
T=END-SS
# 1막: 대사(시간은 SS 기준, v1.words.json 그대로 번역)
C=[(0,5.4,'2019년 렉스 프리드먼 팟캐스트 · 머스크','머스크 "섹스에 대해선 진짜','어마어마한 고민이 있었죠"'),
   (5.4,12.2,'일론 머스크','"번식 목적이 없는 성관계에','엄청난 생각이 쏟아졌는데"'),
   (12.2,22.3,'일론 머스크','"번식이 빠지면 그건','사실 꽤 어리석은 짓이에요"'),
   (22.3,24.4,'','','"그럼 왜 하냐고요?"'),
   (24.4,28.3,'일론 머스크','"변연계(본능 뇌)가','행복해지니까요. 그게 다예요"'),
   (28.3,30.0,'일론 머스크','"근데 진짜','황당하죠"'),
   (30.0,34.8,'진행자 렉스 프리드먼','"존재 자체가','원래 좀 황당하잖아요"'),
   (34.8,40.8,'일론 머스크','"그런데 그 많은 머리를','\'어떻게 더 할까\'에만 썼어요"'),
   (40.8,T,'일론 머스크','"번식은','고려 대상도 아닌데요"')]
# 2막: 정보(소리 없음, 음악은 앱에서). (종류, 길이, 원본 시작, 자막)
A=[('card',4.4,None,('2025년 10월 · 영국 더타임스 \'미인계 간첩\' 보도에','머스크가 직접 남긴 한 줄','"10점 미녀면, 넌 포섭 대상"')),
   ('clip',3.8,0.6,('그런데 반전','번식 없는 건 \'어리석다\'는 그,','알려진 자녀만 14명')),
   ('clip',3.8,25.2,('중국 미인계 간첩 입장에선','정보는 못 빼내고','아이만 생기는 남자?'))]
segs=[]
# 1막 렌더: 원본 시간 기준 조각(12.5~15.1 말 멈춘 구간은 잘라냄)
PARTS=[(0,12.5),(15.1,T)]
for pi,(a,b) in enumerate(PARTS):
    dur=b-a
    inputs=['-ss',str(SS+a),'-t',str(dur),'-i',SRC,'-i',f'{W}/top.png']
    fc=(f"[0:v]crop={CROP},scale=1080:{BH},setsar=1[fg];color=black:s=1080x1920:r=30:d={dur}[bg];[bg][fg]overlay=0:{BY0}:shortest=1[v0];[v0][1:v]overlay[t0]")
    n=2; last='t0'
    for i,(t0,t1,s_,b1,b2) in enumerate(C):
        x0,x1=max(t0,a)-a,min(t1,b)-a
        if x1<=x0: continue
        inputs+=['-loop','1','-t',str(dur),'-i',cap(i,s_,b1,b2)]; fc+=f";[{last}][{n}:v]overlay=enable='between(t,{x0},{x1-0.001})'[c{i}]"; last=f'c{i}'; n+=1
    fc+=f";[{last}]format=yuv420p[vo];[0:a]aresample=44100,aformat=channel_layouts=stereo[ao]"
    out=f'{W}/a{pi}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc,'-map','[vo]','-map','[ao]','-t',str(dur),'-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-c:a','aac','-ar','44100','-ac','2','-b:a','160k',out],check=True)
    segs.append(out)
# 2막 렌더
for k,(kind,dur,ss,(s,b1,b2)) in enumerate(A):
    cp=cap(100+k,s,b1,b2); nf=int(dur*30)
    if kind=='card':
        src=['-loop','1','-framerate','30','-t',str(dur),'-i',quote_card(f'{W}/quote.jpg')]
        fg=f"[0:v]scale=2160:1440,zoompan=z='1+0.06*on/{nf}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x720:fps=30,setsar=1[fg]"
    else:
        src=['-ss',str(ss),'-t',str(dur),'-i',SRC]
        fg=f"[0:v]crop={CROP},scale=1080:{BH},setsar=1[fg]"
    fc=(f"{fg};color=black:s=1080x1920:r=30:d={dur}[bg];[bg][fg]overlay=0:{BY0}:shortest=1,fade=in:st=0:d=0.25[v0];"
        f"[v0][1:v]overlay[t0];[t0][2:v]overlay,format=yuv420p[vo]")
    out=f'{W}/s{k+1}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y',*src,'-i',f'{W}/top.png','-loop','1','-t',str(dur),'-i',cp,
        '-f','lavfi','-t',str(dur),'-i','anullsrc=r=44100:cl=stereo','-filter_complex',fc,'-map','[vo]','-map','3:a',
        '-t',str(dur),'-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-c:a','aac','-ar','44100','-ac','2','-b:a','160k',out],check=True)
    segs.append(out)
open(f'{W}/list.txt','w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{W}/list.txt','-af','loudnorm=I=-16:TP=-1.5','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',f'{D}/reel.mp4'],check=True)
# 커버: 검정 배경 + 가로 띠(y=330) + reel_overlay 큰 제목
import sys; sys.path.insert(0,'scripts'); from reel_overlay import overlay
subprocess.run(['ffmpeg','-v','error','-y','-ss','25.9','-i',SRC,'-frames:v','1',f'{W}/f.png'],check=True)
x,y=300,50
cv=Image.new('RGB',(1080,1920),(0,0,0)); fr=Image.open(f'{W}/f.png').convert('RGB').crop((x,y,x+774,y+516)).resize((1080,720),Image.LANCZOS)
cv.paste(fr,(0,330)); cv=cv.convert('RGBA'); cv.alpha_composite(overlay(['중국 미인계가','머스크한테만',"'안 통하는' 이유"],tag=None))
cv.convert('RGB').save(f'{D}/cover.jpg',quality=93)
print('done')
