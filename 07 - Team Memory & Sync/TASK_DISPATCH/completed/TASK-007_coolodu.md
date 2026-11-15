---
id: TASK-007
title: "Improve UI/UX Readability & Typography Scale: Enlarge Microscopic 9px/10px Text for Researchers & Newbies"
from: jokerodu
to: coolodu
type: token_heavy
priority: HIGH
status: COMPLETED
branch: coolodu/web-frontend
github_issue: 41
github_url: https://github.com/joker0210G/spherex-hunter/issues/41
created_at: 2026-11-15T11:45:00
completed_at: 2026-11-15T11:53:30.770520
output_path: frontend/index.html, tests/test_ui_contract.py
---

## Objective
Refactor microscopic typography (`text-[9px]` & `text-[10px]`) in the SPHEREx spectral control bar (`#chanDisplay`, `#chanFluxBadge`, `#chanSlider`, `#chanPrev`, `#chanNext`, `.array-tab`, `#spectrumNonSimultaneousNotice`, `#btnOpenBandScience`) and the molecular absorption reference table in `frontend/index.html` to comfortable, accessible scales ($\ge 11\text{px}$–$13\text{px}$) with comfortable click padding and WCAG AA contrast.

## Acceptance Criteria
1. `#chanDisplay` enlarged to `text-sm font-bold min-w-[220px]` (14px) for clear channel and wavelength readouts.
2. `#chanFluxBadge` enlarged to `text-xs font-mono font-bold px-2.5 py-1` with solid contrast badge background.
3. Navigation steppers `#chanPrev` and `#chanNext` enlarged to `w-8 h-8 rounded-lg text-base font-bold` for comfortable touch and click targets.
4. SPHEREx 6-Array selector buttons (`.array-tab`) styled with high-contrast text and crisp padding.
5. Observation honesty notice (`#spectrumNonSimultaneousNotice`) enlarged from `text-[11px]` to `text-xs font-medium` with comfortable padding and WCAG AA contrast.
6. 102-Band Science trigger (`#btnOpenBandScience`) styled with `text-xs font-bold` and comfortable click padding.
7. Molecular reference sidebar enlarged from microscopic `text-[9px]` to `text-xs font-mono`, width expanded to `w-64`, with enlarged signature dots (`w-2.5 h-2.5`), high-contrast colors, and bold wavelength readouts.
8. Time step controller buttons in viewport HUD updated to `text-xs font-semibold` across both static HTML and JS state toggle handlers.
9. Contract tests added in `tests/test_ui_contract.py` validating all typography scales and element dimensions.
10. All automated unit and contract tests pass 100% green.
