# Transition — movement within the pinned graph

Part of [work.md](../work.md), the chunk and its lifecycle.

One entry in a chunk's append-only movement record: the fact that a judgement at a node's exit selected an edge and the
chunk moved along it.

- **Every transition is fully formed.** The judgement is what selects the edge — the worker's verdict, the hub's own
  machinery at a hub node, or a human's choice at a gate — so there is no unjudged movement and no transition without a
  judgement.
- **At a gate there is no transition until the human decides.** The node-step's completion lands as an open decision,
  and the resolving choice writes the transition referencing it ([humans.md](../humans.md)).
- **Atomic with the step's artifacts.** A node-step's transition and its artifacts are committed as one write — a
  rejected transition's artifacts never exist ([artifacts.md](../artifacts.md)).
- **Fenced.** A transition carries its attempt's epoch and a stale one is rejected, never recorded (`bzh:epoch-fencing`
  in [execution.md](../execution.md)) — the movement record only ever advances on a live attempt's say-so.
- **Authored by the holder.** The holding runner reports the chunk's transitions; the hub's own executor authors them
  for hub-executed nodes.
