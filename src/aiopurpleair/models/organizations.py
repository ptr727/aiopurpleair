"""Define request and response models for organizations."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field, field_validator

from aiopurpleair.helpers.model import PurpleAirBaseModel
from aiopurpleair.helpers.validator import validate_timestamp


class GetOrganizationResponse(PurpleAirBaseModel):
    """Define a response to GET /v1/organization."""

    api_version: str
    timestamp_utc: datetime = Field(alias="time_stamp")
    organization_id: str
    organization_name: str
    remaining_points: int
    consumption_rate: int

    validate_utc_timestamp = field_validator("timestamp_utc", mode="before")(validate_timestamp)
