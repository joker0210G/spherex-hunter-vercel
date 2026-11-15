---
task_id: TASK-007
title: Improve UI/UX Readability & Typography Scale: Enlarge Microscopic 9px/10px Text for Researchers & Newbies
requested_by: jokerodu
assigned_to: coolodu
type: token_heavy
priority: HIGH
status: PENDING
created_at: 2026-11-15T11:31:54.316754
source_branch: coolodu/web-frontend
---

# Task: Improve UI/UX Readability & Typography Scale: Enlarge Microscopic 9px/10px Text for Researchers & Newbies
> **Requester:** @jokerodu | **Assigned To:** @coolodu
> **Resource Type:** `token_heavy` | **Priority:** `HIGH`

## 📝 Objective & Brief:
Refactor and enlarge the microscopic typography, compact control bars, and low-contrast labels in the SPHEREx spectral panel and control bars (specifically the 102-Band array selector, wavelength stepper, notice banner, and molecular reference sidebar) so that citizen science newcomers can comfortably navigate without cognitive overload, and scientific researchers can easily read precise wavelengths, fluxes, and observational metadata.

### 🔍 Problem Description & User Feedback:
- As reported in citizen testing and UI inspection (see attached screenshot):
  1. **Array Selector Buttons (`A1`–`A6`):** Rendered in tiny `text-[10px]` with cramped padding (`px-2 py-0.5`).
  2. **Spectral Wavelength Stepper & Flux Badge (`#chanDisplay`, `#chanFluxBadge`):** Microscopic text with tiny `text-[9px]` flux badges (`1.00 rel` / `836.05 μJy`), making precise physical readings difficult.
  3. **Non-Simultaneous Observation Notice (`#spectrumNonSimultaneousNotice`):** Critical observational disclaimer for variable stars (`RW Aurigae`, `R Draconis`) is compressed into a 10px amber box (`text-[10px] text-amber-300/90`), making scientific honesty and provenance difficult to read.
  4. **Explainer Trigger (`#btnOpenBandScience`):** Microscopic `text-[10px]` button that blends into the background.
  5. **Molecular Absorption Reference Sidebar:** Microscopic `text-[9px]` table with cramped chemical formula labels (`H₂O`, `CO₂`, `CH₄`).

### 🛠️ Scope of Work (`frontend/index.html` & CSS):
1. **Typography & Scale Modernization:**
   - Upgrade base font sizes from 9px/10px to comfortable, accessible scales (minimum 11px–12px for badges/secondary labels, 12px–13px for primary telemetry and buttons).
   - Enhance font weights (`font-semibold` / `font-mono`) and contrast ratios for dark theme legibility.
2. **Layout & Touch/Click Target Ergonomics:**
   - Provide adequate vertical/horizontal padding (`py-1.5 px-3` rather than `py-0.5 px-1.5`) for array tabs and channel navigation.
   - Ensure responsive wrapping or flexible flexbox arrangement so the notice banner does not compress the wavelength slider on narrow viewports.
3. **Notice Banner Clarity:**
   - Improve presentation of the variable star non-simultaneous disclaimer with clear icon hierarchy and readable prose.
4. **Molecular Reference Table:**
   - Increase row spacing and text size to `text-xs` (12px) for effortless legibility by astrophysicists inspecting absorption features.

## 🎯 Definition of Done:
- [ ] All controls and text in the spectral bar and molecular reference sidebar use $\ge 11\text{px}$–$13\text{px}$ sizing.
- [ ] High contrast against dark theme space background meeting WCAG AA legibility standards.
- [ ] Zero regression in DOM IDs (`chanDisplay`, `chanFluxBadge`, `chanSlider`, `chanPrev`, `chanNext`, `btnOpenBandScience`, `spectrumNonSimultaneousNotice`) so JS hooks continue working.
- [ ] All automated UI contract tests in `tests/test_ui_contract.py` pass green.
- [ ] Task executed by @coolodu on branch `coolodu/web-frontend`.
- [ ] Task marked as completed via `python tools/task_forwarder.py complete --task TASK-007`.
