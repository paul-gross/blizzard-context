# Edges

An edge is a directed, outcome-keyed connection between two nodes of the same graph, in the definition routed from
[../graphs.md](../graphs.md); cross-graph movement is a migration, never an edge (`bzh:migration-not-transition`,
[../work/migration.md](../work/migration.md)). Definitional — a taxonomy of edges, choices, and the judgement that
selects them (`canon:rule-shape` §File kinds). Part of the [domain model](../index.md). An edge is keyed by exactly one
choice of the source node's judgement, and every choice has exactly one edge; resolution is checked at graph creation,
so neither an edge nor a judgement can dangle. A graph has exactly one entry node; cycles are intentional, not a
validation error. An edge carries arrival context: prose appended to the target node's prompt.

## Choices

A choice is one selectable outcome of one node's judgement, scoped to it, never a global registry; its description
sharpens a worker's judgement and is a gate's button text. Its `to:` names a sibling node or the reserved terminal, or
`graph:<name>` — a cross-graph migration target. A choice may declare `requires_checks: true` to demand green checks
before its edge is accepted; validation rejects it on a node without `checks:` and on hub- or human-judged nodes.

### Migration choices

Taking a `graph:<name>` choice re-pins the chunk to the named graph, landing at the name-matched node or else the
target's entry ([../work/migration.md](../work/migration.md) §Landing). The target resolves by name only when taken
(`bzh:ids-exact-names-correlate`, [./ids-and-names.md](./ids-and-names.md)), so targeting a graph not yet minted is a
mint-time warning, not an error. A migration choice may carry `model:` — a single model name re-pinned as the chunk's
default model preference, what undeclared surfaces inherit.

## Judgement

Worker judgement is the default: elicited when the worker declares done, informed by the injected check results, the
worker selecting exactly one of the node's choices. Human judgement is the structural mark of a gate: the person picks
from the same choices, presented as buttons ([../humans/gates.md](../humans/gates.md)). A hub-executed node's `run:`
steps judge for it, selecting an authored choice by exit code and stdout — the same fused choice/edge shape.

## Failure, not judgement

A missing or unparseable selection is a failure, not a judgement — it consumes a retry rather than an edge. Selecting a
`requires_checks` choice while any check is red is the same retry-consuming failure: the engine refuses the edge and
re-elicits with the red evidence, never overriding the worker's routing. A red check reported through a non-gated choice
— a fail with the worker's why — routes normally; that context-rich path stays open.
