import urllib.request

from bs4 import BeautifulSoup

url = 'http://byw.tools/wiseview'
headers = {'User-Agent': 'Mozilla/5.0'}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=12) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

soup = BeautifulSoup(html, 'html.parser')

print(f"Total HTML Length: {len(html)} bytes")

# External scripts and links
scripts = [s.get('src') for s in soup.find_all('script') if s.get('src')]
stylesheets = [l.get('href') for l in soup.find_all('link') if l.get('rel') == ['stylesheet']]
print(f"Scripts ({len(scripts)}): {scripts}")
print(f"Stylesheets ({len(stylesheets)}): {stylesheets}")

# Inline scripts analysis
inline_scripts = soup.find_all('script', src=False)
print(f"Inline script tags: {len(inline_scripts)}")

# All headings, divs, modals
print("\n=== Containers & Sections ===")
for elem in soup.find_all(['h1', 'h2', 'h3', 'h4', 'legend']):
    print(f"[{elem.name.upper()}] {elem.get_text(strip=True)}")

# Inputs and Controls
print("\n=== All Input Elements ===")
for tag in soup.find_all(['input', 'select', 'button']):
    tid = tag.get('id', '')
    tname = tag.get('name', '')
    ttype = tag.get('type', '')
    tval = tag.get('value', '')
    print(f"{tag.name:6s} | id: {tid:20s} | name: {tname:15s} | type: {ttype:10s} | val: {tval}")

with open("wiseview_source.html", "w", encoding="utf-8") as f:
    f.write(html)
