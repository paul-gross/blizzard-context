# e2e scenarios — the runner panel (`bzh:e2e-runner-panel`)

<!-- one `##` section per `tests/e2e/` module, its bullets naming that module's test functions — machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s check C. -->

The scenario that drives a real Chromium over the panel a runner serves itself, against a real ticking runner process.

## test_runner_panel_live_e2e

**The runner panel's own live SSE stream**: unlike every other in-process scenario, this one drives a **real**
`blizzard-runner host` subprocess ticking its own reconciliation loop on a fast interval (`BZ_RUNNER_TICK_SECONDS=1`)
rather than a synchronous `LoopWiring.tick_once()` — the one composer that threads a single `EventBroker` into both the
served app and the ticked loop for real, not the harness's in-process stand-in.

- `test_runner_panel_updates_live_over_sse_with_no_reload` — a real Chromium loads the runner's local panel once and
  never reloads it; the live loop's own FILL step claims the promoted chunk and mints a lease — a real `lease-changed`
  frame, not a fixture shortcut — and the panel's lease count and row move from `0 live` to `1 live` well inside the
  panel's own 1-minute poll backstop, so this first flip's passing assertion is necessarily SSE-driven — the scenario's
  one load-bearing SSE-specific proof; the scripted graph then runs itself to `done` under the same live loop, each
  further transition a further `lease-changed` frame over the same open connection, and the panel settles back to
  `0 live` once `deliver` (a hub node, no runner lease) lands the chunk, asserted with a generous timeout equal to that
  backstop itself — so, unlike the first flip, this closing settle does not on its own rule out the backstop having
  carried it; it proves the scenario completes end to end, not that every intermediate flip was SSE-driven. Together
  they prove the publish → stream → `local-panel`'s own `RunnerLiveUpdates` registry → re-read chain, the runner
  counterpart of `test_board_browser_e2e`'s hub-side live-pause proof. Needs the built bundle the runner itself serves
  (hence `mise run e2e`'s `depends = ["web-build"]`) + the sibling provisioned `blizzard-mock` worktree + a local winter
  source + an installed Chromium; it skips cleanly without `BLIZZARD_E2E=1`, without Chromium, without the provisioned
  worktree, or without the winter source.
