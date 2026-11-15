import urllib.request

url = "http://byw.tools/pawnstars?ra=133.786245&dec=-7.244372&size=704"
print(f"Querying {url}...")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = resp.read().decode('utf-8')
        print("Response:", data[:300])
except Exception as e:
    print("Error:", e)
