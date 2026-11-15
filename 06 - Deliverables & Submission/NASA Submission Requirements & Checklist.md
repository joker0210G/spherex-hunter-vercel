# 📝 NASA Space Apps Submission Requirements & Checklist
> **Team:** RIP (Coimbatore, India) | **Challenge:** Planet X and SPHEREx  
> **Official Guide Reference:** [NASA Project Submission Guide](https://www.spaceappschallenge.org/resources/project-submission-guide/#project-page-form-field-instructions)

---

## ⏱️ Critical Deadlines & Submission Clock
- **Submission Opens:** Saturday, November 14, 2026 @ 9:00 AM (Local Event Time)
- **Hard Deadline:** **Sunday, November 15, 2026 @ 11:59 PM (Local Event Time)**
- **Warning:** Any projects saved or submitted past this deadline are **not eligible for judging**.
- **Edit Lock:** Toggle **"Lock" to 'ON'** while editing your project tab to prevent teammates from overwriting changes.
- **Multiple Saves:** Save your progress frequently via the blue **"Save Progress"** button. Only the last submission before the deadline is evaluated by judges.

---

## 📌 Submission Portal Fields (Exact Requirements)

### 1. Project Title
- **Project Title:** `SPHEREx Hunter: Interactive Time-Domain Infrared Sky Browser & Citizen Science Discovery Engine`
- **Tagline:** Unlocking the 102-band infrared sky to crowdsource the search for Planet X, brown dwarfs, and moving asteroids.

### 2. High-Level Summary (What, How, Why)
- **Status:** Drafted & verified against NASA criteria.
- **Summary:**
  > NASA's SPHEREx mission is mapping over 1 billion celestial objects across 102 near-infrared bands every six months. To solve the challenge of uncovering hidden asteroids, ultra-cool brown dwarfs, and Planet X in this petabyte-scale data stream, Team RIP developed **SPHEREx Hunter**—a high-performance, web-based time-domain astronomical observatory. 
  > 
  > SPHEREx Hunter enables astronomers and citizen scientists to enter any sky coordinates and instantly stream multi-epoch, sub-pixel WCS-aligned cutouts. It features an interactive blink comparator mimicking Clyde Tombaugh’s Pluto discovery method, a mathematically rigorous ZOGY difference-imaging engine that subtracts static background stars, and an on-the-fly 102-band infrared spectroscopy analyzer ($0.75 - 5.0\ \mu\text{m}$) capable of detecting atmospheric water, methane, and carbon dioxide fingerprints. By crowdsourcing verification through one-click deep links, SPHEREx Hunter ensures no transient or moving world in SPHEREx's survey goes unnoticed.

### 3. Project Demo Link (Strict 30-Second Video OR 7-Slide Limit)
- [ ] **Selected Demo Format:** 30-Second Video Pitch (OR 7-Slide Presentation Deck).
- [ ] **Strict Time/Slide Limit:**
  - If Video: **Must be 30 seconds or less!** (Exceeding 30 seconds leads to disqualification from Global Judging).
  - If Slide Deck: **Must be 7 slides or less** (including title and intro slides).
- [ ] **Hosting:** Hosted on a publicly accessible external site (YouTube, Google Drive, GitHub, OneDrive, Dropbox).
- [ ] **Access Test:** Publicly accessible with **zero login, password, or permissions required** (verified in private/incognito browser).
- [ ] **Language:** English language (or English subtitles if video is spoken in another language).

### 4. Final Project Public Link
- [ ] **Public GitHub Repository:** `https://github.com/joker0210G/spherex-hunter`
- [ ] **Live Web Application Link:** Deployed and publicly accessible.
- [ ] **Firewall Whitelist (Recommended):** Submit the [FortiGuard Web Filter Classification](https://www.fortiguard.com/faq/wfratingsubmit) with category *Education / Web-based Application* and company *N/A* to prevent judge firewalls from blocking access.

### 5. Detailed Project Description
- [x] **What exactly does it do?** Full multi-epoch infrared blink comparison, ZOGY difference imaging, and 102-band spectral analysis.
- [x] **How does it work?** FastAPI/Astropy backend + hardware-accelerated 60 FPS HTML5 canvas frontend with Aladin Lite HiPS integration.
- [x] **What benefits does it have?** Bridges raw FITS data with human visual motion detection and rapid citizen science discovery.
- [x] **What do you hope to achieve?** Fast detection of solar system movers, cold brown dwarfs, and Planet X in SPHEREx releases.
- [x] **What tools and software were used?** Python, FastAPI, Astropy, Astroquery, NumPy, SciPy, Vanilla JavaScript, HTML5 Canvas, Web Audio API.

### 6. Super Intelligence (SI) / AI Disclosure
- [x] **Disclosed in Form:** Yes.
- [x] **Rules Followed:**
  - No modified NASA logos or mission branding used.
  - Visible watermarks on SI-generated images/videos.
  - Descriptive text and metadata acknowledgment for code, data, and audio.
  - SI was used solely to accelerate engineering and documentation, not to invent the core solution idea.

### 7. NASA Data & Resources Used (Mandatory for Global Awards)
- [x] **SPHEREx 102-Band Spectral Parameters & Mission Cadence:** Arrays A1–A6 ($0.75 - 5.00\ \mu\text{m}$).
- [x] **NASA IRSA (Infrared Science Archive):** AllWISE, 2MASS, and multi-epoch survey archives via TAP.
- [x] **NASA SkyView Virtual Observatory:** Temporal cutouts.
- [x] **Astropy Core Library:** Celestial spherical trigonometry, WCS TAN projection, and FITS I/O.

### 8. Space Agency Partners & Third-Party Resources
- [x] **ESA Gaia DR3 Catalog:** Reference frame astrometry and proper-motion epoch propagation.
- [x] **CDS Strasbourg:** HiPS color layers (`P/2MASS/color`, `DSS2/color`) and Aladin Lite.
- [x] **CADC (CSA Partner):** NEOSSat asteroid and transient validation bridge.

---

## 🏆 Scoring Rubric Alignment (1–5 Scale)
- **Impact (5/5):** Solves the petabyte-scale big-data challenge of SPHEREx (>1 billion objects) through open citizen science.
- **Creativity (5/5):** Clyde Tombaugh blink comparison + modern ZOGY difference imaging + 6-detector array SNR co-addition ($>4\times$).
- **Validity (5/5):** Astropy WCS sub-pixel alignment, arcsinh contrast stretching, and 100% verified detection across all 5 NASA benchmark targets.
- **Relevance (5/5):** Directly fulfills every primary and secondary requirement of the SPHEREx challenge.
- **Presentation (5/5):** Engaging visual storytelling strictly adhering to the 30-second video / 7-slide format limit.

---

## 🛡️ Final Submission Protocol Checklist
- [ ] All team members confirmed participants at Coimbatore, India Local Event.
- [ ] All required fields completed in English.
- [ ] No likeness of persons under 18 included.
- [ ] Checked: *"Agree to Terms and Conditions"*.
- [ ] Checked: *"Confirm All Work is Original"*.
- [ ] Clicked: **"Submit for Judging"** before Sunday, Nov 15 @ 11:59 PM.
- [ ] Verified green submission confirmation banner.
- [ ] Downloaded Participant Certificates (PDF, Letter format) from user profiles.
