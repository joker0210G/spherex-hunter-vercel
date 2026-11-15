# 🌌 STScI MAST Gaia Mission Portal & Complete Site Map Codex
> **Source Root:** [https://archive.stsci.edu/missions-and-data/gaia](https://archive.stsci.edu/missions-and-data/gaia)  
> **Host Archive:** Mikulski Archive for Space Telescopes (MAST), Space Telescope Science Institute (STScI)  
> **Mission Agency:** European Space Agency (ESA) with NASA / MAST Mirror Collaboration  
> **Operational Baseline:** 2013-12-19 to 2025-01-15 (Over 1 Billion Celestial Sources)  
> **Vault Location:** `05 - Research & Resources/MAST_GAIA_SITEMAP.md`

---

## 1. 🌐 The Complete Site Map Architecture

```
https://archive.stsci.edu/missions-and-data/gaia
│
├── 🔭 1. Mission Overview & Telescope Specifications
│   ├── Wavelength Coverage: Optical (330 to 1050 nm: G-band, BP, RP)
│   ├── Operational Orbit: Sun-Earth Lagrange Point 2 (L2)
│   ├── Mission Baseline: Launch December 19, 2013 | Observations: 2014-07-27 to 2025-01-15
│   ├── Astrometric Precision: Reaching micro-arcseconds (~10 to 100 μas) down to G ~ 20.7 mag
│   ├── Astrometry Instrument Technical Guide: https://www.cosmos.esa.int/web/gaia/astrometric-instrument
│   └── BP/RP Spectrophotometry Instrument Guide: https://www.cosmos.esa.int/documents/29201/302420/IN_photometric_instrument-1.pdf
│
├── 📚 2. ESA Community Documentation & Science Portals
│   ├── ESA Gaia Science Community Hub: https://www.cosmos.esa.int/web/gaia/home
│   ├── ESA Billion Star Surveyor Overview: http://esa.int/Science_Exploration/Space_Science/Gaia
│   └── Official ESA Gaia Archive Interface: https://gea.esac.esa.int/archive/
│
├── 📦 3. Data Releases & Permanent DOIs
│   ├── Data Release 1 (DR1) Overview & DOI: https://archives.esac.esa.int/doi/html/data/astronomy/gaia/DR1.html
│   ├── Data Release 2 (DR2) Overview & DOI: https://archives.esac.esa.int/doi/html/data/astronomy/gaia/DR2.html
│   ├── Early Data Release 3 (EDR3) Overview & DOI: https://archives.esac.esa.int/doi/html/data/astronomy/gaia/EDR3.html
│   └── Data Release 3 (DR3) Overview & DOI: https://archives.esac.esa.int/doi/html/data/astronomy/gaia/DR3.html
│
└── 💾 4. MAST Data Access Interfaces
    ├── MAST Portal (Interactive Cross-Mission Sky Search): https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html
    ├── MAST CasJobs (Server-Side SQL Engine for Massive Catalogs): http://mastweb.stsci.edu/mcasjobs/
    ├── Virtual Observatory (VO / TAP Web Services): http://gsss.stsci.edu/webservices/vo/webform.aspx
    └── Programmatic Astroquery MAST Module: https://astroquery.readthedocs.io/en/latest/mast/mast.html
```

---

## 2. 📋 Comprehensive URL & Resource Catalog

### A. Core Overview & Instrument Links
1. **MAST Gaia Mission Portal:** [missions-and-data/gaia](https://archive.stsci.edu/missions-and-data/gaia) — Primary NASA gateway to Gaia mirror holdings.
2. **Astrometric Instrument Reference:** [astrometric-instrument](https://www.cosmos.esa.int/web/gaia/astrometric-instrument) — Details on the focal plane array, CCD pixel architectures, and 5-parameter astrometric solutions $(\alpha, \delta, \varpi, \mu_\alpha \cos\delta, \mu_\delta)$.
3. **Photometric Instrument Reference (BP/RP):** [photometric_instrument-1.pdf](https://www.cosmos.esa.int/documents/29201/302420/IN_photometric_instrument-1.pdf) — Prism dispersion optics separating Blue Photometer ($330\text{--}680\text{ nm}$) and Red Photometer ($640\text{--}1050\text{ nm}$).

### B. ESA Community Documentation
4. **ESA Gaia Science Community:** [web/gaia/home](https://www.cosmos.esa.int/web/gaia/home) — Official science team papers, data models, and community releases.
5. **ESA Billion Star Surveyor:** [Space_Science/Gaia](http://esa.int/Science_Exploration/Space_Science/Gaia) — Mission milestones and general astronomical outreach.
6. **ESA Gaia Archive:** [gea.esac.esa.int/archive/](https://gea.esac.esa.int/archive/) — European Space Astronomy Centre (ESAC) direct TAP query engine.

### C. Data Releases & Permanent DOIs
7. **Gaia DR1 (September 2016):** [DR1.html](https://archives.esac.esa.int/doi/html/data/astronomy/gaia/DR1.html) — 1.1 billion positions; Tycho-Gaia Astrometric Solution (TGAS) proper motions.
8. **Gaia DR2 (April 2018):** [DR2.html](https://archives.esac.esa.int/doi/html/data/astronomy/gaia/DR2.html) — 1.3 billion 5-parameter astrometric sources; $G, G_{\text{BP}}, G_{\text{RP}}$ photometry; 7.2 million radial velocities.
9. **Gaia EDR3 (December 2020):** [EDR3.html](https://archives.esac.esa.int/doi/html/data/astronomy/gaia/EDR3.html) — Substantially upgraded astrometry with 33 months of observations; reduced proper motion errors by a factor of 2.
10. **Gaia DR3 (June 2022):** [DR3.html](https://archives.esac.esa.int/doi/html/data/astronomy/gaia/DR3.html) — 1.8 billion sources; 33 million radial velocities; 220 million low-resolution BP/RP spectra; astrophysical parameters ($T_{\text{eff}}, \log g, [\text{M/H}]$); binary star orbits.

### D. Data Access Interfaces
11. **MAST Portal:** [Mashup/Clients/Mast/Portal.html](https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html) — Interactive GUI for cross-matching Gaia sources against HST, JWST, TESS, and Kepler targets.
12. **MAST CasJobs:** [mcasjobs/](http://mastweb.stsci.edu/mcasjobs/) — High-throughput relational SQL database allowing queries across billions of Gaia records with personal `mydb` table allocations.
13. **Virtual Observatory (VO):** [webservices/vo/webform.aspx](http://gsss.stsci.edu/webservices/vo/webform.aspx) — Standardized IVOA ConeSearch and TAP services.
14. **Astroquery MAST:** [astroquery.mast](https://astroquery.readthedocs.io/en/latest/mast/mast.html) — Python client for scriptable MAST catalog retrieval.

---

## 3. 🔬 Astrophysical Synergy with SPHEREx Hunter

The STScI MAST Gaia archive serves two vital roles in Team RIP's time-domain detection pipeline:

### A. The Optical Dropout Filter (Finding Planet X / Cold Brown Dwarfs)
- **Problem:** When searching for cold brown dwarfs (such as **WISE 0855-0714**, $T \approx 250\text{ K}$) or hypothetical outer Solar System bodies (Planet X), optical telescopes cannot see them because their Planck blackbody radiation peaks deeply in the mid-infrared ($3\text{--}5\ \mu\text{m}$).
- **Detection Algorithm:**
  1. Detect a prominent dipole in the SPHEREx / 2MASS difference image ($I_2 - I_1$).
  2. Query Gaia DR3 within a $5.0''$ radius via MAST / TAP.
  3. **Classification Rule:**
     $$\text{Gaia Match Found } (G < 20.7) \implies \text{Normal Galactic Star (Fast Proper Motion)}$$
     $$\text{NO Gaia Match Found } (G \ge 21.0 \text{ or Dropout}) \implies \mathbf{Cold\ Infrared\ Candidate\ (Brown\ Dwarf\ /\ Planet\ X)}$$
- **Verification:** In our live app, searching **WISE 0855** displays:
  > `[☄️ Potential Asteroid / Planet X Candidate (No Optical Gaia DR3 Match - Infrared Exclusive)]`

### B. High Proper Motion Vector Overlays (Barnard's Star)
- For bright optical stars like **Barnard's Star** ($G \approx 8.2\text{ mag}$), Gaia DR3 provides high-precision proper motion vectors:
  $$\mu_\alpha \cos\delta = -798.58\text{ mas/yr}, \quad \mu_\delta = 10328.12\text{ mas/yr} \implies \mu = 10.36''/\text{yr}$$
- SPHEREx Hunter plots these vectors directly on the HTML5 canvas as arrowheads from Epoch 1 (2MASS 1999) to Epoch 2 (SPHEREx 2025), confirming stellar trajectories against empirical space observatory astrometry.

---

## 4. 💻 Programmatic Query Recipes

### A. Querying Gaia DR3 via Astroquery MAST
```python
from astroquery.mast import Catalogs
from astropy.coordinates import SkyCoord
from astropy import units as u

# Target: Barnard's Star
coord = SkyCoord(ra=269.45208, dec=4.69339, unit='deg')

# Cone search Gaia DR3 in MAST
gaia_matches = Catalogs.query_region(
    coord,
    radius=0.01 * u.deg,
    catalog="Gaia",
    version=3
)

print(f"Found {len(gaia_matches)} Gaia DR3 stars.")
for row in gaia_matches[:5]:
    print(f"ID: {row['source_id']} | G Mag: {row['phot_g_mean_mag']:.2f} | PM: {row['pm']:.1f} mas/yr")
```

### B. High-Performance Relational Query via MAST CasJobs SQL
```sql
-- Query high proper motion stars in CasJobs
SELECT TOP 100
    source_id, ra, dec, pmra, pmdec,
    SQRT(POWER(pmra, 2) + POWER(pmdec, 2)) AS total_pm_mas,
    phot_g_mean_mag
FROM
    gaia_dr3.gaia_source
WHERE
    phot_g_mean_mag < 18.0
    AND SQRT(POWER(pmra, 2) + POWER(pmdec, 2)) > 500.0 -- Fast movers (> 0.5"/yr)
ORDER BY
    total_pm_mas DESC;
```
