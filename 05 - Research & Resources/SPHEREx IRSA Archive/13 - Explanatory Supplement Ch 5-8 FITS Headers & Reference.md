---
title: "SPHEREx Explanatory Supplement Ch 5-8: FITS Header Schemas, Calibration Tables & Acronyms"
document_id: "SSDC-DP-017"
chapters: "5. Spectral Image Header, 6. Gain Matrix Header, 7. EPSF Header, 8. Acronyms"
source_pdf: "https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf"
pages: "73-84"
tags:
  - nasa
  - spherex
  - explanatory-supplement
  - fits-headers
  - sip-distortion
  - calibration-provenance
  - acronyms
aliases:
  - SPHEREx Ch 5-8 Reference
  - SPHEREx FITS Header Reference
  - SPHEREx Acronym Index
created: 2026-11-14
status: active
---

# 📜 SPHEREx Explanatory Supplement — Chapters 5–8: FITS Header Schemas & Acronyms
> **Source Document:** `SSDC-DP-017` Version 2.1 (Pages 73–84)  
> **Source PDF:** [https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf)  
> **MOC:** [[00 - Team Command Center]] | [[08 - SPHEREx Explanatory Supplement Map]] | [[10 - Explanatory Supplement Ch 2 Data Products & Anomalies]] | [[11 - Explanatory Supplement Ch 3 Data Processing Pipeline]] | [[12 - Explanatory Supplement Ch 4 Calibrations & Instrument Models]]

---

## 📑 Chapter 5: Level 2 Spectral Image Header Schema (Table A.35)
Every Level 2 Spectral Image MEF file contains standardized metadata keywords across the primary and extension HDUs:

### 1. Core Observation & Telemetry Keywords
| FITS Keyword | Example Value | Physical Meaning & Range |
| :--- | :--- | :--- |
| `TELESCOP` | `'SPHEREx'` | NASA SPHEREx space observatory |
| `INSTRUME` | `'SPHEREx-LVF'` | Wide Field Linear Variable Filter Spectrograph |
| `DETECTOR` | `4` | Detector Array index ($1\text{--}3 = \text{SWIR}$, $4\text{--}6 = \text{MWIR}$) |
| `OBSID` | `'2025W17_4B_0458_1'` | Planning period `2025W17_4B`, large slew `0458`, small slew `1` |
| `BUNIT` | `'MJy/sr'` | Standardized calibrated surface brightness unit |
| `EXPTIME` | `110.51` | Total exposure integration time (seconds) |
| `SURDLY` | `1.5349` | SUR sample frame clock interval ($T_{\text{fr}}$) |
| `SURLIM` | `16` | Maximum non-destructive reads in ramp |
| `RA_CENT` | `269.45208` | Bore-sight Right Ascension pointing center (deg, J2000) |
| `DEC_CENT`| `+4.69339` | Bore-sight Declination pointing center (deg, J2000) |
| `PA` | `0.0` or `180.0` | Spacecraft roll Position Angle (determines Survey 1 vs 2, or 3 vs 4) |

### 2. Pipeline Certification & Astrometry Flags
| FITS Keyword | Value | Certification Rule |
| :--- | :--- | :--- |
| `L2DQA` | `'PASS'` / `'FAIL'` | Level 2 Data Quality Assessment status |
| `FINAST` | `0` (Good) or `> 0` | Fine astrometric solution flag (`0` confirms Gaia DR3 convergence $< 0.1''$) |
| `L2.N_COLD` | `2037` | Number of unresponsive cold pixels masked |
| `L2.N_HOT` | `1412` | Number of unstable hot dark-current pixels masked |
| `L2.N_TRAN_NB`| `24856` | Number of transient/cosmic-ray neighbor pixels |

### 3. WCS & Simple Imaging Polynomial (SIP) Distortion
```
CTYPE1  = 'RA---TAN-SIP'           / Gnomonic projection with SIP polynomials
CTYPE2  = 'DEC--TAN-SIP'
CRVAL1  = 269.4520833             / Reference Right Ascension
CRVAL2  = 4.6933889               / Reference Declination
CRPIX1  = 1020.5                  / Detector center pixel (1-based)
CRPIX2  = 1020.5
CD1_1   = -0.00172222             / Pixel scale matrix (~6.2 arcsec/pixel)
CD2_2   = +0.00172222
A_ORDER = 4                       / Forward SIP polynomial degree
B_ORDER = 4
AP_ORDER= 4                       / Inverse SIP polynomial degree
BP_ORDER= 4
```

### 4. Calibration Provenance (`HISTORY` Cards)
Every Level 2 file records the exact calibration files and pipeline modules executed:
```
HISTORY Apply Bad Pixel Mask, SSDC-MS-013 v1.1
HISTORY Apply Flat Field and Photometric Calibration, SSDC-MS-014 v1.5
HISTORY Estimate Fine Astrometry, SSDC-MS-016 v2.5
HISTORY Create Source Mask, SSDC-MS-019 v3.5
HISTORY Detect Outlier Pixels, SSDC-MS-020 v1.4
HISTORY Get Zodi Model, SSDC-MS-022 v2.3
HISTORY Measure Per-Exposure PSF, SSDC-MS-023 v3.3
HISTORY Create Spectral Image, SSDC-MS-024 v2.2
HISTORY Perform Data Quality Assessment for Level 2, SSDC-MS-025 v1.4
HISTORY [CALIB] abs_gain_matrix 019f4f95-6173-79cb-872b-f0f8abd8ed65
HISTORY [CALIB] dark 019f4f96-1086-7845-9c97-d9a1076a80ed
HISTORY [CALIB] epsf 019f4f97-864d-7bee-8722-a634bea7288f
HISTORY [CALIB] sip 019f4f98-7f49-79e3-9a45-85e5641166aa
HISTORY [CALIB] spectral_wcs 019f4f99-3265-766b-b368-e28eb08fdbed
```

