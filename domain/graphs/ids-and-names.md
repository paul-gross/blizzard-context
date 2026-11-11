# Ids and names (`bzh:ids-exact-names-correlate`)

Which references in the graph definition routed from [../graphs.md](../graphs.md) pin an exact id, and which correlate
across graphs by name.

Exact references — a transition's nodes, an artifact's provenance, an edge's choice — carry ids pinning one immutable
definition; cross-graph continuity — migration landing, artifact series, runner-side gate selection — keys on names.
Never the reverse.

An id names exactly one thing in one immutable graph and can never dangle or drift; a name is all same-purpose entities
across graphs share — correlation's only key. For instance, a transition records its two nodes' exact ids, and an
authored-choice migration lands on the target graph's name-matched node. Matching an exact reference by name would
conflate two graphs' `build` nodes; correlating across graphs by id would have a migration expect the same node id in
the target graph, where no node carries it; and an artifact series keyed on node id would break at every migration or
re-publish though the work is the same station's.
