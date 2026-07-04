# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
# aresponses is an untyped mock server; its add()/response-object stubs are
# incomplete, so pyright mistypes the string patterns and the response helper.
"""Define tests for the API object."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import MagicMock

import aiohttp
import pytest
from aresponses import ResponsesMockServer

from aiopurpleair import API
from aiopurpleair.errors import (
    ApiDisabledError,
    ApiKeyRestrictedError,
    ApiKeyTypeMismatchError,
    DataInitializingError,
    InvalidApiKeyError,
    InvalidAverageError,
    InvalidBoundingBoxError,
    InvalidCfError,
    InvalidDataReadKeyError,
    InvalidFieldValueError,
    InvalidJsonPayloadError,
    InvalidLocationTypeError,
    InvalidMaxAgeError,
    InvalidModifiedSinceError,
    InvalidParameterValueError,
    InvalidRequestError,
    InvalidRequestUrlError,
    InvalidShowValueError,
    InvalidTimestampError,
    InvalidTimestampSpanError,
    InvalidTokenError,
    MissingFieldsParameterError,
    MissingJsonPayloadError,
    MissingRequiredParameterError,
    NotFoundError,
    PaymentRequiredError,
    ProjectArchivedError,
    PurpleAirError,
    RateLimitExceededError,
    RequestError,
    RequiresHttpsError,
    raise_error,
)
from aiopurpleair.models.keys import ApiKeyType, GetKeysResponse
from tests.common import TEST_API_KEY, load_fixture


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_fixture_filename,err_type,status_code",
    [
        ("error_invalid_api_key_response.json", InvalidApiKeyError, 403),
        ("error_missing_api_key_response.json", InvalidApiKeyError, 403),
        ("error_not_found_response.json", NotFoundError, 404),
        ("error_unknown_response.json", RequestError, 500),
    ],
)
async def test_api_error(
    aresponses: ResponsesMockServer,
    err_type: type[RequestError],
    error_fixture_filename: str,
    status_code: int,
) -> None:
    """Test an invalid API call.

    Args:
        aresponses: An aresponses server.
        err_type: A subclass of PurpleAirError.
        error_fixture_filename: A fixture that contains an error API response.
        status_code: An HTTP status code.
    """
    aresponses.add(
        "api.purpleair.com",
        "/v1/bad_endpoint",
        "get",
        response=aiohttp.web_response.json_response(
            json.loads(load_fixture(error_fixture_filename)), status=status_code
        ),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        with pytest.raises(err_type):
            await api.async_request("get", "/bad_endpoint", GetKeysResponse)

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_code,err_type,base_type,status_code",
    [
        ("ApiKeyTypeMismatchError", ApiKeyTypeMismatchError, InvalidApiKeyError, 403),
        ("ApiKeyRestrictedError", ApiKeyRestrictedError, InvalidApiKeyError, 403),
        ("ApiDisabledError", ApiDisabledError, InvalidApiKeyError, 403),
        ("ProjectArchivedError", ProjectArchivedError, InvalidApiKeyError, 403),
        ("InvalidTokenError", InvalidTokenError, InvalidApiKeyError, 403),
        ("InvalidDataReadKeyError", InvalidDataReadKeyError, InvalidRequestError, 400),
        ("InvalidFieldValueError", InvalidFieldValueError, InvalidRequestError, 400),
        (
            "InvalidParameterValueError",
            InvalidParameterValueError,
            InvalidRequestError,
            400,
        ),
        (
            "MissingRequiredParameterError",
            MissingRequiredParameterError,
            InvalidRequestError,
            400,
        ),
        ("InvalidRequestUrlError", InvalidRequestUrlError, InvalidRequestError, 400),
        ("InvalidTimestampError", InvalidTimestampError, InvalidRequestError, 400),
        (
            "InvalidTimestampSpanError",
            InvalidTimestampSpanError,
            InvalidRequestError,
            400,
        ),
        ("InvalidAverageError", InvalidAverageError, InvalidRequestError, 400),
        (
            "MissingFieldsParameterError",
            MissingFieldsParameterError,
            InvalidRequestError,
            400,
        ),
        ("InvalidShowValueError", InvalidShowValueError, InvalidRequestError, 400),
        (
            "InvalidLocationTypeError",
            InvalidLocationTypeError,
            InvalidRequestError,
            400,
        ),
        (
            "InvalidModifiedSinceError",
            InvalidModifiedSinceError,
            InvalidRequestError,
            400,
        ),
        ("InvalidMaxAgeError", InvalidMaxAgeError, InvalidRequestError, 400),
        ("InvalidCfError", InvalidCfError, InvalidRequestError, 400),
        (
            "InvalidBoundingBoxError",
            InvalidBoundingBoxError,
            InvalidRequestError,
            400,
        ),
        ("MissingJsonPayloadError", MissingJsonPayloadError, InvalidRequestError, 415),
        ("InvalidJsonPayloadError", InvalidJsonPayloadError, InvalidRequestError, 400),
        ("RequiresHttpsError", RequiresHttpsError, RequestError, 403),
        ("PaymentRequiredError", PaymentRequiredError, RequestError, 402),
        ("RateLimitExceededError", RateLimitExceededError, RequestError, 429),
        ("DataInitializingError", DataInitializingError, RequestError, 503),
    ],
)
async def test_api_error_codes(
    aresponses: ResponsesMockServer,
    error_code: str,
    err_type: type[PurpleAirError],
    base_type: type[PurpleAirError],
    status_code: int,
) -> None:
    """Test the typed exception subclasses introduced for PurpleAir error codes.

    Each newly-mapped error code (HTTP 400/402/403/415/429/503 family) must
    raise its specific subclass, transitively inherit from RequestError so that
    existing `except RequestError:` catch-alls keep working, and chain the
    aiohttp ClientError as `__cause__`. Pre-existing codes covered by
    `test_api_error` (ApiKeyMissingError, ApiKeyInvalidError, NotFoundError)
    are intentionally not duplicated here.

    Args:
        aresponses: An aresponses server.
        error_code: The PurpleAir API error-code string.
        err_type: The aiopurpleair exception subclass that should be raised.
        base_type: The documented base class that must also catch the subclass.
        status_code: The HTTP status code the API returns for this error.
    """
    payload = {
        "api_version": "V1.0.11-0.0.41",
        "time_stamp": 1666903245,
        "error": error_code,
        "description": f"Synthesised description for {error_code}.",
    }

    aresponses.add(
        "api.purpleair.com",
        "/v1/bad_endpoint",
        "get",
        response=aiohttp.web_response.json_response(payload, status=status_code),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        with pytest.raises(err_type) as captured:
            await api.async_request("get", "/bad_endpoint", GetKeysResponse)
        assert isinstance(captured.value, base_type)
        assert isinstance(captured.value, RequestError)
        assert isinstance(captured.value.__cause__, aiohttp.ClientError)

    aresponses.assert_plan_strictly_followed()


def test_raise_error_isolates_cause_per_instance() -> None:
    """Regression: __cause__ must live on the instance, not the class.

    Previously raise_error set __cause__ as a class attribute, so the second
    raise of the same error type would inherit a stale __cause__ from the
    first.
    """
    resp = MagicMock(url="https://api.purpleair.com/v1/sensors/1")
    payload = {"error": "InvalidDataReadKeyError", "description": "first"}
    first_cause = aiohttp.ClientError("network blip")

    with pytest.raises(InvalidDataReadKeyError) as first:
        raise_error(resp, payload, first_cause)
    assert first.value.__cause__ is first_cause

    with pytest.raises(InvalidDataReadKeyError) as second:
        try:
            raise RuntimeError("upstream context")
        except RuntimeError:
            raise_error(resp, {**payload, "description": "second"}, None)
    assert second.value.__cause__ is None
    assert second.value.__suppress_context__ is False
    assert isinstance(second.value.__context__, RuntimeError)
    assert first.value.__cause__ is first_cause


def test_raise_error_surfaces_http_error_without_payload() -> None:
    """An HTTP failure with no PurpleAir `error` key must not be swallowed.

    Without this, a non-PurpleAir HTTP error (proxy 502, HTML body, JSON in
    the wrong shape, etc.) reaches the caller as a confusing pydantic
    ValidationError instead of the original transport failure.
    """
    resp = MagicMock(url="https://api.purpleair.com/v1/sensors/1")
    cause = aiohttp.ClientError("502 Bad Gateway")

    with pytest.raises(RequestError) as captured:
        raise_error(resp, {"unexpected": "shape"}, cause)
    assert captured.value.__cause__ is cause

    raise_error(resp, {"unexpected": "shape"}, None)


@pytest.mark.asyncio
@pytest.mark.parametrize("use_session", [True, False])
async def test_check_api_key(aresponses: ResponsesMockServer, use_session: bool) -> None:
    """Test the GET /keys endpoint.

    Args:
        aresponses: An aresponses server.
        use_session: Whether an existing aiohttp ClientSession should be used.
    """
    aresponses.add(
        "api.purpleair.com",
        "/v1/keys",
        "get",
        response=aiohttp.web_response.json_response(json.loads(load_fixture("get_keys_response.json")), status=200),
    )

    if use_session:
        async with aiohttp.ClientSession() as session:
            api = API(TEST_API_KEY, session=session)
    else:
        api = API(TEST_API_KEY)

    response = await api.keys.async_check_api_key()
    assert isinstance(response, GetKeysResponse)
    assert response.api_key_type == ApiKeyType.READ
    assert response.api_version == "V1.0.11-0.0.41"
    assert response.timestamp_utc == datetime(2022, 10, 27, 18, 25, 41, tzinfo=UTC)

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_check_api_key_validation_error(aresponses: ResponsesMockServer) -> None:
    """Test the GET /keys endpoint, returning a validation error.

    Args:
        aresponses: An aresponses server.
    """
    raw_response = json.loads(load_fixture("get_keys_response.json"))
    raw_response["api_key_type"] = "FAKE"

    aresponses.add(
        "api.purpleair.com",
        "/v1/keys",
        "get",
        response=aiohttp.web_response.json_response(raw_response, status=200),
    )

    async with aiohttp.ClientSession() as session:
        with pytest.raises(RequestError) as err:
            api = API(TEST_API_KEY, session=session)
            _ = await api.keys.async_check_api_key()
        assert "FAKE is an unknown API key type" in str(err.value)

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_async_request_non_json_body(aresponses: ResponsesMockServer) -> None:
    """A 2xx response with a non-JSON body raises RequestError, not a raw JSONDecodeError.

    Args:
        aresponses: An aresponses server.
    """
    aresponses.add(
        "api.purpleair.com",
        "/v1/keys",
        "get",
        response=aiohttp.web_response.Response(status=200, text="<html>not json</html>", content_type="text/html"),
    )

    async with aiohttp.ClientSession() as session:
        api = API(TEST_API_KEY, session=session)
        with pytest.raises(RequestError) as err:
            await api.async_request("get", "/keys", GetKeysResponse)
        assert "Non-JSON response" in str(err.value)

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_async_request_wraps_connection_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """A transport-level ClientError is surfaced as a RequestError.

    Args:
        monkeypatch: The pytest monkeypatch fixture.
    """

    def boom(*_args: object, **_kwargs: object) -> object:
        raise aiohttp.ClientConnectionError("no route to host")

    monkeypatch.setattr(aiohttp.ClientSession, "request", boom)

    api = API(TEST_API_KEY)
    with pytest.raises(RequestError) as err:
        await api.async_request("get", "/keys", GetKeysResponse)
    assert "HTTP error requesting" in str(err.value)


def test_get_map_url() -> None:
    """Test getting the map URL for a sensor index."""
    api = API(TEST_API_KEY)
    map_url = api.get_map_url(12345)
    assert map_url == "https://map.purpleair.com/1/mAQI/a10/p604800/cC0?select=12345"
