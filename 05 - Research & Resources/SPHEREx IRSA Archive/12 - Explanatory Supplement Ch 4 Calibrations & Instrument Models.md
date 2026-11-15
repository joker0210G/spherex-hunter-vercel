---
title: "SPHEREx Explanatory Supplement Ch 4: Calibration Derivations, ePSF Models & 102-Channel Tables"
document_id: "SSDC-DP-017"
chapter: "4. Calibrations"
source_pdf: "https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf"
pages: "52-72"
tags:
  - nasa
  - spherex
  - explanatory-supplement
  - chapter-4
  - calibrations
  - epsf
  - absolute-gain
  - spectral-channels
  - ice-bands
aliases:
  - SPHEREx Ch 4 Calibrations
  - SPHEREx ePSF Models
  - SPHEREx Channel Tables
created: 2026-11-14
status: active
---

# 🌈 SPHEREx Explanatory Supplement — Chapter 4: Calibrations & Instrument Models
> **Source Document:** `SSDC-DP-017` Version 2.1 (Pages 52–72)  
> **Source PDF:** [https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf)  
> **MOC:** [[00 - Team Command Center]] | [[08 - SPHEREx Explanatory Supplement Map]] | [[10 - Explanatory Supplement Ch 2 Data Products & Anomalies]] | [[11 - Explanatory Supplement Ch 3 Data Processing Pipeline]] | [[07 - SPHEREx Spectral Calibrations & Instrument Files]]

---

## 🔬 4.1 Core Calibration Products

### 1. Absolute Gain Matrix (Sect. 4.1.1)
- Flat-field response matrix converting raw photo-electron slope rates ($\text{e}^-/\text{s}$) to physical astronomical surface brightness units (**$\text{MJy/sr}$**).
- Delivered as a $2040 \times 2040$ floating-point FITS image per detector array (`abs_gain_matrix_D[D]...fits`, $\sim 16\text{ MB}$).

### 2. Effective Point Spread Function (`ePSF`) Models (Sect. 4.1.2)
- SPHEREx employs **empirical Effective PSFs** built using the `photutils.psf.EPSFBuilder` methodology.
- **Physical Representation:** Each ePSF is a **$33 \times 33$ pixel array** oversampled by a factor of 4.
- **Spatial Grid Sampling Across Detectors:**
  - **Detectors 1, 2, 4, 5, 6:** **$21 \times 21$ spatial zones** across the $2\text{K} \times 2\text{K}$ focal plane.
  - **Detector 3:** **$11 \times 41$ spatial zones** (higher sampling along the optical dispersion axis to capture steep transmission gradient aberrations).
- **Effective PSF Size ($N_{\text{eff}}$):**
  $$N_{\text{eff}} = \frac{1}{\sum_{i} p_i^2}$$
  where $p_i$ is the normalized pixel response. Measures the effective number of pixels across which point-source flux is distributed.

### 3. Cryogenic Dark Current Maps (Sect. 4.1.3)
- Derived from deep shadow exposures during mission commissioning and IOC.
- Stored as $2040 \times 2040$ arrays (`dark_D[D]...fits`, $\sim 16\text{ MB}$) in units of $\text{e}^-/\text{s}$.

---

## 🎯 4.2 Calibration Derivations & Ground Standards

### 1. Photometric Standard Stars (Sect. 4.2.1)
- Uses an all-sky network of unreddened spectrophotometric standard stars (HST CALSPEC white dwarfs, A-type dwarfs, and solar analogs) listed in Table 26.
- Cross-calibrated against secondary 2MASS $JHK_s$ and AllWISE $W1/W2$ standards.

### 2. Astrometric Calibration (Sect. 4.2.2)
- Solved by matching high-SNR centroid detections against **Gaia DR3** stars with validated trigonometric proper motions propagated to observation epochs.
- Updates the Simple Imaging Polynomial (SIP) distortion coefficients for each array.

---

## 📊 4.3 The 102 Nominal Spectral Channels (Tables 29–34)
Each detector array is divided into **17 nominal science channels** (labeled `1` to `17`). Channels `0` and `18` denote uncalibrated outer detector corner regions.

```
Total Survey Channels: 6 Detectors × 17 Channels = 102 Science Channels
```

### 🧊 Critical Molecular Ice Absorption Channels (Bands 4, 5, 6)

#### Band 4: $\text{H}_2\text{O}$ Ice & Hydrocarbons ($2.42 - 3.82\ \mu\text{m}$, $R \sim 35$)
| Channel | Central Wavelength $\lambda_c$ ($\mu\text{m}$) | Bandpass Range $[\lambda_{\text{min}}, \lambda_{\text{max}}]$ | Resolving Power $R$ | Key Astrophysical Diagnostic |
| :---: | :---: | :---: | :---: | :--- |
| **Channel 1** | $2.445\ \mu\text{m}$ | $[2.422, 2.474]$ | $42 \pm 7.6$ | Near-IR continuum baseline |
| **Channel 9** | **$3.033\ \mu\text{m}$** | $[2.985, 3.079]$ | $34 \pm 0.6$ | **$\text{H}_2\text{O}$ Ice Absorption Core ($3.05\ \mu\text{m}$)** |
| **Channel 10** | **$3.118\ \mu\text{m}$** | $[3.069, 3.164]$ | $34 \pm 0.6$ | **$\text{H}_2\text{O}$ Ice Long-Wavelength Wing** |
| **Channel 13** | **$3.383\ \mu\text{m}$** | $[3.330, 3.434]$ | $35 \pm 0.6$ | **Aliphatic Hydrocarbon ($\text{CH}_4$) Ice** |
| **Channel 17** | $3.768\ \mu\text{m}$ | $[3.707, 3.827]$ | $36 \pm 0.9$ | Methanol ($\text{CH}_3\text{OH}$) complex band |

