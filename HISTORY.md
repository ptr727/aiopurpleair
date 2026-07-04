# aiopurpleair - Release History

Curated highlights of what's shipped. The canonical per-version release ledger (with auto-generated PR/commit detail and downloadable artifacts) is the [GitHub Releases][releases-link] page, and every version is on [PyPI][pypi-link]; this file just summarizes the headline features that landed in each milestone. It is end-user release notes - what changed and what to expect after upgrading - not a design log.

## Release History

- **Version 1.0.0**:
  - First release of the independent, standalone library, published to PyPI as `ptr727-aiopurpleair`. A maintained continuation (no fork lineage) of the work from the abandoned upstream PR [bachya/aiopurpleair#719](https://github.com/bachya/aiopurpleair/pull/719). Requires Python 3.13 or newer; tested on 3.13 and 3.14.
  - **Breaking change** - the API-key check moved from the top-level `api.async_check_api_key()` to the grouped `api.keys.async_check_api_key()`, matching `api.sensors` / `api.organizations` / `api.groups`. Update callers to the new path.
  - **New endpoints** - beyond the canonical library's keys and sensors endpoints, this adds the organization endpoint (`GET /v1/organization`: remaining API points, consumption rate, organization identity), sensor history as JSON or CSV (`GET /v1/sensors/:sensor_index/history[/csv]`), and the complete Groups API (`/v1/groups*`: group and member management, member data, member history CSV). All 11 documented paths are covered.
  - **Consistent typed exceptions** - every documented PurpleAir error code maps to a specific exception subclass (`InvalidDataReadKeyError`, `ApiKeyTypeMismatchError`, `PaymentRequiredError`, `GroupNotFoundError`, `RateLimitExceededError`, ...) instead of pattern-matching on `str(err)`. All derive from a single `PurpleAirError` base, grouped under `RequestError` / `InvalidApiKeyError` / `InvalidRequestError` so a caller can catch broadly or narrowly; an unrecognized code still raises `RequestError`.
  - **Reconstructed OpenAPI spec** - PurpleAir publishes no machine-readable schema, so the repo regenerates one from the upstream apiDoc data with a script ([`scripts/generate_openapi.py`](scripts/generate_openapi.py)) and validates the client's endpoint, field, and error-code coverage against it, and opt-in against the live API.
  - **Typed, timezone-aware models** - responses are typed Pydantic models (with a `py.typed` marker); timestamps parse to explicit-UTC `datetime` objects rather than naive ones.
  - **Modern packaging** - published to PyPI as `ptr727-aiopurpleair` (the import package stays `aiopurpleair`), built with hatchling and managed with uv on a src-layout. Automated NBGV versioning (no manual tags), a 100% test-coverage gate, and syrupy snapshot tests over the response models back every release.

[pypi-link]: https://pypi.org/project/ptr727-aiopurpleair/
[releases-link]: https://github.com/ptr727/aiopurpleair/releases
