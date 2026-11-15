---
title: "Tutorial 4: SPHEREx Source Discovery Tool & Spectral Extraction"
document_id: "SPHEREX-TUT-04"
source_url: "https://caltech-ipac.github.io/irsa-tutorials/spherex-source-discovery-tool-demo/"
authors: "Gabriela Torrini, Andreas Faisst, SPHEREx Science Data Center (SSDC), Troy Raen, Brigitta Sipőcz, Jaladh Singhal (Caltech/IPAC-IRSA)"
updated: "2026-02-18"
tags:
  - spherex
  - caltech-ipac
  - source-discovery
  - sextractor
  - sep
  - spectral-subtraction
  - aperture-photometry
  - firefly
  - 102-band-spectrum
  - tutorial
aliases:
  - SPHEREx Source Discovery Tool
  - Caltech Tutorial 4
  - Spectral Extraction Pipeline
created: 2026-11-14
status: active
---

# 🔭 Tutorial 4: SPHEREx Source Discovery Tool & Spectral Extraction
> **Official Caltech-IPAC Tutorial:** [SPHEREx Source Discovery Tool IRSA Demo](https://caltech-ipac.github.io/irsa-tutorials/spherex-source-discovery-tool-demo/)  
> **Authors:** Gabriela Torrini, Andreas Faisst, SSDC, Troy Raen, Brigitta Sipőcz, Jaladh Singhal (Caltech/IPAC-IRSA)  
> **Core Package:** `spherex_source_discovery_tool` (with aperture photometry by Zafar Rustamkulov)  
> **Target Sky Region:** COSMOS Field ($\alpha = 150.78179^\circ, \delta = +3.35022^\circ$)  
> **MOC:** [[02 - IRSA SPHEREx Data Releases]] | [[10 - Explanatory Supplement Ch 2 Data Products & Anomalies]] | [[15 - Tutorial 1 Introduction to SPHEREx Spectral Images]] | [[16 - Tutorial 2 SPHEREx Spectral Image Cutouts & MEF Packaging]] | [[17 - Tutorial 3 Position-Dependent ePSF Reconstruction & Forward Modeling]]

---

## 📌 1. Executive Summary & Science Motivation
The **SPHEREx Source Discovery Tool (SDT)** provides the complete reference pipeline for identifying astronomical objects and extracting calibrated 102-channel spectra from Level 2 spectral images:

1. **Multi-Detector Spectral Difference Imaging ($I_{\text{D2}} - I_{\text{D4}}$):** By subtracting a shorter-wavelength image (Detector 2 SWIR: $1.10\text{--}1.62\ \mu\text{m}$) from a longer-wavelength image (Detector 4 MWIR: $2.42\text{--}3.82\ \mu\text{m}$), red astronomical sources (cold brown dwarfs, AGNs, heavily dust-obscured protostars) stand out with extreme contrast.
2. **Surface Brightness to Flux Density Calibration:** Converts raw `MJy/sr` images into absolute $\mu\text{Jy}$ using SSDC's **Solid Angle Pixel Maps (SAPM)**.
3. **Automated Source Extraction (SExtractor / SEP):** Employs non-parametric background modeling (`sep.Background`) and automated circular aperture detection.
4. **Multi-Epoch Spectrum Synthesis:** Queries all overlapping exposures across the 2-year survey, applies circular aperture photometry ($r = [3.0, 4.0, 5.0]\text{ px}$), filters 19 pipeline artifact bitmasks, and outputs 1D spectra in $\mu\text{Jy}$ and AB magnitudes.

```
                  SPHEREx Source Discovery Tool Pipeline Flow
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│ Detector 2 Image (1.10-1.62 μm) │     │ Detector 4 Image (2.42-3.82 μm) │
└────────────────┬────────────────┘     └────────────────┬────────────────┘
                 │                                       │
                 ▼                                       ▼
  Multiply by Solid Angle Pixel Map       Multiply by Solid Angle Pixel Map
  (cal-sapm: MJy/sr -> μJy/arcsec^2)      (cal-sapm: MJy/sr -> μJy/arcsec^2)
                 │                                       │
                 ▼                                       ▼
  Background Fit via sep.Background       Background Fit via sep.Background
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     ▼
                    reproject.reproject_exact(D2 -> D4)
                                     ▼
                  Spectral Difference Image: I_diff = I_D2 - I_D4
                                     ▼
                     SExtractor / SEP Source Detection
                                     ▼
                     Selected Candidate Coordinates (ra, dec)
                                     ▼
             All-Sky TAP Query for All Overlapping Exposures
                                     ▼
                  ThreadPoolExecutor(max_workers=8) Cutouts
                                     ▼
             Aperture Photometry (r = 3, 4, 5 px) + 19-Bit Flag Filter
                                     ▼
                    102-Band Calibrated Spectrum Plot (μJy / AB mag)
```

---

## 📐 2. Step 1: Calibration from Surface Brightness to Flux Density

SPHEREx Level 2 images are delivered in surface brightness units:
$$\text{BUNIT} = \text{'MJy/sr'}$$
To perform aperture photometry and multi-band difference imaging, pixel intensities must be converted to microjanskys ($\mu\text{Jy}$) per pixel using the **Solid Angle Pixel Map (SAPM)** calibration file for that detector:

$$I_{\mu\text{Jy}}(x, y) = I_{\text{MJy/sr}}(x, y) \cdot \Omega_{\text{pixel}}(x, y) \cdot 10^{12}\ \mu\text{Jy/Jy}$$

```python
import astropy.units as u
from astropy.units import Unit
from astropy.io import fits

# 1. Download Solid Angle Pixel Map from AWS S3 Open Data bucket
sapm_url = "s3://nasa-irsa-spherex/dr1/solid_angle_pixel_map/cal-sapm-v3-2026-191/2/solid_angle_pixel_map_D2_spx_cal-sapm-v3-2026-191.fits"
with fits.open(sapm_url, fsspec_kwargs={"anon": True}) as hdul_sapm:
    sapm_data = hdul_sapm["IMAGE"].data
    sapm_bunit = hdul_sapm["IMAGE"].header["BUNIT"]  # 'arcsec2'

# 2. Convert surface brightness (MJy/sr) -> flux density (μJy)
img_flux_ujy = (
    (img_data * Unit(img_hdr["BUNIT"])).to(u.uJy / u.arcsec**2) * 
    (sapm_data * Unit(sapm_bunit))
).value

img_hdr["BUNIT"] = "uJy"
```

---

## 🧹 3. Step 2: Background Removal and Flag Masking

### A. Non-Parametric Background Modeling with `sep`:
Before subtracting images, large-scale zodiacal light and diffuse Galactic emission must be subtracted. The Python `sep` package (C-based Source Extractor) fits smooth 2D spline backgrounds:

```python
import sep

# sep requires native byte-order arrays
native_data = img_flux_ujy.astype(img_flux_ujy.dtype.newbyteorder("="))

# Compute smooth background (box size 64x64, filter 11x11)
bkg = sep.Background(native_data, bw=64, bh=64, fw=11, fh=11)
clean_data = img_flux_ujy - bkg
```

### B. Bitmask Filtering:
The Level 2 `FLAGS` HDU uses bitwise flags. Tutorial 4 isolates pure science-grade pixels:
- `2097152` ($2^{21}$): Uncontaminated clean pixel.
- `2` ($2^1$): Zero/negligible overflow error.
- `0`: Completely unflagged nominal pixel.

```python
import numpy as np

# Create binary validity mask (1 = clean, NaN = bad)
mask = np.zeros(flags_data.shape) * np.nan
mask[(flags_data == 2097152) | (flags_data == 2) | (flags_data == 0)] = 1.0
```

---

## 🔄 4. Step 3: Exact Reprojection & Spectral Difference Imaging

Because Detector 2 and Detector 4 have different optical pointings, pixel scales, and orientations, Detector 2 is reprojected onto the Detector 4 astrometric grid using `reproject.reproject_exact` to guarantee total flux conservation:

```python
from reproject import reproject_exact, reproject_interp

# 1. Flux-conserving reprojection of D2 starlight onto D4 WCS grid
d2_reprojected, footprint = reproject_exact(
    input_data=(clean_d2_data, d2_hdr), 
    output_projection=d4_hdr
)
footprint[footprint == 0] = np.nan

# 2. Reproject mask using bilinear interpolation
d2_mask_reprojected, _ = reproject_interp(
    input_data=(d2_mask, d2_hdr), 
    output_projection=d4_hdr
)

# 3. Compute Spectral Difference Image
# Red objects (D4 >> D2) appear as prominent negative residuals
diff_image = (d2_reprojected - clean_d4_data) * d2_mask_reprojected * d4_mask * footprint
```

> [!TIP]
> **Why Spectral Difference Imaging is Ideal for Brown Dwarfs & Planet X:**  
> Ultra-cool brown dwarfs ($T < 700\text{ K}$) and solar system giants have deep methane ($\text{CH}_4$) and water ($\text{H}_2\text{O}$) absorption bands in Detector 2 ($1.1\text{--}1.6\ \mu\text{m}$) but exhibit strong emission windows in Detector 4 ($2.4\text{--}3.8\ \mu\text{m}$) and Detector 6 ($4.4\text{--}5.0\ \mu\text{m}$). On a $(I_{\text{D2}} - I_{\text{D4}})$ difference image, ordinary stars subtract to zero, while ultracool substellar objects glow with dramatic intensity!

---

## 🎯 5. Step 4: Multi-Epoch Aperture Photometry & 19-Bit Flag Filtering

Once candidate sources are detected, the tool extracts their complete multi-epoch spectra across all visits by running circular aperture photometry:

### The Master 19 Rejection Flags:
Photometry points are tagged contaminated if the aperture contains any of the 19 critical detector anomalies:
```python
bad_flags = [
    'TRANSIENT', 'OVERFLOW', 'SUR_ERROR', 'NONFUNC', 'DICHROIC', 
    'MISSING_DATA', 'HOT', 'COLD', 'NONLINEAR', 'CROSSTALK', 
    'GHOST', 'GHOST_FPA', 'GHOST_EXT', 'STREAK', 'PERSIST', 
    'BLOOM', 'SNOWBALL', 'HALO', 'SATELLITE_HALO'
]
```

### Photometry & Spectrum Construction:
```python
from spherex_source_discovery_tool.aperture_photometry import build_phot_table, grab_star

# 1. Perform circular aperture photometry (radii = 3.0, 4.0, 5.0 native pixels)
aperture_radii = [3.0, 4.0, 5.0]
build_phot_table(results_table, matched_candidates, aperture_radii, "ap_phot.pkl", sapm_s3)

# 2. Extract calibrated 1D spectrum for target candidate
wavelengths, band_widths, ab_mags, ab_mag_errs, fluxes_ujy, variances, n_bad = grab_star(
    obs_log_entry=phot_catalog['obs_log'][0], 
    ap_rad=3.0, 
    bad_flags=bad_flags
)
```

---

## 📊 6. Interactive Visualization: Firefly & Bokeh

Tutorial 4 integrates seamless visualization into the IPAC Firefly environment (`FireflyClient`):
- Transmits catalogs directly in memory via `io.BytesIO()` streams without writing intermediate files to disk:
  ```python
  import io
  tbl_stream = io.BytesIO()
  extracted_catalog.write(tbl_stream, format='votable')
  fc.show_table(file_input=tbl_stream, tbl_id="Candidate_Catalog", title="Extracted Sources")
  ```
- Locks multi-wavelength viewports together using `fc.align_images(lock_match=True)` so panning one detector simultaneously pans all other bands and difference images.

---

## 🚀 7. Architectural Implementation in SPHEREx Hunter

Team RIP has incorporated these principles directly into our repository:

1. **Dual Difference Imaging Modes in Frontend (`frontend/index.html`):**  
   - **Temporal Difference ($I_{t2} - I_{t1}$):** Detects moving dipoles and high proper motion objects across observation years.
   - **Spectral Difference ($I_{\text{D2}} - I_{\text{D4}}$ / $I_{\text{D1}} - I_{\text{D6}}$):** Detects static ultra-cold objects (brown dwarfs and Y-dwarfs) by color contrast.
2. **Dynamic In-Memory VOTable Streaming (`backend/api/`):**  
   Using `io.BytesIO()` to stream candidate target lists directly to Aladin Lite and Firefly clients without disk I/O bottlenecks.
3. **Automated 19-Flag Filtering:**  
   Our 102-band spectrum chart (`Chart.js`) dynamically renders error bars and gray out data points flagged by `TRANSIENT`, `SNOWBALL`, or `GHOST`.

---

## 🔗 Related Notes in Obsidian Vault
- [[02 - IRSA SPHEREx Data Releases]] — DR1 calibration and SAPM data products.
- [[10 - Explanatory Supplement Ch 2 Data Products & Anomalies]] — Taxonomy of optical anomalies and pixel flags.
- [[15 - Tutorial 1 Introduction to SPHEREx Spectral Images]] — Spectral WCS dispersion mapping.
- [[16 - Tutorial 2 SPHEREx Spectral Image Cutouts & MEF Packaging]] — Parallel cutout streaming.
- [[17 - Tutorial 3 Position-Dependent ePSF Reconstruction & Forward Modeling]] — ePSF forward modeling.
- [[SPHEREX_DR1_SITEMAP]] — Master catalog of Caltech SPHEREx tutorials.
