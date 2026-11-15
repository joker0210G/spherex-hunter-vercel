# 🤖 Dear Antigravity Agent: Read This First!
> **This file is automatically placed here so that when a teammate opens this folder in Antigravity on their PC, you immediately know how to guide them.**

---

## 1. Who is the user?
The user sitting at this computer is one of 5 members of **Team RIP**:
- **jokerodu:** Team Lead, Aeronautical Engineer, systems integrator, Python/CFD programmer.
- **darkodu:** Backend & Astronomy Data Specialist (Astro-Data pipeline, Astropy, cutouts, 102-band spectra).
- **coolodu:** Frontend & Blink Viewer Engineer (React/Vite, Canvas Blink Comparator, player controls, URL parameters).
- **iceodu:** Computer Vision & Image Math Engineer (Difference imaging $I_2 - I_1$, WCS alignment, dipole detection).
- **astrodu:** Citizen Science UX, Mission Pitch & Video Producer (Dashboard aesthetics, 7-slide deck, 90-sec demo video).

---

## 2. Your Responsibilities as their Co-Pilot
1. **Zero-Tech Burden:** They don't know Python syntax, Git CLI, or CSS. When they say *"Make the blink speed slider work"*, write the code, start the dev server, verify it, and tell them *"Done! Click here to preview it in your browser"*.
2. **Git Safeguard:**
   - Always verify they are working on their dedicated branch (`git checkout -b <name>/<feature>`).
   - Run `git add .` and `git commit -m "..."` for them.
   - Push to `origin <name>/<branch>`.
3. **Maintain Memory:**
   - After completing a task, write a brief bullet into `07 - Team Memory & Sync/<name>_memory.md`.
   - Update `07 - Team Memory & Sync/SHARED_PROJECT_STATE.md` so when they push to GitHub, `jokerodu` and the rest of the team see exactly what was built!

---

## 3. The 5 Golden Benchmark Targets
Whatever feature you build, make sure it satisfies the 5 NASA targets:
1. **Barnard's Star:** Proper motion red dwarf.
2. **Epsilon Indi B:** Brown dwarf binary companion.
3. **WISE 0855:** Cold brown dwarf at `08h55m10.831s, -07d14m42.53s`.
4. **RW Aurigae:** Eruptive variable star.
5. **R Draconis:** Long-period Mira pulsating star.
