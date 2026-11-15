# 🗺️ SPHEREx Data Release 1 (DR1) Complete Recursive Site Map & Access Codex
> **Source Root:** [https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_dr1.html](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_dr1.html)  
> **Host Archive:** NASA / IPAC Infrared Science Archive (IRSA), California Institute of Technology  
> **Release Date:** November 2026 | **Mission Launch:** March 2025  
> **Permanent DOIs:** `10.26131/IRSA678` (Images) & `10.26131/IRSA679` (Cube)  

---

## 1. 🌐 The Complete Recursive Site Map Tree

```
https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_dr1.html
│
├── 🔭 1. Interactive Applications & Mission Portals
│   ├── [SPHEREx Data Explorer (Firefly Web Visualizer)] -> https://irsa.ipac.caltech.edu/applications/spherex
│   ├── [Caltech SPHEREx Project Hub]                   -> https://spherex.caltech.edu
│   └── [Higher-Level Data Products Roadmap]             -> https://spherex.caltech.edu/page/data-products
│
├── 📦 2. Data Releases, Products & Official DOIs
│   ├── [DR1 Spectral Images (DOI: 10.26131/IRSA678)]   -> https://www.ipac.caltech.edu/doi/10.26131/IRSA678
│   ├── [Spectral All-Sky Cube (DOI: 10.26131/IRSA679)] -> https://www.ipac.caltech.edu/doi/10.26131/IRSA679
│   ├── [QR3 Spectral Images Overview Hub]              -> https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_qr.html
│   └── [QR3 Official DOI (10.26131/IRSA662)]          -> https://www.ipac.caltech.edu/doi/irsa/10.26131/IRSA662
│
├── 💾 3. Direct Data Access & Protocol Endpoints
│   ├── [IVOA Simple Image Access v2 (SIAv2)]           -> https://irsa.ipac.caltech.edu/ibe/sia.html
│   ├── [IRSA Astroquery Python Module]                  -> https://astroquery.readthedocs.io/en/latest/ipac/irsa/irsa.html
│   ├── [AWS S3 Open Data Cloud Access]                  -> https://irsa.ipac.caltech.edu/cloud_access/#spherex
│   │   └── Bucket: s3://nasa-irsa-spherex (Region: us-east-1)
│   ├── [Browsable On-Premises L2 Directory]            -> https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/level2
│   └── [Browsable HiPS5 Cube Directory]                -> https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/hips5_cube/hips_20261026
│
├── 📖 4. Official Documentation & Technical Advisories
│   ├── [SPHEREx Explanatory Supplement (PDF)]          -> https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf
│   ├── [SPHEREx Archive User Guide]                     -> https://irsa.ipac.caltech.edu/spherex-archive-documentation/
│   │   ├── SPHEREx Data Releases                       -> https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-releases
│   │   ├── SPHEREx Data Products                       -> https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-products
│   │   └── SPHEREx Data Access                         -> https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-access
│   └── [PSF Extension Header Error Advisory]            -> https://irsa.ipac.caltech.edu/data/SPHEREx/docs/psfhdrerr.html
│
└── 🧑‍💻 5. Caltech-IPAC Python Tutorial Series
    ├── [1. Intro to SPHEREx Spectral Images]            -> https://caltech-ipac.github.io/irsa-tutorials/spherex-intro/
    ├── [2. SPHEREx Spectral Image Cutouts]              -> https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/
    ├── [3. PSF in Spectral Cutouts]                     -> https://caltech-ipac.github.io/irsa-tutorials/spherex-psf/
    ├── [4. Source Discovery Tool Demo]                  -> https://caltech-ipac.github.io/irsa-tutorials/spherex-source-discovery-tool-demo/
    ├── [5. SPHEREx Mosaic Cubes]                        -> https://caltech-ipac.github.io/irsa-tutorials/spherex-mosaic/
    └── [6. SPHEREx HiPS Cubes]                          -> https://caltech-ipac.github.io/irsa-tutorials/spherex-hipscube/
```

---

## 2. 📋 Comprehensive Link Catalog

