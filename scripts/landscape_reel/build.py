"""사용: 저장소 루트에서 python3 scripts/landscape_reel/build.py <원고.json>  (예시: example_poland.json, out 경로는 원고에)
오늘의쓸모 가로 영상 릴스 틀(이탈리아 지도 릴스와 같은 양식).
위: 로고·노란 테두리 꼬리표·제목 2줄(흰/노랑) 고정 / 가운데: 1000x880 둥근 패널에 영상 / 오른쪽 아래 출처 / 아래: ctx·l1·l2 장면 자막."""
import subprocess, os, json, sys
from PIL import Image, ImageDraw, ImageFont
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'work'); os.makedirs(R,exist_ok=True)
F=lambda n,s: ImageFont.truetype(f'assets/fonts/Pretendard-{n}.otf',s)
Y=(255,216,77); BG=(10,11,13); PX,PY,PW,PH=40,500,1000,880
def spaced(d,xy,t,f,fill,sp):
    x,y=xy
    for ch in t: d.text((x,y),ch,font=f,fill=fill); x+=d.textlength(ch,font=f)+sp
def base(tag,t1,t2):
    im=Image.new('RGBA',(1080,1920),BG+(255,)); d=ImageDraw.Draw(im)
    lg=Image.open('brand/logo_typo_A.png').convert('RGBA'); lg=lg.resize((int(lg.width*46/lg.height),46)); im.alpha_composite(lg,(70,112))
    f=F('SemiBold',30); tw=d.textlength(tag,font=f)-0.5*len(tag)
    d.rounded_rectangle((70,186,70+tw+40,186+52),radius=26,outline=Y,width=2); spaced(d,(90,192),tag,f,Y,-0.5)
    f=F('Black',96); spaced(d,(68,262),t1,f,(255,255,255),-3); spaced(d,(68,372),t2,f,Y,-3)
    # 패널 자리 투명(영상이 비치게) + 둥근 모서리
    m=Image.new('L',(1080,1920),0); ImageDraw.Draw(m).rounded_rectangle((PX,PY,PX+PW,PY+PH),radius=30,fill=255)
    a=im.split()[3]; a.paste(0,mask=m); im.putalpha(a); im.save(f'{R}/base.png')
def cap(i,ctx,l1,l2,credit):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    if credit:
        f=F('Medium',20); d.text((1080-58,1352+10),credit,font=f,fill=(255,255,255,140),anchor='ra')
    spaced(d,(70,1438),ctx,F('SemiBold',34),(169,173,181),-0.5)
    spaced(d,(70,1500),l1,F('Black',78),(255,255,255),-2.5); spaced(d,(70,1594),l2,F('Black',78),Y,-2.5)
    im.save(f'{R}/cap{i}.png')
def build(spec):
    base(spec['tag'],*spec['title']); segs=[]; ci=0
    for k,sc in enumerate(spec['scenes']):
        inp=['-ss',str(sc['ss']),'-t',str(sc['dur']),'-i',sc['src'],'-i',f'{R}/base.png']
        crop=sc.get('crop','iw:ih:0:0')
        fc=(f"color=c=0x0a0b0d:s=1080x1920:d={sc['dur']}:r=30[bg];[0:v]crop={crop},scale={PW}:{PH}:force_original_aspect_ratio=increase,crop={PW}:{PH},setsar=1[p];"
            f"[bg][p]overlay={PX}:{PY}:shortest=1[b0];[b0][1:v]overlay[b1]")
        last='b1'
        for j,c in enumerate(sc['caps']):
            cap(ci,c[2],c[3],c[4],sc.get('credit','')); inp+=['-i',f'{R}/cap{ci}.png']
            fc+=f";[{last}][{2+j}:v]overlay=enable='between(t,{c[0]},{c[1]})'[c{j}]"; last=f'c{j}'; ci+=1
        out=f'{R}/s{k}.mp4'
        subprocess.run(['ffmpeg','-v','error','-y',*inp,'-filter_complex',fc,'-map',f'[{last}]','-map','0:a?','-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','2','-b:a','160k',out],check=True)
        segs.append(out)
    open(f'{R}/list.txt','w').write(''.join(f"file '{s}'\n" for s in segs))
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{R}/list.txt','-af','loudnorm=I=-16:TP=-1.5','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',spec['out']],check=True)
if __name__=='__main__': build(json.load(open(sys.argv[1])))
