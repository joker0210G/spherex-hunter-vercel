# 📚 SPHEREx Documentation & Public Archive

---

## 🔗 Official NASA & Caltech Links
- **NASA SPHEREx Mission Page:** [https://www.nasa.gov/mission/spherex/](https://www.nasa.gov/mission/spherex/)
- **Caltech SPHEREx Science Site:** [https://spherex.caltech.edu/](https://spherex.caltech.edu/)
- **IPAC IRSA SPHEREx Data Archive:** [https://irsa.ipac.caltech.edu/Missions/spherex.html](https://irsa.ipac.caltech.edu/Missions/spherex.html)
- **NASA ADS Key Science Paper:** Doré et al., *"Cosmology and Astrophysics with the SPHEREx All-Sky Spectral Survey"* (arXiv:1412.4872).

---

## 🗂️ Obsidian Vault: Deep IRSA Archive Knowledge Base
* **[[01 - IRSA SPHEREx Mission Hub]]** — Main Mission Hub, applications, 6 detector specs, and canonical papers.
* **[[02 - IRSA SPHEREx Data Releases]]** — DR1 vs Quick Releases (QR2/QR3), DOIs, pipeline versions, and PSF header fix ($11 \times 11$ plane indexing).
* **[[03 - SPHEREx Science Data Products & Calibration]]** — Multi-Extension FITS (MEF: `IMAGE`, `FLAGS`, `VARIANCE`, `ZODI`, `ePSF`, `WCS-WAVE`), 12,288 HEALPix Order 5 All-Sky Cube, and calibration artifacts.
* **[[04 - SPHEREx Data Access Protocols & TAP]]** — IVOA SIAv2 (5 collections), dynamic Cutout API (`?center=...&size=...`), TAP ADQL (`spherex.plane`), `astroquery` / `pyvo`, and AWS S3 open bucket.
* **[[05 - SPLICES Ice Source Catalog]]** — 8.6M+ point source target list, biogenic ice absorption features ($\text{H}_2\text{O}, \text{CH}_4, \text{CO}_2, \text{CO}$), $< 7.6''$ contamination ratio, and 2MASS/WISE/Gaia cross-matches.
* **[[06 - Special Target Comet 3I ATLAS]]** — 259 exposures of interstellar object 3I/ATLAS, ObsCore VOTables, extended coma photometry warning, and batch shell scripts.
* **[[07 - SPHEREx Spectral Calibrations & Instrument Files]]** — Laboratory Linear Variable Filter (LVF) transmission profiles, 4 spectral granularities (17, 34, 51, 68 sub-channels), `Cent` vs `Allpix` response curves, and Detectors 4-6 x-axis reflection rule.
* **[[08 - SPHEREx Explanatory Supplement Map]]** — Complete structural map, Table of Contents, Table 16 22-bit pixel flags bitmask (`0x0001` to `0x20000000`), persistence decay equations, and FITS header specifications of SSDC-DP-017 v2.1 (84 pages).
* **[[09 - Explanatory Supplement Ch 1 Mission & Payload Overview]]** — Chapter 1 deep dive: launch parameters, 3 science themes, BCP-100 spacecraft, dual SWIR/MWIR FPAs (62 K / 45 K), and the half-channel Nyquist shift between Survey 1/2 and Survey 3/4.
* **[[10 - Explanatory Supplement Ch 2 Data Products & Anomalies]]** — Chapter 2 deep dive: 6 HDU Level 2 MEF architecture, optical anomalies (snowballs, frame edge ghosts, 8° ghosts, Moon glint, He I airglow, shuttle glow), and 12,288 HEALPix Order 5 All-Sky Cubes with spatial-spectral entanglement caveats.
* **[[11 - Explanatory Supplement Ch 3 Data Processing Pipeline]]** — Chapter 3 deep dive: 12-step Level 2 pipeline flow, Robberto (2007) variance equation, multi-exponential persistence decay ($I_p(t) = \sum A_n C_n e^{-t/\tau_n}$), Gaia DR3 fine astrometry (`FINAST`), ghost masking radius equations, forced aperture photometry, and mosaic reprojection.
* **[[12 - Explanatory Supplement Ch 4 Calibrations & Instrument Models]]** — Chapter 4 deep dive: absolute gain derivation ($\text{e}^-/\text{s} \to \text{MJy/sr}$), $33 \times 33$ px ePSF models ($21 \times 21$ vs $11 \times 41$ zones), and complete 102-channel tables highlighting biogenic ice diagnostics ($\text{H}_2\text{O}$ $3.033\ \mu\text{m}$, $\text{CO}_2$ $4.294\ \mu\text{m}$, $\text{CO}$ $4.669\ \mu\text{m}$).
* **[[13 - Explanatory Supplement Ch 5-8 FITS Headers & Reference]]** — Chapters 5–8 deep dive: primary HDU header keywords (`OBSID`, `BUNIT`, `FINAST`, `L2DQA`), 4th-order SIP distortion matrices, calibration provenance UUIDs in `HISTORY`, and master 30+ acronym index.
* **[[IRSA_SPHEREX_SITEMAP]]** — Complete crawl sitemap, node graph, and resource directory.
* **[[IRSA_SPHEREX_SITEMAP]]** — Complete crawl sitemap and graph.

---

## 📊 Summary of Spectral Bands
- **Detector 1:** $0.75 - 1.11\ \mu	ext{m}$, Resolving power $R \sim 41$
- **Detector 2:** $1.11 - 1.64\ \mu	ext{m}$, Resolving power $R \sim 41$
- **Detector 3:** $1.64 - 2.42\ \mu	ext{m}$, Resolving power $R \sim 41$
- **Detector 4:** $2.42 - 3.82\ \mu	ext{m}$, Resolving power $R \sim 35$
- **Detector 5:** $3.82 - 4.42\ \mu	ext{m}$, Resolving power $R \sim 110$ (Ice band absorption)
- **Detector 6:** $4.42 - 5.00\ \mu	ext{m}$, Resolving power $R \sim 130$ ($CO_2$ & organics)
