---
title: "WiseView Synthetic Object Injection Engine (synth_a, synth_b): Blind Recovery & Dipole Nulling"
url: "http://byw.tools/wiseview"
feature: "Synthetic Moving Object Modeling & Subtraction"
tags:
  - citizen-science
  - wiseview
  - synthetic-injection
  - blind-recovery
  - brown-dwarfs
  - planet-9
  - forward-modeling
aliases:
  - WiseView Synthetic Engine
  - WiseView synth_a
  - Dipole Nulling
created: 2026-11-14
status: active
---

# ☄️ WiseView Synthetic Object Injection Engine (`synth_a`, `synth_b`)
> **Source Module:** `flash3.js` & AWS Lambda Backend (`png-animation`)  
> **Interface Controls:** `#synthAInput`, `#synthBInput`  
> **Lead Architect:** Dan Caselden (AMNH / NASA Backyard Worlds: Planet 9)  
> **MOC:** [[00 - Team Command Center]] | [[WISEVIEW_BYW_TOOLS_SITEMAP]] | [[01 - WiseView Core Engine & Blinking Pipeline]] | [[02 - WiseView Cloud Microservices & unWISE Infrastructure]]

---

## 🎯 1. Scientific Purpose & Architecture
WiseView includes a sophisticated dual synthetic source injection subsystem (`synth_a` and `synth_b`). Rather than simply drawing artificial circles on a canvas, the backend AWS Lambda worker **physically injects (or subtracts) simulated point-spread functions (PSFs)** directly into the raw unWISE co-added pixel data before stretch and rendering.

```
User Input Form (RA, Dec, W1, W2, pmra, pmdec, MJD)
 │
 ├── 1. Flux Conversion: W1/W2 magnitudes converted to Vega photo-electron flux
 │
 ├── 2. Astrometric Trajectory Propagation:
 │    └── For each epoch MJD_k:  Δt_k = (MJD_k - MJD_ref) / 365.25 yr
 │         ├── α_k = α_ref + (pmra / cos δ) · Δt_k
 │         └── δ_k = δ_ref + pmdec · Δt_k
 │
 ├── 3. PSF Convolution:
 │    └── Evaluates unWISE effective Point Spread Function at (α_k, δ_k)
 │
 └── 4. Arithmetic Injection or Subtraction:
      ├── Mode 1 (synth = 1, sub = 0): I_final(x, y) = I_raw(x, y) + PSF_model(x, y)
      └── Mode 2 (synth = 1, sub = 1): I_final(x, y) = I_raw(x, y) - PSF_model(x, y)  ◄── Dipole Nulling
```

---

## ⚙️ 2. Synthetic Parameter Dictionary

| Parameter Key | UI Input ID | Type | Astrophysical Meaning |
| :--- | :--- | :---: | :--- |
| `synth_a` | `#synthAInput` | `0/1` | Enable/disable synthetic object model A. |
| `synth_a_sub` | `#synthASubInput` | `0/1` | **Subtraction Mode:** When `1`, subtracts model from image instead of adding it. |
| `synth_a_ra` | `#synthARaInput` | `float` | Reference Right Ascension in decimal degrees (J2000). |
| `synth_a_dec` | `#synthADecInput` | `float` | Reference Declination in decimal degrees (J2000). |
| `synth_a_w1` | `#synthAW1Input` | `float` | Apparent magnitude in WISE W1 ($3.4\ \mu\text{m}$, Vega). |
| `synth_a_w2` | `#synthAW2Input` | `float` | Apparent magnitude in WISE W2 ($4.6\ \mu\text{m}$, Vega). |
| `synth_a_pmra`| `#synthAPmraInput`| `float` | Proper motion along $\mu_\alpha \cos \delta$ ($\text{mas/yr}$). |
| `synth_a_pmdec`| `#synthAPmdecInput`| `float` | Proper motion along $\mu_\delta$ ($\text{mas/yr}$). |
| `synth_a_mjd` | `#synthAMjdInput` | `float` | Reference epoch Modified Julian Date (defaults to Epoch 2015.5 / MJD 57204). |
| `synth_b...` | `#synthB...` | — | Identical parameter set for an independent secondary object (e.g. wide binary companion). |

