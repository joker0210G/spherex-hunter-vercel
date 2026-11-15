import ssl
import urllib.request

ctx = ssl._create_unverified_context()
url = "https://data.asc-csa.gc.ca/dataset/neossat"
print(f"Fetching {url}...")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    print("Page fetched! Length:", len(html))
    from html.parser import HTMLParser
    class SimpleParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.lines = []
            self.current = []
        def handle_data(self, data):
            t = data.strip()
            if t: self.current.append(t)
        def handle_endtag(self, tag):
            if tag in ['p', 'h1', 'h2', 'h3', 'li', 'td', 'a']:
                if self.current:
                    self.lines.append(" ".join(self.current))
                    self.current = []
    p = SimpleParser()
    p.feed(html)
    for line in p.lines[:40]:
        print(line[:120])
except Exception as e:
    print("Error:", e)
