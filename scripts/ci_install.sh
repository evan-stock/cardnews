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

# 2026.10.24: 지난번에 받아 둔 패키지 파일(~/.apt-debs, actions/cache)이 있으면 apt 보관함에 넣어
# 다운로드 없이 설치되게 한다. 끝나면 다시 ~/.apt-debs로 모아 다음 실행이 쓰게 한다.
DEBS="$HOME/.apt-debs"; mkdir -p "$DEBS"
if ls "$DEBS"/*.deb >/dev/null 2>&1; then
  echo "보관된 패키지 $(ls "$DEBS"/*.deb | wc -l)개 사용"
  sudo cp -n "$DEBS"/*.deb /var/cache/apt/archives/ || true
fi
save_debs() { cp -n /var/cache/apt/archives/*.deb "$DEBS"/ 2>/dev/null || true; }

APT_OPTS="-y -qq -o Acquire::Retries=3 -o Acquire::http::Timeout=20 -o DPkg::Lock::Timeout=60 -o APT::Keep-Downloaded-Packages=true"
ok=0
for i in 1 2 3; do
  if sudo timeout 180 apt-get install $APT_OPTS $PKGS; then ok=1; break; fi
  echo "::warning::apt 설치 실패/시간 초과($i/3) → 목록 갱신 후 재시도"
  sudo timeout 120 apt-get update -qq -o Acquire::Retries=3 || true
done
[ $ok = 1 ] || { echo "::error::apt 설치 3번 실패"; exit 1; }
save_debs

ok=0
for i in 1 2 3; do
  if timeout 300 python -m playwright install --with-deps chromium; then ok=1; break; fi
  echo "::warning::playwright 설치 실패/시간 초과($i/3) → 재시도"
done
[ $ok = 1 ] || { echo "::error::playwright 설치 3번 실패"; exit 1; }
save_debs
