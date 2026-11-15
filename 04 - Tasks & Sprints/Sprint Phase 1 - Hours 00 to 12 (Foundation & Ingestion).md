# 🚀 Sprint Phase 1: Foundation & Data Ingestion (Hours 00 – 12)
> **Goal:** Working repository, environment setup, and verified data retrieval for the 5 benchmark targets.

---

## 📋 Phase 1 Action Items

### 1. General & DevOps Setup (Hours 00 – 02)
- [ ] Initialize Git repository with proper `.gitignore` (Python, Node, FITS).
- [ ] Create frontend directory (`/frontend`) with Vite React + Tailwind.
- [ ] Create backend directory (`/backend`) with FastAPI + Poetry or `requirements.txt`.
- [ ] Verify local run: `npm run dev` and `uvicorn main:app --reload`.

### 2. Backend & Astronomy Data (Hours 02 – 08)
- [ ] Implement `SkyCoord` parser in Python supporting both sexagesimal and decimal coordinates.
- [ ] Write cutout fetcher script using `astroquery.skyview` or IRSA API.
- [ ] Download and stage data for the 5 benchmark targets:
  - Barnard's Star
  - Epsilon Indi B
  - WISE 0855
  - RW Aurigae
  - R Draconis
- [ ] Implement ZScale / Asinh image stretching to convert raw 32-bit FITS arrays to viewable PNGs.

### 3. Frontend Scaffolding (Hours 04 – 12)
- [ ] Build Header with NASA Space Apps 2026 branding & Team RIP credits.
- [ ] Build Coordinate Search Bar with validation and "Locate" button.
- [ ] Add 5 Quick-Preset Buttons for the test targets.
- [ ] Scaffold HTML5 Canvas viewer component for displaying loaded images.

---

## 🎯 Phase 1 Gate Check
- [ ] Can a user click "WISE 0855" on the frontend and see an image appear on screen?
- **Status:** In Progress
