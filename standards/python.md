# Python toolchain

The packaging, lint, format, and type-check toolchain every blizzard Python change — the hub, the runner, the CLI, and the `blizzard-mock` fleet — is held to.
Follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## uv, ruff, pyright (`bzh:python-toolchain`)

**Rule.** Python is packaged with **uv** and held to **ruff** (lint *and* format) and **pyright**; the quality gates run from the first commit, not retrofitted.
The commands a change must pass:

| Check | Command |
|-------|---------|
| Install | `uv sync` — installs the project and its `dev` group |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format --check .` (write with `uv run ruff format .`) |
| Typecheck | `uv run pyright` |
| Test | `uv run pytest` (the unit and component tiers — [./frontend.md](./frontend.md) and [../verification/blizzard.md](../verification/blizzard.md) own the browser tiers) |

`pyproject.toml`'s `[tool.ruff.lint] select` enables exactly `E, F, I, UP, B, C4, SIM, RUF` — **not** bandit's `S` family, so a `# noqa: S10x` directive silences a rule ruff never runs and fails as an unused `noqa` instead.

**Why.** One packaging tool and one lint/format/type toolchain, gated from the first commit, keeps quality cheap to satisfy — the cost of a clean tree is paid continuously rather than as a later cleanup — and gives every agent the same commands to run before pushing regardless of which blizzard component it touched.

**Detect.** A second formatter (black, autopep8) or packaging tool (poetry, pip-tools) introduced alongside these; Python changes pushed without the commands above passing.

**Do.** Run `uv run ruff check . && uv run ruff format --check . && uv run pyright && uv run pytest` before pushing a Python change.

**Don't.** Add black or isort "as well as ruff" — ruff owns both lint and format, and a second formatter is a second opinion that fights the first.

## See also

- [`./wire.md`](./wire.md) — `bzh:utc-instants`, whose fitness test (`tests/test_wire_timestamps.py`) runs under `uv run pytest` like any other unit test.
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md)'s "Docstring prose is bound too" bullet — a docstring is code, not a markdown file, but the same markdown-authoring principles (one canonical owner, point don't duplicate, no retrospective framing, no manual line-wrapping, minimal examples) bind it too.
