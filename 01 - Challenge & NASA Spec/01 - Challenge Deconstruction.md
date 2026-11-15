# 📜 Challenge Deconstruction: Planet X and SPHEREx
> **NASA Source:** [2026 NASA Space Apps Challenge - Planet X and SPHEREx](https://www.spaceappschallenge.org/2026/challenges/planet-x-and-spherex/)
> **Track:** Advanced / Astrophysics / Software / Citizen Science

---

## 1. The Core Problem
In May 2025, NASA launched the **SPHEREx** (Spectro-Photometer for the History of the Universe, Epoch of Reionization and Ices Explorer) space telescope. SPHEREx maps the entire celestial sphere every **six months** across **102 distinct near-infrared bands** (0.75 to 5.0 microns).

Over its nominal 2-year baseline:
- SPHEREx produces **4 full-sky all-epoch surveys**.
- Over **1 billion astronomical objects** are imaged multiple times.
- Objects move or vary in brightness:
  - **Asteroids and Comets:** Fast motion across days/months (solar system).
  - **Brown Dwarfs & Nearby Stars:** High proper motion across 6-month epochs (parallax & space velocity).
  - **Variable Stars & Supernovae:** Large photometric flux variations over time.
  - **Hypothetical "Planet X" / Planet Nine:** Very slow, dim, outer-solar-system thermal emitter.
- **The Challenge:** No single astronomer or automated script can comprehend or inspect every artifact and transient. We must build a **public-facing web tool** that democratizes this data so anyone can enter coordinates and see the sky evolve over time.

---

## 2. Core Functional Requirements
1. **Coordinate Input:** Accepts Right Ascension (RA) and Declination (Dec) in multiple standard formats (J2000 sexagesimal `HH:MM:SS.ss +DD:MM:SS.s` and decimal degrees `deg, deg`).
2. **Multi-Epoch Display:** Show sequential images of the requested sky patch as an animated "little video" (Blink Comparator) to make shifting objects jump out to human eyes.
3. **Mandatory Benchmark Target Suite:** The tool **must** be validated on:
   - Barnard's Star (proper motion)
   - Epsilon Indi B (brown dwarf pair)
   - WISE 0855 (cold brown dwarf)
   - RW Aurigae (variable star)
   - R Draconis (variable star)

---

## 3. NASA Potential Considerations (Our Competitive Advantage)
To score in the top tier (Global Nominee / Winner level), we implement all of NASA's suggested bonus capabilities:

| NASA Suggested Feature | How We Implement It | Responsible Track |
| :--- | :--- | :--- |
| **1. Easy updates with new data** | Modular API ingestion adapter that connects to IPAC IRSA archive tables via PyVO / TAP protocols. | Backend / Data |
| **2. Creative 102-band display** | Co-add the 6 SPHEREx detector arrays into 6 synthetic broadbands to maximize SNR, plus an on-the-fly 102-band SED spectral graph for any clicked pixel. | Astro-Data / Frontend |
| **3. Image Addition & Subtraction** | Pixel-wise difference imaging ($I_{	ext{diff}} = I_{t2} - I_{t1}$) to eliminate stationary background stars and highlight moving/variable transients. | CV & Image Math |
| **4. User-selectable Field of View (FOV)** | Zoomable viewport from wide ($1^\circ 	imes 1^\circ$ for fast solar system objects) to narrow ($2' 	imes 2'$ for stellar proper motion). | Web UI / Canvas |
| **5. Cross-Survey Overlays** | Instant toggle to overlay **Gaia DR3** proper motion vectors and **WISE / 2MASS / Pan-STARRS** archival imagery for historical baseline comparisons. | Astronomy / Frontend |
| **6. URL Deep-Linking** | Clean query parameters: `https://spherex-hunter.app/?ra=133.795&dec=-7.245&fov=5m&speed=3fps&mode=diff` for 1-click sharing and embedding. | Full-Stack Web |
| **7. Contamination Flags** | Display SPHEREx pixel quality flags (cosmic rays, saturation, zodiacal light, stray light) in a HUD overlay. | UI/UX & Data |
| **8. Open Astronomical Tooling** | Built on top of **Astropy**, **Aladin Lite (CDS Strasbourg)**, and **PyVO**. | Full Team |

---

## 4. Evaluation Criteria (NASA Space Apps Rubric)
- **Impact:** Does this tool enable real citizen science discoveries (asteroids, brown dwarfs, Planet X)?
- **Creativity:** Is the 102-band representation and blink comparator novel and intuitive?
- **Validity:** Are astronomical coordinates, WCS alignments, and photometry mathematically correct?
- **Relevance:** Does it solve the SPHEREx big-data bottleneck?
- **Presentation:** Is the web app visually stunning, fast, and accompanied by a concise 30-second to 2-minute demo video?
