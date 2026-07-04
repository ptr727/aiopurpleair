# PurpleAir Library

Python client library for [PurpleAir][purpleair-link] air-quality sensors API.

## Release History

- **Version 1.0.0**:
  - **Initial release** of the independent, standalone library published as `ptr727-aiopurpleair`, a maintained continuation (no fork lineage) of the work from the abandoned upstream PR [bachya/aiopurpleair#719][bachya-pr-link]. Requires Python 3.13 or newer; tested on 3.13 and 3.14.
  - **New endpoints** beyond the canonical library's keys and sensors, covering all 11 documented API paths:
    - Organization (`GET /v1/organization`) - the account's remaining API points, consumption rate, and organization identity.
    - Sensor history (`GET /v1/sensors/:sensor_index/history[/csv]`) - a historical time series as parsed JSON or raw CSV.
    - Groups (`/v1/groups*`) - group create/list/inspect/delete, member add/remove, member data, and member history CSV.
  - **Consistent typed exceptions** - every documented error code maps to a specific `PurpleAirError` subclass:
    - Precise conditions (`InvalidDataReadKeyError`, `ApiKeyTypeMismatchError`, `PaymentRequiredError`, `GroupNotFoundError`, `RateLimitExceededError`, ...) replace pattern-matching on `str(err)`.
    - Subclasses are grouped under `RequestError` / `InvalidApiKeyError` / `InvalidRequestError` so callers can catch broadly or narrowly; an unrecognized code still raises `RequestError`.
  - **Reconstructed OpenAPI spec** - PurpleAir ships no machine-readable schema, so the repo regenerates one from the upstream apiDoc data with [`scripts/generate_openapi.py`](scripts/generate_openapi.py) and validates endpoint, field, and error-code coverage against it, and opt-in against the live API.
  - **Typed, timezone-aware models** - typed Pydantic response models (with a `py.typed` marker); timestamps parse to explicit-UTC `datetime` objects rather than naive ones.
  - **Modern packaging** - built with hatchling and managed with uv on a src-layout; automated NBGV versioning (no manual tags), OIDC Trusted-Publishing to PyPI, a 100% coverage gate, and syrupy snapshot tests. The import package stays `aiopurpleair`.
  - ⚠️ The API-key check moved from the top-level `api.async_check_api_key()` to the grouped `api.keys.async_check_api_key()`, for consistency with `api.sensors` / `api.organizations` / `api.groups`. Update callers to the new path.

[bachya-pr-link]: https://github.com/bachya/aiopurpleair/pull/719
[purpleair-link]: https://www.purpleair.com/
