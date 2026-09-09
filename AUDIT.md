# AUDIT.md

How an agent audits **this repository** against the fleet ground truth and reports drift. The audit is **read-only**: it produces a report (an issue, a pull request comment, or a scratch file) and never edits the repository. Converging is a separate phase, in section 6.

The verdict vocabulary is fixed in section 5 below: **operational / not operational**, **N/A**, and **defect**, each judged against the applicable/absent rule. Do not invent a parallel scheme.

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

- **`python` + `pypi`**, `workflowModel: release`, `consumerModel: pull`. Publishing is **two-phase**: a human merge never auto-cuts a release, and a release is a merge to `main` by an allowlisted bot (`ptr727-codegen[bot]` or `dependabot[bot]`) or a deliberate `workflow_dispatch`. The fleet registry still records `releaseTrigger: publish-on-merge` and is owed an update to `two-phase`, so treat the pipeline rather than that field as the current truth until it is corrected.
- Checks governing absent constructs (a .NET build, an image registry, a transfer artifact) are **N/A**. Record them as N/A and exclude them from the verdict. N/A is never a defect.

## 3. Dimensions

Evaluate each applicable check at two tiers: **letter** (the exact file, section, or config is present) and **intent** (an equivalent outcome holds even where the form differs).

- **python** - ruff, mypy, and pyright present and canonical in [`pyproject.toml`][pyproject]. A standalone `.ruff.toml` or `mypy.ini` is a drift finding. The pytest coverage gate is 100% on the mocked suite, above the fleet's report-only default, and that is deliberate.
- **branch-model** - `main` and `develop` both exist and are protected, and the live rulesets match the **hub's** ruleset payloads by normalized diff, which is what the section 4 command compares against. This repository keeps no ruleset payloads of its own, so the hub's are the single source and there is no second copy to drift.
- **repo-setup** - every required secret is configured, no forbidden secret is present, and the `pypi` deployment environment restricts publishing to the release branches. The required set is `CODEGEN_APP_CLIENT_ID`, `CODEGEN_APP_PRIVATE_KEY`, and `CODECOV_TOKEN`, each in **both** the Actions and Dependabot stores, since a Dependabot-triggered run reads the Dependabot store rather than Actions secrets. A missing `CODECOV_TOKEN` is a **defect** at this dimension even though the upload step itself is `continue-on-error`, so its absence degrades coverage reporting rather than reddening CI, per [`OPERATIONS.md`][operations] "Configuration Layout". PyPI publishing is keyless OIDC, so a `PYPI_API_TOKEN` in either store is a **defect**, not an omission. The environment check is section 4's, and it is the one part of this dimension no script covers.
- **linter-parity** - one config per linter ([`.markdownlint-cli2.jsonc`][markdownlint], [`cspell.json`][cspell], ruff/mypy/pyright in [`pyproject.toml`][pyproject], [`.editorconfig`][editorconfig]) drives the editor extension, the CLI, and CI alike, and CI runs each.
- **recurring-violations** (always run), covering comments concise and non-narrative, US spelling, and line endings per [`.editorconfig`][editorconfig], verified with `git ls-files --eol`. Each is a grep-able check.
- **workflows** - run [`WORKFLOW.md`][workflow]'s methodology against [`.github/workflows/`][workflows]: the static audit of each applicable guarantee with `file:line` citations, plus the trace scenarios. The release-train invariants in [`OPERATIONS.md`][operations] are part of this dimension, not separate from it.

## 4. Validate Settings, Rulesets, Secrets, and the Publish Environment

Settings, labels, and the ruleset payloads are applied by the hub-hosted `repo-config/configure.sh`. Run it **from a hub checkout at `main`**, which is the copy that takes the repository and model as arguments, rather than from any copy carried in this repository:

```shell
# cwd is a hub checkout of github.com/ptr727/ProjectTemplate, at main
repo-config/configure.sh check ptr727/aiopurpleair release
```

`check` reads and never writes, which is what makes it usable here. Its `apply` counterpart writes to the live repository, so it is a converge action rather than a measurement and belongs to section 6.

That command checks the rulesets, the general settings, the security features, and the labels. **It does not check secrets, and it does not check the `pypi` deployment environment.** Both of the checks below are therefore part of this section rather than optional extras, because the command above reports a match whether or not either one holds.

Confirm secret **names** directly, since values are not readable:

```shell
gh api --paginate repos/ptr727/aiopurpleair/actions/secrets --jq '.secrets[].name'
gh api --paginate repos/ptr727/aiopurpleair/dependabot/secrets --jq '.secrets[].name'
```

Expect `CODEGEN_APP_CLIENT_ID`, `CODEGEN_APP_PRIVATE_KEY`, and `CODECOV_TOKEN` in **both** stores. A Dependabot-triggered run reads the Dependabot store rather than Actions secrets, which is why the Codecov token is copied there too. Expect none of `CODEGEN_APP_ID`, `PYPI_API_TOKEN`, or `TWINE_PASSWORD` in either store: the first is the deprecated App input, and the other two would contradict keyless OIDC publishing. `spec/audit.py aiopurpleair`, run from the same hub checkout, asserts exactly this set from the hub's `spec/secrets.json`, so a disagreement between this paragraph and that run is a defect in this paragraph.

Confirm the `pypi` deployment environment by hand. It is the GitHub half of the OIDC publish gate, it is what stops a dispatch from an unintended ref minting a publish token, and **no script checks it**: the hub's script manages no environment at all, and the carried script that once asserted this was retired with the rest of the local repository configuration. **This paragraph is the intended state**, since no payload records it any more:

```shell
gh api repos/ptr727/aiopurpleair/environments/pypi --jq '.deployment_branch_policy'
gh api --paginate repos/ptr727/aiopurpleair/environments/pypi/deployment-branch-policies --jq '.branch_policies[].name'
```

The policy must read `custom_branch_policies: true` and `protected_branches: false`, and the branch list must be exactly `develop` and `main`. Record the result at the `repo-setup` dimension, tiered as section 5 requires. A **missing environment**, or any branch beyond `develop` and `main`, is a **defect**: letter and intent both fail, since a ref that should not publish can. The `protected_branches` preset is a **letter** miss whose intent may still hold, because only `main` and `develop` are protected today, so it is a drift finding that turns into a defect the moment a third branch is protected.

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
- Settings, labels, and rulesets are the exception to the pull-request rule, since they are live configuration rather than tracked files. Converge them by running `repo-config/configure.sh apply ptr727/aiopurpleair release` from a hub checkout at `main`, then re-run the `check` in section 4 to confirm the drift is gone. This writes to the live repository, which is why it appears here and not in the measurement section.

<!-- Repo -->

[cspell]: ./cspell.json
[editorconfig]: ./.editorconfig
[governance]: ./GOVERNANCE.md
[governance-branching-model]: ./GOVERNANCE.md#branching-model
[governance-pr-review]: ./GOVERNANCE.md#pr-review-etiquette
[markdownlint]: ./.markdownlint-cli2.jsonc
[operations]: ./OPERATIONS.md
[pyproject]: ./pyproject.toml
[workflow]: ./WORKFLOW.md
[workflows]: ./.github/workflows/
