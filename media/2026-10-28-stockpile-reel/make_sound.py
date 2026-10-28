"""릴스용 오리지널 사운드(직접 합성): 긴장감 배경 + 이벤트 효과음. 영상 타이밍은 렌더 스크립트에서 가져온다."""
import sys, os, importlib.util, wave
import numpy as np

S = os.path.dirname(os.path.abspath(__file__))
sys.argv = ["x", os.path.join(S, "_dummy")]
spec = importlib.util.spec_from_file_location("rr", os.path.join(S, "stockpile_reel.py"))
rr = importlib.util.module_from_spec(spec); spec.loader.exec_module(rr)

SR = 44100
TOTAL = rr.TOTAL
N = int(TOTAL * SR) + SR
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
t_all = np.arange(N) / SR


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * (1 - max(0, pan))
    R[i:i + len(sig)] += sig * (1 + min(0, pan))


def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def lowpass(x, cut):
    a = np.exp(-2 * np.pi * cut / SR); y = np.zeros_like(x); p = 0.0
    for k in range(len(x)):
        p = (1 - a) * x[k] + a * p; y[k] = p
    return y


def tone(f0, dur, f1=None, d=0.15, wave_="sine"):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.linspace(f0, f1 or f0, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) if wave_ == "sine" else np.sign(np.sin(ph)) * 0.6
    return s * env(n, 0.003, d)


def kick(dur=0.5, f0=110, f1=40, d=0.18):
    return tone(f0, dur, f1, d) * 1.4


def noise(dur, d=0.1, cut=4000):
    n = int(dur * SR)
    return lowpass(rng.standard_normal(n), cut) * env(n, 0.001, d)


def alert_beep(f0=1250, on=0.09, gap=0.05, n_beeps=2):
    """재난문자·경보기 같은 '삐-삐' : 평평한 음량의 각진 소리 두 번."""
    seg = int(on * SR); t = np.arange(seg) / SR
    s = sum(np.sin(2 * np.pi * f0 * h * t) / h for h in (1, 3, 5, 7)) * 0.8
    edge = int(0.004 * SR); e = np.ones(seg); e[:edge] = np.linspace(0, 1, edge); e[-edge:] = np.linspace(1, 0, edge)
    one = s * e
    out = np.zeros(int((on + gap) * SR) * n_beeps)
    for k in range(n_beeps):
        i = k * int((on + gap) * SR); out[i:i + seg] += one
    return out


# 1) 배경: 낮은 드론 + 서서히 커지는 긴장
drone = (np.sin(2 * np.pi * 55 * t_all) * 0.5 + np.sin(2 * np.pi * 82.4 * t_all) * 0.3
         + np.sin(2 * np.pi * 110.3 * t_all) * 0.12) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.25 * t_all))
rumble = lowpass(rng.standard_normal(N), 180) * 0.9
bed = (drone * 0.22 + rumble * 0.35) * np.clip(t_all / 1.5, 0, 1) * (0.7 + 0.3 * np.clip(t_all / rr.T_KR, 0, 1))
bed *= np.clip((TOTAL + 0.6 - t_all) / 0.8, 0, 1)
L += bed; R += bed

# 2) 카운트다운 틱(매초, 교대로 좌우)
tick = noise(0.03, 0.006, 7000) * 0.55 + tone(2200, 0.03, d=0.008) * 0.25
for k, s in enumerate(np.arange(0.0, rr.T_SHEL, 0.5)):
    add(tick, s, 0.7 if k % 2 == 0 else 0.45, 0.3 if k % 2 else -0.3)

# 3) 시작 임팩트
add(kick(1.2, 90, 30, 0.45), 0.0, 1.0)
add(noise(1.5, 0.5, 900), 0.0, 0.35)

# 4) 나라 켜질 때: 저음 펄스 + 삑
for i, c in enumerate(rr.SEQ):
    t0 = c[4]
    add(kick(0.35, 120, 45, 0.12), t0, 0.5)
    add(alert_beep(), t0, 0.42)

# 5) EU: 큰 한 방
add(kick(1.4, 80, 28, 0.6), rr.T_EU, 1.2)
add(noise(1.2, 0.35, 2500), rr.T_EU, 0.35)
add(tone(523, 0.8, d=0.35) + tone(784, 0.8, d=0.35) * 0.6, rr.T_EU, 0.22)

# 6) 아시아로 이동: 휙
n = int((rr.T_PAN1 - rr.T_PAN0 + 0.3) * SR); tt = np.arange(n) / n
sw = rng.standard_normal(n)
w = np.zeros(n); p = 0.0
for k in range(n):
    a = np.exp(-2 * np.pi * (300 + 5000 * np.sin(np.pi * tt[k])) / SR)
    p = (1 - a) * sw[k] + a * p; w[k] = p
w *= np.sin(np.pi * tt) ** 2
add(w, rr.T_PAN0 - 0.1, 0.9, 0)

# 7) 한국: 경보음(두 음 교대)
t0 = rr.T_KR
for k in range(7):
    add(tone(880 if k % 2 == 0 else 660, 0.34, d=0.5, wave_="square") * np.hanning(int(0.34 * SR)), t0 + 0.1 + k * 0.38, 0.38)
add(kick(1.0, 70, 30, 0.4), t0, 1.0)

# 8) 텍스트 카드: 줄마다 쿵, 강조 줄은 크게
def card_hits(t0, nlines, big):
    add(noise(0.9, 0.3, 1200), t0, 0.3)
    for k in range(nlines):
        tk = t0 + 0.12 * k
        if k in big:
            add(kick(1.2, 95, 30, 0.5), tk, 1.3); add(noise(0.8, 0.25, 3000), tk, 0.4)
        else:
            add(kick(0.3, 140, 60, 0.07), tk, 0.6)

card_hits(rr.T_SHEL, 3, {1})
card_hits(rr.T_END, 2, {1})
# 마지막: 긴 여운 + 심장박동 두 번
add(kick(0.4, 70, 40, 0.12), rr.T_END + 1.4, 0.9); add(kick(0.4, 70, 40, 0.12), rr.T_END + 1.7, 0.7)
add(kick(0.4, 70, 40, 0.12), rr.T_END + 2.4, 0.9); add(kick(0.4, 70, 40, 0.12), rr.T_END + 2.7, 0.7)

# 마스터: 소프트 클립 + 정규화(-1dBFS)
mix = np.stack([L, R], 1)[: int(TOTAL * SR)]
mix = np.tanh(mix * 1.1)
mix *= 0.89 / np.abs(mix).max()
fade = int(0.3 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
out = sys.argv_out if hasattr(sys, "argv_out") else os.path.join(S, "sfx.wav")
with wave.open(out, "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", out, round(TOTAL, 2))
