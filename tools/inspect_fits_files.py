import ssl
import urllib.request

from bs4 import BeautifulSoup

ctx = ssl._create_unverified_context()
url = "https://data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/NEOSSAT/ASTRO/2026/001/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    print("Files in ASTRO/2026/001/ folder:")
    files = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.fits')]
    print(f"Total FITS files: {len(files)}")
    for f in files[:10]:
        print(f"  {f}")
except Exception as e:
    print("Error:", e)
