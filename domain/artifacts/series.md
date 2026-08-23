# The chunk's artifact series

What a chunk accumulates across its nodes, and how a later reader addresses an earlier node's output. Spoke of the
[artifacts hub](../artifacts.md).

A **node-scope** artifact accumulates as an **append-only, versioned series** per node and artifact name — append and
resolve-newest, exactly as the rules below state. A **graph-scope** artifact carries no series at all: the mint bakes
each declared entry once, immutable for that mint's whole life, superseded only by a fresh mint under a new `graph_id`.

- **Committed with the step, atomically.** A worker step's artifacts land in the same fenced write as the movement they
  belong to — its transition, its gate decision, or the migration recorded in place of a transition when that step takes
  the chunk off its graph — so a rejected step's artifacts never exist and can never drift from the movement record.
  There is no separate submission for them. A **hub** node is the deliberate exception the delivery below rests on: it
  records its own progress and marker artifacts as it goes, outside any movement, because a script that has landed one
  repo of five must leave a durable trace of that before any transition exists to carry it.
- **Append, never overwrite.** Re-running a node adds new entries under the new attempt; earlier entries remain as
  history.
- **Reads resolve to the newest entry.** Later nodes fetching a node-scope artifact by name get the latest attempt's
  version; the shadowed history stays available.
- **Series key on the node *name*.** After a migration or a re-published graph, a re-run of `build` keeps appending to
  the same series (`bzh:ids-exact-names-correlate` in [graphs/ids-and-names.md](../graphs/ids-and-names.md)); the exact
  producing node is on each artifact's provenance.