### A. Core Applications & Mission Portals
1. **DR1 Overview Hub:** [overview_dr1.html](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_dr1.html)
2. **SPHEREx Data Explorer:** [applications/spherex](https://irsa.ipac.caltech.edu/applications/spherex) — Firefly interactive sky browser.
3. **Caltech SPHEREx Project Hub:** [spherex.caltech.edu](https://spherex.caltech.edu) — Mission background, science team goals, and updates.
4. **Higher-Level Data Products:** [data-products](https://spherex.caltech.edu/page/data-products) — Future science catalog roadmap.

### B. Science Data Products & DOIs
5. **DR1 Spectral Images DOI:** [10.26131/IRSA678](https://www.ipac.caltech.edu/doi/10.26131/IRSA678) — Level 2 spectral images across 0.75 – 5.0 μm.
6. **Spectral All-Sky Cube DOI:** [10.26131/IRSA679](https://www.ipac.caltech.edu/doi/10.26131/IRSA679) — Full 102-channel hyperspectral all-sky data cube.
7. **QR3 Spectral Images Overview:** [overview_qr.html](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_qr.html) — Weekly quick-release documentation.
8. **QR3 Spectral Images DOI:** [10.26131/IRSA662](https://www.ipac.caltech.edu/doi/irsa/10.26131/IRSA662) — Quick Release 3 dataset.

### C. Programmatic Protocols & Cloud Infrastructure
9. **IVOA Simple Image Access (SIAv2):** [ibe/sia.html](https://irsa.ipac.caltech.edu/ibe/sia.html)
   - Endpoint: `https://irsa.ipac.caltech.edu/ibe/sia/query`
   - Collection keys: `COLLECTION=spherex_dr1`, `COLLECTION=spherex_dr1_cube`, `COLLECTION=spherex_qr3`.
   - Query format: `?POS=CIRCLE+{ra}+{dec}+{radius_deg}&COLLECTION=spherex_dr1`.
10. **Astroquery Python Client:** [astroquery IRSA](https://astroquery.readthedocs.io/en/latest/ipac/irsa/irsa.html)
    ```python
    from astroquery.ipac.irsa import Irsa
    # Query SPHEREx plane catalog or SIA cutouts programmatically
    ```
11. **AWS S3 Open Data Cloud Access:** [cloud_access/#spherex](https://irsa.ipac.caltech.edu/cloud_access/#spherex)
    - AWS Bucket: `s3://nasa-irsa-spherex/`
    - Region: `us-east-1`
    - Open data registries: `registry.opendata.aws/spherex-dr1`, `registry.opendata.aws/spherex-qr3`.
12. **On-Premises Level 2 Archive:** [ibe/data/spherex/dr1/level2](https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/level2)
13. **On-Premises HiPS5 Cube Archive:** [ibe/data/spherex/dr1/hips5_cube/hips_20261026](https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/hips5_cube/hips_20261026)

### D. Documentation & Calibration Errata
14. **Mission Explanatory Supplement:** [SPHEREx_Expsupp.pdf](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf) — Exhaustive 100+ page instrument design, calibration pipeline, and noise model reference.
15. **SPHEREx Archive User Guide:** [spherex-archive-documentation](https://irsa.ipac.caltech.edu/spherex-archive-documentation/)
    - Includes documentation on Data Releases, Data Products, and Data Access.
16. **PSF Header Error Advisory:** [psfhdrerr.html](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/psfhdrerr.html)
    - Technical erratum on $11 \times 11$ PSF grid indexing ($i_{\text{plane}} = y \times n_{\text{cols}} + x + 1$) and `+psffix1` pipeline fixes.

### E. Caltech-IPAC Python Tutorial Series
17. **1. Intro to SPHEREx Spectral Images:** [spherex-intro](https://caltech-ipac.github.io/irsa-tutorials/spherex-intro/) — [[15 - Tutorial 1 Introduction to SPHEREx Spectral Images]]. FITS multi-extension structure and WCS coordinate transformations.
18. **2. SPHEREx Spectral Image Cutouts:** [spherex-cutouts](https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/) — [[16 - Tutorial 2 SPHEREx Spectral Image Cutouts & MEF Packaging]]. Dynamic TAP cutout URLs, parallel downloads, and master MEF synthesis.
19. **3. PSF in Spectral Cutouts:** [spherex-psf](https://caltech-ipac.github.io/irsa-tutorials/spherex-psf/) — [[17 - Tutorial 3 Position-Dependent ePSF Reconstruction & Forward Modeling]]. Position-dependent 5x oversampled ePSF extraction and Photutils forward modeling.
20. **4. Source Discovery Tool Demo:** [spherex-source-discovery-tool-demo](https://caltech-ipac.github.io/irsa-tutorials/spherex-source-discovery-tool-demo/) — [[18 - Tutorial 4 SPHEREx Source Discovery Tool & Spectral Extraction]]. Multi-detector spectral difference imaging ($I_{\text{D2}} - I_{\text{D4}}$), SExtractor/SEP source detection, and 19-flag aperture photometry.
21. **5. SPHEREx Mosaic Cubes:** [spherex-mosaic](https://caltech-ipac.github.io/irsa-tutorials/spherex-mosaic/) — [[19 - Tutorial 5 SPHEREx Mosaic Cubes & Multi-Wavelength Overlays]]. 3D $(x, y, \lambda)$ mosaic cube analysis, PAH $3.3\ \mu\text{m}$ mapping, and GALEX FUV overlays.
22. **6. SPHEREx HiPS Cubes:** [spherex-hipscube](https://caltech-ipac.github.io/irsa-tutorials/spherex-hipscube/) — [[20 - Tutorial 6 SPHEREx HiPS All-Sky Mosaic Cubes & HEALPix Geometry]]. 12,288 Order 5 HEALPix tiles, Firefly channel dispatching, and local HPX pixel scaling.
