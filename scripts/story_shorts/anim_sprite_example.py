# 이야기형 그래픽 쇼츠 — 움직이는 그래픽 장면 예시(붉은 번개 2026.10.18). 사용: python3 scripts/story_shorts/anim_sprite_example.py media/<id>/video <참고프레임.jpg> a1886 aalt a1925 a1989
# 장면마다 함수 하나: 배경(grad·stars) + 움직이는 요소(번쩍임·숫자 카운터·선 그리기·팝업·TV 지지직) + 아래쪽 큰 연도/설명(자막 자리 y≈760~1050은 비움). 1080x1490(띠 아래 영역), 30fps, 7초.
import random,math,sys,subprocess
from PIL import Image,ImageDraw,ImageFilter,ImageFont,ImageOps,ImageChops
OUT=sys.argv[1]; SRC=sys.argv[2]
W,H,FPS,DUR=1080,1490,30,7.0
N=int(FPS*DUR)
FB="/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc";FM="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
f=lambda s,b=True:ImageFont.truetype(FB if b else FM,s)
YEL=(255,212,59);WHT=(255,255,255)
ease=lambda t:0 if t<=0 else 1 if t>=1 else 1-(1-t)**3
def writer(name):
    return subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-c:v","libx264","-crf","18","-pix_fmt","yuv420p",f"{OUT}/{name}.mp4"],stdin=subprocess.PIPE)
def grad(top,bot):
    im=Image.new('RGB',(W,H));d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H;d.line([(0,y),(W,y)],fill=tuple(int(top[i]*(1-t)+bot[i]*t) for i in range(3)))
    return im
def stars(seed,n,ymax=0.75):
    r=random.Random(seed);return [(r.randrange(W),r.randrange(int(H*ymax)),r.choice([1,2,2,3]),r.random()*6.28,r.uniform(1,3)) for _ in range(n)]
def draw_stars(d,st,t):
    for x,y,s,ph,sp in st:
        c=int(150+100*(0.5+0.5*math.sin(t*sp*3+ph)));d.ellipse((x,y,x+s,y+s),fill=(c,c,c))
def sprite_layer(cx,cy,sc,seed=3):
    lay=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(lay);r=random.Random(seed)
    d.ellipse((cx-120*sc,cy-40*sc,cx+120*sc,cy+40*sc),fill=(255,40,40,240))
    for k in range(14):
        x=cx+(k-6.5)*17*sc;L=(140+r.randrange(120))*sc;xx=x
        for j in range(12):
            nx=xx+r.uniform(-9,9)*sc;y0=cy+j*L/12;y1=cy+(j+1)*L/12
            d.line([(xx,y0),(nx,y1)],fill=(255,60,60,int(240*(1-j/13))),width=max(2,int(5*sc*(1-j/14))));xx=nx
    core=lay.filter(ImageFilter.GaussianBlur(3*sc));glow=lay.filter(ImageFilter.GaussianBlur(25*sc))
    out=Image.alpha_composite(glow,core);return out
def with_alpha(layer,a):
    if a>=0.999:return layer
    l=layer.copy();al=l.getchannel('A').point(lambda v:int(v*a));l.putalpha(al);return l
def ctext(d,y,s,size,fill,b=True,stroke=0,alpha=1.0):
    ft=f(size,b);w=d.textlength(s,font=ft);d.text(((W-w)/2,y),s,font=ft,fill=fill+(int(255*alpha),),stroke_width=stroke,stroke_fill=(0,0,0,int(255*alpha)))
def text_layer(lines):
    # lines: (y,s,size,fill,bold,stroke)
    lay=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(lay)
    for y,s,size,fill,b,stv in lines: ctext(d,y,s,size,fill,b,stv)
    return lay
