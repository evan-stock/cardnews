"""지도 릴스 효과음(직접 합성해서 저작권 걱정 없음). build.py가 화면 타이밍에 맞춰 부른다.

소리 목록
- whoosh: 사진→지도 전환, 장면 바뀔 때(자막 밀어 올림)
- draw:   나라 윤곽 그려질 때 올라가는 소리
- drop:   핀 떨어질 때 '퉁'
- pop:    사진 카드 튀어나올 때
- tick:   정리 장면 점들 뜰 때 '틱틱틱'
- boom:   정리 장면 시작 '쿵'
- chime:  CTA '띵'
- bed:    밑에 깔리는 낮은 심장박동(긴장감). spec "sfx_bed": false 로 끔
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
rng = np.random.default_rng(7)

def env(n, a=0.005, r=None):
    t = np.arange(n) / SR; a_n = max(1, int(a * SR))
    e = np.ones(n); e[:a_n] = np.linspace(0, 1, a_n)
    if r: e *= np.exp(-t / r)
    return e

def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], btype='band', fs=SR, output='sos'), x)

def whoosh(d=0.55, gain=0.5):
    n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    # 밴드가 위로 쓸려 올라가는 바람 소리
    out = np.zeros(n); seg = 512
    for i in range(0, n, seg):
        f = 300 + 3500 * (i / n) ** 1.5
        out[i:i + seg] = bp(x[i:i + seg], f * 0.6, min(f * 1.6, 18000))
    shape = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return out * shape * gain

def draw(d=1.0, gain=0.12):
    n = int(d * SR); t = np.arange(n) / SR
    f = 220 + 440 * (t / d) ** 2
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return x * np.sin(np.pi * t / d) * gain

def drop(gain=0.9):
    n = int(0.28 * SR); t = np.arange(n) / SR
    f = 180 * np.exp(-t * 9) + 55
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.09)
    click = bp(rng.standard_normal(n), 2000, 6000) * env(n, 0.001, 0.008) * 0.4
    return (body + click) * gain

def pop(gain=0.45):
    n = int(0.16 * SR); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 25) + 500
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.035) * gain + whoosh(0.16, 0.15)[:n]

def tick(gain=0.25):
    n = int(0.05 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1800 * t) * env(n, 0.0005, 0.01) * gain

def boom(gain=1.0):
    n = int(1.6 * SR); t = np.arange(n) / SR
    f = 70 * np.exp(-t * 3) + 38
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, 0.45)
    noise = sosfilt(butter(2, 300, fs=SR, output='sos'), rng.standard_normal(n)) * env(n, 0.002, 0.15) * 0.6
    return (body + noise) * gain

def chime(gain=0.35):
    n = int(1.4 * SR); t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(880, 1), (1318.5, .6), (1760, .3)])
    x2 = np.zeros(n); k = int(0.12 * SR)
    x2[k:] = sum(a * np.sin(2 * np.pi * f * t[:n - k]) for f, a in [(1174.7, .8), (1760, .4)])
    return (x * env(n, 0.002, 0.35) + x2 * env(n, 0.002, 0.4)) * gain / 2

def bed(dur, gain=0.22):
    # 낮은 '두-둥' 심장박동, 0.9초 간격
    n = int(dur * SR); out = np.zeros(n)
    beat = lambda g: np.sin(2 * np.pi * np.cumsum(60 * np.exp(-np.arange(int(.25 * SR)) / SR * 6) + 40) / SR) * env(int(.25 * SR), .004, .07) * g
    t = 0.0
    while t < dur:
        for off, g in [(0, 1.0), (0.22, 0.6)]:
            i = int((t + off) * SR); b = beat(g)
            if i < n: out[i:i + len(b)] += b[:n - i]
        t += 0.9
    return out * gain

def make(S, path, use_bed=True):
    dur = S['dur']; n = int(dur * SR) + SR; mix = np.zeros(n)
    def put(x, at):
        i = int(max(0, at) * SR); m = min(len(x), n - i)
        if m > 0: mix[i:i + m] += x[:m]
    end = S['intro']['end']
    put(whoosh(0.7, 0.55), end - 0.6)
    put(draw(1.0), end - 0.2)
    for i, sc in enumerate(S['scenes']):
        if i > 0: put(whoosh(0.45, 0.3), sc['t'] - 0.1)
        for p in sc['pins']: put(drop(), sc['t'] + 0.15 + 0.3)
        if sc.get('card'): put(pop(), sc['t'] + 0.65)
    put(whoosh(0.5, 0.3), S['recap']['t'] - 0.1)
    put(boom(), S['recap']['t'] + 0.05)
    for j in range(len(S.get('dots', []))): put(tick(), S['recap']['t'] + 0.25 + j * 0.07 + 0.05)
    put(whoosh(0.6, 0.35), S['cta'] - 0.2)
    put(chime(), S['cta'] + 0.3)
    if use_bed:
        b = bed(S['cta'])
        fade = np.ones(len(b)); k = int(0.8 * SR); fade[-k:] = np.linspace(1, 0, k); put(b * fade, 0)
    mix = mix[:int(dur * SR)]
    mix = np.tanh(mix * 1.2) * 0.8  # 부드러운 리미터
    st = np.stack([mix, mix], 1)
    wavfile.write(path, SR, (st * 32767).astype(np.int16))
