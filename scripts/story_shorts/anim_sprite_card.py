# 흰 카드형(오늘의쓸모) 영상 칸용 움직이는 그래픽 — anim_sprite_example.py 를 1080x860 칸에 맞게 옮긴 판(2026.10.18).
# 사용: python3 scripts/story_shorts/anim_sprite_card.py media/<id>/video <참고프레임.jpg> a1886 aalt a1925 a1989  → <이름>_card.mp4
# 자막은 카드의 영상 칸 아래에 따로 들어가므로 그래픽 안에는 연도·짧은 설명만 둔다.
import random,math,sys,subprocess
from PIL import Image,ImageDraw,ImageFilter,ImageFont,ImageOps,ImageChops
OUT=sys.argv[1]; SRC=sys.argv[2]
W,H,FPS,DUR=1080,860,30,7.0
N=int(FPS*DUR)
FB="/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc";FM="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
f=lambda s,b=True:ImageFont.truetype(FB if b else FM,s)
YEL=(255,212,59);WHT=(255,255,255)
ease=lambda t:0 if t<=0 else 1 if t>=1 else 1-(1-t)**3
def writer(name):
    return subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-c:v","libx264","-crf","18","-pix_fmt","yuv420p",f"{OUT}/{name}_card.mp4"],stdin=subprocess.PIPE)
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
# ---------- 1886: 밤하늘에 붉은 번개가 번쩍 → 사람이 하늘을 가리킴
def a1886():
    bg=grad((8,10,30),(25,20,45));st=stars(2,150,0.8);sp=sprite_layer(720,200,0.8,5)
    gr=Image.new('RGBA',(W,H),(0,0,0,0));gd=ImageDraw.Draw(gr);r=random.Random(7);pts=[(0,H)]
    for x in range(0,W+60,60):pts.append((x,770+r.randrange(-25,25)))
    pts.append((W,H));gd.polygon(pts,fill=(5,5,10,255))
    tx=text_layer([(500,"1886",150,YEL,True,6),(670,"첫 목격 기록 · 증거는 없음",48,WHT,True,3)])
    p=writer("a1886")
    for i in range(N):
        t=i/FPS;im=bg.copy().convert('RGBA');d=ImageDraw.Draw(im);draw_stars(d,st,t)
        fl=max(0,1-abs(t-1.0)/0.18)+max(0,1-abs(t-3.6)/0.18)+0.25*max(0,1-abs(t-5.6)/0.25)
        if fl>0: im=Image.alpha_composite(im,with_alpha(sp,min(1,fl)))
        im=Image.alpha_composite(im,gr);d=ImageDraw.Draw(im)
        x,y,s=120,800,1.2;d.ellipse((x-14*s,y-110*s,x+14*s,y-82*s),fill=(0,0,0));d.rounded_rectangle((x-20*s,y-82*s,x+20*s,y-20*s),8,fill=(0,0,0))
        d.rectangle((x-16*s,y-22*s,x-4*s,y),fill=(0,0,0));d.rectangle((x+4*s,y-22*s,x+16*s,y),fill=(0,0,0))
        ang=math.radians(-20+ease((t-1.1)/0.5)*85);d.line([(x+16*s,y-76*s),(x+16*s+48*s*math.cos(ang),y-76*s-48*s*math.sin(ang))],fill=(0,0,0),width=int(9*s))
        a=ease((t-0.2)/0.6);ty=int((1-a)*50);tl=with_alpha(tx,a);im.alpha_composite(tl,(0,0)) if ty==0 else im.alpha_composite(tl.crop((0,0,W,H-ty)),(0,ty))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close();p.wait()
# ---------- 높이: 0→90km 눈금이 올라가며 50~90km 붉은 구역, 비행기는 10km
def aalt():
    bg=grad((5,5,25),(30,40,80));st=stars(4,80,0.9);km=lambda k:int(790-k*7.3);ax=130
    sp=sprite_layer(640,km(86),1.1,9)
    base=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(base)
    d.line([(ax,km(0)),(ax,km(100))],fill=(200,200,200,255),width=4)
    for k in range(0,101,10):
        d.line([(ax-14,km(k)),(ax,km(k))],fill=(200,200,200,255),width=3);d.text((ax-26,km(k)),f"{k}",font=f(26,False),fill=(200,200,200,255),anchor="rm")
    d.text((ax+14,km(100)),"km",font=f(26,False),fill=(200,200,200,255),anchor="lm")
    cloud=Image.new('RGBA',(W,H),(0,0,0,0));cd=ImageDraw.Draw(cloud)
    for (cx,cy,r) in [(520,km(12),105),(650,km(14),120),(780,km(11),95),(410,km(9),80),(880,km(8),75)]:cd.ellipse((cx-r,cy-r*0.55,cx+r,cy+r*0.55),fill=(70,75,95,255))
    cd.text((ax+26,km(19)-6),"번개 구름 ~15km",font=f(38),fill=WHT+(255,),stroke_width=3,stroke_fill=(0,0,0,255))
    p=writer("aalt")
    for i in range(N):
        t=i/FPS;im=bg.copy().convert('RGBA');d=ImageDraw.Draw(im);draw_stars(d,st,t);im.alpha_composite(base)
        lvl=ease((t-0.8)/2.6)*90
        if lvl>50:
            za=min(1,(lvl-50)/15);zone=Image.new('RGBA',(W,H),(0,0,0,0));ImageDraw.Draw(zone).rectangle((ax+10,km(90),W-30,km(50)),fill=(120,10,20,int(200*za)));im.alpha_composite(zone)
            fl=0.6+0.4*abs(math.sin(t*7)) if t>3.4 else za
            im.alpha_composite(with_alpha(sp,za*fl))
            if za>0.5:
                d=ImageDraw.Draw(im);d.text((ax+300,km(55)),"붉은 번개 50~90km",font=f(50),fill=YEL+(255,),stroke_width=4,stroke_fill=(0,0,0,255),anchor="lm")
        im.alpha_composite(cloud);d=ImageDraw.Draw(im)
        if int(t*5)%3==0:
            for x0 in (560,740):d.line([(x0,km(7)),(x0-20,km(4)),(x0+8,km(3)),(x0-16,km(0))],fill=(230,230,255,255),width=5)
        px=int(250+((t*120)%760));py=km(10)
        d.polygon([(px-55,py),(px+48,py-7),(px+56,py),(px+48,py+7)],fill=WHT);d.polygon([(px-4,py),(px-28,py-32),(px-16,py-32),(px+16,py)],fill=WHT);d.polygon([(px-4,py),(px-28,py+32),(px-16,py+32),(px+16,py)],fill=WHT)
        d.text((px-70,py+30),"비행기 10km",font=f(32),fill=WHT,stroke_width=3,stroke_fill=(0,0,0))
        if t>0.8:
            y=km(lvl);d.line([(ax-6,y),(ax+100,y)],fill=YEL,width=6);d.text((ax+110,y),f"{lvl:.0f}km",font=f(48),fill=YEL,anchor="lm",stroke_width=4,stroke_fill=(0,0,0))
        d.rectangle((0,km(0)+6,W,H),fill=(10,12,18))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close();p.wait()
