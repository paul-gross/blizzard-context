# Human entry points (`bzh:human-entries`)

Where people enter blizzard's loop, and the two parked conditions those entries produce. Each spoke owns what resolves
its entry and what an operator's restart ([./work/restart.md](./work/restart.md)) does to it — the hub routes without
restating that.

Parent: [./index.md](./index.md).

## The entries

| Spoke                                   | When to read                                                                                               |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| [asks.md](./humans/asks.md)             | Reasoning about a worker's question to a person mid-step, its answer, or a note a person leaves on a chunk |
| [gates.md](./humans/gates.md)           | Reasoning about a step whose outcome waits on a person's decision                                          |
| [escalation.md](./humans/escalation.md) | Reasoning about a chunk handed to a person because it could not go on                                      |
| [takeover.md](./humans/takeover.md)     | Reasoning about a person entering a worker's session                                                       |

## The two parked conditions

[./work/statuses.md](./work/statuses.md) owns the meanings and derivation of `waiting_on_human` and `needs_human`.
[./execution.md](./execution.md) owns the lease kept dormant while a chunk parks and the reap clock these entries stop.

## Posture

Every human entry is either opt-in (asks, gates) or exceptional (escalation, takeover). The default posture is
human-on-the-loop: no human step is scheduled unless a gate declares one, whether the graph declares it or a runner's
configuration does. Adding and removing gates is the dial between reviewing every step and supervising outcomes.
