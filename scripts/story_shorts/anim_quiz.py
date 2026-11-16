"""오늘의쓸모 퀴즈형 그래픽(영상 칸 1080x780).
python3 scripts/story_shorts/anim_quiz.py <spec.json> <out_dir>
spec: {"q": "...", "opts": ["①..","②..","③.."], "answer": 2, "pick": 0, "q_dur": 6.0, "a_dur": 3.0}
quiz_q.mp4 = 보기 등장 → 3·2·1 카운트다운 → (pick 보기에 '많이 고르는 답' 표시)
quiz_a.mp4 = 정답만 노랑, 나머지 흐리게"""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import card_render as cr
from PIL import Image, ImageDraw

W, H, FPS = 1080, 780, 30
BG, DIM_BG, DIM_TX = (24, 24, 28), (45, 45, 50), (110, 110, 110)


def frame(sp, t, mode):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 90), sp["q"], font=cr.font(60, True), fill="white", anchor="mm")
    of = cr.font(54, True)
    for i, txt in enumerate(sp["opts"]):
        y0 = 190 + i * 160
        if mode == "q":
            a = min(1.0, max(0.0, (t - 0.25 * i) / 0.25))  # 하나씩 등장
            if a <= 0:
                continue
            dx = int((1 - a) * 60)
            fill, tx = (255, 255, 255), cr.INK
            box = [90 + dx, y0, W - 90 + dx, y0 + 124]
            d.rounded_rectangle(box, radius=28, fill=fill)
            if t >= 3.6 and i == sp.get("pick", 0):
                d.rounded_rectangle(box, radius=28, outline=(230, 60, 60), width=8)
                d.text((W - 130 + dx, y0 + 62), "많이 고르는 답", font=cr.font(36, True), fill=(230, 60, 60), anchor="rm")
            d.text((140 + dx, y0 + 62), txt, font=of, fill=tx, anchor="lm")
        else:
            hit = i == sp["answer"]
            s = 1.0 + (0.04 * min(1, t / 0.15) if hit and t < 0.45 else 0)
            pad = int((s - 1) * 450)
            box = [90 - pad, y0 - pad // 4, W - 90 + pad, y0 + 124 + pad // 4]
            d.rounded_rectangle(box, radius=28, fill=cr.YEL if hit else DIM_BG)
            d.text((140, y0 + 62), txt, font=of, fill=cr.INK if hit else DIM_TX, anchor="lm")
            if hit:
                d.text((W - 140, y0 + 62), "정답", font=cr.font(46, True), fill=cr.INK, anchor="rm")
    if mode == "q" and t < 3.6:
        n = 3 - int(t / 1.2)
        k = (t % 1.2) / 1.2
        r = int(60 * (1.15 - 0.15 * min(1, k * 4)))
        d.ellipse([W // 2 - r, 700 - r, W // 2 + r, 700 + r], fill=cr.YEL)
        d.text((W // 2, 700), str(n), font=cr.font(64, True), fill=cr.INK, anchor="mm")
    return im


def make(sp, mode, dur, out):
    with tempfile.TemporaryDirectory() as tmp:
        for f in range(int(dur * FPS)):
            frame(sp, f / FPS, mode).save(f"{tmp}/{f:04d}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%04d.png",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], check=True)


if __name__ == "__main__":
    sp = json.load(open(sys.argv[1]))
    os.makedirs(sys.argv[2], exist_ok=True)
    make(sp, "q", sp.get("q_dur", 6.0), os.path.join(sys.argv[2], "quiz_q.mp4"))
    make(sp, "a", sp.get("a_dur", 3.0), os.path.join(sys.argv[2], "quiz_a.mp4"))
