---
title: "Tutorial 2: SPHEREx Spectral Image Cutouts & MEF Packaging"
document_id: "SPHEREX-TUT-02"
source_url: "https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/"
authors: "Vandana Desai, Jessica Krick, Andreas Faisst, Troy Raen, Brigitta Sipőcz (Caltech/IPAC-IRSA)"
updated: "2026-03-05"
tags:
  - spherex
  - caltech-ipac
  - cutouts
  - tap
  - adql
  - parallel-processing
  - spectral-wcs
  - mef-fits
  - tutorial
aliases:
  - SPHEREx Cutouts Tutorial
  - Caltech Tutorial 2
  - Multi-Extension Cutouts Packaging
created: 2026-11-14
status: active
---

# 🌌 Tutorial 2: SPHEREx Spectral Image Cutouts & MEF Packaging
> **Official Caltech-IPAC Tutorial:** [Download a collection of SPHEREx Spectral Image cutouts as a multi-extension FITS file](https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/)  
> **Authors:** Vandana Desai, Jessica Krick, Andreas Faisst, Troy Raen, Brigitta Sipőcz (Caltech/IPAC-IRSA)  
> **Target Object:** Pinwheel Galaxy (M101: $\alpha = 210.80227^\circ, \delta = +54.34895^\circ$), Detector `SPHEREx-D2`  
> **MOC:** [[02 - IRSA SPHEREx Data Releases]] | [[04 - SPHEREx Data Access Protocols & TAP]] | [[14 - IVOA Simple Image Access v2 Protocol & SPHEREx API]] | [[15 - Tutorial 1 Introduction to SPHEREx Spectral Images]]

---

## 📌 1. Tutorial Objectives & Overview
This official Caltech/IPAC notebook provides the standard reference implementation for:
1. **Dynamic Cutout URL Generation via TAP:** Querying the `spherex.artifact` and `spherex.plane` database tables to construct sub-image cutout URLs on the fly.
2. **Spectral Dispersion Extraction:** Using Astropy's alternate WCS (`key='W'`) with SIP nullification (`sip = None`) to compute the exact observing wavelength ($\lambda_{\text{center}}$) at the target coordinates for each exposure.
3. **High-Throughput Parallel Streaming:** Benchmarking serial vs multi-threaded downloading (`ThreadPoolExecutor`), achieving a **10x speedup** ($2.26\text{ min} \to 0.22\text{ min}$).
4. **Custom Master Multi-Extension FITS (MEF) Packaging:** Consolidating tens or hundreds of individual multi-epoch cutouts into a single self-describing FITS file containing a catalog index HDU (`CUTOUT_INFO`) and enumerated data HDUs (`IMAGE1`, `FLAGS1`, `VARIANCE1`, etc.).

```
                         SPHEREx Target Coordinate (RA, Dec)
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         ADQL TAP Table Query                             Dynamic SIAv2 Query
   (spherex.artifact + spherex.plane)               (IBE dynamic cutout service)
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          ▼
                      List of Cutout URIs + Metadata
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  │   ThreadPoolExecutor(max_workers=10)          │
                  │   • Parallel FITS stream (10x faster)         │
                  │   • Extract Spectral WCS: λ_center (μm)       │
                  │   • Preserve primary header VERSION           │
                  │   • Rename HDUs: EXTNAME = {TYPE}{index}      │
                  └───────────────────────┬───────────────────────┘
                                          ▼
                         Master Packaged Science MEF
                  ├── [0] PrimaryHDU (Blank global root)
                  ├── [1] BinTableHDU ('CUTOUT_INFO' index table)
                  └── [2...N] Enumerated Cutout HDUs (IMAGE, FLAGS, VAR...)
```

---

## 🛰️ 2. Step 1: Dynamic Cutout URL Construction via TAP

While SIAv2 provides a simple cone-search interface, IRSA TAP allows astronomers to query all data immediately upon weekly ingestion and dynamically construct the server-side cutout URLs in SQL.

```python
import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.ipac.irsa import Irsa
import time

# 1. Target Coordinates: Pinwheel Galaxy (M101)
coord = SkyCoord(ra=210.80227 * u.degree, dec=54.34895 * u.degree, frame="icrs")
size = 0.1 * u.degree  # 6 arcmin cutout
bandpass = 'SPHEREx-D2' # Detector 2: 1.20 - 1.87 μm

# 2. ADQL Query string synthesizing dynamic cutout URI
query = f"""
SELECT
    'https://irsa.ipac.caltech.edu/' || a.uri || '?center={coord.ra.deg},{coord.dec.deg}d&size={size.value}' AS uri,
    p.time_bounds_lower
FROM spherex.artifact a
JOIN spherex.plane p ON a.planeid = p.planeid
WHERE 1 = CONTAINS(POINT('ICRS', {coord.ra.deg}, {coord.dec.deg}), p.poly)
        AND p.energy_bandpassname = '{bandpass}'
ORDER BY p.time_bounds_lower
"""

t1 = time.time()
results = Irsa.query_tap(query)
print(f"Time to execute TAP query: {time.time() - t1:.2f} s")
print(f"Number of exposures overlapping M101: {len(results)}")
# Returns: 84 overlapping spectral exposures
```

