import re, sys, requests
url = sys.argv[1]
r = requests.get(url, timeout=45, headers={"User-Agent": "Mozilla/5.0"})
for m in sorted(set(re.findall(r"/products/[a-z0-9\-]+", r.text, re.I))):
    print(m)
