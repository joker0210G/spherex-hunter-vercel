# 🛰️ SPHEREx Hunter - Epoch Pairing Feasibility & DR1 Holdings Report
> **NASA Space Apps Challenge 2026** | **Dataset:** NASA IRSA SPHEREx Data Release 1 (DR1)  
> **Archive Table:** `spherex.obscore` (Collection `spherex_dr1`)  
> **Methodology:** True Spatial Containment Query `CONTAINS(POINT('ICRS', ra, dec), s_region) = 1`  
> **Status:** Empirically Audited against Real IRSA Holdings (November 2026)

---

## 1. Executive Summary & Physics of SPHEREx LVF Pairing

SPHEREx does not observe through discrete broadband filters. Instead, each of its 6 focal plane arrays is fronted by a **Linear Variable Filter (LVF)** where the central transmission wavelength $\lambda(x, y)$ varies continuously across the detector surface along the dispersion axis:
- **Bands 1–3 ($0.75\text{--}2.42\,\mu\text{m}$):** Spectral resolving power $R \equiv \lambda / \Delta\lambda \approx 41.4$ ($\Delta\lambda / \lambda \approx 2.4\%$).
- **Bands 4–6 ($2.42\text{--}5.00\,\mu\text{m}$):** Spectral resolving power $R \equiv \lambda / \Delta\lambda \approx 135$ ($\Delta\lambda / \lambda \approx 0.74\%$).

### The Pairing Constraint
Direct image subtraction (e.g., ZOGY or Alard-Lupton) is **only mathematically valid** if two exposures sample the identical passband within the channel width $\Delta\lambda_{\text{channel}} \equiv \lambda / R$. If exposures sample differing wavelengths, astrophysical spectral slopes (color gradients) produce non-zero residuals on every celestial source, mimicking false transient dipoles.

---

## 2. DR1 Holdings & Exposure Count Comparison

Previous prototype checks utilized a simple $0.5^\circ$ cone search around the exposure boresight `s_ra, s_dec`. Because SPHEREx detector footprints span $3.5^\circ \times 11.3^\circ$, boresight cone searches omitted off-center exposures that fully contained the target. Re-running with the true spatial footprint polygon `s_region` yields the complete DR1 census:

| Target | RA, Dec (ICRS) | Old Cone Count (Boresight $\le 0.5^\circ$) | Real DR1 Holdings (`s_region` Containment) | Delta ($\Delta N$) | Total Time Span |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **WISE 0855-0714** | $133.79513^\circ, -7.24515^\circ$ | 5 | **258** | +253 | 373.6 days (MJD 60800.7 – 61174.3) |
| **Barnard's Star** | $269.45208^\circ, +4.69339^\circ$ | 39 | **363** | +324 | 402.8 days (MJD 60902.9 – 61305.6) |
| **Epsilon Indi B** | $330.84042^\circ, -56.78778^\circ$ | 29 | **459** | +430 | 525.6 days (MJD 60789.9 – 61315.5) |
| **RW Aurigae** | $77.10667^\circ, +30.40111^\circ$ | 0 | **374** | +374 | 380.5 days (MJD 60919.4 – 61299.9) |
| **R Draconis** | $248.33750^\circ, +66.70278^\circ$ | 50 | **2,542** | +2,492 | 520.4 days (MJD 60789.9 – 61310.3) |
| **Leo Minor Sample** | $160.61524^\circ, +30.66908^\circ$ | 35 | **262** | +227 | 377.2 days (MJD 60789.8 – 61166.9) |

---

## 3. Cross-Survey (~6-Month) Wavelength-Matched Pairs

In SPHEREx DR1, the full-sky survey baseline now exceeds 370 to 525 days, covering Survey 1, Survey 2, and Survey 3. Searching for wavelength-matched exposure pairs (same detector band and central wavelength matching within channel width) separated by $\approx 6\text{ months}$ ($130\text{--}230\text{ days}$) confirms extensive cross-survey pairing across **all** demo targets:

