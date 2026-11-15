import ssl
import urllib.request

from bs4 import BeautifulSoup

ctx = ssl._create_unverified_context()
url = "https://data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/NEOSSAT/ASTRO/2026/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    print("Links in ASTRO/2026 folder:")
    for a in soup.find_all('a', href=True)[:25]:
        print(f"  {a.get_text(strip=True)} -> {a['href']}")
except Exception as e:
    print("Error:", e)
