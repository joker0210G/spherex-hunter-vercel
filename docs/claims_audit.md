# 🔍 SPHEREx Hunter - Claims Audit & Real-Data Epoch Pairing Verification
> **Audit Standard:** Empirical Verification against NASA IRSA TAP (`https://irsa.ipac.caltech.edu/TAP`, table `spherex.obscore`)  
> **Date:** 2026-11-14 | **Auditor:** Senior Astronomical-Software Engineer & Astrophysicist  
> **Status:** All quantitative claims audited and classified as **VERIFIED**, **UNVERIFIED**, or **WRONG**.

---

## 1. Quantitative Claims Audit Matrix

| ID | Claim in Phase 1 / `docs/epoch_pairing.md` | Verification Method & Real Command Output | Status | Scientific Assessment / Correction |
| :---: | :--- | :--- | :---: | :--- |
| **C1** | *SPHEREx Level-2 images have dimension $2040 \times 2040$ pixels, unit `MJy / sr`, and 7 HDU extensions.* | `astropy.io.fits.open('data_samples/spherex_level2_sample.fits').info()` -> PRIMARY, IMAGE ($2040 \times 2040$, `float32`, `MJy / sr`), FLAGS, VARIANCE, ZODI, EPSF, WCS-WAVE. | **VERIFIED** | Matches official mission FITS specification exactly. |
| **C2** | *SPHEREx pixel scale is $6.2''/\text{pixel}$ and pixel solid angle $\Omega_{\text{pix}} \approx 9.035 \times 10^{-10}\,\text{sr}$.* | `compute_pixel_solid_angle_sr(wcs)` -> $\text{scale} = 6.20''$, $\Omega = (6.2 / 206264.8)^2 = 9.035 \times 10^{-10}\,\text{sr}$. | **VERIFIED** | Mathematical identity derived directly from FITS WCS CDELT. |
| **C3** | *Parallax amplitude at $d = 500\,\text{AU}$ is $206{,}265 / d \approx 412.53''$.* | `pytest tests/test_motion_models.py::test_parallax_amplitude_at_500_au` -> PASSED ($412.53''$). | **VERIFIED** | Exact trigonometric identity: $\varpi = 1\,\text{AU} / d$. |
| **C4** | *Earth's peak reflex parallax rate at $500\,\text{AU}$ is $\approx 0.30''/\text{hr}$.* | `pytest tests/test_motion_models.py::test_peak_parallax_rate_at_500_au` -> PASSED ($0.296''/\text{hr}$). | **VERIFIED** | Computed from true Astropy Earth barycentric velocity ($29.78\,\text{km/s}$). |
| **C5** | *WISE 0855 has 2 SPHEREx exposures separated by 6 months in Band 5 ($3.82\text{--}4.42\,\mu\text{m}$).* | Real IRSA query `spherex.obscore`: Found 5 exposures at $(\alpha=133.795^\circ, \delta=-7.245^\circ)$ in Band D3 ($1.63\text{--}2.43\,\mu\text{m}$) and Band D6 ($4.41\text{--}5.01\,\mu\text{m}$) at MJD 60993.505 and MJD 61021.351. Time separation is $\Delta t = 27.85\,\text{days}$, not 183 days! | **WRONG** | Corrected: Real SPHEREx passes covering WISE 0855 are in Bands D3 and D6 with $\Delta t = 27.85\,\text{days}$ (cadence within same survey season), not Band 5. |
| **C6** | *Barnard's Star has SPHEREx exposures in Band 2 separated by 183 days.* | Real IRSA query `spherex.obscore`: Found 39 exposures in Bands D3 and D6, observed across MJD 60908.64 and 60912.03 ($\Delta t = 3.39\,\text{days}$), followed by second epoch passes. | **WRONG** | Corrected: Detectors are D3 and D6; initial repeat cadence is 3.4 days, enabling short-baseline asteroid discrimination. |
| **C7** | *RW Aurigae has 2 SPHEREx exposures in Band 4 ($2.42\text{--}3.82\,\mu\text{m}$).* | Real IRSA query `spherex.obscore`: Cone search at $(77.10667^\circ, 30.40111^\circ)$ returned **0 rows**! | **WRONG** | **Honest finding:** RW Aurigae currently has **zero** public SPHEREx exposures in IRSA! Claims of SPHEREx Band 4 differencing on RW Aurigae were unverified prototype hypotheses. Pipeline must flag: *"No public SPHEREx coverage; fallback to 2MASS/WISE"*. |
| **C8** | *R Draconis has $>15$ wavelength-matched pairs in IRSA.* | Real IRSA query `spherex.obscore`: Returned **50 exposures** (query capped at TOP 50) in Bands D2 and D5 across multiple MJDs (60841+). | **VERIFIED** | Near North Ecliptic Pole; high-density multi-epoch coverage confirmed. |
| **C9** | *Stationary stars in ZOGY subtraction leave residuals below $3.5\sigma$.* | `pytest tests/test_differencing.py::test_stationary_star_leaves_no_dipole_residuals` -> PASSED ($\max |S_{\text{corr}}| = 2.41\sigma < 3.5\sigma$). | **VERIFIED** | Optimal PSF matching prevents dipole residuals on stationary stars. |
| **C10** | *Injected moving source is recovered at $>10\sigma$ with sub-pixel centroid accuracy ($<0.5\,\text{px}$).* | `pytest tests/test_differencing.py::test_injected_moving_source_recovered` -> PASSED (detected at $88.66\sigma$, $\Delta x = 0.01\,\text{px}$, $\Delta y = 0.02\,\text{px}$). | **VERIFIED** | ZOGY matched filter score image centroids point sources accurately. |

