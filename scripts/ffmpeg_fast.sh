#!/usr/bin/env bash
# ffmpeg·ffprobe 빠른 설치 (2026.11.19).
# 이유: 우분투 미러 404 때문에 넣은 'apt-get update'가 20~33분씩 걸려 엑스 받기가 30~40분 지연됨
#       (실제 다운로드는 4~8초). → GitHub 릴리스의 정적 빌드(BtbN)를 먼저 받고, 실패할 때만 apt(시간 제한).
set -u
if command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null; then echo "ffmpeg 이미 있음"; exit 0; fi
URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz
D=/tmp/ffmpeg-master-latest-linux64-gpl
if timeout 120 curl -fsSL --retry 3 -o /tmp/ff.tar.xz "$URL" && tar -xJf /tmp/ff.tar.xz -C /tmp \
   && sudo cp "$D/bin/ffmpeg" "$D/bin/ffprobe" /usr/local/bin/; then
  echo "ffmpeg 정적 빌드 설치"; ffmpeg -version | head -1; exit 0
fi
echo "::warning::정적 빌드 실패 → apt로 설치"
APT="-y -qq -o Acquire::Retries=3 -o Acquire::http::Timeout=20 -o DPkg::Lock::Timeout=60"
sudo timeout 180 apt-get install $APT ffmpeg && exit 0
sudo timeout 240 apt-get update -qq -o Acquire::Retries=3 || true
sudo timeout 240 apt-get install $APT --fix-missing ffmpeg
