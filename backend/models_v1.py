"""
🛰️ SPHEREx Hunter - Pydantic v2 API Data Contracts (v1)
NASA Space Apps Challenge 2026 - Team RIP

Provides strictly typed, validated models for:
- RFC 7807 Problem Details for all error responses
- Physical quantities with explicit units, uncertainties, and provenance
- Benchmark target scenes, space-motion propagation, and exposure lists
- Precomputed & live forced photometry, light curves, and difference imaging
- Dynamic scientific validation metrics and citizen science candidate tracking
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# ==============================================================================
# 1. CORE SCIENTIFIC PRIMITIVES & RFC 7807 ERROR SPECIFICATION
# ==============================================================================

class PhysicalQuantity(BaseModel, Generic[T]):
    """Physical quantity with explicit unit, uncertainty, and source."""
    model_config = ConfigDict(extra="forbid")

    value: Optional[T] = Field(None, description="Physical scalar or array value")
    unit: str = Field(..., description="Standard unit string (e.g. 'uJy', 'mag (AB)', 'um', 'arcsec')")
    uncertainty: Optional[float] = Field(None, description="1-sigma uncertainty in the same unit where applicable")
    source: Optional[str] = Field(None, description="Provenance source or derivation method")


class ProblemDetails(BaseModel):
    """
    RFC 7807 Problem Details representation for HTTP API errors.
    Returned with Content-Type: application/problem+json
    """
    model_config = ConfigDict(extra="allow")

    type: str = Field("about:blank", description="URI identifying the problem type")
    title: str = Field(..., description="Short human-readable summary of the problem")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Detailed explanation specific to this occurrence")
    instance: Optional[str] = Field(None, description="URI reference identifying the specific occurrence")
    request_id: str = Field(..., description="Unique request tracing ID (X-Request-Id)")
    retryable: bool = Field(False, description="Whether client should safely retry after backoff")
    code: str = Field(..., description="Machine-readable error identifier (e.g. BAND_MISMATCH, NO_PUBLIC_DATA)")


# ==============================================================================
# 2. CAPABILITIES, STATUS, & HEALTH
# ==============================================================================

class FeatureCapability(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool
    reason: Optional[str] = None


class CapabilitiesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = Field("6.0.0", description="Pipeline semantic version")
    api_version: str = Field("v1", description="API contract major version")
    git_hash: str = Field(..., description="Current Git deployment commit hash")
    environment: str = Field("production", description="Runtime environment")
    capabilities: Dict[str, FeatureCapability] = Field(
        ...,
        description="Dictionary of features and their availability state"
    )


class ArchiveReachability(BaseModel):
    model_config = ConfigDict(extra="forbid")
    irsa_reachable: bool
    cadc_reachable: bool
    skybot_reachable: bool
    latency_ms: Dict[str, float]


class StatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str = Field("ok", description="'ok' or 'degraded'")
    ready: bool = Field(True, description="System readiness for serving requests")
    cache: Dict[str, Any] = Field(..., description="Local RAM and disk cache metrics")
    archive: ArchiveReachability = Field(..., description="External archive network health")


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str = Field("ok", description="Liveness status")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")


# ==============================================================================
# 3. TARGETS & BENCHMARKS
# ==============================================================================

class SpaceMotion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pm_ra_cosdec_mas_yr: Optional[float] = Field(None, description="Proper motion in RA * cos(Dec) in mas/yr")
    pm_dec_mas_yr: Optional[float] = Field(None, description="Proper motion in Dec in mas/yr")
    parallax_mas: Optional[float] = Field(None, description="Parallax in milliarcseconds")
    radial_velocity_km_s: Optional[float] = Field(None, description="Radial velocity in km/s")
    epoch_ref: float = Field(2016.0, description="Reference epoch for astrometry (e.g. 2016.0 for Gaia DR3)")
    source: Optional[str] = Field("Gaia DR3 / Kirkpatrick et al. (2014)", description="Catalog citation")


class TargetSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(..., description="Target slug / identifier (e.g. 'wise0855')")
    name: str = Field(..., description="Official target name")
    ra_deg: float = Field(..., description="Right Ascension in ICRS decimal degrees")
    dec_deg: float = Field(..., description="Declination in ICRS decimal degrees")
    ra_sexagesimal: Optional[str] = Field(None, description="RA in HH:MM:SS.ss")
    dec_sexagesimal: Optional[str] = Field(None, description="Dec in +DD:MM:SS.s")
    target_type: str = Field(..., description="Astrophysical classification")
    description: str = Field(..., description="Scientific significance summary")
    public_exposures_count: int = Field(..., description="Count of public SPHEREx exposures available")
    has_demo_cache: bool = Field(..., description="True if target has precomputed demo cache")


class TargetDetail(TargetSummary):
    model_config = ConfigDict(extra="forbid")
    space_motion: Optional[SpaceMotion] = None
    known_mag_ab: Optional[Dict[str, float]] = Field(default_factory=dict, description="Known apparent magnitudes")
    citations: List[str] = Field(default_factory=list, description="Academic literature citations")


# ==============================================================================
# 4. SCENE GRAPH & SPACE-MOTION PROPAGATION
# ==============================================================================

class SceneLayer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(..., description="Unique layer identifier")
    name: str = Field(..., description="Layer display name")
    type: str = Field(..., description="'reference' | 'science' | 'difference' | 'catalog' | 'orbit_track'")
    visible: bool = Field(True, description="Default layer visibility")
    opacity: float = Field(1.0, description="Default opacity [0.0, 1.0]")
    fits_url: Optional[str] = None
    png_url: Optional[str] = None
    epoch_mjd: Optional[float] = None
    wavelength_um: Optional[float] = None
    detector: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SceneEpoch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mjd: float
    utc: str
    exposure_id: str
    detector: int
    wavelength_um: float
    band: str
    propagated_ra_deg: Optional[float] = None
    propagated_dec_deg: Optional[float] = None
    in_fov: bool = Field(True, description="Whether target is inside SPHEREx field of view at this epoch")


class SceneResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target: TargetDetail
    fov_arcmin: float
    epochs: List[SceneEpoch]
    layers: List[SceneLayer]
    warnings: List[str] = Field(default_factory=list, description="Astronomical caveats or FOV notices")
    provenance: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# 5. PUBLIC EXPOSURES
# ==============================================================================

class ExposureItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    exposure_id: str = Field(..., description="Unique exposure ID")
    mjd: float = Field(..., description="Mid-exposure MJD")
    utc: Optional[str] = Field(None, description="ISO 8601 UTC timestamp")
    detector: int = Field(..., description="SPHEREx detector array (1-6)")
    band: str = Field(..., description="Band name e.g. 'Band 6 (4.42 μm)'")
    wavelength_um: Optional[float] = Field(None, description="Central wavelength in microns")
    wavelength_at_target_um: Optional[float] = Field(None)
    spatial_containment: Optional[str] = Field("fully_contained", description="'fully_contained' | 'partially_contained' | 'edge'")
    exptime_s: Optional[float] = Field(120.0, description="Exposure duration in seconds")
    download_url: Optional[str] = Field(None, description="Direct IRSA FITS download URL")
    preview_url: Optional[str] = Field(None, description="Cached PNG cutout URL")
    matched_pair_id: Optional[str] = None
    s_region: Optional[str] = None
    # Enhanced Fields for Multi-Epoch Archival Stacks (v2 Specification: Step 4 / Amendments A3, A4)
    instrument: Optional[str] = Field("SPHEREx", description="Observing instrument (e.g. 'SPHEREx', '2MASS', 'WISE')")
    survey_release: Optional[str] = Field("DR1", description="Survey data release (e.g. 'DR1', 'AllWISE', 'unWISE')")
    is_coadd: Optional[bool] = Field(False, description="Whether product is a multi-exposure coadd or narrowband stack")
    mjd_mean: Optional[float] = Field(None, description="Mean observation MJD")
    mjd_min: Optional[float] = Field(None, description="Start MJD of observation range")
    mjd_max: Optional[float] = Field(None, description="End MJD of observation range")
    n_exposures: Optional[int] = Field(None, description="Number of stacked exposures if coadd/stack")
    stack_snr: Optional[float] = Field(None, description="Combined stack signal-to-noise ratio")
    channel_id: Optional[int] = Field(None, description="SPHEREx channel ID (1-102)")


class ExposuresResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    target_id: str
    status: str = Field("ok", description="'ok' | 'no_public_data'")
    total_found: Optional[int] = Field(None, description="Total exposures count")
    count_public_total: Optional[int] = None
    count_precomputed_used: Optional[int] = None
    exposures: List[ExposureItem]
    reason: Optional[str] = None
    unavailable_code: Optional[str] = None
    unavailable_reason: Optional[str] = None
    archive_version: str = Field("IRSA spherex.obscore 2026", description="Archive catalog queried")
    provenance: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# 6. CUTOUTS & RAW DATA
# ==============================================================================

class CutoutRawHeaderResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dimensions: List[int] = Field(..., description="[height, width] in pixels")
    dtype: str = Field("float32", description="Binary element type")
    units: str = Field("microjansky / pixel", description="Flux calibration unit")
    crpix: List[float] = Field(..., description="WCS reference pixel [x, y] (1-based)")
    crval: List[float] = Field(..., description="WCS celestial reference [RA, Dec] in degrees")
    cdelt: List[float] = Field(..., description="Pixel scale in degrees per pixel [dRA, dDec]")
    nan_convention: str = Field("IEEE 754 NaN indicates unobserved out-of-coverage pixels")


# ==============================================================================
# 7. DIFFERENCE IMAGING
# ==============================================================================

class DifferenceEpoch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    exposure_id: str
    mjd: float
    detector: int
    band: str
    wavelength_um: float


class DifferenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    valid: bool
    status: str = Field("success", description="'success' | 'rejected'")
    method: str = Field("ZOGY (Zackay, Ofek, & Gal-Yam 2016)", description="Subtraction algorithm")
    epoch_a: DifferenceEpoch
    epoch_b: DifferenceEpoch
    band_matched: bool
    scorr_max: Optional[float] = None
    scorr_min: Optional[float] = None
    scorr_mean: Optional[float] = None
    scorr_std: Optional[float] = None
    mismatch_reason: Optional[str] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# 8. PHOTOMETRY & LIGHT CURVES
# ==============================================================================

class BandPhotometry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    band_id: str
    wavelength_um: float
    flux: PhysicalQuantity[float]
    mag_ab: PhysicalQuantity[float]
    snr: float
    method: str = Field("circular_aperture_3.5pix", description="Photometry extraction method")


class PhotometryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_id: str
    target_name: str
    ra_deg: float
    dec_deg: float
    bands: List[BandPhotometry]
    provenance: Dict[str, Any] = Field(default_factory=dict)


class LightCurvePoint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mjd: float
    utc: str
    wavelength_um: float
    flux: PhysicalQuantity[float]
    mag_ab: PhysicalQuantity[float]
    exposure_id: str


class LightCurveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_id: str
    selection_rule: str = Field(..., description="Calibration rule e.g. 'Like-wavelength exposures only'")
    points: List[LightCurvePoint]
    provenance: Dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# 9. CANDIDATES & CITIZEN SCIENCE FLAGGING
# ==============================================================================

class CandidateItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_id: str
    ra_deg: float
    dec_deg: float
    x_pix: float
    y_pix: float
    snr: float
    flux_ujy: Optional[float] = None
    evidence_tier: str = Field("UNKNOWN_RAPID_MOVER", description="Strict evidence tier string")
    veto_status: str = Field("PASSED", description="'PASSED' | veto rejection reason")
    notes: Optional[str] = None


class CandidatesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_id: str
    total: int
    candidates: List[CandidateItem]
    notes: str = Field("Real pipeline candidates or empty list when no significant detections exist.")
    provenance: Dict[str, Any] = Field(default_factory=dict)


class FlagCandidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_id: Optional[str] = None
    target_id: str
    ra_deg: float = Field(..., ge=0.0, le=360.0)
    dec_deg: float = Field(..., ge=-90.0, le=90.0)
    category: str = Field(..., description="'mover' | 'transient' | 'known_sso' | 'artifact' | 'variable_star'")
    notes: Optional[str] = ""
    user_id: Optional[str] = "@citizen_scientist"


class FlagCandidateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str = "recorded"
    flag_id: str
    candidate_id: Optional[str] = None
    recorded_at: str
    duplicate: bool = False


# ==============================================================================
# 10. SCIENTIFIC VALIDATION METRICS
# ==============================================================================

class ValidationMetric(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    value: Any
    unit: Optional[str] = None
    status: str = Field("verified", description="'verified' | 'under_review' | 'pending'")
    description: str


class ValidationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pipeline_version: str = "6.0.0"
    metrics: List[ValidationMetric]
    audit_reports: List[Dict[str, str]]
    last_updated: str


# ==============================================================================
# 11. SEARCH & TARGET DISCOVERY
# ==============================================================================

class SearchResultItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    name: str
    ra_deg: float
    dec_deg: float
    category: str
    description: str


class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str
    results: List[SearchResultItem]
