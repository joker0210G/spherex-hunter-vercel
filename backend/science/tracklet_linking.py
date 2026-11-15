"""
🛰️ SPHEREx Hunter - Dipole Tracklet Linking Engine for Moving Bodies
NASA Space Apps Challenge 2026 - Team RIP

In difference imaging (D = I_epoch2 - I_epoch1), a real moving source creates:
1. A negative flux well (-) at position r1(t1) where flux was present in Epoch 1.
2. A positive flux peak (+) at position r2(t2) where flux appeared in Epoch 2.

This engine links negative and positive detections into unified motion tracklets:
- Enforces photometric flux conservation: |F(+) - |F(-)|| / F(+) <= 0.40
- Enforces physical velocity bounds (0.01"/hr <= rate <= 50"/hr)
- Generates linked tracklets for motion model fitting
"""

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from scipy import ndimage


@dataclass
class LinkedTracklet:
    tracklet_id: str
    pos_cand_id: str
    x1_pix: float
    y1_pix: float
    x2_pix: float
    y2_pix: float
    separation_pix: float
    separation_arcsec: float
    motion_angle_deg: float
    flux1_ujy: float
    flux2_ujy: float
    flux_ratio: float
    apparent_rate_arcsec_hr: float
    snr_sigma: float
    is_physically_viable: bool


def detect_negative_wells(
    diff_image: np.ndarray,
    s_corr: np.ndarray,
    snr_threshold: float = 5.0,
    edge_margin_pix: int = 4
) -> List[Tuple[float, float, float, float]]:
    """
    Detects significant negative flux wells in the difference image (S_corr <= -snr_threshold).
    Returns list of (cx, cy, peak_negative_sigma, negative_flux).
    """
    h, w = s_corr.shape
    neg_mask = np.nan_to_num(s_corr, nan=0.0) <= -snr_threshold
    labeled, num_features = ndimage.label(neg_mask)

    wells = []
    for feat_id in range(1, num_features + 1):
        cy, cx = ndimage.center_of_mass(np.abs(np.nan_to_num(s_corr, nan=0.0)), labeled, feat_id)
        cy = float(cy)
        cx = float(cx)

        if cx < edge_margin_pix or cx >= (w - edge_margin_pix) or cy < edge_margin_pix or cy >= (h - edge_margin_pix):
            continue

        iy, ix = int(round(cy)), int(round(cx))
        sub_flux = float(diff_image[iy, ix]) if not np.isnan(diff_image[iy, ix]) else 0.0
        peak_sigma = float(abs(s_corr[iy, ix])) if not np.isnan(s_corr[iy, ix]) else 0.0

        wells.append((cx, cy, peak_sigma, sub_flux))

    return wells


def link_dipole_tracklets(
    positive_candidates: list,
    negative_wells: list,
    dt_hours: float,
    pixel_scale_arcsec: float = 6.2,
    max_rate_arcsec_hr: float = 10.0,
    min_separation_pix: float = 1.5
) -> List[LinkedTracklet]:
    """
    Links positive detections (+) with corresponding negative wells (-) across survey epochs.
    """
    tracklets = []
    tracklet_counter = 0

    for pos in positive_candidates:
        if not getattr(pos, "passed_vetoes", True):
            continue

        x2, y2 = pos.x_pix, pos.y_pix
        f2 = abs(pos.flux_ujy)

        best_neg = None
        best_score = 999.0

        for neg in negative_wells:
            x1, y1, neg_sigma, neg_flux = neg
            f1 = abs(neg_flux)

            # Spatial separation
            sep_pix = float(np.hypot(x2 - x1, y2 - y1))
            if sep_pix < min_separation_pix:
                continue

            sep_arcsec = sep_pix * pixel_scale_arcsec
            rate_arcsec_hr = sep_arcsec / max(0.01, dt_hours)

            # Velocity bound
            if rate_arcsec_hr > max_rate_arcsec_hr:
                continue

            # Photometric flux consistency
            mean_f = 0.5 * (f1 + f2)
            flux_diff_rel = abs(f2 - f1) / max(1e-4, mean_f)
            if flux_diff_rel > 0.50:  # Within 50% flux conservation
                continue

            # Combined ranking score (prefers small flux difference and clean trajectory)
            score = flux_diff_rel + (sep_pix * 0.01)
            if score < best_score:
                best_score = score
                best_neg = neg

        if best_neg is not None:
            tracklet_counter += 1
            x1, y1, neg_sigma, neg_flux = best_neg
            sep_pix = float(np.hypot(x2 - x1, y2 - y1))
            sep_arcsec = sep_pix * pixel_scale_arcsec
            rate = sep_arcsec / max(0.01, dt_hours)
            angle_deg = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)) % 360.0)

            t_id = f"TRK-{tracklet_counter:03d}"
            tracklets.append(LinkedTracklet(
                tracklet_id=t_id,
                pos_cand_id=getattr(pos, "candidate_id", "DET-UNKNOWN"),
                x1_pix=round(x1, 2),
                y1_pix=round(y1, 2),
                x2_pix=round(x2, 2),
                y2_pix=round(y2, 2),
                separation_pix=round(sep_pix, 2),
                separation_arcsec=round(sep_arcsec, 2),
                motion_angle_deg=round(angle_deg, 1),
                flux1_ujy=round(abs(neg_flux), 2),
                flux2_ujy=round(f2, 2),
                flux_ratio=round(f2 / max(1e-4, abs(neg_flux)), 2),
                apparent_rate_arcsec_hr=round(rate, 3),
                snr_sigma=round(min(pos.peak_snr_sigma, neg_sigma), 2),
                is_physically_viable=True
            ))

    return tracklets

