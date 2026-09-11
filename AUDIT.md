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

- **`python` + `pypi`**, `workflowModel: release`, `consumerModel: pull`. Publishing is **two-phase**: a human merge never auto-cuts a release, and a release is a merge to `main` by an allowlisted bot (`ptr727-codegen[bot]` or `dependabot[bot]`) or a deliberate `workflow_dispatch`. The fleet registry records `releaseTrigger: two-phase`, which agrees with the pipeline.
- Checks governing absent constructs (a .NET build, an image registry, a transfer artifact) are **N/A**. Record them as N/A and exclude them from the verdict. N/A is never a defect.

## 3. Dimensions

Evaluate each applicable check at two tiers: **letter** (the exact file, section, or config is present) and **intent** (an equivalent outcome holds even where the form differs).

- **python** - ruff, mypy, and pyright present and canonical in [`pyproject.toml`][pyproject]. A standalone `.ruff.toml` or `mypy.ini` is a drift finding. The pytest coverage gate is 100% on the mocked suite, above the fleet's report-only default, and that is deliberate.
- **branch-model** - `main` and `develop` both exist and are protected, and the live rulesets match the **hub's** ruleset payloads by normalized diff, which is what the section 4 command compares against. This repository keeps no ruleset payloads of its own, so the hub's are the single source and there is no second copy to drift.
- **repo-setup** - every required secret is configured, no forbidden secret is present, and the `pypi` deployment environment restricts publishing to the release branches. The required set is `CODEGEN_APP_CLIENT_ID`, `CODEGEN_APP_PRIVATE_KEY`, and `CODECOV_TOKEN`, each in **both** the Actions and Dependabot stores, since a Dependabot-triggered run reads the Dependabot store rather than Actions secrets. A missing `CODECOV_TOKEN` is a **defect** at this dimension even though the upload step itself is `continue-on-error`, so its absence degrades coverage reporting rather than reddening CI, per [`OPERATIONS.md`][operations] "Configuration Layout". PyPI publishing is keyless OIDC, so a `PYPI_API_TOKEN` in either store is a **defect**, not an omission. The environment check is section 4's, and `configure.sh check` covers it against the registry's declaration.
- **linter-parity** - one config per linter ([`.markdownlint-cli2.jsonc`][markdownlint], [`cspell.json`][cspell], ruff/mypy/pyright in [`pyproject.toml`][pyproject], [`.editorconfig`][editorconfig]) drives the editor extension, the CLI, and CI alike, and CI runs each.
- **recurring-violations** (always run), covering comments concise and non-narrative, US spelling, and line endings per [`.editorconfig`][editorconfig], verified with `git ls-files --eol`. Each is a grep-able check.
- **workflows** - run [`WORKFLOW.md`][workflow]'s methodology against [`.github/workflows/`][workflows]: the static audit of each applicable guarantee with `file:line` citations, plus the trace scenarios. The release-train invariants in [`OPERATIONS.md`][operations] are part of this dimension, not separate from it.

## 4. Validate Settings, Rulesets, Secrets, and the Publish Environment

Settings, labels, and the ruleset payloads are the hub's, applied by its `repo-config/configure.sh` against its own payloads. **This repository carries no `repo-config/` directory**, which is the fleet's model rather than an omission, so run the command from a hub checkout at `main`, passing this repository and its model as arguments:

```shell
# cwd is a hub checkout of github.com/ptr727/ProjectTemplate, at main
repo-config/configure.sh check ptr727/aiopurpleair release
```

`check` reads and never writes, which is what makes it usable here. Its `apply` counterpart writes to the live repository, so it is a converge action rather than a measurement and belongs to section 6.

That command checks the rulesets, the general settings, the security features, the labels, and the deployment environments the fleet registry declares for this repository, which is the `pypi` one. **It does not check secrets**, so the secret check below is part of this section rather than an optional extra, because the command above reports a match whether or not it holds.

Confirm secret **names** directly, since values are not readable:

