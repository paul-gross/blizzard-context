# e2e scenarios — the human loop (`bzh:e2e-human-loop`)

<!-- one `##` section per `tests/e2e/` module, its bullets naming that module's test functions — machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s check C. -->

The scenarios where a chunk stops and waits for a person — a retry budget exhausted, a question asked, a decision gated
ahead of deliver.

## test_escalation_e2e

Two verdict-less exits exhaust the node's retry budget and escalate to `needs_human`.

- `test_retries_exhausted_escalates_and_takeover_resumes_session` — the chunk derives `needs_human`, and the surfaced
  takeover command run **verbatim** actually resumes the parked mock session (its persisted turn advances); beside it,
  the escalation's `wrapped_takeover_command` is shape-checked — the runner-composed
  `blizzard runner takeover <chunk_id> --dir <resolved runner dir>` form, asserted against the run's own resolved runner
  directory, though the verbatim raw command remains the one actually executed.

## test_ask_answer_e2e

A build worker runs the real `blizzard runner ask` and exits.

- `test_ask_parks_then_answer_resumes_session_to_done` — the chunk parks `waiting_on_human` with the reap clock stopped
  (extra ticks reap nothing and consume no retry, the same single question stays open), then `blizzard hub answer`
  resumes the dormant session (the mock's persisted session state records the human's answer script) and the chunk lands
  (MVP criterion 7).

## test_gate_decision_e2e

A graph with a human `approve-gate` ahead of deliver.

- `test_graph_gate_parks_a_decision_then_decide_delivers` — parks an open Decision carrying the build's git-commit
  artifact, `blizzard hub decisions` lists it, `blizzard hub decide … approve` resolves it first-write-wins, the holding
  runner records the resolving transition, and the chunk delivers to bare `main` (MVP criterion 12).
