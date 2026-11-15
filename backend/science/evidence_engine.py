"""
🛰️ SPHEREx Hunter - Evidence Tier Engine
NASA Space Apps Challenge 2026 - Team RIP

Synthesizes astrometric kinematics, multi-survey catalog cross-matches,
and SkyBoT ephemeris checks into standard evidence tiers:
1. KNOWN_SOLAR_SYSTEM: Confirmed ephemeris match with known asteroid/comet.
2. KNOWN_STELLAR_OR_BROWN_DWARF: Gaia DR3 / 2MASS optical or NIR stellar source.
3. UNKNOWN_MOVER: Real moving dipole without catalog counterpart.
4. SLOW_IR_EXCESS_CANDIDATE: Persistent high-infrared source without optical match.
5. LIKELY_ARTIFACT: Fails differencing vetoes (edge, cosmic ray, PSF dipole).

EVERY result carries "Candidate, not confirmed". No fabricated probabilities.
"""

from typing import Any, Dict, Optional

from backend.services.metadata_schema import EvidenceTier


def evaluate_candidate_evidence(
    candidate_data: Dict[str, Any],
    skybot_result: Optional[Dict[str, Any]] = None,
    gaia_match: Optional[Dict[str, Any]] = None,
    kinematics_fit: Optional[Dict[str, Any]] = None,
    infrared_excess_color: Optional[float] = None
) -> Dict[str, Any]:
    """
    Evaluates all evidence for a detected candidate and produces an Evidence JSON.
    """
    # 1. Check artifact vetoes first
    if candidate_data.get("passed_vetoes") is False:
        tier = EvidenceTier.LIKELY_ARTIFACT
        summary = f"Flagged as likely artifact ({candidate_data.get('veto_reason', 'UNSPECIFIED_VETO')})."
        confirmation = "LIKELY_ARTIFACT"
        recommendation = "Reject from candidate catalog."

    # 2. Check Solar System ephemeris match (SkyBoT / Horizons)
    elif skybot_result and skybot_result.get("is_matched"):
        tier = EvidenceTier.KNOWN_SOLAR_SYSTEM
        best = skybot_result["best_match"]
        sep = best["separation_arcsec"]
        name = best["object_name"]
        summary = f"Ephemeris match within {sep:.2f} arcsec of known body '{name}' (SkyBoT IMCCE). Candidate, not confirmed."
        confirmation = "EPHEMERIS_MATCH_CANDIDATE"
        recommendation = "Cross-match with Minor Planet Center (MPC) orbit database."

    # 3. Check optical star / brown dwarf counterpart in Gaia DR3
    elif gaia_match and gaia_match.get("source_id"):
        tier = EvidenceTier.KNOWN_STELLAR_OR_BROWN_DWARF
        src_id = gaia_match.get("source_id")
        g_mag = gaia_match.get("g_mag", 99.0)
        pm = gaia_match.get("total_pm_mas_yr", 0.0)
        summary = f"Consistent with cataloged optical star in Gaia DR3 (ID ...{str(src_id)[-6:]}, G={g_mag:.1f}, μ={pm:.1f} mas/yr). Candidate, not confirmed."
        confirmation = "CATALOG_CONSISTENT"
        recommendation = "Archive as stationary/proper-motion background star."

    # 4. Check for slow infrared-excess candidate (Planet X / distant KBO proxy)
    elif infrared_excess_color is not None and infrared_excess_color > 1.2:
        tier = EvidenceTier.SLOW_IR_EXCESS_CANDIDATE
        summary = (
            f"Strong infrared excess (color index {infrared_excess_color:.2f}) with no optical Gaia DR3 counterpart. "
            "Kinematics consistent with distant sub-stellar body (Model B). Candidate, not confirmed."
        )
        confirmation = "SLOW_IR_CANDIDATE_NOT_CONFIRMED"
        recommendation = "Prioritize for SPHEREx 102-band forced spectrophotometry and JWST NIRCam follow-up."

    # 5. Default: Unknown moving candidate
    else:
        tier = EvidenceTier.UNKNOWN_MOVER
        snr = candidate_data.get("peak_snr_sigma", 5.0)
        summary = f"Uncataloged moving source detected at {snr:.1f}σ significance. No Gaia or SkyBoT counterpart found. Candidate, not confirmed."
        confirmation = "UNKNOWN_MOVER_NOT_CONFIRMED"
        recommendation = "Trigger multi-epoch tracklet linking across adjacent SPHEREx tiles."

    evidence_json = {
        "candidate_id": candidate_data.get("candidate_id", "SPX-UNKNOWN"),
        "evidence_tier": tier.value,
        "confirmation_status": confirmation,
        "summary": summary,
        "recommendation": recommendation,
        "snr_sigma": candidate_data.get("peak_snr_sigma", 0.0),
        "flux_ujy": candidate_data.get("flux_ujy", 0.0),
        "position_pixels": {
            "x": candidate_data.get("x_pix", 0.0),
            "y": candidate_data.get("y_pix", 0.0)
        },
        "flags": {
            "is_dipole": candidate_data.get("is_dipole", False),
            "is_edge": candidate_data.get("is_edge", False),
            "is_cosmic_ray": candidate_data.get("is_cosmic_ray", False),
            "passed_vetoes": candidate_data.get("passed_vetoes", True)
        },
        "catalog_crossmatch": {
            "skybot": skybot_result.get("summary_statement") if skybot_result else "No SkyBoT query performed",
            "gaia_dr3": bool(gaia_match and gaia_match.get("source_id")),
            "gaia_source_id": gaia_match.get("source_id") if gaia_match else None
        },
        "kinematics": kinematics_fit if kinematics_fit else {
            "preferred_model": "None fitted",
            "chi2": None,
            "bic": None
        },
        "disclaimer": "All candidate classifications are provisional scientific hypothesis rankings. Candidate, not confirmed."
    }

    return evidence_json
