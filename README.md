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

See [`HISTORY.md`](./HISTORY.md) for the release notes ledger.

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
        keys = await api.async_check_api_key()
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
    - [Getting the Organization](#getting-the-organization)
    - [Error Handling](#error-handling)
    - [Connection Pooling](#connection-pooling)
  - [Installation](#installation)
  - [Questions or Issues](#questions-or-issues)
  - [Build Artifacts](#build-artifacts)
  - [Contributing](#contributing)
  - [Origin](#origin)
  - [License](#license)

## Features

- Async client for the PurpleAir API, covering the sensors and keys endpoints.
- `GET /v1/organization` endpoint exposing remaining API points and consumption rate.
- Typed exception hierarchy mapped from the API's documented error codes.
- Timezone-aware UTC datetimes and typed Pydantic response models with a `py.typed` marker.
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

Private sensors require their per-sensor read key: pass `read_key=` to `async_get_sensor`, or `read_keys=[...]` to `async_get_sensors`. Use `async_get_nearby_sensors(fields, latitude, longitude, distance)` for a distance-sorted search, and `get_map_url(sensor_index)` for a map link.

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
- **Versioning**: automatic via [Nerdbank.GitVersioning][nbgv-link] from [`version.json`](./version.json) (`2026.8` base) plus git height; `main` builds a clean stable `X.Y.Z`, `develop` a `X.Y.Z.dev0` prerelease. There is no manual tagging.
- **Publishing**: releases publish to PyPI over OIDC [Trusted Publishing][trustedpublishing-link] (no stored API token). A shipped-path push to `main` (stable) or `develop` (prerelease), or a manual dispatch, cuts a [GitHub Release][releases-link] and uploads the wheel + sdist to PyPI. See [`WORKFLOW.md`](./WORKFLOW.md) for the complete CI/CD contract.

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

aiopurpleair is an independent, MIT-licensed continuation of the [bachya/aiopurpleair][upstream-link] PurpleAir API client. Its distinguishing capabilities originated in two upstream contributions that were abandoned after the upstream maintainers became unresponsive:

- A pull request against [bachya/aiopurpleair][upstream-link] adding the organization endpoint and typed error codes, which was not merged.
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
[bachya-link]: https://github.com/bachya
[hacorepr-link]: https://github.com/home-assistant/core/pull/140901
[hapurpleair-link]: https://github.com/ptr727/homeassistant-purpleair
[hatchling-link]: https://hatch.pypa.io/latest/
[nbgv-link]: https://github.com/dotnet/Nerdbank.GitVersioning
[ptr727-link]: https://github.com/ptr727
[purpleairapi-link]: https://api.purpleair.com/#api-welcome
[trustedpublishing-link]: https://docs.pypi.org/trusted-publishers/
[upstream-link]: https://github.com/bachya/aiopurpleair
[uv-link]: https://github.com/astral-sh/uv
