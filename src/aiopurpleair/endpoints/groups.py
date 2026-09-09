"""Define an API endpoint for requests related to groups."""

from __future__ import annotations

from datetime import datetime

from aiopurpleair.const import LocationType
from aiopurpleair.endpoints import APIEndpointsBase
from aiopurpleair.models.groups import (
    CreateGroupRequest,
    CreateGroupResponse,
    CreateMemberRequest,
    CreateMemberResponse,
    GetGroupResponse,
    GetGroupsResponse,
    GetMemberResponse,
    GetMembersResponse,
)
from aiopurpleair.models.sensors import (
    GetSensorHistoryRequest,
    GetSensorRequest,
    GetSensorsRequest,
)


class GroupsEndpoints(APIEndpointsBase):
    """Define the groups API manager object."""

    async def async_get_groups(self) -> GetGroupsResponse:
        """Get the list of groups owned by this API key.

        Returns:
            An API response payload in the form of a Pydantic model.
        """
        return await self._async_request("get", "/groups", GetGroupsResponse)

    async def async_create_group(self, name: str) -> CreateGroupResponse:
        """Create a new group.

        Args:
            name: The name to give the new group.

        Returns:
            An API response payload in the form of a Pydantic model.
        """
        request = self._validate_request((("name", name),), CreateGroupRequest)
        return await self._async_request(
            "post",
            "/groups",
            CreateGroupResponse,
            json=request.model_dump(exclude_none=True),
        )

    async def async_get_group(self, group_id: int) -> GetGroupResponse:
        """Get the detail (members) of a group.

        Args:
            group_id: The group to get.

        Returns:
            An API response payload in the form of a Pydantic model.
        """
        return await self._async_request("get", f"/groups/{group_id}", GetGroupResponse)

    async def async_delete_group(self, group_id: int) -> None:
        """Delete a group.

        Args:
            group_id: The group to delete.
        """
        await self._api.async_request_none("delete", f"/groups/{group_id}")

    async def async_create_member(
        self,
        group_id: int,
        *,
        sensor_index: int | None = None,
        sensor_id: str | None = None,
        owner_email: str | None = None,
        location_type: LocationType | None = None,
    ) -> CreateMemberResponse:
        """Add a sensor to a group as a member.

        Provide either ``sensor_index`` or ``sensor_id``. Adding a private sensor
        also requires ``owner_email`` (the sensor's registration email).

        Args:
            group_id: The group to add the member to.
            sensor_index: The sensor_index of the sensor to add.
            sensor_id: The sensor_id (as printed on the sensor's label) to add.
            owner_email: The registration email, required for a private sensor.
            location_type: The expected location type of the sensor.

        Returns:
            An API response payload in the form of a Pydantic model.
        """
        request = self._validate_request(
            (
                ("sensor_index", sensor_index),
                ("sensor_id", sensor_id),
                ("owner_email", owner_email),
                ("location_type", location_type),
            ),
            CreateMemberRequest,
        )
        return await self._async_request(
            "post",
            f"/groups/{group_id}/members",
            CreateMemberResponse,
            json=request.model_dump(exclude_none=True),
        )

    async def async_delete_member(self, group_id: int, member_id: int) -> None:
        """Remove a member from a group.

        Args:
            group_id: The group to remove the member from.
            member_id: The member to remove.
        """
        await self._api.async_request_none("delete", f"/groups/{group_id}/members/{member_id}")

    async def async_get_members(  # pylint: disable=too-many-arguments
        self,
        group_id: int,
        fields: list[str],
        *,
        location_type: LocationType | None = None,
        max_age: int | None = None,
        modified_since_utc: datetime | None = None,
        nw_latitude: float | None = None,
        nw_longitude: float | None = None,
        read_keys: list[str] | None = None,
        se_latitude: float | None = None,
        se_longitude: float | None = None,
        sensor_indices: list[int] | None = None,
    ) -> GetMembersResponse:
        """Get sensor data for all members of a group.

        Args:
            group_id: The group to get member data for.
            fields: The sensor data fields to include.
            location_type: An optional LocationType to filter by.
            max_age: Filter results modified within these seconds.
            modified_since_utc: Filter results modified since a datetime.
            nw_latitude: The latitude of the NW corner of an optional bounding box.
            nw_longitude: The longitude of the NW corner of an optional bounding box.
            read_keys: Optional read keys for private sensors.
            se_latitude: The latitude of the SE corner of an optional bounding box.
            se_longitude: The longitude of the SE corner of an optional bounding box.
            sensor_indices: Filter results by sensor index.

        Returns:
            An API response payload in the form of a Pydantic model.
        """
        response: GetMembersResponse = await self._async_endpoint_request_with_models(
            f"/groups/{group_id}/members",
            (
                ("fields", fields),
                ("location_type", location_type),
                ("max_age", max_age),
                ("modified_since", modified_since_utc),
                ("nwlat", nw_latitude),
                ("nwlng", nw_longitude),
                ("read_keys", read_keys),
                ("selat", se_latitude),
                ("selng", se_longitude),
                ("show_only", sensor_indices),
            ),
            GetSensorsRequest,
            GetMembersResponse,
        )
        return response

    async def async_get_member(
        self,
        group_id: int,
        member_id: int,
        *,
        fields: list[str] | None = None,
        read_key: str | None = None,
    ) -> GetMemberResponse:
        """Get sensor data for a single group member.

        Args:
            group_id: The group the member belongs to.
            member_id: The member to get data for.
            fields: The optional sensor data fields to include.
            read_key: An optional read key for a private sensor.

        Returns:
            An API response payload in the form of a Pydantic model.
        """
        response: GetMemberResponse = await self._async_endpoint_request_with_models(
            f"/groups/{group_id}/members/{member_id}",
            (
                ("fields", fields),
                ("read_key", read_key),
            ),
            GetSensorRequest,
            GetMemberResponse,
        )
        return response

    async def async_get_member_history_csv(  # pylint: disable=too-many-arguments
        self,
        group_id: int,
        member_id: int,
        fields: list[str],
        *,
        start_timestamp_utc: datetime | None = None,
        end_timestamp_utc: datetime | None = None,
        average: int | None = None,
    ) -> str:
        """Get historical data for a group member as raw CSV.

        Args:
            group_id: The group the member belongs to.
            member_id: The member to get history for.
            fields: The sensor data fields to include.
            start_timestamp_utc: The start of the history window (in UTC).
            end_timestamp_utc: The end of the history window (in UTC).
            average: The averaging period in minutes (e.g. 0, 10, 60, 1440).

        Returns:
            The raw CSV response body as a string.
        """
        request = self._validate_request(
            (
                ("fields", fields),
                ("start_timestamp", start_timestamp_utc),
                ("end_timestamp", end_timestamp_utc),
                ("average", average),
            ),
            GetSensorHistoryRequest,
        )
        return await self._api.async_request_text(
            "get",
            f"/groups/{group_id}/members/{member_id}/history/csv",
            params=request.model_dump(exclude_none=True),
        )
