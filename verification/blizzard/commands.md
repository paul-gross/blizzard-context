# Command-method detail (`bzh:matrix-command-detail`)

This file carries the per-method detail behind every `*(more)*`-flagged row of the Commands table in
[`../blizzard.md`](../blizzard.md): what the command runs, what its named guards assert, and what it cannot see. The
short command form and the inventory of method ids are in `../blizzard.md`.

| File                                                             | Read when…                                                                                                                                                   |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`./commands/test-tiers.md`](./commands/test-tiers.md)           | You are running or reading a pytest tier                                                                                                                     |
| [`./commands/web.md`](./commands/web.md)                         | You are verifying the Angular workspace                                                                                                                      |
| [`./commands/contract-sweeps.md`](./commands/contract-sweeps.md) | You are checking a surface against its committed contract, or checking that a restated fact agrees with its owner                                            |
| [`./commands/packaging.md`](./commands/packaging.md)             | You are running a merge or prose gate, checking compatibility with supported releases, or building or validating a distributable or deployment configuration |
| [`./commands/journey.md`](./commands/journey.md)                 | You are running the live-fleet acceptance journey                                                                                                            |
| [`./commands/rehearsal.md`](./commands/rehearsal.md)             | You are running the published-release checks or the focused Postgres unit-of-work concurrency proof                                                          |
| [`./commands/mutation.md`](./commands/mutation.md)               | You are running or reading a mutation-testing scope                                                                                                          |
| [`./commands/mock.md`](./commands/mock.md)                       | You are verifying `blizzard-mock` itself                                                                                                                     |
| [`./e2e-scenarios.md`](./e2e-scenarios.md)                       | You need `blizzard:e2e` — the one row with no section in these spokes, its scenarios registered there instead                                                |

Each method's detail lives in exactly one `### <method-id>` section in a leaf file, which a group spoke may reach
through its own routing table — a reader holding only the id finds it by that heading.
