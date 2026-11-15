# 🛰️ NASA IRSA SPHEREx Data Release 1 (DR1) & Releases Architecture
> **Source Root:** [https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_dr1.html](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_dr1.html)  
> **Host Archive:** NASA / IPAC Infrared Science Archive (IRSA), California Institute of Technology  
> **Release Date:** November 2026 | **Mission Launch:** March 2025  
> **Vault Location:** `05 - Research & Resources/SPHEREx IRSA Archive/02 - IRSA SPHEREx Data Releases.md`

---

## 1. 📌 Overview & Mission Milestone

SPHEREx is a NASA Astrophysics Medium Explorer (MIDEX) mission launched in **March 2025**. During its planned two-year baseline mission, SPHEREx performs all-sky spectroscopy across **0.75 to 5.0 μm** with 102 spectral channels, alongside deeper targeted observations in the SPHEREx Deep Fields (North and South Ecliptic Poles).

### 🚀 Data Release 1 (DR1) Summary
- **Release Timeline:** November 2026.
- **Scope & Reprocessing:** DR1 delivers fully reprocessed versions of the earlier Quick Release 2 (QR2) spectral images.
- **Harmonized Set:** DR1 spectral images are designed and calibrated to be used seamlessly together with **Quick Release 3 (QR3)** images as a single, uniformly processed astronomical set.
- **Spectral All-Sky Cube:** DR1 introduces the first official **all-sky spectral data cube**, providing continuous celestial sphere coverage across all 102 nominal SPHEREx spectral channels.

---

## 2. 📜 Official Digital Object Identifiers (DOIs) & Citations

Whenever utilizing SPHEREx DR1 data, NASA and Caltech/IPAC require formal attribution using the following permanent DOIs:

