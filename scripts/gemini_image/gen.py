"""Gemini 이미지 생성: drafts/gemini_image.json 의 prompts 를 그려 state/gemini_image/ 에 저장.
키는 GEMINI_API_KEY 에서만 읽고 출력하지 않는다. 모델은 cfg.model 이 없으면 목록에서 이미지 모델을 고른다."""
import base64, json, os, sys, time, requests
cfg = json.load(open("drafts/gemini_image.json")); key = os.environ.get("GEMINI_API_KEY", "").strip()
out = "state/gemini_image"; os.makedirs(out, exist_ok=True)
if not key: print("GEMINI_API_KEY 없음"); sys.exit(1)
H = {"x-goog-api-key": key}
models = requests.get("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", headers=H, timeout=60).json().get("models", [])
img = [m["name"].split("/")[-1] for m in models if "image" in m["name"] and "generateContent" in m.get("supportedGenerationMethods", [])]
print("이미지 모델:", img)
pref = [cfg.get("model")] if cfg.get("model") else []
pref += [m for m in img if "pro" in m] + [m for m in img if "flash" in m] + img
model = next((m for m in pref if m in img), None)
if not model: print("이미지 모델 없음"); sys.exit(1)
print("사용 모델:", model)
style = cfg.get("style", "")
report = [f"model {model}"]
for it in cfg["prompts"]:
    body = {"contents": [{"parts": [{"text": (style + "\n\n" + it["prompt"]).strip()}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": it.get("aspect", "9:16")}}}
    for attempt in range(3):
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", json=body, headers=H, timeout=300)
        if r.status_code == 200: break
        print(it["name"], "HTTP", r.status_code, r.text[:300]); time.sleep(8 * (attempt + 1))
    else:
        report.append(f"{it['name']}: 실패"); continue
    ok = False
    for c in r.json().get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            d = p.get("inlineData") or p.get("inline_data")
            if d and d.get("data"):
                ext = "png" if "png" in d.get("mimeType", d.get("mime_type", "png")) else "jpg"
                open(f"{out}/{it['name']}.{ext}", "wb").write(base64.b64decode(d["data"])); ok = True; break
        if ok: break
    report.append(f"{it['name']}: {'성공' if ok else '이미지 없음 ' + json.dumps(r.json())[:200]}")
print("\n".join(report)); open(f"{out}/report.txt", "w").write("\n".join(report) + "\n")
