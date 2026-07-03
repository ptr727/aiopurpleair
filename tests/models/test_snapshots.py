"""Snapshot the canonical parsed form of the response models.

These guard against schema drift: any change to a response model's fields,
types, aliases, or serialized values shows up as a snapshot diff. Regenerate
intentionally with ``uv run pytest --snapshot-update``.
"""

from typing import Any

from syrupy.assertion import SnapshotAssertion

from aiopurpleair.models.keys import GetKeysResponse
from aiopurpleair.models.organizations import GetOrganizationResponse
from aiopurpleair.models.sensors import GetSensorsResponse


def test_get_keys_response_snapshot(get_keys_response: dict[str, Any], snapshot: SnapshotAssertion) -> None:
    """The GET /v1/keys response model serializes to a stable shape."""
    model = GetKeysResponse.model_validate(get_keys_response)
    assert model.model_dump(mode="json") == snapshot


def test_get_sensors_response_snapshot(get_sensors_response: dict[str, Any], snapshot: SnapshotAssertion) -> None:
    """The GET /v1/sensors response model serializes to a stable shape."""
    model = GetSensorsResponse.model_validate(get_sensors_response)
    assert model.model_dump(mode="json") == snapshot


def test_get_organization_response_snapshot(
    get_organization_response: dict[str, Any], snapshot: SnapshotAssertion
) -> None:
    """The GET /v1/organization response model serializes to a stable shape."""
    model = GetOrganizationResponse.model_validate(get_organization_response)
    assert model.model_dump(mode="json") == snapshot
