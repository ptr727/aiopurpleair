# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
# aresponses is an untyped mock server; its add()/response-object stubs are
# incomplete, so pyright mistypes the string patterns and the response helper.
"""Define tests for organization endpoints."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import aiohttp
import pytest
from aresponses import ResponsesMockServer

from aiopurpleair import API
from aiopurpleair.errors import RequestError
from aiopurpleair.models.organizations import GetOrganizationResponse
from tests.common import TEST_API_KEY, load_fixture


@pytest.mark.asyncio
async def test_get_organization(aresponses: ResponsesMockServer) -> None:
    """Test the GET /organization endpoint.

    Args:
        aresponses: An aresponses server.
    """
    aresponses.add(
        "api.purpleair.com",
        "/v1/organization",
        "get",
        response=aiohttp.web_response.json_response(
            json.loads(load_fixture("get_organization_response.json")), status=200
        ),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        response = await api.organizations.async_get_organization()
        assert isinstance(response, GetOrganizationResponse)
        assert response.api_version == "V1.0.11-0.0.41"
        assert response.timestamp_utc == datetime(2022, 10, 27, 20, 40, 45, tzinfo=UTC)
        assert response.organization_id == "abc123def456"
        assert response.organization_name == "Test Org"
        assert response.remaining_points == 50000
        assert response.consumption_rate == 1500

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_get_organization_validation_error(
    aresponses: ResponsesMockServer,
) -> None:
    """Test the GET /organization endpoint, returning a validation error.

    Args:
        aresponses: An aresponses server.
    """
    raw_response = json.loads(load_fixture("get_organization_response.json"))
    raw_response["remaining_points"] = "not-a-number"

    aresponses.add(
        "api.purpleair.com",
        "/v1/organization",
        "get",
        response=aiohttp.web_response.json_response(raw_response, status=200),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        with pytest.raises(RequestError) as err:
            await api.organizations.async_get_organization()
        assert "Error while parsing response" in str(err.value)

    aresponses.assert_plan_strictly_followed()
