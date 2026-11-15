---
title: "NASA IRSA SPHEREx Mission Hub & Web Portal"
url: "https://irsa.ipac.caltech.edu/Missions/spherex.html"
tags:
  - nasa
  - spherex
  - irsa
  - mission-hub
  - archive
  - spectroscopy
aliases:
  - IRSA SPHEREx
  - SPHEREx Mission Hub
  - IRSA Hub
created: 2026-11-14
status: active
---

# 🛰️ NASA IRSA SPHEREx Mission Hub & Web Portal
> **URL:** [https://irsa.ipac.caltech.edu/Missions/spherex.html](https://irsa.ipac.caltech.edu/Missions/spherex.html)  
> **Host:** NASA / IPAC Infrared Science Archive (IRSA), Caltech  
> **MOC:** [[00 - Team Command Center]] | [[SPHEREx Documentation & Public Archive]] | [[IRSA_SPHEREX_SITEMAP]]

---

## 📌 Mission Profile & Hardware Characteristics
The **Spectro-Photometer for the History of the Universe, Epoch of Reionization and Ices Explorer (SPHEREx)** is a NASA Medium-Class Explorer (MIDEX) mission executing an all-sky spectral survey across 102 infrared bands.

| Attribute | Specification |
| :--- | :--- |
| **Operational Lifetime** | 2025 – 2027 (Nominal 25-month survey) |
| **Sky Coverage** | **100% of the celestial sphere** (4 complete all-sky passes) |
| **Instrument Architecture** | Wide Field Linear Variable Filter (LVF) Imaging Spectrograph |
| **Funding Agency** | NASA Astrophysics Division |
| **Lead Institutions** | JPL, Caltech |
| **Contributing Partners** | RIT, Harvard/CfA, Arizona State Univ, Univ of Arizona, Ohio State, KASI (Korea), UC Irvine, Johns Hopkins, ASIAA (Taiwan) |

### 🌈 6 Detector Arrays & Resolving Powers
| Array | Wavelength Range ($\mu\text{m}$) | Resolving Power ($R = \lambda / \Delta\lambda$) | Primary Astrophysical Tracers |
| :--- | :--- | :--- | :--- |
| **Array 1** | $0.75 - 1.10\ \mu\text{m}$ | $R \sim 39$ | Optical-dropout brown dwarfs, galaxy redshift ($z \sim 1$) |
| **Array 2** | $1.11 - 1.60\ \mu\text{m}$ | $R \sim 41$ | Near-IR continuum, early universe galaxy clustering |
| **Array 3** | $1.64 - 2.40\ \mu\text{m}$ | $R \sim 41$ | Stellar populations, 2MASS cross-validation baseline |
| **Array 4** | $2.42 - 3.80\ \mu\text{m}$ | $R \sim 35$ | Diffuse Galactic emission, unWISE W1 baseline |
| **Array 5** | $3.82 - 4.40\ \mu\text{m}$ | $R \sim 112$ | $\text{H}_2\text{O}$ ice ($3.05\ \mu\text{m}$ wing) & Interstellar $\text{CO}_2$ ($4.27\ \mu\text{m}$) |
| **Array 6** | $4.42 - 5.00\ \mu\text{m}$ | $R \sim 128$ | Interstellar $\text{CO}$ ice ($4.67\ \mu\text{m}$), unWISE W2 baseline |

---

## 📅 Official Data Release Timeline
* **July 2025:** First Quick Release Products (QR1) deployed at IRSA.
* **October 2025:** Reprocessed Quick Release 2 (QR2) products available.
* **April 10, 2026:** QR2 headers updated to correct PSF extension header error (see erratum note [[02 - IRSA SPHEREx Data Releases]]).
* **September 2026:** First Quick Release 3 (QR3) products available at IRSA.
* **November 2026:** **Data Release 1 (DR1)** science-quality pipeline products available.

---

## 🛠️ IRSA Web Applications & Science Tools
The mission hub exposes direct links to specialized scientific tools:

1. **SPHEREx Data Explorer:**  
   `https://irsa.ipac.caltech.edu/applications/spherex`  
   *Firefly-based interactive visual sky viewer for multi-band images, tables, and coverage footprints.*
2. **Spectrophotometry Tool:**  
   `https://irsa.ipac.caltech.edu/applications/spherex/tool-spectrophotometry`  
   *Extracts calibrated 102-band spectra from SPHEREx Multi-Extension FITS (MEF) images using forced aperture photometry at target coordinates.*
3. **Mosaic Tool:**  
   `https://irsa.ipac.caltech.edu/applications/spherex/tool-mosaic`  
   *Generates custom multi-wavelength mosaics and all-sky spatial-spectral projections.*
4. **Spatial Cutout Tool:**  
   `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/cutout_tool.html`  
   *Extracts spatial subsets (cutouts) from large SPHEREx Level 2/3 FITS images.*
5. **Source Discovery Tool:**  
   *Identifies and characterizes statistically significant sources without requiring positional priors (blind source extraction).*
6. **Moving Object Search Tool (MOST):**  
   `https://irsa.ipac.caltech.edu/applications/MOST`  
   *Queries orbital ephemerides for comets, asteroids, and NEOs, locating SPHEREx observations matching predicted coordinates at observation epochs.*
7. **Cloud Direct Access:**  
   `https://irsa.ipac.caltech.edu/cloud_access/#spherex`  
   *Public AWS S3 Open Data bucket (`s3://nasa-irsa-spherex/`) hosting high-volume science products.*

---

## 🐍 Official Caltech/IPAC Python Tutorial Notebook Series
IRSA hosts specialized Jupyter notebook tutorials for programmatic exploitation:
- `Introduction to SPHEREx Spectral Images`
- `SPHEREx Spectral Image Cutouts`
- `SPHEREx PSF in Spectral Image Cutouts`
- `SPHEREx Source Discovery Tool`
- `SPHEREx Mosaic Cubes`
- `SPHEREx HiPS Cubes`

---

## 📖 Canonical Literature & Citations
- **Mission Architecture:** Bock et al. (2026), *ApJ*, 999, 139 ([ADS: 2026ApJ...999..139B](https://ui.adsabs.harvard.edu/abs/2026ApJ...999..139B/abstract))
- **Pipeline & Science Data Center:** Akeson et al. (2026), *ApJS*, 285, 67 ([ADS: 2026ApJS..285...67A](https://ui.adsabs.harvard.edu/abs/2026ApJS..285...67A/abstract))
- **Sky Simulator:** Crill et al. (2025), *ApJS*, 281, 10 ([ADS: 2025ApJS..281...10C](https://ui.adsabs.harvard.edu/abs/2025ApJS..281...10C/abstract))
- **Instrument & In-Flight Calibration:** Korngut et al. (2026), *arXiv:2603.29835* ([ADS: 2026arXiv260329835K](https://ui.adsabs.harvard.edu/abs/2026arXiv260329835K/abstract))

### 📝 Official Citation Acknowledgement
> *"This publication makes use of data products from the Spectro-Photometer for the History of the Universe, Epoch of Reionization and Ices Explorer (SPHEREx), which is a joint project of the Jet Propulsion Laboratory and the California Institute of Technology, and is funded by the National Aeronautics and Space Administration."*

---

## 🔗 Next In Obsidian Vault Series
- [[02 - IRSA SPHEREx Data Releases]] — *Deep dive into DR1, QR2/QR3 pipelines and the PSF header fix.*
- [[03 - SPHEREx Science Data Products & Calibration]] — *Detailed MEF FITS extensions, ePSF models, and 102-channel calibrations.*
- [[04 - SPHEREx Data Access Protocols & TAP]] — *SIAv2, TAP ADQL schema, and Python queries.*
- [[05 - SPLICES Ice Source Catalog]] — *Target list of circumstellar and interstellar ices.*
- [[06 - Special Target Comet 3I ATLAS]] — *Target-of-Opportunity solar system observations.*
