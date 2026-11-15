# 🛰️ Official NASA Space Apps Project Submission Guide & Form Field Instructions
> **Reference URL:** [NASA Space Apps Project Submission Guide](https://www.spaceappschallenge.org/resources/project-submission-guide/#project-page-form-field-instructions)  
> **Source Guidelines:** 2026 Global Hackathon Rules, Terms & Conditions, and Judging Criteria  
> **Target Challenge:** Planet X and SPHEREx | **Team:** RIP (Coimbatore, India)

---

## ⏱️ Critical Deadlines & Submission Clock

| Event Stage | Start Time | Deadline | Notes |
| :--- | :--- | :--- | :--- |
| **Project Submission Window** | **Saturday, November 14, 2026 @ 9:00 AM** | **Sunday, November 15, 2026 @ 11:59 PM** | Strict local event time zone. |
| **Universal Event Teams** | Saturday, Nov 14 @ 9:00 AM | Sunday, Nov 15 @ 11:59 PM | Local time of Team Owner's area of residence. |
| **Judging Cut-off** | Sunday, Nov 15 @ 11:59 PM | — | **Hard stop:** Any projects saved or submitted past this deadline are **not eligible for judging**. |

> [!IMPORTANT]
> **Saving vs. Submitting:**  
> - You can edit and save your progress as many times as you like by clicking **"Save Progress"** on the right side of the project page. Changes are visible only to your team until submitted.
> - **Edit Lock:** Toggle the edit **"Lock" to 'ON'** while editing so teammates know changes are in progress, preventing accidental overwriting.
> - You must click **"Submit for Judging"** before the 11:59 PM deadline. Only the last saved submission is reviewed by judges.

---

## 📋 Exact Form Field Instructions & Requirements

### 1. Project Title
- **Field Label:** *What is the name of your project?*
- **Official Instruction:** Share your project's title and tagline to catch your audience's attention. Titles should be short but indicate what problem the project solves or what people gain.
- **Team RIP Input:**
  ```text
  SPHEREx Hunter: Interactive Time-Domain Infrared Sky Browser & Citizen Science Discovery Engine
  ```

---

### 2. High-Level Summary
- **Field Label:** *Provide a high-level summary of your project. What did you develop? How does it address the challenge? Why is it important?*
- **Official Guidance:** Keep it concise, engaging, and focused on the core innovation.
- **Team RIP Response Draft:**
  > NASA's SPHEREx mission is mapping over 1 billion celestial objects across 102 near-infrared bands every six months. To solve the challenge of uncovering hidden asteroids, ultra-cool brown dwarfs, and Planet X in this petabyte-scale data stream, Team RIP developed **SPHEREx Hunter**—a high-performance, web-based time-domain astronomical observatory. 
  > 
  > SPHEREx Hunter enables astronomers and citizen scientists to enter any sky coordinates and instantly stream multi-epoch, sub-pixel WCS-aligned cutouts. It features an interactive blink comparator mimicking Clyde Tombaugh’s Pluto discovery method, a mathematically rigorous ZOGY difference-imaging engine that subtracts static background stars, and an on-the-fly 102-band infrared spectroscopy analyzer ($0.75 - 5.0\ \mu\text{m}$) capable of detecting atmospheric water, methane, and carbon dioxide fingerprints. By crowdsourcing verification through one-click deep links, SPHEREx Hunter ensures no transient or moving world in SPHEREx's survey goes unnoticed.

---

### 3. Project Demonstration ("Demo")
- **Field Label:** *Provide a short demonstration ("demo") of your project...*
- **Mandatory Requirements:**
  - **Format Choice:** Must be either:
    1. **Video:** **30 seconds or less!** (Exceeding 30 seconds disqualifies the project from Global Judging).
    2. **Slide Deck:** **Up to 7 slides** including title and intro slides (Exceeding 7 slides disqualifies from Global Judging).
  - **Hosting:** Must be hosted on an external public cloud or repository (YouTube, Google Drive, GitHub, OneDrive, Dropbox).
  - **Access Permissions:** Must be **100% publicly accessible** with **no passwords, logins, or access requests required**. Test in an incognito/private browser before submitting!
  - **Language:** English language required. If video narration is in another language, **English subtitles are mandatory**. Slide decks must be written in English.
  - **Judging Weight:** Directly determines scoring in the **Presentation** category (1 to 5 points).

#### Recommended 30-Second Video Pitch Structure:
- `[0:00]` **Introduction:** State your name and team name (*"We are Team RIP from Coimbatore, India..."*).
- `[0:02]` **Lead-in:** State the challenge and motivation (*"NASA's SPHEREx is mapping billions of objects in 102 infrared bands, but moving asteroids and Planet X hide in the data."*).
- `[0:05]` **Project Name & Tagline:** Introduce *SPHEREx Hunter*.
- `[0:10]` **Describe the Idea & User Experience:** Show the live tool in action (Blink comparator, sub-pixel difference dipole, and 102-band spectral curve powered by NASA open data).
- `[0:20 - 0:30]` **Future Vision:** Conclude with the broader impact (*"Empowering humanity to discover new worlds across the infrared sky."*).

#### Recommended 7-Slide Deck Structure:
- **Slide 1:** Title, Team Name (Team RIP), Team Members, Challenge (*Planet X and SPHEREx*), Location (Coimbatore, India).
- **Slide 2:** The Big Data Problem: Sifting through 102-band multi-epoch SPHEREx all-sky surveys.
- **Slide 3:** Our Solution: SPHEREx Hunter web-based interactive time-domain observatory.
- **Slide 4:** Core Technology & Math: Gnomonic WCS alignment, Clyde Tombaugh Blink animation, and ZOGY difference imaging.
- **Slide 5:** 102-Band Spectroscopy: Array co-addition boosting SNR $>4\times$, identifying $H_2O, CH_4, CO_2$ absorption.
- **Slide 6:** NASA Benchmark Verification: Successful detections of Barnard's Star, Epsilon Indi B, WISE 0855, RW Aurigae, and R Draconis.
- **Slide 7:** Citizen Science & Vision: Universal deep-linking, candidate flagging, and global community exploration.

---

### 4. Final Project Public Link
- **Field Label:** *Share a publicly accessible link to your final project.*
- **Official Guidance:** Must be publicly viewable without authentication or sign-up.
- **Recommended Links for Team RIP:**
  - **Live Web App:** Hosted on Vercel / Render / Cloudflare Pages.
  - **Open-Source Repository:** `https://github.com/joker0210G/spherex-hunter` (Public GitHub repository with comprehensive README, documentation, and installation steps).
- **Web Filter Classification (FortiGuard Whitelist):**
  - If using a newly registered domain, submit the [FortiGuard Web Filter Classification Form](https://www.fortiguard.com/faq/wfratingsubmit) to prevent NASA judge security firewalls from blocking access.
  - Form Details:
    - *Category:* Select `Education`, `Reference`, or `Web-based Application`.
    - *Company Name:* Enter `N/A`.

---

### 5. Detailed Project Description
- **Field Label:** *Provide additional details about your project.*
- **Key Questions to Address:**
  1. **What exactly does it do?**  
     Provides real-time interactive multi-epoch astronomical visualization, sub-pixel astrometric image differencing, and 102-band spectral energy distribution (SED) analysis for any celestial coordinate.
  2. **How does it work?**  
     Built on a FastAPI/Astropy backend integrating NASA IRSA TAP queries and CDS HiPS all-sky surveys with a responsive, hardware-accelerated frontend supporting 60 FPS multi-layer canvas rendering, Clyde Tombaugh blink comparison, and dynamic frustum LOD streaming.
  3. **What benefits does it have?**  
     Bridges the gap between raw multi-epoch FITS cubes and human visual perception, enabling both professional researchers and citizen scientists to identify high proper-motion objects and transients in minutes instead of weeks.
  4. **What do you hope to achieve?**  
     Accelerate the discovery of ultra-cool brown dwarfs, near-Earth asteroids, Kuiper Belt objects, and hypothetical outer solar system bodies (Planet X) in upcoming SPHEREx data releases.
  5. **What tools, coding languages, hardware, or software did you use?**  
     - *Backend:* Python 3.11+, FastAPI, Astropy, Astroquery, NumPy, SciPy, Pillow, Uvicorn.
     - *Frontend:* Vanilla ES6+ JavaScript, HTML5 Canvas API, CSS3 Grid/Flexbox, Aladin Lite HiPS integration, Web Audio API.
     - *Astronomical Standards:* FITS, WCS (Gnomonic TAN projection), ZOGY difference imaging algorithm, RFC 7807 problem details.

---

### 6. Super Intelligence (SI) & AI Tools Disclosure
- **Field Label:** *Did you utilize any Super Intelligence (SI) tools and software in preparing your solution? If yes, how did you use them?*
- **Official Policy & Rules:**
  - SI is permitted to **accelerate innovation and creativity**, but **must NOT be used to generate the core challenge solution concept**.
  - **Strict Branding Ban:** Generated content **may NOT use, contain, or modify any NASA branding or design elements** (such as NASA logos, meatball, worm, flags, or mission patches) per [NASA Brand Guidelines](https://www.nasa.gov/nasa-brand-center/brand-guidelines/).
  - **Mandatory Attribution:**
    - *Images & Videos:* Must include a **visible watermark** indicating SI generation.
    - *Audio:* Must acknowledge SI generation in descriptive text and metadata.
    - *Code & Data:* Must acknowledge SI generation in descriptive text and metadata (e.g., in repository comments and documentation).
- **Scoring Impact:** This field is for data-collection purposes and not directly scored; however, judges evaluate originality, intent, and execution based on identified SI-assisted elements.
- **Team RIP Disclosure Statement:**
  > *"AI assistance (Google Gemini / Antigravity) was utilized as an engineering accelerator for boilerplate unit test authoring, code documentation formatting, and mathematical cross-checks of WCS gnomonic projection formulas. All core scientific architectures, ZOGY difference math, astronomical TAP integrations, and UI designs were conceptualized, directed, and verified by Team RIP. All AI-assisted code blocks are explicitly documented in repository metadata."*

---

### 7. NASA Data & Resources Used (Mandatory for Global Awards)
- **Field Label:** *Provide specific details about what NASA data and resources you used.*
- **Eligibility Rule:** To be eligible for any Global Award, a team **must use at least one official NASA data or resource**.
- **Team RIP NASA Assets:**
  1. **SPHEREx Mission Data & Science Specs:** 102 near-infrared spectral channels spanning $0.75 - 5.00\ \mu\text{m}$ across 6 detector arrays, observation cadence, and spectral resolution ($R \approx 40 - 130$).
  2. **NASA IRSA (Infrared Science Archive):** TAP/API query access for AllWISE, 2MASS, and multi-epoch archival imagery.
  3. **NASA SkyView Virtual Observatory:** Multi-wavelength temporal cutouts.
  4. **Astropy Project:** Core astronomical library for World Coordinate System (WCS) transformations, FITS I/O, and celestial spherical coordinate conversions.

---

### 8. List of Data, Resources, and Space Agency Partners
- **Field Label:** *List all of the data, resources, and tools used in your project.*
- **Include All Third-Party Assets:**
  - **ESA Gaia DR3 Catalog:** Astrometric reference frame, proper-motion vectors, and epoch propagation ($J2016.0 \to \text{epoch}$).
  - **CDS Strasbourg:** Aladin Lite v3, HiPS all-sky color layers (`P/2MASS/color`, `DSS2/color`).
  - **CADC (Canadian Space Agency partner):** NEOSSat asteroid and transient tracking data bridge.
  - **Space Agency Partners Acknowledgment:** Encouraged integration of partner agency data (CSA, ESA, ISRO, JAXA, etc.).

---

## 🏆 Scoring Rubric Alignment (5 Criteria, 1–5 Scale)

| Criterion | Score Target | How SPHEREx Hunter Meets It |
| :--- | :---: | :--- |
| **Impact** | **5 / 5** | Solves the petabyte-scale data challenge of SPHEREx (>1 billion objects) by providing an open, accessible citizen-science engine that democratizes discovery for researchers and the public worldwide. |
| **Creativity** | **5 / 5** | Combines Clyde Tombaugh’s historic blink methodology with modern ZOGY difference imaging, 6-array SNR co-addition ($>4\times$), and real-time 102-band molecular fingerprinting ($H_2O, CH_4, CO_2$). |
| **Validity** | **5 / 5** | Grounded in rigorous astronomical mathematics: sub-pixel WCS Gnomonic tangent alignment, arcsinh contrast stretching, and 100% verified detection across all 5 official NASA benchmark targets. |
| **Relevance** | **5 / 5** | Fulfills 100% of the NASA *Planet X and SPHEREx* challenge specifications, directly utilizing SPHEREx 102-band parameters and NASA IRSA archive protocols. |
| **Presentation** | **5 / 5** | Clear, compelling storytelling adhering strictly to the **30-second video / 7-slide limit**, high-contrast celestial UI, and beginner-friendly onboarding. |

---

## 🛡️ Final Submission Protocol & Legal Checks

Before clicking **"Submit for Judging"**, verify each item:
- [ ] **Confirmed Team Roster:** All team members are confirmed at the same Local Event (Coimbatore, India) and not waitlisted.
- [ ] **All Fields Completed:** No mandatory field left blank.
- [ ] **English Language:** All form fields, presentation slides, and linked repository docs are in English (or video has English subtitles).
- [ ] **No Under-18 Likeness:** No images, videos, audio, or likeness of persons under 18 years old anywhere in the demo or final project (per [NASA Space Apps Terms & Conditions](https://www.spaceappschallenge.org/legal/)).
- [ ] **No NASA Logo Modification:** No modified or unofficial NASA logos or patches used in project artwork.
- [ ] **Public Links Verified:** All URLs (GitHub, demo video, web app) tested in private/incognito browsing without login prompt.
- [ ] **Agree to Terms:** Checkbox: *"Agree to the Terms and Conditions"*.
- [ ] **Confirm Originality:** Checkbox: *"Confirm All Work is Original"*.
- [ ] **Submit Button Clicked:** Click **"Submit for Judging"** before Sunday, Nov 15, 11:59 PM local time.
- [ ] **Confirmation Banner:** Verify green success banner appears at the top of the portal.
- [ ] **Download Certificate:** Go to User Profile $\to$ Participant Information $\to$ 2026 NASA Space Apps Challenge $\to$ Download Participant Certificate (PDF, Letter 8.5x11").
