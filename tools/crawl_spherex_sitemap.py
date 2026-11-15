import json
import time
import urllib.request
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

start_url = 'https://irsa.ipac.caltech.edu/Missions/spherex.html'
domain = 'irsa.ipac.caltech.edu'

visited = set()
to_visit = [start_url]
sitemap = {}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

while to_visit:
    curr = to_visit.pop(0)
    if curr in visited:
        continue
    visited.add(curr)

    parsed = urlparse(curr)
    if parsed.netloc != domain:
        continue
    path = parsed.path.lower()
    if not any(k in path for k in ['spherex', 'missions/spherex', 'splices', 'comet3iatlas', 'psfhdrerr']):
        continue

    try:
        req = urllib.request.Request(curr, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            content_type = resp.headers.get_content_type()
            if 'html' not in content_type:
                sitemap[curr] = {'title': f'[Data/Binary: {content_type}]', 'internal': [], 'external': []}
                continue
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string.strip() if soup.title and soup.title.string else 'Untitled'

            internal = []
            external = []

            for a in soup.find_all('a', href=True):
                href = a['href'].strip()
                text = ' '.join(a.text.split())
                full = urljoin(curr, href)
                full_clean = full.split('#')[0]
                p = urlparse(full)
                if p.netloc == domain:
                    internal.append({'text': text, 'url': full})
                    if any(k in p.path.lower() for k in ['spherex', 'splices', 'comet3iatlas', 'psfhdrerr']) and full_clean not in visited and full_clean not in to_visit:
                        to_visit.append(full_clean)
                else:
                    external.append({'text': text, 'url': full})

            sitemap[curr] = {
                'title': title,
                'internal': internal,
                'external': external
            }
            time.sleep(0.05)
    except Exception as e:
        sitemap[curr] = {'title': f'[Error: {e}]', 'internal': [], 'external': []}

print(f"Total pages discovered: {len(sitemap)}")
with open("spherex_sitemap.json", "w", encoding="utf-8") as f:
    json.dump(sitemap, f, indent=2)

for url, data in sitemap.items():
    print(f"- {data['title']} -> {url}")
