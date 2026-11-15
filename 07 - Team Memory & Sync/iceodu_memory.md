# 🧠 Memory Log: iceodu (Image Math & AI Lead)
> **Role:** Difference Imaging, WCS Alignment & Anomaly Detection
> **Branch:** `iceodu/image-math-ai`

## Personal Status:
- **Current Task:** Completed deep deconstruction and vault synchronization for the official NASA Space Apps Project Submission Guide and Form Field Instructions (`https://www.spaceappschallenge.org/resources/project-submission-guide/#project-page-form-field-instructions`).
- **Next Task:** Support final package verification and submission readiness.
- **Blockers:** None currently.

## Assigned GitHub Tasks:
- [x] **[#15] [ASTROMETRY] Fix Gaia DR3 Overlay Projection Mismatch & FOV Scale Discrepancy** (https://github.com/joker0210G/spherex-hunter/issues/15) — **CLOSED**
  - Anchored `getActivePixelsPerArcmin()` dynamically to active image/camera FOV (`getActiveFovArcmin()`).
  - Implemented standard WCS Gnomonic Tangent projection (`projectSkyToTangentialArcmin`) matching east-left / north-up canvas axes.
  - Propagated Gaia DR3 coordinates from epoch $J2016.0$ to active observation epoch year (`propagateGaiaEpoch` + `getActiveObservationEpochYear`), keeping reticles aligned across multi-epoch blink morphing.

## Completed Tasks:
- [x] **Deep Deconstruction of Official NASA Space Apps Submission Guide & Field Instructions:**
  - Analyzed official submission rules, portal field mechanics, and all embedded hyperlinks:
    - *NASA Brand Center Guidelines:* strict prohibition on modifying NASA logos, worms, flags, and mission patches in generated content.
    - *2026 Judging & Awards Guide:* 5 criteria (Impact, Creativity, Validity, Relevance, Presentation) evaluated on a 1–5 scale.
    - *FortiGuard Web Filter Classification:* whitelisting procedure for custom domains to avoid firewall blocks during judging.
    - *Super Intelligence (SI) Policy:* mandatory watermarks on media and descriptive text/metadata attribution for code, data, and audio.
    - *Demo Limitations:* strictly enforced **30-second limit for videos** and **7-slide limit for decks** (exceeding causes disqualification from Global Judging).
    - *Deadlines & Submission Windows:* Saturday Nov 14 9:00 AM to Sunday Nov 15 11:59 PM local event time, edit locking, and participant certificate download.
  - Authored `06 - Deliverables & Submission/Official NASA Space Apps Submission Guide & Field Instructions.md`.
  - Updated `06 - Deliverables & Submission/NASA Submission Requirements & Checklist.md`.
  - Re-anchored `06 - Deliverables & Submission/Demo Video Script & Storyboard (30-sec to 3-min).md` strictly to the official 30-second NASA format (`[0:00]`, `[0:02]`, `[0:05]`, `[0:10]`, `[0:20-0:30]`).
  - Updated `06 - Deliverables & Submission/Winning Project Pitch Deck Outline.md` strictly adhering to the 7-slide rule.
- [x] Synchronized repository branches and verified clean status.