# ---------- 1886
def a1886():
    bg=grad((8,10,30),(25,20,45));st=stars(2,170);sp=sprite_layer(720,330,0.9,5)
    gr=Image.new('RGBA',(W,H),(0,0,0,0));gd=ImageDraw.Draw(gr);r=random.Random(7);pts=[(0,H)]
    for x in range(0,W+60,60):pts.append((x,1250+r.randrange(-40,40)))
    pts.append((W,H));gd.polygon(pts,fill=(5,5,10,255))
    tx=text_layer([(1070,"1886",170,YEL,True,6),(1290,"첫 목격 기록 · 증거는 없음",54,WHT,True,3)])
    p=writer("a1886")
    for i in range(N):
        t=i/FPS;im=bg.copy().convert('RGBA');d=ImageDraw.Draw(im);draw_stars(d,st,t)
        # flashes at 1.0s and 3.6s
        fl=max(0,1-abs(t-1.0)/0.18)+max(0,1-abs(t-3.6)/0.18)+0.25*max(0,1-abs(t-5.6)/0.25)
        if fl>0: im=Image.alpha_composite(im,with_alpha(sp,min(1,fl)))
        im=Image.alpha_composite(im,gr);d=ImageDraw.Draw(im)
        # person, arm raises after first flash
        x,y,s=130,1290,1.4;d.ellipse((x-14*s,y-110*s,x+14*s,y-82*s),fill=(0,0,0));d.rounded_rectangle((x-20*s,y-82*s,x+20*s,y-20*s),8,fill=(0,0,0))
        d.rectangle((x-16*s,y-22*s,x-4*s,y),fill=(0,0,0));d.rectangle((x+4*s,y-22*s,x+16*s,y),fill=(0,0,0))
        ang=math.radians(-20+ease((t-1.1)/0.5)*85);d.line([(x+16*s,y-76*s),(x+16*s+48*s*math.cos(ang),y-76*s-48*s*math.sin(ang))],fill=(0,0,0),width=int(9*s))
        a=ease((t-0.2)/0.6);ty=int((1-a)*60);tl=with_alpha(tx,a);im.alpha_composite(tl,(0,0)) if ty==0 else im.alpha_composite(tl.crop((0,0,W,H-ty)),(0,ty))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close();p.wait()
# ---------- altitude
def aalt():
    bg=grad((5,5,25),(30,40,80));st=stars(4,90,0.9);km=lambda k:int(1380-k*13.5);ax=150
    sp=sprite_layer(640,km(85),1.5,9)
    base=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(base)
    d.line([(ax,km(0)),(ax,km(100))],fill=(200,200,200,255),width=4)
    for k in range(0,101,10):
        d.line([(ax-14,km(k)),(ax,km(k))],fill=(200,200,200,255),width=3);d.text((ax-30,km(k)),f"{k}",font=f(30,False),fill=(200,200,200,255),anchor="rm")
    d.text((ax-30,km(100)-50),"km",font=f(30,False),fill=(200,200,200,255),anchor="rm")
    cloud=Image.new('RGBA',(W,H),(0,0,0,0));cd=ImageDraw.Draw(cloud)
    for (cx,cy,r) in [(520,km(12),130),(660,km(14),150),(800,km(11),120),(400,km(9),100),(900,km(8),90)]:cd.ellipse((cx-r,cy-r*0.6,cx+r,cy+r*0.6),fill=(70,75,95,255))
    cd.text((ax+30,km(17)-10),"번개 구름 ~15km",font=f(44),fill=WHT+(255,),stroke_width=3,stroke_fill=(0,0,0,255))
    p=writer("aalt")
    for i in range(N):
        t=i/FPS;im=bg.copy().convert('RGBA');d=ImageDraw.Draw(im);draw_stars(d,st,t);im.alpha_composite(base)
        lvl=ease((t-0.8)/2.6)*90  # rising marker 0->90 km
        if lvl>50:
            za=min(1,(lvl-50)/15);zone=Image.new('RGBA',(W,H),(0,0,0,0));ImageDraw.Draw(zone).rectangle((ax+10,km(90),W-30,km(50)),fill=(120,10,20,int(200*za)));im.alpha_composite(zone)
            fl=0.6+0.4*abs(math.sin(t*7)) if t>3.4 else za
            im.alpha_composite(with_alpha(sp,za*fl))
            if za>0.5:
                d=ImageDraw.Draw(im);d.text((ax+40,km(90)+20),"붉은 번개 50~90km",font=f(58),fill=YEL+(255,),stroke_width=4,stroke_fill=(0,0,0,255))
        im.alpha_composite(cloud);d=ImageDraw.Draw(im)
        # lightning flicker in cloud
        if int(t*5)%3==0:
            for x0 in (560,760):d.line([(x0,km(6)),(x0-25,km(3.5)),(x0+10,km(3)),(x0-20,km(0))],fill=(230,230,255,255),width=6)
        # airplane moving
        px=int(250+((t*120)%800));py=km(10)
        d.polygon([(px-70,py),(px+60,py-8),(px+70,py),(px+60,py+8)],fill=WHT);d.polygon([(px-5,py),(px-35,py-40),(px-20,py-40),(px+20,py)],fill=WHT);d.polygon([(px-5,py),(px-35,py+40),(px-20,py+40),(px+20,py)],fill=WHT)
        d.text((px-90,py+50),"비행기 10km",font=f(40),fill=WHT,stroke_width=3,stroke_fill=(0,0,0))
        # rising marker + counter
        if t>0.8:
            y=km(lvl);d.line([(ax-6,y),(ax+120,y)],fill=YEL,width=6);d.text((ax+130,y),f"{lvl:.0f}km",font=f(56),fill=YEL,anchor="lm",stroke_width=4,stroke_fill=(0,0,0))
        d.rectangle((ax,km(0),W,H),fill=(10,12,18))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close();p.wait()
