import json
import ssl
import urllib.request

ctx = ssl._create_unverified_context()
url = "https://donnees-data.asc-csa.gc.ca/api/action/package_show?id=62d8033b-87b6-4322-8d5f-e26bebf934c1"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    print("API Response Success:", data.get('success'))
    res = data.get('result', {})
    print("Title:", res.get('title'))
    print("Notes:", res.get('notes', '')[:300])
    print("\nResources:")
    for r in res.get('resources', []):
        print(f"- {r.get('name')} | Format: {r.get('format')} | URL: {r.get('url')}")
except Exception as e:
    print("Error:", e)
