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

The docs gate is the `lint` job in the hub's `validate-task.yml`, which this repository reaches by pin from [`test-pull-request.yml`](./.github/workflows/test-pull-request.yml) rather than carrying, and its doc-lint block runs four checks: `markdownlint` over all `*.md`, `cspell` over `README.md` and `HISTORY.md`, `editorconfig-checker` over the tree, and `actionlint`. **Run all four locally rather than deferring a check to CI because a tool is not installed.** Several are Node or Go tools that may be absent, so run them through their official images. **These are the same tools, not the same builds.** CI reaches `markdownlint`, `cspell`, and `actionlint` through SHA-pinned GitHub Actions, and only `editorconfig-checker` is Docker on both sides. The hub `lint` job also runs one `Check shell scripts step` (`shellcheck` plus `shfmt -d`), which discovers shell scripts itself and no-ops on an empty set, so it runs here and finds nothing while the tree carries no shell script. Adding one activates it with no edit here. The fleet prose gate and repo gate, which the hub `lint` job also runs, are covered after the commands below. The `:latest` tags below drift from the pinned CI versions over time, so where an exact-parity answer matters, pin each tag to the version the corresponding action resolves to in the hub's `validate-task.yml`, at the pin [`test-pull-request.yml`](./.github/workflows/test-pull-request.yml)'s `validate` job names rather than the release chain's pin beside it. The commands below are POSIX shell, so on Windows run them from WSL2 or Git Bash, or substitute `${PWD}` for `"$PWD"` in PowerShell.

**The editorconfig-checker line walks the whole working directory, and whether it honors `.gitignore` depends on the shape of the checkout.** Where `.git` is a directory it skips every ignored path, so `.venv/` and the tool caches are never walked. In a linked `git worktree` `.git` is a file, the tool reads no `.gitignore` at all, and those directories join the walk. A worktree is the ordinary local case rather than the exception, since [`GOVERNANCE.md`](./GOVERNANCE.md) "Repository Boundaries and Write Safety" puts every task in one, so `.editorconfig-checker.json` declares an `Exclude` covering `.venv/` and the `__pycache__`, `mypy`, `pytest` and `ruff` caches. **What the `Exclude` removes is the walk rather than a known set of findings.** The `Disable` block leaves only `EndOfLine` enabled, so whether an excluded tree reports anything at all depends on its contents and on the platform that wrote them, and a `uv sync` of this repository's own lock on Linux reports nothing from it. Two limits are worth knowing before reading a clean run as proof. The tool applies its own default excludes on top of `.gitignore`, so `uv.lock` is checked in neither shape and a CRLF one passes the gate. And a gitignored path outside the `Exclude`, `dist/` after a `uv build` or `.pyright/`, is still walked in a worktree, so read an unexpected finding against its path before treating it as a tracked-file failure:

```sh
docker run --rm -v "$PWD:/workdir" -w /workdir ghcr.io/streetsidesoftware/cspell:latest --no-progress --config cspell.json README.md HISTORY.md
docker run --rm -v "$PWD:/workdir" -w /workdir davidanson/markdownlint-cli2:latest '**/*.md'
docker run --rm -v "$PWD":/check --workdir /check mstruebing/editorconfig-checker:latest
docker run --rm -v "$PWD:/workdir" -w /workdir rhysd/actionlint:latest -color
```

