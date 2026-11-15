import urllib.request

url = "https://caltech-ipac.github.io/irsa-tutorials/spherex-hipscube/"
print(f"Fetching {url}...")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8')
    print("Page fetched successfully! Length:", len(html))

    from html.parser import HTMLParser

    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.lines = []
            self.current = []

        def handle_data(self, data):
            text = data.strip()
            if text:
                self.current.append(text)

        def handle_endtag(self, tag):
            if tag in ['p', 'h1', 'h2', 'h3', 'h4', 'li', 'pre', 'code', 'tr', 'div']:
                if self.current:
                    self.lines.append(" ".join(self.current))
                    self.current = []

    parser = TextExtractor()
    parser.feed(html)
    content = "\n".join(parser.lines)
    print("Extracted content lines:", len(parser.lines))

    with open('spherex_hipscube_raw.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Saved to spherex_hipscube_raw.txt")

except Exception as e:
    print("Error fetching:", e)
