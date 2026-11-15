---
title: "Cross-Survey External Verification Endpoints & Microservices"
document_id: "WV-ARCH-05"
system: "BYW Tools (byw.tools/wiseview)"
author: "Dan Caselden (AMNH / Backyard Worlds: Planet 9)"
tags:
  - wiseview
  - byw-tools
  - panstarrs
  - simbad
  - vizier
  - legacysurvey
  - zooniverse
  - verification
  - citizen-science
aliases:
  - WiseView External Verification
  - PanSTARRS Cutouts Proxy
  - Zooniverse XREF Service
created: 2026-11-14
status: active
---

# 🌐 Cross-Survey External Verification Endpoints & Microservices
> **Primary Application:** [http://byw.tools/wiseview](http://byw.tools/wiseview)  
> **Source Engine:** `static/flash3.js` (`lines 410-463`)  
> **Live Microservices:** `byw.tools/xref` | `byw.tools/pawnstars`  
> **MOC:** [[WISEVIEW_BYW_TOOLS_SITEMAP]] | [[01 - WiseView Core Engine & Blinking Pipeline]] | [[02 - WiseView Cloud Microservices & unWISE Infrastructure]] | [[04 - WiseView Version History & v2 vs v3 Architecture]]

---

## 📌 Executive Summary
When a citizen scientist or astronomer spots a candidate moving dipole or high proper motion object in **WiseView**, immediate multi-wavelength verification is mandatory to rule out:
1. **Optical False Positives:** Diffraction spikes, bright star halos, and scattered light artifacts from optical surveys.
2. **Fast Moving Asteroids:** Solar System minor planets that appear in one or two epochs and vanish.
3. **Known Variables / Active Galactic Nuclei (AGN):** Flare stars or quasars mimicking dipoles due to photometric variability.
4. **Already Discovered Brown Dwarfs:** Objects previously cataloged in Simbad or VizieR.

To streamline this workflow, Dan Caselden integrated **5 external verification portals** directly into the WiseView interface, powered by two custom server-side microservices: `/xref` and `/pawnstars`.

```
                                  Target Coordinate (RA, Dec)
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
         Server-Side Microservices                         Direct Deep-Link Portals
       ┌───────────────────────────┐                     ┌───────────────────────────┐
       │ 1. byw.tools/xref         │                     │ 3. DESI Legacy Survey     │
       │    (Zooniverse Subjects)  │                     │    (unWISE neo11 overlay) │
       ├───────────────────────────┤                     ├───────────────────────────┤
       │ 2. byw.tools/pawnstars    │                     │ 4. CDS Simbad Database    │
       │    (STScI Pan-STARRS RGB) │                     │    (Proper motion query)  │
       └───────────────────────────┘                     ├───────────────────────────┤
                                                         │ 5. CDS VizieR Catalogs    │
                                                         │    (AllWISE, Gaia, 2MASS) │
                                                         └───────────────────────────┘
```

---

## 🛰️ 1. Internal BYW Microservices

### A. The Zooniverse Cross-Reference Engine (`/xref`)
- **Endpoint:** `http://byw.tools/xref?ra={ra}&dec={dec}`
- **Protocol:** HTTP GET returning JSON array of subject strings.
- **Client Implementation (`flash3.js:430-455`):**
  ```javascript
  this.updateZooiSubjects = function () {
      var loc_split = this.parseLoc();
      if (loc_split === null) return;
      jQuery.getJSON("/xref", {
          "ra": loc_split[0],
          "dec": loc_split[1]
      }, function (response) {
          var zs = jQuery("#zooiSubjects");
          zs.empty();
          if (response["ids"].length > 0) {
              response["ids"].forEach(function (v) {
                  var new_a = document.createElement("a");
                  new_a.setAttribute("href", "https://www.zooniverse.org/projects/marckuchner/backyard-worlds-planet-9/talk/subjects/" + v);
                  new_a.innerText = v;
                  zs.append(new_a);
              });
          } else {
              zs.append(document.createTextNode("None"));
          }
      });
  };
  ```

#### Live Verification Test (WISE 0855-0714):
```bash
$ curl "http://byw.tools/xref?ra=133.786245&dec=-7.244372"
{"ids":["28037622","13887868","28037622","28037592","28037592","13887813","28037627","13887874","28037627","28037595","28037595","13887821","28037618","13887861","28037618","28037655","13887928","28037655"]}
```
> [!NOTE]
> Every subject ID links directly to the Zooniverse Talk discussion board (e.g. `https://www.zooniverse.org/projects/marckuchner/backyard-worlds-planet-9/talk/subjects/28037622`), allowing users to immediately review whether the object was already tagged `#dipole`, `#mover`, or `#known`.

---

### B. The STScI Pan-STARRS1 Compositor Proxy (`/pawnstars`)
- **Endpoint:** `http://byw.tools/pawnstars?ra={ra}&dec={dec}&size={pixels}`
- **Pixel Scale Calculation:** Pan-STARRS has $0.25''\text{/pixel}$. To convert WiseView's FOV in arcseconds to pixels, the engine multiplies by 4:
  $$\text{Pixels} = \text{FOV}_{\text{arcsec}} \times 4$$
- **Client Implementation (`flash3.js:413-427`):**
  ```javascript
  this.updatePawnstars = function () {
      var loc_split = this.parseLoc();
      if (loc_split === null) return;
      jQuery.getJSON("/pawnstars", {
          "ra": loc_split[0],
          "dec": loc_split[1],
          "size": this.size_input.val() * 4 // arcseconds to pixels
      }, function (response) {
          var new_img = document.createElement("img");
          new_img.setAttribute("src", response);
          jQuery("#pawnstars").empty().append(new_img);
          that.updateZoom();
      });
  };
  ```

#### Live Verification Test:
```bash
$ curl "http://byw.tools/pawnstars?ra=133.786245&dec=-7.244372&size=704"
"http://ps1images.stsci.edu/cgi-bin/fitscut.cgi?red=%2Frings.v3.skycell%2F1176%2F014%2Frings.v3.skycell.1176.014.stk.y.unconv.fits&green=%2Frings.v3.skycell%2F1176%2F014%2Frings.v3.skycell.1176.014.stk.i.unconv.fits&blue=%2Frings.v3.skycell%2F1176%2F014%2Frings.v3.skycell.1176.014.stk.g.unconv.fits&..."
```
> [!TIP]
> The backend server resolves the STScI Pan-STARRS skycell ID (`1176.014`) and constructs an uncompressed FITS cutout composite mapping:
> - **Red Channel:** Pan-STARRS $y$-band ($963\text{ nm}$)
> - **Green Channel:** Pan-STARRS $i$-band ($754\text{ nm}$)
> - **Blue Channel:** Pan-STARRS $g$-band ($481\text{ nm}$)
> Cold brown dwarfs ($T < 700\text{ K}$) are completely black in all three bands, confirming non-detection in optical.

---

## 🔭 2. The 3 External Survey Verification Portals

### 1. DESI Legacy Imaging Surveys (`#legacySurvey`)
- **Target URL Template:**
  `http://legacysurvey.org/viewer?ra={ra}&dec={dec}&zoom=13&layer=unwise-neo11`
- **Key Parameters:**
  - `zoom=13`: Maps to $0.262''\text{/pixel}$ viewport resolution.
  - `layer=unwise-neo11`: Displays unWISE 11-year co-added infrared background with optical DESI DR10 contours.
- **Scientific Utility:** Allows simultaneous comparison of optical depth ($g, r, z$ bands down to $r \sim 24.5\text{ mag}$) and deep NEOWISE infrared emission.

### 2. CDS Simbad Astronomical Database (`#simbad`)
- **Target URL Template:**
  `http://simbad.u-strasbg.fr/simbad/sim-coo?Coord={ra}%20{dec}&Radius=10&Radius.unit=arcsec&coodisp1=d2&list.pmsel=on&list.plxsel=on&list.rvsel=on&list.bibsel=off&list.notesel=off&output.format=HTML`
- **Key Parameters:**
  - `Radius=10&Radius.unit=arcsec`: Tight $10''$ cone search around candidate.
  - `list.pmsel=on`: Includes proper motion measurements ($\mu_\alpha, \mu_\delta$).
  - `list.plxsel=on`: Displays trigonometric parallax ($\varpi$) and distance.
  - `list.rvsel=on`: Displays spectroscopic radial velocities ($v_r$).
- **Scientific Utility:** If Simbad returns an identified source, the candidate is immediately classified (e.g. `High Proper Motion Star`, `White Dwarf`, `Spectroscopic Binary`) without waiting for professional review.

### 3. CDS VizieR Catalog Service (`#vizier`)
- **Target URL Template:**
  `http://vizier.u-strasbg.fr/viz-bin/VizieR?-c={ra}%20{dec}&-c.rs=10&-out.add=_r&-sort=_r`
- **Key Parameters:**
  - `-c={ra} {dec}`: Center coordinate in decimal degrees.
  - `-c.rs=10`: Cone radius of $10''$.
  - `-out.add=_r`: Explicitly computes radial distance from center for every returned catalog entry.
  - `-sort=_r`: Sorts all catalog hits by ascending distance from query center.
- **Scientific Utility:** Cross-matches across 24,000+ astronomical catalogs, querying:
  - **CatWISE2020 (`II/365`):** W1/W2 magnitudes and $\mu_\alpha, \mu_\delta$.
  - **Gaia DR3 (`I/355`):** Precision 5-parameter astrometry down to $G \approx 21\text{ mag}$.
  - **2MASS (`II/246`):** Near-infrared $J, H, K_s$ photometry from 1999–2000.
  - **AllWISE (`II/328`):** 4-band cryogenic photometry ($3.4, 4.6, 12, 22\ \mu\text{m}$).

---

## 🛠️ 3. Full Integration into SPHEREx Hunter

In SPHEREx Hunter (`backend/services/verification_service.py` and `frontend/index.html`), Team RIP has implemented this entire suite of cross-survey links:

```python
# SPHEREx Hunter Backend Verification Builder
def generate_verification_suite(ra: float, dec: float, fov_arcsec: float = 176.0) -> dict:
    ps1_px = int(fov_arcsec * 4)
    return {
        "spherex_hub": f"/api/spherex/cutout?ra={ra}&dec={dec}&fov={fov_arcsec}",
        "wiseview_blink": f"http://byw.tools/wiseview#ra={ra:.6f}&dec={dec:.6f}&size={int(fov_arcsec)}&band=2&speed=500&diff=0&invert=1",
        "wiseview_diff": f"http://byw.tools/wiseview#ra={ra:.6f}&dec={dec:.6f}&size={int(fov_arcsec)}&band=2&speed=500&diff=1&invert=1",
        "legacy_survey": f"http://legacysurvey.org/viewer?ra={ra:.6f}&dec={dec:.6f}&zoom=13&layer=unwise-neo11",
        "panstarrs1": f"https://ps1images.stsci.edu/cgi-bin/ps1cutouts?pos={ra:.6f}+{dec:.6f}&filter=color&filter=g&filter=r&filter=i&filter=z&filter=y&size={ps1_px}&output_size=0&autoscale=99.5",
        "cds_simbad": f"http://simbad.u-strasbg.fr/simbad/sim-coo?Coord={ra:.6f}%20{dec:.6f}&Radius=10&Radius.unit=arcsec&list.pmsel=on&list.plxsel=on",
        "cds_vizier": f"http://vizier.u-strasbg.fr/viz-bin/VizieR?-c={ra:.6f}%20{dec:.6f}&-c.rs=10&-out.add=_r&-sort=_r",
        "byw_xref": f"http://byw.tools/xref?ra={ra:.6f}&dec={dec:.6f}"
    }
```

---

## 🔗 Related Notes in Obsidian Vault
- [[WISEVIEW_BYW_TOOLS_SITEMAP]] — Master directory of endpoints and hash parameters.
- [[01 - WiseView Core Engine & Blinking Pipeline]] — Core canvas engine and scaling.
- [[02 - WiseView Cloud Microservices & unWISE Infrastructure]] — Cloud Lambda and AMNH S3 CDN.
- [[03 - WiseView Synthetic Object Injection Engine]] — Synthetic dipole injection and nulling.
- [[04 - WiseView Version History & v2 vs v3 Architecture]] — Version history and backwards compatibility.
- [[Cross-Survey Catalogs (WISE, Gaia, 2MASS)]] — Multi-wavelength photometric matching.
