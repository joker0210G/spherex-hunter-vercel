# 🔭 darkodu - Astro-Data & Backend Lead
> **Name:** darkodu | **Domain:** Astronomy Data, APIs, Astropy & Spectra
> **Assigned Folder:** `/backend` | **Branch:** `darkodu/astro-backend`
> **Your Memory File:** `[[07 - Team Memory & Sync/darkodu_memory]]`

---

## 🌟 What You Own
You are in charge of getting the real space telescope data! Whenever someone enters coordinates like `08h55m10.8s, -07d14m42.5s` (WISE 0855), your backend fetches the images and calculates the 102-band infrared spectrum.

---

## 🚀 Tasks (Give These Exactly to Antigravity on Your PC)

### Task 1: Initialize FastAPI Backend
> **Prompt for Antigravity:**
> *"Antigravity, I am darkodu. Set up my git branch darkodu/astro-backend. Create a Python FastAPI backend in the /backend folder with requirements.txt (fastapi, uvicorn, astropy, astroquery, pillow, numpy). Write an endpoint GET /api/health that returns status OK."*

### Task 2: Build the Astronomical Cutout Engine
> **Prompt for Antigravity:**
> *"Antigravity, write an Astropy cutout service in /backend/services/cutout.py that accepts RA and Dec coordinates, queries astronomical archives (using Astroquery SkyView for WISE/SPHEREx), applies ZScale / Asinh stretching, and returns multi-epoch PNG images."*

### Task 3: Build the 102-Band Spectrum Generator
> **Prompt for Antigravity:**
> *"Antigravity, create an endpoint GET /api/spectrum that accepts coordinates and returns the 102 near-infrared wavelengths (0.75 to 5.0 microns) with simulated flux and flags for water ice and CO2 absorption features."*

### Task 4: Sync Your Progress
> **Prompt for Antigravity:**
> *"Antigravity, commit my work to git with a clear message, push to my branch darkodu/astro-backend, and update my memory file in 07 - Team Memory & Sync/darkodu_memory.md!"*
