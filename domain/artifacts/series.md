# Artifact series

What a chunk accumulates across its nodes, and how a later node addresses an earlier one's output. A spoke of the
[artifacts hub](../artifacts.md).

A node-scope artifact accumulates as an append-only, versioned series per node and artifact name:

- **Committed with the step, atomically** — a worker step's artifacts land in the same fenced write as the movement they
  belong to (its transition, its gate decision, or the migration recorded in place of a transition when the step takes
  the chunk off its graph), so a rejected step's artifacts never exist.
- **Append, never overwrite** — re-running a node adds new entries under the new attempt, and earlier entries remain as
  history.
- **Reads resolve to the newest entry** — later nodes fetching a node-scope artifact by name get the latest attempt's
  version, while the shadowed history stays available.
- **The series keys on the node name** — after a migration or a re-published graph, a re-run of `build` keeps appending
  to the same series (`bzh:ids-exact-names-correlate`, [ids and names](../graphs/ids-and-names.md)); the exact producing
  node is on each artifact's provenance.

A hub node is the deliberate exception [delivery](./delivery.md) rests on: it records its own progress and marker
artifacts as it goes, outside any movement, because a partially-landed delivery must leave a durable trace before any
transition exists to carry it.

A graph-scope artifact carries no series: the mint bakes each declared entry once, immutable for that mint's whole life,
superseded only by a fresh mint under a new `graph_id`.
