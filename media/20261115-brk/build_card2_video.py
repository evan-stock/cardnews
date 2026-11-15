import sys, subprocess
sys.argv=['x']
exec(open('/tmp/brkscripts/frame_cards.py').read().split('\nframe((')[0])  # helpers only
from PIL import Image, ImageDraw
PH=760
dummy=Image.new('RGB',(940,PH),(0,0,0))
card=frame(("11월 15일 본인 영상에서", "\"생성형 AI를 이용해 '부정행위'를 했습니다\""), dummy,
      "수석 합격은 '정당한 노력'이 아니었다", sub="마스크 쓰고 직접 출연 (유튜브 '이돈호 변호사')", ph=PH).convert('RGBA')
m=Image.new('L',(940,PH),0); ImageDraw.Draw(m).rounded_rectangle((0,0,939,PH-1),18,fill=255)
a=card.split()[3].copy(); hole=Image.new('L',(W,H),255); hole.paste(Image.eval(m,lambda v:255-v),(70,300))
card.putalpha(hole); card.save('/tmp/brk/card2_base.png')
src=str(D/'video/v1.mp4'); out=str(D/'video/card2.mp4')
# 영상 영역(46,370 시작 628x785) 중 얼굴+자막(출처 알약 제외): y 376+... 비율 940:760
ch=round(628*PH/940)  # 508
y0=370+568-ch-4        # 알약(568) 바로 위에서 끝나게
subprocess.run(['ffmpeg','-v','error','-y','-ss','28','-t','28.5','-i',src,'-i','/tmp/brk/card2_base.png',
 '-filter_complex',f'color=c=0x0a0a0c:s=1080x1350:r=30[bg];[0:v]crop=628:{ch}:46:{y0},scale=940:{PH}:flags=lanczos,unsharp=5:5:0.5[v];[bg][v]overlay=70:300:shortest=1[t];[t][1:v]overlay=0:0,format=yuv420p[o]',
 '-map','[o]','-map','0:a','-c:v','libx264','-crf','19','-preset','veryfast','-c:a','aac','-b:a','128k','-movflags','+faststart',out],check=True)
print(out, y0)
