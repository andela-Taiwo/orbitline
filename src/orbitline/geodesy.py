"""WGS84 positions and the view of a target from a ground station.

Positions are Earth-centred, Earth-fixed (ECEF) metres. A ground station is given by
geodetic latitude and longitude in degrees and height above the ellipsoid in metres.
"""

from __future__ import annotations

import math
from typing import NamedTuple

import numpy as np
from numpy.typing import NDArray

WGS84_A = 6378137.0
"""Equatorial radius, metres."""
WGS84_F = 1.0 / 298.257223563
"""Flattening."""
WGS84_B = WGS84_A * (1.0 - WGS84_F)
"""Polar radius, metres."""
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)
"""First eccentricity squared."""


class LookAngles(NamedTuple):
    azimuth_deg: float
    """Clockwise from true north, in [0, 360)."""
    elevation_deg: float
    """Above the local horizon, in [-90, 90]."""
    range_m: float


def _check_latitude(lat_deg: float) -> None:
    if not -90.0 <= lat_deg <= 90.0:
        raise ValueError("latitude must be between -90 and 90 degrees")


def geodetic_to_ecef(lat_deg: float, lon_deg: float, height_m: float) -> NDArray[np.float64]:
    """Return the ECEF position of a geodetic point."""
    _check_latitude(lat_deg)
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * math.sin(lat) ** 2)
    return np.array(
        [
            (n + height_m) * math.cos(lat) * math.cos(lon),
            (n + height_m) * math.cos(lat) * math.sin(lon),
            (n * (1.0 - WGS84_E2) + height_m) * math.sin(lat),
        ]
    )


def ecef_to_geodetic(position: NDArray[np.float64]) -> tuple[float, float, float]:
    """Return (latitude deg, longitude deg, height m) for an ECEF position."""
    x, y, z = (float(v) for v in position)
    p = math.hypot(x, y)
    lon = math.atan2(y, x)
    lat = math.atan2(z, p * (1.0 - WGS84_E2))
    for _ in range(10):
        sin_lat = math.sin(lat)
        n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * sin_lat * sin_lat)
        lat = math.atan2(z + WGS84_E2 * n * sin_lat, p)
    sin_lat, cos_lat = math.sin(lat), math.cos(lat)
    height = p * cos_lat + z * sin_lat - WGS84_A * math.sqrt(1.0 - WGS84_E2 * sin_lat * sin_lat)
    return math.degrees(lat), math.degrees(lon), height


def look_angles(
    lat_deg: float, lon_deg: float, height_m: float, target: NDArray[np.float64]
) -> LookAngles:
    """Return the azimuth, elevation and range of an ECEF target seen from a station."""
    station = geodetic_to_ecef(lat_deg, lon_deg, height_m)
    delta = np.asarray(target, dtype=np.float64) - station
    rng = float(np.linalg.norm(delta))
    if rng == 0.0:
        raise ValueError("target is at the station")
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    east = -math.sin(lon) * delta[0] + math.cos(lon) * delta[1]
    north = (
        -math.sin(lat) * math.cos(lon) * delta[0]
        - math.sin(lat) * math.sin(lon) * delta[1]
        + math.cos(lat) * delta[2]
    )
    up = (
        math.cos(lat) * math.cos(lon) * delta[0]
        + math.cos(lat) * math.sin(lon) * delta[1]
        + math.sin(lat) * delta[2]
    )
    azimuth = math.degrees(math.atan2(east, north)) % 360.0
    elevation = math.degrees(math.asin(max(-1.0, min(1.0, up / rng))))
    return LookAngles(azimuth, elevation, rng)
