#!/usr/bin/env python3
"""새 유튜브 채널 연결 토큰 받기 (맥 터미널에 한 줄 붙여넣기용, 표준 라이브러리만 사용, 2026.10.23).

  curl -fsSL https://raw.githubusercontent.com/evan-stock/cardnews/main/scripts/yt_token.py -o /tmp/yt_token.py && python3 /tmp/yt_token.py

클라이언트 ID·보안 비밀을 물어보고(보안 비밀은 화면에 안 보임) 브라우저 로그인 후 refresh token 을 출력한다.
아무 파일에도 저장하지 않는다.
"""
import getpass
import http.server
import json
import urllib.parse
import urllib.request
import webbrowser

SCOPE = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"
PORT = 8765
REDIRECT = f"http://127.0.0.1:{PORT}"

print("\n=== 새 유튜브 채널 연결 ===\n")
cid = input("1) 클라이언트 ID 붙여넣고 엔터: ").strip()
sec = getpass.getpass("2) 보안 비밀 붙여넣고 엔터 (화면에 안 보이는 게 정상): ").strip()
url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(
    {"client_id": cid, "redirect_uri": REDIRECT, "response_type": "code", "scope": SCOPE,
     "access_type": "offline", "prompt": "consent select_account"})
box = {}


class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        box["code"] = q.get("code", [""])[0]
        box["err"] = q.get("error", [""])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("<h1>완료! 이 창 닫고 터미널로 돌아가세요.</h1>".encode())

    def log_message(self, *a):
        pass


print("\n3) 브라우저가 열려요. **새로 만든 구글 계정**을 고르고 계속/허용을 누르세요.")
print("   '확인되지 않은 앱' 화면이 나오면: 고급 → (앱 이름)(으)로 이동")
print("   브라우저가 안 열리면 이 주소를 복사해서 여세요:\n  ", url, "\n")
webbrowser.open(url)
http.server.HTTPServer(("127.0.0.1", PORT), H).handle_request()
if not box.get("code"):
    raise SystemExit(f"\n실패: 로그인이 취소됐어요 ({box.get('err')}). 다시 실행하세요.")
data = urllib.parse.urlencode({"code": box["code"], "client_id": cid, "client_secret": sec,
                               "redirect_uri": REDIRECT, "grant_type": "authorization_code"}).encode()
try:
    j = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", data, timeout=60))
except urllib.error.HTTPError as e:
    raise SystemExit(f"\n실패: {e.read().decode()[:300]}\n클라이언트 ID·보안 비밀을 다시 확인하세요.")
if "refresh_token" not in j:
    raise SystemExit(f"\n실패: {j}")
req = urllib.request.Request("https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
                             headers={"Authorization": "Bearer " + j["access_token"]})
try:
    items = json.load(urllib.request.urlopen(req, timeout=30)).get("items") or []
    name = items[0]["snippet"]["title"] if items else "(채널 없음 — 이 계정에 유튜브 채널을 먼저 만드세요)"
except Exception:
    name = "(채널 이름 확인 실패)"
print("\n연결된 채널:", name)
print("\n4) 아래 긴 글자를 통째로 복사해서 GitHub의 YT_REFRESH_TOKEN_LIFE 에 넣으세요:\n")
print(j["refresh_token"])
print()
