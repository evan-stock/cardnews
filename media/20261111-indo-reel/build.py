"""인도네시아 족자카르타 시위 썰 릴스 (2026.11.11). 저장소 루트에서: python3 media/20261111-indo-reel/build.py
원본: 엑스 @oqforwhat(11.10 23:40 WIB '병원 앞', media/20261111-indo/video/v1.mp4),
      @unmagnetism(투구 기념탑, media/20261111-indo2/video/v1.mp4). 세로 영상 꽉 + 위 제목 고정 + 아래 장면 자막."""
import subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
D='media/20261111-indo-reel'; W=f'{D}/work'; os.makedirs(W,exist_ok=True)
FB='assets/fonts/Pretendard-Black.otf'; FM='assets/fonts/Pretendard-Medium.otf'; FX='assets/fonts/Pretendard-ExtraBold.otf'
Y=(255,216,77)
A='media/20261111-indo/video/v1.mp4'; B='media/20261111-indo2/video/v1.mp4'
DA=16.8; DB=16.9; HOLD=3.2; T=DA+DB+HOLD
def fit(d,t,f,maxw=940):
    s=f.size
    while d.textlength(t,font=f)>maxw: s-=2; f=ImageFont.truetype(f.path,s)
    return f
def grad(d,y0,y1,a0,a1):
    for y in range(y0,y1):
        t=(y-y0)/(y1-y0); d.line([(0,y),(1080,y)],fill=(0,0,0,int(a0+(a1-a0)*t)))
def top():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    grad(d,0,700,200,0)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); h=46; lg=lg.resize((int(lg.width*h/lg.height),h)); im.alpha_composite(lg,(70,238))
    f=ImageFont.truetype(FX,34); tag='인도네시아 시위'; tw=d.textlength(tag,font=f)
    d.rounded_rectangle((70,310,70+tw+36,362),radius=8,fill=Y); d.text((88,336),tag,font=f,fill=(0,0,0),anchor='lm')
    L=['산불 연기 속 시위','밤 11시 40분 족자카르타',"'병원 앞'까지 최루탄"]
    for i,l in enumerate(L): d.text((70,455+i*88),l,font=fit(d,l,ImageFont.truetype(FB,78)),fill=Y if i==2 else (255,255,255),anchor='ls')
    im.save(f'{W}/top.png')
def cap(i,small,b1,b2):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    grad(d,1250,1920,0,225)
    d.text((70,1450),small,font=fit(d,small,ImageFont.truetype(FM,38)),fill=(225,225,225),anchor='ls')
    d.text((70,1540),b1,font=fit(d,b1,ImageFont.truetype(FB,68)),fill=(255,255,255),anchor='ls')
    d.text((70,1625),b2,font=fit(d,b2,ImageFont.truetype(FB,68)),fill=Y,anchor='ls')
    im.save(f'{W}/cap{i}.png'); return f'{W}/cap{i}.png'
top()
C=[(0,5.5,'11월 10일 밤 11시 40분 · 족자카르타','경찰이 쏜 최루탄,','연기가 거리를 덮었다'),
   (5.5,11,'촬영자 "여기 병원 바로 앞이다"','쫓기던 시위대,','응급실 앞에서 막혔다'),
   (11,DA,'현지 매체 트리분 족자 보도','가자마다대 앞 로터리,','자정 직전 또 충돌'),
   (DA,DA+6,'같은 날 밤 · 투구(Tugu) 기념탑','도시 한복판에','불꽃과 연기'),
   (DA+6,DA+11.5,'이들이 거리로 나온 이유','11년 만의 최악 산불,',"정부는 '재난' 선포 거부"),
   (DA+11.5,DA+DB,'올해 인도네시아','증시는 28년 만의 폭락,','대통령 지지율 81→44%'),
   (DA+DB,T,'시위대 구호','"자연재해가 아니라',"'정치 재해'다\"")]
sc='scale=1080:1920:flags=lanczos,setsar=1,fps=30'
inputs=['-t',str(DA),'-i',A,'-t',str(DB),'-i',B,'-i',f'{W}/top.png']
fc=(f"[0:v]{sc}[a];[1:v]{sc},tpad=stop_mode=clone:stop_duration={HOLD}[b0];[b0]eq=brightness=0:saturation=1[b];"
    f"[0:a]aresample=44100,aformat=channel_layouts=stereo[aa];[1:a]aresample=44100,aformat=channel_layouts=stereo,apad=pad_dur={HOLD}[ba];"
    f"[a][aa][b][ba]concat=n=2:v=1:a=1[v0][a0];[v0][2:v]overlay[t0]")
last='t0'; n=3
for i,(t0,t1,s,b1,b2) in enumerate(C):
    inputs+=['-loop','1','-t',str(T),'-i',cap(i,s,b1,b2)]; fc+=f";[{last}][{n}:v]overlay=enable='between(t,{t0},{t1-0.001})'[c{i}]"; last=f'c{i}'; n+=1
# 마지막 구호 장면은 영상을 어둡게
fc+=f";[{last}]drawbox=0:0:1080:1920:black@0.45:t=fill:enable='gte(t,{DA+DB})'[dk]"
# drawbox가 자막 위에 덮이므로 구호 자막을 한 번 더 얹는다
inputs+=['-loop','1','-t',str(T),'-i',f'{W}/cap{len(C)-1}.png','-i',f'{W}/top.png']
fc+=f";[dk][{n}:v]overlay=enable='gte(t,{DA+DB})'[e1];[e1][{n+1}:v]overlay=enable='gte(t,{DA+DB})',format=yuv420p[vo];[a0]loudnorm=I=-16:TP=-1.5[ao]"
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc,'-map','[vo]','-map','[ao]','-t',str(T),'-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-c:a','aac','-ar','44100','-b:a','160k','-movflags','+faststart',f'{D}/reel.mp4'],check=True)
# 커버: 영상 프레임 꽉 + reel_overlay 큰 제목
sys.path.insert(0,'scripts'); from reel_overlay import overlay
subprocess.run(['ffmpeg','-v','error','-y','-ss',sys.argv[1] if len(sys.argv)>1 else '1.2','-i',A,'-frames:v','1','-vf','scale=1080:1920:flags=lanczos',f'{W}/f.png'],check=True)
cv=Image.open(f'{W}/f.png').convert('RGBA'); cv.alpha_composite(overlay(['인도네시아',"'병원 앞'까지",'최루탄']))
cv.convert('RGB').save(f'{D}/cover.jpg',quality=93)
print('done')
