# Humans in the loop (`bzh:human-entries`)

Where people enter blizzard's loop, and the two parked conditions they produce. Definitional — a taxonomy of the human
entry points (`canon:rule-shape` §File kinds). Part of the [domain model](./index.md).

The default posture is human-**on**-the-loop: the default graph has no human touchpoints — agents verify and merge to
main. Every human entry is either **opt-in** (asks, gates) or **exceptional** (escalation, takeover); adding and
removing gates is the dial between reviewing every step and supervising outcomes.

Full detail lives under [./humans/](./humans/), one file per entry.

## Routing

| File                                      | Entry         | Who initiates                                              | Parks the chunk as                                                                                 |
| ----------------------------------------- | ------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| [`asks.md`](./humans/asks.md)             | Ask           | The worker, mid-step                                       | `waiting_on_human`                                                                                 |
| [`gates.md`](./humans/gates.md)           | Gate decision | The workflow (a human-judged node) or runner configuration | `waiting_on_human`                                                                                 |
| [`escalation.md`](./humans/escalation.md) | Escalation    | The system, on exhausted failure                           | `needs_human`                                                                                      |
| [`takeover.md`](./humans/takeover.md)     | Takeover      | A person, entering a held session                          | Nothing of its own — the chunk keeps the condition it was already in, plus human-in-session detail |

Each entry's own spoke owns what resolves it, and what an operator's restart ([work/restart.md](./work/restart.md)) does
to it — the table above routes rather than restating, so a new resolving path is one edit, not two.

The two parked conditions differ by cause: `waiting_on_human` is **invited** input — the model expects a person and
stops the reap clock; `needs_human` is **failure** — the system ran out of moves and a person must act. Both derive from
open facts, never stored flags ([work/statuses.md](./work/statuses.md)).

## See also

- [./work.md](./work.md) — the statuses these entries derive and the transition a resolved decision becomes.
- [./execution.md](./execution.md) — the lease kept dormant while a chunk parks, and the reap clock these entries stop.
