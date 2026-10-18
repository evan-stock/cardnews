#!/usr/bin/env python3
"""밈 자막형 쇼츠용 효과음을 직접 합성해 assets/sfx/*.mp3 로 만든다(2026.10.18).
외부 음원을 쓰지 않으므로 저작권·라이선스 걱정이 없다(우리가 만든 소리).

쓰는 법: python3 scripts/sfx/make_sfx.py   → assets/sfx/<이름>.mp3 + README 표
원고: 장면 "sfx": [{"f": "pop", "at": 0.4, "vol": 1.0}] 또는 위치 자막 cap 에 "s": "pop"
"""
import os
import subprocess
import tempfile
import wave

import numpy as np

SR = 44100
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sfx")
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(SR * d)) / SR


def env(n, a=0.005, r=None, curve=4.0):
    """짧은 어택 + 지수 감쇠."""
    x = np.arange(n) / SR
    e = 1 - np.exp(-x / max(a, 1e-4))
    if r is None:
        r = n / SR
    return e * np.exp(-curve * x / r)


def sweep(f0, f1, d, shape="sin", log=True):
    tt = t(d)
    f = f0 * (f1 / f0) ** (tt / d) if log else f0 + (f1 - f0) * tt / d
    ph = 2 * np.pi * np.cumsum(f) / SR
    if shape == "saw":
        return 2 * ((ph / (2 * np.pi)) % 1) - 1
    if shape == "square":
        return np.sign(np.sin(ph))
    if shape == "tri":
        return 2 * np.abs(2 * ((ph / (2 * np.pi)) % 1) - 1) - 1
    return np.sin(ph)


def tone(f, d, shape="sin", vib=0.0, vibf=6.0):
    tt = t(d)
    fr = f * (1 + vib * np.sin(2 * np.pi * vibf * tt))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    if shape == "saw":
        return 2 * ((ph / (2 * np.pi)) % 1) - 1
    if shape == "square":
        return np.sign(np.sin(ph)) * 0.6
    return np.sin(ph)


def lowpass(x, cutoff):
    """1차 저역 통과(간단)."""
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def noise(d):
    return rng.uniform(-1, 1, int(SR * d))


def seq(parts, gap=0.0):
    out = []
    for p in parts:
        out.append(p)
        if gap:
            out.append(np.zeros(int(SR * gap)))
    return np.concatenate(out)


def mix(*xs):
    n = max(len(x) for x in xs)
    y = np.zeros(n)
    for x in xs:
        y[:len(x)] += x
    return y


def place(x, at, total):
    y = np.zeros(int(SR * total))
    i = int(SR * at)
    y[i:i + len(x)] += x[:len(y) - i]
    return y


def bell(f, d=1.2):
    tt = t(d)
    y = sum(a * np.sin(2 * np.pi * f * m * tt) for m, a in [(1, 1), (2.01, 0.5), (3.02, 0.25), (4.2, 0.15)])
    return y * env(len(tt), 0.002, d, 5)