**The hub `lint` job's prose gate and repo gate also run locally, from a hub checkout of your own.** Each is a Python script in that checkout, `.github/actions/prose-gate/prose_lint.py` and `.github/actions/repo-gate/repo_gate.py`, and each scans the current working directory rather than the hub checkout it lives in. Run both from this repository's top level, since the prose gate run from a subdirectory reads none of the changed files outside it and passes. Run them before pushing a doc change, since the prose gate is the check most likely to fail a pull request that every other local check passed. **The prose gate is diff-scoped.** It diffs the working tree against a base and reports only on the lines that diff touches, uncommitted and untracked ones included. It reads a whole changed line, so an old violation on a line you edited fails the gate even where your own text is clean. CI passes the pull request's base SHA. Locally, the merge-base with the target branch gives the same scope without counting commits the target gained after the branch was cut. Fetch first, and use `origin/main` in place of `origin/develop` for a promotion pull request. The repo gate needs no base. Its `sha-pin` check resolves the pins under the owner of this checkout's `origin` remote through an authenticated `gh`, and reads every other pin for shape only. In a clone of a fork, a clone with no `origin` remote, without `gh`, or offline, it still passes while resolving none of this repository's hub pins. Read its note before trusting a clean run, since a pin it counts as under another owner, as unowned because this checkout's origin is unreadable, or as one GitHub did not answer for was read for shape only. A note reporting 0 resolved means a clean run proves only that each pin is SHA-shaped. **A hub checkout's copy is not the copy CI runs.** CI resolves both scripts at the hub commit that the `validate` job's `uses:` line in [`test-pull-request.yml`](./.github/workflows/test-pull-request.yml) pins, not at the hub's `main`. Where an exact-parity answer matters, check that commit out in the hub checkout first. The block below is POSIX shell with no PowerShell form, so on Windows run it from WSL2, in a clone or worktree created there, since Linux git cannot follow the Windows path that a Git for Windows worktree records. The Windows Python that Git Bash reaches is no substitute, since it can fail to decode a diff carrying non-ASCII text. Both scripts need only the standard library, so a plain `python3` at 3.9 or later runs them and leaves `.venv` alone. Each gate prints its own verdict, and the block's exit status is the repo gate's alone, so read both results rather than the exit status. `HUB` is the hub checkout's path, and the block runs neither command until both `HUB` and the merge-base are set, since an empty merge-base would scan the whole tree:

