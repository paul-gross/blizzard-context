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

## Strict types (`bzh:strict-types`)

**Rule.** Shipping code type-checks under strict pyright, and a suppression waives one named rule at one line, with its
reason beside it.

**Why.** A signature is the first thing an agent meeting a module reads, and it builds on what the signature says.
Strict mode keeps that promise honest: it rejects an untyped parameter and a value whose type it cannot infer. A bare
`# type: ignore` silences every rule on its line whatever its brackets name, so one copied from module to module hides
real errors behind a comment that looks deliberate.

**Scope.** `pyproject.toml`'s `[tool.pyright]` `strict` names `src` and `exemplars/python`; the store migration tests
colocated under `src` are held to it with the shipping code, and the tests under `tests/` stay `standard` until they are
typed.

**Detect.** `blizzard:typecheck` reports every strict error. The structural gate's `bzh:strict-types` rule
(`blizzard:structural-gate`) flags a `type: ignore` comment and a `# pyright: basic` or `# pyright: standard` header
anywhere under `src` and `exemplars/python`, the store migration tests included.

**Do.** `# pyright: ignore[reportMissingTypeStubs]  # ships no py.typed` on the import of a library that ships no type
information, as `src/blizzard/foundation/platform_tracing/internal/pipeline.py` does; a JSON payload typed where it is
decoded, `decoded: dict[str, list[object]] = json.loads(payload)`.

**Don't.** A `# type: ignore[...]` naming a mypy code — the repo never runs mypy; a `cast` or `Any` that quiets an
unknown whose real type is knowable; a `# pyright: standard` header.

## Docstring prose (`bzh:docstring-prose-authoring`)

**Rule.** A docstring is code, not a markdown file — but every rule in `winter-canon:/principles.md` binds it too. State
a docstring's fact once, forward-looking, in the module that owns it.

**Why.** The defects those principles prevent recur identically in Python prose, and nothing about being inside a
triple-quoted string changes why they matter.

**Scope.** Docstring prose wraps at the toolchain's 120-column ceiling in `src/`, and `tests/*` docstrings hold to the
same 120 even though `per-file-ignores` disables `E501` there — one ceiling everywhere.

**Detect.** A fact duplicated across docstrings; a docstring explaining current code by contrast with code the same
change deletes (*"unlike the old X"*, *"as of this change"*); a process reference in any shape `bzh:comment-locality`'s
Detect names ([`./comments.md`](./comments.md)), gated regardless of whether it would still resolve.

**Do.** `src/blizzard/hub/runtime.py`'s module docstring: *"The `init` / `migrate` verbs run while the daemon is
**down** — the only carve-out to 'only a daemon opens its own store'."*

**Don't.** The same fact framed as change narrative — *"migrations no longer run at startup; the verbs moved to the
CLI"* — a docstring explaining the module by contrast with the code the change deleted.

## A property body only delegates (`bzh:property-delegates`)

**Rule.** A property body only delegates: any branch, boolean operator, or comparison lives in a plain method or
function the property returns.

**Why.** mutmut skips every decorated function except a lone `@staticmethod` or `@classmethod` — its
`_skip_node_and_children` declines a decorator's side effects in the trampoline copy and a `@property`'s signature
assignment. Decision logic in a property body is therefore never mutated, and mutation testing reports nothing about it.

**Scope.** `src/blizzard/**`; the property family is `@property`, `@cached_property`, `@functools.cached_property`, and
`@<name>.setter` / `@<name>.deleter`, alone or stacked with other decorators.

**Detect.** `bzh:property-delegates`, an `ast-grep` rule in the structural gate, flags an `if`, conditional expression,
`match`, comprehension `if`, `and`/`or`/`not`, or comparison anywhere in a property-family body. Every site that
predates the rule carries a `# ast-grep-ignore: bzh:property-delegates` directive on its `def` line; the gate's
unused-suppression check makes that list shrink-only.

**Do.** `LeaseActivity.state` in `src/blizzard/runner/leases/activity.py` returns `self._derive_state()`, a plain method
that holds the precedence chain.

**Don't.** A `# pragma: no mutate` workaround, a second decorator on the delegate (any decorator but a lone
`@staticmethod`/`@classmethod` puts it back out of mutmut's reach), or a new directive on a new site.
