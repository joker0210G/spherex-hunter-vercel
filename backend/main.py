"""
🚀 SPHEREx Hunter - Real-Time FastAPI Astronomical Backend
NASA Space Apps 2026 - Team RIP

Provides REST API endpoints for:
- Multi-epoch astronomical cutouts (Epoch 1, Epoch 2, Difference Map)
- 102-band near-infrared Spectral Energy Distribution (SED)
- Benchmark target metadata (WISE 0855, Barnard's Star, Epsilon Indi B, RW Aurigae, R Draconis)
- Citizen science candidate logging
"""

import csv
import hashlib
import io
import json
import os
import uuid
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

# Silence erfa dubious year warnings on sub-millisecond MJD conversions
try:
    from erfa import ErfaWarning
    warnings.filterwarnings("ignore", category=ErfaWarning)
except ImportError:
    pass
warnings.filterwarnings("ignore", message=".*dubious year.*")

# Load local .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip()
                    if k and k not in os.environ:
                        os.environ[k] = v
    except Exception:
        pass

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.api_v1 import make_request_id
from backend.api_v1 import router as api_v1_router
from backend.models_v1 import ProblemDetails
from backend.services.catalog_engine import (
    crossmatch_photometry,
    query_2mass_psc,
    query_simbad_metadata,
    query_spherex_archive,
    query_wise_catalog,
)
from backend.services.csa_neossat_service import query_csa_neossat
from backend.services.cutout_engine import (
    BENCHMARKS,
    auto_prune_disk_cache,
    clear_all_caches,
    fetch_real_cutout,
    get_102_band_spectrum,
    get_cache_stats,
    query_observation_timeline,
    run_automated_source_discovery,
)
from backend.services.gaia_service import (
    compute_astrometric_residuals,
    propagate_gaia_sources_to_epoch,
    query_gaia_dr3,
)
from backend.services.neossat_service import build_neossat_tracking_report, build_portal_links
from backend.services.scene_service import get_target_scene
from backend.services.verification_service import run_wiseview_verification

app = FastAPI(
    title="SPHEREx Hunter Astronomical API",
    description="NASA Space Apps 2026 - Team RIP (Planet X & SPHEREx)",
    version="1.0.0"
)

# Enable CORS for all origins (frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_FALLBACK_HIPS_JPEG_BYTES: Optional[bytes] = None


def _get_fallback_hips_jpeg_bytes() -> bytes:
    """Builds and caches a 64x64 dark-space JPEG tile for local Aladin HiPS fallback probes."""
    global _FALLBACK_HIPS_JPEG_BYTES
    if _FALLBACK_HIPS_JPEG_BYTES is None:
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (64, 64), (6, 10, 18)).save(buf, format="JPEG")
        _FALLBACK_HIPS_JPEG_BYTES = buf.getvalue()
    return _FALLBACK_HIPS_JPEG_BYTES


# Serve CDS HiPS properties descriptor cleanly so relative Aladin fallback probes return HTTP 200
@app.get("/app/P/DSS2/color/properties")
def get_dss2_hips_properties():
    return Response(
        content=(
            "creator_did = ivo://CDS/P/DSS2/color\n"
            "obs_title = DSS2 color\n"
            "hips_frame = equatorial\n"
            "hips_order = 3\n"
            "hips_tile_width = 512\n"
            "hips_tile_format = jpeg\n"
            "hips_service_url = https://alasky.cds.unistra.fr/DSS/DSSColor\n"
        ),
        media_type="text/plain",
    )


@app.get("/app/P/DSS2/color/{tile_path:path}")
def get_dss2_hips_fallback_tile(tile_path: str):
    """Serves a clean dark-space JPEG fallback tile so Aladin HiPS local probes never 404."""
    return Response(content=_get_fallback_hips_jpeg_bytes(), media_type="image/jpeg")


# Mount local HiPS deterministic fixture for offline testing
LOCAL_HIPS_FIXTURE = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "hips_spherex_dr1_sample")
if os.path.exists(LOCAL_HIPS_FIXTURE):
    app.mount("/app/fixtures/hips_spherex_dr1_sample", StaticFiles(directory=LOCAL_HIPS_FIXTURE), name="hips_dr1_fixture")

# Mount frontend directory for same-origin browsing
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.get("/app/index.html")
def get_app_index_no_cache():
    """Serves the main application with no-cache headers to ensure updates apply immediately."""
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        response = FileResponse(index_file, media_type="text/html")
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    raise HTTPException(status_code=404, detail="index.html not found")

if os.path.exists(FRONTEND_DIR):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    ASSETS_DIR = os.path.join(FRONTEND_DIR, "assets")
    if os.path.exists(ASSETS_DIR):
        app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# Mount Versioned API v1 Router
app.include_router(api_v1_router)

# Global RFC 7807 Exception Handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    req_id = request.headers.get("x-request-id", make_request_id())
    code = getattr(exc, "code", f"HTTP_{exc.status_code}")
    title = getattr(exc, "title", "HTTP Error")
    problem = ProblemDetails(
        type=f"https://spherex-hunter.space/errors/{str(code).lower().replace('_', '-')}",
        title=title,
        status=exc.status_code,
        detail=str(exc.detail),
        instance=str(request.url),
        request_id=req_id,
        code=str(code)
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(),
        media_type="application/problem+json",
        headers={"X-Request-Id": req_id, "Cache-Control": "no-store"}
    )

# In-memory discovery ledger (persisted to JSON, overridable via env for isolated testing)
DISCOVERIES_FILE = os.environ.get(
    "DISCOVERIES_FILE",
    os.path.join(os.path.dirname(__file__), "..", "07 - Team Memory & Sync", "candidate_discoveries.json")
)

class DiscoveryCandidate(BaseModel):
    ra: float
    dec: float
    object_type: Optional[str] = None
    motion_type: Optional[str] = None
    target_name: Optional[str] = None
    candidate_name: Optional[str] = None
    user_handle: Optional[str] = "@citizen_scientist"
    astronomer: Optional[str] = "@citizen_scientist"
    notes: Optional[str] = ""
    proper_motion_mas: Optional[float] = None
    confidence: Optional[int] = 5

@app.get("/")
def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept and not accept.startswith("application/json"):
        return RedirectResponse(url="/app/index.html", status_code=307)
    return {
        "service": "SPHEREx Hunter Astronomy Backend",
        "team": "RIP (Coimbatore, India)",
        "challenge": "Planet X and SPHEREx",
        "docs_url": "/docs",
        "endpoints": [
            "/api/health",
            "/api/targets",
            "/api/cutout?ra=133.79513&dec=-7.24515&target=wise0855",
            "/api/spectrum?ra=133.79513&dec=-7.24515&target=wise0855",
            "/api/scene?target=wise0855",
            "/api/source_discovery?ra=133.79513&dec=-7.24515&target=wise0855",
            "/api/verify_candidate?ra=133.79513&dec=-7.24515&target=wise0855",
            "/api/neossat?ra=133.79513&dec=-7.24515",
            "/api/resources_codex?ra=133.79513&dec=-7.24515",
            "/api/download_fits?target=wise0855&epoch=1",
            "/api/catalog/gaia?ra=269.45208&dec=4.69339&radius=3.0",
            "/api/catalog/2mass?ra=269.45208&dec=4.69339&radius=3.0",
            "/api/catalog/simbad?ra=269.45208&dec=4.69339",
            "/api/catalog/crossmatch?ra=269.45208&dec=4.69339",
            "/api/discoveries",
            "/api/discoveries/export/csv"
        ]
    }


@app.get("/index.html")
def root_index_redirect():
    """Redirects /index.html directly to /app/index.html to avoid 404s from standard root queries."""
    return RedirectResponse(url="/app/index.html", status_code=307)


