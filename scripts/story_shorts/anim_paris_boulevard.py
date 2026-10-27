"""파리 대로 재현 그래픽: 좁은 골목+바리케이드 → 사라짐 → 별 모양 대로가 뻗고 군대 점이 빠르게 이동. 1080x900, 7.5초."""
import math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
W,H,FPS,T=1080,900,30,7.5
F="/home/claude/cardnews/assets/fonts/Pretendard-Black.otf"
out_dir, out = sys.argv[1], sys.argv[2]
random.seed(7)
BG=(18,22,30); GRAY=(120,128,140); YEL=(255,212,59); RED=(235,60,60); BLUE=(90,170,255); WHITE=(255,255,255)
cx,cy=540,430
# 골목: 짧게 꺾이는 선들
alleys=[]
for _ in range(70):
    x,y=random.uniform(40,1040),random.uniform(40,800); pts=[(x,y)]
    for _ in range(random.randint(3,6)):
        a=random.uniform(0,2*math.pi); L=random.uniform(30,80); x+=L*math.cos(a); y+=L*math.sin(a); pts.append((x,y))
    alleys.append(pts)
bars=[(random.uniform(120,960),random.uniform(100,760)) for _ in range(9)]
rays=[i*2*math.pi/12+0.13 for i in range(12)]
f_lab=ImageFont.truetype(F,52); f_small=ImageFont.truetype(F,28)
ease=lambda t: 0 if t<=0 else 1 if t>=1 else 1-(1-t)**3
def frame(t):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im,"RGBA")
    fade=1-ease((t-2.6)/0.8)  # 골목 사라짐
    if fade>0:
        a=int(255*fade)
        for k,pts in enumerate(alleys):
            p=min(1,ease((t-k*0.012)/0.5)); n=max(2,int(len(pts)*p))
            d.line(pts[:n],fill=GRAY+(a,),width=5,joint="curve")
        for k,(x,y) in enumerate(bars):
            s=ease((t-0.9-k*0.1)/0.25)*22
            if s>0:
                d.line((x-s,y-s,x+s,y+s),fill=RED+(a,),width=9); d.line((x-s,y+s,x+s,y-s),fill=RED+(a,),width=9)
        d.text((W//2,830),"좁은 골목 + 바리케이드",font=f_lab,fill=WHITE+(a,),anchor="mm",stroke_width=5,stroke_fill=(0,0,0,a))
    g=ease((t-3.2)/1.4)  # 대로 뻗기
    if g>0:
        R=900*g
        for a_ in rays:
            d.line((cx,cy,cx+R*math.cos(a_),cy+R*math.sin(a_)),fill=YEL,width=26)
        r=60*min(1,g*2); d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=BG,outline=YEL,width=14)
        al=int(255*ease((t-3.8)/0.4))
        d.text((W//2,830),"넓고 곧은 대로",font=f_lab,fill=WHITE+(al,),anchor="mm",stroke_width=5,stroke_fill=(0,0,0,al))
    m=t-4.9  # 군대 점 이동
    if m>0:
        for j,a_ in enumerate(rays[::3]):
            for q in range(4):
                dist=(m*260+q*45-j*20)%620+80
                x,y=cx+dist*math.cos(a_),cy+dist*math.sin(a_)
                d.ellipse((x-11,y-11,x+11,y+11),fill=BLUE,outline=(255,255,255),width=3)
    d.text((24,20),"재현 그래픽",font=f_small,fill=(200,200,200,200))
    return im
n=int(T*FPS)
for i in range(n):
    frame(i/FPS).save(f"{out_dir}/f{i:04d}.png")
subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{out_dir}/f%04d.png","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",out],check=True)
