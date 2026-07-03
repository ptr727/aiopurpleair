"""Opt-in live validation against the real PurpleAir API.

These tests hit the live API with real credentials, so they are excluded from
the default suite: they run only when ``AIOPURPLEAIR_LIVE_TESTS=1`` is set and
credentials are available (from ``.env.test`` in the repo root, the path in
``AIOPURPLEAIR_TEST_ENV``, or the environment). See AGENTS.md
"Live API validation".

Run::

    AIOPURPLEAIR_LIVE_TESTS=1 uv run pytest -m live --no-cov -q
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from aiopurpleair import API
from aiopurpleair.const import SENSOR_FIELDS
from aiopurpleair.models.keys import ApiKeyType


def _load_env() -> dict[str, str]:
    """Merge the environment with a dotenv-style credentials file if present."""
    values = dict(os.environ)
    path = Path(os.environ.get("AIOPURPLEAIR_TEST_ENV", ".env.test"))
    if path.is_file():
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                values.setdefault(key.strip(), value.strip().strip("\"'"))
    return values


_LIVE = os.environ.get("AIOPURPLEAIR_LIVE_TESTS") == "1"
_ENV = _load_env() if _LIVE else {}
# All READ keys to exercise: the primary and an optional second account. Both
# are checked because they hit different account states (e.g. a positive vs an
# overdrawn/negative points balance).
_API_KEYS = [key for key in (_ENV.get("PURPLEAIR_API_KEY", ""), _ENV.get("PURPLEAIR_API_KEY_2", "")) if key]
_PRIMARY_KEY = _API_KEYS[0] if _API_KEYS else ""
# Parametrize labels must NOT be the raw keys (they would leak into test IDs and
# CI logs); use positional labels instead.
_KEY_PARAMS = _API_KEYS or [""]
_KEY_IDS = [f"key{slot + 1}" for slot in range(len(_KEY_PARAMS))]

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not (_LIVE and _API_KEYS),
        reason="set AIOPURPLEAIR_LIVE_TESTS=1 and provide .env.test (see AGENTS.md 'Live API validation')",
    ),
]


def _sensor_pairs() -> list[tuple[int, str | None]]:
    """Return the configured ``(sensor_index, read_key)`` pairs."""
    pairs: list[tuple[int, str | None]] = []
    for slot in (1, 2):
        index = _ENV.get(f"PURPLEAIR_SENSOR_INDEX_{slot}")
        if index:
            pairs.append((int(index), _ENV.get(f"PURPLEAIR_SENSOR_READ_KEY_{slot}") or None))
    return pairs


@pytest.mark.parametrize("api_key", _KEY_PARAMS, ids=_KEY_IDS)
async def test_live_check_api_key(api_key: str) -> None:
    """Each configured READ key is valid and reports a usable key type."""
    response = await API(api_key).async_check_api_key()
    assert response.api_key_type in (ApiKeyType.READ, ApiKeyType.WRITE)


@pytest.mark.parametrize("api_key", _KEY_PARAMS, ids=_KEY_IDS)
async def test_live_get_organization(api_key: str) -> None:
    """The organization endpoint parses for each account.

    ``remaining_points`` may be negative (an overdrawn/grandfathered account),
    so only its type is asserted; the identity fields must be populated.
    """
    response = await API(api_key).organizations.async_get_organization()
    assert isinstance(response.remaining_points, int)
    assert isinstance(response.consumption_rate, int)
    assert response.organization_id


async def test_live_sensors_parse_with_full_field_catalog() -> None:
    """Each owned sensor returns real data that parses into the models when
    every modeled field is requested.

    Requesting all of ``SENSOR_FIELDS`` proves the catalog is a valid subset of
    the live API: an unknown field name would raise ``InvalidFieldValueError``,
    so a clean parse validates the library's field coverage against real data.
    """
    pairs = _sensor_pairs()
    if not pairs:
        pytest.skip("no PURPLEAIR_SENSOR_INDEX_1/2 in .env.test")
    api = API(_PRIMARY_KEY)
    fields = sorted(SENSOR_FIELDS)
    for index, read_key in pairs:
        response = await api.sensors.async_get_sensor(index, fields=fields, read_key=read_key)
        assert response.sensor.sensor_index == index
