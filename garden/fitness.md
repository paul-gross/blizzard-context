# The `fitness` axis

The gardening axis that holds blizzard to the headroom no gate enforces — the budgets, warnings, and ungated checks that
stay yellow until one of them turns red. A spoke of the [garden registry](./index.md); the four fields below are the
shape `canon:gardening-axes` requires.

## Evaluates

Unenforced warnings and lost headroom — a signal every gate stays green through, so it accretes until it crosses the
threshold that fails a build nobody was watching. A run works through this checklist item by item, and reports each item
swept whether or not it found anything:

1. **Build budgets.** Every `budgets` entry in `blizzard/web/angular.json` — the `initial` and `anyComponentStyle`
   budgets of the hub and runner apps — that the built output puts at or past its `maximumWarning`, or within 10% of its
   `maximumError`.
2. **Web build warnings.** Warnings printed by the web build (`mise run web-build`, the hub and runner apps) and by the
   `fleet` library build (`npx ng build fleet` in `blizzard/web`, which no declared command runs).
3. **Python test warnings.** The warnings summary of the full Python suite, counted by category and by source —
   `uv run pytest -n auto` in `blizzard`, and `uv run pytest` in `blizzard-mock`, which carries no `pytest-xdist`. A
   deprecation is a finding whatever it names: the removal it announces will otherwise arrive as a failure.
4. **Dependency health.** `npm audit` in `blizzard/web`, and any pinned tool that reports a newer version of itself on
   the run — pyright's "new version available" notice is the shape.
5. **Ungated checks red on `master`.** Each declared verification method that no pull-request gate runs, run against
   `master`. Among them:
   - `blizzard:prose-ratchet`
   - `blizzard-context:registry-drift`
   - `blizzard:wheel` — `mise run build`, which also runs the web build
   - `web:shell-sweep`
   - `blizzard:e2e`
   - `dprint check` in `blizzard`, over `docs/` and the rest of its markdown
6. **Stale baselines.** A committed baseline or census that no longer matches the tree it measures —
   `blizzard/scripts/prose-density-baseline.json` is the shape.

## Scope

| Slug  | Ground                                                                                               |
| ----- | ---------------------------------------------------------------------------------------------------- |
| `all` | The whole target — `blizzard`, `blizzard-mock`, and `blizzard-context` — swept together on every run |

One slug on purpose: the signals above are cheap to gather and span all three repos, so a run always sweeps the whole
ground and every measurement is comparable with the last.

## Criteria

Each item's threshold lives where the tool or method that enforces it is declared, and this axis points at that home
rather than carrying a copy:

| Item             | Threshold's home                                                                                                                                                                                                                                                                                    |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Build budgets    | The `budgets` blocks of `blizzard/web/angular.json` — one per app's production configuration                                                                                                                                                                                                        |
| Ungated checks   | The Commands tables of [`../verification/blizzard.md`](../verification/blizzard.md) and [`../verifiability.md`](../verifiability.md) declare the methods; each repo's `.github/workflows/pr.yml` is what its pull-request gate actually runs — in `blizzard`, both `gate.yml` and `upper-tiers.yml` |
| Stale baselines  | The method that reads the baseline — `blizzard:prose-ratchet` for the prose-density baseline — declared in the same tables                                                                                                                                                                          |
| Warnings, audits | No declared standard — the tool's own report is the criterion. A finding cites the tool and the count it printed, and nothing here sets a number of warnings that is acceptable                                                                                                                     |

The one threshold this axis owns is the 10% headroom margin in item 1: a budget within 10% of its `maximumError` is a
finding before the build says anything, because the build's own warning fires only at `maximumWarning`.

What a pull-request gate enforces is out of range: a red gate is an unfinished change, not drift. A red **ungated**
method is the opposite case and stays in range — it is what item 5 exists to catch — so a run does not treat one as a
gate to halt on.

`dprint check` in `blizzard` has no row in [`../verification/blizzard.md`](../verification/blizzard.md) yet; its
configuration is `blizzard/dprint.json`. Until a row exists the check runs from that configuration, and declaring the
method is the first finding this item files.

A finding on this axis cites the checklist item it answers and the budget, method id, or tool it concerns; no item here
carries a `bzh:` id.

## Measurement

Every run records, findings or none:

- Headroom for each budget in item 1, in kB and as a percentage of its `maximumError`.
- Warning counts per source, for items 2 through 4.
- The number of ungated methods red on `master`, out of the number run.
- Findings opened.
