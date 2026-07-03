"""Define request and response models for sensors."""

# pylint: disable=too-few-public-methods
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator, model_validator

from aiopurpleair.const import SENSOR_FIELDS, ChannelFlag, ChannelState, LocationType
from aiopurpleair.helpers.model import PurpleAirBaseModel
from aiopurpleair.helpers.validator import validate_timestamp
from aiopurpleair.helpers.validator.sensors import (
    validate_channel_flag,
    validate_fields_request,
    validate_latitude,
    validate_longitude,
)
from aiopurpleair.util.dt import utc_to_timestamp


class SensorModelStats(PurpleAirBaseModel):
    """Define a model for sensor statistics."""

    pm2_5: float = Field(alias="pm2.5")
    pm2_5_10minute: float = Field(alias="pm2.5_10minute")
    pm2_5_1week: float = Field(alias="pm2.5_1week")
    pm2_5_24hour: float = Field(alias="pm2.5_24hour")
    pm2_5_30minute: float = Field(alias="pm2.5_30minute")
    pm2_5_60minute: float = Field(alias="pm2.5_60minute")
    pm2_5_6hour: float = Field(alias="pm2.5_6hour")
    timestamp_utc: datetime = Field(alias="time_stamp")

    validate_timestamp_utc = field_validator("timestamp_utc", mode="before")(validate_timestamp)


