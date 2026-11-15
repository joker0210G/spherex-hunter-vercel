# 📜 Team RIP Constitution: NASA Space Apps SPHEREx Challenge

## Core Principles

1. **Scientific Integrity Over Gimmicks (Real Data First)**:
   - The web tool must serve authentic astronomical data from NASA/IPAC IRSA, SkyView, and SPHEREx archives.
   - Visualizations must be grounded in real astronomical coordinates (ICRS J2000), genuine flux units, and calibrated WCS (World Coordinate System) astrometry.
   - No video game physics or distractions that obscure scientific discovery.

2. **Layman Accessibility & Citizen Science Discovery**:
   - Complex astrophysics must be rendered instantly readable: blinking time-domain flipbooks, difference imaging dipoles ($I_2 - I_1$), and 6-detector co-adds that make moving dots and variable flares obvious to anyone.
   - Provide dual coordinate parsing: Sexagesimal (`08h55m10.831s, -7d14m42.53s`) and Decimal Degrees (`133.79513°, -7.24515°`).

3. **Multi-Epoch & Multi-Mission Synergy**:
   - Compare SPHEREx multi-epoch scans (6-month cadences) with archival baseline surveys (WISE 3.4/4.6 μm, 2MASS J/H/Ks, Gaia DR3 astrometry).
   - Dynamic Field of View selection (1' to 15') to balance tracking speed with data transfer.

4. **102-Band Near-Infrared Spectral Discovery**:
   - Support on-the-fly Spectral Energy Distribution (SED) extraction across all 6 SPHEREx detector arrays (0.75 - 5.00 μm) with molecular signature identification ($H_2O, CO_2, CH_4, CO$).

5. **Universal Embeddability & Open Science**:
   - Queryable and shareable via direct URL parameters (`?ra=...&dec=...&fov=...&target=...`).
   - Clean, reproducible, open-source Python backend (Astropy, PyVO, Astroquery, FastAPI) and responsive zero-dependency frontend.
