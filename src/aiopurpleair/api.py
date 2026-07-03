"""Define an API client."""

from __future__ import annotations

import json
from typing import Any, cast

from aiohttp import ClientResponse, ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError
from pydantic import ValidationError

from aiopurpleair.const import LOGGER
from aiopurpleair.endpoints.groups import GroupsEndpoints
from aiopurpleair.endpoints.organizations import OrganizationsEndpoints
from aiopurpleair.endpoints.sensors import SensorsEndpoints
from aiopurpleair.errors import RequestError, raise_error
from aiopurpleair.helpers.model import PurpleAirBaseModelT
from aiopurpleair.models.keys import GetKeysResponse

API_URL_BASE = "https://api.purpleair.com/v1"

DEFAULT_TIMEOUT = 10

MAP_URL_BASE = "https://map.purpleair.com/1/mAQI/a10/p604800/cC0"


class API:
    """Define the API object."""

    def __init__(
        self,
        api_key: str,
        *,
        session: ClientSession | None = None,
    ) -> None:
        """Initialize.

        Args:
            api_key: A PurpleAir API key.
            session: An optional aiohttp ClientSession.
        """
        self._api_key = api_key
        self._session = session

        self.groups = GroupsEndpoints(self)
        self.organizations = OrganizationsEndpoints(self)
        self.sensors = SensorsEndpoints(self)

    async def async_check_api_key(self) -> GetKeysResponse:
        """Check the validity of the API key.

        Returns:
            An API response payload.
        """
        return await self.async_request("get", "/keys", GetKeysResponse)

    async def _async_send(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> tuple[ClientResponse, str]:
        """Send an HTTP request and raise the appropriate PurpleAir error.

        This is the shared transport for the JSON, text (CSV), and empty (204)
        response wrappers. It reads the body as text (so non-JSON responses like
        CSV are supported), raises for a PurpleAir error payload, and returns the
        response together with the raw body text.

        Args:
            method: An HTTP method.
            endpoint: A relative API endpoint.
            **kwargs: Additional kwargs to send with the request.

        Returns:
            A tuple of the aiohttp response and the raw body text.

        Raises:
            RequestError: Raised on an HTTP error with no PurpleAir error payload.
        """
        url: str = f"{API_URL_BASE}{endpoint}"

        kwargs.setdefault("headers", {})
        if self._api_key:
            kwargs["headers"]["X-API-Key"] = self._api_key

        if self._session is not None and not self._session.closed:
            session = self._session
            use_running_session = True
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))
            use_running_session = False

        try:
            async with session.request(method, url, **kwargs) as resp:
                text = await resp.text()
                raising_err = None

                try:
                    resp.raise_for_status()
                except ClientError as err:
                    raising_err = err

                # An error body is always JSON ({"error": ..., "description": ...});
                # a success body may be JSON or CSV, so a parse failure just means
                # "no error payload" and raise_error is a no-op for a 2xx response.
                payload: dict[str, Any] = {}
                if text:
                    try:
                        parsed = json.loads(text)
                    except json.JSONDecodeError:
                        parsed = None
                    if isinstance(parsed, dict):
                        payload = cast(dict[str, Any], parsed)

                raise_error(resp, payload, raising_err)
        finally:
            if not use_running_session:
                await session.close()

        return resp, text

    async def async_request(
        self,
        method: str,
        endpoint: str,
        response_model: type[PurpleAirBaseModelT],
        **kwargs: Any,
    ) -> PurpleAirBaseModelT:
        """Make an API request and parse the JSON response into a model.

        Args:
            method: An HTTP method.
            endpoint: A relative API endpoint.
            response_model: A Pydantic model to parse the response data with.
            **kwargs: Additional kwargs to send with the request.

        Returns:
            An API response payload in the form of a Pydantic model.

        Raises:
            RequestError: Raised when response data can't be validated.
        """
        _, text = await self._async_send(method, endpoint, **kwargs)

        data = json.loads(text)
        LOGGER.debug("Data received for %s: %s", endpoint, data)

        try:
            return response_model.model_validate(data)
        except ValidationError as err:
            raise RequestError(f"Error while parsing response from {endpoint}: {err}") from err

    async def async_request_text(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> str:
        """Make an API request and return the raw response body text.

        Used by the CSV endpoints, whose response body is ``text/csv`` rather
        than JSON.

        Args:
            method: An HTTP method.
            endpoint: A relative API endpoint.
            **kwargs: Additional kwargs to send with the request.

        Returns:
            The raw response body as a string.
        """
        _, text = await self._async_send(method, endpoint, **kwargs)
        return text

    async def async_request_none(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> None:
        """Make an API request that returns no content (e.g. a 204 delete).

        Args:
            method: An HTTP method.
            endpoint: A relative API endpoint.
            **kwargs: Additional kwargs to send with the request.
        """
        await self._async_send(method, endpoint, **kwargs)

    def get_map_url(self, sensor_index: int) -> str:
        """Get the map URL for a sensor index.

        Args:
            sensor_index: The sensor index to get the map URL for.

        Returns:
            A MAP URL.
        """
        return f"{MAP_URL_BASE}?select={sensor_index}"
