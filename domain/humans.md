# Human entry points (`bzh:human-entries`)

Where people enter blizzard's loop, and the two parked conditions those entries produce. This file is a definitional
taxonomy (`canon:rule-shape` §File kinds); each spoke owns what resolves its entry and what an operator's restart
([./work/restart.md](./work/restart.md)) does to it — the hub routes without restating that.

Parent: [./index.md](./index.md).

## The entries

| Spoke                                   | Entry         | Initiated by                                                      | Parks              |
| --------------------------------------- | ------------- | ----------------------------------------------------------------- | ------------------ |
| [asks.md](./humans/asks.md)             | Ask           | The worker, mid-step                                              | `waiting_on_human` |
| [gates.md](./humans/gates.md)           | Gate decision | The workflow (a human-judged node) or runner configuration        | `waiting_on_human` |
| [escalation.md](./humans/escalation.md) | Escalation    | The system, on exhausted failure, or a worker's `escalate` choice | `needs_human`      |
| [takeover.md](./humans/takeover.md)     | Takeover      | A person entering a held session                                  | Nothing of its own |

## The two parked conditions

[./work/statuses.md](./work/statuses.md) owns the meanings and derivation of `waiting_on_human` and `needs_human`.
[./execution.md](./execution.md) owns the lease kept dormant while a chunk parks and the reap clock these entries stop.

## Posture

Every human entry is either opt-in (asks, gates) or exceptional (escalation, takeover). The default posture is
human-on-the-loop: no human step is scheduled unless a gate declares one, whether the graph declares it or a runner's
configuration does. Adding and removing gates is the dial between reviewing every step and supervising outcomes.
