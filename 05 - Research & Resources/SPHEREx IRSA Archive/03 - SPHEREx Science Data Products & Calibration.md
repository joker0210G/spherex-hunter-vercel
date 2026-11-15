---
title: "NASA IRSA SPHEREx Data Products, MEF FITS Layers & Calibration Pipeline"
url: "https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-products"
tags:
  - nasa
  - spherex
  - irsa
  - fits-mef
  - all-sky-cube
  - epsf
  - calibration
  - spectroscopy
aliases:
  - SPHEREx Data Products
  - SPHEREx MEF Architecture
  - SPHEREx Calibrations
created: 2026-11-14
status: active
---

# 🔬 NASA IRSA SPHEREx Science Data Products & Calibration Architecture
> **Primary Source:** [https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-products](https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-products)  
> **Host Archive:** NASA / IPAC Infrared Science Archive (IRSA), California Institute of Technology  
> **MOC:** [[00 - Team Command Center]] | [[01 - IRSA SPHEREx Mission Hub]] | [[02 - IRSA SPHEREx Data Releases]] | [[SPHEREx Documentation & Public Archive]]

---

## 📂 Summary of Primary Data Products
The SPHEREx archive delivers data across three structural tiers:
1. **Level 2 Spectral Image Multi-Extension FITS (MEF):** Pointing-level calibrated frames ($2040 \times 2040$ px, $\sim 70\text{ MB}$ each).
2. **Level 3 All-Sky Spectral Cubes (DR1 Only):** 12,288 HEALPix Order 5 tiles covering all 102 channels ($512 \times 512 \times 102$ px).
3. **Instrumental Calibration & Artifact Templates:** Optical distortion (SIP), detector noise, gain matrices, and atmospheric emission templates.

---

## 1. 🖼️ Level 2 Spectral Image Multi-Extension FITS (MEF)
Every telescope pointing produces **6 Spectral MEFs** (one for each detector array `D1`–`D6`). Each file contains **6 extensions**:

| Extension Name | Data Type | Dimensions | Units | Physical Description & Pipeline Notes |
| :--- | :--- | :--- | :--- | :--- |
| `IMAGE` | `float32` | $2040 \times 2040$ | $\text{MJy/sr}$ | Calibrated surface brightness. **Zodiacal light is NOT subtracted.** |
| `FLAGS` | `int16` | $2040 \times 2040$ | Bitmask | Per-pixel status & data quality bitmask (cosmic rays, nonfunctional pixels, saturation). |
| `VARIANCE` | `float32` | $2040 \times 2040$ | $(\text{MJy/sr})^2$ | Propagated photometric flux variance. |
| `ZODI` | `float32` | $2040 \times 2040$ | $\text{MJy/sr}$ | Spatially modeled zodiacal light background (Kelsall et al. 1998 model fitted with satellite solar aspect angle). |
| `ePSF` / `PSF` | `float32` 3D Cube | Varies by Release | Normalized | **DR1 & QR3 (ePSF):** Multi-zone effective PSF grid ($21 \times 21$ zones for D1, D2, D4, D5, D6; $11 \times 41$ zones for D3).<br>**QR2 (PSF):** $11 \times 11$ grid (121 planes, $101 \times 101$ px each). |
| `WCS-WAVE` | Binary Table | $1 \text{ row} \times 3 \text{ cols}$ | $\mu\text{m}$ / nm | Spectral WCS lookup table containing spatial control points (`X`, `Y`) and corresponding `VALUES` ($[\lambda_{\text{center}}, \Delta\lambda]$). Bilinear interpolation yields $\lambda_c$ accurate to $< 1\text{ nm}$. |

### 🏷️ Level 2 Filename Standard
```
level2_[Observation ID]D[Detector]_spx_l2b-v[Version]-[Processing Date].fits
```
*Example:* `level2_2025W18_2B_0001_1D1_spx_l2b-v12-2025-164.fits`
- `2025W18_2B`: Survey Planning Period ($\sim 3.5\text{ days}$).
- `0001`: Large slew counter.
- `1`: Small slew counter within the pointing cluster.
- `D1`: Detector Array 1.
- `v12`: Pipeline version.
- `2025-164`: Processing date (Day 164 of 2025).

