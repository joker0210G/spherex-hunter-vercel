---
title: "WiseView Version History & v2 vs v3 Architecture"
document_id: "WV-ARCH-04"
system: "BYW Tools (byw.tools/wiseview)"
author: "Dan Caselden (AMNH / Backyard Worlds: Planet 9)"
tags:
  - wiseview
  - byw-tools
  - architecture
  - version-history
  - backward-compatibility
  - url-serialization
  - citizen-science
aliases:
  - WiseView v2 vs v3
  - WiseView Version History
  - WiseView Backward Compatibility
created: 2026-11-14
status: active
---

# 🕰️ WiseView Version History & v2 vs v3 Architecture
> **Canonical Production:** [http://byw.tools/wiseview](http://byw.tools/wiseview)  
> **Direct v3 Endpoint:** [http://byw.tools/wiseview-v3](http://byw.tools/wiseview-v3)  
> **Legacy v2 Endpoint:** [http://byw.tools/wiseview-v2](http://byw.tools/wiseview-v2)  
> **MOC:** [[WISEVIEW_BYW_TOOLS_SITEMAP]] | [[01 - WiseView Core Engine & Blinking Pipeline]] | [[02 - WiseView Cloud Microservices & unWISE Infrastructure]] | [[03 - WiseView Synthetic Object Injection Engine]]

---

## 📌 Executive Summary
Between 2017 and 2024, Dan Caselden evolved the **WiseView** platform through three major architectural generations to support the discovery of cold brown dwarfs, Y-dwarfs, and trans-Neptunian objects in the NASA **Backyard Worlds: Planet 9** citizen science project:

1. **WiseView v1 (2017):** Pre-computed static co-add modes (`coadd_mode`) with rigid server-side GIF rendering and fixed frame sets.
2. **WiseView v2 (2018–2020):** Client-side HTML5 canvas playback, preliminary difference imaging, and dynamic contrast controls.
3. **WiseView v3 / `flash3.js` (2020–Present):** Fully parametric time-resolved co-addition, orthogonal parameter space (`window`, `scandir`, `diff`, `shift`), live synthetic object injection (`#synthAInput`), ESA Gaia DR3 astrometric overlay, and automatic URL translation (`v1UrlCompat`).

```
                    WiseView Evolutionary Timeline
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│     WiseView v1         │     │     WiseView v2         │     │  WiseView v3 (flash3)   │
│       (2017)            │ ──► │     (2018-2020)         │ ──► │     (2020-Present)      │
├─────────────────────────┤     ├─────────────────────────┤     ├─────────────────────────┤
│ • Discrete 'coadd_mode' │     │ • HTML5 Canvas display  │     │ • Orthogonal parameters │
│ • Static GIF rendering  │     │ • Client-side blinking  │     │ • Full diff dipole mode │
│ • Fixed epochs (Cryo)   │     │ • Basic difference view │     │ • Dual synthetic inject │
│ • No astrometry overlay │     │ • Gaia DR1 integration  │     │ • Gaia DR2/DR3 vectors  │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

---

## 🔄 1. Parameter Paradigm Shift: Discrete Modes vs Orthogonal Space

### WiseView v1: The Discrete `coadd_mode` Paradigm
In WiseView v1, users selected from a dropdown of pre-defined observation strategies stored as a single string parameter `coadd_mode`:

| v1 `coadd_mode` String | Scientific Purpose | Limitation |
| :--- | :--- | :--- |
| `time-resolved` | Show raw 6-month observation epochs. | High noise for faint objects; dominated by parallax. |
| `parallax-cancelling` | Average opposing scan directions to null orbital parallax. | Locked to 1-year fixed temporal windows. |
| `full-depth` | Co-add all 14+ years of data into a single master image. | Erases fast-moving objects completely. |
| `pre-post` | Subtract earliest cryogenic epochs (2010) from late NEOWISE epochs. | Coarse 2-frame blink only; misses intermediate motion. |
| `parallax-enhancing` | Group epochs by solar elongation to maximize parallax ellipse. | Inflexible windowing; cannot fine-tune baseline. |
| `window-X-year` | Rolling window average over $X$ years. | Rigid hard-coded intervals. |
| `shift-and-add` | Shift frames at fixed velocity vectors to detect fast movers. | Single fixed velocity without live preview. |

### WiseView v3: The Orthogonal Parametric Space
WiseView v3 dismantled `coadd_mode` into independent, orthogonal degrees of freedom:
- `window` ($t \in [0.0, 100.0]\text{ yr}$): Continuous temporal co-addition sliding window.
- `scandir` ($\{0, 1\}$): Independent scan direction separation filter.
- `diff` & `diff_window` ($\{0, 1\}, \Delta t\text{ yr}$): Pairwise difference imaging with flexible baseline.
- `outer_epochs` ($\{0, 1\}$): Boundary epoch isolation.
- `shift`, `pmra`, `pmdec`: Real-time coordinate frame velocity drift compensation.

---

## 💻 2. The Backward Compatibility Engine: `v1UrlCompat`

Because tens of thousands of citizen science discussion threads on **Zooniverse Talk** contain legacy WiseView v1 URLs, `flash3.js` contains a dedicated compatibility engine (`this.v1UrlCompat`) that translates legacy URLs into v3 parameter maps in memory on page load.

### Source Code Implementation (`flash3.js:541-579`):

```javascript
this.v1UrlCompat = function(map) {
    // Detect if the URL looks like a wiseview-v1 URL
    if (!("coadd_mode" in map)) {
        return map;
    }

    // Convert wiseview-v1 URL to wiseview-v3
    if (map.coadd_mode == "time-resolved") {
        map.window = 0;
    } else if (map.coadd_mode.startsWith("parallax-cancelling")) {
        map.window = 0;
        map.scandir = 1;
    } else if (map.coadd_mode == "full-depth") {
        map.window = 1.5;
    } else if (map.coadd_mode == "pre-post") {
        map.window = 1.5;
        map.outer_epochs = 1;
    } else if (map.coadd_mode == "parallax-enhancing") {
        map.window = 100;
        map.scandir = 1;
    } else if (map.coadd_mode.startsWith("window-")
               && map.coadd_mode.endsWith("-year")) {
        var m = map.coadd_mode.match(/window-([0-9\.]+)-year/);
        if (m !== null && m.length >= 2) {
            map.window = Number(m[1]);
        }
    } else if (map.coadd_mode.startsWith("window-")
               && map.coadd_mode.endsWith("-year-parallax-enhancing")) {
        var m = map.coadd_mode.match(/window-([0-9\.]+)-year/);
        if (m !== null && m.length >= 2) {
            map.window = Number(m[1]);
            map.scandir = 1;
        }
    } else if (map.coadd_mode == "shift-and-add") {
        map.window = 100;
        map.shift = 1;
    }
};
```

### Complete Translation Lookup Table:

| Legacy v1 / v2 Parameter | Modern v3 Parameter State | Physical Pipeline Action |
| :--- | :--- | :--- |
| `coadd_mode=time-resolved` | `window=0` | Individual 6-month unWISE passes without binning. |
| `coadd_mode=parallax-cancelling` | `window=0&scandir=1` | Segregates forward/reverse passes to eliminate parallax wobbles. |
| `coadd_mode=full-depth` | `window=1.5` | Standard 1.5-year temporal binning for static deep imaging. |
| `coadd_mode=pre-post` | `window=1.5&outer_epochs=1` | Isolates 2010 cryogenic vs 2024 NEOWISE reactivation. |
| `coadd_mode=parallax-enhancing` | `window=100&scandir=1` | Maximize parallax baseline across full 14-year dataset. |
| `coadd_mode=window-0.5-year` | `window=0.5` | 6-month rolling average. |
| `coadd_mode=window-1.0-year-parallax-enhancing` | `window=1.0&scandir=1` | 1-year scan-segregated parallax enhancement. |
| `coadd_mode=shift-and-add` | `window=100&shift=1` | Stacks all frames aligned to candidate proper motion vector. |

---

## 🔍 3. Viewport Navigation & Child Viewport Spawning

In WiseView v3, users can click anywhere inside the blinking canvas or drag to pan and zoom. Rather than reloading the current window, `flash3.js` dynamically generates updated deep links and spawns child viewports:

```javascript
// From flash3.js lines 885-900:
this.open_fov = function (fov) {
    var pos = this.__new_pos();
    var current_zoom = this.zoom_input.val();
    var current_fov = this.size_input.val();

    fov = Number(fov).toFixed(0);
    if (fov < 6) { fov = 6; }

    if (this.diff_input.prop("checked")) {
        // Drop out of diff mode when zooming into detail
        window.open("/wiseview-v3#" + this.buildUrl(pos.ra, pos.dec, fov, (current_fov * current_zoom) / fov, diff=0));
    } else {
        window.open("/wiseview-v3#" + this.buildUrl(pos.ra, pos.dec, fov, (current_fov * current_zoom) / fov));
    }
};
```

### Key Behavioral Rules:
1. **Minimum FOV Clamping:** The field of view cannot drop below $6''$ (`fov < 6 -> fov = 6`), which corresponds to roughly 2 unWISE pixels ($2.75''/\text{px}$).
2. **Automatic Difference Exit on Drill-down:** When an investigator clicks an anomalous dipole in difference mode, WiseView automatically spawns a child viewport in normal mode (`diff=0`), allowing instant visual inspection of the underlying point source without manual toggling.
3. **Preserved Angular Resolution:** The canvas zoom level is automatically recomputed via:
   $$\text{Zoom}_{\text{new}} = \frac{\text{FOV}_{\text{old}} \times \text{Zoom}_{\text{old}}}{\text{FOV}_{\text{new}}}$$
   ensuring smooth visual continuity across viewport transitions.

---

## 🎯 4. Comparative Architecture Matrix: v1 vs v2 vs v3

| Architectural Feature | WiseView v1 (2017) | WiseView v2 (2019) | WiseView v3 (2024 / Present) | SPHEREx Hunter Implementation |
| :--- | :--- | :--- | :--- | :--- |
| **Blink Engine** | Animated GIF (Server) | HTML5 `<canvas>` | Optimized 2D Canvas + Double Buffering | Three.js WebGL + 2D Fallback |
| **Backend Service** | Static Python CGI | AWS Lambda (early) | Serverless `png-animation` Lambda | FastAPI Async + IRSA SIAv2 TAP |
| **Temporal Co-add** | Pre-computed modes | Semi-dynamic | Continuous floating `window` (0.0–100 yr) | 102 SPHEREx Spectral Channels |
| **Difference Mode** | None | Raw frame subtraction | Full dipole flux subtraction ($I_t - I_{t-1}$) | Dual-mode: Temporal + Spectral Diff |
| **Synthetic Injection**| None | None | Dual `#synthA` & `#synthB` models | Forward-modeled PSF injection |
| **Astrometry Overlay** | None | Gaia DR1 static points | Gaia DR3 vectors propagated to epoch | Gaia DR3 + 2MASS + CatWISE2020 |
| **State Storage** | URL query `?param=val`| URL hash `#param=val` | 30+ parameter URL hash fragment | URL Hash + LocalStorage + Session |

---

## 🚀 5. Architectural Lessons for Team RIP (SPHEREx Hunter)

1. **Adopt Orthogonal State Representation:**  
   Never bundle viewing filters into monolithic strings (e.g. `mode="band6-diff"`). Instead, maintain independent states:
   - `spectral_channel`: $0 \dots 101$
   - `epoch`: Survey 1 to 4 ($2025.2 \dots 2027.2$)
   - `diff_mode`: `none`, `temporal_diff`, `spectral_diff`
   - `stretch`: `linear`, `asinh`, `symlog`
2. **Maintain Strict URL Backward Compatibility:**  
   By building a `v1UrlCompat`-style translation layer into `frontend/index.html`, any link shared by a citizen scientist on Discord, Slack, or Zooniverse will continue to load correctly even as we push new frontend builds.
3. **Smart Mode Transitions:**  
   Like WiseView's automatic exit from difference mode on zoom (`diff=0`), SPHEREx Hunter should automatically toggle between All-Sky Healpix View, Detector Cutouts, and Spectral SED Mode based on FOV thresholds ($>5^\circ \to$ Healpix; $5^\circ\text{--}30' \to$ Detector FITS; $<30' \to$ Blink Comparator).

---

## 🔗 Related Notes in Obsidian Vault
- [[WISEVIEW_BYW_TOOLS_SITEMAP]] — Master directory of endpoints and hash parameters.
- [[01 - WiseView Core Engine & Blinking Pipeline]] — Mathematical foundations of `flash3.js`.
- [[02 - WiseView Cloud Microservices & unWISE Infrastructure]] — Cloud Lambda architecture and unWISE S3 CDN.
- [[03 - WiseView Synthetic Object Injection Engine]] — Forward-modeling dipole cancellation.
- [[05 - Cross-Survey External Verification Endpoints]] — Connected survey verification portals.
