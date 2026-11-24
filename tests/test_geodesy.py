import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from orbitline.geodesy import (
    WGS84_A,
    WGS84_B,
    ecef_to_geodetic,
    geodetic_to_ecef,
    look_angles,
)


def test_equator_on_prime_meridian() -> None:
    assert geodetic_to_ecef(0, 0, 0) == pytest.approx([WGS84_A, 0, 0])


def test_north_pole() -> None:
    assert geodetic_to_ecef(90, 0, 0) == pytest.approx([0, 0, WGS84_B], abs=1e-6)


def test_height_moves_along_the_normal() -> None:
    assert geodetic_to_ecef(0, 90, 1000) == pytest.approx([0, WGS84_A + 1000, 0], abs=1e-6)


def test_latitude_out_of_range_is_rejected() -> None:
    with pytest.raises(ValueError, match="latitude"):
        geodetic_to_ecef(91, 0, 0)


@given(
    lat=st.floats(-90, 90),
    lon=st.floats(-180, 180),
    height=st.floats(-500, 2_000_000),
)
def test_round_trip_reproduces_the_position(lat: float, lon: float, height: float) -> None:
    position = geodetic_to_ecef(lat, lon, height)
    back = geodetic_to_ecef(*ecef_to_geodetic(position))
    assert np.allclose(back, position, atol=1e-6, rtol=0)


def test_round_trip_reproduces_latitude_and_height() -> None:
    lat, lon, height = ecef_to_geodetic(geodetic_to_ecef(51.4779, -0.0015, 47.0))
    assert (lat, lon, height) == pytest.approx((51.4779, -0.0015, 47.0), abs=1e-6)


def test_target_overhead_is_at_ninety_degrees() -> None:
    target = geodetic_to_ecef(40, -3, 500_000)
    view = look_angles(40, -3, 0, target)
    assert view.elevation_deg == pytest.approx(90, abs=1e-6)
    assert view.range_m == pytest.approx(500_000, abs=1e-3)


@pytest.mark.parametrize(
    ("offset", "azimuth"),
    [((0, 0, 1000), 0), ((0, 1000, 0), 90), ((0, 0, -1000), 180), ((0, -1000, 0), 270)],
)
def test_azimuth_points_north_east_south_west(
    offset: tuple[float, float, float], azimuth: float
) -> None:
    # At (0, 0) east is +y and north is +z.
    target = geodetic_to_ecef(0, 0, 0) + np.array(offset)
    view = look_angles(0, 0, 0, target)
    assert view.azimuth_deg == pytest.approx(azimuth, abs=1e-9)
    assert view.elevation_deg == pytest.approx(0, abs=1e-3)


def test_target_below_the_horizon_has_negative_elevation() -> None:
    target = geodetic_to_ecef(0, 0, 0) - np.array([1000.0, 0, 0])
    assert look_angles(0, 0, 0, target).elevation_deg == pytest.approx(-90)


def test_target_at_the_station_is_rejected() -> None:
    with pytest.raises(ValueError):
        look_angles(10, 10, 0, geodetic_to_ecef(10, 10, 0))
