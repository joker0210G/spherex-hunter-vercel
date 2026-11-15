import json
import urllib.parse
import urllib.request

url = 'https://n7z4i9pzx8.execute-api.us-west-2.amazonaws.com/prod/catalog/gaiadr2'
ra = 133.786245
dec = -7.244372
size_deg = (176.0 / 3600.0) * 2.75

adql = f"SELECT ra, dec, parallax, pmra, pmdec FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT('ICRS',ra,dec), CIRCLE('ICRS',{ra},{dec},{size_deg}))"
params = {
    'request': 'doQuery',
    'lang': 'adql',
    'format': 'json',
    'query': adql
}
data_bytes = urllib.parse.urlencode(params).encode('utf-8')
req = urllib.request.Request(url, data=data_bytes, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print('Gaia Proxy Response keys:', list(res.keys()))
        rows = res.get('data', [])
        print(f'Discovered {len(rows)} Gaia DR3 stars in FOV.')
        for r in rows[:5]:
            print('  Star:', r)
except Exception as e:
    print('Error querying Gaia proxy:', e)
