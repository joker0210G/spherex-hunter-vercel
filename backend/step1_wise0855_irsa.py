"""
🛰️ SPHEREx / WISE Cutout & Metadata Query Script
NASA Space Apps 2026 - Team RIP

Target: WISE 0855-0714 (Fast-moving cold brown dwarf)
Coordinates: RA = 133.79513 deg (08h 55m 10.831s), Dec = -7.24515 deg (-07d 14m 42.53s)
"""

import json
import ssl
import urllib.parse
import urllib.request

# 1. Target Coordinates (WISE 0855)
TARGET_NAME = "WISE 0855-0714"
RA_DEG = 133.79513
DEC_DEG = -7.24515
CUTOUT_SIZE_DEG = 0.01  # ~36 arcseconds (tight patch around target)

print("=" * 65)
print(f"🛰️ STEP 1: QUERYING IRSA ARCHIVE FOR {TARGET_NAME}")
print(f"   RA: {RA_DEG:.5f}° | Dec: {DEC_DEG:.5f}° | Patch: {CUTOUT_SIZE_DEG}°")
print("=" * 65)

# 2. NASA IRSA TAP (Table Access Protocol) Endpoint
# SPHEREx data and multi-epoch infrared surveys (WISE/NEOWISE) are served by IRSA
IRSA_TAP_URL = "https://irsa.ipac.caltech.edu/TAP/sync"

# TAP SQL Query: Find images overlapping this position sorted by observation time
# Using NEOWISE-R single exposure table (neowiser_p1bs_psd) as the multi-epoch baseline
query = f"""
SELECT TOP 10
    mjd,
    date_obs,
    scan_id,
    frame_num,
    ra,
    dec,
    w1mpro,
    w2mpro
FROM allwise_p3as_psd
WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {RA_DEG}, {DEC_DEG}, {CUTOUT_SIZE_DEG})) = 1
ORDER BY date_obs ASC
"""

params = {
    "REQUEST": "doQuery",
    "LANG": "ADQL",
    "FORMAT": "json",
    "QUERY": query
}

print("\n📡 Sending TAP query to NASA IRSA...")

try:
    encoded_url = f"{IRSA_TAP_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(encoded_url, headers={'User-Agent': 'SPHEREx-Hunter/1.0 (NASA Space Apps Team RIP)'})
    ssl_ctx = ssl._create_unverified_context()

    with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))

        fields = [col['name'] for col in data.get('metadata', [])]
        rows = data.get('data', [])

        print(f"✅ Success! Found {len(rows)} observation records covering this coordinate.\n")
        print(f"{'Date Observed':<22} | {'RA (deg)':<10} | {'Dec (deg)':<10} | {'W2 Mag (4.6μm)':<12}")
        print("-" * 65)

        for row in rows:
            row_dict = dict(zip(fields, row))
            date_obs = str(row_dict.get('date_obs', 'N/A'))[:19]
            ra = float(row_dict.get('ra', 0))
            dec = float(row_dict.get('dec', 0))
            w2 = row_dict.get('w2mpro', 'N/A')
            print(f"{date_obs:<22} | {ra:<10.5f} | {dec:<10.5f} | {str(w2):<12}")

except Exception as e:
    print(f"ℹ️ Note: Live TAP query returned: {e}")
    print("No data was fabricated as a substitute. Re-run when NASA IRSA is reachable.")

print("\nDone.")
