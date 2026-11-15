"""
🛰️ SPHEREx Hunter - Pixel Quality Bitmask & DQ Flag Engine
NASA Space Apps Challenge 2026 - Team RIP

Provides standard SPHEREx Level-2 flag definitions, mask construction,
and pixel sanitization functions for scientific image differencing.
"""

from enum import IntFlag

import numpy as np


class SPHERExFlag(IntFlag):
    """29-bit quality and artifact plane definitions from HDU 2 (FLAGS)."""
    TRANSIENT     = 1 << 0    # 1: Radiation hit or unconfirmed transient spike
    OVERFLOW      = 1 << 1    # 2: Charge well overflow / detector saturation
    SUR_ERROR     = 1 << 2    # 4: Sample-up-the-ramp fit slope error
    NONFUNC       = 1 << 6    # 64: Dead or non-functional detector pixel
    DICHROIC      = 1 << 7    # 128: Low efficiency near dichroic boundary
    MISSING_DATA  = 1 << 9    # 512: Telemetry missing or unobserved pixel
    HOT           = 1 << 10   # 1024: Known high dark current hot pixel
    COLD          = 1 << 11   # 2048: Known unresponsive cold pixel
    FULLSAMPLE    = 1 << 12   # 4096: Saturated on initial Fowler sample
    PHANMISS      = 1 << 14   # 16384: Phantom missing read
    NONLINEAR     = 1 << 15   # 32768: Non-linear detector response regime
    PERSIST       = 1 << 17   # 131072: Latent charge persistence from prior frame
    OUTLIER       = 1 << 19   # 524288: Statistical temporal/spatial sigma outlier
    CROSSTALK     = 1 << 20   # 1048576: Electronic crosstalk from adjacent channel
    SOURCE        = 1 << 21   # 2097152: Real cataloged astrophysical star/galaxy
    GHOST         = 1 << 22   # 4194304: Internal optical reflection ghost
    GHOST_FPA     = 1 << 23   # 8388608: Focal plane array reflection ghost
    GHOST_EXT     = 1 << 24   # 16777216: External baffle optical scatter
    STREAK        = 1 << 25   # 33554432: Satellite streak trail
    BLOOM         = 1 << 26   # 67108864: Saturated charge spillover blooming
    SNOWBALL      = 1 << 27   # 134217728: High-energy cosmic ray particle shower
    HALO          = 1 << 28   # 268435456: Saturated star optical diffraction halo


# Critical bad pixel mask: pixels that must be masked to NaN before differencing
# Explicitly EXCLUDES SOURCE (21), DICHROIC (7), PERSIST (17), HALO (28)
CRITICAL_BAD_MASK = (
    SPHERExFlag.TRANSIENT
    | SPHERExFlag.OVERFLOW
    | SPHERExFlag.SUR_ERROR
    | SPHERExFlag.NONFUNC
    | SPHERExFlag.MISSING_DATA
    | SPHERExFlag.HOT
    | SPHERExFlag.COLD
    | SPHERExFlag.FULLSAMPLE
    | SPHERExFlag.OUTLIER
    | SPHERExFlag.STREAK
    | SPHERExFlag.BLOOM
    | SPHERExFlag.SNOWBALL
)


def apply_pixel_mask(
    image: np.ndarray,
    flags: np.ndarray,
    bad_mask: int = CRITICAL_BAD_MASK
) -> tuple[np.ndarray, np.ndarray]:
    """
    Applies quality bitmask to image data, setting invalid pixels to NaN.

    Args:
        image: 2D float array of pixel flux / surface brightness
        flags: 2D int32 array of bitmask flags from HDU 2 (FLAGS)
        bad_mask: Integer bitmask identifying fatal defects (default: CRITICAL_BAD_MASK)

    Returns:
        tuple of (cleaned_image, coverage_mask)
        cleaned_image: Image with bad pixels replaced by np.nan
        coverage_mask: Boolean array where True indicates valid coverage (not NaN)
    """
    is_bad = (flags & bad_mask) != 0
    cleaned = image.copy()
    cleaned[is_bad] = np.nan

    # Also mask any pre-existing NaNs or Infs
    is_invalid = np.isnan(cleaned) | np.isinf(cleaned)
    cleaned[is_invalid] = np.nan
    coverage_mask = ~is_invalid

    return cleaned, coverage_mask
