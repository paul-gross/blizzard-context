# Transitions

How a chunk moves along an edge within its pinned graph. Spoke of the [work hub](../work.md).

A transition is one entry in a chunk's append-only movement record: a judgement at a node's exit selected an edge and
the chunk moved along it. Every transition is fully formed — the edge is selected by a judgement, whether the worker's
verdict, the hub's own machinery at a hub node, or a human's choice at a gate — so unjudged movement does not exist.

Transitions are authored by the holder: the holding runner reports them, and the hub's own executor authors them for
hub-executed nodes. At a gate the node-step's completion lands as an open decision, and no transition exists until the
human's resolving choice writes one referencing that decision ([../humans/gates.md](../humans/gates.md)).

Three guards hold at the write:

- A transition carries its attempt's epoch, and a stale one is rejected rather than recorded (`bzh:epoch-fencing`,
  [../execution/fencing.md](../execution/fencing.md)).
- A node-step's transition, its artifacts, and its proposed work items ([../graphs/nodes.md](../graphs/nodes.md)) are
  committed as one write, so a rejected transition's artifacts and proposals never exist
  ([../artifacts.md](../artifacts.md)).
- A runner's completion or decision is refused when, at the current epoch, it does not come from the chunk's current
  node; when its attempt's own escalation or question is open; when it comes out of a hub-executed node; or when a
  runner-config gate decision is open at that node-step ([../humans/gates.md](../humans/gates.md)).
  - A replay of a completion or decision already recorded at the same `(from_node, epoch)` answers with its original
    outcome, ahead of this guard.
  - While the hub's own unresolvable-target escalation is open, only a completion that would re-escalate — the same
    cross-graph choice, its target still unresolvable — is answered, writing nothing; every other completion, and every
    decision, is refused ([migration.md](./migration.md)).
