---
task_id: TASK-003
title: Fix Backend Near-Tile Offset Extraction & Robust Boundary Padding
requested_by: jokerodu
assigned_to: darkodu
type: compute_heavy
priority: URGENT
status: COMPLETED
created_at: 2026-11-13T15:29:15.330903
source_branch: darkodu/astro-backend
claimed_by: darkodu
claimed_at: 2026-11-13T15:29:30.042121
completed_at: 2026-11-13T15:31:36.256068
output_path: backend/services/cutout_engine.py
---

# Task: Fix Backend Near-Tile Offset Extraction & Robust Boundary Padding
> **Requester:** @jokerodu | **Assigned To:** @darkodu
> **Resource Type:** `compute_heavy` | **Priority:** `URGENT`

## 📝 Objective & Brief:
The backend load_real_fits_cutout in cutout_engine.py throws ZeroDivisionError on offset celestial coordinates when fetching near-sky tiles around target centers because slicing exceeds pad boundaries. Fix: 1) Dynamically compute celestial coordinate offsets safely. 2) Implement robust array padding (or seamless coordinate wrapping) so any offset RA/Dec query returns valid FITS cutout arrays and Alard-Lupton difference subtraction without crashing. 3) Verify that offset queries return (dim, dim) valid float matrices.

## 🎯 Definition of Done:
- [ ] Task executed by @darkodu using optimal hardware/token capabilities.
- [ ] Output artifacts committed to branch `darkodu/astro-backend` or specified destination.
- [ ] Task marked as completed via `python tools/task_forwarder.py complete --task TASK-003`.


## 🏁 Completion Notes (@darkodu):
Fixed ZeroDivisionError in load_real_fits_cutout by implementing dynamic symmetric padding based on offset coordinates. All LODs and arbitrary offset coordinates now return valid (dim, dim) FITS cutouts and difference images.
Output delivered: `backend/services/cutout_engine.py`
