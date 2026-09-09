# Operations

How this repository is run: the checks to run before pushing, the runbooks for the tasks that recur, and the local rule extensions that apply here on top of the carried fleet rules in [`GOVERNANCE.md`](./GOVERNANCE.md).

This library began as the `feat/organization-endpoint-and-error-codes` branch of a fork of [bachya/aiopurpleair](https://github.com/bachya/aiopurpleair) by Aaron Bach. Those additions were proposed upstream and later abandoned, and the library is now independently maintained here. It is MIT-licensed with dual copyright (original (c) 2024 Aaron Bach, current (c) 2026 Pieter Viljoen), retained in [LICENSE](./LICENSE) and [NOTICE](./NOTICE). The primary consumer is the [`homeassistant-purpleair`](https://github.com/ptr727/homeassistant-purpleair) HACS integration.

## Local Verification

Run the full gate set before pushing. `ruff` alone covers neither `mypy` nor `pyright`, and both are CI gates.

```sh
uv run ruff check              # lint
uv run ruff format --check     # format verify
uv run mypy src                # strict, shipped surface only
uv run pyright                 # src + tests, strict on src
uv run pytest                  # tests, with a 100% coverage gate
```

A pre-commit hook runs `uv run ruff check --fix` and `uv run ruff format` on staged Python files. Install it with `uvx prek install` (prek, a fast drop-in for pre-commit). It is language formatting only, and the doc linters and the full check set run in CI and in the VS Code Lint tasks.

The docs gate is the `docs` job in [`validate-task.yml`](./.github/workflows/validate-task.yml), and it runs five checks: `markdownlint` over all `*.md`, `cspell` over `README.md` and `HISTORY.md`, `editorconfig-checker` over the tree, `actionlint`, and `shellcheck`. **Run all five locally rather than deferring a check to CI because a tool is not installed.** Several are Node or Go tools that may be absent, so run the identical binaries through their official images. The commands below are POSIX shell, so on Windows run them from WSL2 or Git Bash, or substitute `${PWD}` for `"$PWD"` in PowerShell.

**The editorconfig-checker line walks the whole working directory**, and `.editorconfig-checker.json` declares no `Exclude`, so in a checkout that has run `uv sync` it reports thousands of errors from `.venv/` and the tool caches and none from tracked files. CI runs the identical command immediately after checkout, where none of those directories exist. Read its output against tracked files only, or run it in a clean clone:

```sh
docker run --rm -v "$PWD:/workdir" -w /workdir ghcr.io/streetsidesoftware/cspell:latest --no-progress --config cspell.json README.md HISTORY.md
docker run --rm -v "$PWD:/workdir" -w /workdir davidanson/markdownlint-cli2:latest '**/*.md'
docker run --rm -v "$PWD":/check --workdir /check mstruebing/editorconfig-checker:latest
docker run --rm -v "$PWD:/workdir" -w /workdir rhysd/actionlint:latest -color
docker run --rm -v "$PWD:/workdir" -w /workdir koalaman/shellcheck:latest repo-config/configure.sh
```

### Live API Validation

The default suite is fully mocked (aresponses + syrupy) and hits no network. [`tests/test_live_api.py`](./tests/test_live_api.py) is an **opt-in** layer that exercises the client against the real PurpleAir API with real credentials. It validates that the modeled fields, error codes, and organization endpoint still match production, including edge cases the mocks cannot prove, such as an overdrawn account returning a negative `remaining_points`. It is deselected by default and never runs in CI.

- **Credentials live in `.env.test`** at the repository root, gitignored and `chmod 600`, a dotenv file of real keys that is **never committed or echoed**. [`.env.test.example`](./.env.test.example) is the tracked template, so copy it and fill in real values. An alternate path can be given via `AIOPURPLEAIR_TEST_ENV`. Keys must never appear in output, so parametrized tests use positional ids (`key1`, `key2`) rather than the raw key.
- **Run it** with both the env flag and credentials present, or every live test skips:

  ```sh
  AIOPURPLEAIR_LIVE_TESTS=1 uv run pytest -m live --no-cov -v
  ```

  Use `--no-cov` because this layer deliberately does not drive the 100% coverage gate, which is the mocked suite's job. Omitting the flag or the file leaves the default `uv run pytest` unchanged.
- **What it checks**: each configured READ key validates via `check_api_key`; the organization endpoint parses for each account, asserting only field *types* since `remaining_points` may legitimately be negative; each owned sensor parses when **every** `SENSOR_FIELDS` entry is requested, so a clean parse proves the catalog; sensor history JSON and CSV parse, trying each key since history is gated per key and skips if disabled for all; and a self-cleaning groups round-trip creates a group with the WRITE key, lists it with the same-account READ key, and always deletes it. Writes use `PURPLEAIR_API_KEY_WRITE`. When adding an endpoint or field, extend this file so real data exercises it.

## Runbooks

### Add a Feature or Fix a Bug

Feature branch from `develop`, then code plus tests, then `uv run ruff format` and `uv run ruff check --fix`, then `uv run mypy src` and `uv run pyright`, then `uv run pytest`, then a pull request against `develop` with a descriptive title.

### Cut a Stable Release

Merge `develop -> main` with a merge commit. If the promotion touches a shipped path (`src/aiopurpleair/**`, `pyproject.toml`, `version.json`, `uv.lock`, which a real code or dependency change does touch), the paths-filtered push auto-publishes the stable PyPI release. A `workflow_dispatch` on `main` force-publishes the current tip when needed.

### Cut a Prerelease

A shipped-path push to `develop` publishes a `.dev0` prerelease automatically, and a `workflow_dispatch` on `develop` does it on demand.

**Never manually create a GitHub release or a tag.** The pipeline owns this end to end.

### Regenerate the API Spec

Run this whenever the upstream API may have changed. See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for what the spec governs and how the code is validated against it.

```sh
uv run --with pyyaml --with openapi-spec-validator python scripts/generate_openapi.py
```

That is a live fetch, and it writes and validates `docs/purpleair-openapi.yaml`. Pass `--data` and `--project` to run offline from cached `api_data.js` and `api_project.js`. Commit the regenerated spec: a non-empty diff means the upstream API changed and the library's coverage or models may need updating.

### Close an Issue From a Pull Request

**Put issue-closing keywords (`Closes #N`) in the `develop -> main` promotion pull request, not in the feature or `develop` one.** GitHub auto-closes an issue only from the pull request, or commit, that merges to the default branch, which is `main`. A `Closes #N` that merges only to `develop` never fires on promotion and leaves the issue open. Tag the promotion pull request's description, or close the issue by hand once the fix reaches `main`.

### Add a Dependabot Ecosystem

Edit [`.github/dependabot.yml`](./.github/dependabot.yml). Each ecosystem is listed twice, once per target branch.

## Backup and Recovery

The repository is the artifact, and GitHub holds the only copy that matters. Published PyPI releases are immutable and cannot be re-pushed at the same version, so a bad release is superseded by the next patch rather than replaced. See "Release and Versioning Facts" below for why `uv.lock` sits in the publish paths filter.

`.env.test` is the one piece of local state that is not recoverable from the repository. It holds real PurpleAir API keys, is gitignored by design, and is re-created from [`.env.test.example`](./.env.test.example) plus the keys held in the maintainer's password manager.

## Logs and Debugging

CI logs are the primary record: the PR gate in [`test-pull-request.yml`](./.github/workflows/test-pull-request.yml) and the publisher in [`publish-release.yml`](./.github/workflows/publish-release.yml). Coverage reports upload to Codecov, best-effort and `continue-on-error`, so a Codecov outage never reds a PR.

The library itself emits no logging. It raises typed exceptions from [`errors.py`](./src/aiopurpleair/errors.py) instead, so a consumer's own logger sees the failure with the API's error code preserved. When debugging a live-API mismatch, run the opt-in live layer above with `-v` rather than adding logging to the shipped surface.

## Tool Usage

The toolchain is entirely `uv run` (ruff, mypy, pyright, pytest), which behaves identically on every OS. The VS Code tasks in [`.vscode/tasks.json`](./.vscode/tasks.json) wrap the same `uv run` commands.

Snapshot tests use [syrupy](https://github.com/syrupy-project/syrupy). Regenerate them with `uv run pytest --snapshot-update` only when a response model changes intentionally, and review the snapshot diff like any other code.

## Configuration Layout

- [`repo-config/`](./repo-config/) holds this repository's branch-ruleset and deployment-environment payloads: the merge methods, the required check, signed commits, and strict-status-off settings that [`GOVERNANCE.md`](./GOVERNANCE.md) "Branching Model" describes. The apply script that consumes them is hub-hosted and reached rather than carried. Do not restate the ruleset details elsewhere.
- **Bot identity.** The merge bot is the `ptr727-codegen[bot]` App. Its repository secrets are `CODEGEN_APP_CLIENT_ID` (the App's Client ID) and `CODEGEN_APP_PRIVATE_KEY` (the App's private key, PEM contents). These are required in **both** the Actions and Dependabot secret stores, because a Dependabot-triggered run reads the Dependabot store rather than Actions secrets, and the merge bot acts on Dependabot PRs.
- `CODECOV_TOKEN` is the Codecov upload token the pytest matrix uses, in the Actions store only. The fleet registry declares it **required** for this repository, so it is configured rather than omitted. The upload step is separately `continue-on-error`, which means a Codecov outage degrades reporting instead of reddening a pull request. Required to configure and best-effort at run time are two different statements, and both hold.
- The App authors the auto-merges in [`merge-bot-pull-request.yml`](./.github/workflows/merge-bot-pull-request.yml). The built-in `GITHUB_TOKEN` will not do: its merge commits do not trigger the downstream `publish-release` push, and on a Dependabot PR it is read-only. Generate tokens with `actions/create-github-app-token`, never a hard-coded value or a PAT.
- **PyPI publishing is keyless OIDC Trusted Publishing, so there is no API token.** Registration is on PyPI as a trusted publisher for this repository plus workflow, alongside a `pypi` deployment environment restricted to `main` and `develop`.
- With no "Require approvals" on `develop` or `main`, bot PRs auto-merge as soon as the required check is green. If approvals are ever turned on, both `ptr727-codegen[bot]` and `dependabot[bot]` need to be on the bypass list.
- **Local credentials on disk** are limited to `.env.test`, covered under "Backup and Recovery" above.

## Local Rule Extensions

Rules that apply in this repository on top of the carried fleet rules. Each one is here because it is specific to this library, not because it disagrees with the fleet.

### Supported Platforms

Development runs cross-platform on Linux, macOS, and Windows, which is the fleet default in [`GOVERNANCE.md`](./GOVERNANCE.md) "Supported Development Platforms" rather than a narrowing. The `uv run` toolchain behaves identically on every OS and the dev loop has no shell scripts. The consuming [`homeassistant-purpleair`](https://github.com/ptr727/homeassistant-purpleair) integration is Linux-only because Home Assistant Core does not run natively on Windows, and that constraint does not apply to this library.

### Release and Versioning Facts

The version is derived by [Nerdbank.GitVersioning](https://github.com/dotnet/Nerdbank.GitVersioning) (NBGV) from [`version.json`](./version.json) and git history, so nothing in the committed working tree carries the real version number.

- [`version.json`](./version.json) holds the SemVer base `1.0` (major.minor) and the `publicReleaseRefSpec` regex matching `^refs/heads/main$`. NBGV adds the git commit height as the patch component, and on any ref not matching `publicReleaseRefSpec` appends a `-g{sha}` prerelease segment. So `main` produces clean SemVer such as `1.0.5`, and `develop` produces prereleases such as `1.0.5-g1a2b3c4`.
- Bump the base `version` field manually only when opening a new major or minor series. NBGV handles the patch component automatically.
- [`src/aiopurpleair/_version.py`](./src/aiopurpleair/_version.py) carries a placeholder `__version__`, the single source hatchling reads. **Do not hand-edit it to a real version.** The release build `sed`s the NBGV-computed PEP 440 version into it on the runner before `uv build`, so the published wheel carries the real version while git stays clean. On `develop` the build appends `.dev0` so `pip install --pre` prefers the dev build over the main release.

### Review and Merge Preconditions

[`GOVERNANCE.md`](./GOVERNANCE.md) "PR Review Etiquette" carries the fleet's review loop and merge gate whole. One fact is specific to this repository and changes what a merge means here, and it **overrides** the carried "Release Model" section's two-phase default, which states that a human merge never auto-publishes. That default is the fleet's, and this repository is registered `releaseTrigger: publish-on-merge` instead.

**Merging can release, so know which merges publish.** Unlike a pull-distributed target, this repository publishes on a paths-filtered push: a merge to `main` or `develop` that touches a shipped path (`src/aiopurpleair/**`, `pyproject.toml`, `version.json`, `uv.lock`) triggers [`publish-release.yml`](./.github/workflows/publish-release.yml), with `main` producing a stable PyPI release and `develop` a `.dev0` prerelease. A merge touching only docs, tests, or workflow YAML does not publish. So before authorizing a merge to a release branch, know whether it hits a shipped path, because if it does, the merge *is* a release. Never trigger a `workflow_dispatch` publish without explicit maintainer instruction.

### Release-Train Invariants

When reviewing a pull request that touches [`.github/workflows/`](./.github/workflows/) or the release configuration, check the change against these invariants. Each one is intentional and was reached after a real failure mode, so flag any drift and escalate rather than implementing a relaxation.

- **The publish gate is the same validate suite CI runs.** [`publish-release.yml`](./.github/workflows/publish-release.yml)'s `publish-pypi` job `needs:` the `validate` job, which reuses the identical [`validate-task.yml`](./.github/workflows/validate-task.yml) (lint plus the 3.13/3.14 pytest matrix) that [`test-pull-request.yml`](./.github/workflows/test-pull-request.yml) runs. Reject any change that lets the publish path skip validation, or that forks publish-time validation into a weaker copy. The PR gate and the publish gate stay one definition, so nothing publishes that would fail the PR.
- **Publishing is paths-filtered push plus dispatch, and the paths list is the shipped surface.** The publisher triggers on `push` to `main` and `develop` filtered to `src/aiopurpleair/**`, `pyproject.toml`, `version.json`, and `uv.lock`, plus `workflow_dispatch`. `uv.lock` is deliberately in the list: a PyPI version cannot be re-pushed, so a dependency bump must republish to keep the package's declared dependencies current. Reject a change that drops `uv.lock` from the filter, which re-opens the stale-dependency window, or that broadens the filter so docs, test, or workflow-only changes start publishing.
- **Publishing is keyless OIDC Trusted Publishing, with no stored token.** The `publish-pypi` job runs in the `pypi` environment with `permissions: id-token: write` and uploads via `pypa/gh-action-pypi-publish` over OIDC. Reject any change that adds a `password:` or `PYPI_API_TOKEN` secret to the publish step. The Trusted Publisher registration plus the `pypi` environment's branch restriction is the whole trust chain.
- **One required check gates merge, named verbatim.** The single aggregator job is exactly `Check pull request workflow status job`, and its name is the ruleset-bound `context:` in [`repo-config/`](./repo-config/). Reject a rename that is not matched by a `repo-config/` change in the same pull request, because an unmatched rename leaves every pull request unmergeable: CI runs but the required check never resolves.
- **Dependabot auto-merges every tier, and the required checks are the gate rather than the bump magnitude.** The [merge bot](./.github/workflows/merge-bot-pull-request.yml) enables auto-merge on every Dependabot pull request regardless of semver level, **semver-major included**. A bump that breaks a covered path reds the required checks and stays open, rather than every major being held for human review. Reject a change that re-introduces an `update-type` or `version-update:semver-major` filter on the merge step: it was removed deliberately so that a green suite, not the bump magnitude, decides the merge.

### Commit Message Examples

[`GOVERNANCE.md`](./GOVERNANCE.md) "Pull Request Title and Commit Message Conventions" carries the rules. These are worked examples in this repository's own subject matter.

```text
Add the GET /v1/organization endpoint
Map InvalidDataReadKeyError to HTTP 400 read-key failures
Return tz-aware UTC datetimes from the timestamp validator
Bump aiohttp from 3.11.0 to 3.12.0
Clarify the connection-pooling example in README
```
