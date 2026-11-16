#!/usr/bin/env python3
"""유튜브 업로드 연결 도우미(맥 터미널용, 추가 설치 없음).

  curl -fsSL https://raw.githubusercontent.com/evan-stock/cardnews/main/scripts/yt_auth.py | python3 - <클라이언트ID>

1) 보안 비밀을 물어본다(입력해도 화면에 안 보임).
2) 브라우저가 열리면 '업로드할 채널'을 골라 허용한다.
3) 받은 refresh token 을 클립보드에 복사한다 → GitHub Secrets 에 붙여넣기.
"""
import getpass
import http.server
import json
import subprocess
import sys
import urllib.parse
import urllib.request
import webbrowser

PORT = 8765
REDIRECT = f"http://127.0.0.1:{PORT}"
SCOPE = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"


def post(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode())
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        return json.load(e)


def main():
    if len(sys.argv) < 2:
        sys.exit("사용법: ... | python3 - <클라이언트ID>")
    cid = sys.argv[1].strip()
    # 파이프로 실행하면 stdin 이 스크립트라서 키보드 입력은 터미널에서 직접 받는다
    try:
        sys.stdin = open("/dev/tty")
    except OSError:
        pass
    secret = getpass.getpass("보안 비밀을 붙여넣고 엔터 (화면에 안 보여요): ").strip()
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(
        {"client_id": cid, "redirect_uri": REDIRECT, "response_type": "code", "scope": SCOPE,
         "access_type": "offline", "prompt": "consent select_account"})
    box = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            box["code"] = q.get("code", [""])[0]
            box["error"] = q.get("error", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h2>완료! 이 창을 닫고 터미널을 보세요.</h2>".encode())

        def log_message(self, *a):
            pass

    print("\n브라우저가 열립니다. 업로드할 채널(예: 오늘의쓸모)을 골라 허용하세요.")
    print("안 열리면 이 주소를 복사해 여세요:\n" + url + "\n")
    webbrowser.open(url)
    http.server.HTTPServer(("127.0.0.1", PORT), H).handle_request()
    if not box.get("code"):
        sys.exit(f"허용이 안 됐어요: {box.get('error') or '코드 없음'}")
    j = post("https://oauth2.googleapis.com/token",
             {"code": box["code"], "client_id": cid, "client_secret": secret,
              "redirect_uri": REDIRECT, "grant_type": "authorization_code"})
    if "refresh_token" not in j:
        sys.exit(f"실패: {j.get('error')} {j.get('error_description', '')} (보안 비밀이 맞는지 확인)")
    names = "?"
    try:
        req = urllib.request.Request("https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
                                     headers={"Authorization": f"Bearer {j['access_token']}"})
        names = ", ".join(i["snippet"]["title"] for i in json.load(urllib.request.urlopen(req, timeout=60)).get("items", []))
    except Exception:
        pass
    tok = j["refresh_token"]
    try:
        subprocess.run(["pbcopy"], input=tok.encode(), check=True)
        copied = True
    except Exception:
        copied = False
    print(f"\n✅ 연결된 채널: {names}")
    if copied:
        print("✅ 토큰을 클립보드에 복사했어요. GitHub Secrets 값 칸에 붙여넣기(⌘V) 하면 됩니다.")
    else:
        print("토큰(GitHub Secrets 에 붙여넣기):\n" + tok)


if __name__ == "__main__":
    main()
