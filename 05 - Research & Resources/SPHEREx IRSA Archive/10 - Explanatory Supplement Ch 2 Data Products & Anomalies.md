---
title: "SPHEREx Explanatory Supplement Ch 2: Science Data Products, Optical Anomalies & All-Sky Cubes"
document_id: "SSDC-DP-017"
chapter: "2. The SPHEREx Data Products"
source_pdf: "https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf"
pages: "11-22"
tags:
  - nasa
  - spherex
  - explanatory-supplement
  - chapter-2
  - fits-mef
  - all-sky-cubes
  - optical-anomalies
  - snowballs
  - ghosts
  - airglow
aliases:
  - SPHEREx Ch 2 Data Products
  - SPHEREx Optical Anomalies
  - SPHEREx Cubes Specification
created: 2026-11-14
status: active
---

# 📦 SPHEREx Explanatory Supplement — Chapter 2: Science Data Products & Optical Anomalies
> **Source Document:** `SSDC-DP-017` Version 2.1 (Pages 11–22)  
> **Source PDF:** [https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf)  
> **MOC:** [[00 - Team Command Center]] | [[08 - SPHEREx Explanatory Supplement Map]] | [[09 - Explanatory Supplement Ch 1 Mission & Payload Overview]] | [[03 - SPHEREx Science Data Products & Calibration]]

---

## 🗂️ 2.1 Reprocessing Chronology & Survey Definitions
SPHEREx data products evolve across multi-epoch pipelines:
- **Year 1 Surveys (DR1 Baseline):**
  - **Survey 1 (0 to 12.5 months):** All-sky observations taken with Position Angle $\text{PA} = 0^\circ$.
  - **Survey 2 (0 to 12.5 months):** All-sky observations taken with Position Angle $\text{PA} = 180^\circ$.
- **Year 2 Surveys (QR3 $\to$ DR2 Baseline):**
  - **Survey 3 (12.5 to 25 months):** All-sky observations taken with $\text{PA} = 0^\circ$ and a **half-channel spectral shift**.
  - **Survey 4 (12.5 to 25 months):** All-sky observations taken with $\text{PA} = 180^\circ$ and a **half-channel spectral shift**.

### 🏷️ Pipeline Releases Comparison
| Pipeline Version | Release Label | Status | Key Improvements |
| :--- | :--- | :--- | :--- |
| **Pipeline 6.1 – 6.3** | **QR1** | 🛑 Retired | Initial Quick Release. Retired February 2026. |
| **Pipeline 6.4 – 6.5.6** | **QR2** | ⚠️ Deprecated | In-flight absolute gain updates. Patched with `+psffix1` on March 31, 2026 for $11 \times 11$ PSF header error. |
| **Pipeline R7.0+** | **DR1 & QR3** | 🟢 **Active Science Standard** | Comprehensive overhaul: updated persistence models, bad pixel flagging, fine astrometry, $21 \times 21$ ePSF grids, and new All-Sky Cube. |

---

## 🖼️ 2.2 Level 2 Spectral Image Architecture
Every telescope pointing produces 6 Multi-Extension FITS (MEF) files (one per detector array).
- **Physical Dimensions:** $2040 \times 2040$ pixels (excluding reference pixels).
- **File Size:** $\sim 70\text{ MB}$ uncompressed.
- **Surface Brightness Units:** **$\text{MJy/sr}$** ($1\text{ MJy/sr} = 10^{-20}\ \text{W}\cdot\text{m}^{-2}\cdot\text{Hz}^{-1}\cdot\text{sr}^{-1}$).

### 📑 6 HDU Extensions Reference
1. **`IMAGE` (HDU 1, `float32`):** Calibrated surface brightness in $\text{MJy/sr}$. Contains astronomical signal, zodiacal dust background, and atmospheric airglow.
2. **`FLAGS` (HDU 2, `int16`):** Bitmask of per-pixel data quality (see [[08 - SPHEREx Explanatory Supplement Map]] Table 16).
3. **`VARIANCE` (HDU 3, `float32`):** Propagated flux variance in $(\text{MJy/sr})^2$.
4. **`ZODI` (HDU 4, `float32`):** Estimated interplanetary zodiacal light background from the Kelsall et al. (1998) model (NOT subtracted from `IMAGE`).
5. **`ePSF` (HDU 5, `float32` 3D Cube):** Effective Point Spread Function spatial grid ($21 \times 21$ zones for Detectors 1, 2, 4, 5, 6; and **$11 \times 41$ zones for Detector 3**).
6. **`WCS-WAVE` (HDU 6, Binary Table):** 3-column FITS lookup table (`X`, `Y`, `VALUES`) mapping pixel coordinates to $[\lambda_{\text{center}}, \Delta\lambda]$.

---

## ⚡ 2.3 Image Anomalies & Instrumental Features
SPHEREx's optical train, Linear Variable Filters, and Low Earth Orbit environment introduce distinct physical artifacts:

