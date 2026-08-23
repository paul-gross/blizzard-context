# `blizzard:component-test` detail (`bzh:matrix-tier-component`)

<!-- the `###` section below is machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` heading, every test-filename code span, and each `mise run` name with its paired command span are machine-checked registrations — keep them verbatim, inside the section. -->

A domain slice wired with real internal collaborators, doubles only at the seams. Spoke of the
[test-tier hub](../test-tiers.md).

Read [`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

### blizzard:component-test

`uv run pytest -m component` — a domain slice wired with real internal collaborators, doubles only at the seams.

The checks-gate agreement guard (`test_checks_gate_agreement.py`) applies the same anti-drift shape as the
produces-coverage guard to the `requires_checks` gate: both real decision sites — the runner's local gate at worker exit
and the hub's completion backstop — must reach the same, expected, accept/reject verdict over one scenario matrix, so
re-deriving "is a gated choice red?" inline instead of calling the shared `wire.completion.checks_gate_violated`
predicate fails.

The fleet spend-since read (`test_fleet_spend_api.py`) proves `GET /api/spend?since=` sums usage facts by `recorded_at`
across every chunk — distinct from a chunk's own derived total: facts recorded before `since` are excluded, cost-absent
rows give a lower bound with `cost_partial`, and a malformed `since` 422s.
