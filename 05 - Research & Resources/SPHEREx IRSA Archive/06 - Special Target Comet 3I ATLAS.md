---
title: "NASA IRSA SPHEREx Special Target: Interstellar Comet 3I/ATLAS"
url: "https://irsa.ipac.caltech.edu/data/SPHEREx/docs/comet3iatlas/index.html"
tags:
  - nasa
  - spherex
  - irsa
  - interstellar-object
  - comet-3i-atlas
  - obscore
  - votable
  - ices
  - coma
aliases:
  - Comet 3I/ATLAS
  - 3I/ATLAS Observations
  - Interstellar Object 3I
created: 2026-11-14
status: active
---

# ☄️ NASA IRSA SPHEREx Observations: Interstellar Comet 3I/ATLAS
> **Primary Source:** [https://irsa.ipac.caltech.edu/data/SPHEREx/docs/comet3iatlas/index.html](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/comet3iatlas/index.html)  
> **ObsCore Table:** [`obscore_3I_Atlas.vot`](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/comet3iatlas/obscore_3I_Atlas.vot)  
> **Batch Scripts:** [`3IATLASImages-curl.sh`](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/comet3iatlas/3IATLASImages-curl.sh) | [`3IATLASImages-wget.sh`](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/comet3iatlas/3IATLASImages-wget.sh)  
> **MOC:** [[00 - Team Command Center]] | [[01 - IRSA SPHEREx Mission Hub]] | [[03 - SPHEREx Science Data Products & Calibration]] | [[05 - SPLICES Ice Source Catalog]]

---

## 🌌 Observation Campaign & Significance
In **August 2025** and **December 2025**, NASA's SPHEREx mission executed a dedicated Target-of-Opportunity (ToO) observation campaign targeting **3I/ATLAS**, only the third confirmed macroscopic interstellar object traversing our solar system (following 1I/'Oumuamua and 2I/Borisov).

SPHEREx obtained **259 individual calibrated spectral exposures** across its 102 channels ($0.75 - 5.0\ \mu\text{m}$), capturing both pre-perihelion approach and post-perihelion outbound trajectories.

### 🌟 Major Scientific Discoveries
1. **Pristine Water Ice Mantle ($\text{H}_2\text{O}$):**  
   Detection of deep $3.05\ \mu\text{m}$ solid-state absorption signatures indicating an icy outer crust formed in an extrasolar protoplanetary disc.
2. **Extended Carbon Dioxide Coma ($\text{CO}_2$):**  
   Strong resonant emission/absorption at $4.27\ \mu\text{m}$ revealing a prominent outgassing envelope extending dozens of arcseconds beyond the nucleus.
3. **Carbon Monoxide Gas ($\text{CO}$):**  
   Detection of volatile CO sublimation features at $4.67\ \mu\text{m}$ in Detector Array 6 ($R \sim 128$).
4. **Post-Perihelion Surge (December 2025):**  
   Marked increase in activity with the release of refractory silicate dust grains and secondary volatile gas species.

---

## 📑 IVOA ObsCore VOTable Architecture (`obscore_3I_Atlas.vot`)
IRSA distributes an official IVOA-standard ObsCore data model table listing all 259 exposures.

### Key Table Fields:
| Field Name | Datatype | Unit | Description |
| :--- | :--- | :--- | :--- |
| `obs_id` | `char` | — | Observation identifier string. |
| `spherex_detector` | `int` | $1 - 6$ | Active SPHEREx detector array (`D1`–`D6`). |
| `comet_ra`, `comet_dec`| `double` | degrees | Predicted celestial coordinates of 3I/ATLAS nucleus at exposure epoch. |
| `s_ra`, `s_dec` | `double` | degrees | Bore-sight telescope pointing center. |
| `t_min`, `t_max` | `double` | MJD | Start and end observation timestamps. |
| `t_exptime` | `float` | seconds | Total exposure integration time. |
| `em_min`, `em_max` | `double` | meters | Spectral bandpass boundaries covered by the active array. |
| `target_moving` | `boolean` | `true` | Solar System moving target flag. |
| `access_url` | `char` | URI | Direct HTTP download endpoint for the Level 2 MEF FITS file. |

---

## ⚠️ Crucial Photometry Warning: Spatially Extended Sources
> [!CAUTION]
> **Do NOT use the automated SPHEREx Spectrophotometry Tool on 3I/ATLAS!**  
> The SPHEREx Spectrophotometry Tool employs a point-spread function (PSF) fitting algorithm assuming an unresolved point source ($\text{FWHM} \sim 6''$).
> 
> Because 3I/ATLAS exhibits an extended gas coma ($> 30''$) at infrared wavelengths, point-source forced aperture photometry:
> 1. Significantly **underestimates total volatile flux** ($\text{CO}_2$ and $\text{H}_2\text{O}$).
> 2. Artificially tilts the spectral slope.
> 
> *Recommended Technique:* Perform custom polygonal or multi-annulus spatial aperture integration directly on the Level 2 MEF `IMAGE` layers, subtracting the modeled `ZODI` background.

---

## 💻 Automated Batch Download Scripts
IRSA provides ready-to-run shell scripts to pull all 259 calibrated FITS files in parallel:
- **`curl` Downloader:**
  ```bash
  curl -O https://irsa.ipac.caltech.edu/data/SPHEREx/docs/comet3iatlas/3IATLASImages-curl.sh
  chmod +x 3IATLASImages-curl.sh
  ./3IATLASImages-curl.sh
  ```
- **`wget` Downloader:**
  ```bash
  wget https://irsa.ipac.caltech.edu/data/SPHEREx/docs/comet3iatlas/3IATLASImages-wget.sh
  sh 3IATLASImages-wget.sh
  ```

---

## 📖 Related SPHEREx Publications
- **August 2025 Data (Discovery Note):**  
  Lisse et al. (2026), *"SPHEREx Discovery of Strong Water Ice Absorption and an Extended Carbon Dioxide Coma in 3I/ATLAS"*, *RNAAS*, Vol. 9, Iss. 9, id. 242.
- **Pre-Perihelion Mapping:**  
  Lisse et al. (2025), *"SPHEREx Pre-Perihelion Mapping of $\text{H}_2\text{O}$, $\text{CO}_2$, and $\text{CO}$ in Interstellar Object 3I/ATLAS"*, submitted to *ApJL*.
- **December 2025 Data (Post-Perihelion Activity):**  
  Lisse et al. (2026), *"SPHEREx Re-Observation of Interstellar Object 3I/ATLAS in December 2025: Detection of Increased Post-Perihelion Activity, Refractory Coma Dust, and New Coma Gas Species"*, submitted to *RNAAS*.

---

## 🔗 Cross-Links in Obsidian Vault
- [[01 - IRSA SPHEREx Mission Hub]] — Moving Object Search Tool (MOST) and telescope specs.
- [[03 - SPHEREx Science Data Products & Calibration]] — Multi-Extension FITS (MEF) layer parsing.
- [[04 - SPHEREx Data Access Protocols & TAP]] — SIAv2 query protocols and Python scripting.
- [[05 - SPLICES Ice Source Catalog]] — Comparison of interstellar comet ices with circumstellar YSO ices.
- [[07 - SPHEREx Spectral Calibrations & Instrument Files]] — Linear Variable Filter transmission curves.
