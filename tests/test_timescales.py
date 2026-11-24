from datetime import UTC, datetime, timedelta, timezone

import pytest

from orbitline.timescales import J2000, gmst_degrees, julian_date, julian_date_from_datetime


def test_j2000_epoch() -> None:
    assert julian_date(2000, 1, 1, 12) == J2000


def test_meeus_example_7a_sputnik_launch() -> None:
    # 1957 October 4.81 -> JD 2436116.31
    assert julian_date(1957, 10, 4, 19, 26, 24) == pytest.approx(2436116.31, abs=1e-9)


def test_january_and_february_use_previous_year() -> None:
    assert julian_date(2024, 3, 1) - julian_date(2024, 2, 28) == 2.0  # leap year
    assert julian_date(2023, 3, 1) - julian_date(2023, 2, 28) == 1.0


def test_aware_datetime_in_any_zone_gives_same_date() -> None:
    utc = datetime(2026, 6, 1, 12, 0, tzinfo=UTC)
    plus_two = utc.astimezone(timezone(timedelta(hours=2)))
    assert julian_date_from_datetime(plus_two) == julian_date_from_datetime(utc)


def test_naive_datetime_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone"):
        julian_date_from_datetime(datetime(2026, 6, 1))


@pytest.mark.parametrize(
    "args", [(1500, 1, 1), (2026, 13, 1), (2026, 1, 0), (2026, 1, 1, 24), (2026, 1, 1, 0, 60)]
)
def test_out_of_range_dates_are_rejected(args: tuple[int, ...]) -> None:
    with pytest.raises(ValueError):
        julian_date(*args)


def test_meeus_example_12a_gmst_at_midnight() -> None:
    # 1987 April 10, 0h UT -> 13h10m46.3668s
    expected = (13 + 10 / 60 + 46.3668 / 3600) * 15
    assert gmst_degrees(julian_date(1987, 4, 10)) == pytest.approx(expected, abs=1e-6)


def test_meeus_example_12b_gmst_at_any_time() -> None:
    # 1987 April 10, 19:21:00 UT -> 8h34m57.0896s
    expected = (8 + 34 / 60 + 57.0896 / 3600) * 15
    assert gmst_degrees(julian_date(1987, 4, 10, 19, 21)) == pytest.approx(expected, abs=1e-6)


def test_gmst_is_in_range() -> None:
    for offset in range(0, 4000, 37):
        assert 0.0 <= gmst_degrees(J2000 + offset * 0.731) < 360.0
