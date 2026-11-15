"""
🛰️ SPHEREx Hunter - CSA NEOSSat & CADC Asteroid Tracking Service (TASK-006 / Task 4)
NASA Space Apps Challenge 2026 - Team RIP

Two authentic, live data sources are combined to perform rigorous Solar System object vetoing:
Is a detected candidate an already catalogued asteroid, comet, or near-Earth object?

1. IMCCE SkyBoT cone search (ssp.imcce.fr) -> every KNOWN Solar System object
   (asteroids, comets, NEOs, trojans, TNOs) predicted inside the field of view at a
   given epoch, with V magnitude and apparent sky motion (arcsec / hour).
2. CADC CAOM-2 TAP (Canadian Astronomy Data Centre, collection = 'NEOSSAT') ->
   archival observations of the field by the Canadian Space Agency's Near-Earth
   Object Surveillance Satellite, with direct CADC DataLink download URLs.

Scientific integrity rule (Constitution Principle 1): nothing in this module is ever
fabricated. When an archive is unreachable the response says so explicitly
("status": "unavailable") instead of inventing objects.
"""

import json
import math
import ssl
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Optional

SKYBOT_URL = "https://ssp.imcce.fr/webservices/skybot/api/conesearch.php"
CADC_TAP_SYNC_URL = "https://ws.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/argus/sync"
CADC_DATALINK_URL = "https://ws.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/caom2ops/datalink"
USER_AGENT = "SPHERExHunter/6.0 (NASA Space Apps 2026, Team RIP)"

_SKYBOT_CACHE: dict = {}
_CADC_CACHE: dict = {}
_MAX_CACHE = 64

_SSL_CTX = ssl._create_unverified_context()


# =========================================================================
# Helpers
# =========================================================================
def _cache_put(cache: dict, key: str, value: dict) -> None:
    if len(cache) >= _MAX_CACHE:
        del cache[next(iter(cache))]
    cache[key] = value


def _http_get(url: str, timeout: float) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(req, context=_SSL_CTX, timeout=timeout).read()


def _http_post(url: str, data: dict, timeout: float) -> bytes:
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(req, context=_SSL_CTX, timeout=timeout).read()


def hms_to_deg(hms: str) -> float:
    h, m, s = [float(x) for x in str(hms).strip().split()]
    return (h + m / 60.0 + s / 3600.0) * 15.0


def dms_to_deg(dms: str) -> float:
    txt = str(dms).strip()
    sign = -1.0 if txt.startswith("-") else 1.0
    d, m, s = [abs(float(x)) for x in txt.replace("+", "").replace("-", "").split()]
    return sign * (d + m / 60.0 + s / 3600.0)


def datetime_to_jd(dt: datetime) -> float:
    """Julian Date from a timezone-aware UTC datetime."""
    unix = dt.timestamp()
    return unix / 86400.0 + 2440587.5


