# Static-check command detail (`bzh:matrix-command-static`)

<!-- One flat `###` section per method id — the shape this file's sibling spokes share. -->
<!-- rumdl-disable MD001 -->

The detail for the `blizzard:` checks that read the tree without starting a daemon: the build, the linters, the type
check, and the structural scans. Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the
method-id inventory; [`../commands.md`](../commands.md) routes to the other methods' detail.

Each finishes in seconds to about a minute, so a fleet node runs it whole. The lint, format, and typecheck rows are
governed by [`../../../standards/python.md`](../../../standards/python.md). The Python exemplars under
`exemplars/python/` ride `blizzard:lint`, `blizzard:format`, `blizzard:typecheck`, and the pytest tiers like any other
tree.

### blizzard:build

`uv sync` from the repo root installs the `blizzard` project and its `dev` group.

### blizzard:format

`uv run ruff format --check .` from the repo root. `uv run ruff format .` writes the fix.

### blizzard:lint

`uv run ruff check .` from the repo root.

### blizzard:typecheck

`uv run pyright` — strict over repository-owned Python, excluding dependency, cache, dot-directory, and generated build
output (`bzh:strict-types`). The configured gate also fails an inert suppression comment.

### blizzard:markdown-format

`mise x dprint@0.55.2 -- dprint check` — the markdown format gate `dprint.json` declares.

### blizzard:structural-gate

`mise run structural-gate` — the ast-grep structural scan and its rule tests (`contracts/ast-grep/`).

### blizzard:playwright-static

`mise run playwright-check` — the Playwright package's static checks: `tsc`, `eslint` including the runner world's
import boundary, and the wire-type regenerate-and-diff.

### blizzard:exemplar-check

`mise run exemplar-check` — the web exemplars under `exemplars/web/` held to the hub app's gates. `gate.yml` runs it as
its own job. [`../../../exemplars/conformance.md`](../../../exemplars/conformance.md) governs it.

### blizzard:flag-lifecycle

`mise run flag-lifecycle` runs `blizzard-flag-lifecycle`, which reads the registry's flags against every release tag. It
has three modes: `pr` (the default, against `--base origin/master`), `cut`, and `tag` (`bzh:flags-procedure`).

### blizzard:ci-workflows

`mise x actionlint@1.7.12 -- actionlint` from the repo root scans `.github/workflows/` by default. It is local-only:
`gate.yml` does not run it. `blizzard-mock:ci-workflows` is the same command from the `blizzard-mock` repo root.

### blizzard:aggregate-census

`uv run python -m tests.support.aggregate_census` — the runner refusal aggregate coverage census. It runs the component
observations and compares the aggregate assertions that passed against the refusals discovery finds. `blizzard:gate`
runs it as the step after pytest.
