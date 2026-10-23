#!/usr/bin/env bash
# GitHub Actions 설치 단계(렌더용 한글 폰트·ffmpeg·크로미움).
# 2026.10.23: apt-get이 가끔 30분 넘게 멈춰(00:32→01:06, 두 번은 취소) 뒤 원고까지 줄줄이 막혔다.
# → 명령마다 시간 제한 + 재시도, man-db 색인 갱신 끄기, dpkg 잠금 대기 제한.
# 사용: bash scripts/ci_install.sh [apt 패키지...]   (기본: fonts-noto-cjk ffmpeg)
set -u
PKGS="${*:-fonts-noto-cjk ffmpeg}"

pip install -q -r requirements.txt

# man-db 색인 갱신은 패키지 설치 뒤 수 분씩 걸리기도 해서 끈다.
echo 'man-db man-db/auto-update boolean false' | sudo debconf-set-selections || true
sudo rm -f /var/lib/man-db/auto-update || true

APT_OPTS="-y -qq -o Acquire::Retries=3 -o Acquire::http::Timeout=20 -o DPkg::Lock::Timeout=60"
ok=0
for i in 1 2 3; do
  if sudo timeout 180 apt-get install $APT_OPTS $PKGS; then ok=1; break; fi
  echo "::warning::apt 설치 실패/시간 초과($i/3) → 목록 갱신 후 재시도"
  sudo timeout 120 apt-get update -qq -o Acquire::Retries=3 || true
done
[ $ok = 1 ] || { echo "::error::apt 설치 3번 실패"; exit 1; }

ok=0
for i in 1 2 3; do
  if timeout 300 python -m playwright install --with-deps chromium; then ok=1; break; fi
  echo "::warning::playwright 설치 실패/시간 초과($i/3) → 재시도"
done
[ $ok = 1 ] || { echo "::error::playwright 설치 3번 실패"; exit 1; }
