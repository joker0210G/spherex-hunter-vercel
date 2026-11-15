# 🌌 Official NASA & Partner Astronomy Portals & Data Archives
> **Project:** Team RIP - SPHEREx Hunter | **NASA Space Apps Challenge 2026**  
> **Compiled From:** Live NASA, Caltech/IPAC, ESA, CSA, and Citizen Science Data Portals

---

## 1. 🛰️ NASA IPAC IRSA SPHEREx Mission Data Archive
- **Official Portal:** [https://irsa.ipac.caltech.edu/Missions/spherex.html](https://irsa.ipac.caltech.edu/Missions/spherex.html)
- **SPHEREx Data Explorer:** [https://irsa.ipac.caltech.edu/applications/spherex](https://irsa.ipac.caltech.edu/applications/spherex)
- **AWS Cloud Data Access:** `s3://nasa-irsa-spherex` (open public datasets)
- **Moving Object Search Tool (MOST):** [https://irsa.ipac.caltech.edu/applications/MOST](https://irsa.ipac.caltech.edu/applications/MOST)

### Mission & Instrument Characteristics:
- **Lifetime:** 2025 – 2027 (All-sky survey every 6 months, 4 complete sky passes)
- **Instrument:** Wide-Field Linear Variable Filter (LVF) Imaging Spectrograph
- **Area Coverage:** 100% full-sky coverage
- **Spectral Bands (102 Spectral Channels):**
  - **Band 1 (Array 1):** $0.75 - 1.11\ \mu\text{m}$, Resolving power $R \sim 39$
  - **Band 2 (Array 2):** $1.11 - 1.64\ \mu\text{m}$, Resolving power $R \sim 41$
  - **Band 3 (Array 3):** $1.64 - 2.42\ \mu\text{m}$, Resolving power $R \sim 41$
  - **Band 4 (Array 4):** $2.42 - 3.82\ \mu\text{m}$, Resolving power $R \sim 35$
  - **Band 5 (Array 5):** $3.82 - 4.42\ \mu\text{m}$, Resolving power $R \sim 112$ (Interstellar Ice absorption)
  - **Band 6 (Array 6):** $4.42 - 5.00\ \mu\text{m}$, Resolving power $R \sim 128$ ($\text{CO}_2$ & organic molecules)

### Data Release Schedule:
- **QR1 / QR2 (Quick Release):** Initial reprocessed public products.
- **QR3 (Quick Release 3):** September 2026 weekly spectral image products.
- **DR1 (Data Release 1):** November 2026 complete calibrated all-sky multi-extension FITS data.

---

## 2. 📓 Caltech-IPAC SPHEREx Python Tutorial Notebooks
- **Tutorials Home:** [https://caltech-ipac.github.io/irsa-tutorials/spherex/](https://caltech-ipac.github.io/irsa-tutorials/spherex/)
- **Archive Documentation:** [https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-products/](https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-products/)

### Key Tutorial Modules:
1. **`spherex_cutouts.md` (Spectral Cutouts via TAP)**:
   - Queries `spherex.artifact` and `spherex.plane` tables using ADQL geometric polygon matching:
   ```sql
   SELECT
       'https://irsa.ipac.caltech.edu/' || a.uri || '?center=' || p.ra || ',' || p.dec || 'd&size=0.1' AS uri,
       p.energy_bandpassname,
       p.time_bounds_lower
   FROM spherex.artifact a
   JOIN spherex.plane p ON a.planeid = p.planeid
   WHERE 1 = CONTAINS(POINT('ICRS', 133.79513, -7.24515), p.poly)
     AND p.energy_bandpassname = 'SPHEREx-D1'
   ORDER BY p.time_bounds_lower
   ```
2. **`spherex_source_discovery_tool_demo.md` (Source Discovery & Image Subtraction)**:
   - Implements multi-epoch difference imaging ($I_2 - I_1$) on SPHEREx spectral planes without prior catalog coordinates.
   - Discovers high proper motion brown dwarfs, variable protostars, and icy transits.
   - Uses forced aperture photometry to extract 102-band spectral energy distributions (SEDs).
3. **`spherex_psf.md` (Wavelength-Dependent Point Spread Functions)**:
   - Extracts localized 2D optical PSFs tailored to each detector's Linear Variable Filter position.
4. **`spherex_mosaic.md` (Multiwavelength Spatial Mosaics)**:
   - Reprojects and co-adds overlapping spectral frames into large astronomical mosaic cubes.
5. **`spherex_hipscube.md` (HiPS Spectral Cubes in Aladin)**:
   - Visualizes all-sky progressive multi-resolution hierarchical cubes in CDS Aladin Lite.

---

## 3. 🔭 Backyard Worlds: Planet 9 WiseView Comparator
- **Live Tool:** [http://byw.tools/wiseview](http://byw.tools/wiseview)
- **Authors:** Dan Caselden & Paul Westin (NASA Citizen Science / Backyard Worlds: Planet 9)
- **Survey Data:** unWISE time-resolved co-adds (W1 $3.4\ \mu\text{m}$, W2 $4.6\ \mu\text{m}$) spanning 2010–present.

### Key Capabilities & URL Schema:
- **Interactive Deep-Linking:**
  `http://byw.tools/wiseview#ra=[RA]&dec=[DEC]&size=[FOV_ARCSEC]&band=[1|2|3]&speed=[MS]`
- **Photometric Difference Mode:** Subtracts temporal co-adds to highlight moving dipole signatures.
- **Astropy AsinhStretch:** Scaled dynamic range with percentile clipping to reveal faint cold substellar companions.

---

## 4. 🌟 STScI MAST ESA Gaia Archive
- **Portal:** [https://archive.stsci.edu/missions-and-data/gaia](https://archive.stsci.edu/missions-and-data/gaia)
- **Data Release:** Gaia DR3 / EDR3 (over 1.8 billion sources)
- **Astrometric Parameters:**
  - High-precision equatorial coordinates: Right Ascension ($\alpha$), Declination ($\delta$)
  - Proper motion vectors: $\mu_\alpha \cos \delta$ and $\mu_\delta$ in $\text{mas/yr}$
  - Parallaxes ($\varpi$) and distances
  - G-band, BP ($0.33 - 0.68\ \mu\text{m}$), and RP ($0.64 - 1.05\ \mu\text{m}$) spectrophotometry
- **Cross-Matching:** Used by SPHEREx Hunter to project genuine proper motion displacement vectors across multi-decade temporal baselines (1999 2MASS $\to$ 2025 SPHEREx).

---

## 5. 🛰️ Canadian Space Agency (CSA) NEOSSat Mission
- **Mission Overview:** [https://www.asc-csa.gc.ca/eng/satellites/neossat/](https://www.asc-csa.gc.ca/eng/satellites/neossat/)
- **Dataset:** [https://data.asc-csa.gc.ca/dataset/neossat](https://data.asc-csa.gc.ca/dataset/neossat) — [[CSA_OPENDATA_NEOSSAT_SITEMAP]]. Open HTTP bucket architecture (`ASTRO/YYYY/DDD/`), CKAN REST API, and `_cord.fits.gz` calibration pipeline.
- **Spacecraft:** Near-Earth Object Surveillance Satellite (NEOSSat)
- **Instrument:** 15 cm ($f/5.88$) Maksutov optical telescope orbiting in sun-synchronous low Earth orbit.
- **Primary Science:** Monitoring Near-Earth Asteroids (NEOs), comets, space debris tracking, and exoplanet transit photometry without atmospheric turbulence.

---

## 6. 🇨🇦 Canadian Astronomy Data Centre (CADC)
- **Archive Search:** [https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/](https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/)
- **Programmatic Access:** `astroquery.cadc.Cadc`
- **CAOM-2 TAP Interface:** Allows spatial coordinate queries across the complete NEOSSat astronomical observation archive:
  ```python
  from astroquery.cadc import Cadc
  from astropy.coordinates import SkyCoord
  import astropy.units as u

  cadc = Cadc()
  coords = SkyCoord(ra=133.79513, dec=-7.24515, unit='deg')
  results = cadc.query_region(coords, radius=0.5*u.deg, collection='NEOSSAT')
  ```

---

## 7. 🛠️ CSA NEOSSAT Tutorial Repository
- **GitHub Repository:** [https://github.com/asc-csa/NEOSSAT_Tutorial](https://github.com/asc-csa/NEOSSAT_Tutorial)
- **Notebooks:**
  - `01_ Extracting Data and Visualization.ipynb`: FTP and CADC programmatic queries for calibrated FITS files.
  - `02_Pre Processing and Analysis.ipynb`:
    - Overscan and master dark frame subtraction.
    - Streaklet detection via Line Segment Detector (LSD) algorithm.
    - Temporal median stacking across data cubes to extract moving asteroids and orbital transients.

---

## 8. 🔗 Universal Quick-Link Mapping in SPHEREx Hunter

| Portal / Tool | Target / Capability | Integration in SPHEREx Hunter |
| :--- | :--- | :--- |
| **NASA IRSA SPHEREx** | Multi-Extension FITS Cutouts & Spectral Bands | Backend `/api/cutout` & FITS modal (`#fitsModal`) |
| **Caltech IRSA Tutorials** | TAP ADQL Queries & Source Discovery | `backend/services/cutout_engine.py` |
| **Dan Caselden WiseView** | unWISE Blink Comparison & Validation | Direct deep-link button (`#btnWiseViewLink`) |
| **STScI MAST Gaia DR3** | Astrometric Proper Motion Vectors | Hotkey `V` / `#toolGaia` vector overlay |
| **CADC / NEOSSat** | Asteroid Tracking & Moving Object Filtering | Citizen Science candidate logging (`#flagModal`) |
