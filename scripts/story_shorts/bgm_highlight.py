#!/usr/bin/env python3
"""배경음악에서 쇼츠에 쓸 하이라이트 구간을 찾는다.

쓰는 법:
  python3 bgm_highlight.py 곡.mp3 --len 25            # 시작 초만 출력
  python3 bgm_highlight.py 곡.mp3 --len 25 --cut out.mp3   # 그 구간을 잘라 저장(앞 0.15초 페이드인, 끝 1초 페이드아웃)

찾는 방법:
  1) 0.5초 단위 음량(RMS)을 잰다.
  2) 영상 길이(--len)만큼의 구간 중 평균 음량이 가장 큰 곳 = 가장 고조된 부분.
  3) 그 시작점 앞뒤 8초 안에서 음량이 가장 크게 '확' 커지는 지점(드롭·후렴 시작)으로 시작을 맞춘다.
     → 영상 0초부터 음악이 이미 터진 상태로 시작한다(쇼츠는 첫 1~2초가 중요).
  4) 곡 맨 앞 3초와 끝 부분(페이드아웃 꼬리)은 피한다.
"""
import argparse
import subprocess
import sys

import numpy as np

SR = 8000
STEP = 0.5  # 초


def load(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def find_start(x, length):
    hop = int(SR * STEP)
    n = len(x) // hop
    rms = np.sqrt(np.array([np.mean(x[i * hop:(i + 1) * hop] ** 2) for i in range(n)]) + 1e-12)
    rms = rms / rms.max()
    win = int(length / STEP)
    head, tail = int(3 / STEP), int(4 / STEP)
    last = n - win - tail
    if last <= head:  # 곡이 영상보다 짧거나 비슷하면 처음부터
        return 0.0, rms
    sums = np.convolve(rms, np.ones(win), "valid")
    seg = sums[head:last + 1]
    # 거의 같은 크기(97% 이상)의 구간이 여럿이면 가장 앞의 것 = 고조가 시작되는 쪽
    best = head + int(np.argmax(seg >= seg.max() * 0.97))
    # 확 커지는 지점으로 맞추기
    lo, hi = max(head + 4, best - int(8 / STEP)), min(last, best + int(8 / STEP))
    rise = [(rms[s:s + 4].mean() - rms[s - 4:s].mean(), s) for s in range(lo, hi + 1)]
    gain, s = max(rise)
    start = s if gain > 0.12 else best
    return round(start * STEP, 1), rms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--len", type=float, default=25.0, help="영상 길이(초)")
    ap.add_argument("--cut", help="잘라서 저장할 파일")
    a = ap.parse_args()
    x = load(a.path)
    start, rms = find_start(x, a.len)
    print(f"{start}")
    if a.cut:
        fade_out_at = max(0.0, a.len - 1.0)
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", str(start), "-t", str(a.len), "-i", a.path,
             "-af", f"afade=t=in:d=0.15,afade=t=out:st={fade_out_at}:d=1.0", a.cut],
            check=True)
        print(f"saved {a.cut}", file=sys.stderr)


if __name__ == "__main__":
    main()
