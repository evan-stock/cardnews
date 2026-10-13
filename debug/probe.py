import json, re, requests
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36","Accept-Language":"en,ko;q=0.8","Accept":"text/html,application/xhtml+xml,image/avif,image/webp,*/*"}
urls=["https://www.cbsnews.com/baltimore/news/stolen-kitten-bank-robbery-beltsville-maryland/",
"https://www.nbcwashington.com/news/local/magnolia-stolen-kitten-used-in-attempted-bank-robbery-finds-a-forever-family/4139557/",
"https://www.dailymail.co.uk/news/index.html","https://nypost.com/","https://www.bbc.com/news"]
out={}
for u in urls:
    r={}
    try:
        x=requests.get(u,headers=UA,timeout=25);r["direct"]=[x.status_code,len(x.text)];og=re.findall(r'og:image["\'][^>]*content=["\']([^"\']+)',x.text)[:2];r["og"]=og
    except Exception as e: r["direct"]=str(e)[:80]
    try:
        x=requests.get("https://r.jina.ai/"+u,timeout=40);r["jina"]=[x.status_code,len(x.text)];r["jina_imgs"]=re.findall(r'!\[[^\]]*\]\((https?://[^)\s]+)',x.text)[:5]
    except Exception as e: r["jina"]=str(e)[:80]
    imgs=(r.get("og") or [])+(r.get("jina_imgs") or [])
    if imgs:
        i=imgs[0]
        try:
            x=requests.get(i,headers={**UA,"Referer":u},timeout=25);r["img_direct"]=[x.status_code,x.headers.get("content-type"),len(x.content)]
        except Exception as e: r["img_direct"]=str(e)[:80]
        try:
            x=requests.get("https://images.weserv.nl/",params={"url":i,"w":1280,"output":"jpg"},timeout=30);r["img_weserv"]=[x.status_code,x.headers.get("content-type"),len(x.content)]
        except Exception as e: r["img_weserv"]=str(e)[:80]
    out[u]=r
json.dump(out,open("debug/probe_result.json","w"),indent=1)
print(json.dumps(out,indent=1))
