#!/usr/bin/env bash
# 맥에서 렌더 명령을 Actions와 같은 리눅스 환경에서 실행한다.
# 사용: ./local/render.sh python -m cardnews.shorts drafts/shorts.json
#       ./local/render.sh bash            (상자 안으로 들어가기)
# 처음 한 번은 상자 만들기에 5~10분 걸린다. requirements.txt가 바뀌면 자동으로 다시 만든다.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v docker >/dev/null || { echo "Docker Desktop을 먼저 설치하고 실행하세요: https://www.docker.com/products/docker-desktop/"; exit 1; }
TAG="cardnews-local:$(cat requirements.txt local/Dockerfile | shasum | cut -c1-12)"
if ! docker image inspect "$TAG" >/dev/null 2>&1; then
  CTX=$(mktemp -d); cp requirements.txt local/Dockerfile "$CTX"/   # 저장소 전체(수 GB)를 보내지 않도록 필요한 파일만
  docker build -t "$TAG" "$CTX"; rm -rf "$CTX"
fi
ENVF=(); [ -f .env ] && ENVF=(--env-file .env)
TTY=(); [ -t 0 ] && [ -t 1 ] && TTY=(-it)   # Claude Code처럼 터미널이 없을 때도 동작
docker run --rm ${TTY[@]+"${TTY[@]}"} ${ENVF[@]+"${ENVF[@]}"} -v "$PWD":/work -w /work "$TAG" "${@:-bash}"
