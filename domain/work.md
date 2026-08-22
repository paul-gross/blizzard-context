# Work — the chunk and its lifecycle

The unit of work at the center of the model: the chunk, the statuses it derives, and the movement facts that carry it —
transitions within its graph, migrations across graphs, and an operator's restart. Part of the
[domain model](./index.md).

Full detail lives under [./work/](./work/), one file per reader question.

## Routing

| File                                      | Read when…                                                                                                                |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| [`chunk.md`](./work/chunk.md)             | …you need what a chunk is and what it carries — its work refs, its graph pin, and the properties an operator edits on it. |
| [`statuses.md`](./work/statuses.md)       | …you need what a status means, or which condition a chunk in some state derives.                                          |
| [`transitions.md`](./work/transitions.md) | …you need how a chunk moves along an edge within its pinned graph.                                                        |
| [`migration.md`](./work/migration.md)     | …you need how a chunk changes graphs — what triggers a re-pin, and where it lands.                                        |
| [`restart.md`](./work/restart.md)         | …you need what an operator's forced move onto a node does, defers, or refuses.                                            |

## See also

- [./graphs.md](./graphs.md) — the immutable definition a chunk travels, and the node/edge/executor shape a migration's
  landing keys on.
- [./execution.md](./execution.md) — who holds a chunk, the lease behind each node-step attempt, and the epoch its
  transitions are fenced by.
