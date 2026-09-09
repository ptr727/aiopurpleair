"""Define Pydantic validator helpers."""

from datetime import UTC, datetime


def validate_timestamp(value: int) -> datetime:
    """Validate a timestamp.

    Args:
        value: An integer (epoch datetime) to evaluate.

    Returns:
        A parsed timezone-aware datetime (UTC).
    """
    # Returning a tz-aware datetime is required by downstream consumers like
    # Home Assistant's SensorEntity (TIMESTAMP device class), which forces
    # the entity state to "unavailable" when given a naive datetime.
    return datetime.fromtimestamp(value, tz=UTC)
