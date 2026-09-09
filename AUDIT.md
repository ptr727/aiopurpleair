# AUDIT.md

How an agent audits **this repository** against the fleet ground truth and reports drift. The audit is **read-only**: it produces a report (an issue, a pull request comment, or a scratch file) and never edits the repository. Converging is a separate phase, in section 6.

The verdict vocabulary is [`WORKFLOW.md`][workflow]'s: **operational / not operational**, **N/A**, **defect**, and the applicable/absent rule. Do not invent a parallel scheme.

**The deterministic half is mechanized, and it is hub-hosted rather than carried here.** Run it from a checkout of the hub, `github.com/ptr727/ProjectTemplate`, fetched immediately before it is read, per [`GOVERNANCE.md`][governance] "Hub-Hosted Tooling". Verify the host first, since a tool below its floor answers `--version`, looks healthy, and produces a wrong answer.

```shell
python3 scripts/host_gate.py --repo <path-to-this-checkout>   # from a hub checkout
python3 spec/audit.py aiopurpleair                            # the deterministic findings, read at main
python3 spec/audit.py --issue aiopurpleair                    # audits again and renders that run as an issue
```

A finding is a snapshot. Quote the run stamp (`audit run <UTC> | hub <sha>`) in anything derived from it, and re-run before acting on a finding written earlier.

## 1. Scope and Ground-Truth Branch

Read the **`main` branch** as ground truth: `main` is the released, gated state. Read `develop` only to detect divergence, and treat a stale or diverged `develop` as a **drift finding** rather than as the truth.

## 2. Profile

This repository's profile is fixed, so no classification step is needed:

- **`python` + `pypi`**, `workflowModel: release`, `releaseTrigger: publish-on-merge`, `consumerModel: pull`.
- Checks governing absent constructs (a .NET build, an image registry, a transfer artifact) are **N/A**. Record them as N/A and exclude them from the verdict. N/A is never a defect.

## 3. Dimensions

Evaluate each applicable check at two tiers: **letter** (the exact file, section, or config is present) and **intent** (an equivalent outcome holds even where the form differs).

- **python** - ruff, mypy, and pyright present and canonical in [`pyproject.toml`][pyproject]. A standalone `.ruff.toml` or `mypy.ini` is a drift finding. The pytest coverage gate is 100% on the mocked suite, above the fleet's report-only default, and that is deliberate.
- **branch-model** - `main` and `develop` both exist and are protected, and the live rulesets match the committed payloads in [`repo-config/`][repo-config] by normalized diff (section 4).
- **repo-setup** - every required secret is configured and no forbidden secret is present. The required set is `CODECOV_TOKEN` plus the `CODEGEN_APP_CLIENT_ID` and `CODEGEN_APP_PRIVATE_KEY` pair in **both** the Actions and Dependabot stores, per [`OPERATIONS.md`][operations] "Configuration Layout". PyPI publishing is keyless OIDC, so a `PYPI_API_TOKEN` in either store is a **defect**, not an omission.
- **linter-parity** - one config per linter ([`.markdownlint-cli2.jsonc`][markdownlint], [`cspell.json`][cspell], ruff/mypy/pyright in [`pyproject.toml`][pyproject], [`.editorconfig`][editorconfig]) drives the editor extension, the CLI, and CI alike, and CI runs each.
- **recurring-violations** (always run), covering comments concise and non-narrative, US spelling, and line endings per [`.editorconfig`][editorconfig], verified with `git ls-files --eol`. Each is a grep-able check.
- **workflows** - run [`WORKFLOW.md`][workflow]'s methodology against [`.github/workflows/`][workflows]: the static audit of each applicable guarantee with `file:line` citations, plus the trace scenarios. The release-train invariants in [`OPERATIONS.md`][operations] are part of this dimension, not separate from it.

## 4. Validate Settings, Rulesets, and Secrets

Settings and the ruleset payloads are applied by the hub-hosted `repo-config/configure.sh`, run from a hub checkout at `main` rather than from any copy carried here:

```shell
repo-config/configure.sh check ptr727/aiopurpleair release
repo-config/configure.sh apply ptr727/aiopurpleair release
```

Confirm secret **names** directly, since values are not readable:

```shell
gh api repos/ptr727/aiopurpleair/actions/secrets --jq '.secrets[].name'
gh api repos/ptr727/aiopurpleair/dependabot/secrets --jq '.secrets[].name'
```

`bypass_actors` sits deliberately outside any compared subset: who may bypass a ruleset is a human decision taken in the UI, no payload declares one, and comparing it would report a finding against every ruleset that has any bypass actor at all.

## 5. Verdict Model

Per dimension, record `operational | not-operational | N/A`, each with a letter and an intent verdict:

- A letter miss with intent satisfied is a **drift finding**: an equivalent outcome in a non-standard form, worth fixing but not a break.
- A letter and intent miss together is a **defect**, and the repository is not operational.

The repository is **operational** only if every applicable check passes. A single applicable defect makes it not operational. N/A items are excluded and never counted as failures.

## 6. Converge, and Apply the Fixes

The audit is read-only. Converging is the follow-on phase, and the hub's `RESYNC.md` owns the order the remedies are applied in.

- Apply fixes via a **pull request** per the branch model (feature branch into `develop`, promotion into `main`) as described in [`GOVERNANCE.md`][governance-branching-model], never a direct push to a protected branch.
- Drive the review loop to green, addressing and resolving every thread, per [`GOVERNANCE.md`][governance-pr-review] "PR Review Etiquette".
- **Merge only with explicit maintainer permission.** The agent drives to green and stops.
- One focused pull request per drift class, cross-referencing the finding it closes.

<!-- Repo -->

[cspell]: ./cspell.json
[editorconfig]: ./.editorconfig
[governance]: ./GOVERNANCE.md
[governance-branching-model]: ./GOVERNANCE.md#branching-model
[governance-pr-review]: ./GOVERNANCE.md#pr-review-etiquette
[markdownlint]: ./.markdownlint-cli2.jsonc
[operations]: ./OPERATIONS.md
[pyproject]: ./pyproject.toml
[repo-config]: ./repo-config/
[workflow]: ./WORKFLOW.md
[workflows]: ./.github/workflows/