class SensorModel(PurpleAirBaseModel):
    """Define a model for a sensor."""

    sensor_index: int

    altitude: float | None = None
    analog_input: float | None = None
    channel_flags: ChannelFlag | None = None
    channel_flags_auto: ChannelFlag | None = None
    channel_flags_manual: ChannelFlag | None = None
    channel_state: ChannelState | None = None
    confidence: float | None = None
    confidence_auto: float | None = None
    confidence_manual: float | None = None
    date_created_utc: datetime | None = Field(alias="date_created", default=None)
    deciviews: float | None = None
    deciviews_a: float | None = None
    deciviews_b: float | None = None
    firmware_upgrade: str | None = None
    firmware_version: str | None = None
    hardware: str | None = None
    humidity: float | None = None
    humidity_a: float | None = None
    humidity_b: float | None = None
    icon: int | None = None
    is_owner: bool | None = None
    last_modified_utc: datetime | None = Field(alias="last_modified", default=None)
    last_seen_utc: datetime | None = Field(alias="last_seen", default=None)
    latitude: float | None = None
    led_brightness: float | None = None
    location_type: LocationType | None = None
    longitude: float | None = None
    memory: float | None = None
    model: str | None = None
    name: str | None = None
    ozone1: float | None = None
    pa_latency: int | None = None
    pm0_3_um_count: float | None = Field(alias="0.3_um_count", default=None)
    pm0_3_um_count_a: float | None = Field(alias="0.3_um_count_a", default=None)
    pm0_3_um_count_b: float | None = Field(alias="0.3_um_count_b", default=None)
    pm0_5_um_count: float | None = Field(alias="0.5_um_count", default=None)
    pm0_5_um_count_a: float | None = Field(alias="0.5_um_count_a", default=None)
    pm0_5_um_count_b: float | None = Field(alias="0.5_um_count_b", default=None)
    pm10_0: float | None = Field(alias="pm10.0", default=None)
    pm10_0_a: float | None = Field(alias="pm10.0_a", default=None)
    pm10_0_atm: float | None = Field(alias="pm10.0_atm", default=None)
    pm10_0_atm_a: float | None = Field(alias="pm10.0_atm_a", default=None)
    pm10_0_atm_b: float | None = Field(alias="pm10.0_atm_b", default=None)
    pm10_0_b: float | None = Field(alias="pm10.0_b", default=None)
    pm10_0_cf_1: float | None = Field(alias="pm10.0_cf_1", default=None)
    pm10_0_cf_1_a: float | None = Field(alias="pm10.0_cf_1_a", default=None)
    pm10_0_cf_1_b: float | None = Field(alias="pm10.0_cf_1_b", default=None)
    pm10_0_um_count: float | None = Field(alias="10.0_um_count", default=None)
    pm10_0_um_count_a: float | None = Field(alias="10.0_um_count_a", default=None)
    pm10_0_um_count_b: float | None = Field(alias="10.0_um_count_b", default=None)
    pm1_0: float | None = Field(alias="pm1.0", default=None)
    pm1_0_a: float | None = Field(alias="pm1.0_a", default=None)
    pm1_0_atm: float | None = Field(alias="pm1.0_atm", default=None)
    pm1_0_atm_a: float | None = Field(alias="pm1.0_atm_a", default=None)
    pm1_0_atm_b: float | None = Field(alias="pm1.0_atm_b", default=None)
    pm1_0_b: float | None = Field(alias="pm1.0_b", default=None)
    pm1_0_cf_1: float | None = Field(alias="pm1.0_cf_1", default=None)
    pm1_0_cf_1_a: float | None = Field(alias="pm1.0_cf_1_a", default=None)
    pm1_0_cf_1_b: float | None = Field(alias="pm1.0_cf_1_b", default=None)
    pm1_0_um_count: float | None = Field(alias="1.0_um_count", default=None)
    pm1_0_um_count_a: float | None = Field(alias="1.0_um_count_a", default=None)
    pm1_0_um_count_b: float | None = Field(alias="1.0_um_count_b", default=None)
    pm2_5: float | None = Field(alias="pm2.5", default=None)
    pm2_5_10minute: float | None = Field(alias="pm2.5_10minute", default=None)
    pm2_5_10minute_a: float | None = Field(alias="pm2.5_10minute_a", default=None)
    pm2_5_10minute_b: float | None = Field(alias="pm2.5_10minute_b", default=None)
    pm2_5_1week: float | None = Field(alias="pm2.5_1week", default=None)
    pm2_5_1week_a: float | None = Field(alias="pm2.5_1week_a", default=None)
    pm2_5_1week_b: float | None = Field(alias="pm2.5_1week_b", default=None)
    pm2_5_24hour: float | None = Field(alias="pm2.5_24hour", default=None)
    pm2_5_24hour_a: float | None = Field(alias="pm2.5_24hour_a", default=None)
    pm2_5_24hour_b: float | None = Field(alias="pm2.5_24hour_b", default=None)
    pm2_5_30minute: float | None = Field(alias="pm2.5_30minute", default=None)
    pm2_5_30minute_a: float | None = Field(alias="pm2.5_30minute_a", default=None)
    pm2_5_30minute_b: float | None = Field(alias="pm2.5_30minute_b", default=None)
    pm2_5_60minute: float | None = Field(alias="pm2.5_60minute", default=None)
    pm2_5_60minute_a: float | None = Field(alias="pm2.5_60minute_a", default=None)
    pm2_5_60minute_b: float | None = Field(alias="pm2.5_60minute_b", default=None)
    pm2_5_6hour: float | None = Field(alias="pm2.5_6hour", default=None)
    pm2_5_6hour_a: float | None = Field(alias="pm2.5_6hour_a", default=None)
    pm2_5_6hour_b: float | None = Field(alias="pm2.5_6hour_b", default=None)
    pm2_5_a: float | None = Field(alias="pm2.5_a", default=None)
    pm2_5_alt: float | None = Field(alias="pm2.5_alt", default=None)
    pm2_5_alt_a: float | None = Field(alias="pm2.5_alt_a", default=None)
    pm2_5_alt_b: float | None = Field(alias="pm2.5_alt_b", default=None)
    pm2_5_atm: float | None = Field(alias="pm2.5_atm", default=None)
    pm2_5_atm_a: float | None = Field(alias="pm2.5_atm_a", default=None)
    pm2_5_atm_b: float | None = Field(alias="pm2.5_atm_b", default=None)
    pm2_5_b: float | None = Field(alias="pm2.5_b", default=None)
    pm2_5_cf_1: float | None = Field(alias="pm2.5_cf_1", default=None)
    pm2_5_cf_1_a: float | None = Field(alias="pm2.5_cf_1_a", default=None)
    pm2_5_cf_1_b: float | None = Field(alias="pm2.5_cf_1_b", default=None)
    pm2_5_um_count: float | None = Field(alias="2.5_um_count", default=None)
    pm2_5_um_count_a: float | None = Field(alias="2.5_um_count_a", default=None)
    pm2_5_um_count_b: float | None = Field(alias="2.5_um_count_b", default=None)
    pm5_0_um_count: float | None = Field(alias="5.0_um_count", default=None)
    pm5_0_um_count_a: float | None = Field(alias="5.0_um_count_a", default=None)
    pm5_0_um_count_b: float | None = Field(alias="5.0_um_count_b", default=None)
    position_rating: int | None = None
    pressure: float | None = None
    pressure_a: float | None = None
    pressure_b: float | None = None
    primary_id_a: int | None = None
    primary_id_b: int | None = None
    primary_key_a: str | None = None
    primary_key_b: str | None = None
    private: bool | None = None
    rssi: int | None = None
    scattering_coefficient: float | None = None
    scattering_coefficient_a: float | None = None
    scattering_coefficient_b: float | None = None
    secondary_id_a: int | None = None
    secondary_id_b: int | None = None
    secondary_key_a: str | None = None
    secondary_key_b: str | None = None
    stats: SensorModelStats | None = None
    stats_a: SensorModelStats | None = None
    stats_b: SensorModelStats | None = None
    temperature: float | None = None
    temperature_a: float | None = None
    temperature_b: float | None = None
    uptime: int | None = None
    visual_range: float | None = None
    visual_range_a: float | None = None
    visual_range_b: float | None = None
    voc: float | None = None
    voc_a: float | None = None
    voc_b: float | None = None

    validate_channel_flags = field_validator("channel_flags", mode="before")(validate_channel_flag)

    validate_channel_flags_auto = field_validator("channel_flags_auto", mode="before")(validate_channel_flag)

    validate_channel_flags_manual = field_validator("channel_flags_manual", mode="before")(validate_channel_flag)

    @field_validator("channel_state", mode="before")
    @classmethod
    def validate_channel_state(cls, value: int) -> ChannelState:
        """Validate the channel state.

        Args:
            value: The integer-based interpretation of a channel state.

        Returns:
            A ChannelState value.

        Raises:
            ValueError: Raised upon an unknown location type.
        """
        try:
            return ChannelState(value)
        except ValueError as err:
            raise ValueError(f"{value} is an unknown channel state") from err

    validate_date_created_utc = field_validator("date_created_utc", mode="before")(validate_timestamp)

    validate_last_modified_utc = field_validator("last_modified_utc", mode="before")(validate_timestamp)

    validate_last_seen_utc = field_validator("last_seen_utc", mode="before")(validate_timestamp)

    validate_latitude = field_validator("latitude")(validate_latitude)

    @field_validator("location_type", mode="before")
    @classmethod
    def validate_location_type_response(cls, value: int) -> LocationType:
        """Validate a location type for a request payload.

        Args:
            value: The integer-based interpretation of a location type.

        Returns:
            A LocationType value.

        Raises:
            ValueError: Raised upon an unknown location type.
        """
        try:
            return LocationType(value)
        except ValueError as err:
            raise ValueError(f"{value} is an unknown location type") from err

    validate_longitude = field_validator("longitude")(validate_longitude)


