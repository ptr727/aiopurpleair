"""Define API endpoints."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from aiopurpleair.errors import InvalidRequestError
from aiopurpleair.helpers.model import PurpleAirBaseModel, PurpleAirBaseModelT

if TYPE_CHECKING:
    from aiopurpleair.api import API


class APIEndpointsBase:  # pylint: disable=too-few-public-methods
    """Define a base API endpoints manager."""

    def __init__(self, api: API) -> None:
        """Initialize.

        Args:
            api: The API object that owns the request transport.
        """
        self._api = api
        self._async_request = api.async_request

    async def _async_endpoint_request_with_models(
        self,
        endpoint: str,
        query_param_map: Iterable[tuple[str, Any]],
        request_model: type[PurpleAirBaseModel],
        response_model: type[PurpleAirBaseModelT],
    ) -> PurpleAirBaseModelT:
        """Perform a GET API endpoint request whose query is validated by a model.

        Args:
            endpoint: The API endpoint to query.
            query_param_map: A tuple of API query parameters to include (if they exist).
            request_model: The Pydantic model for the request.
            response_model: The Pydantic model for the response.

        Returns:
            An API response payload in the form of a Pydantic model.

        Raises:
            InvalidRequestError: Raised on invalid parameters.
        """
        request = self._validate_request(query_param_map, request_model)
        return await self._async_request(
            "get",
            endpoint,
            response_model,
            params=request.model_dump(exclude_none=True),
        )

    @staticmethod
    def _validate_request(
        query_param_map: Iterable[tuple[str, Any]],
        request_model: type[PurpleAirBaseModel],
    ) -> PurpleAirBaseModel:
        """Validate caller parameters against a request model.

        Args:
            query_param_map: A tuple of API parameters to include (if they exist).
            request_model: The Pydantic model for the request.

        Returns:
            The validated request model.

        Raises:
            InvalidRequestError: Raised on invalid parameters.
        """
        try:
            return request_model.model_validate(
                {
                    api_query_param: func_param
                    for api_query_param, func_param in query_param_map
                    if func_param is not None
                }
            )
        except ValidationError as err:
            raise InvalidRequestError(err) from err
