# Edges, judgements, and choices

How a node's exit is judged and which edge that judgement selects. Part of the graph definition
([../graphs.md](../graphs.md)).

A directed, outcome-keyed connection between two nodes of the **same graph** — cross-graph movement is a migration,
never an edge (`bzh:migration-not-transition` in [work/migration.md](../work/migration.md)).

- **Keyed by exactly one choice** of the source node's judgement, and every choice a judgement can produce has exactly
  one edge — resolution is checked when the graph is created, so an edge can never dangle and a judgement can never
  select nothing.
- **Exactly one entry node** per graph; **cycles are intentional** — build → review → build is the shape, not a
  validation error.
- An edge carries **arrival context**: prose appended to the target node's prompt so the worker knows how it got there.

## Judgement and choices

The evaluation at a node's exit that selects the outgoing edge.

- **Judged by the worker** (the default): elicited when the worker declares done, informed by the node's `checks:` (run
  at exit and injected — the `checks` facet above); the worker selects exactly one of the node's choices. A missing or
  unparseable selection is a **failure, not a judgement** — it consumes a retry rather than an edge. So is selecting a
  `requires_checks` choice while any check is red (below): the engine refuses the edge and re-elicits with the red
  evidence in hand, consuming a retry exactly like an unparseable verdict — never an engine-owned override of the
  worker's routing.
- **Judged by a human**: the structural mark of a gate — the person renders the judgement by picking from the same
  choices, presented as buttons ([humans.md](../humans.md)).
- **Judged by a hub-executed node's own script**: its declared `run:` steps select one of the node's authored choices by
  exit code and stdout, the same fused choice/edge shape a worker's judgement uses — e.g. the shipped `deliver` node's
  script selecting `landed` or `conflict` ([artifacts.md](../artifacts.md),
  [standards/hub-nodes.md](../../standards/hub-nodes.md)).

A **choice** is one selectable outcome of one node's judgement, scoped to that judgement — never a global registry:
`pass` in build and `pass` in review are different choices that happen to share a name. Each choice keys exactly one
outgoing edge; its description is what sharpens a worker's judgement and what a gate renders as button text.

- **A choice may require green checks.** A choice may declare `requires_checks: true` (e.g. build's `pass`; its `fail`
  would not) — the engine then refuses to accept that edge while any of the node's `checks:` is red, treating the
  selection as a failure that consumes a retry and re-queues a fresh attempt (never accepting the edge, never overriding
  the worker's choice). A red check reported through a **non-gated** choice (`fail`, with the worker's assessment of
  *why*) routes normally — that context-rich path stays open. Graph validation rejects `requires_checks` on a node with
  no `checks:` and on hub/human-judged nodes.
- **A choice may target another graph.** A choice's `to:` normally names a sibling node or the reserved terminal; it may
  instead name `graph:<name>` — a cross-graph **migration** target. Taking that choice re-pins the chunk to the named
  graph and lands it at the target's landing node (name-matched, else the target's entry), the landed node's disposition
  governed by [work/migration.md](../work/migration.md) §Landing — recording a migration fact, never a transition — so
  `bzh:migration-not-transition` in [work/migration.md](../work/migration.md) still holds (the authored choice carries
  the target; the *movement* is a migration, not an edge to another graph's node, which stays forbidden). A choice may
  also carry an optional `model:` — a single model name the migration re-pins as the chunk's **default model
  preference**, the value an undeclared surface inherits. The target is resolved by **name** when taken (late-bound, the
  same binding ingest uses, `bzh:ids-exact-names-correlate`), so authoring a choice whose target graph is not yet minted
  is a mint-time warning, not an error.
