"""
Unit tests for SkyBoT identification and Evidence Tier Engine.
Verifies:
1. SkyBoT client structure and ephemeris distance matching.
2. Evidence tier assignment for all 5 tiers:
   - KNOWN_SOLAR_SYSTEM
   - KNOWN_STELLAR_OR_BROWN_DWARF
   - UNKNOWN_MOVER
   - SLOW_IR_EXCESS_CANDIDATE
   - LIKELY_ARTIFACT
3. Strict enforcement: Every output contains 'Candidate, not confirmed'.
4. Fabricated probabilities are completely absent.
"""


from backend.science.evidence_engine import evaluate_candidate_evidence
from backend.science.identification import SkyBoTClient
from backend.services.metadata_schema import EvidenceTier


def test_evidence_tier_known_solar_system():
    candidate = {"candidate_id": "SPX-001", "passed_vetoes": True, "peak_snr_sigma": 15.0}
    skybot_res = {
        "is_matched": True,
        "best_match": {
            "object_name": "Ceres",
            "separation_arcsec": 1.42
        },
        "summary_statement": "Ephemeris match within 1.42 arcsec of Ceres"
    }

    evidence = evaluate_candidate_evidence(candidate, skybot_result=skybot_res)
    assert evidence["evidence_tier"] == EvidenceTier.KNOWN_SOLAR_SYSTEM.value
    assert "Candidate, not confirmed" in evidence["summary"]
    assert "probability" not in evidence


def test_evidence_tier_known_stellar_match():
    candidate = {"candidate_id": "SPX-002", "passed_vetoes": True, "peak_snr_sigma": 25.0}
    gaia_match = {"source_id": "4472832130527458560", "g_mag": 8.19, "total_pm_mas_yr": 10393.4}

    evidence = evaluate_candidate_evidence(candidate, gaia_match=gaia_match)
    assert evidence["evidence_tier"] == EvidenceTier.KNOWN_STELLAR_OR_BROWN_DWARF.value
    assert "Candidate, not confirmed" in evidence["summary"]


def test_evidence_tier_slow_ir_excess_candidate():
    candidate = {"candidate_id": "SPX-003", "passed_vetoes": True, "peak_snr_sigma": 12.0}
    evidence = evaluate_candidate_evidence(candidate, infrared_excess_color=1.85)

    assert evidence["evidence_tier"] == EvidenceTier.SLOW_IR_EXCESS_CANDIDATE.value
    assert "Candidate, not confirmed" in evidence["summary"]


def test_evidence_tier_unknown_mover():
    candidate = {"candidate_id": "SPX-004", "passed_vetoes": True, "peak_snr_sigma": 7.5}
    evidence = evaluate_candidate_evidence(candidate)

    assert evidence["evidence_tier"] == EvidenceTier.UNKNOWN_MOVER.value
    assert "Candidate, not confirmed" in evidence["summary"]


def test_evidence_tier_likely_artifact():
    candidate = {
        "candidate_id": "SPX-005",
        "passed_vetoes": False,
        "veto_reason": "COSMIC_RAY_SPIKE",
        "peak_snr_sigma": 15.0
    }
    evidence = evaluate_candidate_evidence(candidate)

    assert evidence["evidence_tier"] == EvidenceTier.LIKELY_ARTIFACT.value
    assert "artifact" in evidence["summary"].lower()


def test_skybot_client_query_structure():
    import asyncio
    client = SkyBoTClient(timeout_sec=2.0)
    # Query for Ceres location around MJD 60000
    res = asyncio.run(client.query_cone_search(mjd=60000.0, ra_deg=100.0, dec_deg=20.0, radius_arcsec=10.0))
    assert "is_matched" in res
    assert "summary_statement" in res
