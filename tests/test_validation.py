"""
Unit tests for coordinate and target input validation.
"""

import pytest
from fastapi import HTTPException

from backend.utils.validation import sanitize_target_name, validate_coordinates


def test_valid_coordinates():
    ra, dec, rad = validate_coordinates(133.795, -7.245, 3.0)
    assert ra == 133.795
    assert dec == -7.245
    assert rad == 3.0


def test_invalid_ra_out_of_bounds():
    with pytest.raises(HTTPException) as excinfo:
        validate_coordinates(400.0, 10.0)
    assert excinfo.value.status_code == 400
    assert "out of bounds" in excinfo.value.detail


def test_invalid_dec_out_of_bounds():
    with pytest.raises(HTTPException) as excinfo:
        validate_coordinates(100.0, -95.0)
    assert excinfo.value.status_code == 400
    assert "out of bounds" in excinfo.value.detail


def test_invalid_radius():
    with pytest.raises(HTTPException) as excinfo:
        validate_coordinates(100.0, 10.0, -1.0)
    assert excinfo.value.status_code == 400

    with pytest.raises(HTTPException) as excinfo:
        validate_coordinates(100.0, 10.0, 100.0)
    assert excinfo.value.status_code == 400


def test_sanitize_target_name_valid():
    assert sanitize_target_name("WISE 0855-0714") == "WISE 0855-0714"
    assert sanitize_target_name("Barnard's Star") == "Barnard's Star" or "Barnard" in sanitize_target_name("Barnard's Star")


def test_sanitize_target_name_injection_rejection():
    # ADQL SQL Injection attacks
    attacks = [
        "target; DROP TABLE users;--",
        "wise0855' UNION SELECT * FROM gaia_dr3_source --",
        "target/*comment*/",
        "target; SELECT @@version",
        "<script>alert(1)</script>",
        "target' OR '1'='1",
        "target; SHUTDOWN;--",
    ]
    for attack in attacks:
        with pytest.raises(HTTPException) as excinfo:
            sanitize_target_name(attack)
        assert excinfo.value.status_code == 400


def test_coordinate_injection_and_extremes():
    # Non-numeric coordinate injections
    with pytest.raises(HTTPException):
        validate_coordinates("133.7; DROP TABLE", -7.2)
    with pytest.raises(HTTPException):
        validate_coordinates(133.7, "SELECT 1")
    # Coordinates exceeding physical bounds
    with pytest.raises(HTTPException):
        validate_coordinates(365.0, 0.0)
    with pytest.raises(HTTPException):
        validate_coordinates(180.0, -91.0)
    with pytest.raises(HTTPException):
        validate_coordinates(180.0, 91.0)