class GetSensorRequest(PurpleAirBaseModel):
    """Define a request to GET /v1/sensors/:sensor_index."""

    fields: str | None = None
    read_key: str | None = None

    validate_fields = field_validator("fields", mode="before")(validate_fields_request)


class GetSensorResponse(PurpleAirBaseModel):
    """Define a response to GET /v1/sensors/:sensor_index."""

    api_version: str
    sensor: SensorModel
    data_timestamp_utc: datetime = Field(alias="data_time_stamp")
    timestamp_utc: datetime = Field(alias="time_stamp")

    validate_data_timestamp_utc = field_validator("data_timestamp_utc", mode="before")(validate_timestamp)

    validate_timestamp_utc = field_validator("timestamp_utc", mode="before")(validate_timestamp)


class GetSensorHistoryRequest(PurpleAirBaseModel):
    """Define a request to GET /v1/sensors/:sensor_index/history[/csv]."""

    fields: str

    read_key: str | None = None
    start_timestamp: int | None = None
    end_timestamp: int | None = None
    average: int | None = None

    validate_fields = field_validator("fields", mode="before")(validate_fields_request)

    @field_validator("start_timestamp", "end_timestamp", mode="before")
    @classmethod
    def validate_timestamps(cls, value: datetime) -> int:
        """Validate a history window boundary datetime.

        Args:
            value: A datetime object (in UTC).

        Returns:
            The epoch timestamp of the datetime object.
        """
        return round(utc_to_timestamp(value))