# ---------- 1925: 공책 위 구름에서 위로 화살표 → 물음표
def a1925():
    bg=grad((15,12,8),(40,30,20));p=writer("a1925")
    tx=text_layer([(520,"1925",150,YEL,True,6),(690,"이론으로만 예측",50,WHT,True,3)])
    for i in range(N):
        t=i/FPS;im=bg.copy().convert('RGBA');d=ImageDraw.Draw(im)
        a=ease(t/0.5);yo=int((1-a)*60)
        d.rounded_rectangle((200,30+yo,880,480+yo),26,fill=(240,232,210))
        for k in range(6):d.line([(250,95+k*62+yo),(830,95+k*62+yo)],fill=(200,190,170),width=2)
        for (cx,cy,r) in [(440,400,75),(540,385,92),(640,405,72)]:d.ellipse((cx-r,cy-r*0.55+yo,cx+r,cy+r*0.55+yo),fill=(110,110,120))
        g=ease((t-0.6)/1.0);top=330-120*g
        if g>0:d.line([(540,330+yo),(540,top+yo)],fill=(60,60,60),width=7)
        if g>=0.99:d.polygon([(518,215+yo),(562,215+yo),(540,180+yo)],fill=(60,60,60))
        q=ease((t-1.7)/0.35)
        if q>0:
            sz=int(130*(0.5+0.5*q)*(1+0.06*math.sin(t*6)));d.text((660,160+yo),"?",font=f(sz),fill=(200,40,40),anchor="mm")
        b=ease((t-0.3)/0.6);im.alpha_composite(with_alpha(tx,b))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close();p.wait()
# ---------- 1989: 옛날 TV 속 시험 화면에 우연히 찍힘(재현 그래픽)
def a1989():
    sw_,sh_=480,450
    src=Image.open(SRC).convert('L');sw,sh=src.size;cr=src.crop((0,int(sh*0.05),sw,int(sh*0.05)+int(sw*sh_/sw_))).resize((sw_,sh_));cr=ImageOps.autocontrast(cr)
    tv=Image.new('RGBA',(W,H),(22,20,26,255));d=ImageDraw.Draw(tv)
    d.rounded_rectangle((190,20,890,560),40,fill=(70,58,45));d.rounded_rectangle((225,50,745,530),32,fill=(15,15,15))
    for yy in (130,250,370):d.ellipse((785,yy,855,yy+70),fill=(40,32,25))
    d.rectangle((330,560,365,600),fill=(50,40,30));d.rectangle((715,560,750,600),fill=(50,40,30))
    mask=Image.new('L',(sw_,sh_),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,sw_,sh_),30,fill=255)
    tx=text_layer([(600,"1989",130,YEL,True,6),(750,"카메라 시험 중 우연히",46,WHT,True,3)])
    dark=Image.new('L',(sw_,sh_),20);p=writer("a1989")
    for i in range(N):
        t=i/FPS;im=tv.copy();noise=Image.effect_noise((sw_,sh_),70).convert('L')
        if abs(t-1.6)<0.12: k=1.0
        elif t>3.0: k=ease((t-3.0)/1.2)
        else: k=0.0
        base=Image.blend(dark,cr,k);fr=Image.blend(base,noise,0.28 if k>0 else 0.55)
        im.paste(Image.merge('RGB',(fr,fr,fr)),(245,65),mask);d=ImageDraw.Draw(im)
        for y in range(65,515,6):d.line([(245,y),(725,y)],fill=(0,0,0),width=1)
        if int(t*2)%2==0:d.text((260,78),"REC ●",font=f(30),fill=(255,60,60))
        sec=int(t*30)%30;d.text((470,478),f"1989.07  00:{int(t):02d}:{sec:02d}",font=f(26,False),fill=WHT)
        if t>3.0:d.text((260,478),"▶ 느리게",font=f(26,False),fill=YEL)
        d.text((760,525),"재현 그래픽",font=f(24,False),fill=(200,190,170))
        b=ease((t-0.2)/0.6);im.alpha_composite(with_alpha(tx,b))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close();p.wait()
for fn in sys.argv[3:]: globals()[fn]();print('done',fn)
