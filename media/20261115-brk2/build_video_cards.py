import subprocess
exec(open('/tmp/brkscripts/frame_cards.py').read().split('\nframe((')[0])  # 도우미 함수만
from PIL import Image, ImageDraw
PH=760; src=str(D/'video/v1.mp4')
def vcard(top, bottom, sub, t0, t1, name):
    card=frame(top, Image.new('RGB',(940,PH)), bottom, sub=sub, ph=PH).convert('RGBA')
    m=Image.new('L',(940,PH),0); ImageDraw.Draw(m).rounded_rectangle((0,0,939,PH-1),18,fill=255)
    hole=Image.new('L',(W,H),255); hole.paste(Image.eval(m,lambda v:255-v),(70,300)); card.putalpha(hole)
    base=f'/tmp/brk/{name}_base.png'; card.save(base)
    card.convert('RGB').save(O/f'{name}_still.jpg')
    out=str(D/f'video/{name}.mp4')
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t0),'-t',str(round(t1-t0,2)),'-i',src,'-i',base,
     '-filter_complex','color=c=0x0a0a0c:s=1080x1350:r=30[bg];[0:v]crop=628:508:46:426,scale=940:760:flags=lanczos,unsharp=5:5:0.5[v];[bg][v]overlay=70:300:shortest=1[t];[t][1:v]overlay=0:0,format=yuv420p[o]',
     '-map','[o]','-map','0:a','-c:v','libx264','-crf','19','-preset','veryfast','-c:a','aac','-b:a','128k','-movflags','+faststart',out],check=True)
    print(name, round(t1-t0,1))
vcard(("11월 15일 본인 영상에서", "\"생성형 AI를 이용해 '부정행위'를 했습니다\""), "수석 합격은 '정당한 노력'이 아니었다",
      "마스크 쓰고 직접 출연 (유튜브 '이돈호 변호사')", 39.0, 52.0, "card2")
vcard(("알려진 'AI 안경'이 아니라", "'초소형 카메라'로 찍어 AI에 보냈다"), "남은 기기는 '증거물'로 제출",
      "답은 스마트폰으로 확인 · 구체적 과정은 모방 우려로 비공개", 115.4, 124.0, "card3")
vcard(("14일엔 \"공부를 왜 하겠느냐\"더니", "'하루 만에' 자수"), "\"거짓말로 제 행동을 부정했습니다\"",
      "14일 인터뷰에선 \"AI 안경으로 이걸 맞힐 수 있으면\" 반문", 56.9, 77.5, "card4")
vcard(("세무사 1·2차만이 아니었다", "공인회계사 1차도 '같은 방식'"), "\"같은 방식으로 부정행위를 했습니다\"",
      "이돈호 변호사, 수법은 수사기관에 있는 그대로 설명하기로", 51.8, 57.1, "card6")
