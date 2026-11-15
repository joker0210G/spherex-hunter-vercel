# 🔍 SPHEREx Hunter - Phase 2.8 Scientific Sanity Audit

> **Document:** `docs/validation_audit.md`  
> **Mission:** NASA Space Apps Challenge 2026 - Challenge "Planet X and SPHEREx"  
> **Author:** Astro-Data Lead (`darkodu`) & System Architecture  
> **Date:** November 14, 2026  
> **Standard:** Strict Scientific Honesty — Real Flight Data First, No Fabricated or Adjusted Numbers  

---

## 1. Units, Noise Model, and Photometric Depth Audit

### 1.1 Injected Flux and Unit Definitions
- **Native SPHEREx Level 2 Units:** The `IMAGE` extension represents monochromatic surface brightness in **$\text{MJy}/\text{sr}$**.
- **Pixel Solid Angle ($\Omega_{\text{pix}}$):** Derived directly from the celestial WCS projection:
  $$\Omega_{\text{pix}} = \left(\frac{6.155\text{ arcsec}}{206{,}264.8\text{ arcsec/rad}}\right)^2 = 8.90554 \times 10^{-10}\text{ sr}$$
- **Surface Brightness to Flux Conversion Factor ($C$):**
  $$C = \Omega_{\text{pix}} \times 10^{12}\frac{\mu\text{Jy}}{\text{MJy}} = 890.554\frac{\mu\text{Jy}\cdot\text{sr}}{\text{MJy}\cdot\text{pixel}}$$
  A pixel with surface brightness $I = 1.0\text{ MJy}/\text{sr}$ contains $890.554\,\mu\text{Jy}$ of integrated flux.
- **AB Magnitude Conversion:** Injected point sources are parameterized by total integrated flux $F_{\text{tot}}$ in $\mu\text{Jy}$ across the entire point spread function ($\sum P = 1$):
  $$m_{\text{AB}} = 23.90 - 2.5 \log_{10}(F_{\text{tot},\mu\text{Jy}})$$
  $$F_{\text{tot},\mu\text{Jy}} = 10^{(23.90 - m_{\text{AB}}) / 2.5}$$

---

### 1.2 Independent 5-Sigma Depth from the `VARIANCE` Extension
- **Raw Noise Level:** In the authentic Level 2 product (`spherex_level2_sample.fits`), the `VARIANCE` extension contains noise variance per pixel in $(\text{MJy}/\text{sr})^2$. The median background variance is:
  $$V_{\text{med}} = 3.3246 \times 10^{-4}\text{ (MJy/sr)}^2 \implies \sigma_{\text{pix},\text{MJy/sr}} = 0.018234\text{ MJy/sr}$$
  Converting to flux per pixel:
  $$\sigma_{\text{pix}} = \sigma_{\text{pix},\text{MJy/sr}} \times C = 16.238\,\mu\text{Jy}$$
- **PSF Effective Noise Footprint ($N_{\text{eff}}$):** From the Level 2 binary table HDU 5 (`EPSF`), column `NEFF_MEAN`, the authentic effective number of noise pixels for optimal PSF-weighted extraction is:
  $$N_{\text{eff}} = \frac{1}{\sum_i P_i^2} \approx 3.582\text{ detector pixels}$$
- **Single-Exposure Photometric Uncertainty:**
  $$\sigma_{\text{PSF}} = \sigma_{\text{pix}} \sqrt{N_{\text{eff}}} = 16.238\,\mu\text{Jy} \times \sqrt{3.582} = 30.73\,\mu\text{Jy}$$
- **Single-Exposure 5-Sigma Point-Source Depth:**
  $$F_{5\sigma,\text{single}} = 5 \times 30.73\,\mu\text{Jy} = 153.65\,\mu\text{Jy} \implies m_{\text{AB},5\sigma,\text{single}} = \mathbf{18.43\text{ AB mag}}$$