# ---------- 1925
def a1925():
    bg=grad((15,12,8),(40,30,20));p=writer("a1925")
    tx=text_layer([(1070,"1925",170,YEL,True,6),(1290,"이론으로만 예측",58,WHT,True,3)])
    for i in range(N):
        t=i/FPS;im=bg.copy().convert('RGBA');d=ImageDraw.Draw(im)
        a=ease(t/0.5);yo=int((1-a)*80)
        d.rounded_rectangle((140,90+yo,940,700+yo),30,fill=(240,232,210))
        for k in range(8):d.line([(200,170+k*66+yo),(880,170+k*66+yo)],fill=(200,190,170),width=2)
        for (cx,cy,r) in [(430,560,90),(540,540,110),(650,565,85)]:d.ellipse((cx-r,cy-r*0.55+yo,cx+r,cy+r*0.55+yo),fill=(110,110,120))
        # pencil arrow drawing up
        g=ease((t-0.6)/1.0);top=470-140*g
        if g>0:d.line([(540,470+yo),(540,top+yo)],fill=(60,60,60),width=8)
        if g>=0.99:d.polygon([(515,340+yo),(565,340+yo),(540,300+yo)],fill=(60,60,60))
        # question mark pop + wobble
        q=ease((t-1.7)/0.35)
        if q>0:
            sz=int(150*(0.5+0.5*q)*(1+0.06*math.sin(t*6)));d.text((660,250+yo),"?",font=f(sz),fill=(200,40,40),anchor="mm")
        b=ease((t-0.3)/0.6);im.alpha_composite(with_alpha(tx,b))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close();p.wait()
# ---------- 1989 TV
def a1989():
    src=Image.open(SRC).convert('L');sw,sh=src.size;cr=src.crop((0,int(sh*0.05),sw,int(sh*0.05)+int(sw*640/660))).resize((620,600));cr=ImageOps.autocontrast(cr)
    tv=Image.new('RGBA',(W,H),(22,20,26,255));d=ImageDraw.Draw(tv)
    d.rounded_rectangle((90,60,990,800),50,fill=(70,58,45));d.rounded_rectangle((140,110,800,750),40,fill=(15,15,15))
    for yy in (220,360,500):d.ellipse((850,yy,930,yy+80),fill=(40,32,25))
    d.rectangle((300,800,340,860),fill=(50,40,30));d.rectangle((740,800,780,860),fill=(50,40,30))
    mask=Image.new('L',(620,600),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,620,600),40,fill=255)
    tx=text_layer([(1070,"1989",170,YEL,True,6),(1290,"카메라 시험 중 우연히",58,WHT,True,3)])
    dark=Image.new('L',(620,600),20);p=writer("a1989")
    for i in range(N):
        t=i/FPS;im=tv.copy();noise=Image.effect_noise((620,600),70).convert('L')
        # sprite appears briefly at 1.6s, then replays slowly from 3.0s and holds
        if abs(t-1.6)<0.12: k=1.0
        elif t>3.0: k=ease((t-3.0)/1.2)
        else: k=0.0
        base=Image.blend(dark,cr,k);fr=Image.blend(base,noise,0.28 if k>0 else 0.55)
        im.paste(Image.merge('RGB',(fr,fr,fr)),(160,130),mask);d=ImageDraw.Draw(im)
        for y in range(130,730,6):d.line([(160,y),(780,y)],fill=(0,0,0),width=1)
        if int(t*2)%2==0:d.text((175,145),"REC ●",font=f(34),fill=(255,60,60))
        sec=int(t*30)%30;d.text((480,690),f"1989.07  00:{int(t):02d}:{sec:02d}",font=f(30,False),fill=WHT)
        if t>3.0:d.text((175,690),"▶ 느리게",font=f(30,False),fill=YEL)
        d.text((820,770),"재현 그래픽",font=f(26,False),fill=(200,190,170))
        b=ease((t-0.2)/0.6);im.alpha_composite(with_alpha(tx,b))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close();p.wait()
for fn in sys.argv[3:]: globals()[fn]();print('done',fn)
