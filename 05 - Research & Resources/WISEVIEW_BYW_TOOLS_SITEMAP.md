---
title: "Dan Caselden's WiseView Architecture & Site Map (Backyard Worlds: Planet 9)"
url: "http://byw.tools/wiseview"
domain: "byw.tools"
creator: "Dan Caselden (AMNH / NASA Backyard Worlds: Planet 9)"
target_coordinates: "133.786245 -7.244372 (WISE 0855-0714)"
tags:
  - citizen-science
  - wiseview
  - byw-tools
  - unwise
  - backyard-worlds
  - blink-comparator
  - sitemap
  - brown-dwarfs
aliases:
  - WiseView Sitemap
  - BYW Tools Architecture
  - WiseView Deep Link Specification
created: 2026-11-14
status: active
---

# 🔭 WiseView (BYW.tools): Site Map, Architecture & URL Hash Parameter Specification
> **Root Web App:** [http://byw.tools/wiseview](http://byw.tools/wiseview)  
> **Target Observation:** [WISE 0855-0714 Link](http://byw.tools/wiseview#ra=133.786245&dec=-7.244372&size=176&band=2&speed=500&minbright=-50.0000&maxbright=500.0000&window=0.5&diff_window=1&linear=1&color=&zoom=9&border=0&gaia=0&invert=1&maxdyr=0&scandir=0&neowise=0&diff=0&outer_epochs=0&unique_window=1&smooth_scan=0&shift=0&pmra=0&pmdec=0)  
> **Author:** Dan Caselden (American Museum of Natural History / NASA Backyard Worlds: Planet 9)  
> **Core Engine:** `static/flash3.js` (43.6 KB)  
> **MOC:** [[00 - Team Command Center]] | [[Citizen Science Best Practices (Backyard Worlds)]] | [[NASA_AND_PARTNER_DATA_PORTALS]] | [[Cross-Survey Catalogs (WISE, Gaia, 2MASS)]]

---

## 🗺️ 1. Complete Domain & Site Structure (`byw.tools`)

```
http://byw.tools/
 ├── /wiseview               ◄── Production Single-Page Web Application (Active v3)
 ├── /wiseview-v3            ◄── Direct Version 3 Build Endpoint
 ├── /wiseview-v2            ◄── Legacy Version 2 Fallback Viewer
 ├── /static/
 │    ├── flash3.js          ◄── Core Astrometric & Blinking Engine (43,613 bytes)
 │    └── flash3-theme.css   ◄── Custom Astronomy Viewport Dark Styling
 └── External Cloud Microservices & Data Repositories
      ├── AMNH S3 Bucket     ◄── https://amnh-citsci-public.s3-us-west-2.amazonaws.com/ (unWISE Coadds)
      ├── Animation Lambda   ◄── https://moo23y1au0.execute-api.us-west-2.amazonaws.com/default/png-animation
      ├── Gaia DR2 Lambda    ◄── https://n7z4i9pzx8.execute-api.us-west-2.amazonaws.com/prod/catalog/gaiadr2
      ├── ESA Gaia TAP       ◄── https://gea.esac.esa.int/tap-server/tap/sync
      └── Survey Cross-Checks:
           ├── Legacy Survey Viewer (http://legacysurvey.org/viewer?ra=...&dec=...)
           ├── CDS Simbad Inversion (http://simbad.u-strasbg.fr/simbad/sim-coo?Coord=...)
           ├── CDS VizieR Catalog (http://vizier.u-strasbg.fr/viz-bin/VizieR?-c=...)
           ├── Pan-STARRS1 Cutouts (https://ps1images.stsci.edu/cgi-bin/ps1cutouts?pos=...)
           └── Zooniverse Talk (https://www.zooniverse.org/projects/marckuchner/backyard-worlds-planet-9/talk/subjects/)
```

---

## ⚙️ 2. Complete URL Hash Parameter Specification
WiseView stores its complete application state inside the URL hash fragment (`#key=value&...`), enabling instant bookmarking, candidate sharing, and deep-linking from SPHEREx Hunter.

| Parameter | Type | Default | Example Value | Description & Functionality |
| :--- | :---: | :---: | :---: | :--- |
| `ra` | `float` | `133.786` | `133.786245` | Right Ascension in decimal degrees (J2000 ICRS). |
| `dec` | `float` | `-7.244` | `-7.244372` | Declination in decimal degrees (J2000 ICRS). |
| `size` | `int` | `176` | `176` | Field of View (FOV) cutout size in arcseconds ($30''\text{--}2000''$). |
| `band` | `int` | `2` | `2` | Photometric bandpass:<br>• `1`: WISE W1 ($3.4\ \mu\text{m}$)<br>• `2`: WISE W2 ($4.6\ \mu\text{m}$, optimal for cold brown dwarfs)<br>• `3`: W1 + W2 color composite |
| `speed` | `int` | `500` | `500` | Blink cycle speed in milliseconds per frame ($500\text{ ms} = 2.0\text{ FPS}$). |
| `minbright` | `float` | `-50.0` | `-50.0000` | Asinh transfer function floor (raw pixel counts). |
| `maxbright` | `float` | `500.0` | `500.0000` | Asinh transfer function ceiling (raw pixel counts). |
| `window` | `float` | `0.5` | `0.5` | Temporal epoch co-addition window in years ($0.5\text{ yr}$ = 6-month seasonal passes). |
| `diff_window`| `float`| `1.0` | `1` | Baseline duration in years between difference frames. |
| `linear` | `float` | `1.0` | `1` | Stretch linearity factor ($1.0$ = standard non-linear Asinh stretch). |
| `color` | `str` | `""` | `""` (grayscale)| Display color mapping (grayscale, heat, viridis). |
| `zoom` | `int` | `9` | `9` | Display viewport canvas pixel scaling multiplier. |
| `border` | `0/1` | `0` | `0` | Show/hide epoch boundary border grid overlay. |
| `gaia` | `0/1` | `0` | `0` | Overlay Gaia DR2/DR3 astrometric sources and proper motion vectors. |
| `invert` | `0/1` | `1` | `1` | Color inversion: `1` = dark stars on white sky (ideal for spotting dipoles); `0` = standard black sky. |
| `maxdyr` | `0/1` | `0` | `0` | Maximum date range filter across the 14-year baseline. |
| `scandir` | `0/1` | `0` | `0` | Segregate observations by spacecraft scan direction. |
| `neowise` | `0/1` | `0` | `0` | Restrict to NEOWISE Reactivation only (2014–2024), excluding 2010 cryogenic WISE. |
| `diff` | `0/1` | `0` | `0` | **Difference Imaging Mode:** `1` toggles pairwise epoch subtraction ($I_{t} - I_{t-1}$) revealing moving dipoles. |
| `outer_epochs`| `0/1`| `0` | `0` | Include boundary sky coverage epochs with lower SNR. |
| `unique_window`| `0/1`| `1` | `1` | Force unique observation windows without temporal overlap. |
| `smooth_scan`| `0/1` | `0` | `0` | Smooth transitions between scan directions. |
| `shift` | `0/1` | `0` | `0` | Enable manual pixel shift alignment. |
| `pmra` | `float` | `0` | `0` | Proper motion drift compensation along $\mu_\alpha \cos \delta$ ($\text{mas/yr}$). |
| `pmdec` | `float` | `0` | `0` | Proper motion drift compensation along $\mu_\delta$ ($\text{mas/yr}$). |
| `synth_a` | `0/1` | `0` | `0` | Toggle synthetic planet / brown dwarf injection model A. |
| `synth_a_sub`| `0/1`| `0` | `0` | Subtract synthetic object model from the live frame. |
| `synth_a_ra` | `float` | `""` | `""` | Celestial RA of synthetic source. |
| `synth_a_dec`| `float` | `""` | `""` | Celestial Dec of synthetic source. |
| `synth_a_w1` | `float` | `""` | `""` | W1 apparent magnitude of synthetic source. |
| `synth_a_w2` | `float` | `""` | `""` | W2 apparent magnitude of synthetic source. |
| `synth_a_pmra`| `float`| `0` | `0` | Proper motion $\mu_\alpha \cos \delta$ ($\text{mas/yr}$) for synthetic source. |
| `synth_a_pmdec`| `float`| `0` | `0` | Proper motion $\mu_\delta$ ($\text{mas/yr}$) for synthetic source. |
| `synth_a_mjd`| `float` | `""` | `""` | Reference Modified Julian Date (MJD) for synthetic source. |
| `synth_b...` | — | — | — | Parameters for independent synthetic source model B. |

---

## 🎯 3. Target Case Study: WISE 0855-0714
The coordinates in the query link ($\alpha = 133.786245^\circ$, $\delta = -7.244372^\circ$) target **WISE J085510.83-071442.5**, the fourth closest star system to the Sun ($d \approx 2.23\text{ pc} / 7.27\text{ ly}$) and the coldest known sub-stellar brown dwarf ($T_{\text{eff}} \approx 250\text{ K}$).

### Why the Settings in the Link are Optimized for WISE 0855:
1. **`band=2` (W2 $4.6\ \mu\text{m}$):** WISE 0855 is completely invisible in optical and barely detectable in W1 ($3.4\ \mu\text{m}$), but emits strongly in W2 due to deep atmospheric methane ($\text{CH}_4$) and water vapor ($\text{H}_2\text{O}$) absorption windows in W1.
2. **`size=176` ($176'' \approx 2.93'$):** Provides sufficient angular scale to trace WISE 0855's enormous proper motion ($\mu \approx 8.12''\text{/year}$ northward/westward) over the 14-year unWISE baseline.
3. **`speed=500` & `invert=1`:** Renders 2 frames per second with dark stars on a white background, maximizing human visual perception for moving point sources.

---

## 🔗 4. Dynamic Integration in SPHEREx Hunter
In SPHEREx Hunter (`frontend/index.html` and `backend/services/verification_service.py`), we have already wired 1-click dynamic deep-linking to Dan Caselden's WiseView:

```javascript
// Function in frontend/index.html syncing active coordinates to WiseView
function updateWiseViewLink() {
  const ra = parseFloat(document.getElementById('inputRA').value);
  const dec = parseFloat(document.getElementById('inputDec').value);
  const size = Math.min(Math.max(Math.round(currentFOV_arcsec), 30), 300);
  
  // Normal Blink Link
  const wiseviewUrl = `http://byw.tools/wiseview#ra=${ra.toFixed(6)}&dec=${dec.toFixed(6)}&size=${size}&band=2&speed=500&diff=0&invert=1`;
  
  // Difference Mode Link (reveals dipoles)
  const wiseviewDiffUrl = `http://byw.tools/wiseview#ra=${ra.toFixed(6)}&dec=${dec.toFixed(6)}&size=${size}&band=2&speed=500&diff=1&invert=1`;
  
  document.getElementById('linkWiseView').href = wiseviewUrl;
  document.getElementById('linkWiseViewDiff').href = wiseviewDiffUrl;
}
```

---

## 🔗 Technical Knowledge Base: WiseView Deep Dives
* **[[01 - WiseView Core Engine & Blinking Pipeline]]** — Deep dive into `static/flash3.js`, `symlog10`/`symexp10` math, `mjd_to_aarondate`, difference imaging dipole physics ($I_t - I_{t-1}$), and Gaia DR3 MJD 57204 proper-motion projection.
* **[[02 - WiseView Cloud Microservices & unWISE Infrastructure]]** — Serverless AWS Lambda architecture (`png-animation`, `gaiadr2`), AMNH S3 unWISE cutout bucket, JSON metadata return schema, and Lang (2014) / Meisner et al. (2017) time-resolved co-adds.
* **[[03 - WiseView Synthetic Object Injection Engine]]** — Dual forward-modeled synthetic source injection (`#synthAInput` / `#synthBInput`), dipole cancellation / nulling (`synth_a_sub=1`), and blind recovery testing.
* **[[04 - WiseView Version History & v2 vs v3 Architecture]]** — Architectural evolution from discrete v1 `coadd_mode` strings to v3 orthogonal parameter spaces, `v1UrlCompat` backward compatibility engine, and child viewport spawning.
* **[[05 - Cross-Survey External Verification Endpoints]]** — Connected external verification portals (DESI Legacy Survey, CDS Simbad, CDS VizieR, STScI Pan-STARRS1) and live `byw.tools` microservices (`/xref`, `/pawnstars`).

---

## 🔗 Cross-Links in Obsidian Vault
- [[Citizen Science Best Practices (Backyard Worlds)]] — Methodology for vetting Planet 9 and brown dwarf candidates.
- [[NASA_AND_PARTNER_DATA_PORTALS]] — Cross-survey integration with IRSA, MAST, and CADC.
- [[Cross-Survey Catalogs (WISE, Gaia, 2MASS)]] — Multi-epoch baseline calculations ($1999 \to 2010 \to 2026$).
- [[01 - IRSA SPHEREx Mission Hub]] — SPHEREx Band 6 ($4.42 - 5.00\ \mu\text{m}$) cross-match with WISE W2.