| Data Product | DOI Link | Resolving URL |
| :--- | :--- | :--- |
| **DR1 Spectral Images** | `10.26131/IRSA678` | [https://www.ipac.caltech.edu/doi/10.26131/IRSA678](https://www.ipac.caltech.edu/doi/10.26131/IRSA678) |
| **Spectral All-Sky Cube** | `10.26131/IRSA679` | [https://www.ipac.caltech.edu/doi/10.26131/IRSA679](https://www.ipac.caltech.edu/doi/10.26131/IRSA679) |
| **QR3 Spectral Images** | `10.26131/IRSA662` | [https://www.ipac.caltech.edu/doi/irsa/10.26131/IRSA662](https://www.ipac.caltech.edu/doi/irsa/10.26131/IRSA662) |
| **QR2 Spectral Images (Retired)** | `10.26131/IRSA652` | [https://www.ipac.caltech.edu/doi/irsa/10.26131/IRSA652](https://www.ipac.caltech.edu/doi/irsa/10.26131/IRSA652) |
| **QR1 Spectral Images (Retired)** | `10.26131/IRSA629` | [https://www.ipac.caltech.edu/doi/irsa/10.26131/IRSA629](https://www.ipac.caltech.edu/doi/irsa/10.26131/IRSA629) |

### 📝 Mandatory Acknowledgment Text:
> *"This publication makes use of data products from the Spectro-Photometer for the History of the Universe, Epoch of Reionization and Ices Explorer (SPHEREx), which is a joint project of the Jet Propulsion Laboratory and the California Institute of Technology, and is funded by the National Aeronautics and Space Administration."*

---

## 3. 📊 Data Set Characteristics & Delivery Channels

| Data Product | Spectral Range & Description | Access Methods |
| :--- | :--- | :--- |
| **Spectral Images (DR1)** | Level-2 Multi-Extension FITS spectral images spanning 0.75 – 5.0 μm with updated PSF and photometric calibration. | • [SPHEREx Data Explorer](https://irsa.ipac.caltech.edu/applications/spherex)<br>• [IRSA Astroquery Python Module](https://astroquery.readthedocs.io/en/latest/ipac/irsa/irsa.html)<br>• [IVOA Simple Image Access (SIA)](https://irsa.ipac.caltech.edu/ibe/sia.html)<br>• On-Premises IBE Directories<br>• [AWS S3 Cloud Open Data](https://irsa.ipac.caltech.edu/cloud_access/#spherex) |
| **Spectral All-Sky Cube** | Multi-dimensional 102-channel hyperspectral all-sky data cube providing uniform celestial coverage. | • [IRSA Astroquery Python Module](https://astroquery.readthedocs.io/en/latest/ipac/irsa/irsa.html)<br>• [Program Interface via SIA](https://irsa.ipac.caltech.edu/ibe/sia.html)<br>• On-Premises HiPS5 / Cube Directories<br>• [AWS S3 Cloud Access](https://irsa.ipac.caltech.edu/cloud_access/#spherex) |

---

## 4. 🗺️ Complete Site Map of `overview_dr1.html`

```
🌐 https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_dr1.html
│
├── 🔭 1. Interactive Applications & Mission Portals
│   ├── SPHEREx Data Explorer (Firefly Web Visualizer): https://irsa.ipac.caltech.edu/applications/spherex
│   └── Caltech SPHEREx Mission Homepage: https://spherex.caltech.edu
│
├── 📦 2. Data Releases & Products
│   ├── DR1 Spectral Images (DOI: 10.26131/IRSA678): https://www.ipac.caltech.edu/doi/10.26131/IRSA678
│   ├── Spectral All-Sky Cube (DOI: 10.26131/IRSA679): https://www.ipac.caltech.edu/doi/10.26131/IRSA679
│   ├── Quick Release Overview Hub (QR3/QR2): https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_qr.html
│   └── SPHEREx Higher-Level Science Products: https://spherex.caltech.edu/page/data-products
│
├── 💾 3. Direct Data Access & Protocol Endpoints
│   ├── Programmatic Access via IVOA SIA: https://irsa.ipac.caltech.edu/ibe/sia.html
│   ├── IRSA Astroquery Python Client: https://astroquery.readthedocs.io/en/latest/ipac/irsa/irsa.html
│   ├── Cloud Data Access (AWS S3 Bucket): https://irsa.ipac.caltech.edu/cloud_access/#spherex
│   ├── On-Premises Level 2 Directory: https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/level2
│   └── On-Premises HiPS5 Cube Directory: https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/hips5_cube/hips_20261026
│
├── 📖 4. Official Documentation & Technical Advisories
│   ├── SPHEREx Explanatory Supplement (PDF): https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf
│   ├── SPHEREx Archive Documentation (User Guide): https://irsa.ipac.caltech.edu/spherex-archive-documentation/
│   └── PSF Extension Header Error Advisory: https://irsa.ipac.caltech.edu/data/SPHEREx/docs/psfhdrerr.html
│
└── 🧑‍💻 5. Caltech-IPAC Python Tutorial Series
    ├── 1. Introduction to SPHEREx Spectral Images: https://caltech-ipac.github.io/irsa-tutorials/spherex-intro/
    ├── 2. SPHEREx Spectral Image Cutouts: https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/
    ├── 3. SPHEREx PSF in Spectral Image Cutouts: https://caltech-ipac.github.io/irsa-tutorials/spherex-psf/
    ├── 4. SPHEREx Source Discovery Tool Demo: https://caltech-ipac.github.io/irsa-tutorials/spherex-source-discovery-tool-demo/
    ├── 5. SPHEREx Mosaic Cubes: https://caltech-ipac.github.io/irsa-tutorials/spherex-mosaic/
    └── 6. SPHEREx HiPS Cubes: https://caltech-ipac.github.io/irsa-tutorials/spherex-hipscube/
```

---

## 5. 🔍 Deep Dive: Connected Sibling & Advisory Pages

### A. Quick Release Hub (`overview_qr.html`)
- **QR1 (July 2025):** First weekly releases (retired Feb 2026).
- **QR2 (October 2025):** Substantially improved calibrations.
- **Header Erratum (April 2026):** Patch applied to correct PSF cube orientation errors.
- **QR3 (September 2026):** Advanced PSF calibrations; current weekly cadence.
- **DR1 Integration (November 2026):** Reprocesses QR2 to form a single, uniform dataset with QR3.

### B. PSF Header Erratum Advisory (`psfhdrerr.html`)
- **Root Cause:** In earlier QR1/QR2 data, PSF cubes were arranged in an $11 \times 11$ detector grid (121 zones). The planes were stored in order of increasing x-index, but FITS headers erroneously stated increasing y-index:
  $$\text{Correct: } i_{\text{plane}} = y \times n_{\text{cols}} + x + 1 \quad \text{vs.} \quad \text{Erroneous: } i_{\text{plane}} = x \times n_{\text{cols}} + y + 1$$
- **Astrometric / Photometric Impact:** Affected detector corners by up to $\pm 5\%$ in flux extraction.
- **Resolution:** Pipeline versions 6.4 through 6.5.5 were re-calibrated with the `+psffix1` header keyword. Pipeline version 6.5.6+ natively resolved this.

---

## 6. 🛠️ Relevance & Integration in SPHEREx Hunter

1. **Spectral All-Sky Cube & 102 Channels:** Our frontend 102-band SED viewer maps directly to the DR1 102-channel cube specifications (0.75 – 5.0 μm).
2. **PSF-Matched Difference Imaging:** Team RIP's Alard-Lupton difference engine relies on accurate PSF kernel shapes. Adhering to DR1/QR3 corrected PSFs guarantees clean dipole subtractions without $\pm 5\%$ corner photometric artifacts.
3. **Citizen Science Verification:** Direct deep-links to the SPHEREx Data Explorer and official DOIs allow users to cite and verify prospective Planet X / brown dwarf candidates against authenticated NASA science releases.
