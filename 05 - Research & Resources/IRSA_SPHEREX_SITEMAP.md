# 🗺️ Complete Site Map & Architecture: NASA IRSA SPHEREx Mission
> **Source Root:** [https://irsa.ipac.caltech.edu/Missions/spherex.html](https://irsa.ipac.caltech.edu/Missions/spherex.html)  
> **Host Archive:** NASA / IPAC Infrared Science Archive (IRSA), California Institute of Technology  
> **Last Crawled / Verified:** 2026-11-14  

---

## 1. 🌐 Core Hub & Interactive Applications
- **Main Mission Portal:**
  `https://irsa.ipac.caltech.edu/Missions/spherex.html`  
  *The central entry point providing mission overview, operational notices, and links to web applications, documentation, data releases, and community catalogs.*
- **SPHEREx Data Explorer (Interactive Web App):**
  `https://irsa.ipac.caltech.edu/applications/spherex`  
  *Firefly-powered interactive visualizer and query interface for exploring SPHEREx all-sky spectral images and catalogs.*
- **Online Help & User Manual:**
  `https://irsa.ipac.caltech.edu/onlinehelp/spherex/`  
  *Official IRSA user guide detailing search workflows, visualization options, and bandpass queries.*
- **Interactive Cutout Tool Documentation:**
  `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/cutout_tool.html`  
  *Documentation on spatial-spectral sub-image generation directly through IRSA.*
- **Moving Object Search Tool (MOST):**
  `https://irsa.ipac.caltech.edu/applications/MOST`  
  *Cross-mission ephemeris matching tool supporting solar system objects across SPHEREx footprints.*

---

## 2. 📚 SPHEREx Archive Documentation (Modern Knowledge Base)
- **Archive Documentation Hub:**
  `https://irsa.ipac.caltech.edu/spherex-archive-documentation/`
- **Data Releases Overview:**
  `https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-releases`
- **Data Products Reference:**
  `https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-products`
  - *Main Science Data Products:*
    - Spectral Image Multi-Extension FITS (MEF)
    - Spectral Image Cutouts
    - All-Sky Spectral Cubes
  - *Point Spread Function (PSF & ePSF):*
    - Empirical PSF models and effective PSFs across the 6 detector arrays
  - *Calibration Products:*
    - Spectral WCS (World Coordinate System)
    - Dark Current Maps
    - Dichroic Response Functions
    - Absolute Gain Matrices & Electronic Gain Factors
  - *Instrument & Correction Products:*
    - 102 Spectral Channels definitions
    - Simple Imaging Polynomials (SIP) distortion coefficients
    - Solid Angle Pixel Maps
    - Crosstalk Parameters
    - Nonfunctional Pixel Bitmasks
    - Read Noise Matrices
    - Shuttle Glow & Helium Emission Templates
    - Zodiacal Dust Scaling Templates
- **Data Access & Protocols Guide:**
  `https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-access`
  - IVOA Simple Image Access v2 (SIAv2) Protocol
  - IVOA Table Access Protocol (TAP) & ADQL Query Interfaces
  - Programmatic HTTP APIs & Cutout Services
  - Image Based Environmental Directories (IBE)
  - Python Access via `astroquery.ipac.irsa`
  - Cloud Direct Access (AWS S3 Open Data Bucket: `#spherex`)

---

## 3. 📦 Data Releases & Observational Data Products
- **Data Release 1 (DR1):**
  `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_dr1.html`  
  *Full calibrated science pipeline release covering multiple sky passes, Level 2 / Level 3 products, and all-sky cubes.*
- **Quick Releases (QR, QR2, QR3):**
  `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_qr.html`  
  *Fast-turnaround products released shortly after downlink for rapid science and transient alerts.*
- **PSF Extension Header Error Advisory:**
  `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/psfhdrerr.html`  
  *Technical erratum and header fix guidelines for QR2 PSF multi-extension FITS headers.*
- **Explanatory Supplements (PDF):**
  - Mission Explanatory Supplement: `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf`
  - Quick Release Supplement: `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp_QR.pdf`

---

## 4. 🧊 Catalogs & Ice Sources (SPLICES)
- **SPHEREx Target List of Ice Sources (SPLICES):**
  `https://irsa.ipac.caltech.edu/data/SPHEREx/SPLICES/`  
  *High-priority targets for investigating interstellar and circumstellar ice absorption bands ($\text{H}_2\text{O}, \text{CO}_2, \text{CO}, \text{CH}_3\text{OH}$).*
  - **FITS Binary Table:** `https://irsa.ipac.caltech.edu/data/SPHEREx/SPLICES/20241107_SPLICESv8.6.fits.gz`
  - **Release Notes (PDF):** `https://irsa.ipac.caltech.edu/data/SPHEREx/SPLICES/SPLICES_Release_Notes.pdf`
  - **Catalog Column Descriptions:** `https://irsa.ipac.caltech.edu/data/SPHEREx/SPLICES/gator_docs/splices_colDescriptions.html`
  - **Gator Interactive Query:** `https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-scan?submit=Select&projshort=SPHEREX`

---

## 5. ☄️ Special Target Datasets: Comet 3I/ATLAS
- **Comet 3I/ATLAS Dedicated Portal:**
  `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/comet3iatlas/index.html`  
  *Target-of-Opportunity / moving body observation package.*
  - **ObsCore IVOA VOTable:** `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/comet3iatlas/obscore_3I_Atlas.vot`
  - **Batch Download Script (`curl`):** `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/comet3iatlas/3IATLASImages-curl.sh`
  - **Batch Download Script (`wget`):** `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/comet3iatlas/3IATLASImages-wget.sh`

---

## 6. 🌈 Spectral Calibration Deliverables
- **Spectral Calibrations Overview:**
  `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/spherex_spectral_calibrations.html`  
  *Relative spectral response curves and wavelength calibration mapping for all 6 Linear Variable Filter (LVF) detector arrays.*
  - **Spectral Calibration Data Tarball:** `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/spectral_files_20260812/SPHERExSpectralFiles_202607.tar`
  - **Spectral Files Documentation (PDF):** `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHERExSpectralFiles_202607.pdf`

---

## 7. 📄 Core Published Literature & NASA ADS Citations
- **Bock et al. (2026)** — *The SPHEREx Mission Overview & Science Architecture*:  
  `https://ui.adsabs.harvard.edu/abs/2026ApJ...999..139B/abstract`
- **Akeson et al. (2026)** — *The SPHEREx Science Data Center and Archive Architecture at IPAC*:  
  `https://ui.adsabs.harvard.edu/abs/2026ApJS..285...67A/abstract`
- **Crill et al. (2025)** — *SPHEREx Payload Calibration & In-Flight Performance Validation*:  
  `https://ui.adsabs.harvard.edu/abs/2025ApJS..281...10C/abstract`
- **Korngut et al. (2026)** — *All-Sky Spectral Survey Observations with SPHEREx*:  
  `https://ui.adsabs.harvard.edu/abs/2026arXiv260329835K/abstract`