def S():
    s = {}
    # 뿅: 짧게 올라가는 방울 소리
    x = sweep(500, 1500, 0.12)
    s["pop"] = ("뿅(등장·깨달음)", x * env(len(x), 0.003, 0.12, 3))
    # 띠용: 스프링(진동하며 떨어짐)
    tt = t(0.7)
    f = 330 * (1 + 0.5 * np.sin(2 * np.pi * 9 * tt) * np.exp(-3 * tt)) * (1 + 0.6 * np.exp(-6 * tt))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    s["boing"] = ("띠용(황당·튕김)", x * env(len(x), 0.003, 0.7, 3))
    # 휙: 잡음 스윕
    n = noise(0.45)
    e = np.sin(np.pi * np.arange(len(n)) / len(n)) ** 2
    hi = lowpass(n, 3500) - lowpass(n, 600)
    s["whoosh"] = ("휙(빠른 움직임·장면 전환)", hi * e * 2.2)
    # 띵: 종소리
    s["ding"] = ("띵(정답·아이디어)", bell(1318, 1.2))
    # 쿵: 낮은 충돌음
    x = sweep(120, 45, 0.5) * env(int(SR * 0.5), 0.002, 0.5, 5) + lowpass(noise(0.5), 900) * env(int(SR * 0.5), 0.001, 0.12, 6) * 0.8
    s["thud"] = ("쿵(넘어짐·떨어짐)", x)
    # 두둥: 드럼 두 번
    hit = sweep(110, 50, 0.45) * env(int(SR * 0.45), 0.002, 0.45, 4)
    s["dundun"] = ("두둥(등장·긴장)", mix(place(hit, 0, 1.0), place(hit * 1.1, 0.28, 1.0)))
    # 반짝: 높은 음 아르페지오
    notes = [1568, 1976, 2349, 3136]
    s["sparkle"] = ("반짝(귀여움·예쁨)", mix(*[place(bell(fq, 0.5) * 0.6, i * 0.06, 0.9) for i, fq in enumerate(notes)]))
    # 실패 트롬본: 빠-빠-빠-빠아~
    ns = [(392, 0.32), (370, 0.32), (349, 0.32), (330, 1.0)]
    parts = []
    for i, (fq, d) in enumerate(ns):
        x = tone(fq, d, "saw", vib=0.018 if i == 3 else 0, vibf=5.5)
        x = lowpass(x, 1400) * env(len(x), 0.02, d, 1.2 if i == 3 else 2.0)
        parts.append(x)
    s["fail"] = ("빠밤(실패·허무)", seq(parts, 0.04))
    # 짠: 장조 화음
    ch = [523, 659, 784, 1047]
    x = sum(lowpass(tone(fq, 0.9, "saw"), 2500) for fq in ch) / 3
    s["tada"] = ("짠(성공·공개)", mix(place(x[:int(SR * 0.12)] * env(int(SR * 0.12), 0.003, 0.12, 2), 0, 1.1),
                                      place(x * env(len(x), 0.005, 0.9, 2.5), 0.15, 1.1)))
    # 물음표: 올라가는 두 음
    s["question"] = ("갸우뚱(?·의아)", seq([tone(660, 0.12, "square") * env(int(SR * 0.12), 0.003, 0.12, 2),
                                         tone(990, 0.22, "square") * env(int(SR * 0.22), 0.003, 0.22, 2)], 0.03) * 0.8)
    # 살금살금: 피치카토
    pz = [392, 494, 392, 494, 440, 523]
    s["sneak"] = ("살금살금(몰래·조심)", seq([lowpass(tone(fq, 0.16, "saw"), 1800) * env(int(SR * 0.16), 0.002, 0.16, 6) for fq in pz], 0.06))
    # 두근두근
    thump = sweep(80, 50, 0.16) * env(int(SR * 0.16), 0.003, 0.16, 5)
    beat = mix(place(thump, 0, 0.5), place(thump * 0.8, 0.18, 0.5))
    s["heart"] = ("두근두근(설렘·긴장)", np.concatenate([beat, beat * 0.9]))
    # 헉!: 오케스트라 히트 느낌
    x = sum(lowpass(tone(fq, 0.6, "saw"), 3000) for fq in [196, 233, 294, 392, 466]) / 3
    x = x * env(len(x), 0.002, 0.6, 4) + lowpass(noise(0.6), 2000) * env(int(SR * 0.6), 0.001, 0.08, 6) * 0.5
    s["shock"] = ("헉(충격·반전)", x)
    # 뾱뾱: 장난감 삑삑이
    sq = sweep(900, 1300, 0.09, "tri") * env(int(SR * 0.09), 0.003, 0.09, 2)
    s["squeak"] = ("뾱뾱(장난감·귀여움)", seq([sq, sq * 0.9], 0.05))
    # 쭈욱/날름: 미끄러지듯 내려가는 소리
    x = sweep(1200, 300, 0.35, "tri", log=False)
    s["slide"] = ("쭈욱·날름(늘어남·핥기)", x * env(len(x), 0.01, 0.35, 1.5) * 0.8)
    # 째깍째깍
    tick = lowpass(noise(0.03), 5000) * env(int(SR * 0.03), 0.0005, 0.03, 8)
    tock = tick * 0.7
    s["tick"] = ("째깍째깍(기다림)", seq([tick, np.zeros(int(SR * 0.22)), tock, np.zeros(int(SR * 0.22))] * 2))
    # 펑(팝콘·터짐)
    x = lowpass(noise(0.25), 2500) * env(int(SR * 0.25), 0.001, 0.25, 7) + sweep(200, 60, 0.25) * env(int(SR * 0.25), 0.001, 0.25, 6)
    s["poof"] = ("펑(사라짐·터짐)", x)
    # 촵촵(먹는 소리 대신 리듬)
    ch = lowpass(noise(0.07), 3000) * env(int(SR * 0.07), 0.001, 0.07, 6)
    s["nom"] = ("냠냠(먹기)", seq([ch, ch * 0.8, ch, ch * 0.8], 0.09))
    return s


def write(name, x):
    x = np.asarray(x, dtype=np.float64)
    x = x / (np.abs(x).max() + 1e-9) * 0.89
    fade = min(len(x), int(SR * 0.01))
    x[-fade:] *= np.linspace(1, 0, fade)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav = f.name
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ac", "2", "-b:a", "160k",
                    os.path.join(OUT, f"{name}.mp3")], check=True)
    os.remove(wav)
    return len(x) / SR


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for name, (desc, x) in S().items():
        d = write(name, x)
        rows.append(f"| {name} | {desc} | {d:.2f}초 |")
    open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write(
        "# 효과음 (직접 합성, scripts/sfx/make_sfx.py — 저작권 없음)\n\n"
        "원고: 장면 `\"sfx\": [{\"f\": \"pop\", \"at\": 0.4, \"vol\": 1.0}]` 또는 위치 자막에 `\"s\": \"pop\"`.\n\n"
        "| 이름 | 쓰임 | 길이 |\n|---|---|---|\n" + "\n".join(rows) + "\n")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
