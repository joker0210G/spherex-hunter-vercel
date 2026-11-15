import ssl
import urllib.request

from bs4 import BeautifulSoup

ctx = ssl._create_unverified_context()
url = "https://data.asc-csa.gc.ca/dataset/neossat"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

soup = BeautifulSoup(html, 'html.parser')

print("Title:", soup.title.string if soup.title else "No title")

# Look for resource tables, links, descriptions
for h in soup.find_all(['h1', 'h2', 'h3']):
    print(f"Heading: {h.get_text(strip=True)}")

print("\n--- Resource Links ---")
for a in soup.find_all('a', href=True):
    href = a['href']
    text = a.get_text(strip=True)
    if any(k in href.lower() or k in text.lower() for k in ['ftp', 'cadc', 'fits', 'download', 'dataset', 'data', 'open']):
        if len(text) > 2:
            print(f"{text} -> {href}")
