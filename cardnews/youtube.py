"""유튜브 쇼츠 업로드(YouTube Data API v3, 업로드 1건 = 할당량 1,600 → 기본 하루 6건까지).

Secrets: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
최초 1회(내 컴퓨터에서): python -m cardnews.youtube auth <CLIENT_ID> <CLIENT_SECRET>
  → 브라우저에서 채널 계정으로 허용 → 출력되는 refresh token을 YT_REFRESH_TOKEN 에 등록
"""
import datetime as dt
import json
import sys

import requests

from .common import env

TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"


def access_token():
    r = requests.post(TOKEN_URL, data={"client_id": env("YT_CLIENT_ID"), "client_secret": env("YT_CLIENT_SECRET"),
                                       "refresh_token": env("YT_REFRESH_TOKEN"), "grant_type": "refresh_token"},
                      timeout=60)
    j = r.json()
    if "access_token" not in j:
        raise RuntimeError(f"유튜브 토큰 갱신 실패: {j} (refresh token 만료면 auth 다시 실행)")
    return j["access_token"]


def upload(path, yt, publish_at=None):
    """yt = {"title","description","tags","category","privacy","synthetic"}. (video_id, url) 반환.
    publish_at(aware datetime)이 10분 이상 미래면 비공개로 올리고 그 시각에 유튜브가 자동 공개한다."""
    status = {"privacyStatus": yt.get("privacy", "public"), "selfDeclaredMadeForKids": False,
              "containsSyntheticMedia": bool(yt.get("synthetic"))}
    if publish_at and publish_at > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=10):
        status.update(privacyStatus="private",
                      publishAt=publish_at.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"))
    meta = {"snippet": {"title": yt["title"][:100], "description": yt.get("description", "")[:4900],
                        "tags": yt.get("tags", [])[:15], "categoryId": str(yt.get("category", 24)),
                        "defaultLanguage": "ko", "defaultAudioLanguage": "ko"},
            "status": status}
    h = {"Authorization": f"Bearer {access_token()}"}
    data = open(path, "rb").read()
    r = requests.post("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                      headers={**h, "Content-Type": "application/json; charset=UTF-8",
                               "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(len(data))},
                      data=json.dumps(meta), timeout=60)
    if r.status_code != 200 or "Location" not in r.headers:
        raise RuntimeError(f"유튜브 업로드 시작 실패 {r.status_code}: {r.text[:300]}")
    r2 = requests.put(r.headers["Location"], headers={**h, "Content-Type": "video/mp4"}, data=data, timeout=600)
    if r2.status_code not in (200, 201):
        raise RuntimeError(f"유튜브 업로드 실패 {r2.status_code}: {r2.text[:300]}")
    vid = r2.json()["id"]
    return vid, f"https://youtube.com/shorts/{vid}", status


def auth(client_id, client_secret, port=8765):
    """내 컴퓨터에서 한 번 실행해 refresh token을 받는다(브라우저 로그인)."""
    import http.server
    import urllib.parse
    import webbrowser
    redirect = f"http://127.0.0.1:{port}"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(
        {"client_id": client_id, "redirect_uri": redirect, "response_type": "code", "scope": SCOPE,
         "access_type": "offline", "prompt": "consent"})
    box = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            box["code"] = q.get("code", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("완료! 이 창을 닫고 터미널을 보세요.".encode())

        def log_message(self, *a):
            pass

    print("브라우저가 안 열리면 이 주소를 직접 여세요:\n", url)
    webbrowser.open(url)
    http.server.HTTPServer(("127.0.0.1", port), H).handle_request()
    j = requests.post(TOKEN_URL, data={"code": box.get("code"), "client_id": client_id, "client_secret": client_secret,
                                       "redirect_uri": redirect, "grant_type": "authorization_code"}, timeout=60).json()
    if "refresh_token" not in j:
        raise SystemExit(f"실패: {j}")
    print("\nYT_REFRESH_TOKEN =", j["refresh_token"])


if __name__ == "__main__":
    if sys.argv[1] == "auth":
        auth(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "check":
        j = requests.get("https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
                         headers={"Authorization": f"Bearer {access_token()}"}, timeout=60).json()
        print([c["snippet"]["title"] for c in j.get("items", [])] or j)
