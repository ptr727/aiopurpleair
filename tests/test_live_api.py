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

import asyncio
import os
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aiopurpleair import API
from aiopurpleair.const import SENSOR_FIELDS
from aiopurpleair.errors import ApiDisabledError, GroupNotFoundError
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
# A WRITE key (same account) enables the self-cleaning groups round-trip.
_WRITE_KEY = _ENV.get("PURPLEAIR_API_KEY_WRITE", "")
# The owning account's registration email enables the member round-trip.
_OWNER_EMAIL = _ENV.get("PURPLEAIR_OWNER_EMAIL", "")
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
    response = await API(api_key).keys.async_check_api_key()
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


async def test_live_sensor_history() -> None:
    """The sensor history endpoints return parseable JSON and raw CSV.

    Requesting a real 24-hour window for an owned sensor proves the history
    request encoding and JSON/CSV response shapes against the live API. The
    history endpoint is a gated feature; if it is disabled for the key the
    request still round-trips correctly (raising ``ApiDisabledError``), so the
    test skips rather than fails.
    """
    pairs = _sensor_pairs()
    if not pairs:
        pytest.skip("no PURPLEAIR_SENSOR_INDEX_1/2 in .env.test")
    index, read_key = pairs[0]
    end = datetime.now(UTC)
    start = end - timedelta(days=1)
    fields = ["humidity", "temperature", "pm2.5_atm"]

    # History is a gated feature enabled per key; try each configured key and use
    # the first that has it, skipping only if it is disabled for all of them.
    for key in _API_KEYS:
        api = API(key)
        try:
            history = await api.sensors.async_get_sensor_history(
                index, fields, read_key=read_key, start_timestamp_utc=start, end_timestamp_utc=end, average=60
            )
        except ApiDisabledError:
            continue
        assert history.sensor_index == index
        assert history.average == 60
        assert "time_stamp" in history.fields

        csv = await api.sensors.async_get_sensor_history_csv(
            index, fields, read_key=read_key, start_timestamp_utc=start, end_timestamp_utc=end, average=60
        )
        assert csv.splitlines()[0].startswith("time_stamp,sensor_index")
        return
    pytest.skip("the history endpoint is disabled for all configured API keys")


async def _read_when_ready[T](factory: Callable[[], Awaitable[T]]) -> T | None:
    """Await a group read, polling through the transient GroupNotFoundError.

    Group and member reads are eventually consistent after a write, so a read
    can 404 for a few seconds. Returns the result, or ``None`` if it never
    settles.
    """
    for _ in range(12):
        try:
            return await factory()
        except GroupNotFoundError:
            await asyncio.sleep(5)
    return None


async def _add_member_when_ready(write_api: API, group_id: int, sensor_index: int) -> int | None:
    """Add an owned sensor once the new group has propagated.

    Group creation is eventually consistent - the member endpoint can return
    ``GroupNotFoundError`` for a few seconds after the group is created - so this
    retries briefly and returns the member id, or ``None`` if it never settles.
    """
    for _ in range(12):
        try:
            response = await write_api.groups.async_create_member(
                group_id, sensor_index=sensor_index, owner_email=_OWNER_EMAIL
            )
        except GroupNotFoundError:
            await asyncio.sleep(5)
            continue
        return response.member_id
    return None


@pytest.mark.skipif(
    not (_LIVE and _WRITE_KEY and _PRIMARY_KEY),
    reason="need PURPLEAIR_API_KEY_WRITE and a same-account PURPLEAIR_API_KEY in .env.test",
)
async def test_live_groups_roundtrip() -> None:
    """A group and its members round-trip through the real API (self-cleaning).

    Reads and writes use different key types even within groups: create/delete
    take the WRITE key, list/detail/data take the same account's READ key. With
    an owner email + owned sensor configured, a member is added and read back;
    otherwise just the group create/list/delete is exercised. Everything created
    is always deleted, even on assertion failure.
    """
    write_api = API(_WRITE_KEY)
    read_api = API(_PRIMARY_KEY)
    created = await write_api.groups.async_create_group("aiopurpleair-live-test")
    group_id = created.group_id
    try:
        assert group_id
        listing = await read_api.groups.async_get_groups()
        assert isinstance(listing.groups, list)

        pairs = _sensor_pairs()
        if not (_OWNER_EMAIL and pairs):
            return
        sensor_index = pairs[0][0]
        member_id = await _add_member_when_ready(write_api, group_id, sensor_index)
        if member_id is None:
            pytest.skip("the new group did not propagate to the member endpoint in time")
        try:
            # The member reads are eventually consistent too, so poll through the
            # transient GroupNotFoundError. If they never settle, skip rather than
            # pass vacuously (the endpoints are still exercised by the mocked suite).
            member = await _read_when_ready(
                lambda: read_api.groups.async_get_member(group_id, member_id, fields=["name"])
            )
            members = await _read_when_ready(lambda: read_api.groups.async_get_members(group_id, ["name"]))
            if member is None or members is None:
                pytest.skip("member reads did not become consistent in time")
            assert member.member_id == member_id
            assert member.sensor.sensor_index == sensor_index
            assert members.group_id == group_id
        finally:
            await write_api.groups.async_delete_member(group_id, member_id)
    finally:
        await write_api.groups.async_delete_group(group_id)
