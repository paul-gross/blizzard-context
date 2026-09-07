# Delivery

How a chunk's work lands, and why landing is not itself the end. A spoke of the [artifacts hub](../artifacts.md).

Delivery is graph-authored content, not built-in engine machinery: a generic hub command node (`executor: hub` plus
`run:`, [nodes](../graphs/nodes.md)) whose declared script is the delivery policy, authoring its outcome choices exactly
like a worker node's judgement ([edges](../graphs/edges.md)).

- **Fleet-wide serialization.** One fleet-wide execution slot admits one chunk's hub node at a time — any hub node, not
  delivery specifically; a chunk finding it held tries again on a later tick.
- **Per-repository landing, with reconciliation.** A delivery script that lands a multi-repository chunk serially per
  repository records its own `merged/<repo>` marker immediately after each push; a re-run — after a crash, or a
  kicked-back redelivery — skips every repository whose marker is already durable. The engine imposes no per-repository
  landing shape of its own, but reads the `merged/<repo>` marker convention to tell a fully-landed continuation apart
  from a genuinely incomplete delivery ([outcome protocol](../../standards/hub-nodes/outcome-protocol.md)). Even
  chunk-atomicity — checking every repository merges before pushing any — is one script's construction, not a property
  of delivery: a fast-forward policy advances repositories one at a time and accepts a partial land, recovered by
  per-repository reconciliation.
- **Conflict is a judged, authored outcome**, not an engine special case: a dirty repository is one of the script's own
  outcome choices, routed to whatever edge the graph authors — a node that resolves the conflict, one that rebuilds, or
  any other — and the markers already recorded stay durable, outliving the conflict for a later attempt to reconcile
  against.
- **The policy is the script's.** Which policy a chunk gets is a fact about the graph it travels, and the policy is
  whatever its script does: fast-forwarding each repository's base branch onto the chunk's own commit, opening a pull
  request per repository and watching each to a clean merge, or landing no repository at all and recording some other
  outcome. "PR mode" names one such authored policy, adopted by minting a graph whose `deliver` node declares that
  policy's script in place of another's, never by an engine switch.
- **Environment retention.** The holding runner keeps the chunk's environments throughout delivery, until the outcome is
  known.

## Landing is not necessarily terminal

Landing is informational, not itself a terminal condition — only the graph's reserved terminal (`done`,
[statuses](../work/statuses.md)) is. The choice a delivery script prints on a clean landing may route straight to the
graph's reserved terminal or into a further node — the routing is authored, not fixed. A runner node routed after
landing runs in the holding runner's still-held environment; the terminal is reached by whatever choice the authored
routing eventually carries the chunk to.
