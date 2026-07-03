# aiopurpleair

[![CI][ci-badge]][ci]
[![PyPI][pypi-badge]][pypi]
[![Python versions][pyversions-badge]][pypi]
[![License][license-badge]][license]

`aiopurpleair` is a Python, asyncio-based client library for the
[PurpleAir][purpleair] air-quality API. It covers the sensors and keys
endpoints, adds a `GET /v1/organization` endpoint for tracking remaining API
points, and maps the API's documented error codes to a typed exception
hierarchy.

> Originally derived from [bachya/aiopurpleair][upstream] by Aaron Bach, now
> independently maintained. Published to PyPI as **`ptr727-aiopurpleair`**; the
> import name stays `aiopurpleair`. See [About and History](#about-and-history).

- [Installation](#installation)
- [Python Versions](#python-versions)
- [Usage](#usage)
  - [Checking an API Key](#checking-an-api-key)
  - [Getting Sensors](#getting-sensors)
  - [Getting the Organization](#getting-the-organization)
  - [Error Handling](#error-handling)
  - [Connection Pooling](#connection-pooling)
- [About and History](#about-and-history)
- [Development](#development)
- [License and Attribution](#license-and-attribution)

## Installation

```bash
pip install ptr727-aiopurpleair
```

The distribution name is `ptr727-aiopurpleair` (distinct from the canonical
`aiopurpleair` on PyPI); the import path is unchanged:

```python
import aiopurpleair
```

## Python Versions

`aiopurpleair` supports Python 3.13 and 3.14.

## Usage

In-depth documentation on the API is available from [PurpleAir][purpleair-api].
Unless otherwise noted, `aiopurpleair` follows the API as closely as possible.

### Checking an API Key

```python
import asyncio

from aiopurpleair import API


async def main() -> None:
    """Check whether an API key is valid and what properties it has."""
    api = API("<API_KEY>")
    response = await api.async_check_api_key()
    # >>> response.api_key_type == ApiKeyType.READ
    # >>> response.api_version == "V1.0.11-0.0.41"


asyncio.run(main())
```

### Getting Sensors

```python
import asyncio

from aiopurpleair import API


async def main() -> None:
    """Fetch sensor data for the requested fields."""
    api = API("<API_KEY>")
    response = await api.sensors.async_get_sensors(["name", "pm2.5"])
    # >>> response.data == {131075: SensorModel(...), 131079: SensorModel(...)}


asyncio.run(main())
```

Private sensors require their per-sensor read key: pass `read_key=` to
`async_get_sensor`, or `read_keys=[...]` to `async_get_sensors`. Use
`async_get_nearby_sensors(fields, latitude, longitude, distance)` for a
distance-sorted search, and `get_map_url(sensor_index)` for a map link.

### Getting the Organization

The organization endpoint reports the account's remaining API points and
consumption rate — useful for surfacing a low-points warning before queries
start failing:

```python
import asyncio

from aiopurpleair import API


async def main() -> None:
    """Fetch the organization associated with the API key."""
    api = API("<API_KEY>")
    response = await api.organizations.async_get_organization()
    # >>> response.remaining_points == 500000
    # >>> response.consumption_rate == 1234.5
    # >>> response.organization_id == "..."
    # >>> response.organization_name == "..."


asyncio.run(main())
```

### Error Handling

Each documented PurpleAir API error code maps to a specific exception subclass,
so callers can catch a precise condition instead of pattern-matching on
`str(err)`. Every subclass derives from `PurpleAirError`:

```python
import asyncio

from aiopurpleair import API
from aiopurpleair.errors import InvalidApiKeyError, RateLimitExceededError


async def main() -> None:
    """Handle specific PurpleAir error conditions."""
    api = API("<API_KEY>")
    try:
        await api.sensors.async_get_sensors(["name"])
    except InvalidApiKeyError:
        ...  # the API key is missing or invalid
    except RateLimitExceededError:
        ...  # back off and retry later


asyncio.run(main())
```

All error codes and semantics are verified against the official
[PurpleAir API documentation][purpleair-api].

### Connection Pooling

By default a new connection is created per coroutine. Pass an existing
[`aiohttp`][aiohttp] `ClientSession` for connection pooling:

```python
import asyncio

from aiohttp import ClientSession

from aiopurpleair import API


async def main() -> None:
    """Reuse a session across calls."""
    async with ClientSession() as session:
        api = API("<API_KEY>", session=session)
        ...


asyncio.run(main())
```

## About and History

This library began as a fork of [bachya/aiopurpleair][upstream] to add two
capabilities the canonical release lacked: a `GET /v1/organization` endpoint
and a typed exception hierarchy covering the API's documented error codes.
Those additions were proposed upstream, but the upstream maintainer became
unresponsive and the contribution was abandoned.

Rather than leave the work stranded, it is now maintained here as an
independent library published as `ptr727-aiopurpleair`. A companion effort — a
PurpleAir integration proposed for Home Assistant core as
[home-assistant/core#140901][ha-core-pr] — was likewise abandoned and is
maintained separately as the [`homeassistant-purpleair`][ha-purpleair] HACS
custom integration, which is this library's primary consumer.

The original MIT copyright is retained in [LICENSE](LICENSE) and [NOTICE](NOTICE).

## Development

This project uses [uv][uv] for environment and dependency management:

```bash
uv sync --all-groups          # create the venv and install dev dependencies
uv run ruff check             # lint
uv run ruff format --check    # format check
uv run mypy src tests         # type-check (strict)
uv run pyright                # type-check
uv run pytest                 # tests, with 100% coverage enforced
```

Snapshot tests use [syrupy][syrupy]; regenerate snapshots with
`uv run pytest --snapshot-update` when response models change intentionally.

Versioning is automatic (Nerdbank.GitVersioning from `version.json` plus git
height); there is no manual tagging. Releases publish to PyPI via OIDC Trusted
Publishing on merge to `main` (stable) or `develop` (prerelease).

## License and Attribution

MIT — see [LICENSE](LICENSE) and [NOTICE](NOTICE).

- Original `aiopurpleair` author: Aaron Bach ([@bachya][bachya]).
- Current maintainer: Pieter Viljoen ([@ptr727][ptr727]).

[aiohttp]: https://github.com/aio-libs/aiohttp
[bachya]: https://github.com/bachya
[ci-badge]: https://img.shields.io/github/actions/workflow/status/ptr727/aiopurpleair/test-pull-request.yml?branch=main
[ci]: https://github.com/ptr727/aiopurpleair/actions
[ha-core-pr]: https://github.com/home-assistant/core/pull/140901
[ha-purpleair]: https://github.com/ptr727/homeassistant-purpleair
[license]: https://github.com/ptr727/aiopurpleair/blob/main/LICENSE
[license-badge]: https://img.shields.io/pypi/l/ptr727-aiopurpleair.svg
[ptr727]: https://github.com/ptr727
[purpleair]: https://www2.purpleair.com/
[purpleair-api]: https://api.purpleair.com/#api-welcome
[pypi]: https://pypi.org/project/ptr727-aiopurpleair/
[pypi-badge]: https://img.shields.io/pypi/v/ptr727-aiopurpleair.svg
[pyversions-badge]: https://img.shields.io/pypi/pyversions/ptr727-aiopurpleair.svg
[syrupy]: https://github.com/syrupy-project/syrupy
[upstream]: https://github.com/bachya/aiopurpleair
[uv]: https://github.com/astral-sh/uv
