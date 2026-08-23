# Command-method detail (`bzh:matrix-command-detail`)

This file carries the per-method detail behind every `*(more)*`-flagged row of the Commands table in
[`../blizzard.md`](../blizzard.md): what the command runs, what its named guards assert, and what it cannot see. The
short command form and the inventory of method ids are in `../blizzard.md`.

| File                                                             | Read when…                                                                                                                                                                             |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`./commands/test-tiers.md`](./commands/test-tiers.md)           | You are running or reading a pytest tier: `blizzard:unit-test`, `blizzard:component-test`, `blizzard:service-test`, `blizzard:crash-sweep`                                             |
| [`./commands/web.md`](./commands/web.md)                         | You are verifying the Angular workspace: `web:typecheck`, `web:client-drift`, `web:structural-gate`, `web:shell-sweep`                                                                 |
| [`./commands/contract-sweeps.md`](./commands/contract-sweeps.md) | You are changing an SSE frame, or changing a fact one surface restates from another: `blizzard:sse-contract`, `blizzard:restatement-sweep`                                             |
| [`./commands/packaging.md`](./commands/packaging.md)             | You are running the merge gate or building a distributable: `blizzard:gate`, `blizzard:wheel`, `blizzard:wheel-smoke`, `blizzard:image-smoke`, `blizzard:compose-smoke`, `blizzard:ci` |
| [`./commands/journey.md`](./commands/journey.md)                 | You are running the live-fleet acceptance journey: `blizzard:journey`                                                                                                                  |
| [`./commands/mock.md`](./commands/mock.md)                       | You are verifying `blizzard-mock` itself: `blizzard-mock:unit-test`, `blizzard-mock:e2e`                                                                                               |
| [`./e2e-scenarios.md`](./e2e-scenarios.md)                       | You need `blizzard:e2e` — the one row with no section in these spokes, its scenarios registered there instead                                                                          |

Each method's detail lives in exactly one `### <method-id>` section in a leaf file, which a group spoke may reach
through its own routing table.