---

## 🔬 3. The Three Critical Research Applications

### A. Blind Recovery & Completeness Validation
To evaluate human volunteer detection thresholds and benchmark automated search algorithms (such as SPHEREx Hunter's `GET /api/source_discovery`):
1. A researcher injects an ultra-faint synthetic brown dwarf (e.g. $W2 = 16.5\ \text{mag}$, $W1 - W2 = 3.5$, $\mu = 500\ \text{mas/yr}$) into an unWISE field.
2. The field is presented blindly to citizen scientists or computer vision pipelines.
3. Quantifies the survey's **completeness limit** as a function of apparent brightness, Galactic latitude background crowding, and proper motion velocity.

### B. Forward-Modeling Dipole Nulling (Aperture Subtraction)
When a candidate brown dwarf or solar system object is discovered:
- Setting `synth_a_sub = 1` activates **synthetic model subtraction**.
- By tuning `synth_a_w2`, `synth_a_pmra`, and `synth_a_pmdec` until the moving dipole in difference mode (`diff=1`) **completely vanishes**, astronomers measure:
  $$\text{Observed Dipole} - \text{Synthetic Model} = 0 \implies \text{Exact Astrometry & Photometry}$$
- Obtains precise non-linear photometry without requiring traditional aperture correction in crowded stellar fields.

### C. Neighbor De-blending & Binary Companions
Many substellar objects exist in wide binary configurations orbiting brighter primary stars (e.g. Epsilon Indi B & C).
- By parameterizing the bright primary star in `synth_a` with `synth_a_sub = 1`, its blinding diffraction halo and PSF wings are cleanly subtracted.
- Unveils the faint, previously hidden moving substellar companion in `synth_b`.

---

## 💻 4. Python Query Recipe for Synthetic Injection
Researchers can programmatically generate synthetic injection cutouts directly from WiseView's AWS Lambda backend:

```python
import urllib.request
import urllib.parse
import json

# Target field (WISE 0855 background)
endpoint = "https://moo23y1au0.execute-api.us-west-2.amazonaws.com/default/png-animation"
params = {
    "ra": "133.786245",
    "dec": "-7.244372",
    "band": "2",
    "size": "176",
    "minbright": "-50.0000",
    "maxbright": "500.0000",
    "invert": "1",
    "diff": "1",                 # Difference mode to reveal dipole
    # Inject a fast-moving synthetic Planet 9 candidate
    "synth_a": "1",
    "synth_a_sub": "0",
    "synth_a_ra": "133.780000",
    "synth_a_dec": "-7.240000",
    "synth_a_w1": "19.5",
    "synth_a_w2": "15.2",
    "synth_a_pmra": "-1200.0",   # -1.2 arcsec/yr
    "synth_a_pmdec": "450.0",
    "synth_a_mjd": "57204.0",
    "callback": "cb"
}

query_url = f"{endpoint}?{urllib.parse.urlencode(params)}"
req = urllib.request.Request(query_url, headers={"User-Agent": "Mozilla/5.0"})

with urllib.request.urlopen(req, timeout=15) as resp:
    raw = resp.read().decode("utf-8")
    # Parse JSONP
    data = json.loads(raw[3:-1])
    print(f"Generated {len(data['ims'])} synthetic injection frames.")
    for frame_path in data['ims']:
        full_image_url = f"https://amnh-citsci-public.s3-us-west-2.amazonaws.com/{frame_path}"
        print("  -> Frame CDN URL:", full_image_url)
```

---

## 🔗 Cross-Links in Obsidian Vault
- [[01 - WiseView Core Engine & Blinking Pipeline]] — Core canvas rendering and Asinh stretch.
- [[02 - WiseView Cloud Microservices & unWISE Infrastructure]] — AWS Lambda backend processing.
- [[WISEVIEW_BYW_TOOLS_SITEMAP]] — Complete URL hash parameter reference dictionary.
- [[Citizen Science Best Practices (Backyard Worlds)]] — Discovery verification protocols.