@app.get("/favicon.ico")
def root_favicon():
    """Serves the SVG logo or 204 No Content for browser default /favicon.ico probes."""
    fav_path = os.path.join(FRONTEND_DIR, "assets", "logo.svg")
    if os.path.exists(fav_path):
        return FileResponse(fav_path, media_type="image/svg+xml")
    return Response(status_code=204)

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "engine": "Astropy + Astroquery + FastAPI",
        "archive": "NASA IRSA / SkyView Connected",
        "active_epochs": 2
    }

@app.get("/api/targets")
@app.get("/api/benchmarks")
def get_benchmark_targets():
    """Returns the 5 NASA benchmark validation targets as pure coordinate bookmarks."""
    return [
        {
            "id": k,
            "name": v["name"],
            "ra": v["ra"],
            "dec": v["dec"],
            "type": v["type"],
            "temp_k": v["temp_k"],
            "variability": None
        }
        for k, v in BENCHMARKS.items()
    ]

@app.post("/api/cache/clear")
def clear_cache():
    """Flushes L1 RAM LRU cache and purges dynamic FITS files from disk."""
    return clear_all_caches()

@app.get("/api/cache/stats")
def cache_stats():
    """Returns current cache metrics."""
    return get_cache_stats()


@app.get("/api/cache/prune")
@app.post("/api/cache/prune")
def prune_cache(
    max_mb: float = Query(500.0, description="Soft disk cache cap in MB before eviction"),
    target_mb: float = Query(350.0, description="Target disk usage in MB after pruning"),
):
    """Triggers smart disk auto-pruning daemon while keeping benchmark targets pinned."""
    return auto_prune_disk_cache(max_mb=max_mb, target_mb=target_mb)

import astropy.units as u
from astropy.coordinates import SkyCoord

from backend.utils.validation import sanitize_target_name, validate_coordinates


def parse_celestial_coords(ra_input: str, dec_input: str) -> tuple[float, float]:
    """
    Parses both decimal degrees ('133.79513', '-7.24515') and
    standard sexagesimal notation ('08h55m10.831s', '-7d14m42.53s') via Astropy.
    Validates physical celestial boundaries [0, 360) and [-90, +90].
    """
    try:
        ra_val, dec_val = float(ra_input), float(dec_input)
        return validate_coordinates(ra_val, dec_val)[:2]
    except ValueError:
        pass

    try:
        ra_clean = str(ra_input).strip()
        dec_clean = str(dec_input).strip()
        unit = (u.hourangle, u.deg) if 'h' in ra_clean.lower() else (u.deg, u.deg)
        sc = SkyCoord(ra_clean, dec_clean, unit=unit)
        return validate_coordinates(float(round(sc.ra.deg, 5)), float(round(sc.dec.deg, 5)))[:2]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid celestial coordinates '{ra_input}', '{dec_input}': {e}")

@app.get("/cutout")
@app.get("/api/cutout")
def get_cutout(
    request: Request,
    response: Response,
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal ('08h55m10.831s')"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal ('-7d14m42.53s')"),
    fov: float = Query(3.0, description="Field of View in arcminutes"),
    target: Optional[str] = Query(None, description="Benchmark target key (wise0855, barnard, etc.)"),
    lod: int = Query(1, description="Game Level of Detail tier: 0 (Hero Deep), 1 (Standard Science), 2 (Wide Overview)"),
    force_refresh: bool = Query(False, description="Bypass all caches and force fresh NASA query"),
    refresh: bool = Query(False, description="Alias for force_refresh to bypass caches"),
    bypass_cache: bool = Query(False, description="Alias to bypass L1/L2 caches and force live query"),
    include_spectrum: bool = Query(False, description="Compute full 102-band multi-survey spectrophotometry (False for fast tile rendering)"),
    start_date: Optional[str] = Query(None, description="Optional temporal start filter (ISO UTC)"),
    end_date: Optional[str] = Query(None, description="Optional temporal end filter (ISO UTC)"),
    exact_date: Optional[str] = Query(None, description="Optional exact observation epoch target (ISO UTC)")
):
    """
    Universal Astronomical Pipeline:
    Processes ANY celestial coordinates through authentic FITS retrieval, WCS alignment,
    difference imaging, ETag conditional caching (HTTP 304), and multi-tier caching.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        fov_val = float(fov) if isinstance(fov, (int, float, str)) else 3.0
        if fov_val > 15.0:
            raise HTTPException(
                status_code=400,
                detail=f"Requested Field of View ({fov_val:.1f}') exceeds 15.0 arcmin limit. Please zoom in."
            )
        lod_val = int(lod) if isinstance(lod, (int, str)) else 1
        is_refresh = bool(force_refresh or refresh or bypass_cache)
        target_sanitized = sanitize_target_name(target) if target else None
        data = fetch_real_cutout(
            ra=ra_deg,
            dec=dec_deg,
            fov_arcmin=fov_val,
            target_key=target_sanitized,
            lod=lod_val,
            force_refresh=is_refresh,
            include_spectrum=include_spectrum
        )
        if not data or not isinstance(data, dict):
            raise HTTPException(
                status_code=404,
                detail=f"No archival 2MASS/DSS2 FITS cutouts available at RA {ra_deg:.4f}°, Dec {dec_deg:.4f}° within {fov_val:.1f}' arcmin."
            )
        if start_date or end_date or exact_date:
            data = dict(data)
            data["temporal_filter"] = query_observation_timeline(
                ra_deg, dec_deg, start_date=start_date, end_date=end_date, exact_date=exact_date
            )

        # Compute deterministic ETag for conditional caching (Amendment A5)
        etag = f'"{hashlib.sha256(f"{data.get("cached_at", "")}_{ra_deg:.5f}_{dec_deg:.5f}_{fov_val:.2f}_{lod_val}".encode()).hexdigest()[:16]}"'
        client_etag = request.headers.get("if-none-match")
        if client_etag and client_etag.strip('"') == etag.strip('"'):
            return Response(
                status_code=304,
                headers={
                    "ETag": etag,
                    "X-Cache": "HIT",
                    "X-Cache-Tier": "L1_RAM",
                    "Cache-Control": "public, max-age=3600",
                },
            )

        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "public, max-age=3600"
        response.headers["X-Cache"] = str(data.get("cache_status", "MISS"))
        response.headers["X-Cache-Tier"] = str(data.get("cache_tier", "UNKNOWN"))
        response.headers["X-Cached-At"] = str(data.get("cached_at", ""))
        response.headers["X-Archive-Reachability"] = str(data.get("archive_reachability", "nominal"))
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/observations")
def get_available_observations(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"),
    exact_date: Optional[str] = Query(None, description="Optional specific observation epoch date (ISO UTC)"),
):
    """
    Returns authentic multi-epoch observation metadata covering celestial coordinates (RA, Dec)
    within an optional temporal date/time filtering window [start_date, end_date] or exact_date.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return query_observation_timeline(ra_deg, dec_deg, start_date=start_date, end_date=end_date, exact_date=exact_date)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gaia")
