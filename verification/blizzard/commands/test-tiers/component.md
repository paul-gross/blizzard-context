# `blizzard:component-test` detail (`bzh:matrix-tier-component`)

<!-- the `###` section below is machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` heading, every test-filename code span, and each `mise run` name with its paired command span are machine-checked registrations — keep them verbatim, inside the section. -->

The component spoke of the test-tier hub [`../test-tiers.md`](../test-tiers.md). Read
[`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

### blizzard:component-test

`uv run pytest -m component` runs a domain slice wired with real internal collaborators, doubles only at the seams.

- `test_checks_gate_agreement.py` — applies the produces-coverage guard's anti-drift shape to the `requires_checks`
  gate: both real decision sites — the runner's local gate at worker exit and the hub's completion backstop — must reach
  the same, and the expected, accept/reject verdict over one scenario matrix, so re-deriving "is a gated choice red?"
  inline instead of calling the shared `wire.completion.ChecksGate.violated` predicate fails.
- `test_fleet_spend_api.py` — proves `GET /api/spend?since=` sums usage facts by `recorded_at` across every chunk,
  excluding facts recorded before `since` — distinct from a chunk's own derived total — with cost-absent rows giving a
  lower bound flagged `cost_partial`, and a malformed `since` rejected 422.
