---
title: "NASA SPHEREx Explanatory Supplement: Document Map & Technical Index"
document_id: "SSDC-DP-017"
version: "2.1 (2026-11-10)"
url: "https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf"
pages: 84
tags:
  - nasa
  - spherex
  - explanatory-supplement
  - ssdc
  - documentation
  - bitmask
  - pipeline
  - fits-headers
aliases:
  - SPHEREx Explanatory Supplement
  - SSDC-DP-017
  - SPHEREx Technical Manual
created: 2026-11-14
status: active
---

# 📖 NASA SPHEREx Explanatory Supplement (SSDC-DP-017 v2.1)
> **Source PDF:** [https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf)  
> **Document Identifier:** `SSDC-DP-017`, Version 2.1 (Released **November 10, 2026** for DR1)  
> **Authors:** SPHEREx Science Data Center (SSDC) & SPHEREx Science Team (Akeson, Bock, Doré, Ashby, Crill, Korngut, et al.)  
> **Total Length:** 84 pages  
> **MOC:** [[00 - Team Command Center]] | [[01 - IRSA SPHEREx Mission Hub]] | [[02 - IRSA SPHEREx Data Releases]] | [[03 - SPHEREx Science Data Products & Calibration]] | [[SPHEREx Documentation & Public Archive]]

---

## 🗺️ Complete Document Structural Map & Outline

```
SPHEREx Explanatory Supplement (SSDC-DP-017 v2.1)
 ├── 1. Mission Overview (p. 4)
 │    ├── 1.1 Mission Objectives (p. 4)
 │    ├── 1.2 Spacecraft (p. 4)
 │    ├── 1.3 Payload (p. 5)
 │    ├── 1.4 Survey Strategy and Spectral Accumulation (p. 7)
 │    ├── 1.5 Mission and Science Operations Summary (p. 9)
 │    └── 1.6 Acknowledgments (p. 10)
 ├── 2. The SPHEREx Data Products (p. 11)
 │    ├── 2.1 Reprocessing and Quick Release Versions (p. 11)
 │    ├── 2.2 Spectral Images (p. 11)
 │    ├── 2.3 Image Anomalies and Features (p. 14)
 │    ├── 2.4 Spectral Image Known Limitations (p. 18)
 │    └── 2.5 All-Sky Data Cubes (p. 21)
 │         ├── 2.5.1 Data Format (p. 21)
 │         └── 2.5.2 Known Issues (p. 22)
 ├── 3. The SPHEREx Data Processing (p. 23)
 │    ├── 3.1 Data Ingestion and Raw Image Processing (p. 23)
 │    ├── 3.2 Processing Steps (p. 24)
 │    │    ├── 3.2.1 Source Blooming, Snowball and Transient Halo Flagging (p. 24)
 │    │    ├── 3.2.2 Nonlinearity Correction (p. 28)
 │    │    ├── 3.2.3 Variance Map (p. 29)
 │    │    ├── 3.2.4 Persistence Masks (p. 30)
 │    │    ├── 3.2.5 Bad Pixel Flagging (p. 32)
 │    │    ├── 3.2.6 Dark Subtraction (p. 35)
 │    │    ├── 3.2.7 Absolute Gain Correction (p. 35)
 │    │    ├── 3.2.8 Astrometry (p. 35)
 │    │    ├── 3.2.9 Source Masks (p. 38)
 │    │    ├── 3.2.10 Outlier Pixel Detection (p. 41)
 │    │    ├── 3.2.11 Zodi Prediction (p. 41)
 │    │    └── 3.2.12 Level 2 DQA (p. 42)
 │    ├── 3.3 Photometric Measurements (p. 42)
 │    └── 3.4 Mosaics (p. 46)
 │         ├── 3.4.1 Overview (p. 46)
 │         ├── 3.4.2 Input Data (p. 46)
 │         ├── 3.4.3 Data Loading and Preprocessing (p. 46)
 │         ├── 3.4.4 Spectral Channel Definition (p. 47)
 │         ├── 3.4.5 Mosaic Grid (p. 47)
 │         ├── 3.4.6 Reprojection Algorithm (p. 48)
 │         ├── 3.4.7 Mosaic Building Process (p. 48)
 │         ├── 3.4.8 Output File (p. 49)
 │         ├── 3.4.9 Data Quality and Flagging (p. 50)
 │         └── 3.4.10 Known Issues (p. 50)
 ├── 4. Calibrations (p. 52)
 │    ├── 4.1 Calibration Products (p. 52)
 │    │    ├── 4.1.1 Absolute Gain Matrix (p. 52)
 │    │    ├── 4.1.2 Effective Point Spread Function (ePSF) models (p. 52)
 │    │    └── 4.1.3 Dark Current (p. 53)
 │    ├── 4.2 Calibration Procedures (p. 53)
 │    │    ├── 4.2.1 Photometric/Absolute Gain Calibration Derivation (p. 53)
 │    │    ├── 4.2.2 Astrometric Calibration Derivation (p. 56)
 │    │    └── 4.2.3 PSF Measurement (p. 58)
 │    └── 4.3 Additional Products and Inputs (p. 60)
 │         ├── 4.3.1 Spectral WCS (p. 61)
 │         ├── 4.3.2 Spectral Channels (p. 62)
 │         ├── 4.3.3 Atmospheric Templates (p. 67)
 │         └── 4.3.4 Additional Products (p. 67)
 ├── 5. Spectral Image Header Example (p. 73)
 │    └── 5.1 Transient Flags (p. 79)
 ├── 6. Absolute Gain Matrix Header Example (p. 80)
 ├── 7. Average EPSF Header Example (p. 81)
 └── 8. List of Acronyms (p. 83)
```

