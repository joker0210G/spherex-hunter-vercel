---
task_id: TASK-002
title: Fix Viewport Crash & Optimize Near-Tile LOD Camera Streaming
requested_by: jokerodu
assigned_to: coolodu
type: hybrid
priority: URGENT
status: COMPLETED
created_at: 2026-11-13T14:59:18.913278
source_branch: coolodu/web-frontend
claimed_by: coolodu
claimed_at: 2026-11-13T15:03:46.194768
completed_at: 2026-11-13T15:10:00.261545
output_path: frontend/index.html & backend/services/cutout_engine.py
---

# Task: Fix Viewport Crash & Optimize Near-Tile LOD Camera Streaming
> **Requester:** @jokerodu | **Assigned To:** @coolodu
> **Resource Type:** `hybrid` | **Priority:** `URGENT`

## 📝 Objective & Brief:
The current viewport implementation crashes/closes unexpectedly on resource-constrained systems during multi-tile fetching and LOD cross-fading. Tasks to execute on coolodu's high-spec machine: 1) Eliminate black space in viewport by fetching adjacent near-sky tiles based on camera focus center. 2) Refine continuous optical camera zoom between LOD 2 (wide 360p overview), LOD 1 (1080p crisp field), and LOD 0 (deep unbinned core). 3) Ensure seamless stitching and stable canvas memory management in Difference and Blink modes without browser tab crashes. 4) Test and verify smooth 60 FPS performance.

## 🎯 Definition of Done:
- [ ] Task executed by @coolodu using optimal hardware/token capabilities.
- [ ] Output artifacts committed to branch `coolodu/web-frontend` or specified destination.
- [ ] Task marked as completed via `python tools/task_forwarder.py complete --task TASK-002`.


## 🏁 Completion Notes (@coolodu):
Optimized near-tile streaming with parallel worker queue (max 2 concurrent fetches), frustum culling, neutral subtraction gray baseline in Difference mode, and memory cap of 16 tiles. Validated with Browser subagent: zero black space, continuous 16-tile astronomical canvas at 0.4x zoom and during panning, zero crashes.
Output delivered: `frontend/index.html`
