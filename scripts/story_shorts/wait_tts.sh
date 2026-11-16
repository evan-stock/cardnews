#!/bin/bash
# 오늘의쓸모 내레이션: 요청서(state/tts_queue/<id>.json)를 push 한 뒤, 맥북이 목소리를 올릴 때까지 기다린다.
#   bash scripts/story_shorts/wait_tts.sh <id> [최대 분, 기본 25]
# 끝나면 0(목소리 도착) / 1(시간 초과 — 맥북 잠자기 등). 도착 후 card_render.py 를 다시 실행.
id="$1"; max=${2:-25}
for ((i=0; i<max*2; i++)); do
  git pull -q --rebase origin main >/dev/null 2>&1
  if [ ! -f "state/tts_queue/$id.json" ] && ls "media/$id/tts/"*.mp3 >/dev/null 2>&1; then
    echo "목소리 도착: $(ls media/$id/tts/*.mp3 | wc -l)개"; exit 0
  fi
  sleep 30
done
echo "시간 초과: 맥북이 잠자기이거나 꺼져 있을 수 있음"; exit 1