def mjd_to_iso(mjd: Optional[float]) -> Optional[str]:
    if mjd is None:
        return None
    try:
        unix = (float(mjd) + 2400000.5 - 2440587.5) * 86400.0
        return datetime.fromtimestamp(unix, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None


def parse_epoch(epoch: Optional[str]) -> datetime:
    """Accepts ISO dates ('2025-11-20', '2025-11-20T03:00:00Z') or None (= now, UTC)."""
    if not epoch:
        return datetime.now(timezone.utc)
    txt = str(epoch).strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(txt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def angular_sep_arcsec(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    """Great-circle separation (haversine) in arcseconds."""
    r1, d1, r2, d2 = map(math.radians, (ra1, dec1, ra2, dec2))
    a = math.sin((d2 - d1) / 2) ** 2 + math.cos(d1) * math.cos(d2) * math.sin((r2 - r1) / 2) ** 2
    return math.degrees(2 * math.asin(min(1.0, math.sqrt(a)))) * 3600.0


# =========================================================================
# 1. IMCCE SkyBoT: known Solar System objects in the field
# =========================================================================
def query_known_solar_system_objects(ra: float, dec: float, radius_arcmin: float = 6.0,
                                     epoch: Optional[str] = None, timeout: float = 25.0) -> dict:
    """
    Live IMCCE SkyBoT cone search for every known asteroid / comet / NEO predicted
    within `radius_arcmin` of (ra, dec) at `epoch` (geocentric observer, code 500).
    """
    t0 = time.time()
    dt = parse_epoch(epoch)
    jd = datetime_to_jd(dt)
    radius_deg = max(0.01, min(1.0, float(radius_arcmin) / 60.0))
    cache_key = f"{ra:.4f}_{dec:.4f}_{radius_deg:.3f}_{jd:.2f}"

    if cache_key in _SKYBOT_CACHE:
        cached = dict(_SKYBOT_CACHE[cache_key])
        cached["telemetry"] = {"cache_tier": "L1_RAM", "fetch_time_ms": round((time.time() - t0) * 1000, 2)}
        return cached

    params = {
        "-ep": f"{jd:.5f}",
        "-ra": f"{ra:.6f}",
        "-dec": f"{dec:.6f}",
        "-rd": f"{radius_deg:.5f}",
        "-mime": "json",
        "-output": "basic",
        "-loc": "500",
        "-filter": "120",
        "-objFilter": "111",
        "-refsys": "EQJ2000",
        "-from": "SPHERExHunter",
    }
    url = f"{SKYBOT_URL}?{urllib.parse.urlencode(params)}"

    objects = []
    status = "success"
    message = None
    try:
        raw = _http_get(url, timeout=timeout).decode("utf-8", errors="replace").strip()
        rows = json.loads(raw) if raw.startswith("[") else []
        if not raw.startswith("["):
            # SkyBoT answers with a plain-text / VOTable notice when no object is in the field
            message = "No known Solar System object predicted in this field."
        for row in rows:
            try:
                o_ra = hms_to_deg(row.get("RA (hms)"))
                o_dec = dms_to_deg(row.get("DEC (dms)"))
            except Exception:
                continue
            dra = float(row.get("dRA (arcsec/h)") or 0.0)
            ddec = float(row.get("dDEC (arcsec/h)") or 0.0)
            objects.append({
                "number": row.get("Num"),
                "name": row.get("Name"),
                "object_class": row.get("Class"),
                "ra": round(o_ra, 6),
                "dec": round(o_dec, 6),
                "v_mag": row.get("VMag (mag)"),
                "position_error_arcsec": row.get("Err (arcsec)"),
                "offset_arcsec": round(angular_sep_arcsec(ra, dec, o_ra, o_dec), 2),
                "rate_ra_arcsec_hr": round(dra, 3),
                "rate_dec_arcsec_hr": round(ddec, 3),
                "rate_total_arcsec_hr": round(math.hypot(dra, ddec), 3),
                "geocentric_distance_au": row.get("dg (ua)"),
                "heliocentric_distance_au": row.get("dh (ua)"),
                "is_neo": "NEA" in str(row.get("Class", "")) or "NEO" in str(row.get("Class", "")),
                "ssocard_url": (row.get("ssodnet") or {}).get("ssocard"),
            })
        objects.sort(key=lambda o: o["offset_arcsec"])
    except Exception as err:
        status = "unavailable"
        message = f"IMCCE SkyBoT service unreachable: {err}"

    result = {
        "status": status,
        "service": "IMCCE SkyBoT (Virtual Observatory Solar System Portal)",
        "epoch_utc": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "epoch_jd": round(jd, 5),
        "search_center": {"ra_deg": ra, "dec_deg": dec, "radius_arcmin": round(radius_deg * 60.0, 3)},
        "count": len(objects),
        "objects": objects,
        "message": message,
        "telemetry": {"cache_tier": "LIVE_SKYBOT", "fetch_time_ms": round((time.time() - t0) * 1000, 2)},
    }
    if status == "success":
        _cache_put(_SKYBOT_CACHE, cache_key, result)
    return result


# =========================================================================
# 2. CADC CAOM-2 TAP: CSA NEOSSat archival coverage of the field
# =========================================================================
def query_neossat_observations(ra: float, dec: float, radius_deg: float = 0.5,
                               limit: int = 25, timeout: float = 30.0) -> dict:
    """
    Queries the Canadian Astronomy Data Centre CAOM-2 TAP service for NEOSSat science
    observations whose footprint intersects a circle around (ra, dec).
    """
    t0 = time.time()
    radius_deg = max(0.05, min(2.0, float(radius_deg)))
    cache_key = f"{ra:.3f}_{dec:.3f}_{radius_deg:.2f}_{limit}"
    if cache_key in _CADC_CACHE:
        cached = dict(_CADC_CACHE[cache_key])
        cached["telemetry"] = {"cache_tier": "L1_RAM", "fetch_time_ms": round((time.time() - t0) * 1000, 2)}
        return cached

    adql = (
        f"SELECT TOP {int(limit)} o.observationID, o.target_name, o.instrument_name, "
        f"p.publisherID, p.time_bounds_lower, p.time_exposure, p.calibrationLevel "
        f"FROM caom2.Observation AS o JOIN caom2.Plane AS p ON o.obsID = p.obsID "
        f"WHERE o.collection = 'NEOSSAT' AND o.intent = 'science' "
        f"AND INTERSECTS(CIRCLE('ICRS', {ra:.6f}, {dec:.6f}, {radius_deg:.4f}), p.position_bounds) = 1 "
        f"ORDER BY p.time_bounds_lower DESC"
    )

    observations = []
    status = "success"
    message = None
    try:
        raw = _http_post(CADC_TAP_SYNC_URL, {"LANG": "ADQL", "QUERY": adql, "FORMAT": "csv"}, timeout=timeout)
        lines = raw.decode("utf-8", errors="replace").strip().splitlines()
        header = [h.strip() for h in lines[0].split(",")] if lines else []
        for line in lines[1:]:
            cols = line.split(",")
            if len(cols) < len(header):
                continue
            rec = dict(zip(header, cols))
            mjd = float(rec["time_bounds_lower"]) if rec.get("time_bounds_lower") else None
            pub_id = rec.get("publisherID") or ""
            observations.append({
                "observation_id": rec.get("observationID"),
                "target_name": rec.get("target_name") or None,
                "instrument": rec.get("instrument_name") or "NEOSSat",
                "start_mjd": round(mjd, 5) if mjd else None,
                "start_utc": mjd_to_iso(mjd),
                "exposure_s": float(rec["time_exposure"]) if rec.get("time_exposure") else None,
                "calibration_level": rec.get("calibrationLevel"),
                "publisher_id": pub_id,
                "datalink_url": f"{CADC_DATALINK_URL}?ID={urllib.parse.quote(pub_id, safe='')}" if pub_id else None,
            })
        if not observations:
            message = f"No NEOSSat science observation footprint within {radius_deg:.2f}° in the CADC archive."
    except Exception as err:
        status = "unavailable"
        message = f"CADC CAOM-2 TAP service unreachable: {err}"

    result = {
        "status": status,
        "service": "Canadian Astronomy Data Centre (CADC) CAOM-2 TAP",
        "collection": "NEOSSAT",
        "search_center": {"ra_deg": ra, "dec_deg": dec, "radius_deg": radius_deg},
        "count": len(observations),
        "observations": observations,
        "adql": adql,
        "message": message,
        "telemetry": {"cache_tier": "LIVE_CADC_TAP", "fetch_time_ms": round((time.time() - t0) * 1000, 2)},
    }
    if status == "success":
        _cache_put(_CADC_CACHE, cache_key, result)
    return result


# =========================================================================
# 3. Combined NEOSSat / asteroid tracking report
# =========================================================================
def build_portal_links(ra: float, dec: float, fov_arcmin: float = 3.0) -> dict:
    size_arcsec = int(max(30, min(600, round(fov_arcmin * 60.0))))
    coord = f"{ra:.5f} {dec:+.5f}"
    q = urllib.parse.quote
    return {
        "wiseview": f"http://byw.tools/wiseview#ra={ra:.5f}&dec={dec:.5f}&size={size_arcsec}&band=3&speed=200&gaia=1&diff=0",
        "wiseview_difference": f"http://byw.tools/wiseview#ra={ra:.5f}&dec={dec:.5f}&size={size_arcsec}&band=3&speed=200&gaia=1&diff=1",
        "legacy_survey_unwise": f"https://www.legacysurvey.org/viewer?ra={ra:.5f}&dec={dec:.5f}&layer=unwise-neo7&zoom=14",
        "irsa_finderchart": f"https://irsa.ipac.caltech.edu/applications/finderchart/?locstr={q(coord)}",
        "irsa_spherex": "https://irsa.ipac.caltech.edu/applications/spherex",
        "irsa_most": "https://irsa.ipac.caltech.edu/applications/MOST",
        "simbad": f"https://simbad.cds.unistra.fr/simbad/sim-coo?Coord={q(coord)}&Radius=1&Radius.unit=arcmin",
        "vizier_gaia_dr3": f"https://vizier.cds.unistra.fr/viz-bin/VizieR-4?-source=I/355/gaiadr3&-c={q(coord)}&-c.rm=1",
        "mast_portal": f"https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html?searchQuery={q(coord)}",
        "cadc_neossat_search": f"https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/search/?Observation.collection=NEOSSAT&Plane.position.bounds={q(coord)}",
        "csa_neossat_dataset": "https://data.asc-csa.gc.ca/dataset/neossat",
        "csa_neossat_tutorial": "https://github.com/asc-csa/NEOSSAT_Tutorial",
        "mpc_checker": "https://minorplanetcenter.net/cgi-bin/checkmp.cgi",
    }


def build_neossat_tracking_report(ra: float, dec: float, fov_arcmin: float = 3.0,
                                  epoch: Optional[str] = None,
                                  include_cadc: bool = True,
                                  match_radius_arcsec: float = 20.0) -> dict:
    """
    Combines SkyBoT known-SSO predictions with CADC NEOSSat coverage and returns an
    asteroid-rejection verdict for the field centre.
    """
    t0 = time.time()
    search_radius_arcmin = max(3.0, float(fov_arcmin) * 0.75)
    sso = query_known_solar_system_objects(ra, dec, radius_arcmin=search_radius_arcmin, epoch=epoch)
    cadc = query_neossat_observations(ra, dec, radius_deg=0.5) if include_cadc else {
        "status": "skipped", "count": 0, "observations": [], "message": "CADC query skipped."}

    nearest = sso["objects"][0] if sso.get("objects") else None
    if sso["status"] != "success":
        verdict = "SSO_CHECK_UNAVAILABLE"
        verdict_text = "Known-asteroid check could not be completed (SkyBoT unreachable)."
    elif nearest and nearest["offset_arcsec"] <= match_radius_arcsec:
        verdict = "KNOWN_SOLAR_SYSTEM_OBJECT"
        verdict_text = (f"Field centre matches catalogued Solar System body {nearest['object_class']} '{nearest['name']}' "
                        f"({nearest['offset_arcsec']}\" separation, V={nearest['v_mag']}). Candidate, not confirmed as novel source.")
    else:
        verdict = "NO_KNOWN_SSO_MATCH"
        verdict_text = (f"No known asteroid or comet within {match_radius_arcsec:.0f}\" of field centre "
                        f"({sso['count']} known SSOs elsewhere in the {search_radius_arcmin:.1f}' search cone). Candidate, not confirmed.")

    return {
        "status": "success",
        "coordinates": {"ra_deg": ra, "dec_deg": dec, "fov_arcmin": fov_arcmin},
        "verdict": verdict,
        "verdict_text": verdict_text,
        "match_radius_arcsec": match_radius_arcsec,
        "known_solar_system_objects": sso,
        "neossat_archive": cadc,
        "links": build_portal_links(ra, dec, fov_arcmin),
        "telemetry": {"fetch_time_ms": round((time.time() - t0) * 1000, 2)},
    }
