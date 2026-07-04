# aiopurpleair

Async Python client library for the PurpleAir air-quality API, with the organization endpoint and typed error codes.

## Build and Distribution

- **Source Code**: [GitHub][github-link] - Source code, issues, discussions, and CI/CD pipelines.
- **Versioned Releases**: [GitHub Releases][releases-link] - Version tagged source code and build artifacts.
- **PyPI Packages**: [PyPI][pypi-link] - Python wheel + sdist published to PyPI.org as `ptr727-aiopurpleair`.

### Build Status

[![Releases Build][releasebuildstatus-shield]][actions-link]\
[![Last Commit][lastcommit-shield]][commits-link]

### Releases

[![GitHub Release][releaseversion-shield]][releases-link]\
[![GitHub Pre-Release][prereleaseversion-shield]][releases-link]\
[![PyPI Release][pypireleaseversion-shield]][pypi-link]

### Release Notes

Release highlights - see [Release History](./HISTORY.md) for details.

**Version 1.0.0**:

- First release of the independent, standalone library, published to PyPI as `ptr727-aiopurpleair`. It is a maintained continuation (no fork lineage) of the work from the abandoned upstream PR [bachya/aiopurpleair#719][bachya-pr-link]. Requires Python 3.13 or newer; tested on 3.13 and 3.14.
- **Breaking change** - the API-key check moved from the top-level `api.async_check_api_key()` to the grouped `api.keys.async_check_api_key()`, so keys sit alongside `api.sensors`, `api.organizations`, and `api.groups` for one consistent endpoint-group surface. Update callers to the new path.
- **New endpoints** - beyond the keys and sensors endpoints of the canonical library, this adds the organization endpoint (`GET /v1/organization`: remaining API points, consumption rate, organization identity), sensor history as JSON or CSV (`GET /v1/sensors/:sensor_index/history[/csv]`), and the complete Groups API (`/v1/groups*`: group and member management, member data, member history CSV) - full coverage of the documented API.
- **Consistent typed exceptions** - every documented PurpleAir error code maps to a specific `PurpleAirError` subclass (`InvalidApiKeyError`, `PaymentRequiredError`, `GroupNotFoundError`, `RateLimitExceededError`, ...), grouped under `RequestError` / `InvalidApiKeyError` / `InvalidRequestError` so callers can catch broadly or narrowly instead of pattern-matching on `str(err)`.
- **Reconstructed OpenAPI spec** - PurpleAir publishes no machine-readable schema, so the repo regenerates one from the upstream apiDoc data with a script and validates the client's endpoint, field, and error-code coverage against it (and, opt-in, against the live API).
- **Typed, timezone-aware models** - responses are typed Pydantic models (with a `py.typed` marker); timestamps parse to explicit-UTC `datetime` objects rather than naive ones.
- **Modern packaging** - hatchling + uv on a src-layout, automatic NBGV versioning (no manual tags), OIDC Trusted-Publishing releases, a 100% coverage gate, and syrupy snapshot tests.

See [GitHub Releases][releases-link] for per-release changes.\
See [Release History](./HISTORY.md) for historic changes.

## Getting Started

Get started with aiopurpleair in two easy steps:

1. **Add aiopurpleair to your project**:

    ```shell
    # Add the package to your project (import name stays `aiopurpleair`)
    pip install ptr727-aiopurpleair
    ```

2. **Write some code**:

    ```python
    import asyncio

    from aiopurpleair import API


    async def main() -> None:
        """Check an API key and fetch sensors."""
        api = API("<API_KEY>")
        keys = await api.keys.async_check_api_key()
        sensors = await api.sensors.async_get_sensors(["name", "pm2.5"])
        organization = await api.organizations.async_get_organization()


    asyncio.run(main())
    ```

See [Usage](#usage) for detailed usage instructions.

## Table of Contents

- [aiopurpleair](#aiopurpleair)
  - [Build and Distribution](#build-and-distribution)
    - [Build Status](#build-status)
    - [Releases](#releases)
    - [Release Notes](#release-notes)
  - [Getting Started](#getting-started)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Usage](#usage)
    - [Checking an API Key](#checking-an-api-key)
    - [Getting Sensors](#getting-sensors)
    - [Getting Sensor History](#getting-sensor-history)
    - [Getting the Organization](#getting-the-organization)
    - [Working with Groups](#working-with-groups)
    - [Error Handling](#error-handling)
    - [Connection Pooling](#connection-pooling)
  - [Installation](#installation)
  - [Questions or Issues](#questions-or-issues)
  - [Build Artifacts](#build-artifacts)
  - [API Reference](#api-reference)
  - [Contributing](#contributing)
  - [Origin](#origin)
  - [License](#license)

## Features

Full async coverage of the PurpleAir API, each method mirroring a documented endpoint:

- **Keys** - validate an API key and read its type (`GET /v1/keys`), via `api.keys.async_check_api_key()`.
- **Sensors** - one sensor, many sensors by field selection, or a distance-sorted nearby search, plus a map-URL helper (`GET /v1/sensors`, `GET /v1/sensors/{sensor_index}`), via `api.sensors`.
- **Sensor history** - historical time series for a sensor as parsed JSON or raw CSV (`GET /v1/sensors/{sensor_index}/history[/csv]`), via `api.sensors`.
- **Organization** - the account's remaining API points and consumption rate (`GET /v1/organization`), via `api.organizations`.
- **Groups** - create, list, inspect, and delete groups; add and remove member sensors; read member sensor data and member history CSV (`/v1/groups*`), via `api.groups`.
- **Typed errors** - each documented API error code maps to a specific `PurpleAirError` subclass, so callers catch a precise condition instead of parsing `str(err)`.
- Timezone-aware UTC datetimes and typed Pydantic response models, shipped with a `py.typed` marker.
- Modern packaging: hatchling, uv, automatic versioning, OIDC-published releases, and 100% test coverage.

## Usage

In-depth documentation on the API is available from [PurpleAir][purpleairapi-link]. Unless otherwise noted, aiopurpleair follows the API as closely as possible.

### Checking an API Key

```python
import asyncio

from aiopurpleair import API


async def main() -> None:
    """Check whether an API key is valid and what properties it has."""
    api = API("<API_KEY>")
    response = await api.keys.async_check_api_key()
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

Private sensors require their per-sensor read key: pass `read_key=` to `async_get_sensor`, or `read_keys=[...]` to `async_get_sensors`. Use `async_get_nearby_sensors(fields, latitude, longitude, distance)` for a distance-sorted search, and `get_map_url(sensor_index)` for a map link.

### Getting Sensor History

Fetch a historical time series for a sensor, as parsed JSON or as raw CSV. The averaging period is in minutes (e.g. `0` for real-time, `60` for hourly, `1440` for daily):

```python
import asyncio
from datetime import UTC, datetime, timedelta

from aiopurpleair import API


async def main() -> None:
    """Fetch a day of hourly history for a sensor."""
    api = API("<API_KEY>")
    end = datetime.now(UTC)
    start = end - timedelta(days=1)

    history = await api.sensors.async_get_sensor_history(
        131075,
        ["humidity", "temperature", "pm2.5_atm"],
        start_timestamp_utc=start,
        end_timestamp_utc=end,
        average=60,
    )
    # >>> history.data == [{"time_stamp": 1667336400, "humidity": 37, ...}, ...]

    csv = await api.sensors.async_get_sensor_history_csv(
        131075, ["pm2.5_atm"], start_timestamp_utc=start, end_timestamp_utc=end, average=60
    )
    # >>> csv.startswith("time_stamp,sensor_index,pm2.5_atm")


asyncio.run(main())
```

The history endpoint is a gated feature; if it is not enabled for your API key the call raises `ApiDisabledError`.

### Getting the Organization

The organization endpoint reports the account's remaining API points and consumption rate, useful for surfacing a low-points warning before queries start failing:

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

### Working with Groups

Groups organize sensors for data access. Create and delete operations require a **WRITE** key; reads (list, detail, member data) use a **READ** key:

```python
import asyncio

from aiopurpleair import API


async def main() -> None:
    """Create a group, add a member, read it back, then clean up."""
    write_api = API("<WRITE_API_KEY>")
    read_api = API("<READ_API_KEY>")

    created = await write_api.groups.async_create_group("My Sensors")
    group_id = created.group_id

    await write_api.groups.async_create_member(group_id, sensor_index=131075)

    groups = await read_api.groups.async_get_groups()
    detail = await read_api.groups.async_get_group(group_id)
    # >>> detail.members == [GroupMember(id=..., sensor_index=131075, ...)]

    members = await read_api.groups.async_get_members(group_id, ["name", "pm2.5"])
    # >>> members.data == {131075: SensorModel(...)}

    await write_api.groups.async_delete_group(group_id)


asyncio.run(main())
```

Adding a private sensor also requires its registration `owner_email`. Per-member history is available as CSV via `async_get_member_history_csv(group_id, member_id, fields, ...)`.

### Error Handling

Each documented PurpleAir API error code maps to a specific exception subclass, so callers can catch a precise condition instead of pattern-matching on `str(err)`. Every subclass derives from `PurpleAirError`:

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

All error codes and semantics are verified against the official [PurpleAir API documentation][purpleairapi-link].

### Connection Pooling

By default a new connection is created per coroutine. Pass an existing [`aiohttp`][aiohttp-link] `ClientSession` for connection pooling:

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

## Installation

**Project integration**:

```shell
# Add the package to your project
pip install ptr727-aiopurpleair
```

```python
# Import the library (the import name stays `aiopurpleair`)
import aiopurpleair
```

The distribution name is `ptr727-aiopurpleair` (distinct from the canonical `aiopurpleair` on PyPI); the import path is unchanged. aiopurpleair supports Python 3.13 and 3.14, and depends on `aiohttp`, `pydantic`, `yarl`, and `certifi`.

## Questions or Issues

**General questions**:

- Use the [Discussions][discussions-link] forum for general questions.

**Bug reports**:

- Ask in the [Discussions][discussions-link] forum if you are not sure if it is a bug.
- Check the existing [Issues][issues-link] tracker for known problems.
- If the issue is unique and a bug, file it in [Issues][issues-link], and include all pertinent steps to reproduce the issue.

## Build Artifacts

**Build process and artifacts**:

- **Package**: a Python wheel + sdist (`ptr727-aiopurpleair`), built with the [hatchling][hatchling-link] backend on a src-layout ([`src/aiopurpleair/`](./src/aiopurpleair/)) and managed with [uv][uv-link].
- **Versioning**: automatic via [Nerdbank.GitVersioning][nbgv-link] from [`version.json`](./version.json) (`1.0` base) plus git height; `main` builds a clean stable `X.Y.Z`, `develop` a `X.Y.Z.dev0` prerelease. There is no manual tagging.
- **Publishing**: releases publish to PyPI over OIDC [Trusted Publishing][trustedpublishing-link] (no stored API token). A shipped-path push to `main` (stable) or `develop` (prerelease), or a manual dispatch, cuts a [GitHub Release][releases-link] and uploads the wheel + sdist to PyPI. See [`WORKFLOW.md`](./WORKFLOW.md) for the complete CI/CD contract.

## API Reference

PurpleAir does not publish an OpenAPI/Swagger spec. This repo reconstructs one at [`docs/purpleair-openapi.yaml`](./docs/purpleair-openapi.yaml) from PurpleAir's [apiDoc][apidoc-link]-generated docs (which serve machine-readable `api_data.js`), using [`scripts/generate_openapi.py`](./scripts/generate_openapi.py). The library's endpoint, field, and error-code coverage is validated against this spec.

Regenerate it after an upstream API change:

```shell
# Live-fetch https://api.purpleair.com/api_data.js, rebuild and validate the spec
uv run --with pyyaml --with openapi-spec-validator python scripts/generate_openapi.py
```

The generator takes the API version from the docs' changelog (the apiDoc build-metadata version lags behind), validates the result, and writes `docs/purpleair-openapi.yaml`. A non-empty diff means the upstream API changed. See [`AGENTS.md`](./AGENTS.md) for how the code is validated against the spec.

**Coverage**: all 11 paths of the spec (currently API `1.2.0`) are implemented - keys, sensors (list, single, and history JSON/CSV), organization, and the full Groups API (group and member management, member data, and member history). The single-sensor `stats`/`stats_a`/`stats_b` blocks are returned as part of the sensor payload but are not requestable `fields` values, so they are parsed on the response but excluded from the requestable field catalog.

## Contributing

- **Branching workflow**:
  - The repo uses a two-branch model with ruleset-enforced merge methods.
  - Feature branch -> `develop` via **squash merge** (develop is kept linear).
  - `develop` -> `main` via **merge commit** (preserves develop's commit list on main as the second parent of each release commit).
  - Dependabot targets `main` and `develop` in parallel via separate PRs and auto-merges every tier once the required check passes.
  - See [`WORKFLOW.md`](./WORKFLOW.md) and [`AGENTS.md`](./AGENTS.md) for complete details.
- **Code style**:
  - See [`CODESTYLE.md`](./CODESTYLE.md) and [`.editorconfig`](./.editorconfig) for Python code style rules. Everything runs through `uv run` (`ruff`, `mypy`, `pyright`, `pytest` with 100% coverage and syrupy snapshots).
- **Repository setup**:
  - See [`repo-config/README.md`](./repo-config/README.md) for repo configuration details.

## Origin

aiopurpleair is an independent, MIT-licensed continuation of the [bachya/aiopurpleair][upstream-link] PurpleAir API client. Its distinguishing capabilities originated in two upstream contributions that were abandoned:

- A pull request against bachya/aiopurpleair adding the organization endpoint and typed error codes ([bachya/aiopurpleair#719][bachya-pr-link]), since abandoned.
- A PurpleAir integration proposed for Home Assistant core as [home-assistant/core#140901][hacorepr-link], now maintained separately as the [`homeassistant-purpleair`][hapurpleair-link] HACS custom integration, this library's primary consumer.

The import package name is `aiopurpleair`; the distribution name `ptr727-aiopurpleair` keeps it distinct from the canonical `aiopurpleair` on PyPI. The original MIT copyright is retained alongside the current maintainer's in [LICENSE](./LICENSE) and [NOTICE](./NOTICE).

## License

Licensed under the [MIT License][license-link]\
![GitHub License][license-shield]

- Original `aiopurpleair` author: Aaron Bach ([@bachya][bachya-link]).
- Current maintainer: Pieter Viljoen ([@ptr727][ptr727-link]).

<!-- Shields links -->

[actions-link]: https://github.com/ptr727/aiopurpleair/actions
[commits-link]: https://github.com/ptr727/aiopurpleair/commits/main
[discussions-link]: https://github.com/ptr727/aiopurpleair/discussions
[github-link]: https://github.com/ptr727/aiopurpleair
[issues-link]: https://github.com/ptr727/aiopurpleair/issues
[lastcommit-shield]: https://img.shields.io/github/last-commit/ptr727/aiopurpleair?logo=github&label=Last%20Commit
[license-link]: ./LICENSE
[license-shield]: https://img.shields.io/github/license/ptr727/aiopurpleair?label=License
[prereleaseversion-shield]: https://img.shields.io/github/v/release/ptr727/aiopurpleair?include_prereleases&filter=*-g*&label=GitHub%20Pre-Release&logo=github
[pypi-link]: https://pypi.org/project/ptr727-aiopurpleair/
[pypireleaseversion-shield]: https://img.shields.io/pypi/v/ptr727-aiopurpleair?logo=pypi&label=PyPI%20Release
[releasebuildstatus-shield]: https://img.shields.io/github/actions/workflow/status/ptr727/aiopurpleair/publish-release.yml?logo=github&label=Releases%20Build
[releases-link]: https://github.com/ptr727/aiopurpleair/releases
[releaseversion-shield]: https://img.shields.io/github/v/release/ptr727/aiopurpleair?logo=github&label=GitHub%20Release

<!-- Other links -->

[aiohttp-link]: https://github.com/aio-libs/aiohttp
[apidoc-link]: https://apidocjs.com/
[bachya-link]: https://github.com/bachya
[bachya-pr-link]: https://github.com/bachya/aiopurpleair/pull/719
[hacorepr-link]: https://github.com/home-assistant/core/pull/140901
[hapurpleair-link]: https://github.com/ptr727/homeassistant-purpleair
[hatchling-link]: https://hatch.pypa.io/latest/
[nbgv-link]: https://github.com/dotnet/Nerdbank.GitVersioning
[ptr727-link]: https://github.com/ptr727
[purpleairapi-link]: https://api.purpleair.com/#api-welcome
[trustedpublishing-link]: https://docs.pypi.org/trusted-publishers/
[upstream-link]: https://github.com/bachya/aiopurpleair
[uv-link]: https://github.com/astral-sh/uv
