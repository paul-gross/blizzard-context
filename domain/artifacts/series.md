# Artifact series

What a chunk accumulates across its nodes, and how a later node addresses an earlier one's output. A spoke of the
[artifacts hub](../artifacts.md).

A node-scope artifact accumulates as an append-only, versioned series per node and artifact name:

- **Committed with the step, atomically** — a worker step's artifacts land in the same fenced write as the movement they
  belong to (its transition, its gate decision, or the migration recorded in place of a transition when the step takes
  the chunk off its graph, or the `escalate-choice` escalation recorded in place of a transition), so a rejected step's
  artifacts never exist.
- **Append, never overwrite** — re-running a node adds new entries under the new attempt, and earlier entries remain as
  history.
- **Reads resolve to the newest entry** — a later node fetching a node-scope artifact by name gets the newest entry
  under that name, ordered by epoch, then by when it was produced, while the shadowed history stays available.
- **A name several nodes produced resolves across all of them** — the newest entry wins whichever node wrote it, so a
  node several paths converge on reads the one name each branch publishes and gets whichever branch wrote last. Naming a
  producing node (`--node`) is an optional narrowing: the read then resolves to the newest entry in that node's series
  alone.
- **A name in more than one scope is refused, never guessed** — a name that resolves in more than one of the node,
  graph, and system scopes is refused until the read names the scope, and the refusal lists the candidates
  ([declarations](../../standards/worker-nodes/declarations.md) owns the narrowing verbs).
- **The series keys on the node name** — after a migration or a re-published graph, a re-run of `build` keeps appending
  to the same series (`bzh:ids-exact-names-correlate`, [ids and names](../graphs/ids-and-names.md)); the exact producing
  node is on each artifact's provenance.

A hub node is the deliberate exception [delivery](./delivery.md) rests on: it records its own progress and marker
artifacts as it goes, outside any movement, because a partially-landed delivery must leave a durable trace before any
transition exists to carry it.

A graph-scope artifact carries no series: the mint bakes each declared entry once, immutable for that mint's whole life,
superseded only by a fresh mint under a new `graph_id`.