```
SPHEREx Focal Plane Anomalies
 ├── Optical Scattering & Stray Light
 │    ├── Frame Edge Ghost: Off-axis light scattering off the LVF filter mounting bezel
 │    ├── Linear Bright Source Ghost: Internal reflection within the filter substrate
 │    ├── Dichroic Beam Splitter Ghost: Multi-bounce reflection between DBS surfaces
 │    ├── 8° Stray Light Ghost: Baffle scatter from extremely bright stars ~8° off-axis
 │    └── Moon Glint: Stray light at detector edges during near-avoidance angles (Bands 1–3)
 ├── Cosmic Ray Phenomena
 │    ├── Standard SUR Transients: Single-pixel ionization spikes during ramp clocking
 │    ├── Snowballs: Giant primary cosmic rays depositing huge charge clouds with saturated cores
 │    └── Substrate Luminescence: Weak, diffuse phosphorescence persisting across multiple ramps
 ├── Atmospheric Airglow & Spacecraft Emission
 │    ├── Metastable He I (1.083 μm): Prominent horizontal band across Band 1 following LVF contours
 │    ├── Auroral Nitrogen (N2, N): Dynamic line emission during geomagnetic oval crossings
 │    └── Shuttle Glow: Ram-facing atomic oxygen recombination glow in Band 5 (3.82–4.40 μm)
 └── Satellite & Orbital Trails
      ├── LEO Satellite Streaks: Linear trails from orbital mega-constellations (STREAK flag)
      └── Diffraction Halos: Broad halo surrounding bright satellite trails (SATELLITE_HALO flag)
```

---

## ⚠️ 2.4 Known Limitations in Spectral Images
1. **Dichroic Smile Effect (Bands 3 & 4):**
   - Optical field curvature causes curved isochromic lines near the filter edge.
   - Pixels in the corners where transmission drops $< 50\%$ are stamped with the `DICHROIC` bitmask flag (`Bit 7, 0x0080`).
2. **Astropy 0-Based vs FITS 1-Based Coordinates:**
   - FITS header keywords follow the 1-based convention (`CRPIX1 = 1.0`). Python libraries (Astropy, NumPy) use 0-based array indexing (`[0, 0]`). Software must apply a $\pm 1$ offset.

---

## 🧊 2.5 All-Sky Data Cubes (DR1 Feature)
The **All-Sky Spectral Cube** aggregates Surveys 1 & 2 into 12,288 HEALPix Order 5 tiles.

### 📐 Structural Specifications
- **Tiling Scheme:** HEALPix Order 5 in `NESTED` numbering scheme ($N_{\text{pix}} = 12 \times 4^5 = 12,288$).
- **Tile Dimensions:** $512 \times 512$ spatial pixels ($1.8^\circ \times 1.8^\circ$ field of view, $12.9''\text{/pixel}$).
- **Spectral Depth:** **102 channels** (channels 1–17 of each of the 6 detectors).
- **Zodiacal Light:** **Subtracted** (unlike Level 2 frames, the modeled `ZODI` background is cleanly removed).
- **5 HDU Layers:** `IMAGE` (MJy/sr), `NHITS` (coverage depth), `FLAGS` (propagated bitmask), `SPECTRAL_CHANNELS` (table of band centers/edges), and `WCS-WAVE`.

### ⚠️ All-Sky Cube Known Caveats
- **Blank Channels 51 and 52 (`BLANKCH`):** Channels adjacent to the dichroic splitter boundary have insufficient unmasked data in Year 1. They are filled with `NaN` (`NHITS = 0`, `FLAGS = 0`) to preserve channel numbering.
- **Airglow Striping:** The time-varying $\text{He}\ \text{I}$ line ($1.083\ \mu\text{m}$) produces scan-correlated horizontal striping across Band 1 tiles.
- **Spatial-Spectral Entanglement:** Extended nebular emission lines (e.g. $\text{Br}\alpha$ at $4.052\ \mu\text{m}$) rotate with spacecraft roll angle between visits, producing sawtooth or **moiré interference patterns** upon co-addition.
- **HiPS PNG Caveat:** The public HiPS tree has a fixed stretch ($0 - 40\ \text{MJy/sr}$ asinh) and low dynamic range; always use the FITS cubes for quantitative astrophysical analysis.

---

## 🔗 Cross-Links in Obsidian Vault
- [[08 - SPHEREx Explanatory Supplement Map]] — Full Table of Contents and Table 16 bitmask table.
- [[09 - Explanatory Supplement Ch 1 Mission & Payload Overview]] — Spacecraft orbit and dual FPA hardware.
- [[03 - SPHEREx Science Data Products & Calibration]] — Multi-Extension FITS layer definitions.
- [[06 - Special Target Comet 3I ATLAS]] — Handling spatially extended emission features.
- [[07 - SPHEREx Spectral Calibrations & Instrument Files]] — Laboratory transmission curves and channel definitions.
