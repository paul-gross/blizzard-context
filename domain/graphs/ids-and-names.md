# Ids are exact, names correlate (`bzh:ids-exact-names-correlate`)

The reference rule the graph definition and everything correlating across graphs is held to. Part of the graph
definition ([../graphs.md](../graphs.md)); the slot skeleton is owned by `winter-canon:/rule-shape.md`
(`canon:rule-shape`).

**Rule.** Exact references — a transition's nodes, an artifact's provenance, an edge's choice — carry **ids**, which pin
one immutable definition; continuity across graphs — migration landing, artifact series, runner-side gate selection —
keys on **names**. Never the reverse.

**Why.** An id names exactly one thing in exactly one immutable graph, so an exact reference can never dangle or drift;
a name is the only thing same-purpose entities in different graphs share, so it is the only key correlation can use.

**Detect.** A design that matches an exact reference by name — two graphs' `build` nodes conflated — or that correlates
across graphs by id, such as a migration expecting the target graph to contain the same node id.

**Do.** A transition records the exact ids of its two nodes; an authored-choice migration lands the chunk on the target
graph's node whose *name* matches the one it left.

**Don't.** Key an artifact series on the node id — the series would break at every migration or re-published graph,
though the work is the same station's.
