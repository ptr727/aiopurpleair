"""Define request and response models for groups.

All group and member response shapes are verified against the live API. The
members-data reads reuse the sensors response shape with ``group_id`` (and the
single-member read also carries ``member_id``); ``max_age`` and
``firmware_default_version`` are present but kept optional for robustness.
"""

# pylint: disable=too-few-public-methods
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator, model_validator

from aiopurpleair.const import SENSOR_FIELDS, LocationType
from aiopurpleair.helpers.model import PurpleAirBaseModel
from aiopurpleair.helpers.validator import validate_timestamp
from aiopurpleair.models.sensors import SensorModel


class GroupSummary(PurpleAirBaseModel):
    """Define a group as listed by GET /v1/groups."""

    id: int
    name: str
    created_utc: datetime = Field(alias="created")

    validate_created_utc = field_validator("created_utc", mode="before")(validate_timestamp)


class GroupMember(PurpleAirBaseModel):
    """Define a member entry within a group's detail."""

    id: int
    sensor_index: int
    created_utc: datetime = Field(alias="created")

    validate_created_utc = field_validator("created_utc", mode="before")(validate_timestamp)


class GetGroupsResponse(PurpleAirBaseModel):
    """Define a response to GET /v1/groups."""

    api_version: str
    groups: list[GroupSummary]
    timestamp_utc: datetime = Field(alias="time_stamp")
    data_timestamp_utc: datetime = Field(alias="data_time_stamp")

    validate_timestamp_utc = field_validator("timestamp_utc", mode="before")(validate_timestamp)

    validate_data_timestamp_utc = field_validator("data_timestamp_utc", mode="before")(validate_timestamp)


class GetGroupResponse(PurpleAirBaseModel):
    """Define a response to GET /v1/groups/:group_id."""

    api_version: str
    group_id: int
    members: list[GroupMember]
    timestamp_utc: datetime = Field(alias="time_stamp")
    data_timestamp_utc: datetime = Field(alias="data_time_stamp")

    validate_timestamp_utc = field_validator("timestamp_utc", mode="before")(validate_timestamp)

    validate_data_timestamp_utc = field_validator("data_timestamp_utc", mode="before")(validate_timestamp)


class CreateGroupRequest(PurpleAirBaseModel):
    """Define a request to POST /v1/groups."""

    name: str


class CreateGroupResponse(PurpleAirBaseModel):
    """Define a response to POST /v1/groups."""

    api_version: str
    group_id: int
    timestamp_utc: datetime = Field(alias="time_stamp")

    validate_timestamp_utc = field_validator("timestamp_utc", mode="before")(validate_timestamp)


class CreateMemberRequest(PurpleAirBaseModel):
    """Define a request to POST /v1/groups/:group_id/members."""

    sensor_index: int | None = None
    sensor_id: str | None = None
    owner_email: str | None = None
    location_type: int | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_identifier_present(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Require a sensor identifier.

        Args:
            values: The fields passed into the model.

        Returns:
            The fields.

        Raises:
            ValueError: Neither a sensor_index nor a sensor_id was provided.
        """
        if values.get("sensor_index") is None and values.get("sensor_id") is None:
            raise ValueError("must pass either sensor_index or sensor_id")
        return values

    @field_validator("location_type", mode="before")
    @classmethod
    def validate_location_type(cls, value: LocationType) -> int:
        """Validate the location type.

        Args:
            value: A LocationType value.

        Returns:
            The integer-based interpretation of a location type.
        """
        return value.value


class CreateMemberResponse(PurpleAirBaseModel):
    """Define a response to POST /v1/groups/:group_id/members."""

    api_version: str
    group_id: int
    member_id: int
    timestamp_utc: datetime = Field(alias="time_stamp")

    validate_timestamp_utc = field_validator("timestamp_utc", mode="before")(validate_timestamp)


class GetMembersResponse(PurpleAirBaseModel):
    """Define a response to GET /v1/groups/:group_id/members.

    Mirrors GetSensorsResponse (fields + row-oriented data) with a ``group_id``.
    """

    fields: list[str]
    data: dict[int, SensorModel]

    api_version: str
    group_id: int
    max_age: int | None = None
    firmware_default_version: str | None = None
    timestamp_utc: datetime = Field(alias="time_stamp")
    data_timestamp_utc: datetime = Field(alias="data_time_stamp")

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Reshape the row-oriented data into a mapping keyed by sensor index.

        Args:
            values: The response payload.

        Returns:
            The response payload with ``data`` keyed by sensor index.

        Raises:
            ValueError: An unknown field was received.
        """
        for field in values["fields"]:
            if field not in SENSOR_FIELDS:
                raise ValueError(f"{field} is an unknown field")

        values["data"] = {
            sensor_values[0]: SensorModel.model_validate(
                dict(zip(values["fields"], sensor_values))  # noqa: B905
            )
            for sensor_values in values["data"]
        }
        return values

    validate_timestamp_utc = field_validator("timestamp_utc", mode="before")(validate_timestamp)

    validate_data_timestamp_utc = field_validator("data_timestamp_utc", mode="before")(validate_timestamp)


class GetMemberResponse(PurpleAirBaseModel):
    """Define a response to GET /v1/groups/:group_id/members/:member_id.

    Mirrors GetSensorResponse (a single sensor) with ``group_id`` and
    ``member_id``.
    """

    api_version: str
    group_id: int
    member_id: int
    sensor: SensorModel
    data_timestamp_utc: datetime = Field(alias="data_time_stamp")
    timestamp_utc: datetime = Field(alias="time_stamp")

    validate_data_timestamp_utc = field_validator("data_timestamp_utc", mode="before")(validate_timestamp)

    validate_timestamp_utc = field_validator("timestamp_utc", mode="before")(validate_timestamp)
