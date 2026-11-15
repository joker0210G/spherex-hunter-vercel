---
title: "WiseView Core Engine: Architecture, unWISE Blinking & Astronomical Math (flash3.js)"
url: "http://byw.tools/wiseview"
engine: "static/flash3.js (43,613 bytes)"
author: "Dan Caselden (American Museum of Natural History / NASA Backyard Worlds: Planet 9)"
tags:
  - citizen-science
  - wiseview
  - byw-tools
  - blink-comparator
  - flash3
  - asinh-stretch
  - difference-imaging
  - gaia-dr3
aliases:
  - WiseView Engine
  - flash3.js Architecture
  - WiseView Blinking Pipeline
created: 2026-11-14
status: active
---

# 🔭 WiseView Core Engine: Architecture, unWISE Blinking & Astronomical Math
> **Primary Web App:** [http://byw.tools/wiseview](http://byw.tools/wiseview)  
> **Source Script:** `http://byw.tools/static/flash3.js` (43,613 characters)  
> **Lead Developer:** Dan Caselden (AMNH / Backyard Worlds: Planet 9)  
> **MOC:** [[00 - Team Command Center]] | [[WISEVIEW_BYW_TOOLS_SITEMAP]] | [[Citizen Science Best Practices (Backyard Worlds)]] | [[NASA_AND_PARTNER_DATA_PORTALS]]

---

## 🏛️ 1. Architecture Overview & Data Flow
**WiseView** is a specialized, high-performance web-based blink comparator engineered by Dan Caselden for the **NASA Backyard Worlds: Planet 9** citizen science project. It allows volunteers and professional astronomers to visually inspect up to **14 years of time-resolved infrared sky images** ($2010\text{--}2024$) collected by the Wide-field Infrared Survey Explorer (WISE) and NEOWISE missions.

```
User Browser (byw.tools/wiseview)
 │
 ├── 1. URL Hash State Parser: Deserializes coordinates, zoom, FOV, and stretch parameters
 │
 ├── 2. AWS Lambda Animation Service:
 │    └── POST to https://moo23y1au0.execute-api.us-west-2.amazonaws.com/default/png-animation
 │         ├── Input: RA, Dec, size, band, window, diff, minbright, maxbright, pmx, pmy
 │         └── Output: JSON metadata (all_mjds, epochs, min/max flux, WCS CRVAL/CRPIX)
 │
 ├── 3. AMNH S3 Asset Retrieval:
 │    └── GET https://amnh-citsci-public.s3-us-west-2.amazonaws.com/{meta.ims[e]}
 │         └── Fetches pre-processed, co-added unWISE PNG frames into browser Image cache
 │
 ├── 4. ESA Gaia DR3 Vector Overlay:
 │    └── POST to https://n7z4i9pzx8.execute-api.us-west-2.amazonaws.com/prod/catalog/gaiadr2
 │         ├── Executes ADQL cone search on gaiadr3.gaia_source
 │         └── Propagates astrometry from Base Epoch MJD 57204 (2015.5) to each observation window
 │
 └── 5. HTML5 Canvas Blinking Loop:
      └── High-speed interval flip (speed ms) with Asinh stretch, color inversion, and reticle
```

---

## 🧮 2. Core Mathematical Functions in `flash3.js`

### A. Symmetrical Logarithmic Scaling (`symlog10` & `symexp10`)
Because astronomical infrared images contain both faint diffuse backgrounds (which can become slightly negative after background subtraction) and extremely bright stellar cores, WiseView employs signed symmetrical logarithmic transforms:

```javascript
function symlog10 (x) {
    if (x == 0) return 0;
    else if (x < 0) return -Math.log10(-x);
    else return Math.log10(x);
}

function symexp10 (x) {
    if (x == 0) return 0;
    else if (x < 0) return -(10**(-x));
    else return 10**x;
}
```
- Converts raw sliders and pixel bounds (`minbright`, `maxbright`) into symmetrical log space, allowing seamless linear transitions across zero without numerical exceptions.

### B. Modified Julian Date to Fractional Year Conversion (`mjd_to_aarondate`)
Converts satellite epoch Modified Julian Dates into human-readable astronomical fractional years:
```javascript
function mjd_to_aarondate(mjd) {
    // Reference offset: MJD 0 in Unix milliseconds = -3506716800000
    var d = new Date(-3506716800000 + (mjd * 86400000));
    return d.getFullYear() + "." + (((d.getMonth() / 12.0) * 10).toPrecision(1));
}
```
*Example:* $\text{MJD}\ 55200 \to 2010.0$ (Cryogenic WISE survey kickoff); $\text{MJD}\ 60300 \to 2023.9$ (Late NEOWISE pass).

### C. Proper Motion Drift Transformation
To compensate for stellar motion or test hypothetical orbital drifts, WiseView accepts `pmra` and `pmdec` in milli-arcseconds per year ($\text{mas/yr}$). Because unWISE has a native pixel scale of **$2.75''\text{/pixel}$**, the shift per year in pixel coordinates is derived as:
$$\Delta x_{\text{pixel/yr}} = \frac{\mu_\alpha \cos \delta}{1000 \times 2.75}$$
$$\Delta y_{\text{pixel/yr}} = \frac{\mu_\delta}{1000 \times 2.75}$$

---

## 🌓 3. Difference Imaging & Dipole Physics (`diff=1`)
When the difference toggle is activated (`diff=1`), WiseView transforms the blinking sequence from static images into temporal derivative frames:
$$I_{\text{diff}}(t) = I(t) - I(t - \Delta t_{\text{window}})$$

### 🔭 The Optical Dipole Signature
- **Static Stars:** Subtract cleanly to a neutral mid-gray baseline ($I_{\text{diff}} \approx 0$).
- **High Proper Motion Objects (Brown Dwarfs / Planet 9):**
  - Leaves an unmistakable **optical dipole**: a dark negative depression at the prior epoch location, and a bright positive peak at the subsequent epoch location:
  $$\text{Dipole} \implies \ominus \longrightarrow \oplus$$
  - Traces the exact proper motion vector across the baseline.

---

## 🛰️ 4. Gaia DR3 Astrometric Overlay Architecture
WiseView queries Gaia DR3 using an asynchronous ADQL spatial cone search:
```sql
SELECT ra, dec, parallax, pmra, pmdec 
FROM gaiadr3.gaia_source 
WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', [RA], [DEC], [FOV_DEG]))
```
- **Base Epoch:** $\text{MJD}_{\text{base}} = 57204$ (corresponding to **Epoch 2015.5**).
- For each frame $k$ with central timestamp $\text{MJD}_k$, the stellar centroid is dynamically projected forward or backward in time:
  $$\Delta t_k = \frac{\text{MJD}_k - 57204}{365.25}\text{ years}$$
  $$\alpha_k = \alpha_{\text{Gaia}} + \frac{\mu_\alpha \cos \delta}{\cos \delta_{\text{Gaia}}} \cdot \Delta t_k$$
  $$\delta_k = \delta_{\text{Gaia}} + \mu_\delta \cdot \Delta t_k$$
- Draws a glowing cyan reticle on top of every confirmed star.
- **Scientific Impact:** If an infrared moving source **lacks a Gaia overlay**, it immediately confirms an **optical dropout** (a candidate ultra-cold Y/T-type brown dwarf or solar system object)!

---

## 🔗 Cross-Links in Obsidian Vault
- [[WISEVIEW_BYW_TOOLS_SITEMAP]] — Master site map and 30+ parameter URL specification.
- [[Citizen Science Best Practices (Backyard Worlds)]] — Discovery methodology and candidate vetting rules.
- [[NASA_AND_PARTNER_DATA_PORTALS]] — Cross-survey integration protocols.
- [[01 - IRSA SPHEREx Mission Hub]] — SPHEREx Band 4 & 6 comparison with unWISE W1 & W2.
- [[10 - Explanatory Supplement Ch 2 Data Products & Anomalies]] — SPHEREx difference imaging and optical dipoles.
