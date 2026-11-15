"""
Unit tests for calibrated preprocessing pipeline:
- Bad-pixel masking (CRITICAL_BAD_MASK -> NaN)
- ZODI background subtraction
- Variance propagation
- Exact MJy/sr to uJy flux conversion using WCS pixel solid angle
- Coverage mask generation
"""

import numpy as np
from astropy.wcs import WCS

from backend.science.preprocessing import MJY_SR_TO_UJY_SR, compute_pixel_solid_angle_sr, preprocess_spherex_hdu
from tests.fixtures.synthetic_spherex import create_synthetic_spherex_fits


def test_preprocessing_on_synthetic_spherex():
    hdul = create_synthetic_spherex_fits(size=64)
    res = preprocess_spherex_hdu(hdul, subtract_zodi=True)

    # 1. Assert dimensions
    assert res.flux_ujy.shape == (64, 64)
    assert res.variance_ujy2.shape == (64, 64)
    assert res.coverage_mask.shape == (64, 64)

    # 2. Check bad pixels were converted to NaN
    # In synthetic fixture: (5, 5) is transient, (10, 10) is hot
    assert np.isnan(res.flux_ujy[5, 5])
    assert np.isnan(res.variance_ujy2[5, 5])
    assert not res.coverage_mask[5, 5]

    assert np.isnan(res.flux_ujy[10, 10])
    assert not res.coverage_mask[10, 10]

    # 3. Check central source is preserved and converted to uJy
    cy, cx = 32, 32
    assert not np.isnan(res.flux_ujy[cy, cx])
    assert res.coverage_mask[cy, cx]

    # 4. Check unit conversion math
    # Expected conversion factor = Omega_pix * 10^12
    expected_conv = res.pixel_solid_angle_sr * MJY_SR_TO_UJY_SR
    sb_val = res.surface_brightness_mjy_sr[cy, cx]
    flux_val = res.flux_ujy[cy, cx]
    assert np.isclose(flux_val, sb_val * expected_conv, rtol=1e-5)

    # 5. Check variance propagation
    # Var(F) = Var(I) * conv^2
    var_i = hdul["VARIANCE"].data[cy, cx] + (0.05 * hdul["ZODI"].data[cy, cx])**2
    assert np.isclose(res.variance_ujy2[cy, cx], var_i * (expected_conv**2), rtol=1e-5)


def test_pixel_solid_angle_computation():
    # 6.2 arcsec pixel scale
    w = WCS(naxis=2)
    scale_deg = 6.2 / 3600.0
    w.wcs.cdelt = [-scale_deg, scale_deg]
    w.wcs.crval = [100.0, 20.0]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]

    scale_arcsec, solid_angle_sr = compute_pixel_solid_angle_sr(w)
    assert np.isclose(scale_arcsec, 6.2, atol=0.1)

    # Omega_pix in steradians ~ (6.2 / 206265)^2 ~ 9.03e-10 sr
    expected_sr = (6.2 / 206264.806)**2
    assert np.isclose(solid_angle_sr, expected_sr, rtol=1e-3)
