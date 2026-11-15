# 📚 SPHEREx Hunter - Astronomical References & Data Portals
> **NASA Space Apps Challenge 2026** | **Team:** RIP
> **Document:** `docs/references.md`

This document summarizes the external astronomical data services, archives, tutorials, and partner platforms referenced by SPHEREx Hunter. All third-party documentation and manuals are kept external per repository hygiene rules.

---

## 1. SPHEREx Mission & IPAC / IRSA Archive
* **NASA SPHEREx Mission Hub:** [https://spherex.caltech.edu](https://spherex.caltech.edu)
* **IRSA SPHEREx Data Access:** [https://irsa.ipac.caltech.edu/applications/spherex](https://irsa.ipac.caltech.edu/applications/spherex)
* **IVOA TAP Service:** `https://irsa.ipac.caltech.edu/TAP` (`table = spherex.obscore`)
  * Contains $\sim 1.62\times 10^6$ observation footprints across 6 spectral detector arrays ($0.75\,\mu\text{m}$ to $5.0\,\mu\text{m}$).
  * Spatial queries: IVOA ADQL `INTERSECTS(s_region, ...)` or point cone search.
* **SIAv2 Image Cutout Service:** IVOA Simple Image Access v2 protocols for multi-extension FITS (MEF) cutouts.
* **Data License / Terms:** NASA Open Data Policy (public domain / free scientific use).

---

## 2. Canadian Space Agency (CSA) & CADC NEOSSat
* **Canadian Astronomy Data Centre (CADC):** [https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca](https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca)
* **CADC CAOM-2 TAP Endpoint:** `https://ws.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/argus/sync` (`collection = 'NEOSSAT'`)
* **CADC DataLink Service:** `https://ws.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/caom2ops/datalink?ID=...`
* **CSA NEOSSat Open Data Portal:** [https://data.asc-csa.gc.ca/dataset/neossat](https://data.asc-csa.gc.ca/dataset/neossat)
* **Purpose in SPHEREx Hunter:** Asteroid tracklet verification. When an infrared transient or high-proper-motion candidate is detected, CADC CAOM-2 is queried for archival NEOSSat tracks to check whether the object is a known or candidate Solar System asteroid.
* **Data License / Terms:** Open Government Licence - Canada.

---

## 3. IMCCE SkyBoT (Système de Recommandation des Petits Corps)
* **Endpoint:** `https://ssp.imcce.fr/webservices/skybot/api/conesearch.php`
* **Query Parameters:** `ra`, `dec`, `sdist` (arcseconds), `epoch` (Julian Date, geocentric observer 500).
* **Purpose:** Ephemeris cone-search identifying every known asteroid, comet, Near-Earth Object (NEO), Trojan, Centaur, and Trans-Neptunian Object (TNO) located within the field of view at the observation epoch.
* **HTTP User-Agent Note:** IMCCE requires a descriptive User-Agent header (generic Python urllib agents may be blocked with HTTP 403). SPHEREx Hunter identifies itself with `SPHERExHunter/6.0 (NASA Space Apps 2026, Team RIP)`.
* **Data License / Terms:** Observatoire de Paris / IMCCE Open Science.

---

## 4. Dan Caselden's WiseView & unWISE
* **WiseView 2 / 3 Viewer:** [http://byw.tools/wiseview](http://byw.tools/wiseview)
* **unWISE Coadds & Catalogs:** [http://unwise.me](http://unwise.me) (Lang 2014, Meisner et al. 2017)
* **Backyard Worlds: Planet 9 Project:** [https://www.backyardworlds.org](https://www.backyardworlds.org)
* **Deep Link Pattern:** `http://byw.tools/wiseview#ra={ra}&dec={dec}&size={size}&band=3&linear=True&diff=True`
* **Purpose:** External citizen-science verification of unbinned W1/W2 infrared motion signatures across a 15-year baseline (WISE 2010 to NEOWISE 2024).

---

## 5. ESA Gaia DR3 & CDS Strasbourg
* **ESA Gaia Archive:** [https://gea.esac.esa.int/archive/](https://gea.esac.esa.int/archive/)
* **CDS SIMBAD Astronomical Database:** [https://simbad.cds.unistra.fr/simbad/](https://simbad.cds.unistra.fr/simbad/)
* **CDS Aladin Lite v3:** [https://aladin.cds.unistra.fr/AladinLite/](https://aladin.cds.unistra.fr/AladinLite/)
* **Purpose:** Optical counterpart dropout testing ($G$-band absence proves ultracold substellar/IR-only nature) and high-accuracy astrometric reference frames.
