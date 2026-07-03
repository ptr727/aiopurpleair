# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
# aresponses is an untyped mock server; its add()/response-object stubs are
# incomplete, so pyright mistypes the string patterns and the response helper.
"""Define tests for group endpoints."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import aiohttp
import pytest
from aresponses import ResponsesMockServer

from aiopurpleair import API
from aiopurpleair.const import LocationType
from aiopurpleair.errors import InvalidRequestError
from aiopurpleair.models.sensors import SensorModel
from tests.common import TEST_API_KEY, load_fixture


@pytest.mark.asyncio
async def test_get_groups(aresponses: ResponsesMockServer) -> None:
    """Test the GET /groups endpoint.

    Args:
        aresponses: An aresponses server.
    """
    aresponses.add(
        "api.purpleair.com",
        "/v1/groups",
        "get",
        response=aiohttp.web_response.json_response(json.loads(load_fixture("get_groups_response.json")), status=200),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        response = await api.groups.async_get_groups()
        assert response.api_version == "V1.2.0-1.1.45"
        assert response.timestamp_utc == datetime(2022, 11, 3, 19, 26, 29, tzinfo=UTC)
        assert response.data_timestamp_utc == datetime(2022, 11, 3, 19, 25, 31, tzinfo=UTC)
        assert len(response.groups) == 2
        assert response.groups[0].id == 1234
        assert response.groups[0].name == "My Sensors"
        assert response.groups[0].created_utc == datetime(2021, 9, 29, 22, 46, 14, tzinfo=UTC)

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_create_group(aresponses: ResponsesMockServer) -> None:
    """Test the POST /groups endpoint.

    Args:
        aresponses: An aresponses server.
    """
    aresponses.add(
        "api.purpleair.com",
        "/v1/groups",
        "post",
        response=aiohttp.web_response.json_response(json.loads(load_fixture("create_group_response.json")), status=201),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        response = await api.groups.async_create_group("My Sensors")
        assert response.api_version == "V1.2.0-1.1.45"
        assert response.group_id == 1234
        assert response.timestamp_utc == datetime(2022, 11, 3, 19, 26, 29, tzinfo=UTC)

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_get_group(aresponses: ResponsesMockServer) -> None:
    """Test the GET /groups/:group_id endpoint.

    Args:
        aresponses: An aresponses server.
    """
    aresponses.add(
        "api.purpleair.com",
        "/v1/groups/1234",
        "get",
        response=aiohttp.web_response.json_response(json.loads(load_fixture("get_group_response.json")), status=200),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        response = await api.groups.async_get_group(1234)
        assert response.group_id == 1234
        assert len(response.members) == 2
        assert response.members[0].id == 5678
        assert response.members[0].sensor_index == 131075
        assert response.members[0].created_utc == datetime(2021, 9, 29, 22, 46, 40, tzinfo=UTC)

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_delete_group(aresponses: ResponsesMockServer) -> None:
    """Test the DELETE /groups/:group_id endpoint (204, no body).

    Args:
        aresponses: An aresponses server.
    """
    aresponses.add(
        "api.purpleair.com",
        "/v1/groups/1234",
        "delete",
        response=aresponses.Response(status=204, text=""),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        assert await api.groups.async_delete_group(1234) is None

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_create_member(aresponses: ResponsesMockServer) -> None:
    """Test the POST /groups/:group_id/members endpoint.

    Args:
        aresponses: An aresponses server.
    """
    aresponses.add(
        "api.purpleair.com",
        "/v1/groups/1234/members",
        "post",
        response=aiohttp.web_response.json_response(
            json.loads(load_fixture("create_member_response.json")), status=201
        ),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        response = await api.groups.async_create_member(1234, sensor_index=131075, location_type=LocationType.OUTSIDE)
        assert response.group_id == 1234
        assert response.member_id == 5678

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_create_member_requires_identifier() -> None:
    """A member request without a sensor identifier raises before any request."""
    api = API(TEST_API_KEY)
    with pytest.raises(InvalidRequestError) as err:
        await api.groups.async_create_member(1234, owner_email="a@b.com")
    assert "must pass either sensor_index or sensor_id" in str(err.value)


@pytest.mark.asyncio
async def test_delete_member(aresponses: ResponsesMockServer) -> None:
    """Test the DELETE /groups/:group_id/members/:member_id endpoint.

    Args:
        aresponses: An aresponses server.
    """
    aresponses.add(
        "api.purpleair.com",
        "/v1/groups/1234/members/5678",
        "delete",
        response=aresponses.Response(status=204, text=""),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        assert await api.groups.async_delete_member(1234, 5678) is None

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_get_members(aresponses: ResponsesMockServer) -> None:
    """Test the GET /groups/:group_id/members endpoint.

    Args:
        aresponses: An aresponses server.
    """
    aresponses.add(
        "api.purpleair.com",
        "/v1/groups/1234/members",
        "get",
        response=aiohttp.web_response.json_response(json.loads(load_fixture("get_members_response.json")), status=200),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        response = await api.groups.async_get_members(1234, fields=["name", "latitude", "longitude"])
        assert response.group_id == 1234
        assert response.max_age == 604800
        assert response.firmware_default_version == "7.02"
        assert response.data == {
            131075: SensorModel(
                sensor_index=131075,
                name="Mariners Bluff",
                latitude=33.51511,
                longitude=-117.67972,
            ),
            131079: SensorModel(
                sensor_index=131079,
                name="BRSKBV-outside",
                latitude=37.75315,
                longitude=-122.44364,
            ),
        }

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_get_member(aresponses: ResponsesMockServer) -> None:
    """Test the GET /groups/:group_id/members/:member_id endpoint.

    Args:
        aresponses: An aresponses server.
    """
    aresponses.add(
        "api.purpleair.com",
        "/v1/groups/1234/members/5678",
        "get",
        response=aiohttp.web_response.json_response(json.loads(load_fixture("get_member_response.json")), status=200),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        response = await api.groups.async_get_member(1234, 5678, fields=["name"])
        assert response.group_id == 1234
        assert response.member_id == 5678
        assert response.sensor.sensor_index == 131075
        assert response.sensor.name == "Mariners Bluff"

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_get_member_history_csv(aresponses: ResponsesMockServer) -> None:
    """Test the GET /groups/:group_id/members/:member_id/history/csv endpoint.

    Args:
        aresponses: An aresponses server.
    """
    csv = load_fixture("get_sensor_history_response.csv")
    aresponses.add(
        "api.purpleair.com",
        "/v1/groups/1234/members/5678/history/csv",
        "get",
        response=aresponses.Response(status=200, text=csv, content_type="text/csv"),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        result = await api.groups.async_get_member_history_csv(
            1234,
            5678,
            ["humidity", "pm2.5_atm"],
            start_timestamp_utc=datetime(2022, 11, 1, tzinfo=UTC),
            end_timestamp_utc=datetime(2022, 11, 3, tzinfo=UTC),
            average=60,
        )
        assert result == csv
        assert result.startswith("time_stamp,sensor_index,humidity,pm2.5_atm")

    aresponses.assert_plan_strictly_followed()
