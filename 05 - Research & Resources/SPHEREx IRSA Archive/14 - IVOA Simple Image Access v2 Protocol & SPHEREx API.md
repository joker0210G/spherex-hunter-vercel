# 🛰️ IVOA Simple Image Access v2 (SIAv2) & SPHEREx API Protocols
> **Source Root:** [https://irsa.ipac.caltech.edu/ibe/sia.html](https://irsa.ipac.caltech.edu/ibe/sia.html) & [SPHEREx Data Access](https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-access)  
> **Host Archive:** NASA / IPAC Infrared Science Archive (IRSA), California Institute of Technology  
> **Standard:** International Virtual Observatory Alliance (IVOA) SIA Version 2.0  
> **Vault Location:** `05 - Research & Resources/SPHEREx IRSA Archive/13 - IVOA Simple Image Access v2 Protocol & SPHEREx API.md`

---

## 1. 📌 Overview

The IRSA implementation of the **IVOA Simple Image Access version 2 (SIAv2)** specification allows astronomers and automated pipelines to query the vast majority of IRSA holdings—spanning hundreds of millions of records—through a single, standardized REST interface.

For **SPHEREx**, SIAv2 is the primary programmatic mechanism used to search, filter, and stream:
1. **Level-2 Spectral Image Multi-Extension FITS (MEFs)** (0.75 – 5.0 $\mu\text{m}$).
2. **Spectral All-Sky Cubes** (102 nominal SPHEREx spectral channels).
3. **Deep Survey Observations** in the North and South Ecliptic Poles.

> [!NOTE]
> Static calibration products (dark frames, dichroic response profiles, nonfunctional pixel masks) are **not** served via SIAv2 and must be retrieved via on-premises browsable directories or AWS S3 open buckets.

---

## 2. 🌐 Service Endpoints & Core Collections

### Standard Endpoint
```http
GET https://irsa.ipac.caltech.edu/SIA?
```

### The 5 SPHEREx SIAv2 Collections
Because **DR1** (November 2026 reprocessed data) and **QR3** (weekly quick-release data) together supersede QR2, a comprehensive all-sky search across all active SPHEREx observations requires querying both `spherex_dr1` and `spherex_qr3`.

| Collection Parameter | Target Dataset | Astronomical Use Case |
| :--- | :--- | :--- |
| `COLLECTION=spherex_dr1` | DR1 Spectral Images (Wide Survey) | Uniform all-sky coverage across the entire sky (ignoring additional deep field passes). |
| `COLLECTION=spherex_dr1_deep` | DR1 Spectral Images (Deep Survey) | High-depth visits concentrated around the North and South Ecliptic Poles. |
| `COLLECTION=spherex_dr1_cube` | DR1 Spectral All-Sky Cubes | 102-band hyperspectral data cubes covering the celestial sphere. |
| `COLLECTION=spherex_qr3` | QR3 Spectral Images (Wide Survey) | Recent weekly quick-release data processed with updated PSF kernels. |
| `COLLECTION=spherex_qr3_deep` | QR3 Spectral Images (Deep Survey) | Recent deep field observations at the Ecliptic Poles. |

---

## 3. 🔍 Standard SIAv2 Query Parameters

| Parameter | Type / Syntax | Description & Astronomical Examples |
| :--- | :--- | :--- |
| `POS` | `CIRCLE ra dec radius`<br>`RANGE ra1 ra2 dec1 dec2`<br>`POLYGON ra1 dec1 ...` | Spatial constraint in decimal degrees (ICRS).<br>Example: `POS=circle+133.79513+-7.24515+0.05` |
| `BAND` | `min max` (in meters) | Wavelength interval in meters.<br>Example (SPHEREx 2.0 to 5.0 $\mu\text{m}$): `BAND=2.0e-6+5.0e-6` |
| `DPTYPE` | `image` or `cube` | Specifies whether searching for 2D spectral images or 3D hyperspectral cubes. |
| `EXPTIME` | `min max` (in seconds) | Integration time filter. Example: `EXPTIME=30+120` |
| `CALIB` | Integer (0 to 3) | Calibration level: `2` (Calibrated Level-2 images), `3` (Derived/mosaics). |
| `RESPONSEFORMAT` | `VOTABLE`, `HTML`, `CSV`, `IPAC_TABLE` | Desired output serialization format. |
| `MAXREC` | Integer | Maximum records returned (default unlimited; max query timeout is 5 min). |
| `CLOSEST` | `COLLECTION,FACILITY,INSTRUMENT` | Grouping modifier returning only the closest image satisfying constraints. |
| `UPLOAD` | `param:tag` or remote VOTable URL | Batch query interface supporting uploaded position catalogs. |

---

## 4. 💻 Command-Line & Python Query Recipes

### A. Wget & cURL CLI Examples
```bash
# 1. Query SPHEREx DR1 wide survey images around WISE 0855 within 0.05 deg (VOTable output)
wget -O wise0855_dr1.vot \
  "https://irsa.ipac.caltech.edu/SIA?COLLECTION=spherex_dr1&POS=circle+133.79513+-7.24515+0.05&RESPONSEFORMAT=VOTABLE"

# 2. Query both DR1 and QR3 simultaneously in CSV format
curl -o spherex_multirelease.csv \
  "https://irsa.ipac.caltech.edu/SIA?COLLECTION=spherex_dr1&COLLECTION=spherex_qr3&POS=circle+133.79513+-7.24515+0.02&RESPONSEFORMAT=CSV"

# 3. Query DR1 102-channel All-Sky Cubes
curl -o dr1_cubes.vot \
  "https://irsa.ipac.caltech.edu/SIA?COLLECTION=spherex_dr1_cube&POS=circle+133.79513+-7.24515+0.1"
```

### B. Python Access via `pyvo`
```python
import pyvo as vo

# Connect to the official IRSA SIAv2 service
sia_service = vo.dal.SIAService('https://irsa.ipac.caltech.edu/SIA')

# Execute cone search on SPHEREx DR1
results = sia_service.search(
    pos=(133.79513, -7.24515),
    size=0.05,  # degrees
    collection='spherex_dr1'
)

# Extract download URLs for matching Level-2 FITS files
for row in results:
    print(f"Title: {row.title} | Band: {row.energy_bandpassname} | URL: {row.access_url}")
```

### C. Dynamic Cutout Extraction Recipe
When a Level-2 Spectral Image MEF access URL is returned from an SIAv2 query (e.g. `https://irsa.ipac.caltech.edu/ibe/data/spherex/.../image.fits`), an on-the-fly spatial sub-image can be extracted by appending the cutout parameters directly to the base URL:
```http
https://irsa.ipac.caltech.edu/ibe/data/spherex/.../image.fits?center=133.79513,-7.24515&size=0.05
```

---

## 5. 🎯 Integration with Team RIP's Architecture

1. **Automated Cutout Backend (`backend/services/cutout_engine.py`):**
   - Can fall back directly to `COLLECTION=spherex_dr1` via SIAv2 when live IRSA FinderChart queries time out.
2. **Deep Field vs. Wide Field Selector:**
   - Supports selecting `spherex_dr1_deep` for high-depth ecliptic pole targets.
3. **Direct Cube Streaming:**
   - Enables direct slicing of 102-band spectral cubes using `COLLECTION=spherex_dr1_cube`.
