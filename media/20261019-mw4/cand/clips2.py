import subprocess, sys
S = "/tmp/claude-0/-home-claude/d6776cdd-212a-5ebf-b82f-fed962dd0419/scratchpad"
SRC = {"g1": (f"{S}/g1xn.mp4", 12.012), "g2": (f"{S}/g2n.mp4", 48.0146), "g3": (f"{S}/g3n.mp4", 141.0075)}
# (group, abs start, abs end, crop center x) — absolute trailer times; cuts only where the trailer itself cuts
CLIPS = [
    # (group, abs start, abs end, crop center x, speed)
    ("g1", 13.15, 15.70, 0.50, 0.65),   # 네온 골목 한 컷, 천천히
    ("g1", 24.15, 26.10, 0.45, 0.80),   # 편의점 TV 한글 뉴스
    ("g1", 26.18, 28.58, 0.33, 1.00),   # 같은 편의점, 병사 대화
    ("g2", 51.30, 52.55, 0.40, 0.60),   # 폭발
    ("g3", 144.02, 145.85, 0.24, 0.70), # 호버크래프트 상륙
]
CW, CH, Y0 = 459, 816, 132
def crop(cx):
    x = max(0, min(1920 - CW, int(round(cx * 1920 - CW / 2))))
    return f"crop={CW}:{CH}:{x}:{Y0},scale=1080:1920:flags=lanczos"
mode = sys.argv[1]
if mode == "preview":
    outs = []
    for i, (g, s, e, cx, sp) in enumerate(CLIPS):
        f, off = SRC[g]
        for j, t in enumerate([s + 0.15, (s + e) / 2, e - 0.15]):
            o = f"{S}/q{i}{j}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t - off), "-i", f, "-vf", f"{crop(cx)},scale=180:320", "-frames:v", "1", o], check=True)
            outs.append(o)
    args = sum([["-i", o] for o in outs], [])
    n = len(outs)
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", "".join(f"[{i}]" for i in range(n)) + f"xstack=inputs={n}:layout=" + "|".join(f"{(i%3)*180}_{(i//3)*320}" for i in range(n)), f"{S}/preview2.jpg"], check=True)
else:
    parts = []
    for i, (g, s, e, cx, sp) in enumerate(CLIPS):
        f, off = SRC[g]
        o = f"{S}/d{i}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s - off), "-t", str(e - s), "-i", f, "-vf", f"{crop(cx)},setpts=PTS/{sp},minterpolate=fps=30:mi_mode=blend,fps=30,format=yuv420p", "-an", "-c:v", "libx264", "-crf", "17", "-preset", "medium", o], check=True)
        parts.append((o, s, s + (e - s) / sp))
    v2 = sys.argv[2]
    filt = [f"[{len(parts)}:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st={e-s-0.08}:d=0.08[a{i}]" for i, (o, s, e) in enumerate(parts)]
    ins = sum([["-i", o] for o, _, _ in parts], []) + ["-i", v2]
    chain = "".join(f"[{i}:v][a{i}]" for i in range(len(parts)))
    fc = ";".join(filt) + f";{chain}concat=n={len(parts)}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "160k", f"{S}/base2.mp4"], check=True)
    print("built")
