"""
🛰️ SPHEREx Hunter - Coordinate & Target Input Validation
NASA Space Apps Challenge 2026 - Team RIP

Provides rigorous validation and sanitization for all astronomical coordinates,
search radii, and target identifier strings before constructing ADQL/TAP queries
or invoking remote archives.
"""

import re
from typing import Optional, Tuple

from fastapi import HTTPException

# Allowed characters for target identifier strings: alphanumeric, space, +, -, _, ., (), ', /
TARGET_NAME_REGEX = re.compile(r"^[a-zA-Z0-9\s\+\-\_\.\(\)\'\/]+$")


def validate_coordinates(
    ra: float,
    dec: float,
    radius_arcmin: Optional[float] = None,
    max_radius_arcmin: float = 60.0
) -> Tuple[float, float, Optional[float]]:
    """
    Validates and bounds-checks astronomical equatorial coordinates (ICRS / J2000).

    Args:
        ra: Right Ascension in decimal degrees [0.0, 360.0)
        dec: Declination in decimal degrees [-90.0, +90.0]
        radius_arcmin: Optional search radius in arcminutes (0.0, max_radius_arcmin]
        max_radius_arcmin: Maximum permitted search radius (default 60 arcmin)

    Returns:
        Tuple of (clean_ra, clean_dec, clean_radius)

    Raises:
        HTTPException(400) if any coordinate violates physical celestial bounds.
    """
    try:
        clean_ra = float(ra)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid RA: must be a valid float.")

    try:
        clean_dec = float(dec)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid Dec: must be a valid float.")

    if not (0.0 <= clean_ra < 360.0):
        # Handle wraparound gracefully if slightly out of bounds (e.g. 360.0001 -> 0.0001)
        if 360.0 <= clean_ra < 360.001:
            clean_ra = clean_ra % 360.0
        elif -0.001 < clean_ra < 0.0:
            clean_ra = (clean_ra + 360.0) % 360.0
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Right Ascension {clean_ra:.4f}° out of bounds. Must be in range [0.0, 360.0) degrees."
            )

    if not (-90.0 <= clean_dec <= 90.0):
        raise HTTPException(
            status_code=400,
            detail=f"Declination {clean_dec:.4f}° out of bounds. Must be in range [-90.0, +90.0] degrees."
        )

    clean_radius = None
    if radius_arcmin is not None:
        try:
            clean_radius = float(radius_arcmin)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid radius: must be a valid float.")

        if clean_radius <= 0.0 or clean_radius > max_radius_arcmin:
            raise HTTPException(
                status_code=400,
                detail=f"Search radius {clean_radius:.2f}' out of bounds. Must be in range (0.0, {max_radius_arcmin:.1f}] arcminutes."
            )

    return clean_ra, clean_dec, clean_radius


def sanitize_target_name(target_name: str) -> str:
    """
    Sanitizes astronomical target names to prevent ADQL injection and syntax errors.

    Args:
        target_name: Raw input string

    Returns:
        Sanitized target string

    Raises:
        HTTPException(400) if target name contains illegal or suspicious characters.
    """
    if not target_name or not isinstance(target_name, str):
        return "Unknown Target"

    clean = target_name.strip()
    if len(clean) > 80:
        clean = clean[:80]

    if not TARGET_NAME_REGEX.match(clean):
        # Disallow SQL/ADQL meta-characters (; ' " -- /* \ etc.)
        raise HTTPException(
            status_code=400,
            detail=f"Target name '{target_name}' contains illegal characters. Only alphanumeric, spaces, +, -, _, ., and () are permitted."
        )

    return clean
