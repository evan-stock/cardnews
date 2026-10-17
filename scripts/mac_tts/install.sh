#!/bin/bash
# 맥북 목소리 도우미 설치: 터미널에 아래 한 줄을 붙여넣고 엔터
#   curl -fsSL https://raw.githubusercontent.com/evan-stock/cardnews/main/scripts/mac_tts/install.sh | bash
set -e
DIR="$HOME/.cardnews_tts"
mkdir -p "$DIR"
chmod 700 "$DIR"
curl -fsSL https://raw.githubusercontent.com/evan-stock/cardnews/main/scripts/mac_tts/tts_local.py -o "$DIR/tts_local.py"

if ! /usr/bin/python3 -c "print(1)" >/dev/null 2>&1; then
  echo "파이썬이 없어요. 뜨는 창에서 '설치'를 누른 뒤 이 명령을 다시 실행해 주세요."
  xcode-select --install || true
  exit 1
fi

if [ ! -f "$DIR/config.json" ]; then
  while true; do
    echo ""
    echo "① 타입캐스트 API 키를 붙여넣고 엔터 (화면에 안 보여요)"
    read -rs TC_KEY < /dev/tty; echo ""
    echo "② GitHub 토큰(github_pat_ 로 시작)을 붙여넣고 엔터 (화면에 안 보여요)"
    read -rs GH_TOKEN < /dev/tty; echo ""
    TC_KEY="$(printf '%s' "$TC_KEY" | tr -d '[:space:]')"; GH_TOKEN="$(printf '%s' "$GH_TOKEN" | tr -d '[:space:]')"
    echo "   타입캐스트 키 길이: ${#TC_KEY}자 / GitHub 토큰: ${GH_TOKEN:0:11}... (${#GH_TOKEN}자)"
    code=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/repos/evan-stock/cardnews/contents/README.md)
    if [ "$code" = "200" ]; then echo "   ✅ GitHub 토큰 확인됨"; break; fi
    echo "   ❌ GitHub 토큰이 안 맞아요(응답 $code). github_pat_ 로 시작하는 긴 토큰 전체를 다시 복사해서 넣어 주세요."
  done
  /usr/bin/python3 - "$TC_KEY" "$GH_TOKEN" "$DIR/config.json" <<'PY'
import json, sys
json.dump({"typecast_key": sys.argv[1].strip(), "github_token": sys.argv[2].strip(),
           "repo": "evan-stock/cardnews", "monthly_cap": 14000}, open(sys.argv[3], "w"))
PY
  chmod 600 "$DIR/config.json"
fi

PL="$HOME/Library/LaunchAgents/com.cardnews.tts.plist"
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PL" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.cardnews.tts</string>
  <key>ProgramArguments</key><array><string>/usr/bin/python3</string><string>$DIR/tts_local.py</string></array>
  <key>StartInterval</key><integer>120</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$DIR/launchd.out</string>
  <key>StandardErrorPath</key><string>$DIR/launchd.err</string>
</dict></plist>
EOF
launchctl unload "$PL" 2>/dev/null || true
launchctl load "$PL"
echo ""
echo "✅ 설치 완료! 맥북이 켜져 있으면 2분마다 목소리 요청을 확인해요."
echo "   기록 보기: cat ~/.cardnews_tts/log.txt"
echo "   끄기: launchctl unload ~/Library/LaunchAgents/com.cardnews.tts.plist"