class GetSensorHistoryResponse(PurpleAirBaseModel):
    """Define a response to GET /v1/sensors/:sensor_index/history."""

    api_version: str
    sensor_index: int
    average: int
    fields: list[str]
    data: list[dict[str, Any]]

    private: bool | None = None
    timestamp_utc: datetime = Field(alias="time_stamp")
    start_timestamp_utc: datetime = Field(alias="start_timestamp")
    end_timestamp_utc: datetime = Field(alias="end_timestamp")

    @model_validator(mode="before")
    @classmethod
    def build_data(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Zip each history row into a ``{field: value}`` mapping.

        Args:
            values: The response payload.

        Returns:
            The response payload with ``data`` reshaped into per-row mappings.
        """
        values["data"] = [
            dict(zip(values["fields"], row))  # noqa: B905
            for row in values["data"]
        ]
        return values

    validate_timestamp_utc = field_validator("timestamp_utc", mode="before")(validate_timestamp)

    validate_start_timestamp_utc = field_validator("start_timestamp_utc", mode="before")(validate_timestamp)

    validate_end_timestamp_utc = field_validator("end_timestamp_utc", mode="before")(validate_timestamp)


class GetSensorsRequest(PurpleAirBaseModel):
    """Define a request to GET /v1/sensors."""

    fields: str

    location_type: int | None = None
    max_age: int | None = None
    modified_since: int | None = Field(alias="modified_since_utc", default=None)
    nwlat: float | None = None
    nwlng: float | None = None
    read_keys: str | None = None
    selat: float | None = None
    selng: float | None = None
    show_only: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_bounding_box_missing_or_complete(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validate the fields.

        Args:
            values: The fields passed into the model.

        Returns:
            The fields.

        Raises:
            ValueError: Only some of the bounding box coordinates have been provided.
        """
        num_of_keys = len([key for key in ("nwlng", "nwlat", "selng", "selat") if values.get(key) is not None])

        if num_of_keys not in (0, 4):
            raise ValueError("must pass none or all of the bounding box coordinates")

        return values

    validate_fields = field_validator("fields", mode="before")(validate_fields_request)

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

    @field_validator("modified_since", mode="before")
    @classmethod
    def validate_modified_since(cls, value: datetime) -> int:
        """Validate the "modified since" datetime.

        Args:
            value: A "modified since" datetime object (in UTC).

        Returns:
            The timestamp of the datetime object.
        """
        return round(utc_to_timestamp(value))

    validate_nwlat = field_validator("nwlat")(validate_latitude)

    validate_nwlng = field_validator("nwlng")(validate_longitude)

    @field_validator("read_keys", mode="before")
    @classmethod
    def validate_read_keys(cls, value: list[str]) -> str:
        """Validate the read keys.

        Args:
            value: A list of read key strings.

        Returns:
            A comma-separate string of read keys.
        """
        return ",".join([str(v) for v in value])

    validate_selat = field_validator("selat")(validate_latitude)
    validate_selng = field_validator("selng")(validate_longitude)

    @field_validator("show_only", mode="before")
    @classmethod
    def validate_show_only(cls, value: list[int]) -> str:
        """Validate the sensor ID list by which to filter the results.

        Args:
            value: A list of sensor IDs.

        Returns:
            A comma-separate string of sensor IDs.
        """
        return ",".join([str(i) for i in value])


class GetSensorsResponse(PurpleAirBaseModel):
    """Define a response to GET /v1/sensors."""

    fields: list[str]
    data: dict[int, SensorModel]

    api_version: str
    firmware_default_version: str
    max_age: int
    data_timestamp_utc: datetime = Field(alias="data_time_stamp")
    timestamp_utc: datetime = Field(alias="time_stamp")

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validate the fields string.

        Args:
            values: The response payload.

        Returns:
            The response payload with validated fields.

        Raises:
            ValueError: An invalid API key type was received.
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

    validate_data_timestamp_utc = field_validator("data_timestamp_utc", mode="before")(validate_timestamp)

    validate_timestamp_utc = field_validator("timestamp_utc", mode="before")(validate_timestamp)
