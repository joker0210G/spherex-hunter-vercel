# 🛰️ CSA NEOSSat Mission Portal & Complete Site Map Codex
> **Source Root:** [https://www.asc-csa.gc.ca/eng/satellites/neossat/](https://www.asc-csa.gc.ca/eng/satellites/neossat/)  
> **Mission Lead:** Canadian Space Agency (CSA) & Defence Research and Development Canada (DRDC)  
> **Spacecraft Type:** Agile Microsatellite (~74 kg, 3U suitcase size)  
> **Orbital Baseline:** Sun-synchronous circular orbit at 800 km altitude (100 min period, 24/7 unhindered viewing)  
> **Primary Archives:** Canadian Astronomy Data Centre (CADC) & Open Government Canada  
> **Vault Location:** `05 - Research & Resources/CSA_NEOSSAT_SITEMAP.md`

---

## 1. 🌐 The Complete Site Map Architecture

```
https://www.asc-csa.gc.ca/eng/satellites/neossat/
│
├── 🛰️ 1. Spacecraft & Mission Infrastructure
│   ├── Mission Summary: World's first space telescope dedicated to asteroid tracking and space debris
│   ├── Operational Orbit: 800 km altitude Sun-synchronous dawn-dusk polar orbit (100-minute period)
│   ├── Daytime Immunity: Operates 24/7 outside Earth's atmosphere, unhindered by weather or daylight
│   ├── Spacecraft Platform: Microsat Systems Canada Inc. (MSCI) with Spectral Applied Research & COM DEV
│   ├── Precision Attitude Control: Heritage reaction wheels from MOST satellite (sub-arcsecond pointing stability)
│   └── Mission Partners: CSA (Space Astronomy) & DRDC (High Earth Orbit Space Surveillance - HEOSS)
│
├── 🔭 2. Science Focus Areas & Research Cycles (Cycles 1 - 10)
│   ├── Tracking Near-Earth Asteroids & Comets:
│   │   ├── Near-Sun asteroid detection near perihelion (low solar elongation ε < 45°)
│   │   ├── Active study of hazardous asteroid (3200) Phaethon near perihelion
│   │   └── Astrometric follow-up of NEOCP (Near-Earth Object Confirmation Page) targets
│   ├── Space Domain Awareness (HEOSS): Tracking resident space objects, orbital debris, and collision risks
│   ├── Exoplanet Transit Photometry:
│   │   ├── NOTES Survey: NEOSSat Observations of Transiting Exoplanets
│   │   ├── TESS Candidate Follow-up: TOI-123b, TOI-1516b, TOI-2046b, TOI-2395.01, WASP-43b
│   │   └── ORACLE Program: Orbit refinement and alias confirmation for long-period exoplanets (Cycles 7–10)
│   └── Stellar Variability & Ultracool Dwarfs:
│   │   ├── Measuring rotation periods of ultracool dwarfs in crowded TESS fields (Cycles 5, 6, 9)
│   │   ├── Monitoring the impending recurrent nova eruption of T Coronae Borealis (T CrB, Cycles 9–10)
│   │   └── White dwarf variability confirmation (Cycles 7–8)
│
├── 💾 3. Open Data & Archive Access Endpoints
│   ├── Canadian Astronomy Data Centre (CADC): https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/
│   │   ├── CAOM-2 TAP Endpoint: `https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/tap`
│   │   └── Python Query Client: `astroquery.cadc` (Collection: `NEOSSAT`)
│   ├── Canada Open Government Data Portal: Directive on Open Government (daily public FITS data downlinks)
│   └── NEOSSat Guest Observation Program: https://www.asc-csa.gc.ca/eng/funding-programs/funding-opportunities/ao/
│
└── 🇨🇦 4. Related Canadian Space Programs
    ├── MOST Satellite Heritage: https://www.asc-csa.gc.ca/eng/satellites/most/
    ├── James Webb Space Telescope (Canadian FGS/NIRISS): https://www.asc-csa.gc.ca/eng/satellites/jwst/
    ├── RADARSAT Constellation Mission (RCM): https://www.asc-csa.gc.ca/eng/satellites/radarsat/
    └── Defence Research and Development Canada (DRDC): http://www.drdc-rddc.gc.ca/
```

---

## 2. 📋 Comprehensive URL & Resource Directory

### A. Core Mission & Telescope Links
1. **CSA NEOSSat Portal:** [satellites/neossat/](https://www.asc-csa.gc.ca/eng/satellites/neossat/) — Central Canadian mission hub.
2. **French Language Mirror:** [fra/satellites/neossat/](https://www.asc-csa.gc.ca/fra/satellites/neossat/) — Official bilingual Canadian documentation.
3. **CSA Comets & Asteroids Guide:** [comets-and-asteroids.asp](https://www.asc-csa.gc.ca/eng/astronomy/solar-system/comets-and-asteroids.asp) — Solar system science context.

### B. Science Programs & Funding Opportunities
4. **Guest Observer Program AO (Cycle 7+):** [ao/2024-neossat-science-guest-observation-program-cycle-7.asp](https://www.asc-csa.gc.ca/eng/funding-programs/funding-opportunities/ao/2024-neossat-science-guest-observation-program-cycle-7.asp) — Open observation calls for international researchers.
5. **DRDC Space Domain Awareness:** [drdc-rddc.gc.ca](http://www.drdc-rddc.gc.ca/) — Military and civil orbital debris research.

### C. Open Data & Archival Services
6. **CADC Portal:** [cadc-ccda.hia-iha.nrc-cnrc.gc.ca](https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/) — Principal data archive hosted by NRC Herzberg Astronomy and Astrophysics Research Centre.
7. **CADC TAP Service:** `https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/tap` — Standard IVOA Table Access Protocol for programmatic ADQL querying.
8. **Open Government Portal:** [open.canada.ca](https://open.canada.ca/) — Open-data direct public access to NEOSSat images.

---

## 3. 🔬 Astrophysical Synergy with SPHEREx Hunter

The CSA NEOSSat mission directly solves one of the most critical challenges in the **Planet X and SPHEREx** hackathon challenge: **Distinguishing Solar System Asteroids from Distant Cold Brown Dwarfs and Planet X Candidates**.

### A. The Asteroid Streaklet vs. Dipole Distinction
When subtracting two astronomical epochs ($I_2 - I_1$):
- **Planet X / Cold Brown Dwarfs:** Move slowly across the sky ($0.1''\text{--}10''/\text{yr}$), producing **point-like stationary dipole pairs** (a negative PSF hole next to a positive PSF core).
- **Near-Earth Asteroids (NEAs):** Move rapidly ($> 10''/\text{hour}$ or several arcseconds during a single exposure), leaving **extended linear streaklet tracks**.

### B. Line Segment Detector (LSD) Streaklet Algorithm
Incorporated into SPHEREx Hunter's automated source discovery pipeline (`backend/services/cutout_engine.py`):
1. Compute the difference residual map: $D = I_2 - I_1$.
2. Run gradient orientation analysis:
   $$\nabla D(x, y) = \left( \frac{\partial D}{\partial x}, \frac{\partial D}{\partial y} \right), \quad \theta(x, y) = \arctan\left(\frac{\partial D/\partial y}{\partial D/\partial x}\right)$$
3. Identify aligned level-line regions where gradient vectors point in consistent directions over length $L \ge 5\text{ pixels}$.
4. **Classification Output:**
   - **Linear streak ($L > 5\text{ px}$, aspect ratio $> 2.5$):** Flagged as `[☄️ CSA NEOSSat Asteroid Streaklet (NEA / Minor Planet)]`.
   - **Symmetric circular dipole ($L \approx \text{FWHM}$, aspect ratio $\approx 1.0$):** Flagged as `[🪐 Genuine Time-Domain Candidate (Planet X / Brown Dwarf)]`.

---

## 4. 💻 Programmatic Query Recipes

### A. Querying NEOSSat Observations via `astroquery.cadc`
```python
from astroquery.cadc import Cadc
from astropy.coordinates import SkyCoord
from astropy import units as u

cadc = Cadc()

# Target coordinates (e.g., Near-Sun Asteroid Phaethon)
coord = SkyCoord(ra=84.29, dec=22.36, unit='deg')

# Query CADC for NEOSSat observations
results = cadc.query_region(coord, radius=0.1 * u.deg, collection='NEOSSAT')

print(f"Found {len(results)} NEOSSat observations in CADC.")
for row in results[:5]:
    print(f"Observation ID: {row['observationID']} | Exposure: {row['exposure_time']}s | Target: {row['target_name']}")
```

### B. Direct TAP ADQL Query for NEOSSat Images
```sql
SELECT
    observationID, target_name, time_exposure,
    spatial_bounds, access_url
FROM
    caom2.Observation
WHERE
    collection = 'NEOSSAT'
    AND CONTAINS(POINT('ICRS', 84.29, 22.36), spatial_bounds) = 1
ORDER BY
    time_bounds_lower DESC;
```