```shell
gh api --paginate repos/ptr727/aiopurpleair/actions/secrets --jq '.secrets[].name'
gh api --paginate repos/ptr727/aiopurpleair/dependabot/secrets --jq '.secrets[].name'
```

Expect `CODEGEN_APP_CLIENT_ID`, `CODEGEN_APP_PRIVATE_KEY`, and `CODECOV_TOKEN` in **both** stores. A Dependabot-triggered run reads the Dependabot store rather than Actions secrets, which is why the Codecov token is copied there too. Expect none of `CODEGEN_APP_ID`, `PYPI_API_TOKEN`, or `TWINE_PASSWORD` in either store: the first is the deprecated App input, and the other two would contradict keyless OIDC publishing. `spec/audit.py aiopurpleair`, run from the same hub checkout, asserts exactly this set from the hub's `spec/secrets.json`, so a disagreement between this paragraph and that run is a defect in this paragraph.

The `pypi` deployment environment is the GitHub half of the OIDC publish gate, and it is what stops a dispatch from an unintended ref minting a publish token. **The `check` above now asserts it**, against the `environments` block the fleet registry declares for this repository, so this is no longer a by-hand step: it confirms the environment exists, that its deployment-branch policy is the declared form, and that a `custom` policy allows exactly the declared branches, so a branch added by hand reads as drift. The registry is where the intended state now lives. An environment the registry declares nothing about is reported rather than asserted, so the `copilot` environment GitHub creates on its own prints as a note rather than as a finding. The commands below remain useful for reading the live values directly when a `check` finding needs to be seen rather than trusted:

```shell
gh api repos/ptr727/aiopurpleair/environments/pypi --jq '.deployment_branch_policy'
gh api --paginate repos/ptr727/aiopurpleair/environments/pypi/deployment-branch-policies --jq '.branch_policies[].name'
```

The policy must read `custom_branch_policies: true` and `protected_branches: false`, and the branch list must be exactly `develop` and `main`, which is what the registry declares. Record the result at the `repo-setup` dimension, tiered as section 5 requires. A **missing environment**, or any branch beyond `develop` and `main`, is a **defect**: letter and intent both fail, since a ref that should not publish can. A `protected_branches` preset is a **defect** rather than a drift finding, and the script fails on it outright. Letter and intent miss together: the fleet configures protection through rulesets, and this repository has no classic branch protection at all, so `gh api repos/ptr727/aiopurpleair/branches/main/protection` returns `404 Branch not protected`. Under that preset no branch would qualify, so the gate this environment exists to express would not exist either.

**Neither command reads an environment's own secret and variable store.** That is a scoping decision about what the hub's script owns rather than a limit the API imposes, since a secret's name, and a variable's name and value, are all enumerable. For this repository that store is empty, which is a live fact rather than an inference from `spec/secrets.json`, whose `requires` and `stores` describe the repository's own Actions and Dependabot stores rather than an environment's: `environments/pypi/secrets` and `environments/pypi/variables` each return `total_count: 0`, and publishing is keyless OIDC. So what a publish needs from this environment is its existence and its branch policy, and the `check` above asserts both. What the check does not read is the environment's `protection_rules` array, so a required-reviewer or wait-timer rule added by hand would gate every deployment here and go unreported. Today `pypi` carries only its `branch_policy` rule.

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
- Settings, labels, and rulesets are the exception to the pull-request rule, since they are live configuration rather than tracked files. Converge them by running `repo-config/configure.sh apply ptr727/aiopurpleair release` from a hub checkout at `main`, then re-run the `check` in section 4 to confirm the drift is gone. This writes to the live repository, which is why it appears here and not in the measurement section. **The `pypi` environment is the exception inside that exception.** `apply` carries no environment write, so an environment finding is converged by hand, in the GitHub UI or through the `gh api` environment endpoints, and the `check` re-run to confirm. Running `apply` against one changes nothing and says nothing either, since it touches no environment endpoint at all and exits clean: the re-run `check` is what still fails.

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
