# Delivery

How a chunk's work lands, and why landing is not itself the end. A spoke of the [artifacts hub](../artifacts.md).

Delivery is graph-authored content, not built-in engine machinery: a generic hub command node (`executor: hub` plus
`run:`, [nodes](../graphs/nodes.md)) whose declared script is the delivery policy, authoring its outcome choices exactly
like a worker node's judgement ([edges](../graphs/edges.md)).

- **Fleet-wide serialization.** One fleet-wide execution slot admits one chunk's hub node at a time — any hub node, not
  delivery specifically; a chunk finding it held tries again on a later tick.
- **Per-repository landing, with reconciliation.** A shipped delivery script lands a multi-repository chunk serially per
  repository, recording its own `merged/<repo>` marker immediately after each push; a re-run — after a crash, or a
  kicked-back redelivery — skips every repository whose marker is already durable. The engine imposes no per-repository
  landing shape of its own, but reads the `merged/<repo>` marker convention to tell a fully-landed continuation apart
  from a genuinely incomplete delivery ([outcome protocol](../../standards/hub-nodes/outcome-protocol.md)). Even
  chunk-atomicity — checking every repository merges before pushing any — is one script's construction, not a property
  of delivery: the fast-forward policy advances repositories one at a time and accepts a partial land, recovered by
  per-repository reconciliation.
- **Conflict is a judged, authored outcome**, not an engine special case: a dirty repository is one of the script's own
  outcome choices, routed to whatever edge the graph authors — ordinarily back into `build`, carrying the retained
  partial lands for the next attempt's reconciliation.
- **PR mode.** Which policy a chunk gets is a fact about the graph it travels; the shipped `deliver` nodes either
  fast-forward each repository's base branch onto the chunk's own commit, or open a pull request per repository and
  watch each to a clean merge. "PR mode" is an authored alternative policy — the plan-gated lane's `deliver` node —
  adopted by minting a graph naming that node in place of another's, never by an engine switch.
- **Environment retention.** The holding runner keeps the chunk's environments throughout delivery, until the outcome is
  known.

## Landing is not necessarily terminal

Landing is informational, not itself a terminal condition — only the graph's reserved terminal (`done`,
[statuses](../work/statuses.md)) is. A `deliver` node's `landed` choice may route straight to the graph's reserved
terminal, but the routing is authored, not fixed — every shipped lane in fact routes it into a further runner node, run
in the holding runner's still-held environment after every repository has merged, whose own choice then reaches the
terminal.
