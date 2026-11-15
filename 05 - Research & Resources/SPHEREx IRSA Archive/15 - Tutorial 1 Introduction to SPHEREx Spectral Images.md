# 🛰️ Tutorial 1: Introduction to SPHEREx Spectral Images
> **Source URL:** [https://caltech-ipac.github.io/irsa-tutorials/spherex-intro](https://caltech-ipac.github.io/irsa-tutorials/spherex-intro)  
> **Source Platform:** Caltech / IPAC IRSA Tutorials (Jupyter Notebooks)  
> **Vault Location:** `05 - Research & Resources/SPHEREx IRSA Archive/15 - Tutorial 1 Introduction to SPHEREx Spectral Images.md`  

---

## 1. 📌 Overview & Learning Objectives

This tutorial is the foundational developer guide created by Caltech / IPAC for querying, downloading, and decomposing **SPHEREx Level-2 Spectral Image Multi-Extension FITS (MEF)** files using Astropy, Astroquery, and Firefly.

### Core Objectives:
1. **Querying SPHEREx Holdings:** Programmatic cone search across `spherex_dr1` and `spherex_qr3` collections using `astroquery.ipac.irsa.Irsa.query_sia`.
2. **Deconstructing Level-2 MEF Architecture:** Opening all 6 HDU extensions into memory and extracting science pixel arrays.
3. **Mastering the Dual WCS Architecture:**
   - Standard Spatial WCS (`WCSNAME = 'SPHEREx Distortion-corrected celestial coordinates'`).
   - Alternate Spectral WCS (`key='W'`) referencing HDU 6 lookup tables to map $(x, y)$ pixels directly to wavelength $\lambda$ ($\mu\text{m}$) and spectral bandwidth $\delta\lambda$.
4. **Interpreting Quality Flags & Bitmasks:** Decoding the `FLAGS` extension (`MSKN*` and `MSKD*` header cards).

---

## 2. 📦 Python Environment & Dependencies

```bash
pip install numpy matplotlib astropy astroquery firefly-client
```

---

## 3. 🔍 Step-by-Step Code Recipes

### Step 1: Querying Overlapping Spectral Images via SIA
```python
from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.ipac.irsa import Irsa

# Define celestial target coordinates
ra_deg = 304.693508808
dec_deg = 42.4436872991
coord = SkyCoord(ra_deg, dec_deg, unit='deg')
search_radius = 1.0 * u.arcsec

# Query both DR1 and QR3 collections simultaneously
results = Irsa.query_sia(
    pos=(coord, search_radius),
    collection=['spherex_dr1', 'spherex_qr3']
)

print(f"Found {len(results)} overlapping spectral images.")
spectral_image_url = results['access_url'][0]
print(f"Direct download URL: {spectral_image_url}")
```

### Step 2: Ingesting the 6-Extension Level 2 MEF
```python
from astropy.io import fits

# Stream MEF directly from IPAC into memory with retry logic
with fits.open(spectral_image_url, cache=True) as hdulist:
    hdulist.load()  # Load all HDU extensions into memory
    hdulist.info()
```

#### Level-2 HDU Structure:
| HDU # | EXTNAME | Data Type | Dimensions | Units | Description |
| :---: | :--- | :--- | :---: | :---: | :--- |
| `0` | `PRIMARY` | PrimaryHDU | `()` | — | Global mission metadata (`OBSID`, `DATE-OBS`, `DETECTOR`) |
| `1` | `IMAGE` | ImageHDU | `(2040, 2040)` | `MJy/sr` | Calibrated surface brightness pixel array |
| `2` | `FLAGS` | ImageHDU | `(2040, 2040)` | Integer | 32-bit data quality and artifact mask |
| `3` | `VARIANCE`| ImageHDU | `(2040, 2040)` | `(MJy/sr)²`| Per-pixel statistical variance estimate |
| `4` | `ZODI` | ImageHDU | `(2040, 2040)` | `MJy/sr` | Modeled Zodiacal light background template |
| `5` | `ePSF` | ImageHDU | `(33, 33, N)`| — | Effective Point Spread Function cube across detector |
| `6` | `WCS-WAVE`| BinTableHDU | Table | — | 1D lookup table for spectral coordinate transformation |

---

### Step 3: Resolving Spatial World Coordinates
```python
from astropy.wcs import WCS

image_header = hdulist['IMAGE'].header
spatial_wcs = WCS(image_header)

# Convert celestial center to pixel coordinates
crval_ra, crval_dec = spatial_wcs.wcs.crval
x_pix, y_pix = spatial_wcs.world_to_pixel(SkyCoord(ra=crval_ra, dec=crval_dec, unit='deg'))
print(f"Center pixel: ({x_pix:.2f}, {y_pix:.2f})")
```

---

### Step 4: Alternate Spectral WCS (`key='W'`) & Dispersion Map
Each pixel $(x, y)$ in a SPHEREx detector corresponds to a distinct observed wavelength due to the Linear Variable Filter (LVF). To convert pixel coordinates to $(\lambda, \delta\lambda)$:

```python
import numpy as np
import matplotlib.pyplot as plt

# 1. Load the Spectral WCS using key='W' and pass the full hdulist for the lookup table
spectral_wcs = WCS(header=hdulist['IMAGE'].header, fobj=hdulist, key='W')

# 2. Disable SIP distortions for spectral coordinate solution
spectral_wcs.sip = None

# 3. Compute continuous wavelength across the entire 2040x2040 detector array
y_grid, x_grid = np.indices(hdulist['IMAGE'].shape)
wavelength, bandwidth = spectral_wcs.pixel_to_world(x_grid, y_grid)

print(f"Wavelength range on detector {image_header['DETECTOR']}: {wavelength.min():.4f} to {wavelength.max():.4f} {wavelength.unit}")
```

---

### Step 5: Decoding Quality Flags (`FLAGS` Extension)
SPHEREx provides bitmask flags in HDU 2. The bit assignments are defined dynamically in the header cards `MSKN*` (mask name) and `MSKD*` (description):

| Bit # | Mask Name (`MSKN*`) | Description (`MSKD*`) | Pipeline Action |
| :---: | :--- | :--- | :--- |
| `0` | `TRANSIENT` | Transient / cosmic ray detected during SUR | Pixel rejected or flagged |
| `1` | `OVERFLOW` | A/D converter saturation during SUR | Excluded from slope fit |
| `2` | `SUR_ERROR` | Onboard flight software fit error | Bad pixel |
| `6` | `NONFUNC` | Permanently unresponsive pixel | Masked permanently |
| `7` | `DICHROIC` | Low throughput due to dichroic boundary | Reduced sensitivity |
| `9` | `MISSING_DATA` | Telemetry packet dropout | No science data |

```python
flags_header = hdulist['FLAGS'].header
flags_data = hdulist['FLAGS'].data

# Check if a target pixel has transient or nonfunctional flags
is_bad = (flags_data & (1 << 0)) | (flags_data & (1 << 6))
```

---

## 4. 🚀 Direct Alignment with SPHEREx Hunter Features

1. **Frontend Click-to-Spectrum:**
   - In `frontend/index.html`, clicking starlight queries `/api/spectrum`. The wavelength mapping logic directly reflects Step 4's LVF dispersion model ($\lambda(y)$ gradient across $A1$–$A6$).
2. **Dual-Epoch Alignment:**
   - Astropy's `WCS` spatial transform is used in our FastAPI backend (`backend/services/cutout_engine.py`) to align 2MASS 1999 frames with modern SPHEREx/DSS2 cutouts.
3. **Cosmic Ray Rejection:**
   - Our automated source discovery endpoint `/api/source_discovery` screens candidates against Bit 0 (`TRANSIENT`) to prevent false-positive asteroid dipoles.
