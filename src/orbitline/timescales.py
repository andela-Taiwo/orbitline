"""Calendar dates to Julian dates, and Greenwich mean sidereal time.

Orbit propagation works in Julian dates; turning a satellite position into a direction in
the sky needs the Earth's rotation angle, which sidereal time gives. Formulas follow
Meeus, *Astronomical Algorithms* (2nd ed.), chapters 7 and 12.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime

J2000 = 2451545.0
"""Julian date of 2000-01-01 12:00 TT, the standard epoch."""

DAYS_PER_CENTURY = 36525.0


def julian_date(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: float = 0.0
) -> float:
    """Return the Julian date of a Gregorian calendar date and time of day."""
    if year < 1583:
        raise ValueError("only Gregorian calendar dates (1583 onwards) are supported")
    if not 1 <= month <= 12:
        raise ValueError("month must be 1 to 12")
    if not 1 <= day <= 31:
        raise ValueError("day must be 1 to 31")
    if not (0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 61):
        raise ValueError("time of day is out of range")
    y, m = (year - 1, month + 12) if month <= 2 else (year, month)
    a = y // 100
    b = 2 - a + a // 4
    day_fraction = (hour + (minute + second / 60.0) / 60.0) / 24.0
    return (
        math.floor(365.25 * (y + 4716))
        + math.floor(30.6001 * (m + 1))
        + day
        + day_fraction
        + b
        - 1524.5
    )


def julian_date_from_datetime(moment: datetime) -> float:
    """Return the Julian date of a timezone-aware datetime."""
    if moment.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    utc = moment.astimezone(UTC)
    return julian_date(
        utc.year,
        utc.month,
        utc.day,
        utc.hour,
        utc.minute,
        utc.second + utc.microsecond / 1e6,
    )


def gmst_degrees(jd_ut1: float) -> float:
    """Return Greenwich mean sidereal time in degrees, in [0, 360)."""
    d = jd_ut1 - J2000
    t = d / DAYS_PER_CENTURY
    theta = 280.46061837 + 360.98564736629 * d + 0.000387933 * t * t - t * t * t / 38710000.0
    return theta % 360.0
