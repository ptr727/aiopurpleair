"""Define dynamic fixtures."""

import json
from typing import Any, cast

import pytest

from tests.common import load_fixture


@pytest.fixture(name="error_invalid_api_key_response", scope="session")
def error_invalid_api_key_response_fixture() -> dict[str, Any]:
    """Define a fixture for error response data from GET /v1/keys.

    Args:
        Define an API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("error_invalid_api_key_response.json")))


@pytest.fixture(name="get_keys_response", scope="session")
def get_keys_response_fixture() -> dict[str, Any]:
    """Define a fixture for successful response data from GET /v1/keys.

    Args:
        Define an API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("get_keys_response.json")))


@pytest.fixture(name="get_sensors_response", scope="session")
def get_sensors_response_fixture() -> dict[str, Any]:
    """Define a fixture for successful response data from GET /v1/sensors.

    Args:
        Define an API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("get_sensors_response.json")))


@pytest.fixture(name="get_organization_response", scope="session")
def get_organization_response_fixture() -> dict[str, Any]:
    """Define a fixture for successful response data from GET /v1/organization.

    Returns:
        An API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("get_organization_response.json")))


@pytest.fixture(name="get_sensor_history_response", scope="session")
def get_sensor_history_response_fixture() -> dict[str, Any]:
    """Define a fixture for response data from GET /v1/sensors/:sensor_index/history.

    Returns:
        An API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("get_sensor_history_response.json")))


@pytest.fixture(name="get_groups_response", scope="session")
def get_groups_response_fixture() -> dict[str, Any]:
    """Define a fixture for response data from GET /v1/groups.

    Returns:
        An API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("get_groups_response.json")))


@pytest.fixture(name="get_group_response", scope="session")
def get_group_response_fixture() -> dict[str, Any]:
    """Define a fixture for response data from GET /v1/groups/:group_id.

    Returns:
        An API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("get_group_response.json")))


@pytest.fixture(name="create_group_response", scope="session")
def create_group_response_fixture() -> dict[str, Any]:
    """Define a fixture for response data from POST /v1/groups.

    Returns:
        An API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("create_group_response.json")))


@pytest.fixture(name="create_member_response", scope="session")
def create_member_response_fixture() -> dict[str, Any]:
    """Define a fixture for response data from POST /v1/groups/:group_id/members.

    Returns:
        An API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("create_member_response.json")))


@pytest.fixture(name="get_members_response", scope="session")
def get_members_response_fixture() -> dict[str, Any]:
    """Define a fixture for response data from GET /v1/groups/:group_id/members.

    Returns:
        An API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("get_members_response.json")))


@pytest.fixture(name="get_member_response", scope="session")
def get_member_response_fixture() -> dict[str, Any]:
    """Define a fixture for response data from a single group member.

    Returns:
        An API response payload.
    """
    return cast(dict[str, Any], json.loads(load_fixture("get_member_response.json")))
