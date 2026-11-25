# 표지: 김남국(왼쪽) + 비트코인 차트(오른쪽) 가로로 겹치기
from PIL import Image, ImageFilter
W,H=1080,1350
PH=1010  # 사진 높이(덜 확대)
def fit_h(p,cx_src,cx_dst):
    im=Image.open(p).convert('RGB'); s=PH/im.height
    im=im.resize((round(im.width*s),PH),Image.LANCZOS)
    x0=max(0,min(im.width-W,round(cx_src*s)-cx_dst)); return im.crop((x0,0,x0+W,PH))
kim=fit_h('cand/kim_hd.png',650,330)
btc=fit_h('cand/btc.jpg',712,830)
mask=Image.new('L',(W,PH)); px=mask.load()
a,b=560,860   # 이 구간에서 김남국→비트코인으로 넘어감
for x in range(W):
    v=255 if x<a else 0 if x>b else int(255*(1-(x-a)/(b-a)))
    for y in range(PH): px[x,y]=v
top=btc.copy(); top.paste(kim,(0,0),mask)
out=Image.new('RGB',(W,H),'black')
vm=Image.new('L',(W,PH),255); vp=vm.load()
for y in range(760,PH):
    v=int(255*(1-(y-760)/(PH-760)))
    for x in range(W): vp[x,y]=v
out.paste(top,(0,0),vm); out.save('cand/cover.jpg',quality=95)
