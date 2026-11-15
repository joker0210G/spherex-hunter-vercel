---
title: "WiseView Cloud Microservices: Serverless AWS Lambda, AMNH S3 & Gaia DR3 Infrastructure"
url: "https://moo23y1au0.execute-api.us-west-2.amazonaws.com/default/png-animation"
author: "Dan Caselden (AMNH / NASA Backyard Worlds)"
tags:
  - citizen-science
  - wiseview
  - aws-lambda
  - serverless
  - unwise
  - amnh
  - gaia-dr3
  - api-reference
aliases:
  - WiseView Microservices
  - WiseView Backend Architecture
  - unWISE Image Infrastructure
created: 2026-11-14
status: active
---

# ☁️ WiseView Cloud Microservices: Serverless AWS Lambda & unWISE Infrastructure
> **Service Endpoints:**  
> - **Cutout & Animation Service:** `https://moo23y1au0.execute-api.us-west-2.amazonaws.com/default/png-animation`  
> - **Gaia DR3 Astrometry Proxy:** `https://n7z4i9pzx8.execute-api.us-west-2.amazonaws.com/prod/catalog/gaiadr2`  
> - **Public S3 Image Repository:** `https://amnh-citsci-public.s3-us-west-2.amazonaws.com/`  
> **Lead Architect:** Dan Caselden (American Museum of Natural History)  
> **MOC:** [[00 - Team Command Center]] | [[WISEVIEW_BYW_TOOLS_SITEMAP]] | [[01 - WiseView Core Engine & Blinking Pipeline]] | [[Citizen Science Best Practices (Backyard Worlds)]]

---

## 🏛️ 1. Serverless Microservices Topology
WiseView operates completely serverless on **Amazon Web Services (AWS)** in the `us-west-2` (Oregon) region:

```
Client Web Browser (byw.tools/wiseview)
 │
 ├── 1. Request unWISE Cutouts & Epoch Metadata:
 │    └── GET /default/png-animation?ra=...&dec=...&size=...&band=2&callback=cb
 │         │
 │         └── AWS Lambda (Cutout Worker):
 │              ├── Queries unWISE co-added time-resolved tile database (2010–2024)
 │              ├── Resamples sub-image cutouts to requested FOV size (e.g. 176 arcsec)
 │              ├── Computes Asinh non-linear pixel stretch & optional difference imaging
 │              ├── Renders standard 8-bit PNG frames and uploads to S3
 │              └── Returns JSON metadata with cutout UUIDs & WCS header parameters
 │
 ├── 2. Direct S3 Image Streaming:
 │    └── Parallel GET https://amnh-citsci-public.s3-us-west-2.amazonaws.com/cutouts/{UUID}
 │         └── Direct CDN streaming into browser HTML5 Image buffers (zero server bottleneck)
 │
 └── 3. Asynchronous Gaia DR3 Astrometry Query:
      └── POST /prod/catalog/gaiadr2 (ADQL Cone Search)
           │
           └── AWS Lambda (Gaia Proxy):
                ├── Forwards ADQL to ESA Gaia TAP (https://gea.esac.esa.int/tap-server/tap/sync)
                └── Returns JSON table of [ra, dec, parallax, pmra, pmdec] for vector projection
```

---

## 📡 2. Cutout & Animation Service Specification (`png-animation`)

### 🔗 Endpoint
```http
GET https://moo23y1au0.execute-api.us-west-2.amazonaws.com/default/png-animation
```

### 📥 Input Query Parameters
| Parameter | Type | Required | Example | Description |
| :--- | :---: | :---: | :--- | :--- |
| `ra` | `float` | Yes | `133.786245` | Target Right Ascension in decimal degrees (J2000). |
| `dec` | `float` | Yes | `-7.244372` | Target Declination in decimal degrees (J2000). |
| `band` | `int` | Yes | `2` | `1` (W1 $3.4\ \mu\text{m}$), `2` (W2 $4.6\ \mu\text{m}$), `3` (Color composite). |
| `size` | `int` | Yes | `176` | Field of view size in arcseconds. |
| `minbright` | `float` | Yes | `-50.0000` | Asinh stretch lower threshold (raw DN). |
| `maxbright` | `float` | Yes | `500.0000` | Asinh stretch upper saturation clamp (raw DN). |
| `invert` | `0/1` | Yes | `1` | Color inversion (`1` = dark stars on white sky). |
| `diff` | `0/1` | Yes | `0` | Difference imaging mode toggle ($I_t - I_{t-1}$). |
| `window` | `float` | Yes | `0.5` | Epoch grouping window in years. |
| `diff_window`| `float`| Yes | `1.0` | Baseline time difference between subtracted frames. |
| `stretch` | `float` | Yes | `1.0` | Linearity scaling parameter. |
| `pmx`, `pmy` | `float` | No | `0.0` | Motion compensation drift $(\mu / 1000) / 2.75''$. |
| `callback` | `str` | Yes | `cb` | JSONP callback wrapper function name. |

