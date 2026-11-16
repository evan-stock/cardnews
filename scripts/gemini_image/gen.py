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
order = [cfg.get("model")] if cfg.get("model") else []
order += [m for m in img if "flash" in m and "lite" not in m] + [m for m in img if "pro" in m] + img
cands = []
for m in order:
    if m in img and m not in cands: cands.append(m)
if not cands: print("이미지 모델 없음"); sys.exit(1)
print("후보 모델:", cands)
style = cfg.get("style", "")
report = []
bad = set()
for it in cfg["prompts"]:
    body = {"contents": [{"parts": [{"text": (style + "\n\n" + it["prompt"]).strip()}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": it.get("aspect", "9:16")}}}
    ok = False
    for model in [m for m in cands if m not in bad]:
        r = None
        for attempt in range(2):
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", json=body, headers=H, timeout=300)
            if r.status_code == 200: break
            print(it["name"], model, "HTTP", r.status_code, r.text[:160].replace("\n", " "))
            if r.status_code in (429, 403, 404) and ("limit: 0" in r.text or r.status_code != 429): break
            time.sleep(10)
        if r.status_code != 200:
            if "limit: 0" in r.text or r.status_code in (403, 404): bad.add(model)
            continue
        for c in r.json().get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                d = p.get("inlineData") or p.get("inline_data")
                if d and d.get("data"):
                    ext = "png" if "png" in d.get("mimeType", d.get("mime_type", "png")) else "jpg"
                    open(f"{out}/{it['name']}.{ext}", "wb").write(base64.b64decode(d["data"])); ok = True; break
            if ok: break
        if ok: report.append(f"{it['name']}: 성공 ({model})"); break
    if not ok: report.append(f"{it['name']}: 실패")
print("\n".join(report)); open(f"{out}/report.txt", "w").write("\n".join(report) + "\n")
