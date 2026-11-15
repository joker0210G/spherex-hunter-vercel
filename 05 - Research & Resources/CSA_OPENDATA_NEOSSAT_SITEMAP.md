---
title: "Government of Canada Open Data NEOSSat Dataset & FITS Architecture"
document_id: "CSA-OPENDATA-NEOSSAT-01"
portal_url: "https://data.asc-csa.gc.ca/dataset/neossat"
open_gov_url: "https://open.canada.ca/data/en/dataset/b25bf396-857e-407d-94c7-e6f772fa8d57"
api_endpoint: "https://donnees-data.asc-csa.gc.ca/api/action/package_show?id=62d8033b-87b6-4322-8d5f-e26bebf934c1"
astro_bucket: "https://data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/NEOSSAT/ASTRO/"
supporting_docs: "https://donnees-data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/NEOSSAT/Supporting%20Documents/"
license: "Open Government Licence - Canada"
tags:
  - neossat
  - csa
  - open-data
  - canada
  - fits-architecture
  - asteroid-tracking
  - space-surveillance
aliases:
  - CSA OpenData NEOSSat Sitemap
  - Open Canada NEOSSat Dataset
  - NEOSSat Open Data Architecture
created: 2026-11-14
status: active
---

# 🍁 Government of Canada Open Data NEOSSat Dataset & FITS Architecture
> **Primary Portal:** [https://data.asc-csa.gc.ca/dataset/neossat](https://data.asc-csa.gc.ca/dataset/neossat)  
> **Direct Open Access Bucket:** [https://data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/NEOSSAT/ASTRO/](https://data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/NEOSSAT/ASTRO/)  
> **API Metadata Endpoint:** `https://donnees-data.asc-csa.gc.ca/api/action/package_show?id=62d8033b-87b6-4322-8d5f-e26bebf934c1`  
> **User Manual:** `CSA-NEOSSAT-MAN-0002_FITS_IMAGE_UGUIDE-v4-00.pdf`  
> **MOC:** [[00 - Team Command Center]] | [[CSA_NEOSSAT_SITEMAP]] | [[CADC_CANADIAN_ARCHIVE_SITEMAP]] | [[NEOSSAT_TUTORIAL_CODE_CODEX]]

---

## 📌 1. Executive Summary & Mission Infrastructure
The **Near-Earth Object Surveillance Satellite (NEOSSat)**, launched February 25, 2013, is Canada's dedicated microsatellite for space surveillance and astronomy. Operating in an 800 km Sun-synchronous dawn-dusk polar orbit, NEOSSat continuously tracks Near-Earth Asteroids (NEOs), comets, exoplanet transits, and artificial satellites without Day/Night atmospheric downtime.

Through the **Government of Canada Open Data Portal**, the Canadian Space Agency (CSA) provides completely open, unauthenticated public access to over **13 years of space imagery** (2013 to present) through an open HTTP directory tree and CKAN REST API.

```
                    Government of Canada NEOSSat Open Data Tree
┌─────────────────────────────────────────────────────────────────────────────┐
│ https://data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/NEOSSAT/     │
├─────────────────────────────────────────────────────────────────────────────┤
│ ├── ASTRO/                       ◄── Astronomical observations (2017 - 2026) │
│ │    ├── 2017/ ... 2026/         ◄── Partitioned by Observation Year        │
│ │    │    ├── 001/ ... 366/      ◄── Partitioned by Day of Year (DDD)       │
│ │    │    │    ├── NEOS_SCI_YYYYDDDHHMMSS.fits.gz      (Raw Science)        │
│ │    │    │    ├── NEOS_SCI_YYYYDDDHHMMSS_cor.fits.gz  (Overscan Bias Corr) │
│ │    │    │    └── NEOS_SCI_YYYYDDDHHMMSS_cord.fits.gz (Bias + Dark Corr)   │
│ │    └── NESS/                   ◄── Near-Earth Space Surveillance files     │
│ ├── XML/                         ◄── Machine-readable Observation Manifests  │
│ └── Supporting Documents/        ◄── Technical Manuals & Dictionaries        │
│      ├── CSA-NEOSSAT-MAN-0002_FITS_IMAGE_UGUIDE-v4-00.pdf                   │
│      ├── NEOSSat supporting document.docx                                   │
│      └── neossat-experience-v1.5.pdf                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 2. FITS Calibration Suffixes & Image Processing Levels

Each observation produces three distinct levels of FITS files in the `ASTRO/` directory:

| Filename Pattern | Calibration Stage | Description & Pipeline State |
| :--- | :---: | :--- |
| `NEOS_SCI_YYYYDDDHHMMSS.fits.gz` | **Raw (Level 0)** | Uncalibrated detector telemetry containing raw pixel counts, 50-pixel overscan columns, and bias offsets. |
| `NEOS_SCI_YYYYDDDHHMMSS_cor.fits.gz` | **Bias-Corrected (Level 1)** | Corrected for electronic bias using row-by-row median subtraction of the 50-column unilluminated overscan region. |
| `NEOS_SCI_YYYYDDDHHMMSS_cord.fits.gz` | **Science-Ready (Level 2)** | **Fully calibrated:** Bias-subtracted + thermal dark-current subtracted using master dark frames scaled to exposure time. |

### Filename Anatomy:
Example: `NEOS_SCI_2026001002151_cord.fits.gz`
- `NEOS`: Spacecraft identifier (NEOSSat).
- `SCI`: Science imaging observation (vs `ENG` for engineering or `CAL` for calibration).
- `2026`: Gregorian year of observation.
- `001`: Day of Year (January 1).
- `002151`: Time of mid-exposure in UTC (`00:21:51` UTC).
- `_cord`: Calibrated science product (corrected bias + dark subtracted).
- `.fits.gz`: Gzip-compressed Flexible Image Transport System file.

---

## 🛠️ 3. Programmatic Open Data Harvesting (Python Recipe)

Because the CSA open data tree is standard Apache directory browsing, astronomers can harvest images programmatically using standard HTTP clients without API keys:

```python
import urllib.request
import ssl
import re

# Bypassing local Windows CA bundle issues
ctx = ssl._create_unverified_context()

def get_neossat_images(year: int, day_of_year: int, calibrated_only: bool = True) -> list:
    """
    Retrieves all available NEOSSat FITS files for a specific day from CSA Open Data.
    """
    base_url = f"https://data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/NEOSSAT/ASTRO/{year}/{day_of_year:03d}/"
    req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    with urllib.request.urlopen(req, context=ctx) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        
    pattern = r'href="(NEOS_SCI_[^"]+_cord\.fits\.gz)"' if calibrated_only else r'href="(NEOS_SCI_[^"]+\.fits\.gz)"'
    files = re.findall(pattern, html)
    return [base_url + f for f in files]

# Example: Fetch calibrated images for 2026 Day 1
images = get_neossat_images(2026, 1, calibrated_only=True)
print(f"Discovered {len(images)} calibrated NEOSSat images on 2026-001:")
for img_url in images[:5]:
    print(f"  -> {img_url}")
```

---

## 📡 4. CKAN REST API Integration (`package_show`)

The dataset is cataloged in Canada's CKAN registry. The complete dataset state, licensing, contact emails, and resource URLs can be monitored via the Open Government API:

- **Endpoint:** `https://donnees-data.asc-csa.gc.ca/api/action/package_show?id=62d8033b-87b6-4322-8d5f-e26bebf934c1`
- **Output Schema:**
  - `title`: `"NEOSSAT - Astronomy Data"`
  - `license_title`: `"Open Government Licence - Canada"`
  - `resources`: Array of direct links to FTP/HTTP directories, CADC, XML manifests, and PDF manuals.
  - `maintainer_email`: `gouvernementouvert-opengovernment@asc-csa.gc.ca`

---

## 🚀 5. Integration into SPHEREx Hunter

Team RIP leverages the CSA Open Data repository for:
1. **Asteroid & Satellite Cross-Filtering:**  
   When a user in SPHEREx Hunter observes a moving dipole or optical transient, our backend can cross-query NEOSSat observations for that Julian Date to confirm whether a cataloged near-Earth asteroid (NEO) or space debris crossed the field of view.
2. **Direct FITS Streaming for Asteroid Observers:**  
   Our `#fitsModal` provides direct links to the matching `_cord.fits.gz` file in CSA's open bucket for immediate secondary photometric analysis in DS9 or Astropy.

---

## 🔗 Related Notes in Obsidian Vault
- [[CSA_NEOSSAT_SITEMAP]] — Comprehensive spacecraft specs, 10 Guest Observer cycles, and orbit telemetry.
- [[CADC_CANADIAN_ARCHIVE_SITEMAP]] — CADC CAOM-2 TAP access and SSOIS solar system image search.
- [[NEOSSAT_TUTORIAL_CODE_CODEX]] — Line Segment Detector (LSD) streaklet detection algorithms.
- [[NASA_AND_PARTNER_DATA_PORTALS]] — Master registry of 8 official astronomical data archives.
