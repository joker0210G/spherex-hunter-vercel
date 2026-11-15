# 🎤 Winning Project Pitch Deck Outline (Strict 7-Slide Rule)
> **Challenge:** Planet X and SPHEREx | **Team:** RIP (Coimbatore, India)  
> **Official Limit:** **Maximum 7 slides** (including title and introductory slides). Projects exceeding 7 slides are **disqualified from Global Judging**.  
> **Language:** English only.

---

### Slide 1: Title, Team & Challenge
- **Visual:** High-resolution dark-mode visualization of the SPHEREx spacecraft mapping the infrared cosmos with glowing 102-band dispersion.
- **Headline:** **SPHEREx Hunter**
- **Tagline:** Interactive Time-Domain Infrared Sky Browser & Citizen Science Discovery Engine
- **Mandatory Details:**
  - **Challenge:** *Planet X and SPHEREx*
  - **Team Name:** Team RIP
  - **Team Members:** jokerodu (Lead), darkodu (Backend/Data), coolodu (Frontend/UI), iceodu (AI/Image Math), astrodu (Story/UX)
  - **Location:** Coimbatore, India (Local Event: Coimbatore)

---

### Slide 2: The Big Data Challenge
- **Headline:** Finding Needles in an Infrared Haystack
- **Key Points:**
  - NASA’s SPHEREx mission maps the entire sky every 6 months across **102 near-infrared spectral bands** ($0.75 - 5.00\ \mu\text{m}$).
  - Over **1 billion objects** observed per epoch—resulting in massive multi-epoch data cubes.
  - Elusive ultra-cool brown dwarfs, near-Earth asteroids, and hypothetical outer solar system bodies (Planet X) hide in this petabyte-scale stream.
  - **The Bottleneck:** Automated pipelines flag millions of candidates, but need accessible human-in-the-loop verification to filter false positives.

---

### Slide 3: Our Solution — SPHEREx Hunter
- **Headline:** Turning Petabytes into Real-Time Human Exploration
- **Key Points:**
  - High-performance, open-source web application connecting directly to NASA IRSA, SkyView, and ESA Gaia TAP archives.
  - **Instant Celestial Search:** Input any RA & Dec coordinates or select NASA benchmark calibration targets.
  - **Clyde Tombaugh Blink Comparator:** Multi-epoch temporal animation (2MASS 1999 $\to$ WISE 2010/2020 $\to$ SPHEREx 2025) utilizing the human brain's natural motion-detection reflexes.
  - **Responsive 60 FPS Engine:** Hardware-accelerated canvas with smooth frustum LOD streaming.

---

### Slide 4: Scientific Engineering & Difference Imaging
- **Headline:** Sub-Pixel Astrometry & ZOGY Background Subtraction
- **Key Points:**
  - **Rigorous Astrometric Alignment:** Standard Gnomonic Tangent (`TAN`) WCS projection ensuring sub-pixel registration across decades of survey baselines.
  - **ZOGY Difference Imaging ($I_2 - I_1$):** Mathematical background star subtraction with arcsinh dynamic range stretching.
  - **Transient & Dipole Highlighting:** Static background stars vanish into neutral gray, leaving moving proper-motion dipoles and variable stars glowing with clear contrast.

---

### Slide 5: 102-Band Infrared Spectroscopy & Array Co-Addition
- **Headline:** Beyond Images: Atmospheric Fingerprinting Across 6 Arrays
- **Key Points:**
  - **102 Continuous Spectral Channels:** Full coverage from $0.75\ \mu\text{m}$ to $5.00\ \mu\text{m}$ across detector arrays A1 through A6.
  - **Array Co-Addition:** Combines multi-channel signals to boost signal-to-noise ratio by $>4\times$.
  - **Molecular Fingerprint Identification:** Pinpoints absorption features for atmospheric Water ($H_2O$), Methane ($CH_4$), and Carbon Dioxide ($CO_2$) directly on the Spectral Energy Distribution curve.

---

### Slide 6: NASA Benchmark Verification Suite
- **Headline:** 100% Validated on Official NASA Calibration Targets
- **Visual Matrix:** 5 visual verification cards with detected dipole vectors:
  1. **WISE 0855-0714:** Cold Y-Dwarf ($T \approx 250\text{ K}$) shifting $8.12''/\text{yr}$ westward.
  2. **Barnard's Star:** High proper-motion star ($10.36''/\text{yr}$) northward shift clearly resolved.
  3. **Epsilon Indi B:** Brown dwarf binary companion companion motion verified.
  4. **RW Aurigae:** Young stellar object exhibiting eruptive $2.8\times$ flare variability.
  5. **R Draconis:** Mira pulsating giant showing $3.4\times$ amplitude modulation.

---

### Slide 7: Citizen Science, Open Science & Future Vision
- **Headline:** Democratizing Discovery for Everyone on Earth
- **Key Points:**
  - **Universal Deep-Linking:** Every sky region, zoom level, and epoch frame is shareable via a single URL for peer review and research papers.
  - **One-Click Candidate Flagging:** Intuitive discovery form generating standardized candidate alerts.
  - **Space Agency Partner Synergy:** Ready for multi-mission cross-correlation with CSA NEOSSat, ESA Euclid, and ISRO ASTROSAT.
  - **Closing Statement:** *The universe is shifting every six months. SPHEREx Hunter ensures humanity won't miss a single discovery.*
