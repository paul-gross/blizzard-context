# Blizzard test-tier command detail (`bzh:matrix-command-tiers`)

The per-tier detail for the pytest tiers among the [`../../blizzard.md`](../../blizzard.md) Commands rows marked
*(more)* — what each tier runs, what its named guards assert, and what it cannot see. Read
[`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail. Which marker a test carries, and why, is
[`../tier-rules.md`](../tier-rules.md#test-tiers).

Each tier's `### <method-id>` section lives in its own spoke below — one method per file, so a fact stated in one spoke
is linked from the others, never restated.

## Routing

| File                                            | Read when…                                                                                                                       |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| [`unit.md`](./test-tiers/unit.md)               | …you are running or reading `blizzard:unit-test` — one class or function in isolation, and the sweep guards that ride the tier.  |
| [`component.md`](./test-tiers/component.md)     | …you are running or reading `blizzard:component-test` — a domain slice with real internal collaborators.                         |
| [`service.md`](./test-tiers/service.md)         | …you are running or reading `blizzard:service-test` — a running daemon's HTTP API against a mock counterpart.                    |
| [`crash-sweep.md`](./test-tiers/crash-sweep.md) | …you are running or reading `blizzard:crash-sweep` — the kill-9 sweep arming the crash-point registry against real subprocesses. |
