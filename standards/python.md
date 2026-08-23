# Python

The Python toolchain every blizzard change is held to — hub, runner, CLI, and the blizzard-mock fleet — plus the
authoring conventions a docstring's prose is held to. Rules follow the Rule/Why/Detect/Do/Don't slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`) with stable `bzh:` ids in their headings.

## Toolchain (`bzh:python-toolchain`)

**Rule.** Python is packaged with uv and held to ruff (lint and format both) and pyright, with the quality gates in
force from the first commit, never retrofitted.

**Why.** One toolchain, gated from the first commit, keeps a clean tree continuously cheap and gives every agent the
same commands regardless of component.

**Detect.** A second formatter (black, autopep8) or packaging tool (poetry, pip-tools) beside these — a second formatter
is a second opinion fighting the one ruff already is.

**Do.** A change must pass, after `uv sync` installs the project and its dev group:

- `uv run ruff check .`
- `uv run ruff format --check .` (write with `uv run ruff format .`)
- `uv run pyright`
- `uv run pytest` — the unit and component tiers; [./frontend.md](./frontend.md) and
  [../verification/blizzard.md](../verification/blizzard.md) own the browser tiers.

**Don't.** A `# noqa: S10x` directive — `pyproject.toml`'s `[tool.ruff.lint]` `select` enables exactly `E`, `F`, `I`,
`UP`, `B`, `C4`, `SIM`, `RUF`, not bandit's `S` family, so it silences a rule ruff never runs and fails as an unused
noqa instead.

## Docstring prose (`bzh:docstring-prose-authoring`)

**Rule.** A docstring is code, not a markdown file — but every rule in `winter-canon:/principles.md` binds it too. State
a docstring's fact once, forward-looking, in the module that owns it.

**Why.** The defects those principles prevent recur identically in Python prose, and nothing about being inside a
triple-quoted string changes why they matter.

**Scope.** Docstring prose wraps at the toolchain's 120-column ceiling in `src/`, and `tests/*` docstrings hold to the
same 120 even though `per-file-ignores` disables `E501` there — one ceiling everywhere.

**Detect.** A fact duplicated across docstrings; a docstring explaining today's code by contrast with code the same
change deletes (*"unlike the old X"*, *"as of this change"*); a citation of a chunk-internal review-finding id that
resolves nowhere once the chunk closes.

**Do.** `src/blizzard/hub/runtime.py`'s module docstring: *"The `init` / `migrate` verbs run while the daemon is
**down** — the only carve-out to 'only a daemon opens its own store'."*

**Don't.** The same fact framed as change narrative — *"migrations no longer run at startup; the verbs moved to the
CLI"* — a docstring explaining the module by contrast with the code the change deleted.
