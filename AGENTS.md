# Agent guide

Notes for AI coding agents working in this repo. Keep responses concise; prefer editing existing files over creating new ones; never narrate internal deliberation.

## What this is

An async Python client library for the [PurpleAir][purpleair] air-quality API, published to PyPI as **`ptr727-aiopurpleair`** (the import package stays `aiopurpleair`). It covers the sensors and keys endpoints, adds a `GET /v1/organization` endpoint for tracking remaining API points, and maps the API's documented error codes to a typed exception hierarchy. Library source lives under [`src/aiopurpleair/`](src/aiopurpleair/) (src-layout), the build backend is hatchling, and the environment is [uv][uv]-managed. `requires-python >=3.13`.

The library began as the `feat/organization-endpoint-and-error-codes` branch of a fork of [bachya/aiopurpleair][upstream] by Aaron Bach. Those additions were proposed upstream and later abandoned; the library is now independently maintained here. It is **MIT-licensed with dual copyright** - original © 2024 Aaron Bach, current © 2026 Pieter Viljoen - retained in [LICENSE](LICENSE) and [NOTICE](NOTICE). The primary consumer is the [`homeassistant-purpleair`][ha-purpleair] HACS integration.

## Branches and merging

- Pipeline is `feature -> develop -> main`. Both `develop` and `main` are protected; everything lands via PR.
- **Feature -> develop PRs squash-merge** (single commit on develop, PR title becomes the commit message; never rebase-merge).
- **Develop -> main PRs merge-commit** (one merge commit on main per release, develop's tip becomes a second parent and stays in main's ancestry). The rulesets are split: PRs into `develop` are squash-only (linear history); PRs into `main` are merge-commit only. Clicking "Create a merge commit" on a develop -> main PR makes develop a real ancestor of main, so the *next* develop -> main PR has a clean merge base (no recurring conflicts).
- Open feature PRs against `develop`. `develop -> main` is how stable releases are cut.
- The branch rulesets that enforce this (merge methods, required check, signed commits, strict-status off), the repository settings, and the required secret names are codified in [`repo-config/`](repo-config/); `repo-config/configure.sh apply` syncs the live repo and `check` audits it for drift (the 5D audit). Do not restate the ruleset details elsewhere.
- **Mirror to `develop` any change that lands on `main` outside the feature -> develop -> main flow.** A reconciliation-branch fix made to resolve a `develop -> main` promotion conflict, or a security PR that merges only to `main`, leaves `develop` behind on that content - and forward-only `develop` never back-merges to catch up (the same parallel-target principle as the bots). Before basing new work on `develop`, or diagnosing a defect from it, check `git diff origin/develop origin/main`: a non-empty content diff means develop is stale and the defect may already be fixed on `main`.
- **Put issue-closing keywords (`Closes #N`) in the `develop -> main` promotion PR, not the feature or develop PR.** GitHub auto-closes an issue only from the PR (or commit) that merges to the default branch (`main`); a `Closes #N` that merges only to `develop` does not fire on promotion and leaves the issue open. Tag the promotion PR's description, or close the issue manually once the fix reaches `main`.

## Git and Commit Rules

