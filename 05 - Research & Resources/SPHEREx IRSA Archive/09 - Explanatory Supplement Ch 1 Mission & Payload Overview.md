---
title: "SPHEREx Explanatory Supplement Ch 1: Mission Overview, Spacecraft & Payload Architecture"
document_id: "SSDC-DP-017"
chapter: "1. Mission Overview"
source_pdf: "https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf"
pages: "4-10"
tags:
  - nasa
  - spherex
  - explanatory-supplement
  - chapter-1
  - spacecraft
  - payload
  - h2rg
  - survey-strategy
aliases:
  - SPHEREx Ch 1 Overview
  - SPHEREx Payload Specs
created: 2026-11-14
status: active
---

# 🛰️ SPHEREx Explanatory Supplement — Chapter 1: Mission & Payload Overview
> **Source Document:** `SSDC-DP-017` Version 2.1 (Pages 4–10)  
> **Source PDF:** [https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf)  
> **MOC:** [[00 - Team Command Center]] | [[08 - SPHEREx Explanatory Supplement Map]] | [[01 - IRSA SPHEREx Mission Hub]]

---

## 🚀 1.1 Mission Milestones & Core Science Themes
- **Launch Date & Time:** **12 March 2025 at 03:10:12 UTC** aboard a SpaceX Falcon 9 from Vandenberg Space Force Base.
- **Science Operations Commissioning:** Regular science operations initiated **May 1, 2025** following the In-Orbit Checkout (IOC) phase.
- **Nominal Duration:** 25 months executing **4 complete all-sky passes** ($1.4\text{ trillion voxels}$ per pass).

### 🌌 The 3 Strategic Science Themes
1. **Probing Inflation & Early Universe:**
   - 3D large-scale structure reconstruction across cosmological volumes using $\ge 450\text{ million}$ galaxy redshifts.
   - Constrains primordial non-Gaussianity via the parameter $f_{\text{NL}}$ with target sensitivity $\sigma(f_{\text{NL}}) \le 1$, differentiating single- vs multi-field inflationary paradigms.
2. **Origin of Planetary Systems & Biogenic Ices:**
   - Surveying interstellar and circumstellar ice absorption bands in YSOs, protoplanetary disks, and clouds throughout the Milky Way.
   - Collecting $\ge 20,000$ high-SNR ice spectra for $\text{H}_2\text{O}$ ($3.05\ \mu\text{m}$), $\text{CH}_4$ ($3.32/3.53\ \mu\text{m}$), $\text{CO}_2$ ($4.27\ \mu\text{m}$), and $\text{CO}$ ($4.67\ \mu\text{m}$).
3. **Galaxy Evolution via Extragalactic Background Light (EBL):**
   - Deep spectral imaging of North and South Ecliptic Poles measuring spatial power spectra of EBL fluctuations to separate intra-halo light, dwarf galaxies, and Epoch of Reionization sources.

### 📊 Archival Legacy Metrics
- $\ge 1\text{ billion}$ galaxy spectra
- $\ge 450\text{ million}$ galaxy redshifts
- $\ge 1\text{ million}$ quasar spectra
- $\ge 100\text{ million}$ stellar spectra
- $\ge 600,000$ exoplanet target host stars
- $\ge 700,000$ ice absorption spectra
- $\ge 100,000$ asteroid and comet spectra

---

## 🛰️ 1.2 Spacecraft & Orbital Parameters (Table 1)
Built on the **Ball Configurable Platform (BCP-100)** bus operating in a sun-synchronous dawn-dusk low Earth orbit (LEO):

| Orbital Parameter | Value | Engineering Significance |
| :--- | :--- | :--- |
| **Mean Semi-Major Axis** | $7,037.41\text{ km}$ | $\sim 700\text{ km}$ altitude above Earth surface |
| **Eccentricity** | $0.00034$ | Near-circular orbit |
| **Orbital Inclination** | $97.951^\circ$ | Retrograde polar sun-synchronous |
| **Orbital Period** | $98\text{ minutes}$ | $\sim 14.7$ revolutions per day |
| **Mean Local Time of Ascending Node (MLTAN)** | **6:00 AM** | Dawn-dusk sun-synchronous geometry minimizing Earth albedo |
| **Attitude Control** | 3-axis stabilized | Star trackers, SSIRU gyros, GPS, 4 reaction wheels, 3 torque rods |
| **Science Telemetry** | Ka-band at $600\text{ Mbps}$ | Downlinked via NASA Near Space Network (NSN) ground stations |
| **Onboard Solid-State Recorder** | 8 days capacity | $\sim 1\text{ TB}$ uncompressed buffer |