```sh
git fetch origin
base="$(git merge-base origin/develop HEAD)"
if [ -n "$HUB" ] && [ -n "$base" ]; then
  python3 "$HUB/.github/actions/prose-gate/prose_lint.py" --diff "$base" -- .
  python3 "$HUB/.github/actions/repo-gate/repo_gate.py"
else
  echo "set HUB to your hub checkout's path, and fetch the target branch" >&2
fi
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

Merge `develop -> main` with a merge commit, then **dispatch the publisher on `main`**. The promotion merge itself publishes nothing, because a human merge never auto-cuts a release, so the release is a separate and deliberate step. The one path that publishes without a dispatch is a shipped-path merge to `main` made by an **allowlisted** bot, meaning `ptr727-codegen[bot]` or `dependabot[bot]`.

### Cut a Prerelease

Dispatch the publisher on `develop`, which builds a `.dev0` prerelease. Pushes to `develop` reach no publish trigger at all, so a prerelease is always deliberate.

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

- **This repository carries no repository-configuration payloads.** The branch rulesets implementing the merge methods and promotion rules in [`GOVERNANCE.md`](./GOVERNANCE.md) "Branching Model", the fleet label set, and the general repository settings listed in [`WORKFLOW.md`](./WORKFLOW.md) section 6 are all the hub's, applied and checked by the hub-hosted `repo-config/configure.sh` against the hub's own payloads. Running `repo-config/configure.sh check ptr727/aiopurpleair release` from a hub checkout at `main` is the whole of it, so there is no local copy to keep in step and none to drift. Do not restate the ruleset details here or reintroduce a payload directory.
- **The `pypi` deployment environment is checked but never applied.** The hub's script asserts it against the `environments` block the fleet registry declares for this repository, so a hand-added branch or a changed policy reads as drift. What it will not do is write one: `apply` carries no environment write at all, which is the hub's choice about what the script owns. So the environment is created by hand once and verified by the tool thereafter. That hand step is small here, because publishing is keyless OIDC and this environment holds no secret and no variable, so its existence and its branch policy are the whole of its contribution to the gate. [`AUDIT.md`](./AUDIT.md) section 4 records the expected values.
- **Bot identity.** The merge bot is the `ptr727-codegen[bot]` App. Its repository secrets are `CODEGEN_APP_CLIENT_ID` (the App's Client ID) and `CODEGEN_APP_PRIVATE_KEY` (the App's private key, PEM contents). These are required in **both** the Actions and Dependabot secret stores, because a Dependabot-triggered run reads the Dependabot store rather than Actions secrets, and the merge bot acts on Dependabot PRs.
- `CODECOV_TOKEN` is the Codecov upload token the pytest matrix uses, required in **both** the Actions and Dependabot stores for the same reason the App credentials are: a Dependabot-triggered run reads the Dependabot store, so without that copy the coverage upload fails on every bot pull request. The step logs it and does not red the run, so the loss shows in the log rather than in the check result. The fleet registry declares it **required** for this repository, so it is configured rather than omitted. The upload step is separately `continue-on-error`, which means a Codecov outage degrades reporting instead of reddening a pull request. Required to configure and best-effort at run time are two different statements, and both hold.
- The App authors the auto-merges. [`merge-bot-pull-request.yml`](./.github/workflows/merge-bot-pull-request.yml) is a thin caller and the job graph is the hub's `merge-bot-task.yml`, so the token is minted there rather than here and this repository passes only the two App secrets. The built-in `GITHUB_TOKEN` will not do: its merge commits do not trigger the downstream `publish-release` push, and on a Dependabot PR it is read-only. Any workflow needing an App token generates one with `actions/create-github-app-token`, never a hard-coded value or a PAT.
- **PyPI publishing is keyless OIDC Trusted Publishing, so there is no API token.** Registration is on PyPI as a trusted publisher for this repository plus workflow, alongside a `pypi` deployment environment restricted to `main` and `develop`.
- With no "Require approvals" on `develop` or `main`, bot PRs auto-merge as soon as the required check is green. If approvals are ever turned on, both `ptr727-codegen[bot]` and `dependabot[bot]` need to be on the bypass list.
- **Local credentials on disk** are limited to `.env.test`, covered under "Backup and Recovery" above.

## Local Rule Extensions

Rules that apply in this repository on top of the carried fleet rules. Each one is here because it is specific to this library, not because it disagrees with the fleet.

### Supported Platforms

Development runs cross-platform on Linux, macOS, and Windows, which is the fleet default in [`GOVERNANCE.md`](./GOVERNANCE.md) "Supported Development Platforms" rather than a narrowing. The `uv run` toolchain behaves identically on every OS and the dev loop has no shell scripts. The consuming [`homeassistant-purpleair`](https://github.com/ptr727/homeassistant-purpleair) integration is Linux-only because Home Assistant Core does not run natively on Windows, and that constraint does not apply to this library.

### Release and Versioning Facts

The version is derived by [Nerdbank.GitVersioning](https://github.com/dotnet/Nerdbank.GitVersioning) (NBGV) from [`version.json`](./version.json) and git history, so nothing in the committed working tree carries the real version number.

- [`version.json`](./version.json) holds the SemVer base `1.0` (major.minor), the `publicReleaseRefSpec` regex matching `^refs/heads/main$`, and `versionHeightOffset: -1`. NBGV takes the git commit height plus that offset as the patch component, so the patch is the height minus one. On any ref not matching `publicReleaseRefSpec` NBGV appends a `-g{sha}` prerelease segment. So `main` produces clean SemVer such as `1.0.5`, and `develop` produces prereleases such as `1.0.5-g1a2b3c4`.
- Bump the base `version` field manually only when opening a new major or minor series. NBGV handles the patch component automatically.
- [`src/aiopurpleair/_version.py`](./src/aiopurpleair/_version.py) carries a placeholder `__version__`, the single source hatchling reads. **Do not hand-edit it to a real version.** The release build, this repository's [`build-pypi`](./.github/actions/build-pypi/action.yml) hook run by the hub's `build-release-task.yml`, `sed`s the NBGV-computed PEP 440 version into it on the runner before `uv build`, so the published wheel carries the real version while git stays clean. That version is the release tag's `X.Y.Z`, and the hook exists to keep it so, since the hub's own PyPI default would publish a four-part version the tag never matches (ptr727/ProjectTemplate#1521). On `develop` the build appends `.dev0`, marking a prerelease. It is not guaranteed to sort above the latest `main` release, so install it by its exact PyPI version, not its release tag, as `pip install ptr727-aiopurpleair==X.Y.Z.dev0` rather than through `pip install --pre ptr727-aiopurpleair` (#111).

### Review and Merge Preconditions

[`GOVERNANCE.md`](./GOVERNANCE.md) "PR Review Etiquette" carries the fleet's review loop and merge gate whole, and this repository now follows it without exception. **A human merge never auto-cuts a release here.** Publishing happens on a code-merge to `main` by an allowlisted bot (`ptr727-codegen[bot]` or `dependabot[bot]`), or on a deliberate dispatch, and the decision has one definition in the hub's `publish-plan-task.yml` that every publisher job gates on.

**Your own merge does not release, and an allowlisted bot's can.** A merge you make to `main` reaches [`publish-release.yml`](./.github/workflows/publish-release.yml)'s push trigger, and the `plan` job then returns `publish=false` and emits a `::warning::` naming the actor, so nothing is built or uploaded. The allowlist is exactly `ptr727-codegen[bot]` and `dependabot[bot]`, so any other identity, a new App or a renamed one included, takes that same non-publishing branch. A merge to `main` by one of those two that touches a shipped path (`src/aiopurpleair/**`, `pyproject.toml`, `version.json`, `uv.lock`) does publish a stable release, which is how a Dependabot bump reaches PyPI without a human step. Everything else is a deliberate dispatch. Never trigger a `workflow_dispatch` publish without explicit maintainer instruction.

### Release-Train Invariants

When reviewing a pull request that touches [`.github/workflows/`](./.github/workflows/) or the release configuration, check the change against these invariants. Each one is intentional and was reached after a real failure mode, so flag any drift and escalate rather than implementing a relaxation.

- **The publish gate is the same validate suite CI runs.** [`publish-release.yml`](./.github/workflows/publish-release.yml)'s `publish-pypi` job `needs:` the `validate` job, which reuses the identical hub `validate-task.yml` pin (lint, the 3.13/3.14 pytest matrix, and this repository's `pyright` hook) that [`test-pull-request.yml`](./.github/workflows/test-pull-request.yml) runs. The one step that differs is the prose gate, guarded on `github.event.pull_request` and so skipped on the publisher's push or dispatch. Reject any change that lets the publish path skip validation, or that forks publish-time validation into a weaker copy. **Since the task is no longer carried here, the pin is what makes them one definition**, so the two `uses:` lines carry the same SHA or the invariant is broken. Reject a change that advances one without the other, Dependabot's bump included, and note that a bump landing on only one is the shape to watch for. The release chain is held the same way: [`test-pull-request.yml`](./.github/workflows/test-pull-request.yml)'s `smoke-build` and [`publish-release.yml`](./.github/workflows/publish-release.yml)'s `publish` both reach the hub's `build-release-task.yml`, and the two `uses:` lines carry one SHA, so the build a pull request proves is the build a release runs.
- **The package version is the release tag's `X.Y.Z`, which is what the `build-pypi` hook is for.** [`.github/actions/build-pypi`](./.github/actions/build-pypi/action.yml) replaces the hub's `pypi-build-default`, which would stamp NBGV's four-part `AssemblyFileVersion` and publish a version the tag never matches, and it also uploads the wheel + sdist as the GitHub release's asset. Reject a change that deletes the hook to fall back to the hub default, or that passes `pypi_version_file` to the hub task, which only that default reads, until ptr727/ProjectTemplate#1521 settles the default's version shape. PyPI versions are immutable, so a four-part version published once stays on PyPI.
- **The `plan` job is the release gate, and every publisher job gates on it.** [`publish-release.yml`](./.github/workflows/publish-release.yml)'s first job calls the hub's `publish-plan-task.yml` at a pinned SHA, and `validate` and `publish` both carry `needs.plan.outputs.publish == 'true'`. Reject a change that removes the gate, that lets a job run without it, or that replaces the pinned reference with a floating one. A human merge must never auto-cut a release.
- **Publishing is a paths-filtered push to `main` plus dispatch, and the paths list is the shipped surface.** The publisher triggers on `push` to `main` only, filtered to `src/aiopurpleair/**`, `pyproject.toml`, `version.json`, and `uv.lock`, plus `workflow_dispatch`. `uv.lock` is deliberately in the list: a PyPI version cannot be re-pushed, so a dependency bump must republish to keep the package's declared dependencies current. Reject a change that drops `uv.lock` from the filter, which re-opens the stale-dependency window, that broadens the filter so docs, test, or workflow-only changes start publishing, or that re-adds `develop` to the push branches, since a prerelease is a deliberate dispatch here.
- **Publishing is keyless OIDC Trusted Publishing, with no stored token.** The `publish-pypi` job runs in the `pypi` environment with `permissions: id-token: write` and uploads via `pypa/gh-action-pypi-publish` over OIDC. Reject any change that adds a `password:` or `PYPI_API_TOKEN` secret to the publish step. The Trusted Publisher registration plus the `pypi` environment's branch restriction is the whole trust chain.
- **One required check gates merge, named verbatim.** The single aggregator job is exactly `Check pull request workflow status job`, and its name is the `context:` the **live** branch rulesets require. That `context:` is applied from the hub's payloads, and this repository carries no copy of them, so nothing a pull request here can edit moves it. **Reject a rename that arrives as a repository-local change only.** An unmatched rename leaves every pull request unmergeable, this one included: CI runs but the required check never resolves, so the change that broke the gate cannot be merged or reverted through the gate. The string is fleet-wide, so moving it starts at the hub and reaches this repository last, and [`GOVERNANCE.md`](./GOVERNANCE.md) "Workflow YAML Conventions" enumerates the hub-side surfaces that move together. The only local precondition worth restating is the one a reviewer here can actually check: the live rulesets already require the new string. Confirm that before approving the workflow rename, in POSIX shell (on Windows, WSL2 or Git Bash):

  ```sh
  for id in $(gh api --paginate 'repos/ptr727/aiopurpleair/rulesets?per_page=100' --jq '.[].id'); do
    gh api "repos/ptr727/aiopurpleair/rulesets/$id" \
      --jq '.name + ": " + ([.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context] | join(", "))'
  done
  ```

- **Dependabot auto-merges every tier, and the required checks are the gate rather than the bump magnitude.** The [merge bot](./.github/workflows/merge-bot-pull-request.yml) enables auto-merge on every Dependabot pull request regardless of semver level, **semver-major included**. A bump that breaks a covered path reds the required checks and stays open, rather than every major being held for human review. The merge step now lives in the hub task this file calls, so there is no local step to filter and a reintroduced tier filter would arrive as a hub change or as a `with:` input here. Reject either: the filter was dropped deliberately so that a green suite, not the bump magnitude, decides the merge.

### Commit Message Examples

[`GOVERNANCE.md`](./GOVERNANCE.md) "Pull Request Title and Commit Message Conventions" carries the rules. These are worked examples in this repository's own subject matter.

```text
Add the GET /v1/organization endpoint
Map InvalidDataReadKeyError to HTTP 400 read-key failures
Return tz-aware UTC datetimes from the timestamp validator
Bump aiohttp from 3.11.0 to 3.12.0
Clarify the connection-pooling example in README
```
