"""영상 캐러셀 장: 검은 바탕 + 노란 소제목·굵은 제목(위) + 원본 영상 가로 1080 꽉(가운데, 원본 자막·소리 그대로) + 출처 + 하단 로고"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw
R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "scripts"))
from video_cap_card import F, W, H, BG, YE, MU, wrap, fix_quotes, draw_rich_center, logo  # noqa
B = Path(__file__).resolve().parent
VW, VH, VY = 1080, 608, 470
SRC = "영상: 이돈호 변호사 유튜브(11.27)"
def card(sub, title, out):
    im = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(im)
    ft = F("Black", 54); fs = F("SemiBold", 32)
    tl = fix_quotes(wrap(d, title, ft, 960))
    y_end = VY - 50  # 제목 마지막 줄 바닥
    y0 = y_end - 52 - 73 * (len(tl) - 1)
    for i, ln in enumerate(tl):
        draw_rich_center(d, W / 2, y0 + i * 73, ln, ft)
    if sub:
        w = d.textlength(sub, font=fs); d.text((W / 2 - w / 2, y0 - 62), sub, font=fs, fill=YE)
    f2 = F("Medium", 22); tw = d.textlength(SRC, font=f2)
    d.text((W - 30 - tw, VY + VH + 14), SRC, font=f2, fill=MU)
    d.rectangle((0, VY, VW - 1, VY + VH - 1), fill=(0, 0, 0, 0))
    logo(im, 0, H - 78, 40, center=True)
    im.save(out)
for s in json.load(open(B / "vids.json")):
    png = B / "cand" / (s["name"] + "_ov.png"); card(s.get("sub"), s["title"], png)
    out = B / "video" / (s["name"] + ".mp4")
    segs = s["segs"]  # [[src,start,end],...]
    ins, fc = [], []
    for i, (src, a, b) in enumerate(segs):
        ins += ["-ss", str(a), "-t", str(b - a), "-i", str(R / src)]
        fc.append(f"[{i}:v]scale={VW}:{VH},setsar=1,fps=30[v{i}];[{i}:a]aresample=48000[a{i}]")
    n = len(segs)
    fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vv][aa]")
    fc.append(f"color=c=0x0c0c0e:s={W}x{H}:r=30[bg];[bg][vv]overlay=0:{VY}:shortest=1[x];[x][{n}:v]overlay=0:0,format=yuv420p,setpts=PTS-STARTPTS[o];[aa]asetpts=PTS-STARTPTS[ao]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-i", str(png), "-filter_complex", ";".join(fc),
                    "-map", "[o]", "-map", "[ao]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-profile:v", "high",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-use_editlist", "0", "-movflags", "+faststart", str(out)], check=True)
    print(out)
