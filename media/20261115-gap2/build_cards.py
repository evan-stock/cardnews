import subprocess
exec(open('/tmp/brkscripts/frame_cards.py').read().split('\nframe((')[0])
from PIL import Image, ImageDraw
G=Path('/home/claude/cardnews/media/20261115-gap'); GO=G/'cand'
frame(("1차는 감독관 바로 앞자리 다음", "2차는 감독관 '바로 앞'에서 시험"), GO/"yt_fool.jpg",
      "감독관 4명 모두 \"특이사항 없었다\"", sub="한국산업인력공단 설명 (11월 13일)", focus=(.5,.5)).save(GO/"f02.jpg", quality=95)
frame(("1차 시험장엔 CCTV '없었다'", "2차는 있었지만 '보존 기간 지나'"), GO/"pass_cert.jpg",
      "당시 영상으로 확인할 길이 없다", sub="국민일보 11.15 보도 · 사진은 본인이 블로그에 올린 합격 확인서", focus=(.5,.35)).save(GO/"f03.jpg", quality=95)
# 5장: 본인 경고 영상
PH=760; src=str(D/'video/v1.mp4')
card=frame(("수능을 나흘 앞두고", "본인이 남긴 '경고'"), Image.new('RGB',(940,PH)), "\"'난 안 걸리겠지'라는 생각을 하지 않으셨으면\"",
           sub="11월 15일 유튜브 '이돈호 변호사' 영상", ph=PH).convert('RGBA')
m=Image.new('L',(940,PH),0); ImageDraw.Draw(m).rounded_rectangle((0,0,939,PH-1),18,fill=255)
hole=Image.new('L',(W,H),255); hole.paste(Image.eval(m,lambda v:255-v),(70,300)); card.putalpha(hole); card.save('/tmp/brk/gap5.png')
card.convert('RGB').save(GO/'card5_still.jpg')
subprocess.run(['ffmpeg','-v','error','-y','-ss','141.8','-t','19.9','-i',src,'-i','/tmp/brk/gap5.png','-filter_complex',
 'color=c=0x0a0a0c:s=1080x1350:r=30[bg];[0:v]crop=628:508:46:426,scale=940:760:flags=lanczos,unsharp=5:5:0.5[v];[bg][v]overlay=70:300:shortest=1[t];[t][1:v]overlay=0:0,format=yuv420p[o]',
 '-map','[o]','-map','0:a','-c:v','libx264','-crf','19','-preset','veryfast','-c:a','aac','-b:a','128k','-movflags','+faststart',str(G/'video/card5.mp4')],check=True)
print('ok')
