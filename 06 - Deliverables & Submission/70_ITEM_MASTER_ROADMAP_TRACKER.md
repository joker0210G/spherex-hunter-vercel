# 🛰️ SPHEREx Hunter | 70-Item NASA Space Apps Master Evaluation Tracker
> **NASA Space Apps Challenge 2026** | **Team:** RIP (Coimbatore, India)  
> **Challenge:** Planet X and SPHEREx (Astrophysics / Planetary Defense / Citizen Science)  
> **Status:** All 70 Checklist Items Implemented & Verified (100% Coverage)  
> **Repository:** [joker0210G/spherex-hunter](https://github.com/joker0210G/spherex-hunter) | **Working Branch:** `coolodu/web-frontend`

---

## 📊 Executive Summary Dashboard

| Phase | Scope & Title | Items | Implementation Status | Automated Verification |
| :--- | :--- | :---: | :---: | :---: |
| **Phase 0** | **Data Foundation & Archive Integrity** | #17–#24 | 🟢 100% Operational | NASA IRSA TAP, SkyView, HiPS Cube, `test_data_acquisition_and_ui.py` |
| **Phase 1** | **Coordinate Search & Input Parsing** | #9–#16 | 🟢 100% Operational | Astropy `SkyCoord`, Decimal/Sexagesimal, `test_validation.py` |
| **Phase 2** | **Image Viewer, Scaling & Metadata** | #25–#32 | 🟢 100% Operational | HTML5 Canvas 60 FPS, WebGL, Asinh/ZScale, `test_viewport_overhaul_v2.py` |
| **Phase 3** | **Time Sequence & Temporal Playback** | #33–#40 | 🟢 100% Operational | Clyde Tombaugh Blink, Morph Fader, 0.5–6.0 FPS, `test_ui_contract.py` |
| **Phase 4** | **Movement, Photometry & Difference** | #41–#54 | 🟢 100% Operational | Astropy WCS Reproject, ZOGY Math, Gaia Space Motion, `test_differencing.py` |
| **Phase 5** | **102-Band SED & Molecular Features** | #55–#60 | 🟢 100% Operational | 6 Arrays A1–A6, Chart.js, 102-Band HiPS Slicing, `test_bands_spectrum.py` |
| **Phase 6** | **5 NASA Benchmark Target Validations** | #61–#67 | 🟢 100% Verified | Barnard, Epsilon Indi, WISE 0855, RW Aur, R Dra in `test_golden_suite.py` |
| **Phase 7** | **Polish, Onboarding & Deliverables** | #1–#8, #68–#70 | 🟢 100% Operational | Cosmic Quick-Start, 7-Slide Deck, Video Script, 32 Contract Tests |
| **Gate** | **Pre-Submission Warning Signs Audit** | Gate 1–5 | 🟢 100% Passed | Zero fake data, WCS alignment, Calibrated flux, All 5 targets verified |

---

## 🔬 Detailed 70-Item Checklist Audit Matrix

### 🟢 Phase 0: Data Foundation (Items #17–#24)
*Everything else depends on this; handles primary scientific integrity and archive veracity.*

| # | Item Requirement | SPHEREx Hunter Implementation | Verification Evidence | Status |
| :-: | :--- | :--- | :--- | :-: |
| **17** | **Pull real SPHEREx data from public archive** | Connected to authentic **NASA IRSA IPAC TAP** (`https://irsa.ipac.caltech.edu/TAP`), NASA SkyView Virtual Observatory, and official **IRSA SPHEREx DR1 HiPS all-sky cube** (`https://irsa.ipac.caltech.edu/data/hips/SPHEREx/spherex_allsky_cube/`). | `backend/services/cutout_engine.py`, `backend/services/catalog_engine.py`, `tests/test_aladin_hips_e2e.py` | ✅ **DONE** |
| **18** | **Document source & access method in app & README** | Comprehensive data citations in `README.md`, `03 - SPHEREx Instrument & Data Primer.md`, and in-app **Resources Codex Modal** (`/api/v1/resources/codex`) detailing TAP queries and HiPS endpoints. | `README.md`, `frontend/index.html` (`#resourcesModal`), `backend/main.py` (`get_resources_codex`) | ✅ **DONE** |
| **19** | **Return observation date/time with every record** | Standardized JSON bundle schema attaches ISO `date_obs` (`YYYY-MM-DD`), `mjd`, and `dec_year` to every epoch record. | `backend/services/cutout_engine.py`, validated in `tests/test_scene_and_metadata.py` | ✅ **DONE** |
| **20** | **Display timestamp on active frame at all times** | Viewport telemetry HUD chip (`#vpFrameLabel`) and time-step indicator (`#timeStepHUD`) display the active observation date in real time. | `frontend/index.html` (`#vpFrameLabel`), verified in `tests/test_ui_contract.py` | ✅ **DONE** |
| **21** | **Label sample / mock data visibly; never mix silently** | Distinct badges for synthetic/sample fallbacks (`/app/fixtures/hips_spherex_dr1_sample`); prominent DR1 HiPS mosaic warning: *"DR1 all-sky mosaic: context only (co-add blurs movers)"*. | `frontend/index.html` (`#aladinContextBar`), `backend/main.py` | ✅ **DONE** |
| **22** | **Handle empty results with clear user explanation** | Coordinates in unobserved sky regions return structured HTTP 404 with `#noObsBanner` and user-friendly explanation rather than blank canvas. | `backend/main.py` (`fetch_real_cutout`), `tests/test_ui_contract.py` (`test_issue_39`) | ✅ **DONE** |
| **23** | **Provide retry option on network or archive failure** | Circuit breaker telemetry (`backend/services/catalog_engine.py`) with automatic fallback to mirrored SkyView endpoints and UI retry trigger toast (`#alertToast`). | `backend/services/catalog_engine.py`, `tests/test_golden_suite.py` | ✅ **DONE** |
| **24** | **Preserve raw FITS metadata & provenance** | Returns FITS header cards (`TELESCOP`, `INSTRUME`, `FILTER`, `WCSAXES`, `CRVAL1`, `CRVAL2`, `CDELT1`, `CDELT2`, `BUNIT`) in the REST payload. | `backend/services/cutout_engine.py`, `backend/models_v1.py` | ✅ **DONE** |

---

### 🟢 Phase 1: Coordinate Search (Items #9–#16)
*Precision astronomical input parsing and validation.*

| # | Item Requirement | SPHEREx Hunter Implementation | Verification Evidence | Status |
| :-: | :--- | :--- | :--- | :-: |
| **9** | **Accept Decimal Degree RA/Dec inputs** | Native support for decimal degrees (e.g., `133.79513, -7.24515`) via Astropy `SkyCoord(ra, dec, unit='deg', frame='icrs')`. | `backend/services/cutout_engine.py`, `tests/test_validation.py` | ✅ **DONE** |
| **10** | **Accept Sexagesimal HMS/DMS coordinate inputs** | Native parsing for string sexagesimal formats (e.g. `08h 55m 10.83s, -07d 14m 42.5s` and `17:57:48.5 +04:41:36.2`). | `tests/test_golden_suite.py` (`test_sexagesimal_and_decimal_parsing`), `test_data_acquisition_and_ui.py` | ✅ **DONE** |
| **11** | **State accepted coordinate formats clearly in UI** | Input fields feature placeholder text and coordinate validation micro-hints (`#raValidationHint`: `0° to 360° or 00h 00m 00s`, `#decValidationHint`: `-90° to +90°`). | `frontend/index.html` (`#raValidationHint`, `#decValidationHint`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **12** | **Validate coordinate range with helpful errors** | Server-side HTTP 400 validation and client-side input clamping guarding against $\text{RA} < 0$, $\text{RA} \ge 360$, and $|\text{Dec}| > 90$. | `scripts/test_data_acquisition_and_ui.py` (5/5 edge cases pass) | ✅ **DONE** |
| **13** | **Search radius / Field-of-View (FOV) control** | Interactive FOV slider and numerical input ranging from $1.0'$ to $15.0'$ with real-time arcminute badge (`#fovInput`, `#fovSlider`). | `frontend/index.html` (`#fovSlider`), `backend/main.py` FOV clamp | ✅ **DONE** |
| **14** | **Display searched coordinates beside results** | Target coordinate readout permanently rendered in viewport HUD header (`#vpTargetName`, `#vpCoords`) in decimal degrees and sexagesimal. | `frontend/index.html` (`#vpCoords`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **15** | **Repeatable searches without full page reload** | Asynchronous AJAX/Fetch lifecycle fetches new cutouts and re-renders canvas dynamically without reload. | `frontend/index.html` (`loadSkyCutout()`), `tests/test_continuous_viewport_e2e.py` | ✅ **DONE** |
| **16** | **One-click Benchmark Target Presets** | Instant slew preset buttons for all 5 mandatory targets (`#btnPresetWise0855`, `#btnPresetBarnard`, `#btnPresetEpsIndi`, `#btnPresetRwAur`, `#btnPresetRDraconis`). | `frontend/index.html` (`#presetTargetsContainer`), `tests/test_ui_contract.py` | ✅ **DONE** |

---

### 🟢 Phase 2: Image Viewer & Metadata (Items #25–#32)
*Display fidelity, contrast controls, and physical scaling.*

| # | Item Requirement | SPHEREx Hunter Implementation | Verification Evidence | Status |
| :-: | :--- | :--- | :--- | :-: |
| **25** | **Display images with attached date, band & wavelength** | Every rendered canvas layer renders active survey tag (2MASS, AllWISE, SPHEREx A6), filter band, and central $\mu\text{m}$. | `frontend/index.html` (`#vpFrameLabel`, `#vpFilterBadge`), `backend/services/cutout_engine.py` | ✅ **DONE** |
| **26** | **Smooth hardware-accelerated pan & drag** | 60 FPS HTML5 Canvas with pointer tracking, mouse dragging, and multi-touch translation support. | `frontend/index.html` (`viewportCanvas`), `tests/test_viewport_overhaul.py` | ✅ **DONE** |
| **27** | **Interactive zoom with cursor centering** | Logarithmic zoom slider, cursor-centered mouse wheel scaling, and quick reset (`#btnZoomIn`, `#btnZoomOut`, `#btnZoomReset`). | `frontend/index.html` (`#vpZoomSlider`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **28** | **Brightness & contrast stretch engine** | Multiple astronomical stretch algorithms: Asinh (`arcsinh`), ZScale, Linear, and MinMax, computed via Astropy / NumPy. | `backend/services/cutout_engine.py` (`apply_locked_asinh_stretch`), `tests/test_preprocessing.py` | ✅ **DONE** |
| **29** | **Astronomical false-color colormaps (LUTs)** | 4 selectable contrast palettes: Inferno (high dynamic range), Viridis (perceptually uniform), Greyscale (classical optical), and Cool-Warm (difference mode). | `frontend/index.html` (`#colormapSelect`), `backend/services/cutout_engine.py` | ✅ **DONE** |
| **30** | **State physical units and scaling explicitly** | Viewport HUD displays physical device-pixel scale (`″/dev_px`) and distinguishes display-stretched counts from calibrated flux. | `frontend/index.html` (`#vpDeviceScale`, `#chanFluxBadge`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **31** | **Surface detector pixel pitch comparison** | Dual LOD threshold badges comparing HiPS Order 5 ($12.88''/\text{px}$) against SPHEREx native detector pitch ($6.15''/\text{px}$). | `frontend/index.html` (`#lodBadgeHips`, `#lodBadgeNative`), `tests/test_viewport_overhaul_v2.py` | ✅ **DONE** |
| **32** | **Raw 1:1 Detector Pixels inspection mode** | Dedicated toggle for nearest-neighbor interpolation (`gl.NEAREST` / `image-rendering: pixelated`) showing authentic pixel boundaries. | `frontend/index.html` (`#btnRawPixelMode`), `tests/test_viewport_overhaul_v2.py` | ✅ **DONE** |

---

### 🟢 Phase 3: Time Sequence & Temporal Playback (Items #33–#40)
*Clyde Tombaugh blink comparison and multi-epoch progression.*

| # | Item Requirement | SPHEREx Hunter Implementation | Verification Evidence | Status |
| :-: | :--- | :--- | :--- | :-: |
| **33** | **Sort observations chronologically by default** | Auto-sorts temporal baseline epochs chronologically by `MJD` (e.g. 2MASS 1999 $\rightarrow$ WISE 2010 $\rightarrow$ SPHEREx 2025/2026). | `backend/services/cutout_engine.py`, `tests/test_scene_and_metadata.py` | ✅ **DONE** |
| **34** | **Play / Pause automatic blink cycling** | Clyde Tombaugh Blink comparator toggle button (`#btnPlayBlink`) with animated state indication. | `frontend/index.html` (`#btnPlayBlink`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **35** | **Previous & Next manual frame steppers** | Dedicated keyboard and UI stepper buttons (`#btnHudStepPrev`, `#btnHudStepNext`) allowing single-step epoch toggling. | `frontend/index.html` (`#btnHudStepPrev`, `#btnHudStepNext`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **36** | **Adjustable blink playback speed** | Variable blink frequency slider ranging from $0.5$ FPS to $6.0$ FPS with live indicator badge (`#speedSlider`, `#speedLabel`). | `frontend/index.html` (`#speedSlider`, `#speedLabel`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **37** | **Smooth Morph (cross-fade) blend slider** | Continuous opacity transition slider (`#morphSlider`) enabling users to blend slowly between historical and modern frames to track trajectories. | `frontend/index.html` (`#morphSlider`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **38** | **Keyboard navigation shortcuts** | Arrow keys (`Left`/`Right`) step frames/channels; `Spacebar` toggles play/pause blink; `D` toggles difference mode. | `frontend/index.html` (keydown listener), `tests/test_ui_contract.py` | ✅ **DONE** |
| **39** | **Continuous time-step HUD indicator** | Compact pill badge displaying active step index (`1 / 2`), survey origin, and observation year. | `frontend/index.html` (`#viewportTimeStepHUD`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **40** | **Multi-tier tile caching (L0 RAM / L1 IndexedDB)** | Scoped multi-tier cache storing decoded textures with micro-degree quantized spatial keys, HTTP 304 ETag support, and idle prefetching. | `frontend/index.html` (`spherex_tile_store`), `tests/test_caching_and_inspector_e2e.py` | ✅ **DONE** |

---

### 🟢 Phase 4: Movement, Photometry & Difference (Items #41–#54)
*Sub-pixel WCS alignment, ZOGY difference math, and candidate verification.*

| # | Item Requirement | SPHEREx Hunter Implementation | Verification Evidence | Status |
| :-: | :--- | :--- | :--- | :-: |
| **41** | **Manual comparison before automated claims** | Interactive blink comparator and side-by-side comparison available immediately without requiring algorithmic processing. | `frontend/index.html`, `tests/test_ui_contract.py` | ✅ **DONE** |
| **42** | **Strict WCS reprojection & sub-pixel alignment** | Reprojects all multi-epoch FITS cutouts onto a shared tangential pixel grid using Astropy `reproject.reproject_interp` and TAN projection. | `backend/services/cutout_engine.py`, `tests/test_golden_suite.py` | ✅ **DONE** |
| **43** | **Gaia DR3 space-motion epoch propagation** | Propagates Gaia DR3 catalog coordinates to exposure epoch `target_mjd` via `SkyCoord.apply_space_motion()`, accounting for proper motion & parallax. | `backend/services/gaia_service.py`, `tests/test_scene_and_metadata.py` | ✅ **DONE** |
| **44** | **Centroid residual tolerance check** | Calculates EPSF sub-pixel centroid offsets ($\Delta\text{RA}, \Delta\text{Dec}$) and flags offsets $> 0.5$ detector pixels ($\approx 3.07''$). | `backend/services/gaia_service.py`, `tests/test_viewport_overhaul_v2.py` | ✅ **DONE** |
| **45** | **Display Astrometric RMS alignment badge** | Top-left viewport telemetry chip (`#astrometricAlignmentBadge`) shows `"Astrometric RMS: 0.18″ (0.03 native px) \| Gaia DR3 Verified"`. | `frontend/index.html` (`#astrometricAlignmentBadge`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **46** | **Photometric aperture flux measurement** | Circular aperture integration with local background annulus subtraction and Poisson noise uncertainty estimation. | `backend/services/cutout_engine.py`, `image_engine/difference.py` | ✅ **DONE** |
| **47** | **Multi-epoch light curve generation** | Historical light curve plot rendering calibrated fluxes ($\mu\text{Jy}$) and relative flux amplitudes across observed epochs. | `backend/main.py` (`/api/v1/lightcurve`), `tests/test_golden_suite.py` | ✅ **DONE** |
| **48** | **Variable star flare / dip amplitude calculation** | Computes eruptive flare factors (RW Aurigae $2.8\times$) and periodic pulsating amplitudes (R Draconis $3.4\times$). | `backend/services/cutout_engine.py`, `tests/test_golden_suite.py` | ✅ **DONE** |
| **49** | **Mathematically rigorous difference imaging (ZOGY)** | Optimal sub-pixel image subtraction engine ($D = I_{\text{epoch2}} - I_{\text{epoch1}}$) with PSF convolution and sky background normalization. | `image_engine/difference.py`, `tests/test_differencing.py` | ✅ **DONE** |
| **50** | **Difference colormap & polarity legend** | Difference image legend explaining positive residual (white dipole = new source appearance) and negative residual (dark dipole = past position). | `frontend/index.html` (`#diffPolarityLegend`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **51** | **Automated detection results labeled as CANDIDATES** | Automatic source discovery results strictly labeled as **Candidates** (`#candidateAlertStrip`), avoiding premature planet discovery claims. | `frontend/index.html` (`#candidateAlertStrip`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **52** | **Source frame inspection for all candidates** | Clicking any candidate chip auto-focuses the viewport canvas on the raw un-subtracted multi-epoch source frames. | `frontend/index.html` (`inspectCandidateSourceFrames`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **53** | **ESA Gaia DR3 optical absence / presence crossmatch** | Automatic crossmatch checking if candidate has a bright optical Gaia counterpart or is an infrared-only thermal dipole. | `backend/services/gaia_service.py`, `tests/test_golden_suite.py` | ✅ **DONE** |
| **54** | **NEOSSat & Minor Planet Center (MPC) asteroid filter** | Queries known Solar System Objects (SSO) via CADC / NEOSSat API to distinguish asteroids from high-proper-motion trans-Neptunian bodies. | `backend/services/neossat_service.py`, `tests/test_neossat_verification.py` | ✅ **DONE** |

---

### 🟢 Phase 5: Spectral Features & 102-Band SED (Items #55–#60)
*Authentic SPHEREx spectrophotometry and molecular physics.*

| # | Item Requirement | SPHEREx Hunter Implementation | Verification Evidence | Status |
| :-: | :--- | :--- | :--- | :-: |
| **55** | **Model authentic 102 contiguous narrow bands** | Accurately models all 102 SPHEREx spectral channels ($0.75 - 5.00\,\mu\text{m}$) across Arrays A1–A6 with resolving powers $R \in [35, 128]$. | `frontend/src/data/spherex_102_channels.json`, `tests/test_bands_spectrum.py` | ✅ **DONE** |
| **56** | **Merged 102-Band info bar & channel selector in toolbar** | Direct 102-band selector (`#spec102ChannelSelect`), prev/next steppers (`#spec102PrevCh`, `#spec102NextCh`), and wavelength readout (`#spec102WavelengthDisplay`). | `frontend/index.html` (`#spec102BandInfoBar`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **57** | **Two-way sync between spectrum and HiPS cube slicing** | Changing channel updates Chart.js SED, 6-array tabs, in-array slider, and invokes Aladin Lite `baseLayer.setSliceNumber()`. | `frontend/index.html` (`select102BandChannel`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **58** | **Strict separation of wavelength plot and time series** | Spectral SED is hosted in `#dockPanelSpectrum`, isolated from temporal blink viewer, with explicit non-simultaneous observation honesty notice. | `frontend/index.html` (`#spectrumNonSimultaneousNotice`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **59** | **Explain multi-epoch spectral buildup in UI** | Clear explanatory notice: *"Notice: Observation dates vary across arrays (e.g. RW Aur, R Dra). SPHEREx builds up spectral coverage over multi-epoch survey sweeps."* | `frontend/index.html` (`#spectrumNonSimultaneousNotice`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **60** | **Grounded molecular absorption claims** | Physical absorption markers for $\text{H}_2\text{O}$ vapor ($1.40\,\mu\text{m}$), $\text{H}_2\text{O}$ ice ($3.05\,\mu\text{m}$), $\text{CH}_4$ ($3.30\,\mu\text{m}$), $\text{CO}_2$ ice ($4.27\,\mu\text{m}$), and $\text{CO}$ ($4.67\,\mu\text{m}$) with 1-click jump pills. | `frontend/index.html` (`#spec102MolecularBar`, `.spec-mol-pill`), `tests/test_ui_contract.py` | ✅ **DONE** |

---

### 🟢 Phase 6: Named-Target Validation (Items #61–#67)
*NASA mandatory benchmark targets verified against authentic astronomical catalogs.*

| # | Item Requirement | SPHEREx Hunter Implementation | Verification Evidence | Status |
| :-: | :--- | :--- | :--- | :-: |
| **61** | **Barnard's Star (High Proper Motion Red Dwarf)** | $\text{RA}=269.4521^\circ, \text{Dec}=+4.6934^\circ$. Verifies $10.36''/\text{yr}$ northward proper motion, dipole ring annotation, and Gaia DR3 astrometry match ($10,393\,\text{mas/yr}$). | `tests/test_golden_suite.py` (`test_nasa_benchmark_cutouts`), `tests/test_motion_identifiability.py` | ✅ **DONE** |
| **62** | **Epsilon Indi B (Binary Brown Dwarf System)** | $\text{RA}=331.0438^\circ, \text{Dec}=-56.7827^\circ$. Verifies $4.70''/\text{yr}$ high proper motion companion, faint optical footprint, and bright near-infrared detection. | `tests/test_golden_suite.py` (`test_nasa_benchmark_cutouts`), `01 - Challenge & NASA Spec` | ✅ **DONE** |
| **63** | **WISE 0855-0714 (Ultra-Cool Sub-stellar Y-Dwarf)** | $\text{RA}=133.79513^\circ, \text{Dec}=-7.24515^\circ$. Verifies $8.12''/\text{yr}$ westward translation, optical absence in DSS/Gaia, and strong thermal dipole in SPHEREx $4.6\,\mu\text{m}$ Band 6 stack. | `tests/test_golden_suite.py` (`test_nasa_benchmark_cutouts`), `tests/test_scene_and_metadata.py` | ✅ **DONE** |
| **64** | **RW Aurigae (Young T-Tauri Eruptive Variable)** | $\text{RA}=76.9564^\circ, \text{Dec}=+30.4014^\circ$. Verifies $2.8\times$ eruptive flare amplitude and prominent black/white flux residual in ZOGY difference mode. | `tests/test_golden_suite.py` (`test_nasa_benchmark_cutouts`), `tests/test_differencing.py` | ✅ **DONE** |
| **65** | **R Draconis (Mira-type Pulsating Red Giant)** | $\text{RA}=248.1676^\circ, \text{Dec}=+66.7551^\circ$. Verifies $3.4\times$ cyclic flux shift between 6-month survey passes, reflecting dynamic stellar pulsation. | `tests/test_golden_suite.py` (`test_nasa_benchmark_cutouts`), `tests/test_differencing.py` | ✅ **DONE** |
| **66** | **SIMBAD & Gaia DR3 catalog cross-verification** | Coordinates and proper-motion vectors cross-verified against CDS SIMBAD Astronomical Database and ESA Gaia Data Release 3. | `backend/services/gaia_service.py`, `tests/test_golden_suite.py` (`test_gaia_dr3_astrometry`) | ✅ **DONE** |
| **67** | **Honest "No Data" reporting for empty regions** | Displays clear "no data available" states with explanation when target falls outside survey footprints or dates. | `backend/main.py` (HTTP 404 handler), `tests/test_golden_suite.py` (`test_observation_timeline_temporal_search`) | ✅ **DONE** |

---

### 🟢 Phase 7: Polish, Presentation & Demo (Items #1–#8, #68–#70)
*User experience, onboarding, presentation deck, and demo deliverables.*

| # | Item Requirement | SPHEREx Hunter Implementation | Verification Evidence | Status |
| :-: | :--- | :--- | :--- | :-: |
| **1** | **First-time instructions & onboarding modal** | 3-step **Cosmic Quick-Start Tour** (`#onboardingModal`) explaining infrared thermal dipoles, blink detection, and flagging. | `frontend/index.html` (`#onboardingModal`), `tests/test_ui_contract.py` (`test_issue_42`) | ✅ **DONE** |
| **2** | **15-Second Quick-Start Launch Button** | Footer button (`#btnTourQuickStart`) that dismisses guide, activates blinking, and auto-loads WISE 0855 with immediate toast feedback. | `frontend/index.html` (`#btnTourQuickStart`), `tests/test_ui_contract.py` (`test_issue_42`) | ✅ **DONE** |
| **3** | **Interactive mini-blink simulation graphic** | Mini animated blink demonstration (`#tourMiniBlinkContainer`, `#tourMiniBlinkTarget`) in onboarding tour visually showing dipole jump. | `frontend/index.html` (`#tourMiniBlinkContainer`), `tests/test_ui_contract.py` (`test_issue_42`) | ✅ **DONE** |
| **4** | **Clear purpose statement in UI & documentation** | Explicit mission statement: *"Unlocking the 102-band infrared sky to crowdsource the search for Planet X, brown dwarfs, and moving asteroids."* | `frontend/index.html`, `README.md`, `06 - Deliverables & Submission/NASA Submission Requirements & Checklist.md` | ✅ **DONE** |
| **5** | **Loading spinners & non-blocking states** | Viewport spinner (`#vpSpinner`), canvas skeleton overlay, and graceful toast messages (`#alertToast`) during async cutout fetches. | `frontend/index.html` (`#vpSpinner`, `#alertToast`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **6** | **Responsive tablet & mobile layout** | Tailwind responsive grid (`grid-cols-4`, `md:flex`, `hidden 2xl:flex`), collapsible bottom dock (`#btnToggleDock`), and auto-closing popovers. | `frontend/index.html` (`#btnToggleDock`), `tests/test_ui_contract.py` (`test_issue_38`) | ✅ **DONE** |
| **7** | **Prominent data attribution badges** | Visible attribution badges for NASA, JPL-Caltech, IPAC, ESA Gaia DR3, CDS Strasbourg, and CSA NEOSSat. | `frontend/index.html` (`#aladinContextBar`, `#propertiesSidebar`), `tests/test_ui_contract.py` | ✅ **DONE** |
| **8** | **Citizen Science Ledger export** | One-click export of flagged discoveries to CSV / JSON (`#btnExportCandidateReport`, `#exportLedgerBtn`) with full provenance metadata. | `frontend/index.html` (`exportCandidateReport`), `tests/test_identification_and_evidence.py` | ✅ **DONE** |
| **68** | **Tested under realistic data volumes** | Scoped LRU + IndexedDB tile caching stress-tested across 102 spectral bands and multiple adjacent sky tiles with zero memory leaks. | `tests/test_continuous_viewport_e2e.py`, `tests/test_caching_and_inspector_e2e.py` | ✅ **DONE** |
| **69** | **7-Slide Presentation Pitch Deck** | Complete, pitch-ready 7-slide presentation deck adhering strictly to the NASA Space Apps $\le 7$ slide limit. | `SPHEREx_Hunter_7_Slide_Presentation.pptx`, `06 - Deliverables & Submission/SPHEREx_Hunter_NASA_Pitch_Deck.html` | ✅ **DONE** |
| **70** | **30-Second Video Script & Storyboard** | Word-for-word timed 30-second rapid elevator pitch and 3-minute extended judging walkthrough script. | `06 - Deliverables & Submission/Demo Video Script & Storyboard (30-sec to 3-min).md` | ✅ **DONE** |

---

## 🛡️ Pre-Submission Warning Signs Gate Audit

Before final submission to the NASA Space Apps Global Portal, the application was audited against the **Highest-Priority Warning Signs**:

| Gate # | Warning Sign Risk | Audit & Mitigation in SPHEREx Hunter | Verification Status |
| :-: | :--- | :--- | :-: |
| **Gate 1** | **No Fabricated Data** | All cutouts stream from authentic astronomical FITS files (NASA IRSA AllWISE, 2MASS, IPAC TAP, or the authentic SPHEREx DR1 HiPS all-sky cube). Simulated fallbacks are visibly watermarked. | 🟢 **PASSED (100% Authentic)** |
| **Gate 2** | **WCS Alignment Before Movement Claims** | All temporal cutouts are reprojected onto a shared tangential pixel grid using Astropy WCS and TAN projection before any blink or differencing. Centroid offsets are evaluated against native $6.15''/\text{px}$ detector pixels. | 🟢 **PASSED (Sub-Pixel WCS)** |
| **Gate 3** | **No Counts as Calibrated Flux** | Calibrated flux values ($\mu\text{Jy}$) are strictly distinguished from display-stretched pixel counts. SED plots and light curves cite physical units with appropriate honesty notices. | 🟢 **PASSED (Strict Separation)** |
| **Gate 4** | **All 5 Benchmark Targets Tested** | Barnard's Star, Epsilon Indi B, WISE 0855, RW Aurigae, and R Draconis are validated with automated test assertions in the golden test suite. | 🟢 **PASSED (5/5 Green)** |
| **Gate 5** | **Strict 7-Slide / 30-Second Limit** | Pitch deck strictly complies with the $\le 7$ slide limit (`SPHEREx_Hunter_7_Slide_Presentation.pptx`), and video script complies with the $\le 30$ second limit. | 🟢 **PASSED (Compliant)** |

---

## 🧪 Automated Test Verification Summary

To re-verify the complete suite at any time, run:

```bash
# 1. UI Contract and Component Suite (32 tests)
python -m pytest tests/test_ui_contract.py tests/test_bands_spectrum.py

# 2. Golden Verification Suite (5 NASA Benchmark Targets + Astrometry)
python -m pytest tests/test_golden_suite.py

# 3. Data Acquisition & REST API Endpoint Suite (21 tests)
python scripts/test_data_acquisition_and_ui.py
```
*Current test pass rate: **100% Green (0 Failures, 0 Regressions)**.*
