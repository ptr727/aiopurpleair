# Code Style and Formatting Rules

This is the single code-style guide for the repo. The **General** section applies to every language. The **Python** language section is self-contained: it is the style guide for the Python code this repo ships.

Cross-cutting *process* rules (PR titles, branching, US English, markdown style, comments philosophy, PR review etiquette) live in [AGENTS.md](./AGENTS.md) and are not repeated here.

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

### Markdown and Spelling

These apply repo-wide, in every directory:

1. **Markdown**: keep `.md` files clean under a standard markdownlint ruleset, with `MD013` (line-length) treated as disabled - long prose lines are intentional here (one logical paragraph per line). Fix violations at the source rather than disabling rules wholesale.
2. **Spelling**: US English throughout (the repo-wide convention - see [AGENTS.md](./AGENTS.md)). Project-specific terms (`aiopurpleair`, `PurpleAir`, `aiohttp`, `pydantic`, `syrupy`, `NBGV`) are correct, not misspellings.

## Python

*This section is the style guide for the Python code this repo ships.*

This repo ships an **installable PyPI package** (`aiopurpleair-ptr727`, import package `aiopurpleair`) using a **src-layout** (`src/aiopurpleair/`), the **hatchling** build backend, and **[uv][uv]** for environment and dependency management (`uv.lock` is committed). Everything runs through `uv run`.

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
- **100% coverage is a hard gate.** `[tool.coverage.report]` sets `fail_under = 100` over the `aiopurpleair` source; a line the tests don't reach reds the run. Cover the branch, or justify an exclusion via the existing `exclude_lines` (`raise NotImplementedError`, `if TYPE_CHECKING:`) - don't lower the floor.
- **Snapshot tests use [syrupy][syrupy].** They assert whole response-model shapes. Regenerate with `uv run pytest --snapshot-update` **only** when a model changes intentionally, and review the snapshot diff like any other code - a snapshot churned to make a test pass is a silent contract change.
- One test module per source module. Test functions named `test_<scenario>_<expected_behavior>` - descriptive, not numbered.
- Use fixtures for shared setup instead of setup/teardown methods. **Avoid mocking when fakes work** - hand-rolled fakes (or `aresponses` for HTTP) are usually clearer and break less than `unittest.mock` magic.
- **Test the behavior the docstring promises**, not implementation details. If a test breaks when you refactor *without changing behavior*, it is asserting on an implementation detail.

### Versioning

The package version lives nowhere in the committed tree as a real number: `src/aiopurpleair/_version.py` carries a placeholder `__version__` (the single source hatchling reads via `[tool.hatch.version]`). At build time NBGV computes the real version from `version.json` (CalVer base `2026.8` plus git height) and the build task `sed`s the PEP 440 form into `_version.py` **on the runner only** - no commit. See [WORKFLOW.md](./WORKFLOW.md) for the full version model. Don't hand-edit the placeholder to a real version, and don't create manual tags.

### Linter Cleanliness

Before pushing or opening a PR:

- VS Code's **Problems** pane should be quiet for the files you touched. The relevant linters are ruff (via the `charliermarsh.ruff` extension) and pyright (via the `ms-python.python` extension's bundled Pylance).
- CI runs the same verify set (`uv run ruff check` + `uv run ruff format --check` + `uv run mypy src` + `uv run pyright`) plus `uv run pytest` as separate workflow steps - the authoritative gate.
- Markdown in this directory follows the repo-wide [Markdown and Spelling](#markdown-and-spelling) rules.

[mypy]: https://mypy-lang.org/
[pep257]: https://peps.python.org/pep-0257/
[pyright]: https://microsoft.github.io/pyright/
[pytest]: https://docs.pytest.org/
[ruff]: https://docs.astral.sh/ruff/
[syrupy]: https://github.com/syrupy-project/syrupy
[uv]: https://github.com/astral-sh/uv
