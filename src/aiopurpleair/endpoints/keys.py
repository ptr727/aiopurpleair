"""Define an API endpoint for requests related to API keys."""

from __future__ import annotations

from aiopurpleair.endpoints import APIEndpointsBase
from aiopurpleair.models.keys import GetKeysResponse


class KeysEndpoints(APIEndpointsBase):  # pylint: disable=too-few-public-methods
    """Define the keys API manager object."""

    async def async_check_api_key(self) -> GetKeysResponse:
        """Check the validity of the API key.

        Returns:
            An API response payload in the form of a Pydantic model.
        """
        return await self._async_request("get", "/keys", GetKeysResponse)