#### Band 5: High-Resolution $\text{CO}_2$ Ice Channel ($3.81 - 4.42\ \mu\text{m}$, $R \sim 112$)
| Channel | Central Wavelength $\lambda_c$ ($\mu\text{m}$) | Bandpass Range $[\lambda_{\text{min}}, \lambda_{\text{max}}]$ | Resolving Power $R$ | Key Astrophysical Diagnostic |
| :---: | :---: | :---: | :---: | :--- |
| **Channel 1** | $3.834\ \mu\text{m}$ | $[3.815, 3.852]$ | $109 \pm 0.4$ | Continuum baseline |
| **Channel 7** | $4.041\ \mu\text{m}$ | $[4.020, 4.059]$ | $110 \pm 0.6$ | $\text{Br}\alpha$ ($4.052\ \mu\text{m}$) hydrogen recombination |
| **Channel 12** | $4.221\ \mu\text{m}$ | $[4.199, 4.240]$ | $115 \pm 1.1$ | Interstellar $^{13}\text{CO}_2$ isotope shoulder |
| **Channel 13** | **$4.257\ \mu\text{m}$** | $[4.235, 4.277]$ | $114 \pm 0.9$ | **$\text{CO}_2$ Ice Blue Wing** |
| **Channel 14** | **$4.294\ \mu\text{m}$** | $[4.272, 4.314]$ | $115 \pm 0.8$ | **$\text{CO}_2$ Ice Deep Absorption Core ($4.27\ \mu\text{m}$)** |
| **Channel 17** | $4.405\ \mu\text{m}$ | $[4.382, 4.427]$ | $117 \pm 1.2$ | Red continuum baseline |

#### Band 6: High-Resolution Interstellar $\text{CO}$ Ice Channel ($4.41 - 5.00\ \mu\text{m}$, $R \sim 128$)
| Channel | Central Wavelength $\lambda_c$ ($\mu\text{m}$) | Bandpass Range $[\lambda_{\text{min}}, \lambda_{\text{max}}]$ | Resolving Power $R$ | Key Astrophysical Diagnostic |
| :---: | :---: | :---: | :---: | :--- |
| **Channel 1** | $4.435\ \mu\text{m}$ | $[4.418, 4.452]$ | $129 \pm 1.6$ | Blue continuum baseline |
| **Channel 7** | $4.635\ \mu\text{m}$ | $[4.616, 4.653]$ | $127 \pm 1.4$ | $^{12}\text{CO}$ gas absorption lines |
| **Channel 8** | **$4.669\ \mu\text{m}$** | $[4.650, 4.688]$ | $126 \pm 1.7$ | **Interstellar Solid $\text{CO}$ Ice Absorption ($4.67\ \mu\text{m}$)** |
| **Channel 12** | $4.808\ \mu\text{m}$ | $[4.788, 4.827]$ | $132 \pm 2.6$ | OCS / Carbon sulfide ice |
| **Channel 17** | $4.989\ \mu\text{m}$ | $[4.966, 5.009]$ | $135 \pm 4.3$ | Survey long-wavelength cutoff |

---

## 🌌 4.4 Atmospheric Emission Templates (Sect. 4.3.3)
1. **Auroral Line Template (Band 1 Only):**
   - Corrects for upper-atmosphere atomic and molecular Nitrogen lines ($N_2, N$) in the auroral zones.
2. **Helium Line Template (Bands 1 & 2):**
   - Corrects for the prominent metastable triplet line **$\text{He}\ \text{I}$ at $\lambda = 1.0830\ \mu\text{m}$**.
3. **Shuttle Glow Template (Band 5 Only):**
   - Corrects for atomic oxygen surface recombination continuum on the spacecraft ram face ($3.82 - 4.40\ \mu\text{m}$).

---

## 🔗 Cross-Links in Obsidian Vault
- [[08 - SPHEREx Explanatory Supplement Map]] — Master outline of SSDC-DP-017.
- [[09 - Explanatory Supplement Ch 1 Mission & Payload Overview]] — Hardware optics and dual FPA temperatures.
- [[10 - Explanatory Supplement Ch 2 Data Products & Anomalies]] — MEF architecture and All-Sky Cubes.
- [[11 - Explanatory Supplement Ch 3 Data Processing Pipeline]] — 12-step Level 2 pipeline and variance calculations.
- [[05 - SPLICES Ice Source Catalog]] — Matching SPLICES targets against Bands 4, 5, and 6 ice channels.
- [[07 - SPHEREx Spectral Calibrations & Instrument Files]] — Laboratory transmission curves ($T(\lambda)$) and 4 oversampling granularities.