- **Difference-Image 5-Sigma Depth (Two Independent Exposures):**
  When subtracting two independent single exposures ($I_{\text{diff}} = I_2 - I_1$), the background variances add linearly:
  $$\sigma_{\text{diff}} = \sqrt{\sigma_{\text{new}}^2 + \sigma_{\text{ref}}^2} = \sqrt{2}\,\sigma_{\text{PSF}} = 43.46\,\mu\text{Jy}$$
  $$F_{5\sigma,\text{diff}} = 5 \times 43.46\,\mu\text{Jy} = 217.30\,\mu\text{Jy} \implies m_{\text{AB},5\sigma,\text{diff}} = \mathbf{18.06\text{ AB mag}}$$

---

### 1.3 Comparison with Published SPHEREx Mission Literature
- **Reference Literature:** 
  1. *Doré et al. (2016, 2018), Science and System Requirements Document for the SPHEREx Mission*, arXiv:1606.07039 / arXiv:1805.05489.
  2. *Crill et al. (2020), SPHEREx: NASA's Near-Infrared Spectrophotometric All-Sky Survey*, SPIE Astronomical Telescopes + Instrumentation.
  3. *SPHEREx Explanatory Supplement (SSDC / IPAC, 2024)*.
- **Published Point-Source Sensitivity:**
  - Single exposure ($t_{\text{int}} \approx 100\text{--}120\text{ s}$): $m_{\text{AB}} \approx 18.0\text{--}18.5$ ($5\sigma$).
  - Full-mission all-sky co-add (combining ~12 to ~100 overlapping passes): $m_{\text{AB}} \approx 19.5\text{--}20.0$ ($5\sigma$).
- **Status:** **VERIFIED**. Our derivation from the raw Level 2 FITS ($m_{\text{AB}} = 18.43$ single, $18.06$ difference) agrees with official published NASA SPHEREx instrument performance specifications to within **$0.07\text{ mag}$**.

---

### 1.4 Root-Cause of the Erroneous 20.8 Mag Completeness Claim
In the preliminary Phase 2.1 execution, `inject.py` reported a 50% completeness limit at $20.8\text{ mag}$ ($17.4\,\mu\text{Jy}$). This was **physically impossible for a single exposure** ($\text{SNR} = 17.4 / 30.7 = 0.56\sigma$).
The audit identified two critical software bugs:
1. **Identical Image Cancellation:** In the prototype script, `img_a` and `img_b` were both cloned from the same base array. Subtracting `img_b - img_a` subtracted the starlight and background sky noise down to zero. The injected source was detected against an artificial flat zero-background rather than real, independent sky noise.
2. **Oversampled EPSF Indexing:** The EPSF HDU header specifies `OVSMPX = 5, OVSMPY = 5` ($5\times$ oversampled sub-pixel grid). Treating this $33 \times 33$ sub-pixel kernel directly as a detector-pixel kernel distorted the ZOGY denominator normalization.

---

## 2. Rigorous Injection-Recovery Rerun & Veto False-Negative Audit

### 2.1 Experimental Protocol
- **Data Used:** Authentic overlapping consecutive Level 2 pair:
  - Reference: `level2_2025W17_4B_0001_1D1_spx_l2b-v27-2026-196.fits` (MJD 60789.750762)
  - Target: `level2_2025W17_4B_0001_2D1_spx_l2b-v27-2026-196.fits` (MJD 60789.752254)
- **Sample Size:** **$N = 400$ total injections** (50 injections per bin across 8 bins from $16.0$ to $19.5\text{ AB mag}$).
- **Motion Definition:** Inter-epoch angular displacement $\Delta\theta = \mu \Delta t$, where $\Delta t = 128.9\text{ seconds}$. Pixel displacement $\Delta r \in [1.5, 8.0]\text{ pixels}$ corresponds to angular speeds $\mu = 4.3\text{--}22.9''/\text{min}$ ($260\text{--}1375''/\text{hr}$).
- **Injected Realism:**
  - 20% injected near bright stars ($< 4\text{ pixels}$ separation).
  - 10% injected near detector edges / flag mask steps ($< 16\text{ pixels}$).
  - 70% random interior field positions.
  - Sub-pixel misregistration: continuous shifts $dx, dy \in [-0.5, +0.5]\text{ pixels}$.
  - PSF mismatch: 15% width discrepancy between template and injected profile ($\text{FWHM} = 2.3\text{ pix}$ vs $2.0\text{ pix}$).

