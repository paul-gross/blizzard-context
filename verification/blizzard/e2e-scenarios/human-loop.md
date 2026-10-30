<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Human-loop e2e scenarios (`bzh:e2e-human-loop`)

The scenarios where a chunk stops for a person — a retry budget exhausted, a question asked, a decision gated ahead of
deliver.

## test_gate_decision_e2e

A graph with a human `approve-gate` ahead of deliver. Its `fleet traces` subtest proves what the acceptance loop's does.

- `test_graph_gate_parks_a_decision_then_decide_delivers` — proves an open Decision parks carrying the build's
  git-commit artifact, `blizzard hub decisions` lists it, `blizzard hub decide … approve` resolves it first-write-wins,
  the holding runner records the resolving transition, and the chunk delivers to bare `main` (MVP criterion 12).