---

## 2. Rebuilt Epoch-Pairing Table from Real NASA IRSA ObsCore Queries
*Source Table: `spherex.obscore` (Total rows: 1,628,318). Cached locally at `data_samples/irsa_obscore_cache.json`.*

| Target | Target Coordinates ($\alpha, \delta$) | Real SPHEREx Exposures | Public Survey Status | Detectors Available | Observed Wavelength Ranges ($\mu\text{m}$) | Observation Dates (MJD) | Verified Wavelength-Matched Pairs | Recommended Scientific Pipeline Path |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **WISE 0855-0714** | $133.795^\circ, -7.245^\circ$ | **5** | **Public** | D3, D6 | $1.63\text{--}2.43$, $4.41\text{--}5.01$ | 60993.51, 61021.35 | **2 Matched Pairs** (D3-D3, D6-D6 at $\Delta t = 27.85\,\text{d}$) | **ZOGY Differencing** on real 27.8d pairs; Forward-model on 2MASS/SPHEREx |
| **Barnard's Star** | $269.452^\circ, +4.693^\circ$ | **39** | **Public** | D3, D6 | $1.63\text{--}2.43$, $4.41\text{--}5.01$ | 60908.64, 60912.03, ... | **>10 Matched Pairs** | **ZOGY Differencing** on 3.4d and multi-month pairs; Astrometry check |
| **Epsilon Indi B** | $330.840^\circ, -56.788^\circ$ | **29** | **Public** | D3, D6 | $1.63\text{--}2.43$, $4.41\text{--}5.01$ | 60794.68, ... | **>8 Matched Pairs** | **ZOGY Differencing** on repeated visits; companion photometry |
| **RW Aurigae** | $77.107^\circ, +30.401^\circ$ | **0** | **Not in ObsCore** | None | None | None | **0 Matched Pairs** | **Honest UI Notification:** No SPHEREx coverage; Multi-survey 2MASS/WISE forward model |
| **R Draconis** | $248.338^\circ, +66.703^\circ$ | **50+** | **Public** | D2, D5 | $1.10\text{--}1.65$, $3.81\text{--}4.43$ | 60841.45, ... | **>25 Matched Pairs** | **ZOGY Multi-Epoch Stack** (Deep NEP polar survey cadence) |
| **Leo Minor Locus** | $160.615^\circ, +30.669^\circ$ | **35** | **Public** | D1, D4 | $0.75\text{--}1.12$, $2.40\text{--}3.85$ | 60789.75, ... | **>10 Matched Pairs** | **Ground-truth FITS sample verification** (`spherex_level2_sample.fits`) |

---

## 3. Key Findings & Adjustments for Phase 2 Validation

1. **SPHEREx Release Coverage Reality:**  
   The SPHEREx data release in IRSA ObsCore has extensive coverage ($1.62\times 10^6$ exposures), but coverage is non-uniform across the sky. High-ecliptic-latitude targets (R Draconis) have dozens of visits, while equatorial targets (WISE 0855) have 5, and certain Galactic coordinates (RW Aurigae) have zero public exposures. The pipeline must gracefully display: *"0 SPHEREx exposures covering target in current release"* rather than inventing artificial data.
2. **Cadence Correction:**  
   Initial SPHEREx visits over the same field in the current release are separated by hours to weeks ($\Delta t \approx 3\text{--}28\,\text{days}$), rather than an idealized 183-day half-year cadence. This provides sensitivity to Kuiper Belt Objects, Centaurs, and high-rate asteroids, but requires tracklet linking (Step 2.5) across the full survey baseline.

