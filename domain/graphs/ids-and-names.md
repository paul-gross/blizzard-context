# Ids and names (`bzh:ids-exact-names-correlate`)

A convention rule in the graph definition routed from [../graphs.md](../graphs.md), following the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Rule

Exact references — a transition's nodes, an artifact's provenance, an edge's choice — carry ids pinning one immutable
definition; cross-graph continuity — migration landing, artifact series, runner-side gate selection — keys on names.
Never the reverse.

## Why

An id names exactly one thing in one immutable graph and can never dangle or drift; a name is all same-purpose entities
across graphs share — correlation's only key.

## Detect

Matching an exact reference by name (two graphs' `build` nodes conflated), or correlating across graphs by id (a
migration expecting the same node id in the target graph).

## Do

A transition records its two nodes' exact ids; an authored-choice migration lands on the target graph's name-matched
node.

## Don't

Key an artifact series on node id — it breaks at every migration or re-publish though the work is the same station's.
