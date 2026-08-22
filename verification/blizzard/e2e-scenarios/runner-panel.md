<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Runner-panel e2e scenario (`bzh:e2e-runner-panel`)

The scenario driving a real Chromium over the panel a runner serves itself, against a real ticking runner process.

## test_runner_panel_live_e2e

The runner panel's own live SSE stream, driving — unlike the in-process scenarios — a real `blizzard-runner host`
subprocess ticking its reconciliation loop fast (`BZ_RUNNER_TICK_SECONDS=1`) rather than a synchronous
`LoopWiring.tick_once()`: the one composer threading a single `EventBroker` into both the served app and the ticked loop
for real. The module needs the built bundle the runner itself serves (`mise run e2e` declares
`depends = ["web-build"]`), the sibling provisioned `blizzard-mock` worktree, a local winter source, and an installed
Chromium, skipping cleanly without `BLIZZARD_E2E=1` or without any of those.

- `test_runner_panel_updates_live_over_sse_with_no_reload` — loads the panel once in Chromium, never reloading; the live
  loop's FILL claims the promoted chunk and mints a lease — a real `lease-changed` frame, no fixture shortcut — and the
  lease count and row move from `0 live` to `1 live` well inside the panel's 1-minute poll backstop, making the first
  flip necessarily SSE-driven: the scenario's one load-bearing SSE-specific proof. The scripted graph then runs to
  `done` under the same live loop, each transition another `lease-changed` frame over the same open connection, and the
  panel settles to `0 live` once `deliver` (a hub node, no runner lease) lands the chunk, on a timeout equal to the poll
  backstop — so the closing settle proves end-to-end completion, not that every intermediate flip was SSE-driven.
  Together the two halves prove the publish → stream → `local-panel` `RunnerLiveUpdates` registry → re-read chain, the
  runner counterpart of `test_board_browser_e2e`'s hub-side live-pause proof ([board.md](./board.md)).
