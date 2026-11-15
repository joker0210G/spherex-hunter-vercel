# 🏗️ System Architecture Overview
> **Project:** SPHEREx Hunter - Time-Domain Infrared Sky Browser

```mermaid
flowchart TD
    subgraph Client["Web Frontend (React / Vite / Tailwind)"]
        SearchBar["Coordinate / Target Search Bar
(Supports Sexagesimal & Decimal)"]
        PresetBar["Preset Buttons
(Barnard, WISE 0855, etc.)"]
        BlinkView["Interactive Blink Viewer
(Canvas / WebGL Engine)"]
        DiffToggle["Difference Image Toggle
(I_epoch2 - I_epoch1)"]
        SpectraModal["102-Band Spectral Plot
(Recharts SED Viewer)"]
        ShareBtn["URL Deep-Link Generator
(?ra=...&dec=...)"]
    end

    subgraph Server["Backend API (FastAPI / Python)"]
        CoordResolver["Coordinate Standardizer (Astropy SkyCoord)"]
        Cache["LRU Image & Cutout Cache"]
        CutoutEngine["Cutout & Reprojection Engine
(reproject_interp + WCS)"]
        CoaddEngine["Detector Array Co-addition
(6 Arrays / 102 Bands)"]
        DiffEngine["Sub-pixel Difference Generator"]
    end

    subgraph Archives["External Astronomical Archives"]
        SPHEREx["SPHEREx Mock / Release Archive
(IRSA IPAC TAP)"]
        WISE["WISE / NEOWISE Catalog
(IRSA 3.4 / 4.6 μm)"]
        Gaia["Gaia DR3 Catalog
(Proper Motion Vectors)"]
        CDS["CDS Strasbourg Aladin / HiPS"]
    end

    SearchBar --> CoordResolver
    PresetBar --> CoordResolver
    CoordResolver --> CutoutEngine
    CutoutEngine --> Cache
    CutoutEngine --> SPHEREx
    CutoutEngine --> WISE
    CutoutEngine --> Gaia
    CutoutEngine --> CoaddEngine --> DiffEngine
    DiffEngine --> BlinkView
    CoaddEngine --> SpectraModal
    BlinkView --> DiffToggle
    ShareBtn --> SearchBar
```

---

## 🔄 Core Data Flow
1. **Input Phase:** The user enters coordinates or clicks a preset button.
2. **Resolution Phase:** Astropy standardizes the input to ICRS degrees and queries available epoch tiles.
3. **Processing Phase:** Backend reprojects images to a uniform pixel grid, applies Asinh/ZScale stretch, and calculates image difference.
4. **Rendering Phase:** Frontend receives optimized epoch PNGs and renders them at 1-10 FPS with interactive controls.
5. **Deep Dive Phase:** Clicking any pixel queries the 102-channel flux array, graphing the object's infrared SED.