---

## 🔭 1.3 Payload & Optical Parameters (Table 2)
An all-reflective wide-field imaging spectrograph employing Linear Variable Filters (LVFs) mounted directly in front of the detector focal planes:

| Parameter | Value | Description |
| :--- | :--- | :--- |
| **Effective Aperture** | **$20\text{ cm}$** | Off-axis all-aluminum reflective telescope |
| **Focal Ratio** | **$f/3$** | Fast optical beam |
| **Total Field of View** | **$2 \times (3.5^\circ \times 11.3^\circ)$** | Split by a dichroic beam splitter |
| **Spatial Pixel Scale** | **$6.2''\text{ / pixel}$** | Resolves dense point source fields |
| **Single Frame Time** | **$1.5349\text{ s}$** | Non-destructive Sample-Up-the-Ramp (SUR) clock cycle |
| **Detector Arrays** | **6x Teledyne H2RG** | $2048 \times 2048$ pixels ($18\ \mu\text{m}$ pitch) |

### 🌈 Dual Focal Plane Assemblies & Bandpass Mapping
```
Telescope Beam (f/3, 20 cm)
 │
 ├── Dichroic Beam Splitter (Reflection: λ ≤ 2.44 μm)
 │    └── SWIR FPA (62 K, Passive Radiator)
 │         ├── Band 1: λ = 0.744 – 1.116 μm, R = 39 (H2RG 2.6 μm cutoff)
 │         ├── Band 2: λ = 1.099 – 1.651 μm, R = 41 (H2RG 2.6 μm cutoff)
 │         └── Band 3: λ = 1.636 – 2.421 μm, R = 41 (H2RG 2.6 μm cutoff)
 │
 └── Dichroic Beam Splitter (Transmission: λ ≥ 2.40 μm)
      └── MWIR FPA (45 K, Staged Passive V-Groove Radiator)
           ├── Band 4: λ = 2.423 – 3.822 μm, R = 35 (H2RG 5.3 μm cutoff)
           ├── Band 5: λ = 3.809 – 4.420 μm, R = 112 (H2RG 5.3 μm cutoff)
           └── Band 6: λ = 4.412 – 5.002 μm, R = 128 (H2RG 5.3 μm cutoff)
```

---

## 🔄 1.4 Survey Strategy & The Half-Channel Nyquist Shift
SPHEREx scans the sky by stepping its bore-sight along the dispersion axis of the Linear Variable Filters:
1. **Surveys 1 & 2 (Year 1):** Pointing steps correspond to **one full spectral channel** in the LVF.
2. **Surveys 3 & 4 (Year 2):** Pointing steps are deliberately offset on the sky by **half of a spectral channel** relative to Surveys 1 & 2.
   $$\Delta \theta_{\text{Survey 3,4}} = \Delta \theta_{\text{Survey 1,2}} + \frac{1}{2} \Delta\theta_{\text{channel}}$$
3. **Astrophysical Benefit:**
   - **Nyquist-samples the spectra across the entire sky twice** when all survey passes are combined.
   - Prevents narrow emission/absorption lines (such as unresolved planetary nebula lines or sharp ice absorption edges) from falling into gaps between discrete channel boundaries.

### 🎯 Deep Survey Fields
- Located at the **North Ecliptic Pole (NEP)** and **South Ecliptic Pole (SEP)**.
- Target groups are highly overlapping, providing dozens of repeated visits per week as the orbital plane precesses throughout the year.

---

## 🔗 Cross-Links in Obsidian Vault
- [[08 - SPHEREx Explanatory Supplement Map]] — Full Table of Contents and document index.
- [[01 - IRSA SPHEREx Mission Hub]] — IRSA web interface and tools.
- [[02 - IRSA SPHEREx Data Releases]] — DR1 vs QR2/QR3 processing pipeline.
- [[03 - SPHEREx Science Data Products & Calibration]] — FITS HDU specifications and ePSF models.
- [[07 - SPHEREx Spectral Calibrations & Instrument Files]] — LVF transmission laboratory calibration curves.
