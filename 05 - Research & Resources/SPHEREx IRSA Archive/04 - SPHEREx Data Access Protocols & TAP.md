---
title: "NASA IRSA SPHEREx Data Access Protocols: SIAv2, TAP, IBE & AWS Cloud S3"
url: "https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-access"
tags:
  - nasa
  - spherex
  - irsa
  - protocols
  - siav2
  - tap
  - adql
  - python
  - aws-s3
aliases:
  - SPHEREx Data Access
  - SPHEREx SIAv2
  - SPHEREx TAP
  - SPHEREx Cloud
created: 2026-11-14
status: active
---

# 🌐 NASA IRSA SPHEREx Data Access Protocols & Query Interfaces
> **Primary Source:** [https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-access](https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-access)  
> **Host Archive:** NASA / IPAC Infrared Science Archive (IRSA), California Institute of Technology  
> **MOC:** [[00 - Team Command Center]] | [[01 - IRSA SPHEREx Mission Hub]] | [[02 - IRSA SPHEREx Data Releases]] | [[03 - SPHEREx Science Data Products & Calibration]] | [[SPHEREx Documentation & Public Archive]]

---

## 🏛️ Two Tier Infrastructure: On-Premises & AWS Cloud
IRSA serves SPHEREx data concurrently from two redundant infrastructures:
1. **On-Premises IPAC Storage (Caltech):**
   - Root URL: `https://irsa.ipac.caltech.edu/ibe/data/spherex/`
   - Powers the interactive SPHEREx Data Explorer, live cutout server, and IVOA endpoints.
2. **Amazon Web Services (AWS) Cloud Open Data:**
   - Public S3 Bucket: `s3://nasa-irsa-spherex/`
   - Designed for high-throughput cloud batch processing, serverless AWS Lambda pipelines, and cloud EC2 analysis without egress bandwidth bottlenecks.

---

## 📡 1. IVOA Simple Image Access (SIAv2) Protocol
IRSA exposes programmatic access to SPHEREx Level 2 Spectral Image MEFs and Level 3 All-Sky Cubes through version 2 of the IVOA Simple Image Access protocol.

* **Base Endpoint:** `https://irsa.ipac.caltech.edu/SIA?`

### 📦 The 5 Official SPHEREx SIAv2 Collections
| Collection Identifier | Description & Sky Coverage | Use Case Recommendation |
| :--- | :--- | :--- |
| `spherex_dr1` | DR1 Wide Survey Spectral Image MEFs | Uniform all-sky science across Surveys 1 & 2. |
| `spherex_dr1_deep` | DR1 Deep Survey Spectral Image MEFs | Deep field exposures near North/South Ecliptic Poles. |
| `spherex_dr1_cube` | DR1 All-Sky Spectral Cubes (HEALPix) | Full-sky 102-channel continuum extraction. |
| `spherex_qr3` | QR3 Wide Survey Spectral Image MEFs | Current Surveys 3 & 4 weekly rolling exposures. |
| `spherex_qr3_deep` | QR3 Deep Survey Spectral Image MEFs | High-cadence Deep Field monitoring. |

> [!TIP]
> **Complete Mission Query:** To search all active SPHEREx exposures, submit concurrent SIAv2 queries across both `spherex_dr1` and `spherex_qr3`.

### 💻 CLI Query Examples (`curl` & `wget`)
```bash
# Query DR1 Wide Survey cone of radius 0.01 deg around Barnard's Star
curl -o spherex_dr1_results.vot \
  "https://irsa.ipac.caltech.edu/SIA?COLLECTION=spherex_dr1&POS=circle+269.45208+4.69339+0.01&RESPONSEFORMAT=VOTABLE"

# Query QR3 Wide Survey cone around WISE 0855
wget -O spherex_qr3_results.html \
  "https://irsa.ipac.caltech.edu/SIA?COLLECTION=spherex_qr3&POS=circle+133.84271+-7.24072+0.01&RESPONSEFORMAT=HTML"
```

The returned VOTable includes:
- `access_url`: HTTPS on-premises link for direct IPAC download.
- `cloud_access`: Corresponding direct `s3://` S3 URI on AWS.

---