---

## 2. 🧊 DR1 All-Sky Spectral Data Cube (Order 5 HEALPix)
Introduced in **DR1 (November 2026)**, the All-Sky Cube aggregates all Level 2 exposures into a seamless, zodiacal-subtracted 3D spectral volume.

### 🌐 Geometric & Spectral Specifications
- **Tiling Scheme:** HEALPix Order 5 in `NESTED` numbering scheme $\to$ **12,288 total sky tiles**.
- **Tile Coverage:** Approximately $1.8^\circ \times 1.8^\circ$ per tile.
- **Pixel Scale:** $12.9''\text{ / pixel}$ ($512 \times 512$ spatial pixels per tile).
- **Spectral Depth:** **102 channels** (channels 1–17 of each of the 6 detectors).
- **Zodiacal Background:** **Subtracted** (unlike Level 2 frames, the `ZODI` component is removed to reveal faint diffuse extragalactic background light).

### 📑 All-Sky Cube FITS Extensions (5 HDUs)
1. `IMAGE`: Surface brightness cube in $\text{MJy/sr}$ ($512 \times 512 \times 102$).
2. `NHITS`: Integer exposure coverage cube counting how many input raw pixels contributed to each voxel ($512 \times 512 \times 102$).
3. `FLAGS`: Propagated quality bitmask cube ($512 \times 512 \times 102$).
4. `SPECTRAL_CHANNELS`: Binary table documenting edge and central wavelengths for all 102 channels.
5. `WCS-WAVE`: Global spectral WCS lookup table.

### ⚠️ All-Sky Cube Caveats & Known Artifacts
- **Blank Channels 51 & 52:** Located directly adjacent to the physical dichroic beam splitter boundary ($2.40 - 2.42\ \mu\text{m}$). These channels contain no data and are flagged with the `BLANKCH` FITS header keyword.
- **Atmospheric Emission Stripes:** Upper-atmospheric emission lines—most prominently the **$\text{He}\ \text{I}$ line at $1.083\ \mu\text{m}$ in Band 1**—create linear striping across tiles aligned with satellite orbital motion.
- **HEALPix HPX Distortion:** Standard FITS viewers (e.g. older DS9 builds) do not handle the HPX projection natively, causing apparent trapezoidal stretching near tile edges.

---

## 3. 🎯 Point Spread Function Architecture: ePSF vs PSF
SPHEREx employs two Point Spread Function paradigms:

### A. DR1 & QR3: Effective PSF (`ePSF`)
- Rather than a simple exposure average, `ePSF` models sub-pixel intra-pixel sensitivity variations and jitter.
- **Detector 1, 2, 4, 5, 6 Grid:** $21 \times 21$ spatial zones across the $2\text{K} \times 2\text{K}$ detector.
- **Detector 3 Grid:** **$11 \times 41$ spatial zones** (higher sampling along the dispersion axis to account for optical aberration and steep filter transmission gradients in the $1.64 - 2.40\ \mu\text{m}$ array).

### B. QR2: Legacy Empirical PSF (`PSF`)
- Represented as a FITS cube with 121 planes ($11 \times 11$ zones across the detector), each plane sized $101 \times 101$ pixels.
- *Note:* Subject to the [[02 - IRSA SPHEREx Data Releases]] header erratum; corrected via `VERSION = '6.5.x+psffix1'` and superseded by `ePSF`.

---

## 4. 🧰 Standalone Instrumental Calibration Products
IRSA provides standalone calibration files matching every mission epoch:

