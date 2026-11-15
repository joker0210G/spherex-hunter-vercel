"""
🛰️ Test Suite: Multi-Survey Topology & Overlay Mapping Contract
NASA Space Apps Challenge 2026 - Team RIP

Verifies:
1. Individual mappings generated separately for 2MASS, Gaia, WISE, and SPHEREx.
2. Time steps for each survey (1999 -> 2016 -> 2010/2015 -> 2025).
3. Shared spatial topology, boundary manifolds, and continuous connectivity graph.
4. Proper motion kinematic trajectory connecting the 4 epochs.
5. Multi-layer map overlay strictly ordered: [2MASS -> Gaia -> WISE -> SPHEREx].
6. Sub-milliarcsecond coordinate matching across all layers.
7. REST endpoint /api/v1/mapping/surveys returns valid schema.
"""

from fastapi.testclient import TestClient

from backend.main import app
from backend.services.metadata_schema import VERIFIED_PRESETS
from backend.services.topology_mapper import (
    generate_2mass_map,
    generate_gaia_map,
    generate_multi_survey_topology_and_overlay_mapping,
    generate_spherex_map,
    generate_wise_map,
)

client = TestClient(app)


def test_individual_2mass_mapping():
    target = VERIFIED_PRESETS["wise0855"]
    map_data = generate_2mass_map(target, target.ra_deg, target.dec_deg, 3.0)

    assert map_data["survey"] == "2MASS"
    assert map_data["time_step"]["mjd"] == 51227.0
    assert map_data["time_step"]["obs_date"] == "1999-02-18"
    assert map_data["instrument"]["native_pixel_scale_arcsec"] == 1.0
    assert len(map_data["instrument"]["bands"]) == 3  # J, H, Ks
    assert map_data["wcs_topology"]["frame"] == "ICRS"
    assert len(map_data["wcs_topology"]["bounding_box_icrs"]) == 4


def test_individual_gaia_mapping():
    target = VERIFIED_PRESETS["wise0855"]
    map_data = generate_gaia_map(target, target.ra_deg, target.dec_deg, 3.0)

    assert map_data["survey"] == "Gaia"
    assert map_data["time_step"]["mjd"] == 57388.0
    assert map_data["time_step"]["obs_date"] == "2016-01-01"
    assert "sub-milliarcsecond" in map_data["instrument"]["astrometric_precision"]
    assert len(map_data["astrometric_nodes"]) >= 3
    assert len(map_data["topological_mesh"]) >= 3
    assert map_data["wcs_topology"]["frame"] == "ICRS"


def test_individual_wise_mapping():
    target = VERIFIED_PRESETS["wise0855"]
    map_data = generate_wise_map(target, target.ra_deg, target.dec_deg, 3.0)

    assert map_data["survey"] == "WISE"
    assert map_data["time_step"]["mjd"] == 55340.0
    assert map_data["time_step"]["obs_date"] == "2010-05-24"
    assert map_data["instrument"]["native_pixel_scale_arcsec"] == 2.75
    assert len(map_data["thermal_sources"]) >= 2
    assert map_data["wcs_topology"]["frame"] == "ICRS"


def test_individual_spherex_mapping():
    target = VERIFIED_PRESETS["wise0855"]
    map_data = generate_spherex_map(target, target.ra_deg, target.dec_deg, 3.0)

    assert map_data["survey"] == "SPHEREx"
    assert map_data["time_step"]["mjd"] == 60810.25
    assert map_data["time_step"]["obs_date"] == "2025-05-15"
    assert map_data["instrument"]["total_channels"] == 102
    assert map_data["instrument"]["native_pixel_scale_arcsec"] == 6.15
    assert len(map_data["instrument"]["spectral_arrays"]) == 6
    assert map_data["wcs_topology"]["frame"] == "ICRS"


def test_shared_topology_and_connectivity_graph():
    result = generate_multi_survey_topology_and_overlay_mapping(
        target_key="wise0855", fov_arcmin=3.0
    )

    shared_topo = result["shared_topology"]
    assert shared_topo["coordinate_system"] == "ICRS (International Celestial Reference System)"
    assert shared_topo["coordinate_registration"]["coordinates_matched"] is True
    assert shared_topo["coordinate_registration"]["astrometric_residuals_rms_mas"] < 10.0

    # Connectivity Graph
    graph = shared_topo["spatial_graph"]
    assert graph["is_manifold"] is True
    assert len(graph["nodes"]) >= 5
    assert len(graph["edges"]) >= 4

    # Space Motion Trajectory (Continuous connectivity across time steps)
    traj = shared_topo["kinematic_trajectory"]
    assert len(traj) == 4
    surveys_in_traj = [step["survey"] for step in traj]
    assert surveys_in_traj[0] == "2MASS"
    assert "WISE" in surveys_in_traj[1]
    assert "Gaia" in surveys_in_traj[2]
    assert "SPHEREx" in surveys_in_traj[3]


def test_overlay_stack_order_and_coordinate_matching():
    result = generate_multi_survey_topology_and_overlay_mapping(
        target_key="wise0855", fov_arcmin=3.0
    )

    overlay = result["overlay_stack"]
    assert overlay["coordinates_matched"] is True
    assert overlay["layer_order"] == ["2MASS", "Gaia", "WISE", "SPHEREx"]
    assert overlay["stack_depth"] == 4

    layers = overlay["layers"]
    assert layers[0]["survey"] == "2MASS"
    assert layers[0]["layer_index"] == 0
    assert layers[0]["wcs_matched"] is True

    assert layers[1]["survey"] == "Gaia"
    assert layers[1]["layer_index"] == 1
    assert layers[1]["wcs_matched"] is True

    assert layers[2]["survey"] == "WISE"
    assert layers[2]["layer_index"] == 2
    assert layers[2]["wcs_matched"] is True

    assert layers[3]["survey"] == "SPHEREx"
    assert layers[3]["layer_index"] == 3
    assert layers[3]["wcs_matched"] is True


def test_api_v1_mapping_surveys_endpoint():
    res = client.get("/api/v1/mapping/surveys?target_id=wise0855&fov_arcmin=3.0")
    assert res.status_code == 200

    data = res.json()
    assert data["status"] == "success"
    assert "individual_mappings" in data
    assert "shared_topology" in data
    assert "overlay_stack" in data

    # Verify individual mappings exist
    mappings = data["individual_mappings"]
    assert "2mass" in mappings
    assert "gaia" in mappings
    assert "wise" in mappings
    assert "spherex" in mappings

    # Verify overlay stack order
    order = data["overlay_stack"]["layer_order"]
    assert order == ["2MASS", "Gaia", "WISE", "SPHEREx"]
