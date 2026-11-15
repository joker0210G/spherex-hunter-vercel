---
task_id: TASK-004
title: Analyze & Fix Mirrored Sky Reflection: Fetch Real Astronomical Surrounding Fields
requested_by: jokerodu
assigned_to: darkodu
type: compute_heavy
priority: URGENT
status: COMPLETED
created_at: 2026-11-13T15:41:49.282602
source_branch: darkodu/astro-backend
completed_at: 2026-11-13T15:50:23.583512
output_path: backend/services/cutout_engine.py
---

# Task: Analyze & Fix Mirrored Sky Reflection: Fetch Real Astronomical Surrounding Fields
> **Requester:** @jokerodu | **Assigned To:** @darkodu
> **Resource Type:** `compute_heavy` | **Priority:** `URGENT`

## 📝 Objective & Brief:
The user identified that adjacent near-tiles in the viewport appear mirrored like a kaleidoscope instead of displaying authentic adjacent sky. Technical cause: load_real_fits_cutout in cutout_engine.py pads the central benchmark FITS file with mode='symmetric'/'reflect'. Whenever an offset tile is requested beyond the core bounds, it slices into the mirror-reflected array. Required Fix: 1) Analyze why the mirror reflection occurs. 2) When offset coordinates (center_ra, center_dec) exceed the authentic coverage of the benchmark FITS file, query the genuine surrounding astronomical field via fetch_live_irsa_fits or coordinate-seeded unique field generator. 3) Completely eliminate mode='symmetric'/'reflect' duplication so every adjacent sky tile displays authentic, unmirrored celestial coordinates.

## 🎯 Definition of Done:
- [ ] Task executed by @darkodu using optimal hardware/token capabilities.
- [ ] Output artifacts committed to branch `darkodu/astro-backend` or specified destination.
- [ ] Task marked as completed via `python tools/task_forwarder.py complete --task TASK-004`.


## 🏁 Completion Notes (@darkodu):
Analyzed and eliminated mirrored sky reflection: When offset queries exceed authentic benchmark FITS bounds (>3.4 arcmin), cutout_engine queries authentic surrounding fields via NASA IRSA or coordinate-seeded unique fields. Removed symmetric reflection padding and replaced with median cosmic sky flux.
Output delivered: `backend/services/cutout_engine.py`
