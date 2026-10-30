import sys; sys.path.insert(0,'scripts')
from mag_cover import *
from PIL import Image, ImageDraw, ImageOps
src=Image.open(sys.argv[1]).convert('RGB'); mode=sys.argv[2]; out=sys.argv[3]
cell=10
g=ImageOps.autocontrast(ImageOps.grayscale(fill(src,0.5,0.1)),cutoff=2)
sm=g.resize((W//cell,H//cell))
dark = mode=='dark'
o=Image.new('RGB',(W,H),(12,12,12) if dark else (245,243,236)); d=ImageDraw.Draw(o)
for yy in range(sm.height):
  for xx in range(sm.width):
    v=sm.getpixel((xx,yy))/255
    r=(v if dark else 1-v)*cell*0.7
    if r>0.4:
      cx,cy=xx*cell+cell/2,yy*cell+cell/2
      d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(235,235,235) if dark else (20,20,20))
f=font(FB,300)
if dark:
  d.text((W//2,30),'-30%',font=f,fill=Y,anchor='ma')
else:
  tw=d.textlength('-30%',font=f); d.rectangle((W//2-tw/2-30,60,W//2+tw/2+30,400),fill=Y)
  d.text((W//2,70),'-30%',font=f,fill=(15,15,15),anchor='ma')
o.save(out,quality=95)
