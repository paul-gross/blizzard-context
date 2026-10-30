<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Node-sessions e2e scenarios (`bzh:e2e-node-sessions`)

What a node's session carries across an entry when the daemon restarts mid-session. Resume-time preamble elision now
lives at `blizzard:service-test` in `tests/service/fleet/resume-preamble.spec.ts`.

`test_mixed_harness_e2e` drives a real `blizzard-hub`/`blizzard-runner` subprocess pair, the daemon itself restarted
mid-scenario (`tests/crash/`'s own subprocess harness, reused rather than re-derived). Every module needs the sibling
provisioned `blizzard-mock` worktree and skips without `BLIZZARD_E2E=1`, and runs in the tag `release` workflow's full
e2e tier.

## test_mixed_harness_e2e

One traversal, one graph: a `build` node (default Claude Code, no `session_harnesses` declared) hands off to an
`opencode-review` node declaring OpenCode through a graph-level named session (`session: resume:<name>`), then to
`deliver` — related mixed-harness dispatch behavior is proven at `blizzard:service-test` by
`tests/service/runner/mixed-harness-dispatch.spec.ts`; this traversal uses a real daemon pair. The runner daemon is
cleanly restarted (SIGTERM, unarmed — no crash-point) twice: once right at the lineage boundary, before
`opencode-review`'s fresh mint is ever attempted, and once more mid-way through that same OpenCode session, while it is
hung open — proving a graceful operator restart survives both a harness handoff and a resume inside an already-open
session on the harness it lands in. Where a collector is present, both daemons export to a real `otelcol-contrib` from
their first start, and the `runner traces` subtest proves the runner host's own sweep tells both nodes' lease spans
across the restarts, nested on the hub's step roots by id alone, with `build`'s invocations carrying Claude Code and
`opencode-review`'s carrying OpenCode in the one run; that subtest alone skips without one.

- `test_mixed_lineage_crosses_a_harness_boundary_and_survives_two_operator_restarts` asserts:
  - Every dispatch lands on the correct adapter with no cross-harness leakage (the runner store's own `harness_id` per
    lease).
  - The second restart resumes the SAME lease/epoch/session opencode-review already held rather than minting a retry.
  - Each node's resolved effort and model carry the provenance its own session declared or inherited (build the chunk
    default, opencode-review its own session's).
  - The board's per-node-step usage attributes the right harness/model/version to the right node, cross-checked against
    the runner's own ground truth.
  - The hub's derived analytics events attribute the right harness/model to the right node (this test does not assert
    their `harness_version`).
  - Both nodes' commits land on bare main exactly once.

Resume-intent persistence and clearing are covered by `tests/test_runner_restart_resume.py`.
