# Blizzard command detail (`bzh:matrix-command-detail`)

Full per-method detail for the [`../blizzard.md`](../blizzard.md) Commands table rows marked *(more)* — what each
command actually runs, what its named guards assert, and what it cannot see. Read [`../blizzard.md`](../blizzard.md)
first for the short command and the method-id inventory.

The detail lives in the spokes below, one `### <method-id>` section per row, grouped by the question a reader arrives
with. Each method has exactly one home; a fact stated in one spoke is linked from the others, never restated.
`blizzard:e2e` is the one row with no section here — its scenarios are [their own registry](./e2e-scenarios.md).

## Routing

| File                                                  | Read when…                                                                                                                                                                                |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`test-tiers.md`](./commands/test-tiers.md)           | …you are running or reading a pytest tier — `blizzard:unit-test`, `blizzard:component-test`, `blizzard:service-test`, `blizzard:crash-sweep`.                                             |
| [`contract-sweeps.md`](./commands/contract-sweeps.md) | …you are changing an SSE frame or a fact one surface restates from another — `blizzard:sse-contract`, `blizzard:restatement-sweep`.                                                       |
| [`packaging.md`](./commands/packaging.md)             | …you are running the merge gate or building a distributable — `blizzard:gate`, `blizzard:wheel`, `blizzard:wheel-smoke`, `blizzard:image-smoke`, `blizzard:compose-smoke`, `blizzard:ci`. |
| [`web.md`](./commands/web.md)                         | …you are verifying the Angular workspace — `web:typecheck`, `web:client-drift`, `web:structural-gate`, `web:shell-sweep`.                                                                 |
| [`journey.md`](./commands/journey.md)                 | …you are running the live-fleet acceptance journey — `blizzard:journey`.                                                                                                                  |
| [`mock.md`](./commands/mock.md)                       | …you are verifying `blizzard-mock` itself — `blizzard-mock:unit-test`, `blizzard-mock:e2e`.                                                                                               |