---

## 🧮 Chapter 6: Absolute Gain Matrix Header Schema (Table B.1)
- **HDU Type:** `IMAGE` (`BITPIX = -32`, $2040 \times 2040$).
- **Conversion Factor:** `BUNIT = 'MJy/sr / (e-/s)'` — multiplies raw electronic slope maps directly into calibrated surface brightness.
- **Reference Date:** `CAL_DATE = '2026-10-26'`.

---

## 🎯 Chapter 7: Effective Point Spread Function Header Schema (Table C.1)
- **HDU Type:** `BINTABLE` (`XTENSION = 'BINTABLE'`).
- **Binary Table Structure:**
  - `ZONE_ID`: Spatial zone identifier ($0\text{--}440$).
  - `X_ZONE`, `Y_ZONE`: Central detector coordinates of zone.
  - `EPSF_ARRAY`: $33 \times 33$ oversampled floating-point image array.
  - `NEFF_MEAN`: Mean effective pixel footprint size ($N_{\text{eff}} = 1/\sum p_i^2$).
  - `NEFF_STD`: Spatial standard deviation of PSF width.
  - `WAVELENGTH`: Nominal channel central wavelength ($\mu\text{m}$).

---

## 📚 Chapter 8: Master Acronym Reference Index
Compiled from Appendix D (Pages 83–84):

| Acronym | Complete Expansion | Scientific / Engineering Context |
| :--- | :--- | :--- |
| **ADCS** | Attitude Determination and Control Subsystem | Spacecraft 3-axis pointing and slewing |
| **ADU** | Analog Digital Units | Raw uncalibrated detector counts |
| **ASIC** | Application-Specific Integrated Circuit | Custom Video8 cryogenic readout electronics |
| **BCP** | Ball Configurable Platform | BCP-100 spacecraft bus |
| **CDS** | Correlated Double Sampling | Electronic readout noise reduction |
| **DBS** | Dichroic Beam Splitter | Separates SWIR (reflection) and MWIR (transmission) beams |
| **DQA** | Data Quality Assessment | Automated pipeline validation certification |
| **EBL** | Extragalactic Background Light | Cosmic diffuse infrared background |
| **ePSF** | Effective Point Spread Function | Sub-pixel intra-pixel empirical PSF model |
| **FPA** | Focal Plane Assembly | Cryogenic detector housing (SWIR 62 K, MWIR 45 K) |
| **H2RG** | Hawaii-2RG | Teledyne $2048 \times 2048$ HgCdTe detector arrays |
| **HEALPix** | Hierarchical Equal Area isoLatitude Pixelization | Order 5 all-sky tiling geometry (12,288 tiles) |
| **HiPS** | Hierarchical Progressive Surveys | Multi-resolution progressive sky map |
| **IOC** | In-Orbit Checkout | Initial commissioning phase (March–April 2025) |
| **IPAC** | Infrared Processing and Analysis Center | Science Operations Center at Caltech |
| **IRSA** | Infrared Science Archive | NASA astrophysics data repository |
| **LVF** | Linear Variable Filter | Continuous dispersion filter mounted on FPAs |
| **MEF** | Multi-Extension FITS | 6-HDU calibrated data container |
| **MIDEX** | Medium-class Explorer | NASA astrophysics flight program |
| **MLTAN** | Mean Local Time of Ascending Node | Dawn-dusk sun-synchronous orbit parameter (6:00 AM) |
| **MOST** | Moving Object Search Tool | IRSA solar system ephemeris cross-match service |
| **NEP / SEP**| North / South Ecliptic Pole | SPHEREx Deep Survey fields |
| **PA** | Position Angle | Spacecraft roll orientation ($0^\circ$ vs $180^\circ$) |
| **SIP** | Simple Imaging Polynomial | FITS non-linear geometric distortion format |
| **SPLICES** | SPHEREx Target List of Ice Sources | 8.6M+ point source ice absorption catalog |
| **SPS** | Survey Planning Software | Mission scheduling system at Arizona State / JPL |
| **SSDC** | SPHEREx Science Data Center | Processing pipeline facility at IPAC/Caltech |
| **SUR** | Sample-Up-the-Ramp | Non-destructive continuous detector clocking mode |
| **TVAC** | Thermal Vacuum Chamber | Cryogenic laboratory test environment at KASI/Caltech |
| **YSO** | Young Stellar Object | Circumstellar ice absorption science targets |

---

## 🔗 Cross-Links in Obsidian Vault
- [[08 - SPHEREx Explanatory Supplement Map]] — Document master table of contents.
- [[09 - Explanatory Supplement Ch 1 Mission & Payload Overview]] — Hardware specs and launch details.
- [[10 - Explanatory Supplement Ch 2 Data Products & Anomalies]] — MEF structure and optical anomalies.
- [[11 - Explanatory Supplement Ch 3 Data Processing Pipeline]] — Robberto (2007) variance and 12-step pipeline.
- [[12 - Explanatory Supplement Ch 4 Calibrations & Instrument Models]] — Absolute gain and 102-channel wavelength tables.
- [[SPHEREx Documentation & Public Archive]] — Master vault index.