- **Default to staging, not committing.** Stage changes with `git add` and leave `git commit` to the developer unless the developer has explicitly authorized the agent to commit for the current ask ("commit this", "open a PR", etc.). Authorization is scope-bound - it covers the commits needed for that specific task, not a blanket commit license for the rest of the session.
- **All commits must be cryptographically signed (SSH or GPG).** Branch protection enforces this on both branches; unsigned commits are rejected on push. Signing depends on environment configuration - `git config commit.gpgsign true`, a configured `user.signingkey`, and a working signing agent (loaded `ssh-agent` for SSH, or `gpg-agent` for GPG). If signing is not configured in the environment, **do not commit** - surface the missing config to the developer and stop at `git add`. Verify before any agent-authored commit (`git config --get commit.gpgsign && ssh-add -L` or the GPG equivalent). **Signing must be live before the *first* commit, not retrofitted.** Turning on `Require signed commits` against a branch that already has unsigned commits forces a rewrite of that entire history to re-sign it - changing every commit SHA and making whoever does the rewrite the committer and signer of every commit (a rebase preserves the `author` field but not the original signatures; you cannot sign another contributor's commits for them). During new-repo setup, never create commits until signing is verified.
- **Never force push.** Do not run `git push --force` or `git push --force-with-lease` under any circumstances. Force pushing rewrites shared history and can cause data loss.
- **Never run destructive git commands** (`git reset --hard`, `git checkout .`, `git restore .`, `git clean -f`) without explicit developer instruction.

## Pull Request Title and Commit Message Conventions

### Format

- Imperative subject summarizing the change, <=72 characters, no trailing period. ("Add organization endpoint", not "Added X" or "Adds X".)
- Optional body, blank-line separated, explaining *why* the change is being made when that's non-obvious. The diff shows *what*.

### Rules

- Don't write `update stuff`, `wip`, or other vague titles. (Dependabot's default `Bump X from Y to Z` titles are fine - keep them.)
- Don't add `Co-Authored-By:` lines unless the developer explicitly asks.
- Don't put release-bump magnitude in the title - no "minor", "patch", "release v1.0.1", etc. Nerdbank.GitVersioning computes the next release version from `version.json` + git history. Dependency versions in dependency-bump titles are fine and expected.
- Use US English spelling and match the existing heading style of the file you're editing: title case with lowercase short bind words (a, an, the, and, but, or, of, in, on, at, to, by, for, from); hyphenated compounds capitalize both parts unless the second is a short preposition (*Built-in*, *Read-only*, *24-Hour*).

### Examples

```text
Add the GET /v1/organization endpoint
Map InvalidDataReadKeyError to HTTP 400 read-key failures
Return tz-aware UTC datetimes from the timestamp validator
Bump aiohttp from 3.11.0 to 3.12.0
Clarify the connection-pooling example in README
```

## Writing style

Use **US English spelling** in code comments, identifiers, commit messages, PR descriptions, and documentation: *behavior* (not behaviour), *color* (not colour), *recognize* (not recognise), *organize* (not organise), *cancel/canceled* (not cancelled), and so on.

**Headings** are title case with lowercase short bind words: a, an, the, and, but, or, of, in, on, at, to, by, for, from. Verbs (including *is/are/was*) and other content words are capitalized. Hyphenated compounds capitalize the second part unless it's a short preposition - *Built-in*, *Read-only*, *24-Hour*.

