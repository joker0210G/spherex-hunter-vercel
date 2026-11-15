---
title: "NASA IRSA SPHEREx Spectral Calibrations & Linear Variable Filter (LVF) Transmission Curves"
url: "https://irsa.ipac.caltech.edu/data/SPHEREx/docs/spherex_spectral_calibrations.html"
tags:
  - nasa
  - spherex
  - irsa
  - spectral-calibration
  - lvf
  - transmission-curves
  - bandpass
  - response-functions
aliases:
  - SPHEREx Spectral Calibrations
  - SPHEREx Transmission Curves
  - SPHEREx LVF Calibrations
created: 2026-11-14
status: active
---

# 🌈 NASA IRSA SPHEREx Spectral Calibrations & LVF Transmission Profiles
> **Primary Source:** [https://irsa.ipac.caltech.edu/data/SPHEREx/docs/spherex_spectral_calibrations.html](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/spherex_spectral_calibrations.html)  
> **Documentation PDF:** [`SPHERExSpectralFiles_202607.pdf`](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHERExSpectralFiles_202607.pdf)  
> **Master Calibration Tarball:** [`SPHERExSpectralFiles_202607.tar`](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/spectral_files_20260812/SPHERExSpectralFiles_202607.tar)  
> **MOC:** [[00 - Team Command Center]] | [[01 - IRSA SPHEREx Mission Hub]] | [[03 - SPHEREx Science Data Products & Calibration]] | [[04 - SPHEREx Data Access Protocols & TAP]]

---

## 🔬 Laboratory-Derived Spectral Response Products
SPHEREx achieves all-sky spectroscopy without moving dispersion elements (gratings or prisms) by mounting **Linear Variable Filters (LVFs)** directly in front of its six $2048 \times 2048$ detector arrays. As a result, the transmitted central wavelength $\lambda_c$ varies continuously across the detector active area along the dispersion axis.

To support high-precision synthetic photometry, spectral cross-correlation, and molecular absorption modeling, IRSA distributes the underlying laboratory test bench calibration deliverables.

---

## 🎚️ 4 Granularity Levels of Spectral Sub-Channels
The calibration suite provides spectral response functions at **4 discrete sub-channel resolutions**:

| Sub-Channels per Detector | Total All-Sky Channels ($6 \times N$) | Effective Spectral Sampling | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **17 sub-channels** | **102 channels** | Nominal SPHEREx Science Baseline | Standard SED fitting, DR1 All-Sky Cubes, WiseView W1/W2 comparison. |
| **34 sub-channels** | **204 channels** | $2\times$ oversampled | Narrow ice absorption profile mapping ($\text{CO}_2$ $4.27\ \mu\text{m}$, $\text{H}_2\text{O}$ $3.05\ \mu\text{m}$). |
| **51 sub-channels** | **306 channels** | $3\times$ oversampled | Low-temperature Brown Dwarf methane ($\text{CH}_4$) and ammonia ($\text{NH}_3$) band analysis. |
| **68 sub-channels** | **408 channels** | $4\times$ oversampled | High-resolution redshift estimation ($z$) for extragalactic clustering. |

---

## 📦 Tarball Archive Structure (`SPHERExSpectralFiles_202607.tar`)
The downloadable calibration package contains five standardized subdirectories:

```
SPHERExSpectralFiles_202607/
 ├── ChannelMaps/
 │    └── FITS files mapping the 2D detector pixel coordinates (x, y) to channel index (0–18).
 ├── MiddlePixel/ (Cent)
 │    └── CSV tables containing transmission curves for pixels at the exact spectral center of each channel.
 ├── MeanAllPixel/ (Allpix)
 │    └── CSV tables containing transmission curves averaged over all pixels assigned to each channel.
 ├── FidSecSummary/
 │    └── Summary CSV files documenting nominal band centers, central wavelengths, and FWHM bandwidths.
 └── ParameterFiles/
      └── 2D FITS parameter maps of central wavelength (λ0) and bandwidth (Δλ) across all 6 focal planes.
```

---

## 📈 Two Transmission Response Models: `Cent` vs `Allpix`
For every channel, two distinct normalized transmission curves $T(\lambda)$ are delivered:

1. **Middle-Pixel Response (`Cent`):**
   - Represents the localized transmission function of detector pixels situated at the central dispersion coordinate of the channel.
   - **Recommended For:** Single-epoch forced aperture photometry of isolated point sources where exact pixel $(x, y)$ coordinates are known.
2. **All-Pixel Response (`Allpix`):**
   - Represents the aggregate spatial average of transmission functions across all physical pixels within the channel footprint.
   - **Recommended For:** Co-added images, multi-epoch stacks (e.g. SPHEREx Deep Fields), and spatially extended objects (e.g. [[06 - Special Target Comet 3I ATLAS]]) where emission spans multiple pixel columns.

---

## ⚠️ Critical Coordinate Inversion Warning: Detectors 4, 5, 6
> [!WARNING]
> **Detector Coordinates vs On-Sky Celestial Orientation:**  
> These raw laboratory calibration files are provided in **native detector coordinates**.  
> For **Detectors 4, 5, and 6 (Long-Wavelength Focal Plane Assembly)**, the physical detector readout layout is **flipped along the x-axis** relative to calibrated on-sky Level 2 FITS images (`IMAGE` HDU).
> 
> When mapping laboratory transmission profiles or pixel channel masks to on-sky Level 2 images:
> $$x_{\text{on-sky}} = N_{\text{cols}} - 1 - x_{\text{detector}}$$
> Failure to apply this reflection transposes the short-to-long wavelength gradient in Detectors 4, 5, and 6.

---

## 🛠️ Pipeline Calibrations vs Laboratory Calibrations
- **Laboratory Calibrations (This Dataset):** Raw physical transmission curves derived from Cryogenic Vacuum Chamber (TVAC) optical testing at Caltech/JPL. Ideal for synthetic photometry and forward-modeling spectral synthesis.
- **Pipeline Calibrations (IRSA IBE):** Real-time operational calibration files (`abs_gain_matrix`, `epsf`, `dark`, `spectral_wcs`) updated with in-flight starlight observations. See [[03 - SPHEREx Science Data Products & Calibration]].

---

## 🔗 Cross-Links in Obsidian Vault
- [[01 - IRSA SPHEREx Mission Hub]] — Resolving powers $R = \lambda / \Delta\lambda$ across Detectors 1–6.
- [[02 - IRSA SPHEREx Data Releases]] — DR1 and QR3 pipeline integration.
- [[03 - SPHEREx Science Data Products & Calibration]] — WCS-WAVE lookup tables and SIP polynomials.
- [[05 - SPLICES Ice Source Catalog]] — Detecting ice absorption features using Band 5 & 6 transmission profiles.
- [[06 - Special Target Comet 3I ATLAS]] — Applying `Allpix` transmission curves to extended comae.