def get_gaia_astrometry(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(3.0, description="Search radius in arcminutes")
):
    """
    Queries official Gaia Data Release 3 (DR3) catalog directly from NASA IRSA TAP.
    Returns stellar proper motions, parallax, and optical G-band magnitudes.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return query_gaia_dr3(ra=ra_deg, dec=dec_deg, radius_arcmin=radius)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cutout/raw")
def get_cutout_raw_compat(
    request: Request,
    target: str = Query(..., description="Target slug e.g. 'sample_leo' or 'wise0855'"),
    format: Optional[str] = Query("binary", description="'binary' or 'header'")
):
    """Exposes Float32 ArrayBuffer cutout streaming for dynamic client-side stretch sliders."""
    from backend.api_v1 import get_cutout_raw
    return get_cutout_raw(request=request, target=target, format=format)

@app.get("/api/cutout/raw/header")
def get_cutout_raw_header_compat(
    request: Request,
    target: str = Query(..., description="Target slug e.g. 'sample_leo' or 'wise0855'")
):
    """Exposes JSON WCS header for raw float32 cutout."""
    from backend.api_v1 import get_cutout_raw_header
    return get_cutout_raw_header(request=request, target=target)

@app.get("/api/spectrum")
def get_spectrum(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    target: Optional[str] = Query(None, description="Benchmark target key")
):
    """Returns the 102 near-infrared spectral bands (0.75 - 5.0 μm) with molecular detections."""
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        spectrum = get_102_band_spectrum(ra=ra_deg, dec=dec_deg, target_key=target)
        return spectrum
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bands")
def get_bands_metadata():
    """Returns static SPHEREx 6-array x 17-channel (102 bands) structural metadata."""
    ARRAYS = [
        {"array_id": "A1", "array_name": "Array 1 (0.75-1.11 µm)", "band_range": "1-17", "range_um": "0.750-1.110", "wavelength_min": 0.750, "wavelength_max": 1.110, "resolving_power": 41, "science": "Optical/NIR boundary, stellar continuum, proper motion stars"},
        {"array_id": "A2", "array_name": "Array 2 (1.11-1.64 µm)", "band_range": "18-34", "range_um": "1.110-1.640", "wavelength_min": 1.110, "wavelength_max": 1.640, "resolving_power": 41, "science": "2MASS J/H overlap, stellar photospheres"},
        {"array_id": "A3", "array_name": "Array 3 (1.64-2.42 µm)", "band_range": "35-51", "range_um": "1.640-2.420", "wavelength_min": 1.640, "wavelength_max": 2.420, "resolving_power": 41, "science": "2MASS Ks overlap, warm circumstellar dust"},
        {"array_id": "A4", "array_name": "Array 4 (2.42-3.82 µm)", "band_range": "52-68", "range_um": "2.420-3.820", "wavelength_min": 2.420, "wavelength_max": 3.820, "resolving_power": 35, "science": "H₂O Ice (3.05 µm), CH₄ Methane (3.30 µm)"},
        {"array_id": "A5", "array_name": "Array 5 (3.82-4.42 µm)", "band_range": "69-85", "range_um": "3.820-4.420", "wavelength_min": 3.820, "wavelength_max": 4.420, "resolving_power": 110, "science": "CO₂ Ice (4.27 µm), Cold Brown Dwarf thermal peak"},
        {"array_id": "A6", "array_name": "Array 6 (4.42-5.00 µm)", "band_range": "86-102", "range_um": "4.420-5.000", "wavelength_min": 4.420, "wavelength_max": 5.000, "resolving_power": 130, "science": "CO Carbon Monoxide (4.67 µm), Organics, Planet X emission"}
    ]
    channels = []
    for arr in ARRAYS:
        w_min = arr["wavelength_min"]
        w_max = arr["wavelength_max"]
        w_step = (w_max - w_min) / 16.0
        start_idx = int(arr["band_range"].split("-")[0])
        for i in range(17):
            b_id = start_idx + i
            w_center = round(w_min + i * w_step, 4)
            mol = None
            if abs(w_center - 1.40) < 0.05: mol = "H2O"
            elif abs(w_center - 3.05) < 0.08: mol = "H2O_ICE"
            elif abs(w_center - 3.30) < 0.08: mol = "CH4"
            elif abs(w_center - 4.27) < 0.05: mol = "CO2_ICE"
            elif abs(w_center - 4.67) < 0.06: mol = "CO"
            channels.append({
                "band_id": b_id,
                "band": b_id,
                "array_id": arr["array_id"],
                "array_name": arr["array_name"],
                "wavelength_um": w_center,
                "resolving_power": arr["resolving_power"],
                "molecular_flag": mol
            })
    return {"status": "success", "total_bands": 102, "arrays": ARRAYS, "bands": channels}

@app.get("/api/source_discovery")
def source_discovery(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    fov: float = Query(3.0, description="Field of View in arcminutes"),
    target: Optional[str] = Query(None, description="Benchmark target key")
):
    """Runs Caltech-IPAC Source Discovery + CSA NEOSSat Line Segment Detector (LSD) streaklet analysis."""
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return run_automated_source_discovery(ra=ra_deg, dec=dec_deg, fov_arcmin=fov, target_key=target)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/catalog/gaia")
def get_gaia_catalog(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(3.0, description="Search radius in arcminutes (0.2 to 15.0)"),
    limit: int = Query(100, description="Maximum number of sources to return (1 to 300)")
):
    """
    Queries European Space Agency (ESA) Gaia DR3 catalog for astrometric sources,
    magnitudes (G, BP, RP), proper motions (pmRA, pmDEC), parallax distances, and motion vectors.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        catalog_data = query_gaia_dr3(ra=ra_deg, dec=dec_deg, radius_arcmin=radius, row_limit=limit)
        catalog_data["total_sources"] = catalog_data.get("matched_count", len(catalog_data.get("sources", [])))
        for s in catalog_data.get("sources", []):
            if "phot_g_mag" in s and "g_mag" not in s:
                s["g_mag"] = s["phot_g_mag"]
            if "pm_ra_mas_yr" in s and "pmra_mas_yr" not in s:
                s["pmra_mas_yr"] = s["pm_ra_mas_yr"]
            if "pm_dec_mas_yr" in s and "pmdec_mas_yr" not in s:
                s["pmdec_mas_yr"] = s["pm_dec_mas_yr"]
        return catalog_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/astrometry/gaia")
