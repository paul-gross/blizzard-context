# Blizzard test-tier command detail (`bzh:matrix-command-tiers`)

The per-tier detail for the test tiers among the [`../../blizzard.md`](../../blizzard.md) Commands rows — what each tier
runs, what its named guards assert, and what it cannot see. Read [`../../blizzard.md`](../../blizzard.md) first for the
short command and the method-id inventory; [`../commands.md`](../commands.md) routes to the other methods' detail. Which
marker a test carries, and why, is [`../tier-rules.md`](../tier-rules.md#test-tiers).

Each tier's `### <method-id>` section lives in its own spoke below — one tier per file, its scoped row in a second
section beside it — so a fact stated in one spoke is linked from the others, never restated. For the statement guards'
tier mechanics and isolation scenarios, see [`../tier-rules.md`](../tier-rules.md); their refusals belong to
`bzh:tenant-scoped-store` and `bzh:runner-scoped-store`.

## Routing

| File                                                                      | Read when…                                                                                                                                                     |
| ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`unit.md`](./test-tiers/unit.md)                                         | …you are running or reading `blizzard:unit-test` or `blizzard:unit-test-scoped` — one class or function in isolation, and the sweep guards that ride the tier. |
| [`component.md`](./test-tiers/component.md)                               | …you are running or reading `blizzard:component-test` or `blizzard:component-test-scoped` — a domain slice with real internal collaborators.                   |
| [`sqlite-test-engine-leaks.md`](./test-tiers/sqlite-test-engine-leaks.md) | …you are verifying parallel test-suite SQLite engine cleanup and temporary-file handle retention.                                                              |
| [`postgres-uow-concurrency.md`](./test-tiers/postgres-uow-concurrency.md) | …you are verifying hub unit-of-work or cursor concurrency, or tenant close/drain, with the focused Postgres proof.                                             |
| [`service.md`](./test-tiers/service.md)                                   | …you are running or reading `blizzard:service-test` or `blizzard:service-test-scoped` — real daemons, store files, and external-tool bindings.                 |
| [`ui.md`](./test-tiers/ui.md)                                             | …you are running or reading `blizzard:ui` or `blizzard:ui-scoped` — the Playwright `ui*` projects, a Chromium page against the board a test's hub serves.      |
| [`crash-sweep.md`](./test-tiers/crash-sweep.md)                           | …you are running or reading `blizzard:crash-sweep` or `blizzard:crash-sweep-ci` — the kill-9 sweep arming the crash-point registry against real subprocesses.  |
| [`harness-check.md`](./test-tiers/harness-check.md)                       | …you changed the Playwright harness under `tests/harness/` and are running `blizzard:harness-check`, its own proof.                                            |
| [`winter-binding.md`](./test-tiers/winter-binding.md)                     | …you are running or reading `blizzard:winter-binding` — the winter workspace provider against the real winter CLI, local-only.                                 |
