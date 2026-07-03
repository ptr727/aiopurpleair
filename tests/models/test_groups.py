"""Define model-level tests for groups."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from aiopurpleair.models.groups import GetMembersResponse


def test_get_members_unknown_field() -> None:
    """An unknown field name in a members-data response is rejected."""
    payload = {
        "api_version": "V1.2.0-1.1.45",
        "time_stamp": 1667503589,
        "data_time_stamp": 1667503531,
        "group_id": 1234,
        "fields": ["sensor_index", "bogus_field"],
        "data": [[131075, 1.0]],
    }
    with pytest.raises(ValidationError) as err:
        GetMembersResponse.model_validate(payload)
    assert "bogus_field is an unknown field" in str(err.value)
