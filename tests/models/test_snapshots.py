"""Snapshot the canonical parsed form of the response models.

These guard against schema drift: any change to a response model's fields,
types, aliases, or serialized values shows up as a snapshot diff. Regenerate
intentionally with ``uv run pytest --snapshot-update``.
"""

from typing import Any

from syrupy.assertion import SnapshotAssertion

from aiopurpleair.models.groups import (
    CreateGroupResponse,
    CreateMemberResponse,
    GetGroupResponse,
    GetGroupsResponse,
    GetMemberResponse,
    GetMembersResponse,
)
from aiopurpleair.models.keys import GetKeysResponse
from aiopurpleair.models.organizations import GetOrganizationResponse
from aiopurpleair.models.sensors import GetSensorHistoryResponse, GetSensorsResponse


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


def test_get_sensor_history_response_snapshot(
    get_sensor_history_response: dict[str, Any], snapshot: SnapshotAssertion
) -> None:
    """The sensor history response model serializes to a stable shape."""
    model = GetSensorHistoryResponse.model_validate(get_sensor_history_response)
    assert model.model_dump(mode="json") == snapshot


def test_get_groups_response_snapshot(get_groups_response: dict[str, Any], snapshot: SnapshotAssertion) -> None:
    """The GET /v1/groups response model serializes to a stable shape."""
    model = GetGroupsResponse.model_validate(get_groups_response)
    assert model.model_dump(mode="json") == snapshot


def test_get_group_response_snapshot(get_group_response: dict[str, Any], snapshot: SnapshotAssertion) -> None:
    """The group detail response model serializes to a stable shape."""
    model = GetGroupResponse.model_validate(get_group_response)
    assert model.model_dump(mode="json") == snapshot


def test_create_group_response_snapshot(create_group_response: dict[str, Any], snapshot: SnapshotAssertion) -> None:
    """The create-group response model serializes to a stable shape."""
    model = CreateGroupResponse.model_validate(create_group_response)
    assert model.model_dump(mode="json") == snapshot


def test_create_member_response_snapshot(create_member_response: dict[str, Any], snapshot: SnapshotAssertion) -> None:
    """The create-member response model serializes to a stable shape."""
    model = CreateMemberResponse.model_validate(create_member_response)
    assert model.model_dump(mode="json") == snapshot


def test_get_members_response_snapshot(get_members_response: dict[str, Any], snapshot: SnapshotAssertion) -> None:
    """The group members-data response model serializes to a stable shape."""
    model = GetMembersResponse.model_validate(get_members_response)
    assert model.model_dump(mode="json") == snapshot


def test_get_member_response_snapshot(get_member_response: dict[str, Any], snapshot: SnapshotAssertion) -> None:
    """The single-member response model serializes to a stable shape."""
    model = GetMemberResponse.model_validate(get_member_response)
    assert model.model_dump(mode="json") == snapshot
