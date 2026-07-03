# aiopurpleair - Release History

Curated highlights of what's shipped. The canonical per-version release ledger (with auto-generated PR/commit detail and downloadable artifacts) is the [GitHub Releases][releases-link] page, and every version is on [PyPI][pypi-link]; this file just summarizes the headline features that landed in each milestone. It is end-user release notes - what changed and what to expect after upgrading - not a design log.

## Release History

- **Version 1.0.0**:
  - First release of the independent, standalone library, published to PyPI as `ptr727-aiopurpleair`. A maintained continuation (no fork lineage) of the work from the now-closed upstream PR [bachya/aiopurpleair#719](https://github.com/bachya/aiopurpleair/pull/719). Requires Python 3.13 or newer; tested on 3.13 and 3.14.
  - **Full endpoint coverage** - keys, sensors (list, single, and history as JSON or CSV), organization, and the complete Groups API (group and member management, member data, and member history CSV). All 11 paths of the reconstructed OpenAPI spec are covered and validated, opt-in, against the live API.
  - **Organization endpoint** - a new `GET /v1/organization` call (`api.organizations.async_get_organization()`) reports the account's **remaining API points** and **consumption rate**, alongside the organization id, name, and API version. It lets a consumer surface a low-points warning before queries start failing.
  - **Typed exception hierarchy** - each of the PurpleAir API's documented error codes maps to a specific exception subclass, so callers catch a precise condition (`InvalidDataReadKeyError`, `ApiKeyTypeMismatchError`, `ApiDisabledError`, `PaymentRequiredError`, `RateLimitExceededError`, ...) instead of pattern-matching on `str(err)`. All 30 subclasses derive from a single `PurpleAirError` base, grouped under `RequestError` / `InvalidApiKeyError` / `InvalidRequestError` intermediates so a caller can catch broadly or narrowly. An unrecognized code still raises `RequestError`.
  - **Timezone-aware UTC timestamps** - response timestamps are parsed to `datetime` objects with an explicit UTC timezone, never naive datetimes, so downstream consumers (e.g. Home Assistant's timestamp sensors) accept them directly.
  - **Modern packaging** - published to PyPI as `ptr727-aiopurpleair` (the import package stays `aiopurpleair`), built with hatchling and managed with uv on a src-layout. Automated NBGV versioning (no manual tags), a 100% test-coverage gate, and syrupy snapshot tests over the response models back every release.

[pypi-link]: https://pypi.org/project/ptr727-aiopurpleair/
[releases-link]: https://github.com/ptr727/aiopurpleair/releases