### 📤 Output JSON Schema (`meta`)
```json
{
  "ims": [
    "cutouts/e845a1da-a61d-4153-a537-a0de3dadfd31",
    "cutouts/7b46d1cc-e9f6-465c-8e39-726ee4f901fd",
    "cutouts/0eca79bc-4d12-4707-a4de-5eddbd4b5e03"
  ],
  "all_mjds": [55204.12, 55389.45, 56780.22, 60120.88],
  "mjds": [
    [55204.12, 55204.15],
    [55389.45, 55389.48]
  ],
  "epochs": [[0, 1], [2, 3]],
  "min": -50.0,
  "max": 500.0,
  "CRPIX1": 32.5,
  "CRPIX2": 32.5,
  "CRVAL1": 133.786245,
  "CRVAL2": -7.244372,
  "NAXIS1": 64,
  "NAXIS2": 64
}
```

---

## 🗄️ 3. AMNH Public AWS S3 Storage Bucket
All rendered time-series PNG cutouts are written to the public Amazon S3 bucket hosted by the American Museum of Natural History:
```
https://amnh-citsci-public.s3-us-west-2.amazonaws.com/
 └── cutouts/
      ├── e845a1da-a61d-4153-a537-a0de3dadfd31  (Valid 8-bit PNG)
      ├── 7b46d1cc-e9f6-465c-8e39-726ee4f901fd  (Valid 8-bit PNG)
      └── ...
```
- **Caching Benefit:** Once a citizen scientist queries a position, the cutouts remain cached in S3. Subsequent queries for identical coordinates and stretch parameters are loaded instantaneously without re-executing unWISE FITS reprojections.

---

## 🌌 4. Gaia DR3 Astrometry Proxy Service (`gaiadr2`)

### 🔗 Endpoint
```http
POST https://n7z4i9pzx8.execute-api.us-west-2.amazonaws.com/prod/catalog/gaiadr2
```

### 📥 Request Payload (ADQL)
```json
{
  "request": "doQuery",
  "lang": "adql",
  "format": "json",
  "query": "SELECT ra, dec, parallax, pmra, pmdec FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT('ICRS',ra,dec), CIRCLE('ICRS',133.786245,-7.244372,0.134444))"
}
```

### 📤 Response Structure
Returns a compact 2D data matrix where each entry represents a verified astrometric star:
```json
{
  "metadata": ["ra", "dec", "parallax", "pmra", "pmdec"],
  "data": [
    [133.7634933, -7.3561686, 0.8468, -10.235, 6.220],
    [133.7009605, -7.3322022, 0.0915, -6.037, -4.910],
    [133.8676887, -7.3502874, -0.9063, -2.160, 0.490]
  ]
}
```

---

## 🔬 5. The unWISE Co-Add Science Foundation
The underlying imagery delivered by WiseView originates from the **unWISE co-add catalog** (Lang 2014, Meisner et al. 2017):
1. **Preserved Angular Resolution:** Unlike the official AllWISE atlas which intentionally smoothed images by convolving with the point-spread function, unWISE maintains the full native $2.75''\text{/pixel}$ resolution.
2. **Time-Resolved Epoch Co-adds:** WISE images from the 2010 cryogenic mission and the 2014–2024 NEOWISE Reactivation are co-added into **distinct half-year seasonal passes**. This 14-year baseline provides unprecedented sensitivity to proper motions down to $\mu \sim 50\ \text{mas/yr}$.

---

## 🔗 Cross-Links in Obsidian Vault
- [[01 - WiseView Core Engine & Blinking Pipeline]] — Complete `flash3.js` mathematical functions and canvas rendering.
- [[WISEVIEW_BYW_TOOLS_SITEMAP]] — Master URL hash parameters dictionary.
- [[Citizen Science Best Practices (Backyard Worlds)]] — Protocols for identifying Planet 9 and brown dwarf dipoles.
- [[Cross-Survey Catalogs (WISE, Gaia, 2MASS)]] — Multi-survey cross-matching.