## ✂️ 2. Dynamic Spatial Cutout API
Rather than downloading full 70 MB Level 2 MEF files ($2040 \times 2040$ pixels), IRSA's Image-Based Environmental (IBE) service generates dynamic spatial cutouts on the fly.

### 🔗 Dynamic Cutout Syntax
Append `?center=RA,Dec&size=Degrees` to any on-premises FITS file URL:
```
https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/level2/[Planning_Period]/[Version]/[Detector]/[Filename].fits?center=[RA],[DEC]&size=[FOV_DEG]
```

### 💻 Example Live Cutout Request
```bash
curl -o wise0855_cutout.fits \
  "https://irsa.ipac.caltech.edu/ibe/data/spherex/qr3/level2/2026W21_2A/l2b-v27-2026-268/1/level2_2026W21_2A_0001_2D1_spx_l2b-v27-2026-268.fits?center=133.84271,-7.24072&size=0.05"
```
The returned FITS retains the full 6-extension MEF structure (`IMAGE`, `FLAGS`, `VARIANCE`, `ZODI`, `ePSF`, `WCS-WAVE`) cropped specifically to the region of interest.

---

## 🐍 3. Python Integration (`pyvo` & `astroquery`)

### A. High-Level Querying with `astroquery.ipac.irsa`
```python
from astroquery.ipac.irsa import Irsa
from astropy.coordinates import SkyCoord
import astropy.units as u

# Target coordinates (WISE 0855)
coord = SkyCoord(ra=133.84271*u.deg, dec=-7.24072*u.deg, frame='icrs')

# Query SIA2 collection for DR1
table = Irsa.query_sia(
    pos=coord,
    size=0.02 * u.deg,
    collection='spherex_dr1'
)

print(f"Found {len(table)} overlapping SPHEREx DR1 spectral frames.")
for row in table:
    print(f"Band: {row['energy_bandpassname']} | Access URL: {row['access_url']}")
```

### B. Table Access Protocol (TAP) & ADQL with `pyvo`
```python
import pyvo as vo

# Connect to IRSA TAP service
service = vo.dal.TAPService("https://irsa.ipac.caltech.edu/TAP")

# ADQL spatial query on SPHEREx observation plane
query = """
SELECT p.obs_id, p.band, p.exp_time, p.ra, p.dec, p.access_url
FROM spherex.plane p
WHERE CONTAINS(POINT('ICRS', p.ra, p.dec), CIRCLE('ICRS', 133.84271, -7.24072, 0.05)) = 1
  AND p.release_status = 'DR1'
ORDER BY p.band ASC
"""

results = service.search(query)
df = results.to_table().to_pandas()
print(df.head())
```

---

## 🗄️ 4. On-Premises Browsable Directory Hierarchy (IBE)
For direct file tree navigation and bulk mirror scripting (`rsync` / `wget -r`), files are structured systematically:

```
https://irsa.ipac.caltech.edu/ibe/data/spherex/
 ├── dr1/
 │    ├── level2/[Planning_Period]/l2b-v[Ver]-[Date]/[Detector]/
 │    ├── hips5_cube/hips_20261026/Norder5/Dir[DirNum]/
 │    ├── abs_gain_matrix/cal-agm-v[Ver]-[Date]/[Detector]/
 │    ├── epsf/cal-epsf-v[Ver]-[Date]/[Detector]/
 │    ├── dark/cal-drk-v[Ver]-[Date]/[Detector]/
 │    ├── dichroic/base-[Date]/[Detector]/
 │    └── ... (calibrations)
 ├── qr3/
 │    └── level2/[Planning_Period]/...
 └── qr2/
      └── level2/ (direct download open until Feb 2027)
```

---

## 🔗 Cross-Links in Obsidian Vault
- [[01 - IRSA SPHEREx Mission Hub]] — Mission characteristics and tools.
- [[02 - IRSA SPHEREx Data Releases]] — DR1 vs QR2/QR3 details.
- [[03 - SPHEREx Science Data Products & Calibration]] — MEF extensions and HEALPix cube specifications.
- [[05 - SPLICES Ice Source Catalog]] — Querying target catalogs via Gator and TAP.
- [[Useful Libraries & Astropy Cheat Sheet]] — Astropy / Astroquery code snippets.
