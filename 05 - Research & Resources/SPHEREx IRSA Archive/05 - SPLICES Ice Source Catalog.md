---
title: "NASA IRSA SPLICES: SPHEREx Target List of Ice Sources (8.6M Point Sources)"
url: "https://irsa.ipac.caltech.edu/data/SPHEREx/SPLICES/"
tags:
  - nasa
  - spherex
  - irsa
  - splices
  - ices
  - catalog
  - gator
  - cross-match
  - yso
aliases:
  - SPLICES Catalog
  - SPHEREx Ice Sources
  - SPLICES v8.6
created: 2026-11-14
status: active
---

# 🧊 NASA IRSA SPLICES: SPHEREx Target List of Ice Sources
> **Primary Source:** [https://irsa.ipac.caltech.edu/data/SPHEREx/SPLICES/](https://irsa.ipac.caltech.edu/data/SPHEREx/SPLICES/)  
> **Schema Reference:** [https://irsa.ipac.caltech.edu/data/SPHEREx/SPLICES/gator_docs/splices_colDescriptions.html](https://irsa.ipac.caltech.edu/data/SPHEREx/SPLICES/gator_docs/splices_colDescriptions.html)  
> **Dataset DOI:** [`10.26131/IRSA554`](https://doi.org/10.26131/IRSA554)  
> **Canonical Paper:** Ashby et al. (2023), *ApJS*  
> **MOC:** [[00 - Team Command Center]] | [[01 - IRSA SPHEREx Mission Hub]] | [[03 - SPHEREx Science Data Products & Calibration]] | [[Cross-Survey Catalogs (WISE, Gaia, 2MASS)]]

---

## 🌟 Catalog Overview & Scientific Objective
The **SPHEREx Target List of Ice Sources (SPLICES)** is an all-sky compilation of **nearly nine million (8.6+ million) spatially isolated, infrared-bright point sources** selected to investigate the lifecycle of interstellar and circumstellar ices.

When SPHEREx observes these targets across its 102 spectral channels ($0.75 - 5.0\ \mu\text{m}$), the spectra probe absorption features of biogenic and prebiotic volatile ices:
- **$\text{H}_2\text{O}$ Ice:** Broad OH-stretching vibrational band centered at **$3.05\ \mu\text{m}$** (probed by SPHEREx Detector Array 4 & 5).
- **Hydrocarbon Ice ($\text{CH}_4$):** Absorption band at **$3.32\ \mu\text{m}$** and **$3.53\ \mu\text{m}$**.
- **$\text{CO}_2$ Ice:** Deep, sharp bending/stretching mode at **$4.27\ \mu\text{m}$** (probed by Detector Array 5, $R \sim 112$).
- **$\text{CO}$ Ice:** Interstellar CO absorption at **$4.67\ \mu\text{m}$** (probed by Detector Array 6, $R \sim 128$).
- **Methanol ($\text{CH}_3\text{OH}$) & Complex Organics:** Features from $3.53 - 3.90\ \mu\text{m}$.

---

## 📦 Data Products & Deliverables
1. **Full FITS Binary Table:**
   - Filename: `20241107_SPLICESv8.6.fits.gz`
   - Size: **3.1 GB** (compressed gzip FITS table).
   - Rows: $\sim 8,600,000$ validated astronomical targets.
2. **Interactive Gator Search Tool:**
   - Web URL: `https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-scan?submit=Select&projshort=SPHEREX`
   - Allows spatial cone searches, box queries, and multi-band brightness filtering.
3. **Programmatic TAP / ADQL Access:**
   - Catalog Name in IRSA TAP: `spherex_splices`

---

## 🔬 Multi-Survey Cross-Match Architecture
Each SPLICES source is cross-matched across multi-wavelength surveys with rigorous spatial confusion metrics:

```
SPLICES Source (source_id, ra, dec, GAL_LONG, GAL_LAT)
 ├── 2MASS (1999–2001): J, H, K magnitudes, ph_qual, prox
 ├── AllWISE / NEOWISE: W1, W2, W3, W4, cc_flags, var_flg, W1VARAMP, W2VARAMP
 ├── Spitzer IRAC: [3.6], [4.5], [5.8], [8.0] μm (mag3_6, mag4_5, etc.)
 ├── Gaia DR3: G, BP, RP, Parallax (Plx), Proper Motion (pmra, pmdec), Distance (Dist)
 ├── High-Resolution NIR: VISTA VVV (VVVJ, VVVH, VVVK) & UKIDSS (UKSJ, UKSH, UKSK)
 ├── Dust Extinction & Cloud: Line-of-sight Av, Molecular Cloud (MC), Dame et al. CO clouds
 └── Isolation Quality (< 7.6"): numGaiaNB, fluxratioGaia, numIRACnbors, fluxratioI1
```

### 🛡️ The SPHEREx Isolation & Contamination Metric ($< 7.6''$)
Because SPHEREx has a native pixel scale of **$6.2''\text{ / pixel}$** (FWHM $\sim 6''$), point sources in crowded fields (e.g. Galactic Plane) can suffer from flux blending:
- SPLICES explicitly evaluates all neighbor sources within **$7.6''$**.
- Metrics `fluxratioGaia`, `fluxratioI1`, `fluxratioI2` quantify the exact background flux contamination ratio:
  $$\text{fluxratio} = \frac{\sum F_{\text{neighbors}}}{F_{\text{target}}} \times 100\%$$
- Allows filtering for pristine, unblended ice absorption profiles (`fluxratio < 5%`).

---

## 🏷️ Key Schema Fields Reference

| Column Name | Type | Units | Astrophysical Description |
| :--- | :--- | :--- | :--- |
| `source_id` | `long` | — | Unique SPLICES identification number. |
| `designation` | `char` | — | Official source designation string. |
| `ra`, `dec` | `double` | degrees | J2000 ICRS celestial coordinates. |
| `J`, `H`, `K` | `float` | mag | 2MASS near-infrared broadband magnitudes. |
| `W1`, `W2`, `W3`, `W4`| `float` | mag | AllWISE mid-infrared magnitudes ($3.4, 4.6, 12, 22\ \mu\text{m}$). |
| `Plx`, `e_Plx` | `double` | mas | Gaia DR3 trigonometric parallax and $1\sigma$ uncertainty. |
| `pmra`, `pmdec` | `double` | $\text{mas/yr}$| Gaia DR3 proper motion ($\mu_\alpha \cos \delta, \mu_\delta$). |
| `Dist` | `float` | pc | Bailer-Jones geometric distance derived from Gaia DR3. |
| `Av` | `double` | mag | Total visual extinction estimated from $H - W2$ or $K - W2$ color excess. |
| `MC`, `MC_Dist` | `char` / `double` | name / pc | Associated molecular cloud complex name and distance. |
| `CLASS_1` | `char` | — | Primary source class (`YSO`, `AGB`, `Carbon Star`, `Main Sequence`). |
| `STYPE_ML_PROB1` | `double` | $0.0 - 1.0$| Machine learning classification probability score. |
| `W1VARAMP`, `W2VARAMP` | `double`| mag | NEOWISE multi-year mid-IR light curve variability amplitude. |
| `numGaiaNB` | `int` | counts | Number of Gaia neighbor sources within $7.6''$ radius. |
| `fluxratioGaia` | `double` | % | Ratio of total neighbor flux to target flux in Gaia $R$ band. |

---

## 💻 Programmatic Query Example (Python `astroquery.ipac.irsa`)
```python
from astroquery.ipac.irsa import Irsa
from astropy.coordinates import SkyCoord
import astropy.units as u

# Cone search around Orion Molecular Cloud ice target
coord = SkyCoord(ra=83.822*u.deg, dec=-5.391*u.deg, frame='icrs')

# Query the SPLICES catalog via IRSA Gator
table = Irsa.query_region(
    coord,
    catalog="spherex_splices",
    spatial="Cone",
    radius=1.0 * u.arcmin
)

print(f"Discovered {len(table)} SPLICES ice candidate targets:")
for row in table:
    print(f"Target: {row['designation']} | Class: {row['CLASS_1']} | Av: {row['Av']:.1f} mag | Dist: {row['Dist']:.0f} pc")
```

---

## 🔗 Cross-Links in Obsidian Vault
- [[01 - IRSA SPHEREx Mission Hub]] — Mission detector parameters and ice sensitivity bands (Detectors 5 & 6).
- [[03 - SPHEREx Science Data Products & Calibration]] — 102-channel wavelength grid and spectral WCS mapping.
- [[04 - SPHEREx Data Access Protocols & TAP]] — Querying TAP schemas and downloading FITS cutouts.
- [[Cross-Survey Catalogs (WISE, Gaia, 2MASS)]] — Infrared baseline catalogs and Astropy cross-matching.
