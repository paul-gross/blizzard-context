# Artifacts and delivery

What work produces and how it lands, what a graph declares for its workers to read, and delivery as graph-authored
content. Part of the [domain model](./index.md).

Full detail lives under [./artifacts/](./artifacts/), one file per reader question; where a spoke states an enforceable
invariant, it does so in the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Routing

| File                                         | Read when…                                                                                                   |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| [`model.md`](./artifacts/model.md)           | …you need what an artifact is — its kinds and scopes, and what a graph declares beside its nodes to be read. |
| [`never-code.md`](./artifacts/never-code.md) | …you need what an artifact may and may not carry.                                                            |
| [`series.md`](./artifacts/series.md)         | …you need what a chunk accumulates across its nodes, or how a later node addresses an earlier one's output.  |
| [`delivery.md`](./artifacts/delivery.md)     | …you need how a chunk's work lands, and why landing is not itself terminal.                                  |

## See also

- [./work.md](./work.md) — the transition an artifact commits with, and the `done` status delivery derives.
- [../standards/hub-nodes.md](../standards/hub-nodes.md) — the technical authoring contract a hub command node like
  `deliver` is held to.
- [../standards/worker-nodes.md](../standards/worker-nodes.md) — the technical authoring contract a worker node's
  declared asset is held to.
