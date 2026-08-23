# Execution — runners, tenure, and fencing

The routing hub for execution in the [domain model](./index.md): who runs a chunk and how exactly-once holds. Full
detail lives under [./execution/](./execution/), one file per reader question. Definitions, with the enforceable
invariant written in the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Routing

| File                                                     | Read when…                                                                                                        |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| [`responsibilities.md`](./execution/responsibilities.md) | …you need which party owns a piece of execution, or what a runner's registry entry reports.                       |
| [`acquisition.md`](./execution/acquisition.md)           | …you need how a chunk is granted to one runner, what the route locates, or which writes give tenure back.         |
| [`fencing.md`](./execution/fencing.md)                   | …you need what bounds one node-step attempt, or how a stale attempt is kept from advancing the chunk.             |
| [`envelope.md`](./execution/envelope.md)                 | …you need what a worker session is primed with, or how a change reaches it.                                       |
| [`pause.md`](./execution/pause.md)                       | …an operator has paused a runner or a chunk and you need what stops, what keeps running, and what the claim does. |
| [`recovery.md`](./execution/recovery.md)                 | …a lease expired, an attempt was exhausted, or a chunk must change runner.                                        |

## See also

- [./work.md](./work.md) — the transitions these leases produce and the statuses tenure derives.
- [../architecture/crash-correctness.md](../architecture/crash-correctness.md) — how the daemons are built and tested so
  these semantics survive `kill -9`.
