"""
Unit tests for SPHEREx flag bits, CRITICAL_BAD_MASK, and synthetic FITS generation.
"""

import numpy as np

from backend.science.flags import CRITICAL_BAD_MASK, SPHERExFlag, apply_pixel_mask
from tests.fixtures.synthetic_spherex import create_synthetic_spherex_fits


def test_flag_bit_values():
    assert SPHERExFlag.TRANSIENT == 1
    assert SPHERExFlag.OVERFLOW == 2
    assert SPHERExFlag.NONFUNC == 64
    assert SPHERExFlag.HOT == 1024
    assert SPHERExFlag.COLD == 2048
    assert SPHERExFlag.SOURCE == 2097152
    assert SPHERExFlag.STREAK == 33554432
    assert SPHERExFlag.SNOWBALL == 134217728


def test_critical_bad_mask_excludes_real_sources():
    # Astrophysical sources must NOT be masked out by CRITICAL_BAD_MASK!
    assert (SPHERExFlag.SOURCE & CRITICAL_BAD_MASK) == 0
    # Dichroic edge and halos must also not be converted to NaN automatically
    assert (SPHERExFlag.DICHROIC & CRITICAL_BAD_MASK) == 0
    assert (SPHERExFlag.HALO & CRITICAL_BAD_MASK) == 0


def test_apply_pixel_mask():
    image = np.ones((10, 10), dtype=np.float32) * 5.0
    flags = np.zeros((10, 10), dtype=np.int32)

    # Set pixel (2, 2) as transient radiation hit
    flags[2, 2] = SPHERExFlag.TRANSIENT
    # Set pixel (3, 3) as cataloged source
    flags[3, 3] = SPHERExFlag.SOURCE
    # Set pixel (4, 4) as hot pixel
    flags[4, 4] = SPHERExFlag.HOT
    # Set pixel (5, 5) as satellite streak
    flags[5, 5] = SPHERExFlag.STREAK

    cleaned, mask = apply_pixel_mask(image, flags)

    # Check bad pixels become NaN
    assert np.isnan(cleaned[2, 2])
    assert mask[2, 2] is False or mask[2, 2] == 0

    assert np.isnan(cleaned[4, 4])
    assert np.isnan(cleaned[5, 5])

    # Check real source is preserved!
    assert not np.isnan(cleaned[3, 3])
    assert cleaned[3, 3] == 5.0
    assert mask[3, 3] == 1 or mask[3, 3] is True


def test_synthetic_spherex_fits_generator():
    hdul = create_synthetic_spherex_fits(size=64)
    assert len(hdul) == 7
    assert hdul[1].name == "IMAGE"
    assert hdul[1].data.shape == (64, 64)
    assert hdul[2].name == "FLAGS"
    assert hdul[3].name == "VARIANCE"
    assert hdul[4].name == "ZODI"
    assert hdul[5].name == "EPSF"
    assert hdul[6].name == "WCS-WAVE"

    # Test bad pixel masking on synthetic FITS
    cleaned, mask = apply_pixel_mask(hdul[1].data, hdul[2].data)
    # The transient at (5, 5) and hot pixel at (10, 10) must be NaN
    assert np.isnan(cleaned[5, 5])
    assert np.isnan(cleaned[10, 10])
    # The center source must be preserved
    cy, cx = 32, 32
    assert not np.isnan(cleaned[cy, cx])