---

## 🔬 3. Step 2: Per-Cutout Processing & Spectral WCS Extraction

Each downloaded SPHEREx cutout is an MEF containing 7 HDUs (Primary Header + 6 extensions: `IMAGE`, `FLAGS`, `VARIANCE`, `ZODI`, `EPSF`, `WCS-WAVE`). Because the Linear Variable Filter (LVF) disperses starlight continuously across the focal plane, starlight at $(\alpha, \delta)$ has a unique wavelength depending on where it fell on the detector in each visit.

```python
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

def process_cutout(row, coord, cache=False):
    """
    Downloads a SPHEREx cutout, computes the wavelength at the center pixel,
    preserves pipeline provenance, and extracts HDUs.
    """
    with fits.open(row["uri"], cache=cache) as hdulist:
        header = hdulist[1].header

        # 1. Spatial WCS: celestial world -> pixel (x, y)
        spatial_wcs = WCS(header)
        x, y = spatial_wcs.world_to_pixel(coord)

        # 2. Spectral WCS: pixel (x, y) -> wavelength (microns)
        spectral_wcs = WCS(header, fobj=hdulist, key="W")
        spectral_wcs.sip = None  # Crucial: nullify spatial SIP distortions for spectral WCS
        wavelength, bandwidth = spectral_wcs.pixel_to_world(x, y)
        
        row["central_wavelength"] = wavelength.to(u.micrometer).value

        # 3. Preserve pipeline version from primary header (e.g. 'l2b-v27-2026-198')
        row["version"] = hdulist[0].header.get("VERSION", "")

        # 4. Enumerate and copy HDUs to keep memory valid after close
        hdus = []
        for hdu in hdulist[1:]:
            hdu.header["EXTNAME"] = f"{hdu.header['EXTNAME']}{row['cutout_index']}"
            hdus.append(hdu.copy())
            
        row["hdus"] = hdus
```

> [!IMPORTANT]
> **Why `spectral_wcs.sip = None` is mandatory:**  
> The spatial FITS header contains 4th-order Simple Imaging Polynomial (`SIP`) distortion coefficients (`A_ORDER=4`, `B_ORDER=4`) for geometric sky mapping. If not stripped from the alternate `W` header, Astropy attempts to evaluate spatial SIP distortion on the 1D wavelength dispersion axis, generating runtime calculation errors!

---

## ⚡ 4. Step 3: High-Throughput Parallel Download Benchmark

The tutorial explicitly contrasts serial execution with multi-threaded downloads using Python's `concurrent.futures.ThreadPoolExecutor`:

| Processing Mode | Worker Count | Total Exposures | Benchmark Time | Speedup Factor |
| :--- | :---: | :---: | :---: | :---: |
| **Serial (`for` loop)** | 1 | 84 Cutouts | **2.26 minutes** (135 s) | $1.0\times$ (Baseline) |
| **Parallel (`ThreadPoolExecutor`)** | 10 | 84 Cutouts | **0.22 minutes** (13.2 s) | **$10.3\times$ Faster!** |

### Parallel Implementation Recipe:
```python
import concurrent.futures

results_table = results.to_table()
results_table["cutout_index"] = range(1, len(results_table) + 1)
results_table["central_wavelength"] = np.full(len(results_table), np.nan)
results_table["version"] = np.full(len(results_table), "", dtype="U32")
results_table["hdus"] = np.full(len(results_table), None)

# Run with 10 threads
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_cutout_with_error_handling, row, coord, False)
               for row in results_table]
    concurrent.futures.wait(futures)

# Filter out transient network disconnects
valid_cutouts = results_table[results_table["hdus"] != None]
print(f"Successfully downloaded {len(valid_cutouts)} cutouts in parallel.")
```

---

## 📦 5. Step 4: Packaging into a Master Multi-Extension FITS (MEF)

To prevent researchers from managing hundreds of loose `.fits` files on disk, the notebook synthesizes a single, self-describing master FITS file.

