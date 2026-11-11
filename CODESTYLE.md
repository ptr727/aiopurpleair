# Code Style and Formatting Rules

This is the single code-style guide for the repo. The **General** section applies to every language. The **Python** language section is self-contained: it is the style guide for the Python code this repo ships.

Cross-cutting *process* rules (PR titles, branching, US English, markdown style, comments philosophy, PR review etiquette) live in [GOVERNANCE.md](./GOVERNANCE.md) and are not repeated here.

## General

These rules apply to every language in the repo.

### Tooling Names and Casing

Use each tool's official casing in task labels, docs, and prose - `uv`, `ruff`, `mypy`, `pyright`, `pytest`, `syrupy`, `hatchling`, `NBGV`. Don't invent personal variants.

### Clean-Compile Verification

Each language defines a **clean-compile** verification - the combination of build, formatter, linter, and type-check tools that must report clean before a commit. The concrete commands live in the language section below.

- **Run it after every code change.** The relevant language's clean-compile must pass before you commit; CI runs the same checks as a backstop.
- **The documented command sequence is the canonical spec** - its exact arguments and strictness. No shortcuts and no more-lenient options (for example, never drop `ruff format --check`'s verify mode or loosen a lint/type-check severity).
- **A local commit/pre-commit gate is the repo's choice.** No hook runner is mandated, but that is not a recommendation against commit gates. CI is the authoritative backstop regardless; a local gate (for example `pre-commit` running `ruff`, `mypy`, and `pyright`) is an additive convenience a repo may wire and keep - this repo wires none today.

### Analyzer Diagnostics and Suppressions

- **A new port is not a license to silence diagnostics.** Brownfield / just-ported status never justifies relaxing analyzer or linter severities or muting newly surfaced warnings - fix them.
- **Suppress only genuine false-positives or deliberate, documented exceptions**, always at the **narrowest scope that fits**, in this order of preference:
  1. An **in-code annotation on the specific symbol**, with a justification (the language's comment form), never a blanket pragma spanning a region.
  2. The **project's local config** (`pyproject.toml`) when the exception is project-wide and genuinely applicable.
- **Never blanket-relax a batch of rules** to get code to build. The per-language mechanics are in the language section.

### Operations and Failure Messages

- **Let the real operation be the check, not a prediction of it.** Attempt the read, the write, or the call itself, and turn its failure into a clean refusal. Do not probe first with an existence, type, or permission test. Where the operation could block or succeed on the wrong kind of target, judge what it opened instead. A probe is a second model of the operation. It misjudges each case its author did not foresee, such as a dangling link, a link loop, or a platform's own permission model. The operation cannot disagree with itself.
- **Classify a subprocess failure by which command failed and the status code it reports, never by the prose of its message.** That prose varies by tool version and locale, and a status code's value does not, even one printed inside the message. A printed code is read by the notation that marks it, and a match finding none counts as an unexpected failure. Where one command's status code cannot separate the failures its caller handles differently, give each expected failure its own real operation. Where no such operation exists, treat the failure as unexpected. A test asserting a script's output, such as the refusal "Command-Line Arguments" requires, verifies that output rather than classifying a failure.
- **A failure message states the error, the path or other target, and the remedy, and claims nothing about the state the failure left.** The error the operation raised is the one fact the code holds at that point. A description of what the failure left behind is a prediction. It reads false once an unforeseen state reaches the message, such as a file written in full that then fails to close. A remedy such as "fix what it names, then re-run" needs no such claim.

### Parsing Structured Formats

- **A program reading a structured format uses a maintained parser rather than a hand-written one, where a field-tested parser exists for the runtime in use.** That covers YAML, Markdown, TOML, JSON, a programming language's comments or strings, and a shell command line. The standard library's own parsers count, such as Python's `json`, `tomllib`, `ast`, `tokenize`, and `html.parser`. A hand-written reader converges on the format's full grammar one review finding at a time, and every script that grows one pays that cost again.

### Command-Line Arguments

A command-line script is one a person or an agent runs by name. A hook its host runs, taking its input from that host rather than from a command line, is not one.

- **Every command-line script answers `--help` and `-h`** with the same text on stdout, then exits 0, changing nothing. That text opens on a usage line naming the script. An agent learns a script's interface by asking it, so a script that reads `--help` as an input acts in a way nobody predicted. A PowerShell script declaring its own parameters answers `-Help` and `-h` instead, from a `-Help` switch carrying an `h` alias. That form follows PowerShell's own parameter convention, so such a script owes no answer to a literal `--help`. A wrapper that forwards its arguments to another script answers whatever that script answers.
- **An argument the script does not recognize is refused**, with a non-zero exit before any read or write. The refusal names it as an unknown or unrecognized option, argument, flag, or parameter, and PowerShell's own refusal of a parameter it cannot bind counts. So a PowerShell script declaring its own parameters refuses a literal `--help` like any other unrecognized argument. Where no parameter takes the remaining arguments, the binder's refusal does that. A script with such a parameter refuses a dash-prefixed leftover itself. An unrecognized first argument is never taken as a default mode or as a target.

### Script and Utility File Names

| Type | Rule | Basis |
| --- | --- | --- |
| Python `.py` | lowercase snake_case | [PEP 8][pep8-names-link] module naming. A hyphenated module also cannot be named in an `import` statement |
| Shell `.sh` and PowerShell `.ps1` | lowercase-hyphenated | The Linux command convention. A cross-platform pair keeps one name, `sync-tools.sh` beside `sync-tools.ps1` |
| Windows batch `.cmd` and `.bat` | lowercase-hyphenated | The same convention as shell and PowerShell. A shim that puts a command on `PATH` takes the name of the command it provides, `sync-tools.cmd` launching `sync-tools.ps1` |
| PowerShell functions inside a `.ps1` | Verb-Noun with an approved verb (`Get-Verb`) | PSScriptAnalyzer `PSUseApprovedVerbs`. This is a command rule, not a file rule |
| Env and secret files, tracked or not | lowercase fields joined by `_`, with no dot but the extension | `mail_relay.env`, `db_root_password`, `app_web-01_prod.env` |
| Env variable names and CI secret names | UPPER_SNAKE_CASE | The POSIX and GitHub convention |

- **Installed commands.** An executable or launcher on `PATH` or in a system slot (systemd, cron, run-parts, motd) is named as a command, whatever its language. That name is lowercase-hyphenated. It carries no extension unless the platform needs one to run it, such as `.cmd` or `.ps1` on Windows.
- **Wrapper exemption.** A thin launcher whose only job is to run a Python tool keeps that tool's stem, so `fetch_report.py`, `fetch_report.sh`, and `fetch_report.ps1` stay grouped together. It covers only a launcher run by its path. A launcher installed onto `PATH` or into a system slot is an installed command instead, such as `fetch-report` rather than `fetch_report`.
- **Env and secret file names reach every file a repository names.** That covers a tracked file or template and a secret file mounted into a container. It also covers a host-side file the repository's docs or scripts name, such as an `ENV_FILE` path or a compose `env_file`.
- **`_` joins the fields of an env or secret file name, and each field keeps its own valid form.** A host name field stays verbatim, hyphens included, so `app_web-01_prod.env` is right and `app_web_01_prod.env` and `app.web-01.prod.env` are not. That field is a short name, the host's first DNS label (`web-01`) or a logical role name (`vps-staging`), and never a fully qualified one. Either way it takes the DNS label form, so its own words join with `-`. A repository name field takes the repository's name in lower case, hyphens kept, as in `github_example-repo_codecov_token`. GitHub allows `_` and `.` in a repository name too. A repository whose name carries either cannot form this field, so it may name no env or secret file that needs one. In every other field a hyphen never joins words, since that is the job of `_`. A host name label can carry `-` and never `_`, so every `_` is a separator and the name splits back into its fields. The name is lowercase, carries no dot but its extension, and starts and ends with a letter or digit. A tracked template's `.example` suffix is not counted as a dot.
- **A variable name converts separately.** An env variable or CI secret name allows only `A-Z`, `0-9`, and `_`. Where a field becomes one, the hyphen becomes `_` there, as in `APP_WEB_01_PROD_TOKEN`, and never in the file name.
- **Some consumers set limits of their own.** A name used as a Docker secret stays within the 64 characters Docker allows. A name that maps to an env variable or CI secret does not start with a digit, which POSIX and GitHub both forbid.
- **Externally fixed names are exempt.** That covers Git hook names, `__init__.py`, `conftest.py`, and Pester's `.Tests.ps1` suffix, whose stem mirrors the script under test. It covers a PowerShell data file (`.psd1`) whose name a tool fixes, such as a module manifest named for its module. `PSScriptAnalyzerSettings.psd1` is another, since PSScriptAnalyzer finds it by that name. So is an env file a tool reads by a fixed name, such as `.env`, `.env.local`, or `.env.production`. An env or secret file in a `.secrets/` directory is never one, since it is read by a path the repository configures. The exemption also covers any name a platform defines.
- **Directories are out of scope.** That means directory names.

Departures, stated on purpose so a reader does not "fix" them back:

- The [Google Shell Style Guide][google-shell-link] asks for underscores in shell file names. The fleet uses hyphens instead, matching installed Linux commands.
- Microsoft's [approved verbs][ps-approved-verbs-link] govern command names. A `.ps1` run by path is a file rather than an exported command, so the file takes the shell convention and its functions take Verb-Noun.

### Markdown and Spelling

These apply repo-wide, in every directory:

1. **Markdown**: keep `.md` files clean under a standard markdownlint ruleset, with `MD013` (line-length) treated as disabled - long prose lines are intentional here (one logical paragraph per line). Fix violations at the source rather than disabling rules wholesale.
2. **Spelling**: US English throughout, in code comments, commit messages, PR descriptions, documentation, and the names this repo chooses for itself. Prefer the American form of every word that has two: *behavior*, *color*, *recognize*, *organize*, and *canceled* with one L, never their British spellings. **A name defined outside this repo is not ours to spell**, so it is written the way its definition writes it: GitHub Actions' `cancelled()` status function and the `cancelled` job result keep their two Ls, as does any API field, enum member, or config key that arrives spelled that way. Project-specific terms (`aiopurpleair`, `PurpleAir`, `aiohttp`, `pydantic`, `syrupy`, `NBGV`) are correct, not misspellings.
3. **Spelling CI scope**: The enforced CI spell-check gate covers **`README.md` and `HISTORY.md` only** - these are the files every repo visitor sees, so they must be clean. It is deliberately **not** all `**/*.md`: repos carry many markdown files full of technical terms, and gating every one of them would mean endlessly padding `cspell.json` just to keep CI green. Broad, live spell-checking across any file (source, markdown, text) is the **cspell editor extension's** job, so typos still surface to whoever is editing. A repo owner **may** widen their own CI file list, but the template ships README + HISTORY as the default; keep every surface that runs cspell - the CI workflow and any local VS Code task or one-liner the repo has - on the same file list. The list is explicit (not a glob), so a repo that ships no `HISTORY.md` (e.g. one with no changelog) must drop it from all three surfaces and gate on `README.md` alone - cspell errors on a listed file that does not exist. Markdown *linting* (item 1) stays repo-wide `**/*.md` - it does not choke on technical terms.

## Python

*This section is the style guide for the Python code this repo ships.*

This repo ships an **installable PyPI package** (`ptr727-aiopurpleair`, import package `aiopurpleair`) using a **src-layout** (`src/aiopurpleair/`), the **hatchling** build backend, and **[uv][uv]** for environment and dependency management (`uv.lock` is committed). Everything runs through `uv run`.

### Toolchain

| Tool | Role | Config |
|---|---|---|
| [uv][uv] | environment + dependency management, build driver | `pyproject.toml` `[dependency-groups]`, `uv.lock` |
| [ruff][ruff] | lint + format + import sort | `pyproject.toml` `[tool.ruff]` |
| [mypy][mypy] | strict type gate (shipped surface) | `pyproject.toml` `[tool.mypy]` |
| [pyright][pyright] | type checker (src + tests) | `pyproject.toml` `[tool.pyright]` |
| [pytest][pytest] | test runner + coverage | `pyproject.toml` `[tool.pytest.ini_options]`, `[tool.coverage.*]` |
| [syrupy][syrupy] | snapshot assertions | via pytest |

Two type checkers run, and **both are gates**. `mypy` runs `strict = true` over **`src`** only - the shipped library surface. `pyright` runs over **`src` and `tests`** (its `include`), with `strict = ["src"]` so the public surface is held to strict mode while tests stay at standard mode (fixtures, fakes, and parametrize args are commonly looser). Both must be clean.

**Tools target the 3.13 floor.** `ruff` `target-version = "py313"`, `mypy` `python_version = "3.13"`, and `pyright` `pythonVersion = "3.13"` all pin the analysis to the minimum supported interpreter, so 3.13 compatibility is statically enforced - while CI's pytest matrix exercises both **3.13 and 3.14**.

### Local Development Loop

Run from the repo root:

```sh
uv sync --all-groups          # create the venv and install runtime + dev dependencies
uv run ruff format            # apply formatting
uv run ruff check --fix       # apply safe lint autofixes
uv run ruff check             # lint (verify)
uv run ruff format --check    # format (verify)
uv run mypy src               # strict type gate, shipped surface only
uv run pyright                # type-check src + tests (strict on src)
uv run pytest                 # tests, with 100% coverage enforced
```

The Python clean-compile (see [Clean-Compile Verification](#clean-compile-verification)) is the verify set: `uv run ruff check` + `uv run ruff format --check` + `uv run mypy src` + `uv run pyright` + `uv run pytest`. Run it before committing - `ruff` alone does **not** cover `mypy` or `pyright`, both of which are CI gates. CI runs the same checks as the authoritative backstop.

### Layout

Standard src-layout - the import package lives under `src/`, is built into a wheel by hatchling, and is never imported from the source root:

```text
src/aiopurpleair/
    __init__.py            # public API re-exports (API, ...)
    _version.py            # __version__ placeholder; NBGV-stamped at build
    api.py                 # the API client
    const.py
    errors.py              # PurpleAirError hierarchy + ERROR_CODE_MAP
    py.typed               # PEP 561 typing marker
    endpoints/             # per-endpoint request helpers (sensors, organizations)
    models/                # pydantic request/response models
    helpers/               # base model, validators
    util/                  # datetime + geo helpers
tests/
    ...                    # one test module per source module; syrupy snapshots
```

### Code Style

#### Formatting and Linting

- **`ruff format` is authoritative.** Don't argue with the formatter; if it reformats your code, that's the final form. Configure formatter behavior in `pyproject.toml` `[tool.ruff.format]`, not via inline `# fmt:` directives. `docstring-code-format` is on, so code blocks inside docstrings are formatted too.
- **Run `uv run ruff format` + `uv run ruff check --fix` before committing.** Most ruff lint rules have safe autofixes; let the tool handle them. The configured rule families are `["E", "W", "F", "I", "B", "UP", "N", "SIM", "RUF"]` in `[tool.ruff.lint]`. Add new rule families project-wide rather than scattering inline `# noqa` markers.
- **`# noqa` is a last resort.** When you must use one, scope it narrowly (`# noqa: E501`, not bare `# noqa`) and add a short comment on the same line explaining why. Recurring false positives belong in `[tool.ruff.lint]` `ignore` or `per-file-ignores`, with a comment.

#### Comments

- **Inline `#` comments**: keep tight and local. One line is preferred, but multi-line is fine when you need to document a non-obvious implementation constraint, a local trade-off, or coupling that future edits could easily break. Keep that rationale next to the affected block. See the tz-aware comment in [`src/aiopurpleair/helpers/validator/__init__.py`](src/aiopurpleair/helpers/validator/__init__.py) for the shape - it explains *why* the validator returns a tz-aware datetime (a downstream consumer requires it), not *what* the line does.
- **Don't explain *what* the code does** - well-named identifiers handle that. Don't reference the current task ("added for X", "used by Y"); that belongs in the PR description.

#### Docstrings

- Follow [PEP 257][pep257]. Focus docstrings primarily on the **behavior contract** (what callers and tests can rely on), public semantics, and edge-case expectations. Implementation-local rationale belongs in inline `#` comments, not docstrings.
- A short one-liner is fine for trivial functions and tests with self-documenting names.
- For non-trivial behavior - contracts a test pins, edge cases callers must know about, load-bearing design trade-offs - write a one-line summary, blank line, then a details paragraph. Use the `Args:` / `Returns:` / `Raises:` sections already established across the codebase (see [`src/aiopurpleair/errors.py`](src/aiopurpleair/errors.py)'s `raise_error`).
- Design notes belong **in the code** (docstrings or inline comments). They do NOT belong in [`HISTORY.md`](./HISTORY.md) - that file is end-user release notes, not a design log.

#### Type Hints

- **Everything is typed.** `mypy src` (strict, with `warn_unreachable` and the pydantic plugin) and `pyright` (strict on `src`) are both CI gates. Both must be clean.
- **Use modern syntax**: `list[int]` not `List[int]`, `dict[str, X]` not `Dict[str, X]`, `X | None` not `Optional[X]`. Use `from __future__ import annotations` only when needed for forward references (the codebase uses it where models reference each other).
- **Don't add `# type: ignore` without a comment** explaining the constraint. If a recurring false positive needs suppression, configure it project-wide in `[tool.mypy]` / `[tool.pyright]` rather than scattering inline markers.

#### Naming

- `snake_case` for functions, methods, variables, modules, package directories.
- `PascalCase` for classes, type aliases, type vars, enum members. Exception subclasses end in `Error` (`PaymentRequiredError`, `InvalidDataReadKeyError`).
- `UPPER_SNAKE_CASE` for module-level constants (`ERROR_CODE_MAP`, `EPOCHORDINAL`).
- Single leading underscore for module-private (`_version.py`); double leading underscore for name-mangled (rare - usually means rethink the design).

#### Imports

- **Let ruff sort imports.** The `I` rule family (isort-equivalent) is enabled; don't hand-sort. Standard library first, then third-party, then first-party (`aiopurpleair`).
- Avoid wildcard imports (`from x import *`) outside `__init__.py` re-exports.

#### Patterns to Avoid

- **Don't add backward-compat shims, `# removed` markers, or rename-to-`_` for unused vars** - just delete. Git history is the audit trail.
- **Don't add error handling for impossible cases.** Trust internal code; only validate at boundaries - here, the boundary is the parsed API response, mapped through `ERROR_CODE_MAP` in `errors.py` and validated by the pydantic models.
- **Don't use exceptions for expected control flow.** The `PurpleAirError` hierarchy is for the API's documented failure conditions, not for branching on normal responses.
- **Don't suppress errors silently** (`except Exception: pass`). Handle the specific exception and document why it's safe, or let it propagate.

### Tests

- `pytest` with the configuration in `pyproject.toml` `[tool.pytest.ini_options]` (`asyncio_mode = "auto"`, `testpaths = ["tests"]`, `--strict-markers`, `--strict-config`). Run with `uv run pytest`.
- **A test lives in a `tests/` directory, never inside the production file it tests.** A deployed script may keep a `--selftest` that runs a small smoke check in seconds, and the case matrix lives in `tests/`. A self-test shipped inside the file it tests grows the file every reviewer reads, and its cases can come to outweigh the code they test.
- **100% coverage is a hard gate.** `[tool.coverage.report]` sets `fail_under = 100` over the `aiopurpleair` source; a line the tests don't reach reds the run. Cover the branch, or justify an exclusion via the existing `exclude_lines` (`raise NotImplementedError`, `if TYPE_CHECKING:`) - don't lower the floor.
- **Snapshot tests use [syrupy][syrupy].** They assert whole response-model shapes. Regenerate with `uv run pytest --snapshot-update` **only** when a model changes intentionally, and review the snapshot diff like any other code - a snapshot churned to make a test pass is a silent contract change.
- One test module per source module. Test functions named `test_<scenario>_<expected_behavior>` - descriptive, not numbered.
- Use fixtures for shared setup instead of setup/teardown methods. **Avoid mocking when fakes work** - hand-rolled fakes (or `aresponses` for HTTP) are usually clearer and break less than `unittest.mock` magic.
- **Test the behavior the docstring promises**, not implementation details. If a test breaks when you refactor *without changing behavior*, it is asserting on an implementation detail.

### Versioning

The package version lives nowhere in the committed tree as a real number: `src/aiopurpleair/_version.py` carries a placeholder `__version__` (the single source hatchling reads via `[tool.hatch.version]`). At build time NBGV computes the real version from `version.json` (SemVer base `1.0` plus git height) and the build task `sed`s the PEP 440 form into `_version.py` **on the runner only**, with no commit. See [WORKFLOW.md](./WORKFLOW.md) for the full version model. Don't hand-edit the placeholder to a real version, and don't create manual tags.

### Linter Cleanliness

Before pushing or opening a PR:

- VS Code's **Problems** pane should be quiet for the files you touched. The relevant linters are ruff (via the `charliermarsh.ruff` extension) and pyright (via the `ms-python.python` extension's bundled Pylance).
- CI runs the same verify set through the hub's validate task rather than as local steps, and the invocations differ from the local ones while the coverage matches. `ruff check` and `ruff format --check` run in its `lint` job, `mypy` runs there bare, targeted by `files = ["src"]` in `pyproject.toml` rather than by a path argument, `pytest` runs in its `unit-test` job, and `pyright` runs in this repository's own `.github/actions/validate` hook, because that job takes `mypy` or `pyright` and never both. It remains the authoritative gate.
- Markdown in this directory follows the repo-wide [Markdown and Spelling](#markdown-and-spelling) rules.

[google-shell-link]: https://google.github.io/styleguide/shellguide.html
[mypy]: https://mypy-lang.org/
[pep257]: https://peps.python.org/pep-0257/
[pep8-names-link]: https://peps.python.org/pep-0008/#package-and-module-names
[ps-approved-verbs-link]: https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands
[pyright]: https://microsoft.github.io/pyright/
[pytest]: https://docs.pytest.org/
[ruff]: https://docs.astral.sh/ruff/
[syrupy]: https://github.com/syrupy-project/syrupy
[uv]: https://github.com/astral-sh/uv
