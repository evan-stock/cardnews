"""20261116-haircam-reel: 머리카락 굵기 카메라. 선 끝(카메라)을 노란 화살표+라벨로 따라가며 표시."""
import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 24
K = [(0,507,923),(0.75,515,977),(1.5,499,857),(2.25,693,1043),(3.0,515,990),(3.75,413,1030),(4.5,488,1003),
     (5.25,541,990),(6.0,595,1030),(6.75,632,950),(7.5,680,995),(7.7,680,995)]
def tip(t):
    for (t0,x0,y0),(t1,x1,y1) in zip(K,K[1:]):
        if t0<=t<=t1:
            a=(t-t0)/(t1-t0); a=a*a*(3-2*a); return x0+(x1-x0)*a, y0+(y1-y0)*a
    return K[-1][1:]
ov = Image.open("cand/overlay.png").convert("RGBA")
font = ImageFont.truetype("../../assets/fonts/Pretendard-Black.otf", 54)
dec = subprocess.Popen(["ffmpeg","-v","error","-i","src/orig.mp4","-vf","scale=1080:-2:flags=lanczos,crop=1080:1920,unsharp=5:5:0.6",
                        "-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
                        "-i","src/orig.mp4","-map","0:v","-map","1:a?","-c:v","libx264","-preset","veryfast","-crf","18",
                        "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart","video/v2.mp4"], stdin=subprocess.PIPE)
n=0
while True:
    buf = dec.stdout.read(W*H*3)
    if len(buf) < W*H*3: break
    im = Image.frombytes("RGB",(W,H),buf).convert("RGBA")
    x,y = tip(n/FPS); d = ImageDraw.Draw(im)
    # 라벨(노란 알약) + 화살표: 라벨 → 선 끝
    tw = d.textlength("이게 카메라", font=font)
    lx, ly = min(x+150, W-40-tw-44), y-170
    d.rounded_rectangle((lx, ly, lx+tw+44, ly+80), 40, fill=(255,216,77,255), outline=(0,0,0,255), width=4)
    d.text((lx+22, ly+40), "이게 카메라", font=font, fill=(0,0,0), anchor="lm")
    sx, sy = lx+40, ly+80; ex, ey = x+14, y-12
    for wdt,col in ((18,(0,0,0,255)),(10,(255,216,77,255))):
        d.line((sx,sy,ex,ey), fill=col, width=wdt)
        v=np.array([ex-sx,ey-sy],float); v/=np.linalg.norm(v); p=np.array([-v[1],v[0]])
        hl = 46 if wdt==18 else 38; hw = 30 if wdt==18 else 22
        b=np.array([ex,ey])-v*hl
        d.polygon([(ex+v[0]*(6 if wdt==18 else 0),ey+v[1]*(6 if wdt==18 else 0)),tuple(b+p*hw),tuple(b-p*hw)], fill=col)
    im.alpha_composite(ov)
    enc.stdin.write(im.convert("RGB").tobytes()); n+=1
enc.stdin.close(); enc.wait(); print("frames", n)
# 커버: 4.5초 프레임 + 표시
subprocess.run(["ffmpeg","-v","error","-y","-ss","4.5","-i","video/v2.mp4","-frames:v","1","-q:v","2","cand/reel_cover_final.jpg"])
