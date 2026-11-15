# 📊 SPHEREx Hunter - Comprehensive Scientific Validation Report

> **Evaluation Phase:** Phase 2.8 (Rigorous Real Data Validation & Scientific Sanity Audit)  
> **Mission Dataset:** Authentic NASA SPHEREx Level-2 MEF FITS Pair:
> - `level2_2025W17_4B_0001_1D1_spx_l2b-v27-2026-196.fits` (MJD 60789.750762)
> - `level2_2025W17_4B_0001_2D1_spx_l2b-v27-2026-196.fits` (MJD 60789.752254)  
> **Date:** 2026-11-14 | **Team:** Team RIP

---

## 1. Executive Summary & Validation Methodology

SPHEREx Hunter subjects all algorithmic components to empirical validation on real flight data. Rather than fine-tuning thresholds or masking failures, this report presents the unvarnished findings, detection completeness limits, false-positive rates, astrometric accuracy against Gaia DR3, and physical detectability maps.

### Figures Produced in Validation:
1. **Completeness vs Magnitude:** [`docs/figures/completeness_vs_mag.png`](file:///c:/Users/DELL/OneDrive/Documents/nasa_space_apps/spherex-hunter/docs/figures/completeness_vs_mag.png)  
   *(Sample: N=400 injections across 8 magnitude bins, real flight pair with independent noise, 95% Clopper-Pearson binomial CI)*
2. **Completeness vs Motion Rate:** [`docs/figures/completeness_vs_rate.png`](file:///c:/Users/DELL/OneDrive/Documents/nasa_space_apps/spherex-hunter/docs/figures/completeness_vs_rate.png)  
   *(Sample: N=200 bright injections $m_{\text{AB}} \le 17.5$, 15% PSF width mismatch and sub-pixel misregistration, 95% CI)*
3. **Empirical False Positive Rate:** [`docs/figures/false_positive_rate.png`](file:///c:/Users/DELL/OneDrive/Documents/nasa_space_apps/spherex-hunter/docs/figures/false_positive_rate.png)  
   *(Sample: Authentic consecutive flight pair, 2.7219 deg² overlap, Poisson 95% CI)*
4. **False Alarm Residual Collage:** [`docs/figures/false_positive_thumbnails.png`](file:///c:/Users/DELL/OneDrive/Documents/nasa_space_apps/spherex-hunter/docs/figures/false_positive_thumbnails.png)  
   *(Top false alarm categories: bright star subtraction dipoles, unmasked spikes, boundary steps)*
5. **Physical Detectability Calculator:** [`docs/figures/detectability_map.png`](file:///c:/Users/DELL/OneDrive/Documents/nasa_space_apps/spherex-hunter/docs/figures/detectability_map.png)  
   *(Reflected sunlight + blackbody thermal emission vs SPHEREx single-exposure 5σ sensitivity)*

---

## 2. Injection-Recovery Completeness Benchmark (`validation/inject.py`)

Using the authentic empirical Point Spread Function (`HDU 5: EPSF`, $N_{\text{eff}} = 3.582\text{ pix}$) and detector noise variance from real Level-2 exposures, 400 synthetic point sources were injected into independent real flight noise:
- **Flux Range:** $57.5\,\mu\text{Jy}$ to $1445.4\,\mu\text{Jy}$ ($m_{\text{AB}} = 16.0\text{--}19.5\,\text{mag}$).
- **Motion Rate:** $4.3''/\text{min}$ to $22.9''/\text{min}$ ($\Delta s = 1.5\text{--}8.0\,\text{pixels}$ across survey cadence $\Delta t = 128.9\text{ s}$).
- **Systematic Realism:** 20% placed near bright stars, 10% near detector edges, 15% PSF width mismatch, sub-pixel centering offsets.

### Key Completeness Results:
- **50% Completeness Limit:** $m_{\text{AB}} \approx \mathbf{17.3\text{ mag}}$ ($\approx 436\,\mu\text{Jy}$ at $5.0\sigma$ in difference imaging).
- **90% Completeness Limit:** $m_{\text{AB}} \approx \mathbf{17.0\text{ mag}}$ ($575\,\mu\text{Jy}$, $92.0\%$ completeness, 95% CI: $[80.8\%, 97.8\%]$).
- **Theoretical Single-Exposure 5σ Depth:** $m_{\text{AB}} = 18.43\text{ mag}$ ($153.7\,\mu\text{Jy}$).
- **Theoretical Difference-Image 5σ Depth:** $m_{\text{AB}} = 18.06\text{ mag}$ ($217.3\,\mu\text{Jy}$).

### Veto False-Negative Rate Audit ($m_{\text{AB}} \le 17.5$, $N=200$):
- **Cosmic-Ray Sharpness Veto ($F_{\text{peak}} / F_{3\times 3} > 0.65$):** **0.00% False-Negative Rate** (95% CI: $[0.00\%, 1.83\%]$).
- **Stationary-Star Dipole Veto:** **4.50% False-Negative Rate** (95% CI: $[2.08\%, 8.37\%]$) due to crowding when true movers are located $< 4\text{ pixels}$ from bright static stars.
- **Edge Proximity Veto ($< 6\text{ pixels}$):** **0.50% False-Negative Rate** (95% CI: $[0.01\%, 2.75\%]$).

---

## 3. Empirical False-Positive Rate Benchmark (`validation/false_positives.py`)

Evaluating the pipeline over $2.7219\,\text{deg}^2$ of real overlapping flight data:
- At standard $S_{\text{corr}} \ge 5.0\sigma$ with all scientific vetoes active: **$41.52\text{ false alarms / deg}^2$** (95% Poisson CI: $[34.21, 49.91]$).
- At $S_{\text{corr}} \ge 6.0\sigma$: **$24.98\text{ false alarms / deg}^2$** (95% Poisson CI: $[19.40, 31.67]$).
- Unvetoed raw pixel excursions at $5.0\sigma$ yield $358.9\text{ detections / deg}^2$, demonstrating that our scientific vetoes eliminate **88.4% of all false alarms**.
- The remaining residuals are primarily starlight subtraction dipoles around saturated $G \le 12$ stars due to Linear Variable Filter (LVF) spatial dispersion gradients between exposures.

---

## 4. Astrometric Verification Against Gaia DR3 in Flight Pixels

Comparing SPHEREx-measured pixel centroids directly against propagated Gaia DR3 positions across 18 isolated stars ($G = 11\text{--}14$) in `spherex_level2_sample.fits`:
- **Median Coordinate Offset:** $\Delta \text{RA} = +0.487''$, $\Delta \text{Dec} = +0.511''$.
- **RMS Astrometric Residual:** **$1.047\text{ arcsec}$ ($0.170\text{ pixels}$)**.
- **Finding:** Pixel centroids achieve sub-pixel astrometric alignment ($0.17\,\text{pix}$) without external distortion tuning.

---

## 5. Outer Solar System Detectability Findings (Planet Nine Analysis)

From `validation/detectability_calculator.py`:
1. **Reflected Sunlight:** At $d \ge 400\,\text{AU}$, geometric attenuation drops as $1/d^4$. For a $3\,R_\oplus$ body with albedo $p = 0.4$, reflected flux at $4.5\,\mu\text{m}$ is $F_{\text{refl}} < 10^{-4}\,\mu\text{Jy}$ ($m_{\text{AB}} > 34\,\text{mag}$), completely undetectable.
2. **Thermal Emission:** For an equilibrium/internal temperature of $T_{\text{eff}} \approx 45\,\text{K}$ (Fortney et al. 2016), the blackbody emission peaks at $\lambda \approx 64\,\mu\text{m}$. At SPHEREx Band 6 ($4.5\text{--}5.0\,\mu\text{m}$), the Wien exponential tail suppresses thermal flux to $< 10^{-15}\,\mu\text{Jy}$.
3. **Scientific Conclusion:**
   - **Hypothetical Cold Planet Nine ($T \approx 45\,\text{K}$, $d \ge 400\,\text{AU}$):** **NOT detectable** by SPHEREx in direct imaging. Any claim to detect cold Planet Nine with SPHEREx in single exposures is unphysical.
   - **Substellar Bodies & Brown Dwarfs:** If a body of effective temperature $T$ were situated at distance $d$, its predicted combined reflected solar and thermal flux at $4.5\,\mu\text{m}$ would compare to SPHEREx limits as shown in the sensitivity map (e.g. bodies with $T \ge 250\,\text{K}$ are detectable out to tens of parsecs).

---

## 6. Limitations, Negative Results & Fallbacks

1. **Polygon Footprint vs Boresight Cone Queries:**  
   In IRSA TAP `spherex.obscore`, queries centered on boresight `(s_ra, s_dec)` miss exposures because SPHEREx has an extensive off-axis focal plane. When using spatial polygon containment `1=CONTAINS(POINT('ICRS', ra, dec), s_region)`:
   - **RW Aurigae:** Has **335 authentic exposures** in IRSA.
   - **R Draconis:** Has **2,493 authentic exposures** in IRSA.
2. **Short-Baseline Distance Degeneracy:**  
   When observation epochs span fewer than 60 days ($\Delta t < 60\,\text{d}$), reflex parallax ellipse curvature is collinear with linear drift. In this regime, distance $d$ is mathematically degenerate. The motion fitter honestly returns:
   `distance_status: "UNCONSTRAINED" (allowed range: [10, 5000] AU)` rather than returning a deceptive point estimate.
3. **In-Flight Asteroid Recovery Constraints:**  
   The sample dataset currently in the repository covers high ecliptic latitude ($\beta \approx +19.4^\circ$), where zero $V < 18$ known asteroids crossed during the 128s observation window. Direct in-flight asteroid validation requires moving-target cross-match indexing (e.g. IRSA SSOD) and low-ecliptic-latitude scans.