def get_gaia_astrometry_v1(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(3.0, description="Search radius in arcminutes (0.2 to 15.0)"),
    limit: int = Query(100, description="Maximum number of sources to return (1 to 300)"),
    target_mjd: Optional[float] = Query(None, description="Observation epoch MJD for astrometric space motion propagation")
):
    """
    Step 4: Live Gaia DR3 Astrometry with Astropy space motion propagation (apply_space_motion)
    and EPSF centroid astrometric residual computation.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        catalog_data = query_gaia_dr3(ra=ra_deg, dec=dec_deg, radius_arcmin=radius, row_limit=limit)
        sources = catalog_data.get("sources", [])
        if target_mjd is not None:
            sources = propagate_gaia_sources_to_epoch(sources, target_mjd=target_mjd)
        residuals = compute_astrometric_residuals(None, sources, pixel_scale_arcsec=6.15)
        return {
            "status": "success",
            "catalog": "Gaia DR3",
            "search_center": {"ra_deg": ra_deg, "dec_deg": dec_deg, "radius_arcmin": radius},
            "matched_count": len(sources),
            "target_mjd": target_mjd,
            "sources": sources,
            "astrometric_residuals": residuals,
            "pixel_scale_arcsec": 6.15,
            "provenance": {
                "reference_epoch": "J2016.0",
                "propagated_to_mjd": target_mjd,
                "engine": "astropy.coordinates.SkyCoord.apply_space_motion"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/neossat")
def get_neossat_tracking(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    fov: float = Query(3.0, description="Field of View in arcminutes"),
    epoch: Optional[str] = Query(None, description="ISO UTC observation epoch"),
    include_cadc: bool = Query(True, description="Query CADC CAOM-2 TAP for NEOSSat archival footprints")
):
    """Task 4: Queries IMCCE SkyBoT known Solar System objects and CADC CAOM-2 NEOSSat observations."""
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return build_neossat_tracking_report(ra=ra_deg, dec=dec_deg, fov_arcmin=fov, epoch=epoch, include_cadc=include_cadc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wiseview/url")
def get_wiseview_url(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    size: int = Query(150, description="Cutout box size in pixels (default: 150)")
):
    """
    Task 3: WiseView 1-Click Verification Bridge.
    Generates verified deep-link URL to NASA Backyard Worlds WiseView tool
    (http://byw.tools/wiseview) for multi-epoch WISE coadd verification.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        wiseview_url = f"http://byw.tools/wiseview#ra={ra_deg:.5f}&dec={dec_deg:.5f}&size={size}&band=3&linear=True&diff=True"
        return {
            "status": "success",
            "ra_deg": ra_deg,
            "dec_deg": dec_deg,
            "wiseview_url": wiseview_url,
            "description": "NASA Backyard Worlds: Planet 9 unbinned multi-epoch WISE coadd viewer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/verify_candidate")
def verify_candidate_wiseview(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    fov: float = Query(3.0, description="Field of View in arcminutes"),
    target: Optional[str] = Query(None, description="Benchmark target key")
):
    """Task 3: Runs Backyard Worlds WiseView 5-step verification checklist (Dipole + Gaia DR3 + SkyBoT + W1-W2 + WiseView)."""
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return run_wiseview_verification(ra=ra_deg, dec=dec_deg, fov_arcmin=fov, target_key=target)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AIAskRequest(BaseModel):
    ra: Union[float, str]
    dec: Union[float, str]
    fov: float = 3.0
    target: Optional[str] = None
    question: str = "Why is this target scientifically interesting?"
    api_key: Optional[str] = None


def _call_openrouter_api(api_key: str, synthesis: dict, question: str, model: Optional[str] = None) -> Optional[dict]:
    """Calls OpenRouter API with real observational telemetry grounding."""
    import json
    import urllib.error
    import urllib.request

    try:
        tname = synthesis.get("target_name", "Target Sky Field")
        coords = synthesis.get("coordinates", {})
        metrics = synthesis.get("telemetry_metrics", {})
        verdict = synthesis.get("verdict", "INCONCLUSIVE")
        evidence_tier = synthesis.get("evidence_tier", "INCONCLUSIVE")

        system_instruction = (
            "You are the AI Astronomical Science Co-Pilot for SPHEREx Hunter (NASA Space Apps 2026). "
            "Your role is to assist astronomers and citizen scientists by interpreting multi-epoch astronomical cutouts, "
            "102-band near-infrared spectrophotometry (0.75-5.00 um), Gaia DR3 optical astrometry, and SkyBoT asteroid vetoes. "
            "STRICT RULES: Ground every assertion 100% in the real retrieved archive data provided. Never hallucinate fake coordinates or objects. "
            "Speak clearly, authoritatively, and concisely."
        )

        user_prompt = (
            f"Telescope Field: {tname} (RA {coords.get('ra_deg')}°, Dec {coords.get('dec_deg')}°)\n"
            f"Verdict: {verdict} | Evidence Tier: {evidence_tier}\n"
            f"Proper Motion: {metrics.get('proper_motion_arcsec_yr')}\"/yr | Distance: {metrics.get('distance_pc')} pc\n"
            f"WISE Color W1-W2: {metrics.get('wise_w1_w2_color')} mag\n"
            f"Plain English Summary: {synthesis.get('plain_english_summary')}\n"
            f"Technical Summary: {synthesis.get('scientist_technical_summary')}\n\n"
            f"Citizen Question: {question}"
        )

        # Determine topic from question semantics
        q_lower = question.lower()
        if any(k in q_lower for k in ("spectrum", "sed", "102", "band", "molecular", "absorption", "dip", "methane", "water")):
            topic = "102-Band Infrared Spectroscopy"
        elif any(k in q_lower for k in ("scan", "dipole", "motion", "move", "speed", "proper")):
            topic = "Kinematics & Dipole Scan"
        elif any(k in q_lower for k in ("planet", "brown dwarf", "cold", "why", "explain", "what")):
            topic = "Astrophysical Interpretation"
        else:
            topic = "Co-Pilot Field Synthesis"

        chosen_model = model or os.environ.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")
        req_body = {
            "model": chosen_model,
            "max_tokens": 500,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ]
        }

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/joker0210G/spherex-hunter",
            "X-Title": "SPHEREx Hunter"
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(req_body).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=14.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                ans_text = choices[0].get("message", {}).get("content", "").strip()
                if ans_text:
                    return {
                        "status": "success",
                        "question": question,
                        "topic": topic,
                        "answer": ans_text,
                        "evidence_tier": synthesis["evidence_tier"],
                        "verdict": synthesis["verdict"],
                        "candidate_status": synthesis["candidate_status"],
                        "llm_provider": f"OpenRouter ({chosen_model})",
                        "synthesis": synthesis,
                    }
    except Exception as e:
        print(f"OpenRouter API call notice: {e}")
    return None


