# 🛰️ SPHEREx DR1 & HiPS Context Layer Research Notes
> **Standard:** NASA/IPAC Infrared Science Archive (IRSA) DR1 & HiPS Specification  
> **Date:** 2026-11-14 | **Branch:** `darkodu/astro-backend`  
> **Document:** `docs/dr1_notes.md`

---

## 1. Data Releases Overview (QR2, QR3, DR1) & Date Ranges

| Release | Release Date | Coverage / Survey Focus | Observation Date Range (MJD) | Archive Status |
| :--- | :---: | :--- | :---: | :--- |
| **QR2 (Quick Release 2)** | Oct 2025 (headers patched Apr 2026) | Initial survey validation; improved calibration over QR1 | ~60789 to 60950 | Archived; superseded by QR3/DR1. No longer returned by standard IRSA/VO queries. |
| **QR3 (Quick Release 3)** | Sep 2026 | Refined Point Spread Function (PSF) models and calibration updates for reliable photometry | ~60789 to 61120 | Operates alongside DR1 as uniform pipeline standard. |
| **DR1 (Data Release 1)** | Nov 2026 | First full all-sky public data release; comprehensively reprocessed Level-2 spectral images + all-sky spectral cube | **MJD 60789.75076 to 61174.49276** (May 2025 to late 2026) | Primary active collection in IRSA TAP (`spherex.obscore`, collection: `spherex_dr1`). |

---

## 2. Exact HiPS Identifiers & Endpoint URLs (from IRSA HiPS Directory)
Queried directly from `https://irsa.ipac.caltech.edu/data/hips/list` and validated against `https://irsa.ipac.caltech.edu/data/hips/SPHEREx/spherex_allsky_cube/properties`:

* **IVOA Creator DID (`creator_did`):** `ivo://IPAC/P/SPHEREx/DR1/cube`
* **HiPS Service Base URL (`hips_service_url`):** `https://irsa.ipac.caltech.edu/data/hips/SPHEREx/spherex_allsky_cube`
* **Dataset Title (`obs_title`):** `SPHEREx DR1 all-sky data cube`
* **Dataset Collection (`obs_collection`):** `SPHEREx DR1`
* **Progenitor URL:** `https://irsa.ipac.caltech.edu/data/hips/SPHEREx/spherex_allsky_cube/HpxFinder`
* **Explanatory Supplement:** `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf`

---

## 3. Spectral Cube Structure & HEALPix Geometry

* **Data Product Type:** `dataproduct_type = cube`
* **Cube Depth:** **102 channels** (`hips_cube_depth = 102`, `hips_cube_firstframe = 1`)
* **Spectral Unit:** `um` (microns)
* **Spectral Range:** **$0.743\,\mu\text{m}$ to $5.009\,\mu\text{m}$** (`em_min = 7.430000e-07`, `em_max = 5.009000e-06`)
* **Channel Distribution:**
  - 6 detector bands (Bands 1 to 6) $\times$ 17 channels per band = 102 channels.
  - Frame index formula: $\text{frame} = 17 \times (\text{band} - 1) + (\text{channel} - 1) + 1$.
  - Dichroic filter transition channels (Frames 50 & 51, corresponding to Band 3 Channel 17 and Band 4 Channel 1) are blank.
* **HEALPix Geometry:**
  - Maximum Order: `hips_order = 5`
  - Minimum Order: `hips_order_min = 0`
  - Coordinate Frame: `hips_frame = equatorial` (ICRS)
  - Tile Dimension: $512 \times 512$ pixels (`hips_tile_width = 512`)
  - Pixel Scale: `0.0035786 deg/pixel` ($\approx 12.88''/\text{pixel}$)
  - Formats: Default tiles are `png`; custom tile format `fits-cube`
  - Pixel Scaling: `asinh` function with data range `[-1418.79, 11348.3]`, cut `[0, 40]`
* **Per-Survey vs Merged:**
  - `spherex_allsky_cube` is a **single merged all-sky composite cube** covering the full mission baseline up to DR1.
  - Per-survey separate cubes (e.g., Survey 1 vs Survey 2) do not exist in the HiPS registry. Multi-epoch time-domain differencing must be performed on individual Level-2 calibrated exposures (`spherex.obscore`), while the HiPS cube serves as an all-sky contextual background.

---

## 4. License & Credit Text

* **HiPS Creator:** `SPHEREx Science Data Center`
* **Provenance / Progenitor:** `SPHEREx / IPAC`
* **Copyright Mention:** `Caltech/IPAC`
* **Original Data Copyright:** `NASA/SPHEREx`
* **Mandatory UI Credit:**  
  *"NASA / IPAC / SPHEREx Science Data Center (DR1 all-sky mosaic). Context only, not used for scientific detection."*

---

## 5. Cross-Origin Resource Sharing (CORS) Test

* **Direct HTTP Header Verification:**  
  A probe to `https://irsa.ipac.caltech.edu/data/hips/SPHEREx/spherex_allsky_cube/properties` confirmed the following response header:
  ```http
  Access-Control-Allow-Origin: *
  ```
* **Result:** **PASSED**. The IRSA server explicitly permits browser cross-origin requests (`*`), meaning Aladin Lite v2/v3 instances can directly stream HiPS tiles without requiring a reverse proxy or custom tile server.