---

## 🏷️ Table 16: Level 2 Image Pixel Flag Definitions (Bitmask Reference)
Extracted verbatim from Section 3.2.5 (Pages 33–35). These bit values populate the 16-bit integer `FLAGS` HDU of every Level 2 Spectral Image:

| Bit # | Symbolic Flag Name | Hex Mask | Astronomical Condition & Pipeline Impact |
| :---: | :--- | :--- | :--- |
| **0** | `TRANSIENT` | `0x0001` | Transient charge jump (such as a cosmic ray hit) detected during Sample-Up-the-Ramp (SUR). |
| **1** | `OVERFLOW` | `0x0002` | Analog-to-digital converter (ADC) charge overflow limit reached during ramp integration. |
| **2** | `SUR_ERROR` | `0x0004` | Checksum error from onboard instrument data processor. |
| **6** | `NONFUNC` | `0x0040` | Static permanently non-functioning (dead) pixel characterized pre-flight. Unusable for science. |
| **7** | `DICHROIC` | `0x0080` | "Dark corners" of Bands 3 and 4 where the optical smile effect results in throughput cut off by the dichroic edge. |
| **9** | `MISSING_DATA` | `0x0200` | Telemetry packet lost during downlink prior to SSDC ingest. |
| **10** | `HOT` | `0x0400` | Unstable hot pixel exhibiting spurious, high dark current counts. |
| **11** | `COLD` | `0x0800` | Unresponsive cold pixel exhibiting quantum efficiency $< 10\%$. |
| **12** | `FULLSAMPLE` | `0x1000` | Full non-destructive read ramp history is available. |
| **14** | `PHANMISS` | `0x4000` | Phantom missing calibration correction. |
| **15** | `NONLINEAR` | `0x8000` | Fluence exceeds the linear regime and cannot be reliably corrected by the 5th-order polynomial. |
| **17** | `PERSIST` | `0x00020000`| Latent charge persistence remaining from saturated exposure in previous pointing ($I_p(t) = \sum A_n C_n e^{-t/\tau_n}$). |
| **19** | `OUTLIER` | `0x00080000`| Statistical spatial flux outlier flagged by the Detect Outlier Pixels module. |
| **20** | `CROSSTALK` | `0x00100000`| Inter-channel capacitive electronic crosstalk between ASIC readout amplifiers. |
| **21** | `SOURCE` | `0x00200000`| Pixel spatial centroid coincides with a known cataloged astronomical source. |
| **22** | `GHOST` | `0x00400000`| Internal optical reflection ghost artifact. |
| **23** | `GHOST_FPA` | `0x00800000`| Focal Plane Assembly filter-to-substrate optical reflection ghost. |
| **24** | `GHOST_EXT` | `0x01000000`| Out-of-field bright source stray light ghost. |
| **25** | `STREAK` | `0x02000000`| Satellite streak or fast-moving low-Earth orbit object track. |
| **26** | `BLOOM` | `0x04000000`| Source blooming where photocharge spills into adjacent pixels along the slow-read axis. |
| **27** | `SNOWBALL` | `0x08000000`| Giant secondary ionization charge deposition event ("snowball") spanning hundreds of pixels. |
| **28** | `HALO` | `0x10000000`| Diffuse halo surrounding a saturated cosmic ray or transient hit. |
| **29** | `SATELLITE_HALO` | `0x20000000`| Broad optical diffraction halo surrounding a bright LEO satellite trail. |

---

## 🔬 Core Pipeline Modules & Scientific Algorithms (Section 3)

### 1. Persistence Modeling (Sect. 3.2.4)
Latent charge decay following bright target saturation is dynamically modeled as a multi-component exponential decay:
$$I_p(t) = \sum_{n=1}^{N} A_n C_n e^{-t/\tau_n}$$
Pixels with predicted residual persistence exceeding the noise threshold are stamped with Bit 17 (`PERSIST`) and suppressed from co-addition.

### 2. Nonlinearity Correction (Sect. 3.2.2)
Corrects the nonlinear charge accumulation near detector well saturation using pre-flight calibration coefficients ($Q_{nl}, b_1, b_2, b_3, Q_{max}$) for each of the $2040 \times 2040$ pixels.

### 3. Absolute Photometric Gain & Zodi Background (Sect. 3.2.7 & 3.2.11)
- **Photometric Calibration:** Level 2 flux density is standardized in **$\text{MJy/sr}$** through cross-calibration against standard stars and 2MASS/WISE secondary calibrators.
- **Zodiacal Light:** Calculated using the **Kelsall et al. (1998)** interplanetary dust cloud model, evaluating line-of-sight solar elongation and orbital aspect angle. Stored un-subtracted in the `ZODI` HDU of Level 2 frames, and subtracted from Level 3 All-Sky Cubes.

---

## 🔗 Cross-Links in Obsidian Vault
- [[01 - IRSA SPHEREx Mission Hub]] — Overview of telescope hardware and 6 detector arrays.
- [[02 - IRSA SPHEREx Data Releases]] — DR1 and QR3 release chronologies.
- [[03 - SPHEREx Science Data Products & Calibration]] — Detailed MEF layers (`IMAGE`, `FLAGS`, `VARIANCE`, `ZODI`, `ePSF`, `WCS-WAVE`).
- [[04 - SPHEREx Data Access Protocols & TAP]] — Querying files via SIAv2 and IBE APIs.
- [[07 - SPHEREx Spectral Calibrations & Instrument Files]] — LVF transmission profiles and detector coordinate conventions.
