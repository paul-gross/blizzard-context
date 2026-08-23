# Work

The unit of work at the model's center: the chunk, its derived statuses, and the movement facts carrying it — in-graph
transitions, cross-graph migrations, and an operator's restart. Part of the domain model; parent hub:
[./index.md](./index.md).

| File                                         | When to read                                                                                                    |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| [work/chunk.md](./work/chunk.md)             | You need what a chunk is and carries — its work refs, its graph pin, and the properties an operator edits on it |
| [work/statuses.md](./work/statuses.md)       | You need what a status means, or which condition a chunk in some state derives                                  |
| [work/transitions.md](./work/transitions.md) | You need how a chunk moves along an edge within its pinned graph                                                |
| [work/migration.md](./work/migration.md)     | You need how a chunk changes graphs — what triggers a re-pin, and where it lands                                |
| [work/restart.md](./work/restart.md)         | You need what an operator's forced move onto a node does, defers, or refuses                                    |

## See also

- [./graphs.md](./graphs.md) — the immutable definition a chunk travels, and the node/edge/executor shape a migration's
  landing keys on.
- [./execution.md](./execution.md) — who holds a chunk, the lease behind each node-step attempt, and the epoch fencing
  its transitions.