### Structure of the Master Packaged MEF:
1. **HDU 0 (`PrimaryHDU`):** Blank global header container.
2. **HDU 1 (`CUTOUT_INFO`):** Binary FITS table containing catalog columns:
   - `cutout_index` (`int32` / `J`)
   - `observation_date` (`float64` / `D`, units: days)
   - `central_wavelength` (`float64` / `D`, units: $\mu\text{m}$)
   - `version` (`str` / `A32`)
   - `access_url` (`str` / `A200`)
3. **HDUs 2 through $N$ (`Data HDUs`):**
   - `IMAGE1`, `FLAGS1`, `VARIANCE1`, `ZODI1`, `EPSF1`, `WCS-WAVE1`
   - `IMAGE2`, `FLAGS2`, `VARIANCE2`, `ZODI2`, `EPSF2`, `WCS-WAVE2`
   - ... up to `IMAGE84`.

```python
# 1. Build summary table HDU
cols = fits.ColDefs([
    fits.Column(name="cutout_index", format="J", array=valid_cutouts["cutout_index"], unit=""),
    fits.Column(name="observation_date", format="D", array=valid_cutouts["time_bounds_lower"], unit="d"),
    fits.Column(name="central_wavelength", format="D", array=valid_cutouts["central_wavelength"], unit="um"),
    fits.Column(name="version", format="A32", array=valid_cutouts["version"], unit=""),
    fits.Column(name="access_url", format="A200", array=valid_cutouts["uri"], unit=""),
])
table_hdu = fits.BinTableHDU.from_columns(cols)
table_hdu.header["EXTNAME"] = "CUTOUT_INFO"

# 2. Assemble Master HDUList
primary_hdu = fits.PrimaryHDU()
hdulist_list = [primary_hdu, table_hdu]
hdulist_list.extend(hdu for fits_hdulist in valid_cutouts["hdus"] for hdu in fits_hdulist)
combined_hdulist = fits.HDUList(hdulist_list)

# 3. Stream to disk
output_filename = "M101_spherex_cutouts_mef.fits"
combined_hdulist.writeto(output_filename, overwrite=True)
```

---

## 📊 6. Step 5: Visualizing Multi-Channel Spectral Evolution

Once packaged, extracting starlight across all visits requires just a few lines of Astropy code:

```python
from astropy.table import Table
import matplotlib.pyplot as plt

# Read summary catalog
summary_table = Table.read(output_filename, hdu=1)
wavelengths = summary_table["central_wavelength"].quantity

# Plot first 10 spectral slices with log stretch
fig, axs = plt.subplots(2, 5, figsize=(16, 6))
with fits.open(output_filename) as hdul:
    for i in range(10):
        ax = axs.flat[i]
        idx = summary_table["cutout_index"][i]
        data = hdul[f"IMAGE{idx}"].data
        wl = wavelengths[i]
        
        ax.imshow(data, norm="log", origin="lower", cmap="inferno")
        ax.text(0.05, 0.05, rf"$\lambda = {wl.value:.4f}\,\mu\text{{m}}$", 
                color="white", transform=ax.transAxes, fontsize=10, weight="bold")
        ax.axis("off")
plt.tight_layout()
plt.show()
```

---

## 🚀 7. Key Takeaways for Team RIP (SPHEREx Hunter)

1. **Adopt `ThreadPoolExecutor(max_workers=10)` in Backend:**  
   In `backend/services/spherex_service.py`, our multi-visit cutout fetcher should use concurrent threads instead of serial requests, reducing target load times from ~15 seconds to under 2 seconds.
2. **Dynamic URL Synthesis Pattern:**  
   The SQL string concatenation `'https://irsa.ipac.caltech.edu/' || a.uri || '?center=...&size=...'` allows us to bypass intermediate API calls and stream cutouts directly from IRSA's cache.
3. **Master MEF Export Feature:**  
   In our frontend `#fitsModal`, we can offer astronomers a **"Download Complete Multi-Epoch MEF"** button that bundles all 102 channels + the `CUTOUT_INFO` summary table into a single authenticated FITS package ready for Astropy or SAOImage DS9.

---

## 🔗 Related Notes in Obsidian Vault
- [[02 - IRSA SPHEREx Data Releases]] — DR1 and QR3 data specifications.
- [[04 - SPHEREx Data Access Protocols & TAP]] — ADQL query protocols.
- [[14 - IVOA Simple Image Access v2 Protocol & SPHEREx API]] — Direct SIAv2 endpoints.
- [[15 - Tutorial 1 Introduction to SPHEREx Spectral Images]] — FITS 6-extension architecture and WCS.
- [[SPHEREX_DR1_SITEMAP]] — Master catalog of all 6 Caltech tutorials.