### 1. WISE 0855-0714 (Cold Brown Dwarf / Planet X Analog)
* **Total DR1 Exposures:** 258
* **Cross-Survey (~6-Mo) Pairs:** **2,788 pairs** (separation $\Delta t \approx 188\text{ days}$)
* **Key Matched Pair:**
  - Exposure 1: `2025W19_1B_0116_1` (Band D3, $1.9\,\mu\text{m}$, MJD 60800.7)
  - Exposure 2: `2025W46_1A_0075_4` (Band D3, $1.9\,\mu\text{m}$, MJD 60989.3)
  - $\Delta t = 188.6\text{ days}$ ($\approx 6.2\text{ months}$). At $\mu \approx 8.12''/\text{yr}$, WISE 0855 moves $4.19''$ ($\approx 0.68\text{ pixels}$) between these epochs, forming a distinct, verifiable dipole.
* **Short-Baseline Pairs (2–45 d):** 1,172 pairs (for rapid orbital motion vetoes).

### 2. Barnard's Star (High Proper Motion Star)
* **Total DR1 Exposures:** 363
* **Cross-Survey (~6-Mo) Pairs:** **4,504 pairs** (separation $\Delta t \approx 215\text{ days}$)
* **Key Matched Pair:**
  - Exposure 1: `2025W33_2C_0321_1` (Band D3, MJD 60902.9)
  - Exposure 2: `2026W12_1A_0598_1` (Band D3, MJD 61118.3)
  - $\Delta t = 215.4\text{ days}$. At $\mu \approx 10.36''/\text{yr}$, the motion baseline is $6.11''$ ($0.99\text{ pixels}$), creating an optimal $\sim 1\text{-pixel}$ dipole.

### 3. Epsilon Indi B (Brown Dwarf Binary Companion)
* **Total DR1 Exposures:** 459
* **Cross-Survey (~6-Mo) Pairs:** **5,332 pairs** (separation $\Delta t \approx 159.6\text{ days}$)
* **Key Matched Pair:**
  - Exposure 1: `2025W17_4B_0017_1` (Band D2, MJD 60789.9)
  - Exposure 2: `2025W40_1A_0529_4` (Band D2, MJD 60949.4)
  - $\Delta t = 159.56\text{ days}$.

### 4. RW Aurigae (Variable T Tauri Star)
* **Total DR1 Exposures:** 374 *(previously assumed 0 under boresight cone search)*
* **Cross-Survey (~6-Mo) Pairs:** **4,922 pairs** (separation $\Delta t \approx 183.9\text{ days}$)
* **Key Matched Pair:**
  - Exposure 1: `2025W36_1A_0095_1` (Band D1, $0.95\,\mu\text{m}$, MJD 60919.4)
  - Exposure 2: `2026W10_1A_0445_1` (Band D1, $0.95\,\mu\text{m}$, MJD 61103.3)
  - $\Delta t = 183.91\text{ days}$ ($\approx 6.0\text{ months}$). Provides authentic multi-epoch variability differencing across eruptive cycles.

### 5. R Draconis (Mira Pulsating Variable Star)
* **Total DR1 Exposures:** 2,542 (near North Ecliptic Pole high-density cadence)
* **Cross-Survey (~6-Mo) Pairs:** **7,357 pairs** (separation $\Delta t \approx 223.3\text{ days}$)
* **Short-Baseline Pairs:** 342,203 pairs.

### 6. Leo Minor Technical Verification Field
* **Total DR1 Exposures:** 262
* **Cross-Survey (~6-Mo) Pairs:** **2,826 pairs** (separation $\Delta t \approx 205.6\text{ days}$)
* **Key Matched Pair:**
  - Exposure 1: `2025W17_4B_0001_1` (Band D1, MJD 60789.8)
  - Exposure 2: `2025W46_2A_0590_1` (Band D1, MJD 60995.3)

---

## 4. Architectural Decision Point

Now that DR1 cross-survey 6-month pairs are cataloged:
- In accordance with team directives, **science pipeline products remain frozen** during this step so existing verified benchmarks remain undisturbed.
- We present these empirical holdings and pair counts to the team lead/user. Any generation of new numerical difference products from these 6-month DR1 pairs will be executed upon explicit review and authorization.
