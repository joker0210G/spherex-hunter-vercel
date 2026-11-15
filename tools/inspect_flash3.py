import re
import urllib.request

url = 'http://byw.tools/static/flash3.js'
headers = {'User-Agent': 'Mozilla/5.0'}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    code = resp.read().decode('utf-8', errors='ignore')

print(f"Fetched flash3.js: {len(code)} characters")
with open("flash3.js", "w", encoding="utf-8") as f:
    f.write(code)

# Find backend endpoints and APIs
urls = set(re.findall(r'https?://[^\s\'"]+', code))
print(f"\nURLs and APIs found in flash3.js ({len(urls)}):")
for u in sorted(urls):
    print("  *", u)

# Find hash parameters parsed
hash_params = re.findall(r'params\[["\']([^"\']+)["\']\]', code)
hash_params += re.findall(r'params\.([a-zA-Z0-9_]+)', code)
print(f"\nHash parameters ({len(set(hash_params))}):")
for p in sorted(set(hash_params)):
    print("  -", p)

# Check functions
funcs = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', code)
print(f"\nFunctions ({len(funcs)}):")
for f in funcs[:30]:
    print("  fn:", f)
