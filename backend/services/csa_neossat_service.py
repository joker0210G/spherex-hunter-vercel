"""
SPHEREx Hunter - CSA NEOSSat & CADC asteroid tracking (compat wrapper)

Previously this module returned hardcoded "nearest asteroid" names, offsets, observation
counts and a Planet-X probability for the benchmark targets, and pointed at a non-existent
CADC domain. All of that was fabricated and has been removed.

query_csa_neossat() now delegates to backend.services.neossat_service, which performs
LIVE queries against IMCCE SkyBoT (known solar-system objects) and the CADC CAOM-2 TAP
(NEOSSat archival footprints). If an archive is unreachable the result says so.
"""

import time
import urllib.parse

from backend.services.neossat_service import build_neossat_tracking_report


def query_csa_neossat(ra: float, dec: float, radius_arcmin: float = 3.0) -> dict:
    t0 = time.time()
    report = build_neossat_tracking_report(ra, dec, fov_arcmin=max(3.0, float(radius_arcmin)))
    sso = report["known_solar_system_objects"]
    cadc = report["neossat_archive"]
    nearest = sso["objects"][0] if sso.get("objects") else None

    target = f"{ra:.5f} {dec:+.5f}"
    return {
        "status": "success",
        "facility": "Canadian Space Agency (CSA) NEOSSat",
        "archive_host": "Canadian Astronomy Data Centre (CADC / NRC Herzberg)",
        "cadc_search_url": report["links"]["cadc_neossat_search"],
        "cadc_search_url_text": urllib.parse.quote(target),
        "search_center": {"ra_deg": round(ra, 5), "dec_deg": round(dec, 5), "radius_arcmin": radius_arcmin},
        "verdict": report["verdict"],
        "verdict_text": report["verdict_text"],
        "neossat_telemetry": {
            "cadc_collection": "NEOSSAT",
            "archive_status": cadc.get("status"),
            "observation_epochs_count": cadc.get("count") if cadc.get("status") == "success" else None,
            "nearest_tracked_asteroid": nearest["name"] if nearest else None,
            "asteroid_separation_arcsec": nearest["offset_arcsec"] if nearest else None,
            "asteroid_hourly_motion_arcsec_hr": nearest["rate_total_arcsec_hr"] if nearest else None,
            "known_sso_in_cone": sso.get("count") if sso.get("status") == "success" else None,
            "skybot_status": sso.get("status"),
            "message": cadc.get("message") or sso.get("message"),
        },
        "known_solar_system_objects": sso,
        "neossat_archive": cadc,
        "telemetry": {"cache_tier": "LIVE_SKYBOT_CADC", "fetch_time_ms": round((time.time() - t0) * 1000, 2)},
    }
