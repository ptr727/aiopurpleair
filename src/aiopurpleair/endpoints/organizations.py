"""Define an API endpoint for requests related to organizations."""

from __future__ import annotations

from typing import cast

from aiopurpleair.endpoints import APIEndpointsBase
from aiopurpleair.models.organizations import GetOrganizationResponse


class OrganizationsEndpoints(APIEndpointsBase):  # pylint: disable=too-few-public-methods
    """Define the organizations API manager object."""

    async def async_get_organization(self) -> GetOrganizationResponse:
        """Get organization information.

        Returns:
            An API response payload in the form of a Pydantic model.
        """
        return cast(
            GetOrganizationResponse,
            await self._async_request(
                "get",
                "/organization",
                GetOrganizationResponse,
            ),
        )
