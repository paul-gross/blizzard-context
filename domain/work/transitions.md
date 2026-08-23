# Transitions

How a chunk moves along an edge within its pinned graph. Spoke of the [work hub](../work.md).

A transition is one entry in a chunk's append-only movement record: a judgement at a node's exit selected an edge and
the chunk moved along it. Every transition is fully formed — the edge is selected by a judgement, whether the worker's
verdict, the hub's own machinery at a hub node, or a human's choice at a gate — so unjudged movement does not exist.

Transitions are authored by the holder: the holding runner reports them, and the hub's own executor authors them for
hub-executed nodes. At a gate the node-step's completion lands as an open decision, and no transition exists until the
human's resolving choice writes one referencing that decision ([../humans.md](../humans.md)).

Two guards hold at the write:

- A transition carries its attempt's epoch, and a stale one is rejected rather than recorded (`bzh:epoch-fencing`,
  [../execution.md](../execution.md)).
- A node-step's transition and its artifacts are committed as one write, so a rejected transition's artifacts never
  exist ([../artifacts.md](../artifacts.md)).
