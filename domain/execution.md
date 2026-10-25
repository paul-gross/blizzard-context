# Execution — who runs a chunk

Who runs a chunk, on which machine, and how exactly-once holds. Part of the [domain model](./index.md).

Full detail lives under [./execution/](./execution/), one file per reader question; where a spoke states an enforceable
invariant, it does so in the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Routing

| File                                                     | Read when…                                                                                                           |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| [`responsibilities.md`](./execution/responsibilities.md) | …you need which party owns a piece of execution, or what a runner's registry entry reports.                          |
| [`acquisition.md`](./execution/acquisition.md)           | …you need how a chunk is granted to one runner, what the route locates, or which writes give tenure back.            |
| [`hosts.md`](./execution/hosts.md)                       | …you need a host's identity or lifecycle, runner membership, or how its runners share resources and allocate agents. |
| [`fencing.md`](./execution/fencing.md)                   | …you need what bounds one node-step attempt, or how a stale attempt is kept from advancing the chunk.                |
| [`envelope.md`](./execution/envelope.md)                 | …you need what a worker session is primed with, or how a change reaches it.                                          |
| [`throttling.md`](./execution/throttling.md)             | …you need what holds a runner back without braking it, or which runners a subscription's exhaustion stops.           |
| [`pause.md`](./execution/pause.md)                       | …an operator paused a runner or a chunk — what stops, what keeps running, and what happens to the claim.             |
| [`retirement.md`](./execution/retirement.md)             | …an operator retired a runner or revoked its token — what stops, what survives, and how it is reversed.              |
| [`recovery.md`](./execution/recovery.md)                 | …a lease expired, an attempt was exhausted, or a chunk must change runner.                                           |
| [`claim-vocabulary.md`](./execution/claim-vocabulary.md) | …you need the operator-facing terms for a claim and what a runner's process does to it.                              |

## See also

- [./work.md](./work.md) — the transitions these leases produce and the statuses tenure derives.
- [../architecture/crash-correctness.md](../architecture/crash-correctness.md) — how the daemons are built and tested so
  these semantics survive `kill -9`.