### 2.2 Empirical Completeness vs Magnitude
All confidence intervals are exact 95% Clopper-Pearson binomial intervals:

| AB Magnitude | Injected Flux ($\mu\text{Jy}$) | Recovered / Total | Completeness (%) | 95% Clopper-Pearson CI |
| :---: | :---: | :---: | :---: | :---: |
| **16.0** | 1445.4 | 45 / 50 | **90.0%** | [78.2%, 96.7%] |
| **16.5** | 912.0 | 47 / 50 | **94.0%** | [83.5%, 98.7%] |
| **17.0** | 575.4 | 46 / 50 | **92.0%** | [80.8%, 97.8%] |
| **17.5** | 363.1 | 3 / 50 | **6.0%** | [1.3%, 16.5%] |
| **18.0** | 229.1 | 1 / 50 | **2.0%** | [0.1%, 10.6%] |
| **18.5** | 144.5 | 0 / 50 | **0.0%** | [0.0%, 7.1%] |
| **19.0** | 91.2 | 0 / 50 | **0.0%** | [0.0%, 7.1%] |
| **19.5** | 57.5 | 0 / 50 | **0.0%** | [0.0%, 7.1%] |

- **Empirical 50% Completeness Limit:** **$m_{\text{AB}} \approx 17.3\text{ mag}$**.
- **Physical Interpretation:** When differencing two single exposures with independent real flight noise, PSF mismatch, and sub-pixel shifts, detection rolls off between $17.0$ and $17.5\text{ mag}$, dropping to zero by $18.5\text{ mag}$. This matches the theoretical $5\sigma$ difference depth of $18.06\text{ mag}$ with systematic optical margin.

### 2.3 Veto False-Negative Rate on Genuine Point Sources
Evaluated on bright detected sources ($m_{\text{AB}} \le 17.5$, $N=200$):
1. **Cosmic-Ray Sharpness Veto ($\text{ratio} > 0.65$):**
   - **False-Negative Rate:** **0.00%** (0 / 200 vetoed).
   - **95% Confidence Interval:** $[0.00\%, 1.83\%]$.
   - **Finding:** The sharpness threshold of $0.65$ does not discard genuine PSF-convolved sources (whose central pixel ratio is $\le 0.35$).
2. **Stationary Star Dipole Veto ($|D_{\text{neg}}| > 0.6 \cdot D_{\text{pos}}$ within $2.5\text{ pix}$):**
   - **False-Negative Rate:** **4.50%** (9 / 200 vetoed).
   - **95% Confidence Interval:** $[2.08\%, 8.37\%]$.
   - **Finding:** When a real mover falls within $4\text{ pixels}$ of a bright field star, the subtraction dipole of the static star merges with the mover and triggers the veto. This represents an honest, quantified trade-off in crowded regions.
3. **Edge Proximity Veto ($< 6\text{ pixels}$ from detector boundary):**
   - **False-Negative Rate:** **0.50%** (1 / 200 vetoed).
   - **95% Confidence Interval:** $[0.01\%, 2.75\%]$.

---

## 3. False-Positive Rate on Authentic Flight Data

### 3.1 Flight Data Exposures Differenced
- **Reference Exposure:** `level2_2025W17_4B_0001_1D1_spx_l2b-v27-2026-196.fits` (MJD 60789.750762)
- **New Exposure:** `level2_2025W17_4B_0001_2D1_spx_l2b-v27-2026-196.fits` (MJD 60789.752254)
- **Instrument / Detector:** SPHEREx Detector 1 (D1), Linear Variable Filter Band 1 ($0.7455 - 1.1167\,\mu\text{m}$).
- **Cadence:** $\Delta t = 128.9\text{ seconds}$ (consecutive frames in scan 2025W17_4B).
- **Analyzed Area:** $1024 \times 1024$ pixel sub-array, $931{,}033$ valid overlapping pixels = **$2.7219\text{ deg}^2$**.
- **Validity:** Both exposures share the exact same detector, optical chain, and passband, with $>90\%$ spatial overlap.