def _call_gemini_api(api_key: str, synthesis: dict, question: str) -> Optional[dict]:
    """Calls Google Gemini API (BYOK) with real observational telemetry system grounding."""
    import json
    import urllib.error
    import urllib.request

    try:
        tname = synthesis.get("target_name", "Target Sky Field")
        coords = synthesis.get("coordinates", {})
        metrics = synthesis.get("telemetry_metrics", {})
        verdict = synthesis.get("verdict", "INCONCLUSIVE")
        evidence_tier = synthesis.get("evidence_tier", "INCONCLUSIVE")

        system_instruction = (
            "You are the AI Astronomical Science Co-Pilot for SPHEREx Hunter (NASA Space Apps 2026). "
            "Your role is to assist astronomers and citizen scientists by interpreting multi-epoch astronomical cutouts, "
            "102-band near-infrared spectrophotometry (0.75-5.00 um), Gaia DR3 optical astrometry, and SkyBoT asteroid vetoes. "
            "STRICT RULES: Ground every assertion 100% in the real retrieved archive data provided. Never hallucinate fake coordinates or objects. "
            "Speak clearly, authoritatively, and concisely."
        )

        user_prompt = (
            f"Telescope Field: {tname} (RA {coords.get('ra_deg')}°, Dec {coords.get('dec_deg')}°)\n"
            f"Verdict: {verdict} | Evidence Tier: {evidence_tier}\n"
            f"Proper Motion: {metrics.get('proper_motion_arcsec_yr')}\"/yr | Distance: {metrics.get('distance_pc')} pc\n"
            f"WISE Color W1-W2: {metrics.get('wise_w1_w2_color')} mag\n"
            f"Plain English Summary: {synthesis.get('plain_english_summary')}\n"
            f"Technical Summary: {synthesis.get('scientist_technical_summary')}\n\n"
            f"Citizen Question: {question}"
        )

        req_body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_instruction}\n\n{user_prompt}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 800
            }
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key.strip()}"
        req = urllib.request.Request(
            url,
            data=json.dumps(req_body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=12.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts and "text" in parts[0]:
                    ans_text = parts[0]["text"].strip()
                    return {
                        "status": "success",
                        "question": question,
                        "topic": "Gemini AI Astronomical Reasoning",
                        "answer": ans_text,
                        "evidence_tier": synthesis["evidence_tier"],
                        "verdict": synthesis["verdict"],
                        "candidate_status": synthesis["candidate_status"],
                        "llm_provider": "Google Gemini (BYOK)",
                        "synthesis": synthesis,
                    }
    except Exception as e:
        print(f"BYOK Gemini API call notice (falling back to deterministic synthesis): {e}")
    return None


def _build_ai_science_synthesis(ra_deg: float, dec_deg: float, fov: float, target: Optional[str]) -> dict:
    """
    Synthesizes real astronomical telemetry across source discovery, 5-step archival verification,
    102-band spectrophotometry, and scene astrometry without fabricating synthetic scores.
    """
    discovery = run_automated_source_discovery(ra=ra_deg, dec=dec_deg, fov_arcmin=fov, target_key=target)
    verification = run_wiseview_verification(ra=ra_deg, dec=dec_deg, fov_arcmin=fov, target_key=target)
    spectrum = get_102_band_spectrum(ra=ra_deg, dec=dec_deg, target_key=target)
    scene = get_target_scene(target_key=target, ra=ra_deg, dec=dec_deg, fov_arcmin=fov)

    t_meta = scene.get("target") or {}
    target_name = t_meta.get("name") or f"Field ({ra_deg:.4f}, {dec_deg:+.4f})"
    object_type = t_meta.get("object_type") or "Celestial Field"
    pm_arcsec = float(t_meta.get("total_pm_arcsec_yr") or 0.0)
    dist_pc = t_meta.get("distance_pc")
    teff_k = spectrum.get("temperature_k") or t_meta.get("effective_temp_k")
    mol_features = spectrum.get("expected_features") or spectrum.get("detected_molecules") or []
    candidates = discovery.get("candidates") or []
    checklist = verification.get("checklist") or []
    evidence_tier = verification.get("evidence_tier") or "INCONCLUSIVE"
    verdict = verification.get("verdict") or evidence_tier
    candidate_status = verification.get("candidate_status") or "Candidate, not confirmed"
    wise_cp = spectrum.get("wise_counterpart") or {}
    w1_w2 = wise_cp.get("w1_w2_color")
    spherex_cov = spectrum.get("spherex_coverage") or {}

    # Plain-English Citizen Scientist translation
    if teff_k is not None:
        celsius = round(float(teff_k) - 273.15)
        if float(teff_k) <= 500:
            temp_desc = f"around {round(float(teff_k))} K ({celsius}°C — colder than a home freezer, completely invisible to normal optical cameras)"
        elif float(teff_k) <= 2500:
            temp_desc = f"around {round(float(teff_k))} K ({celsius}°C — a cool substellar brown dwarf glowing mainly in infrared)"
        else:
            temp_desc = f"around {round(float(teff_k))} K ({celsius}°C — warm stellar photosphere)"
    else:
        temp_desc = "not yet constrained by archival photometry"

    if pm_arcsec >= 5.0:
        shift_26 = pm_arcsec * 26.2
        speed_desc = (
            f"rockets across the sky at {pm_arcsec:.2f} arcseconds/year "
            f"(~{shift_26:.0f}\" over the 26-year 2MASS→SPHEREx baseline), proving it is in our close solar neighborhood"
        )
    elif pm_arcsec >= 0.5:
        speed_desc = f"drifts noticeably at {pm_arcsec:.2f} arcseconds/year across multi-epoch images"
    elif candidates and candidates[0].get("separation_arcsec"):
        speed_desc = f"exhibits a measured difference-map shift of {candidates[0]['separation_arcsec']}\" ({candidates[0].get('classification', 'RESIDUAL')})"
    else:
        speed_desc = "remains nearly stationary relative to background stars"

    mol_names = ", ".join(f"{m['molecule']} ({m['wavelength_um']} μm)" for m in mol_features[:3]) if mol_features else "continuum stellar profile"

    plain_english_summary = (
        f"{target_name} ({object_type}) {speed_desc}. "
        f"Its infrared temperature is {temp_desc}. "
        f"In SPHEREx's 102-band infrared spectrum, key molecular tracers for this temperature class include {mol_names}. "
        f"Current multi-archive classification: {evidence_tier} ({candidate_status})."
    )

    cand_note = (
        f"{len(candidates)} residual source(s) measured (peak {candidates[0].get('snr', 'N/A')}σ at {candidates[0].get('separation_arcsec', 'N/A')}\" sep)"
        if candidates else "0 significant ZOGY/Bramich dipoles isolated in current field"
    )
    scientist_technical_summary = (
        f"ICRS ({ra_deg:.5f}°, {dec_deg:+.5f}°), FOV={fov:.1f}': μ={pm_arcsec:.3f}\"/yr"
        + (f", d={dist_pc} pc" if dist_pc else "")
        + (f", Teff={round(float(teff_k))} K ({spectrum.get('data_type', 'NONE')})" if teff_k else "")
        + (f", WISE W1-W2={w1_w2:+.2f} mag" if w1_w2 is not None else "")
        + f". Source discovery: {cand_note}. Evidence tier: {evidence_tier} — {verification.get('evidence_summary', '')}"
    )

    key_insights = [
        {
            "category": "Kinematics & Difference Imaging",
            "status": candidates[0]["classification"] if candidates else ("HIGH_PM" if pm_arcsec >= 1.0 else "STATIONARY"),
            "detail": cand_note + f" | Proper motion μ = {pm_arcsec:.3f}\"/yr."
        },
        {
            "category": "102-Band SPHEREx SED & Temperature",
            "status": spectrum.get("data_type", "NONE"),
            "detail": (
                f"Teff = {round(float(teff_k))} K; Expected molecular features: {mol_names}."
                if teff_k is not None else
                "No infrared SED photometry anchors available at this exact sky locus."
            )
        },
        {
            "category": "Multi-Archive Vetting (Gaia DR3 + SkyBoT + SPHEREx)",
            "status": evidence_tier,
            "detail": (
                f"{verification.get('evidence_summary', '')} "
                f"SPHEREx archive coverage: {spherex_cov.get('coverage_type', 'CHECKED')} ({spherex_cov.get('count', 0)} plane(s))."
            )
        }
    ]

    return {
        "status": "success",
        "coordinates": {"ra_deg": round(ra_deg, 6), "dec_deg": round(dec_deg, 6), "fov_arcmin": float(fov)},
        "target_name": target_name,
        "object_type": object_type,
        "evidence_tier": evidence_tier,
        "verdict": verdict,
        "candidate_status": candidate_status,
        "plain_english_summary": plain_english_summary,
        "scientist_technical_summary": scientist_technical_summary,
        "key_insights": key_insights,
        "source_discovery": discovery,
        "verification": verification,
        "molecular_signatures": mol_features,
        "checklist": checklist,
        "telemetry_metrics": {
            "proper_motion_arcsec_yr": round(pm_arcsec, 4),
            "temperature_k": teff_k,
            "distance_pc": dist_pc,
            "wise_w1_w2_color": w1_w2,
            "spectrum_data_type": spectrum.get("data_type", "NONE"),
            "spherex_coverage_type": spherex_cov.get("coverage_type"),
            "candidates_found": len(candidates),
        }
    }


def _answer_ai_question(synthesis: dict, question: str) -> dict:
    q = (question or "").lower()
    tname = synthesis["target_name"]
    metrics = synthesis["telemetry_metrics"]
    ver = synthesis["verification"]
    disc = synthesis["source_discovery"]
    cands = disc.get("candidates") or []
    mols = synthesis.get("molecular_signatures") or []

    if any(k in q for k in ("asteroid", "sso", "neossat", "gaia", "optical", "star")):
        gaia_item = next((c for c in ver.get("checklist", []) if c.get("id") == "gaia"), {})
        sso_item = next((c for c in ver.get("checklist", []) if c.get("id") == "sso"), {})
        answer = (
            f"Multi-archive optical & Solar System vetting for {tname}: "
            f"(1) Gaia DR3 check [{gaia_item.get('status', 'n/a')}]: {gaia_item.get('evidence', 'Checked')}. "
            f"(2) IMCCE SkyBoT / NEOSSat Solar System check [{sso_item.get('status', 'n/a')}]: {sso_item.get('evidence', 'Checked')}."
        )
        topic = "Optical & Asteroid Veto"
    elif any(k in q for k in ("spectrum", "band", "102", "water", "methane", "ch4", "h2o", "co2", "molecule", "dip")):
        mol_list = ", ".join(f"{m['molecule']} at {m['wavelength_um']} μm" for m in mols) if mols else "no specific narrow molecular absorption template matched"
        answer = (
            f"102-Band SPHEREx Spectroscopy (0.75–5.00 μm) for {tname}: "
            f"Data provenance is {metrics.get('spectrum_data_type')}. "
            + (f"Effective temperature Teff = {metrics['temperature_k']} K. " if metrics.get("temperature_k") else "")
            + f"Expected molecular absorption bands for this thermal class: {mol_list}. "
            + "Note: Band arrays A4 (2.42–3.82 μm), A5 (3.82–4.42 μm), and A6 (4.42–5.00 μm) probe H₂O ice, CH₄ methane, CO₂ ice, and CO."
        )
        topic = "102-Band Infrared Spectroscopy"
    elif any(k in q for k in ("scan", "dipole", "motion", "move", "speed", "proper")):
        cand_msg = (
            f"Automated difference-map scan isolated {len(cands)} candidate(s): "
            + "; ".join(f"{c['id']} ({c['classification']}, SNR={c.get('snr')}σ, sep={c.get('separation_arcsec')}\")" for c in cands)
            if cands else
            f"No isolated ZOGY dipole residual exceeded threshold ({disc.get('message') or 'stationary background'})."
        )
        answer = (
            f"Motion & Dipole Analysis for {tname}: Proper motion μ = {metrics['proper_motion_arcsec_yr']}\" /yr. "
            + cand_msg
        )
        topic = "Kinematics & Dipole Scan"
    elif any(k in q for k in ("planet", "brown dwarf", "cold", "why", "explain", "what")):
        answer = synthesis["plain_english_summary"]
        topic = "Astrophysical Interpretation"
    else:
        answer = f"{synthesis['plain_english_summary']} Technical summary: {synthesis['scientist_technical_summary']}"
        topic = "Co-Pilot Field Synthesis"

    return {
        "status": "success",
        "question": question,
        "topic": topic,
        "answer": answer,
        "evidence_tier": synthesis["evidence_tier"],
        "verdict": synthesis["verdict"],
        "candidate_status": synthesis["candidate_status"],
        "synthesis": synthesis,
    }


@app.get("/api/ai/analyze")
def ai_analyze_field(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    fov: float = Query(3.0, description="Field of View in arcminutes"),
    target: Optional[str] = Query(None, description="Benchmark target key")
):
    """Integrated AI Science Co-Pilot: synthesizes real difference imaging, Gaia DR3, SkyBoT, and 102-band SED telemetry."""
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return _build_ai_science_synthesis(ra_deg=ra_deg, dec_deg=dec_deg, fov=fov, target=target)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/ask")
def ai_ask_get(
    request: Request,
    ra: str = Query(..., description="Right Ascension"),
    dec: str = Query(..., description="Declination"),
    fov: float = Query(3.0, description="Field of View in arcminutes"),
    target: Optional[str] = Query(None, description="Benchmark target key"),
    question: str = Query("Explain this object in plain English", description="Natural-language science question"),
    api_key: Optional[str] = Query(None, description="Optional Google Gemini or OpenRouter API Key (BYOK)")
):
    """Interactive AI Science Co-Pilot Q&A backed 100% by real NASA/ESA archive telemetry."""
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        synthesis = _build_ai_science_synthesis(ra_deg=ra_deg, dec_deg=dec_deg, fov=fov, target=target)

        # Check OpenRouter first (configured in .env or supplied via header/query starting with sk-or-)
        or_key = (
            api_key if (api_key and "sk-or-" in api_key)
            else request.headers.get("x-openrouter-key")
            or os.environ.get("OPENROUTER_API_KEY")
        )
        if or_key and len(or_key.strip()) > 10:
            llm_res = _call_openrouter_api(or_key.strip(), synthesis, question)
            if llm_res:
                return llm_res

        # Check direct Gemini Key
        key = api_key or request.headers.get("x-gemini-key") or os.environ.get("GEMINI_API_KEY")
        if key and len(key.strip()) > 8:
            llm_res = _call_gemini_api(key.strip(), synthesis, question)
            if llm_res:
                return llm_res

        return _answer_ai_question(synthesis, question)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/ask")
def ai_ask_post(payload: AIAskRequest, request: Request):
    """Interactive AI Science Co-Pilot Q&A (POST) backed 100% by real NASA/ESA archive telemetry."""
    try:
        ra_deg, dec_deg = parse_celestial_coords(payload.ra, payload.dec)
        synthesis = _build_ai_science_synthesis(ra_deg=ra_deg, dec_deg=dec_deg, fov=payload.fov, target=payload.target)

        # Check OpenRouter first (configured in .env or supplied via payload/header)
        or_key = (
            payload.api_key if (payload.api_key and "sk-or-" in payload.api_key)
            else request.headers.get("x-openrouter-key")
            or os.environ.get("OPENROUTER_API_KEY")
        )
        if or_key and len(or_key.strip()) > 10:
            llm_res = _call_openrouter_api(or_key.strip(), synthesis, payload.question)
            if llm_res:
                return llm_res

        # Check direct Gemini Key
        key = payload.api_key or request.headers.get("x-gemini-key") or os.environ.get("GEMINI_API_KEY")
        if key and len(key.strip()) > 8:
            llm_res = _call_gemini_api(key.strip(), synthesis, payload.question)
            if llm_res:
                return llm_res

        return _answer_ai_question(synthesis, payload.question)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/csa/neossat")
def get_csa_neossat(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(3.0, description="Search radius in arcminutes (0.5 to 15.0)")
):
    """
    Task 4: CSA NEOSSat & CADC Asteroid Tracking Integration.
    Queries Canadian Astronomy Data Centre (CADC) for Canadian Space Agency NEOSSat
    observations and computes Near-Earth Object / asteroid vs Planet X discrimination.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        rad = float(radius) if isinstance(radius, (int, float, str)) else 3.0
        return query_csa_neossat(ra=ra_deg, dec=dec_deg, radius_arcmin=rad)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resources_codex")
def get_resources_codex(
    ra: str = Query("133.79513", description="Current Right Ascension"),
    dec: str = Query("-7.24515", description="Current Declination"),
    fov: float = Query(3.0, description="Current Field of View in arcminutes")
):
    """Task 5: Official NASA, IPAC, MAST, WiseView, CSA NEOSSat & CADC Resources Codex with live coordinate queries."""
    ra_deg, dec_deg = parse_celestial_coords(ra, dec)
    links = build_portal_links(ra_deg, dec_deg, fov)
    return {
        "status": "success",
        "coordinates": {"ra_deg": ra_deg, "dec_deg": dec_deg, "fov_arcmin": fov},
        "links": links,
        "portals": [
            {
                "id": "irsa_spherex",
                "title": "1. NASA/IPAC IRSA SPHEREx Archive",
                "agency": "NASA / Caltech-IPAC",
                "url": "https://irsa.ipac.caltech.edu/Missions/spherex.html",
                "explorer_url": links["irsa_spherex"],
                "role": "102-band Linear Variable Filter (0.75–5.0 μm) all-sky spectrophotometry, L2 quality bitmasks & AWS S3 cloud FITS.",
                "query_lang": "ADQL (IRSA TAP)",
                "query_snippet": (
                    f"SELECT 'https://irsa.ipac.caltech.edu/' || a.uri || '?center=' || p.ra || ',' || p.dec || 'd&size=0.1' AS uri,\n"
                    f"       p.energy_bandpassname, p.time_bounds_lower\n"
                    f"FROM spherex.artifact a JOIN spherex.plane p ON a.planeid = p.planeid\n"
                    f"WHERE 1 = CONTAINS(POINT('ICRS', {ra_deg:.5f}, {dec_deg:.5f}), p.poly)\n"
                    f"ORDER BY p.time_bounds_lower"
                )
            },
            {
                "id": "ipac_tutorials",
                "title": "2. Caltech-IPAC SPHEREx Python Tutorials",
                "agency": "Caltech-IPAC",
                "url": "https://caltech-ipac.github.io/irsa-tutorials/spherex/",
                "explorer_url": "https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-products/",
                "role": "Source Discovery Tool Demo (Alard-Lupton image subtraction), wavelength-dependent PSF extraction & HiPS spectral cubes.",
                "query_lang": "Python (PyVO)",
                "query_snippet": (
                    f"import pyvo as vo\n"
                    f"tap = vo.dal.TAPService('https://irsa.ipac.caltech.edu/TAP')\n"
                    f"res = tap.search(\"SELECT TOP 10 * FROM spherex.plane WHERE 1=CONTAINS(POINT('ICRS',{ra_deg:.5f},{dec_deg:.5f}),poly)\")"
                )
            },
            {
                "id": "wiseview",
                "title": "3. Backyard Worlds WiseView Comparator",
                "agency": "NASA Citizen Science / Dan Caselden",
                "url": links["wiseview"],
                "explorer_url": links["wiseview_difference"],
                "role": "14+ years of unWISE time-resolved W1 (3.4 μm) & W2 (4.6 μm) co-adds with AsinhStretch and dipole difference blinking.",
                "query_lang": "Deep-Link URL",
                "query_snippet": links["wiseview"]
            },
            {
                "id": "mast_gaia",
                "title": "4. STScI MAST & ESA Gaia DR3 Archive",
                "agency": "STScI / ESA",
                "url": "https://archive.stsci.edu/missions-and-data/gaia",
                "explorer_url": links["mast_portal"],
                "role": "1.8 billion optical stars with micro-arcsecond proper motion vectors (pmra, pmdec), parallax & optical dropout vetting.",
                "query_lang": "ADQL (Gaia DR3 TAP)",
                "query_snippet": (
                    f"SELECT TOP 50 source_id, ra, dec, pmra, pmdec, parallax, phot_g_mean_mag\n"
                    f"FROM gaia_dr3_source\n"
                    f"WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra_deg:.5f}, {dec_deg:.5f}, {fov/60.0:.4f})) = 1\n"
                    f"ORDER BY phot_g_mean_mag ASC"
                )
            },
            {
                "id": "csa_neossat",
                "title": "5. CSA NEOSSat Space Telescope Mission",
                "agency": "Canadian Space Agency (CSA)",
                "url": "https://www.asc-csa.gc.ca/eng/satellites/neossat/",
                "explorer_url": links["csa_neossat_dataset"],
                "role": "15 cm f/5.88 Maksutov space telescope in sun-synchronous orbit tracking Near-Earth Asteroids (NEOs) & comets.",
                "query_lang": "Open Data Portal",
                "query_snippet": "https://data.asc-csa.gc.ca/dataset/neossat"
            },
            {
                "id": "cadc_archive",
                "title": "6. Canadian Astronomy Data Centre (CADC)",
                "agency": "NRC Canada / CADC",
                "url": "https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/",
                "explorer_url": links["cadc_neossat_search"],
                "role": "CAOM-2 TAP programmatic archive hosting calibrated NEOSSat science FITS exposures and DataLink products.",
                "query_lang": "ADQL (CADC CAOM-2 TAP)",
                "query_snippet": (
                    f"SELECT TOP 25 o.observationID, o.target_name, p.time_bounds_lower, p.time_exposure\n"
                    f"FROM caom2.Observation AS o JOIN caom2.Plane AS p ON o.obsID = p.obsID\n"
                    f"WHERE o.collection = 'NEOSSAT' AND o.intent = 'science'\n"
                    f"  AND INTERSECTS(CIRCLE('ICRS', {ra_deg:.5f}, {dec_deg:.5f}, 0.50), p.position_bounds) = 1\n"
                    f"ORDER BY p.time_bounds_lower DESC"
                )
            },
            {
                "id": "neossat_tutorial",
                "title": "7. CSA NEOSSAT_Tutorial GitHub Pipeline",
                "agency": "CSA Open Source",
                "url": "https://github.com/asc-csa/NEOSSAT_Tutorial",
                "explorer_url": links["csa_neossat_tutorial"],
                "role": "Official Python notebooks for overscan/dark subtraction, temporal median stacking & Line Segment Detector (LSD) streaklets.",
                "query_lang": "Python (astroquery.cadc)",
                "query_snippet": (
                    f"from astroquery.cadc import Cadc\n"
                    f"from astropy.coordinates import SkyCoord\n"
                    f"import astropy.units as u\n"
                    f"cadc = Cadc()\n"
                    f"results = cadc.query_region(SkyCoord({ra_deg:.5f}, {dec_deg:.5f}, unit='deg'), radius=0.5*u.deg, collection='NEOSSAT')"
                )
            }
        ]
    }

@app.get("/api/download_fits")
def download_fits(
    target: Optional[str] = Query(None, description="Benchmark target key"),
    ra: Optional[str] = Query(None, description="Right Ascension"),
    dec: Optional[str] = Query(None, description="Declination"),
    epoch: int = Query(1, description="Epoch 1 (2MASS) or Epoch 2 (DSS2/SPHEREx)")
):
    """Streams authentic NASA scientific FITS file for requested target/coordinates & epoch."""
    import glob
    survey_suffix = "2mass.fits" if epoch == 1 else "dss2.fits"
    dyn_dir = os.path.join(os.path.dirname(__file__), "cache", "dynamic_fits")
    fits_dir = os.path.join(os.path.dirname(__file__), "cache", "fits")

    target_ra = None
    target_dec = None
    target_name = "target"

    if target and target.lower() in BENCHMARKS:
        b = BENCHMARKS[target.lower()]
        target_ra = b["ra"]
        target_dec = b["dec"]
        target_name = target.lower()
    elif ra and dec:
        target_ra, target_dec = parse_celestial_coords(ra, dec)
        target_name = f"sky_{target_ra:.4f}_{target_dec:.4f}"

    # 1. Search dynamic_fits by coordinate string
    if target_ra is not None and target_dec is not None and os.path.exists(dyn_dir):
        ra_str = f"{target_ra:.4f}"
        pattern = os.path.join(dyn_dir, f"*{ra_str}*{survey_suffix}")
        matches = glob.glob(pattern)
        if matches:
            filename = f"spherex_{target_name}_epoch{epoch}_{survey_suffix}"
            return FileResponse(matches[0], media_type="application/fits", filename=filename)

    # 2. Search fits dir by target name
    if target and os.path.exists(fits_dir):
        p = os.path.join(fits_dir, f"{target.lower()}_{survey_suffix}")
        if os.path.exists(p):
            filename = f"spherex_{target.lower()}_epoch{epoch}_{survey_suffix}"
            return FileResponse(p, media_type="application/fits", filename=filename)

    # 3. If any FITS file in dynamic_fits matches epoch, return most recent
    if os.path.exists(dyn_dir):
        matches = sorted(glob.glob(os.path.join(dyn_dir, f"*{survey_suffix}")), key=os.path.getmtime, reverse=True)
        if matches:
            filename = f"spherex_field_epoch{epoch}_{survey_suffix}"
            return FileResponse(matches[0], media_type="application/fits", filename=filename)

    raise HTTPException(status_code=404, detail="Requested FITS file not found in telescope archive.")

@app.get("/api/scene")
def get_scene(
    target: Optional[str] = Query(None, description="Preset target key (e.g. wise0855, barnard, epsindi)"),
    ra: Optional[str] = Query(None, description="Right Ascension in decimal deg or sexagesimal"),
    dec: Optional[str] = Query(None, description="Declination in decimal deg or sexagesimal"),
    fov: float = Query(3.0, description="Field of view in arcminutes (0.5 to 15.0)")
):
    """
    Returns the single source of truth 'scene' object:
    Target Metadata, Propagated Epochs List, and Interactive Layers List.
    """
    try:
        ra_val, dec_val = None, None
        if isinstance(ra, str) and isinstance(dec, str):
            ra_val, dec_val = parse_celestial_coords(ra, dec)

        target_key = target if isinstance(target, str) else None
        fov_val = float(fov) if isinstance(fov, (int, float, str)) and type(fov).__name__ != 'Query' else 3.0

        return get_target_scene(
            target_key=target_key,
            ra=ra_val,
            dec=dec_val,
            fov_arcmin=fov_val
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/catalog/2mass")
def get_2mass_catalog(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(3.0, description="Search radius in arcminutes (0.2 to 15.0)"),
    limit: int = Query(50, description="Maximum number of sources to return (1 to 200)")
):
    """
    Queries NASA IRSA 2MASS Point Source Catalog (PSC) for near-infrared
    J (1.25 μm), H (1.65 μm), and Ks (2.17 μm) photometry and color indices.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return query_2mass_psc(ra=ra_deg, dec=dec_deg, radius_arcmin=radius, limit=limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/catalog/simbad")
def get_simbad_metadata(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(3.0, description="Search radius in arcminutes")
):
    """
    Queries CDS Strasbourg SIMBAD database for canonical astronomical object identification,
    morphological and spectral classifications, and literature citation counts.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return query_simbad_metadata(ra=ra_deg, dec=dec_deg, radius_arcmin=radius)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/catalog/crossmatch")
def get_crossmatched_photometry(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(3.0, description="Search radius in arcminutes")
):
    """
    Performs unified optical-to-infrared photometric cross-matching across Gaia DR3, 2MASS,
    WISE/NEOWISE, SPHEREx DR1, and SIMBAD. Computes diagnostic color baselines (G - Ks, J - Ks, W1 - W2)
    to flag Brown Dwarfs and Planet X candidates.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return crossmatch_photometry(ra=ra_deg, dec=dec_deg, radius_arcmin=radius)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _run_catalog_cone(fn, ra: str, dec: str, radius: float):
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return fn(ra=ra_deg, dec=dec_deg, radius_arcmin=radius)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/catalog/wise")
def get_wise_catalog(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(3.0, description="Search radius in arcminutes")
):
    """
    Queries NASA AllWISE (`allwise_p3as_psd`, fallback Harvard CfA VizieR `II/328/allwise`)
    and NEOWISE-R (`neowiser_p1bs_psd`) for W1-W4 magnitudes, microJansky fluxes, and epochs.
    """
    return _run_catalog_cone(query_wise_catalog, ra, dec, radius)


@app.get("/api/catalog/spherex")
def get_spherex_archive(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(15.0, description="Search radius in arcminutes")
):
    """
    Queries NASA IRSA SPHEREx DR1 (`spherex.obscore`) for spectral coverage planes
    (0.75 - 5.00 um) with calibrated DR1 reference plane fallback when 0 cone hits exist.
    """
    return _run_catalog_cone(query_spherex_archive, ra, dec, radius)

@app.get("/api/discoveries")
def get_discoveries(
    object_type: Optional[str] = Query(None, description="Filter by object type"),
    limit: int = Query(50, description="Max entries to return")
):
    """Returns community discoveries logged by users, with optional filtering."""
    if os.path.exists(DISCOVERIES_FILE):
        try:
            with open(DISCOVERIES_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)
                if object_type and isinstance(object_type, str):
                    items = [it for it in items if object_type.lower() in str(it.get("object_type", "")).lower()]
                lim = limit if isinstance(limit, int) else 50
                return items[:lim]
        except Exception:
            return []
    return []

@app.post("/api/flag")
def flag_candidate(candidate: DiscoveryCandidate):
    """
    Logs a citizen science candidate discovery into the community ledger.
    Automatically cross-references multi-survey archives (Gaia DR3, 2MASS, SIMBAD)
    and evaluates Planet X / Brown Dwarf color criteria.
    """
    discoveries = []
    if os.path.exists(DISCOVERIES_FILE):
        try:
            with open(DISCOVERIES_FILE, "r", encoding="utf-8") as f:
                discoveries = json.load(f)
        except Exception:
            discoveries = []

    # Harmonize naming between frontend & swagger contracts
    target_name = candidate.target_name or candidate.candidate_name or f"Candidate at {candidate.ra:.4f}, {candidate.dec:.4f}"
    obj_type = candidate.object_type or candidate.motion_type or "High Proper Motion Transient"
    cand_id = f"SPX-2026-{uuid.uuid4().hex[:6].upper()}"

    # Auto-crossmatch with multi-wavelength archives
    try:
        xmatch = crossmatch_photometry(ra=candidate.ra, dec=candidate.dec, radius_arcmin=1.5)
        is_ultracold = xmatch.get("color_diagnostics", {}).get("is_ultracold_candidate", False)
        g_k_color = xmatch.get("color_diagnostics", {}).get("optical_g_minus_infrared_k")
        simbad_match = xmatch.get("simbad_classification", {}).get("canonical_name", "Uncataloged Source")
        spectral_type = xmatch.get("simbad_classification", {}).get("spectral_type", "Unknown")
        verif_status = "CONFIRMED_ULTRACOLD" if is_ultracold else "PENDING_VERIFICATION"
    except Exception:
        is_ultracold = False
        g_k_color = None
        simbad_match = "Survey Query Pending"
        spectral_type = "Unknown"
        verif_status = "LOGGED"

    entry = {
        "candidate_id": cand_id,
        "target_name": target_name,
        "candidate_name": target_name,
        "ra": candidate.ra,
        "dec": candidate.dec,
        "object_type": obj_type,
        "motion_type": obj_type,
        "user_handle": candidate.user_handle or candidate.astronomer or "@citizen_scientist",
        "astronomer": candidate.astronomer or candidate.user_handle or "@citizen_scientist",
        "notes": candidate.notes or "",
        "proper_motion_mas": candidate.proper_motion_mas,
        "confidence": candidate.confidence or 5,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scientific_validation": {
            "is_ultracold_candidate": is_ultracold,
            "optical_infrared_g_minus_ks": g_k_color,
            "simbad_counterpart": simbad_match,
            "spectral_classification": spectral_type,
            "verification_status": verif_status
        }
    }

    discoveries.insert(0, entry)

    with open(DISCOVERIES_FILE, "w", encoding="utf-8") as f:
        json.dump(discoveries[:100], f, indent=2)

    return {"status": "recorded", "candidate_id": cand_id, "entry": entry}

@app.get("/api/discoveries/export/csv")
def export_discoveries_csv():
    """Exports all logged citizen science discoveries as a CSV spreadsheet."""
    discoveries = []
    if os.path.exists(DISCOVERIES_FILE):
        try:
            with open(DISCOVERIES_FILE, "r", encoding="utf-8") as f:
                discoveries = json.load(f)
        except Exception:
            discoveries = []

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Candidate_ID", "Timestamp_UTC", "Target_Name", "RA_deg", "Dec_deg",
        "Object_Type", "User_Handle", "Confidence", "Proper_Motion_mas_yr",
        "Optical_IR_G_minus_Ks", "SIMBAD_Match", "Spectral_Type", "Status", "Notes"
    ])

    for d in discoveries:
        sci = d.get("scientific_validation", {})
        writer.writerow([
            d.get("candidate_id", ""),
            d.get("timestamp", ""),
            d.get("target_name", ""),
            d.get("ra", ""),
            d.get("dec", ""),
            d.get("object_type", ""),
            d.get("user_handle", ""),
            d.get("confidence", ""),
            d.get("proper_motion_mas", ""),
            sci.get("optical_infrared_g_minus_ks", ""),
            sci.get("simbad_counterpart", ""),
            sci.get("spectral_classification", ""),
            sci.get("verification_status", ""),
            d.get("notes", "")
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=spherex_hunter_discoveries.csv"}
    )

@app.delete("/api/discoveries/{candidate_id}")
def delete_discovery(candidate_id: str):
    """Deletes a candidate by ID."""
    if os.path.exists(DISCOVERIES_FILE):
        try:
            with open(DISCOVERIES_FILE, "r", encoding="utf-8") as f:
                discoveries = json.load(f)
            original_len = len(discoveries)
            discoveries = [d for d in discoveries if d.get("candidate_id") != candidate_id]
            if len(discoveries) < original_len:
                with open(DISCOVERIES_FILE, "w", encoding="utf-8") as f:
                    json.dump(discoveries, f, indent=2)
                return {"status": "deleted", "candidate_id": candidate_id}
        except Exception:
            pass
    raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

if __name__ == "__main__":
    import uvicorn
    print("Starting SPHEREx Hunter Astronomical Backend on http://localhost:8000...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
