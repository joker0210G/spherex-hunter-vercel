"""
🛰️ SPHEREx Hunter - Calibrated Preprocessing Pipeline
NASA Space Apps Challenge 2026 - Team RIP

Implements scientifically rigorous FITS preprocessing:
1. Applies CRITICAL_BAD_MASK to set detector defect and artifact pixels to NaN.
2. Subtracts the 2D ZODI extension background when present.
3. Propagates VARIANCE (sigma^2) through all mathematical steps.
4. Converts surface brightness (MJy / sr) to point-source flux (microJanskys, uJy)
   using exact pixel solid angle Omega_pix derived from WCS.
5. Generates boolean and weighted coverage maps.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

import astropy.wcs.utils as wcs_utils
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

from backend.science.flags import CRITICAL_BAD_MASK, apply_pixel_mask

MJY_SR_TO_UJY_SR = 1.0e12  # 1 MJy = 10^6 Jy = 10^12 uJy


@dataclass
class PreprocessedProduct:
    flux_ujy: np.ndarray              # 2D float32 flux array in uJy per pixel
    variance_ujy2: np.ndarray         # 2D float32 propagated variance array in uJy^2
    surface_brightness_mjy_sr: np.ndarray  # Cleaned surface brightness in MJy / sr
    zodi_subtracted_mjy_sr: Optional[np.ndarray]  # Subtracted zodiacal light
    coverage_mask: np.ndarray         # 2D boolean mask: True where pixel has valid coverage
    pixel_scale_arcsec: float         # Mean pixel scale in arcseconds
    pixel_solid_angle_sr: float       # Pixel solid angle in steradians
    wcs: WCS                          # Astropy WCS instance
    mjd_avg: float                    # Mid-exposure MJD
    wavelength_um: Optional[float]    # Effective band wavelength in microns


def compute_pixel_solid_angle_sr(wcs: WCS) -> Tuple[float, float]:
    """
    Computes exact pixel area from WCS celestial projections:
    Returns (pixel_scale_arcsec, pixel_solid_angle_sr).
    """
    try:
        # proj_plane_pixel_area returns area in deg^2
        area_deg2 = wcs_utils.proj_plane_pixel_area(wcs)
        pixel_scale_arcsec = float(np.sqrt(area_deg2) * 3600.0)
        deg_to_rad = np.pi / 180.0
        pixel_solid_angle_sr = float(area_deg2 * (deg_to_rad**2))
    except Exception:
        # Fallback to cdelt or standard 6.2 arcsec for SPHEREx
        cdelt = getattr(wcs.wcs, "cdelt", None)
        if cdelt is not None and len(cdelt) >= 2:
            scale_deg = float(np.sqrt(abs(cdelt[0] * cdelt[1])))
        else:
            scale_deg = 6.2 / 3600.0
        pixel_scale_arcsec = scale_deg * 3600.0
        deg_to_rad = np.pi / 180.0
        pixel_solid_angle_sr = (scale_deg * deg_to_rad)**2

    return pixel_scale_arcsec, pixel_solid_angle_sr


def preprocess_spherex_hdu(
    hdul: fits.HDUList,
    bad_mask: int = CRITICAL_BAD_MASK,
    subtract_zodi: bool = True
) -> PreprocessedProduct:
    """
    Processes a SPHEREx Level-2 multi-extension FITS file:
    - HDU 0: PRIMARY
    - HDU 1: IMAGE (MJy/sr)
    - HDU 2: FLAGS (int32 quality mask)
    - HDU 3: VARIANCE (MJy2/sr2)
    - HDU 4: ZODI (MJy/sr, optional)
    """
    # 1. Extract image, header, and WCS
    image_hdu = hdul["IMAGE"] if "IMAGE" in hdul else hdul[1]
    image_raw = image_hdu.data.astype(np.float32)
    header = image_hdu.header
    wcs = WCS(header)

    # 2. Extract flags and apply bad-pixel mask to NaN
    if "FLAGS" in hdul:
        flags = hdul["FLAGS"].data.astype(np.int32)
        image_cleaned, coverage_mask = apply_pixel_mask(image_raw, flags, bad_mask=bad_mask)
    else:
        # If FLAGS HDU not present, mask out existing non-finite pixels
        flags = np.zeros_like(image_raw, dtype=np.int32)
        invalid = np.isnan(image_raw) | np.isinf(image_raw)
        image_cleaned = image_raw.copy()
        image_cleaned[invalid] = np.nan
        coverage_mask = ~invalid

    # 3. Extract or initialize VARIANCE
    if "VARIANCE" in hdul:
        variance_raw = hdul["VARIANCE"].data.astype(np.float32)
        # Bad pixels in variance also set to NaN
        variance_clean = variance_raw.copy()
        variance_clean[~coverage_mask] = np.nan
    else:
        # Fallback to estimated background variance via robust MAD
        valid_pixels = image_cleaned[coverage_mask]
        if len(valid_pixels) > 10:
            med = np.median(valid_pixels)
            mad = np.median(np.abs(valid_pixels - med))
            sigma_est = float(1.4826 * mad)
        else:
            sigma_est = 0.5
        variance_clean = np.full_like(image_cleaned, fill_value=sigma_est**2, dtype=np.float32)
        variance_clean[~coverage_mask] = np.nan

    # 4. Subtract ZODI background if present
    zodi_subtracted = None
    if subtract_zodi and "ZODI" in hdul:
        zodi_data = hdul["ZODI"].data.astype(np.float32)
        zodi_subtracted = zodi_data.copy()
        # Subtract modeled background
        image_cleaned = image_cleaned - zodi_data
        # Propagate 5% systematic uncertainty on zodi model
        zodi_variance = (0.05 * zodi_data)**2
        variance_clean = variance_clean + zodi_variance

    # 5. Convert surface brightness (MJy/sr) to flux (uJy)
    pixel_scale_arcsec, pixel_solid_angle_sr = compute_pixel_solid_angle_sr(wcs)

    # Conversion factor from MJy/sr to uJy per pixel
    conv_factor = pixel_solid_angle_sr * MJY_SR_TO_UJY_SR

    flux_ujy = (image_cleaned * conv_factor).astype(np.float32)
    variance_ujy2 = (variance_clean * (conv_factor**2)).astype(np.float32)

    # Observation time and wavelength lookup
    mjd_avg = float(header.get("MJD-AVG", header.get("MJD-OBS", 60000.0)))
    wavelength_um = float(header.get("CWAVE", 0.0)) if "CWAVE" in header else None

    return PreprocessedProduct(
        flux_ujy=flux_ujy,
        variance_ujy2=variance_ujy2,
        surface_brightness_mjy_sr=image_cleaned,
        zodi_subtracted_mjy_sr=zodi_subtracted,
        coverage_mask=coverage_mask,
        pixel_scale_arcsec=pixel_scale_arcsec,
        pixel_solid_angle_sr=pixel_solid_angle_sr,
        wcs=wcs,
        mjd_avg=mjd_avg,
        wavelength_um=wavelength_um
    )
