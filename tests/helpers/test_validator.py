"""Define tests for Pydantic validator helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from aiopurpleair.helpers.validator import validate_timestamp


def test_validate_timestamp_returns_tz_aware_utc() -> None:
    """Returned datetime carries tzinfo=UTC.

    Naive datetimes break downstream consumers like Home Assistant's
    SensorEntity TIMESTAMP class, which forces the entity state to
    "unavailable" when the value lacks tzinfo.
    """
    result = validate_timestamp(1667889279)
    assert result == datetime(2022, 11, 8, 6, 34, 39, tzinfo=UTC)
    assert result.tzinfo == UTC