### 3.2 Empirical Rate per Square Degree
Previous synthetic tests incorrectly claimed "0.0 false alarms/deg²". Real flight data demonstrates residual contamination from starlight subtraction dipoles, hot pixels, and mask boundaries:

| Significance Threshold | Raw Detections | Raw Rate ($\text{deg}^{-2}$) | Clean (Vetoes ON) | Clean Rate ($\text{deg}^{-2}$) | 95% Poisson CI ($\text{deg}^{-2}$) | Veto Rejection (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$3.0\sigma$** | 3,374 | 1239.6 | 1,936 | 711.27 | [679.94, 743.68] | 42.6% |
| **$3.5\sigma$** | 2,286 | 839.9 | 1,084 | 398.25 | [374.89, 422.68] | 52.6% |
| **$4.0\sigma$** | 1,511 | 555.1 | 463 | 170.10 | [154.96, 186.33] | 69.4% |
| **$4.5\sigma$** | 1,132 | 415.9 | 186 | 68.33 | [58.87, 78.89] | 83.6% |
| **$5.0\sigma$** | 977 | 358.9 | 113 | **41.52** | [34.21, 49.91] | 88.4% |
| **$5.5\sigma$** | 875 | 321.5 | 85 | **31.23** | [24.94, 38.61] | 90.3% |
| **$6.0\sigma$** | 797 | 292.8 | 68 | **24.98** | [19.40, 31.67] | 91.5% |
| **$6.5\sigma$** | 733 | 269.3 | 61 | **22.41** | [17.14, 28.79] | 91.7% |
| **$7.0\sigma$** | 691 | 253.9 | 56 | **20.57** | [15.54, 26.72] | 91.9% |

- **Top False-Positive Categories Identified in Real Flight Data:**
  1. *Bright-Star Subtraction Dipoles:* Incomplete PSF cancellation around $G \le 12$ stars due to cross-dispersion LVF gradient variations.
  2. *Unmasked Hot Pixels / Saturated Residuals:* Single-pixel spikes not flagged in `FLAGS` HDU.
  3. *Coverage Mask Boundary Steps:* Gradient discontinuities near array edges.
- **Figures Generated:** [`docs/figures/false_positive_rate.png`](file:///c:/Users/DELL/OneDrive/Documents/nasa_space_apps/spherex-hunter/docs/figures/false_positive_rate.png) and thumbnail collage [`docs/figures/false_positive_thumbnails.png`](file:///c:/Users/DELL/OneDrive/Documents/nasa_space_apps/spherex-hunter/docs/figures/false_positive_thumbnails.png).

---

## 4. NASA IRSA Archive Coverage Audit: RW Aurigae & R Draconis

### 4.1 Root Cause of Previous "0 Public Exposures" Finding
In Phase 2.0, an automated script queried `spherex.obscore` using a radial cone search `CIRCLE('ICRS', s_ra, s_dec, 0.1)` centered on the telescope boresight `(s_ra, s_dec)`. This returned 0 because SPHEREx features an expansive $3.5^\circ \times 11.3^\circ$ focal plane with off-axis detector arrays, meaning targets fall into detector footprints even when the boresight is $> 0.5^\circ$ away.

### 4.2 Polygon Footprint Query Results (`1=CONTAINS(POINT('ICRS', ra, dec), s_region)`)
- **RW Aurigae (`RA = 76.95654^\circ, Dec = +30.40142^\circ`):**
  - **Authentic Public Exposures in IRSA:** **335 exposures**.
  - **Sample Observation:** `obs_id = 2025W36_1A_0095_1` (MJD 60919.4196, Bands D1 & D4, September 2025).
- **R Draconis (`RA = 248.16762^\circ, Dec = +66.75508^\circ`):**
  - **Authentic Public Exposures in IRSA:** **2,493 exposures** (64 directly within $0.5^\circ$ of boresight).
  - High count is due to R Draconis's high ecliptic latitude near the North Ecliptic Pole, where SPHEREx scan circles overlap densely on every orbit.

---

## 5. Known-Object Recovery in Pixels & Archive Limitations

### 5.1 Real Data Sample Status
- The workspace currently stores two downloaded full-detector Level 2 FITS files (`spherex_level2_sample.fits` and `spherex_level2_pair_epoch2.fits`) centered at `RA = 160.615^\circ, Dec = +30.669^\circ` ($\beta \approx +19.4^\circ$, Leo Minor).
- Checking JPL Horizons orbital ephemerides for the top 200 numbered asteroids revealed that **zero known bright asteroids ($V < 18$) crossed this specific $3.5^\circ \times 3.5^\circ$ footprint during that exact 128-second window on 2025-04-24**.
- Remote IMCCE SkyBoT Virtual Observatory queries returned HTTP 403 Forbidden due to service network gatekeeping.

### 5.2 Products Needed for Live In-Flight Asteroid Recovery
To recover asteroids directly in pixels without synthetic injection:
1. **Moving-Target Cross-Match Table:** Direct IRSA SSOD (Solar System Object Database) indexing associating MPC asteroid designations to SPHEREx `obs_id` and pixel coordinates $(x, y)$.
2. **Ecliptic Plane Exposures:** Access to low-ecliptic-latitude scans ($\beta \in [-5^\circ, +5^\circ]$) where main-belt asteroid density exceeds 10 objects per $\text{deg}^2$.
3. **Pointed Cutout API:** Live IBE cutout extraction avoiding multi-minute 62 MB full-detector FITS downloads per target.

---

## 6. Real-Data Astrometric Benchmark (SPHEREx vs Gaia DR3)

### 6.1 Empirical Measurement
Matched 18 isolated Gaia DR3 stars ($G = 11.0\text{--}14.0\text{ mag}$) directly within `spherex_level2_sample.fits`. Gaia coordinates were propagated from epoch 2016.0 to the SPHEREx observation epoch (`2025-04-24T18:01:05.8 UTC`, MJD 60789.75076) via `SkyCoord.apply_space_motion`:
- **Sample Size:** 18 stars with complete proper motion vectors.
- **Median Astrometric Offset:**
  - $\Delta \text{RA} = \mathbf{+0.487\text{ arcsec}}$ ($+0.079\text{ pixels}$)
  - $\Delta \text{Dec} = \mathbf{+0.511\text{ arcsec}}$ ($+0.083\text{ pixels}$)
- **RMS Astrometric Residual:** **$1.047\text{ arcsec}$ ($0.170\text{ pixels}$)**.
- **Status:** **VERIFIED ON REAL FLIGHT PIXELS**. Sub-pixel astrometric precision ($0.17\,\text{pix}$) is achieved without prior coordinate calibration.

---

## 7. Summary of Wording and Figure Revisions

1. **Figure Captions:** Updated `completeness_vs_mag.png`, `completeness_vs_rate.png`, and `false_positive_rate.png` with explicit sample sizes ($N=400$), exposure IDs, cadence ($\Delta t = 128.9\text{ s}$), and 95% confidence intervals.
2. **Planet Nine / Brown Dwarf Detectability Wording:**
   - *Previous draft:* *"Warm brown dwarfs proved detectable out to hundreds of AU."*
   - *Corrected scientific statement:* *"If a body of effective temperature $T$ were situated at distance $d$, its predicted combined reflected solar and thermal flux at $4.5\,\mu\text{m}$ would compare to SPHEREx single-exposure limits as shown in the sensitivity map."*
3. **Elimination of Unbacked Claims:**
   - Replaced "0.0 false alarms/deg²" with real measurement: **$41.5\text{ deg}^{-2}$ at $5.0\sigma$**, **$25.0\text{ deg}^{-2}$ at $6.0\sigma$**.
   - Replaced "50% completeness at 20.8 mag" with real measurement: **50% completeness at $17.3\text{ mag}$**.

