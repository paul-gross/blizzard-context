# Delivery

How a chunk's work lands, and why landing is not itself the end. Spoke of the [artifacts hub](../artifacts.md).

Delivery is not built-in engine machinery — it is graph-authored content, a generic hub command node (`executor: hub` +
`run:`, [graphs/nodes.md](../graphs/nodes.md)) like any other, whose declared script IS the delivery policy. Several
policies ship, and which one a chunk gets is a fact about the graph it travels rather than about the engine: the shipped
lanes' `deliver` nodes either fast-forward each repo's base branch onto the chunk's own commit, or open a pull request
per repo and watch each to a clean merge. Even chunk-atomicity — checking every repo merges before pushing any — is one
script's construction, not a property of delivery: the fast-forward policy advances repos one at a time and accepts a
partial land, and the per-repo reconciliation below is what recovers it.

- **Fleet-wide serialization is a generic fact, not a delivery-only lane.** One fleet-wide execution slot admits one
  chunk's hub node — any hub node, not delivery specifically — at a time; a chunk finding it held elsewhere simply tries
  again on a later tick.
- **Per-repo landing with reconciliation is the script's own property, read by one shared convention.** A shipped
  delivery script lands a multi-repo chunk serially per repo, recording its own `merged/<repo>` marker immediately after
  each push; a re-run — after a crash, or a kicked-back redelivery — skips every repo whose marker is already durable.
  The engine imposes no per-repo landing *shape* of its own — a differently-authored script could land however it
  chooses — but it does read the `merged/<repo>` marker convention to tell a fully-landed continuation apart from a
  genuinely incomplete delivery
  ([standards/hub-nodes/outcome-protocol.md](../../standards/hub-nodes/outcome-protocol.md)).
- **Conflict is a judged, authored outcome, never an engine special case.** A dirty repo is one of the script's own
  outcome choices, routed like any other node's choice to whatever edge the graph authors — ordinarily back into
  `build`, carrying the retained partial lands for the next attempt's reconciliation.
- **"PR mode" is an authored alternative policy, not a built-in mode.** Opening a pull request per repo and waiting for
  it to go cleanly mergeable, instead of advancing the base branch directly, is one shipped script — the plan-gated
  lane's `deliver` node — among however many an operator wants, adopted by minting a graph naming that node in place of
  another's, never by an engine switch.
- The holding runner **keeps the chunk's environments throughout delivery**, until the outcome is known.

## Landing is not necessarily terminal

A hub node's script authors its outcome choices exactly like a worker node's judgement
([graphs/edges.md](../graphs/edges.md)). A `deliver` node's `landed` choice may route straight to the graph's reserved
terminal — but that routing is authored, not fixed, and every shipped lane in fact routes it into a further **runner**
node, run in the holding runner's still-held environment after every repo has merged, before that node's own choice
finally reaches the terminal. Landing is therefore informational, not itself a terminal condition — only the graph's
reserved terminal (`done`, [work/statuses.md](../work/statuses.md)) is.
