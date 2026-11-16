from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys
import os
S=os.environ.get('OUT','.')
FM='assets/fonts/Pretendard-Medium.otf';FB='assets/fonts/Pretendard-Black.otf'
W,H=1080,1920
def cover(frame,l1,l2,tag=None,circle=None,logo='brand/logo_typo_A.png',cut=0.60,zoom=1.0,cy=0.0):
    im=Image.open(frame).convert('RGB')
    top=im.crop((0,0,W,int(H*cut)))
    if zoom!=1.0:
        z=top.resize((int(W*zoom),int(top.height*zoom)),Image.LANCZOS);x0=(z.width-W)//2;y0=int((z.height-top.height)*cy);top=z.crop((x0,y0,x0+W,y0+top.height))
    c=Image.new('RGB',(W,H),(6,6,8));c.paste(top,(0,0))
    ov=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(ov)
    g0=int(H*(cut-0.16))
    for y in range(g0,H):
        t=max(0,min(1,(y-g0)/(H*cut-g0)));d.line([(0,y),(W,y)],fill=(6,6,8,int(255*t**1.3)))
    c=Image.alpha_composite(c.convert('RGBA'),ov);d=ImageDraw.Draw(c)
    if circle:
        x,y,r=circle;glow=Image.new('RGBA',(W,H),(0,0,0,0));gd=ImageDraw.Draw(glow);gd.ellipse((x-r,y-r,x+r,y+r),outline=(255,40,40,200),width=30);glow=glow.filter(ImageFilter.GaussianBlur(18))
        c=Image.alpha_composite(c,glow);d=ImageDraw.Draw(c);d.ellipse((x-r,y-r,x+r,y+r),outline=(255,42,42,255),width=16)
    M=W-160;sb=104
    while True:
        fb=ImageFont.truetype(FB,sb)
        if d.textlength(l2.replace("'",""),font=fb)<=M or sb<64:break
        sb-=2
    s1=int(sb*.56)
    while True:
        f1=ImageFont.truetype(FM,s1)
        if d.textlength(l1,font=f1)<=M or s1<34:break
        s1-=2
    base=1455  # 3:4 격자(240~1680) 안에 제목+로고
    runs=[];cur='';q=False
    for ch in l2:
        if ch=="'":runs.append((cur,q));cur='';q=not q
        else:cur+=ch
    runs.append((cur,q));tw=sum(d.textlength(r,font=fb) for r,_ in runs);x=(W-tw)/2
    for r,h in runs: d.text((x,base),r,font=fb,fill=(255,216,77) if h else (255,255,255),anchor='ls');x+=d.textlength(r,font=fb)
    y1=base-sb*1.12;d.text((W/2,y1),l1,font=f1,fill=(236,236,236),anchor='ms')
    if tag:
        tf=ImageFont.truetype('assets/fonts/Pretendard-SemiBold.otf',32);tw=d.textlength('● '+tag,font=tf)+36;ty=y1-s1-70
        d.rounded_rectangle(((W-tw)/2,ty,(W+tw)/2,ty+52),radius=10,fill=(228,30,40));d.text((W/2,ty+26),'● '+tag,font=tf,fill=(255,255,255),anchor='mm')
    lg=Image.open(logo).convert('RGBA');lh=60;lw=int(lg.width*lh/lg.height);lg=lg.resize((lw,lh),Image.LANCZOS);c.alpha_composite(lg,((W-lw)//2,1555))
    return c.convert('RGB')
if __name__=='__main__':
    c=cover(sys.argv[1] if len(sys.argv)>1 else 'frame.png',"9년 기다린 테슬라, 벽 타고 오르더니","'하늘을 날았다'",tag='실제 영상',circle=(585,520,165))
    c.save(f'{S}/reel_cover_new.jpg',quality=93)
    # 격자(3:4) 미리보기 + 릴스 화면 가림 영역 표시
    g=c.crop((0,240,1080,1680)).resize((300,400))
    ui=c.copy();d=ImageDraw.Draw(ui,'RGBA');d.rectangle((0,1540,1080,1920),fill=(255,0,90,70));d.rectangle((920,900,1080,1920),fill=(255,0,90,70))
    d.text((40,1800),'인스타 UI가 가리는 영역(재생 중)',font=ImageFont.truetype('assets/fonts/Pretendard-SemiBold.otf',38),fill=(255,255,255))
    out=Image.new('RGB',(540*2+40+300,960),(18,18,20));out.paste(c.resize((540,960)),(0,0));out.paste(ui.resize((540,960)),(560,0));out.paste(g,(1120,280))
    ImageDraw.Draw(out).text((1270,700),'격자에서 보이는 모습',font=ImageFont.truetype('assets/fonts/Pretendard-SemiBold.otf',26),fill=(200,200,200),anchor='mm')
    out.save(f'{S}/reel_cover_views.jpg',quality=90)