| Product Name | Format & Dimensions | Units / Content | File Naming Pattern |
| :--- | :--- | :--- | :--- |
| **Absolute Gain Matrix** | FITS Image ($2040 \times 2040$) | Flat-field photon-to-DN gain | `abs_gain_matrix_D[D]_spx_cal-agm-v[V]-[Date].fits` |
| **Dark Current Map** | FITS Image ($2040 \times 2040$) | $\text{e}^-/\text{s}$ thermally generated counts | `dark_D[D]_spx_cal-drk-v[V]-[Date].fits` |
| **Dichroic Transmission** | FITS Image ($2040 \times 2040$) | Transmittance factor ($0.0 - 1.0$) | `dichroic_D[D]_spx_base-[Date].fits` |
| **Electronic Gain Factors** | YAML File | 32 pre-amp readout channel gains | `gain_factors_spx_base-[Date].yaml` |
| **SIP Optical Distortion** | FITS Header | Simple Imaging Polynomial coefficients | `sip_D[D]_spx_cal-sip-v[V]-[Date].fits` |
| **Solid Angle Pixel Map** | FITS Image ($2040 \times 2040$) | $\text{arcsec}^2$ per physical pixel | `solid_angle_pixel_map_D[D]_spx_cal-sapm-v[V]-[Date].fits` |
| **Nonfunctional Pixel Mask**| FITS Image ($2040 \times 2040$) | $1 = \text{dead/hot pixel},\ 0 = \text{nominal}$ | `nonfunc_v[V]_D[D]_spx_base-[Date].fits` |
| **Read Noise Parameters** | 2-Extension FITS ($2040 \times 2040$) | Electrons ($\text{READNOISE-1}$, $\text{READNOISE-2}$) | `readnoise_pars_D[D]_spx_base-[Date].fits` |
| **Nonlinearity Parameters** | 5-Extension FITS ($2040 \times 2040$) | Coefficients ($Q_{nl}, b_1, b_2, b_3, Q_{max}$) | `nonlinear_pars_D[D]_spx_base-[Date].fits` |
| **L3 Flux Corrections** | FITS Image ($2040 \times 2040$) | Scaling linking QR2 gain to QR3/DR1 | `l3_flux_corrections_D[D]_spx_cal-flxc-v[V]-[Date].fits` |

---

## 5. 🌌 Atmospheric & Spacecraft Emission Templates
SPHEREx operates in Low Earth Orbit (LEO, $\sim 700\text{ km}$ altitude), encountering transient atmospheric glow features modeled in DR1 & QR3:

1. **Auroral Line Template (Detector 1 Only):**
   - Models atomic and molecular nitrogen ($N_2, N$) emission in the upper thermosphere within the $0.75 - 1.10\ \mu\text{m}$ bandpass.
   - File: `aurora_template_D1_spx_base-[Date].fits`
2. **Helium Emission Template (Detectors 1 & 2):**
   - Corrects for the prominent resonant metastable neutral Helium line ($\text{He}\ \text{I}$ triplet at $\lambda = 1.0830\ \mu\text{m}$).
   - File: `he_template_D[1-2]_spx_base-[Date].fits`
3. **Spacecraft Shuttle Glow Template (Detector 5 Only):**
   - Corrects for surface recombination of atomic oxygen on the spacecraft ram-facing surfaces, emitting continuum radiation in the $3.82 - 4.40\ \mu\text{m}$ ice absorption window.
   - File: `shuttle_glow_template_D5_spx_base-[Date].fits`
4. **Crosstalk Parameters (Types 1, 2, 3):**
   - ECSV tables parameterizing capacitive coupling between readout channels:
     - Type 1: Vertically displaced electronic ghosts.
     - Type 2: Horizontally displaced electronic ghosts.
     - Type 3: Streak-like blooming along fast-read rows.

---

## 🔗 Cross-Links in Obsidian Vault
- [[01 - IRSA SPHEREx Mission Hub]] — Hardware specifications and science goals.
- [[02 - IRSA SPHEREx Data Releases]] — Pipeline version history and release dates.
- [[04 - SPHEREx Data Access Protocols & TAP]] — Querying Level 2 and All-Sky Cube products via TAP & SIAv2.
- [[Useful Libraries & Astropy Cheat Sheet]] — Working with Astropy FITS cutouts and WCS reprojection.
