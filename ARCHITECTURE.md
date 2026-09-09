# Architecture

How this library is built and what governs its API surface. The operational half (how to run the checks, the runbooks, and the local rule extensions) is in [`OPERATIONS.md`](./OPERATIONS.md).

## Module Layout

The library is src-layout under [`src/aiopurpleair/`](./src/aiopurpleair/).

- [`api.py`](./src/aiopurpleair/api.py) is the client entry point and owns the `aiohttp` session and request plumbing.
- [`endpoints/`](./src/aiopurpleair/endpoints/) holds one caller per endpoint family: `keys`, `sensors`, `groups`, and `organizations`.
- [`models/`](./src/aiopurpleair/models/) holds the Pydantic response models, one module per endpoint family, with the shared validator helpers in [`helpers/`](./src/aiopurpleair/helpers/).
- [`const.py`](./src/aiopurpleair/const.py) holds `SENSOR_FIELDS`, the requestable field catalog.
- [`errors.py`](./src/aiopurpleair/errors.py) holds the typed exception hierarchy and `ERROR_CODE_MAP`.
- [`_version.py`](./src/aiopurpleair/_version.py) carries a placeholder the release build rewrites on the runner. See [`OPERATIONS.md`](./OPERATIONS.md) "Release and Versioning Facts".

## The API Spec Is Generated, and It Is the Source of Truth

PurpleAir publishes no OpenAPI or Swagger spec. Its docs at <https://api.purpleair.com/> are generated with [apiDoc](https://apidocjs.com/), which serves machine-readable data at `/api_data.js` and `/api_project.js`. [`docs/purpleair-openapi.yaml`](./docs/purpleair-openapi.yaml) is reconstructed from that data by [`scripts/generate_openapi.py`](./scripts/generate_openapi.py) and is the source of truth for the API surface this library targets.

**Do not hand-edit the spec, because it is generated.** [`OPERATIONS.md`](./OPERATIONS.md) "Regenerate the API Spec" holds the command and when to run it.

**The version comes from the changelog, not the metadata.** apiDoc's build version (`api_project.js` `version`) lags the real REST API version, which is published only as a changelog in the `welcome` doc block. The script takes the real version as the highest semver in that changelog and records the build version in the spec description. Trust the changelog version.

## Validating the Code Against the Spec

Do this when adding or changing an endpoint, a response model, a sensor field, or an error class.

- **Endpoints** in [`api.py`](./src/aiopurpleair/api.py) and [`endpoints/`](./src/aiopurpleair/endpoints/) must map to a spec `paths` entry, path plus method. An endpoint the spec lacks is API drift: regenerate first rather than inventing it.
- **`SENSOR_FIELDS`** in [`const.py`](./src/aiopurpleair/const.py) is the **requestable** `fields` catalog and must be a subset of the live API's accepted values. The spec's `components.schemas.SensorDataFields` mixes requestable fields with **response-only** ones: `stats`, `stats_a`, and `stats_b` are returned in the sensor payload, and parsed by `SensorModel`, but are **rejected** as `fields` values with `InvalidFieldValueError`, so they must **not** appear in `SENSOR_FIELDS`. The live full-catalog test (`test_live_sensors_parse_with_full_field_catalog`) is the guard: it requests every `SENSOR_FIELDS` entry, so an unrequestable field fails it.
- **The exception classes and `ERROR_CODE_MAP`** in [`errors.py`](./src/aiopurpleair/errors.py) track the spec's `components.schemas.Error` `error` enum, **plus** the HTTP and auth error codes the spec's per-endpoint `@apiError` blocks omit: API-key, payment, rate-limit, https, and data-initializing. Keep both, because the spec enum is a documented subset rather than the full set the API returns.

## Coverage

All 11 spec paths (API `1.2.0`) are implemented, and every response shape is verified against the live API: keys, sensors (list, single, history JSON and CSV), organization, and the full Groups API (groups CRUD, member add and remove, members data, single member, member history CSV).

Group create and member-add are eventually consistent, so a just-created group can 404 the member endpoint for roughly 10 seconds. Live capture polls until the group settles.
