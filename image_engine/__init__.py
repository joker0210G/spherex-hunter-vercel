"""
🌌 SPHEREx Hunter - Image Math, Difference Engine & AI
NASA Space Apps Challenge 2026 - Planet X & SPHEREx
Lead: iceodu
"""

from .difference import (
    compute_difference_image,
    process_real_fits_difference,
    save_difference_png,
    render_difference_base64,
    calculate_cancellation_residual_rms
)
from .coaddition import (
    coadd_channels,
    build_spherex_6array_broadbands,
    coadd_real_fits_multiband,
    SPHEREX_DETECTOR_ARRAYS
)

__all__ = [
    "compute_difference_image",
    "process_real_fits_difference",
    "save_difference_png",
    "render_difference_base64",
    "calculate_cancellation_residual_rms",
    "coadd_channels",
    "build_spherex_6array_broadbands",
    "coadd_real_fits_multiband",
    "SPHEREX_DETECTOR_ARRAYS"
]
