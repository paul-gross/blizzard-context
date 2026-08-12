# Python toolchain and docstring authoring

The packaging, lint, format, and type-check toolchain every blizzard Python change — the hub, the runner, the CLI, and the `blizzard-mock` fleet — is held to, plus the authoring conventions a docstring's prose is held to.
Follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## uv, ruff, pyright (`bzh:python-toolchain`)

**Rule.** Python is packaged with **uv** and held to **ruff** (lint *and* format) and **pyright**; the quality gates run from the first commit, not retrofitted.
The commands a change must pass:

| Check     | Command                                                                                                                                                              |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Install   | `uv sync` — installs the project and its `dev` group                                                                                                                 |
| Lint      | `uv run ruff check .`                                                                                                                                                |
| Format    | `uv run ruff format --check .` (write with `uv run ruff format .`)                                                                                                   |
| Typecheck | `uv run pyright`                                                                                                                                                     |
| Test      | `uv run pytest` (the unit and component tiers — [./frontend.md](./frontend.md) and [../verification/blizzard.md](../verification/blizzard.md) own the browser tiers) |

`pyproject.toml`'s `[tool.ruff.lint] select` enables exactly `E, F, I, UP, B, C4, SIM, RUF` — **not** bandit's `S` family, so a `# noqa: S10x` directive silences a rule ruff never runs and fails as an unused `noqa` instead.

**Why.** One packaging tool and one lint/format/type toolchain, gated from the first commit, keeps quality cheap to satisfy — the cost of a clean tree is paid continuously rather than as a later cleanup — and gives every agent the same commands to run before pushing regardless of which blizzard component it touched.

**Detect.** A second formatter (black, autopep8) or packaging tool (poetry, pip-tools) introduced alongside these; Python changes pushed without the commands above passing.

**Do.** Run `uv run ruff check . && uv run ruff format --check . && uv run pyright && uv run pytest` before pushing a Python change.

**Don't.** Add black or isort "as well as ruff" — ruff owns both lint and format, and a second formatter is a second opinion that fights the first.

## Docstring prose is bound by the markdown-authoring principles too (`bzh:docstring-prose-authoring`)

**Rule.** A docstring is code, not a markdown file, but every rule in `winter-canon:/principles.md` binds it too — all of it except `canon:no-hard-wrap`, scoped below.

**Why.** The same defects the markdown-authoring principles exist to prevent — a fact duplicated across two docstrings, a docstring that explains today's code by contrasting it with a deleted one, a citation to a chunk-internal review id that resolves nowhere once the chunk closes — recur in Python prose exactly as often as in markdown; nothing about being inside a triple-quoted string changes why they're worth naming.

**Scope.** `canon:no-hard-wrap` binds a docstring only outside `src/`. `bzh:python-toolchain`'s own `ruff` gate gives every `src/` docstring a real line-length ceiling (`line-length = 120`, `E501` selected), so a rule additionally forbidding line breaks inside that ceiling would have no way to comply with both gates at once inside `src/` — the toolchain's own wrap governs there instead. `tests/*` carries no competing ceiling: `pyproject.toml`'s `per-file-ignores` disables `E501` for `tests/*`, so `canon:no-hard-wrap` binds a `tests/*` docstring the same as any other prose.

**Detect.** A docstring re-explaining a fact its own class/module already states elsewhere; a docstring anchored to code the same change deletes ("unlike the old X…", "ported from Y", "as of this change"); a docstring citing a chunk-internal review-round finding id; a `tests/*` docstring hard-wrapped to a fixed column, where no competing line-length ceiling excuses it.

**Do.** State a docstring's fact once, forward-looking, in the module that owns it. Let `ruff format`'s own wrap stand in `src/`; write a `tests/*` docstring one sentence per physical line, same as markdown.

**Don't.** Repeat a fact a sibling docstring or this file's own prose already states. Frame present behavior as a correction to code the same change removes.

## See also

- [`./wire.md`](./wire.md) — `bzh:utc-instants`, whose fitness test (`tests/test_wire_timestamps.py`) runs under `uv run pytest` like any other unit test.