**Markdown style** uses reference-style links with definitions at the bottom of the file for external URLs and any URL referenced more than once. Single-use relative links to local repo files are fine inline. Write one logical paragraph per line - hard-wrapping mid-sentence makes diffs noisier than necessary. Code blocks, tables, and intentional `\` line breaks stay verbatim.

**Quantitative claims** in [README.md](README.md) and this file (percentages, counts, timings) must be verified against current code or a reproducible measurement before being added or carried forward. When a claim depends on a source-side constant (e.g. the number of mapped error codes in [`src/aiopurpleair/errors.py`](src/aiopurpleair/errors.py)), re-count against the source rather than trusting a prior figure.

## Versioning

The version is derived by [Nerdbank.GitVersioning][nbgv] (NBGV) from [version.json](version.json) and git history - nothing in the committed working tree carries the real version number.

- [version.json](version.json) holds the SemVer base `1.0` (major.minor) and the `publicReleaseRefSpec` regex matching `^refs/heads/main$`. NBGV adds the git commit height as the patch component, and on non-public refs (anything not matching `publicReleaseRefSpec`) appends a `-g{sha}` prerelease segment. So `main` produces clean SemVer like `1.0.5`; `develop` produces prereleases like `1.0.5-g1a2b3c4`.
- Bump `version.json`'s base `version` field manually only when opening a new major/minor series (e.g. `1.1` or `2.0`). NBGV handles the patch (height) component automatically. **Never create manual tags** - the release pipeline creates the tag.
- [`src/aiopurpleair/_version.py`](src/aiopurpleair/_version.py) carries a placeholder `__version__` (the single source hatchling reads). Do not hand-edit it to a real version. [`build-release-task.yml`](.github/workflows/build-release-task.yml) `sed`s the NBGV-computed PEP 440 version into it on the runner before `uv build`, so the published wheel carries the real version while git stays clean. On `develop` the build appends `.dev0` so `pip install --pre` prefers the dev build over the main release.

## PurpleAir API Reference and Coverage

PurpleAir does not publish an OpenAPI/Swagger spec; its docs at <https://api.purpleair.com/> are generated with [apiDoc](https://apidocjs.com/), which serves machine-readable data at `/api_data.js` and `/api_project.js`. [`docs/purpleair-openapi.yaml`](docs/purpleair-openapi.yaml) is reconstructed from that data by [`scripts/generate_openapi.py`](scripts/generate_openapi.py) and is the source of truth for the API surface this library targets. **Don't hand-edit the spec - it is generated.**

- **Regenerate** whenever the upstream API may have changed: `uv run --with pyyaml --with openapi-spec-validator python scripts/generate_openapi.py` (live fetch; writes and validates `docs/purpleair-openapi.yaml`). Pass `--data`/`--project` to run offline from cached `api_data.js`/`api_project.js`. Commit the regenerated spec; a non-empty diff means the upstream API changed and the library's coverage or models may need updating.
- **Version comes from the changelog, not the metadata.** apiDoc's build version (`api_project.js` `version`) lags the real REST API version, which is published only as a changelog in the `welcome` doc-block. The script takes the real version as the highest semver in that changelog and records the build version in the spec description. Trust the changelog version.
- **Validate the code against the spec** when adding or changing an endpoint, response model, sensor field, or error class:
  - Endpoints in [`api.py`](src/aiopurpleair/api.py) / [`endpoints/`](src/aiopurpleair/endpoints/) must map to a spec `paths` entry (path + method). An endpoint the spec lacks is API drift - regenerate first, don't invent it.
  - `SENSOR_FIELDS` in [`const.py`](src/aiopurpleair/const.py) is the **requestable** `fields` catalog and must be a subset of the live API's accepted values. Note the spec's `components.schemas.SensorDataFields` mixes requestable fields with **response-only** ones: `stats`/`stats_a`/`stats_b` are returned in the sensor payload (and parsed by `SensorModel`) but are **rejected** as `fields` values (`InvalidFieldValueError`), so they must **not** be in `SENSOR_FIELDS`. The live full-catalog test (`test_live_sensors_parse_with_full_field_catalog`) is the guard: it requests every `SENSOR_FIELDS` entry, so an unrequestable field fails it.
  - The exception classes and `ERROR_CODE_MAP` in [`errors.py`](src/aiopurpleair/errors.py) track the spec's `components.schemas.Error` `error` enum, **plus** the HTTP/auth error codes the spec's per-endpoint `@apiError` blocks omit (API-key, payment, rate-limit, https, data-initializing). Keep both: the spec enum is a documented subset, not the full set the API returns.
- **Coverage**: all 11 spec paths (API `1.2.0`) are implemented and every response shape is verified against the live API - keys, sensors (list, single, history JSON/CSV), organization, and the full Groups API (groups CRUD, member add/remove, members data, single member, member history CSV). Note: group create/member-add are eventually consistent (a just-created group can 404 the member endpoint for ~10s), so live capture polls until the group settles.

## Live API validation

The default suite is fully mocked (aresponses + syrupy) and hits no network. [`tests/test_live_api.py`](tests/test_live_api.py) is an **opt-in** layer that exercises the client against the real PurpleAir API with real credentials - it validates that the modeled fields, error codes, and organization endpoint still match production, including edge cases the mocks can't prove (e.g. an overdrawn account returning a negative `remaining_points`). It is deselected by default and never runs in CI.

- **Credentials live in `.env.test`** (repo root, gitignored, `chmod 600`) - a dotenv file of real keys that is **never committed or echoed**. [`.env.test.example`](.env.test.example) is the tracked template; copy it and fill in real values. An alternate path can be given via `AIOPURPLEAIR_TEST_ENV`. Keys must never appear in output: parametrized tests use positional ids (`key1`, `key2`), not the raw key.
- **Run** (both the env flag and credentials are required, else every live test skips):

  ```sh
  AIOPURPLEAIR_LIVE_TESTS=1 uv run pytest -m live --no-cov -v
  ```

  Use `--no-cov` because this layer intentionally doesn't drive the 100% coverage gate (that is the mocked suite's job). Omitting the flag or the file leaves the default `uv run pytest` unchanged - live tests skip.
- **What it checks**: each configured READ key validates via `check_api_key`; the organization endpoint parses for each account (asserting only field *types*, since `remaining_points` may legitimately be negative); each owned sensor parses when **every** `SENSOR_FIELDS` entry is requested (an unknown/unrequestable field would raise, so a clean parse proves the catalog); sensor history JSON+CSV parse (trying each key, since history is gated per key and skips if disabled for all); and a self-cleaning groups round-trip creates a group with the WRITE key, lists it with the same-account READ key, and always deletes it. Uses `PURPLEAIR_API_KEY_WRITE` for writes. When adding an endpoint or field, extend this file so real data exercises it.

## PR Review Etiquette

> **Mandatory contract.** This entire "PR Review Etiquette" section is the provider-agnostic review-loop *contract*, carried alongside the [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) "GitHub Copilot Review Runbook" that implements it. Without both in-repo, an agent has no pointer to the reliable Copilot mechanics and falls back to ad-hoc (and known-broken) behavior.

The repo runs a review loop on every PR: local agent iteration plus remote automated review (GitHub Copilot is the configured reviewer). Treat this as a contract regardless of which local agent authored the changes.

### Merge Gate (read this first)

**Do not merge - and do not enable auto-merge - unless ALL of these hold:**

1. Required status checks are green (`mergeStateStatus: CLEAN`), **and**
2. A Copilot review is confirmed on the **current head SHA** (not an earlier push), **and**
3. **Every** Copilot finding on that head SHA is closed out - all review threads resolved, **and** any issue-level Copilot comments (which have no resolve action) triaged and replied to - so zero outstanding findings remain, **and**
4. The maintainer has given **explicit** permission to merge.

`mergeStateStatus: CLEAN` reflects **only** required statuses - it never reflects open bot review comments, so `CLEAN` alone is **never** sufficient to merge. A green/`CLEAN` PR with an unresolved Copilot finding fails this gate; treat it as "not mergeable" no matter what the merge-state field says. The agent never merges on its own (consistent with "default to staging"; merging is maintainer-authorized).

**Merging *can* release here - know which merges publish.** Unlike a pull-distributed target, this repo publishes on a **paths-filtered push**: a merge to `main` or `develop` that touches a *shipped* path (`src/aiopurpleair/**`, `pyproject.toml`, `version.json`, `uv.lock`) triggers [`publish-release.yml`](.github/workflows/publish-release.yml) - `main` -> a stable PyPI release, `develop` -> a `.dev0` prerelease. A merge that touches only docs, tests, or workflow YAML does **not** publish. So before authorizing a merge to a release branch, know whether it hits a shipped path; if it does, the merge *is* a release. Never trigger a `workflow_dispatch` publish without explicit maintainer instruction.

### Expected Review Loop

1. Push changes to the PR branch.
2. Re-request a review for the **current head SHA**. Auto-trigger is unreliable, so request it explicitly via the `requestReviews` GraphQL mutation (see the runbook); the UI is only a fallback.
3. Wait for review activity on that head. A completed review that raises **no findings** is a valid terminal outcome for that head - proceed; do not re-trigger it or treat the absence of comments as a missing review.
4. Triage findings.
5. Apply fixes or write a rationale for declines.
6. Reply to each thread and resolve what was addressed.
7. Re-run the loop after every fix push until no actionable findings remain.

Drive the loop to green - review confirmed on the latest head SHA and every actionable finding closed - then stop and apply the **Merge Gate** above: all four preconditions must hold, and `mergeStateStatus: CLEAN` alone never satisfies it.

For provider-specific mechanics (how to request review, query review state, post replies, resolve threads), see the **GitHub Copilot Review Runbook** in [.github/copilot-instructions.md](./.github/copilot-instructions.md). This file owns the contract; that file owns the mechanics.

### Triaging Review Comments

For each comment, classify before responding:

- **Bug** - wrong behavior, missing test coverage, or a real divergence between code and docs. Fix it. Reply with the fixing commit SHA when done.
- **Style/convention** - the comment cites a rule from this file or a language-specific style guide. Two cases:
  - The cited rule matches what the existing codebase already does -> fix the offending code.
  - The cited rule contradicts what's in the tree, or industry norm -> **update the rule instead of the code**. The rule is wrong, not the code. Bouncing the same code across rounds is the symptom of a wrong rule. Heuristic: three rounds on the same style category means the rule needs adjusting and the user should authorize the rule change.
- **Architectural opinion** - the comment proposes a different design ("constrain this", "move it elsewhere", "add a runtime guardrail"). This is judgment, not a bug. Surface it to the user with a recommendation; don't apply unilaterally.

### Responding and Resolution Expectations

Reply inline with either the fixing commit SHA (for accepted issues) or a concise rationale (for declines). Resolve review threads when addressed or intentionally declined with rationale. Issue-level comments (those at `repos/.../issues/<N>/comments` rather than tied to a specific line) have no resolution action - acknowledge with a reply if needed and move on.

After the final push on a PR, sweep older threads from earlier rounds whose code paths no longer exist; otherwise stale unresolved markers remain in the review UI.

### Escalating to the User

Bring the user in when:

- **Genuine design trade-off** surfaces (fail-open vs fail-closed, narrow vs broad refactor scope, "should we add a guardrail or trust the docstring"). Triage, recommend, ask.
- **Repeated friction** across rounds without convergence - that's the rule-needs-updating signal. Stop, summarize the pattern, and let the user authorize the rule change.
- **Architectural redesign** is requested rather than a bug fix. Surface with a recommendation; never apply unilaterally.

Anti-pattern: don't keep flipping the code on the same style point. Flip the rule once and stick to the rule.

## Reviewing CI / Release-Train Changes

When reviewing a PR that touches [`.github/workflows/`](.github/workflows/) or the release configuration, check the change against these load-bearing invariants. Each one is intentional and was reached after a real failure mode; flag any drift.

- **The publish gate is the same validate suite CI runs.** [`publish-release.yml`](.github/workflows/publish-release.yml)'s `publish-pypi` job `needs:` the `validate` job, which reuses the identical [`validate-task.yml`](.github/workflows/validate-task.yml) (lint + the 3.13/3.14 pytest matrix) that [`test-pull-request.yml`](.github/workflows/test-pull-request.yml) runs. Reject any PR that lets the publish path skip validation, or that forks the publish-time validation into a weaker copy - the PR gate and the publish gate must stay one definition, so nothing publishes that would fail the PR.
- **Publishing is paths-filtered push plus dispatch - and the paths list is the shipped surface.** The publisher triggers on `push` to `main`/`develop` filtered to `src/aiopurpleair/**`, `pyproject.toml`, `version.json`, and `uv.lock`, plus `workflow_dispatch`. `main` publishes a stable release, `develop` a `.dev0` prerelease. `uv.lock` is deliberately in the list: a PyPI version can't be re-pushed, so a dependency bump must republish to keep the package's declared dependencies current. Reject PRs that drop `uv.lock` from the paths filter (re-opens the stale-dependency window) or that broaden the filter so docs/test/workflow-only changes start publishing.
- **Publishing is keyless OIDC Trusted Publishing - no stored token.** The `publish-pypi` job runs in the `pypi` environment with `permissions: id-token: write` and uploads via `pypa/gh-action-pypi-publish` over OIDC. There is **no** PyPI API token anywhere. Reject any PR that adds a `password:`/`PYPI_API_TOKEN` secret to the publish step - the Trusted Publisher registration on PyPI plus the `pypi` environment's branch restriction (main/develop) is the whole trust chain.
- **One required check gates merge, named verbatim.** The single aggregator job is exactly `Check pull request workflow status job`; its name is the ruleset-bound `context:` in [`repo-config/`](repo-config/). Reject a rename that isn't matched by a `repo-config/` change in the same PR (an unmatched rename leaves every PR unmergeable - CI runs but the required check never resolves).
- **Dependabot auto-merges every tier - the required checks are the gate, not the version bump.** The [merge-bot](.github/workflows/merge-bot-pull-request.yml) enables auto-merge on every Dependabot PR regardless of semver level, **semver-major included**; a bump that breaks a covered path reds the required checks and stays open, rather than every major being held for human review. Reject PRs that re-introduce an `update-type` / `version-update:semver-major` filter on the merge step - it was removed deliberately so that a green suite, not the bump magnitude, decides the merge.

If a reviewer argues for relaxing any of these, escalate to the maintainer rather than implementing - these are explicit user decisions, not lint rules.

## Code style

Full language rules live in [CODESTYLE.md](./CODESTYLE.md) (a General section plus a self-contained Python section). Highlights:

- The toolchain runs through `uv run`: `uv run ruff check` (lint), `uv run ruff format --check` (format verify), `uv run mypy src` (strict, shipped surface only), `uv run pyright` (src + tests, strict on src), `uv run pytest` (tests with a **100% coverage** gate).
- **Tools target the 3.13 floor** (`target-version = "py313"`, `python_version = "3.13"`, `pythonVersion = "3.13"`), so 3.13 compatibility is statically enforced, while CI's pytest matrix exercises both **3.13 and 3.14**.
- **Snapshot tests use [syrupy][syrupy].** Regenerate them with `uv run pytest --snapshot-update` only when a response model changes intentionally; review the snapshot diff like any other code.
- Run the lint set plus `uv run pytest` before pushing - `ruff` alone does not cover `mypy` or `pyright`, both of which are CI gates.

## Bot identity and secrets

- App: `ptr727-codegen[bot]`. Repo secrets:
  - `CODEGEN_APP_CLIENT_ID` - the App's Client ID.
  - `CODEGEN_APP_PRIVATE_KEY` - the App's private key (PEM contents).
  - These are required in **both** the Actions and Dependabot secret stores: the merge-bot reads them from the Dependabot store when it acts on a Dependabot PR (a Dependabot-triggered run gets the Dependabot store, not Actions secrets).
  - `CODECOV_TOKEN` - the Codecov upload token the pytest matrix uses. Optional (the upload is best-effort `continue-on-error`), Actions store only.
- The App authors the auto-merges in [`merge-bot-pull-request.yml`](.github/workflows/merge-bot-pull-request.yml) (Dependabot PRs). The built-in `GITHUB_TOKEN` will not do: its merge commits do not trigger the downstream `publish-release` push, and on a Dependabot PR it is read-only. Generate tokens with `actions/create-github-app-token` - never hard-code or use a PAT.
- **PyPI publishing is keyless OIDC** (Trusted Publishing) - there is **no** API token. Registration is on PyPI as a pending/trusted publisher for this repo + workflow, plus a `pypi` deployment environment restricted to `main` and `develop`.
- With no "Require approvals" on `develop`/`main`, bot PRs auto-merge as soon as the required check is green. If approvals get turned on, both `ptr727-codegen[bot]` and `dependabot[bot]` need to be on the bypass list.

## Common tasks

- **Add a feature / fix a bug**: feature branch from `develop` -> code + tests -> `uv run ruff format` + `uv run ruff check --fix` -> `uv run mypy src` + `uv run pyright` -> `uv run pytest` -> PR against `develop` with a descriptive title.
- **Cut a stable release**: merge `develop -> main` with a merge commit. If the promotion touches a shipped path (`src/aiopurpleair/**`, `pyproject.toml`, `version.json`, `uv.lock` - a real code or dependency change does), the paths-filtered push auto-publishes the stable PyPI release. A `workflow_dispatch` on `main` force-publishes the current tip when needed.
- **Cut a prerelease**: a shipped-path push to `develop` publishes a `.dev0` prerelease automatically; a `workflow_dispatch` on `develop` does it on demand.
- **Don't manually create GitHub releases or tags.** The pipeline owns this end-to-end.
- **Add a Dependabot config / new ecosystem**: edit [`.github/dependabot.yml`](.github/dependabot.yml) (each ecosystem is listed twice, once per target branch).

[ha-purpleair]: https://github.com/ptr727/homeassistant-purpleair
[nbgv]: https://github.com/dotnet/Nerdbank.GitVersioning
[purpleair]: https://api.purpleair.com/#api-welcome
[syrupy]: https://github.com/syrupy-project/syrupy
[upstream]: https://github.com/bachya/aiopurpleair
[uv]: https://github.com/astral-sh/uv
