<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Operator-board-in-a-browser e2e scenarios (`bzh:e2e-board`)

The scenarios driving a real Chromium over the web app the hub serves — the operator board's views and its live SSE
updates.

The browser scenarios are skipped in the `gate`/`pr` single-repo checkout; the tag `release` workflow runs the full e2e
tier headless over the multi-repo checkout (Chromium via `uv run playwright install --with-deps chromium`; locally,
`uv run playwright install chromium`).

Every browser scenario here needs the built bundle `blizzard hub host` serves and installed Chromium, skipping cleanly
without either or without `BLIZZARD_E2E=1`. Every scenario also needs the sibling provisioned `blizzard-mock` worktree.
The in-process event-log function needs only the worktree, no built bundle or Chromium.

## test_event_log_e2e

The operational event log's in-process half; its browser half runs as `tests/ui/event-log.spec.ts`.

- `test_a_verdict_less_exit_surfaces_a_critical_worker_lost_event` — the in-process half: a real mock worker's
  verdict-less exit exhausts its retry budget, the runner escalates, and the emission surfaces a critical `worker-lost`
  operational event that reads back off the live `GET /api/events` and fans out as an `event-logged` SSE frame read off
  the stream's replay tail — the runner-emit, hub-fold, read-and-fan-out chain, no browser.
