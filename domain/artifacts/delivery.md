# Delivery

How a chunk's work lands, and why landing is not itself the end. A spoke of the [artifacts hub](../artifacts.md).

Delivery is graph-authored content, not built-in engine machinery: a hub node (`executor: hub` plus `action:`,
[nodes](../graphs/nodes.md)) whose declared action is the delivery policy, authoring its outcome choices exactly like a
worker node's judgement ([edges](../graphs/edges.md)).

- **Fleet-wide serialization.** One fleet-wide execution slot admits one chunk's hub node at a time — any hub node, not
  delivery specifically; a chunk finding it held tries again on a later tick. The slot is not reentrant: a chunk's own
  live run is never re-entered, and a hub node runs only while its chunk still stands at it, so a re-submitted
  completion or a hub-advance never starts a second run, nor re-runs a node the chunk has left.
- **Only a live, promoted chunk is driven.** A chunk standing at a hub node is run there only while it is promoted and
  has not ended: one resting un-promoted, or stopped or done, is never driven through it.
- **Per-repository landing, with reconciliation.** A delivery action that lands a multi-repository chunk serially per
  repository records its own `merged/<repo>` marker immediately after each push; a re-run — after a crash, or a
  kicked-back redelivery — skips every repository whose marker is already durable. The engine imposes no per-repository
  landing shape of its own, but reads the `merged/<repo>` marker convention to tell a fully-landed continuation apart
  from a genuinely incomplete delivery ([outcome protocol](../../standards/hub-nodes/outcome-protocol.md)). Even
  chunk-atomicity — checking every repository merges before pushing any — is one action's construction, not a property
  of delivery: a policy could advance repositories one at a time and accept a partial land, recovered the same way, per
  repository.
- **Delivery references.** A policy that opens a PR records it as a `delivery-pr/<repo>/<number>` marker — durable,
  idempotent, written mid-run as soon as the PR is known, before any wait or merge; it is a review reference, not a
  signal that a person must merge. A replacement PR gets its own marker, so the latest recorded reference for a repo —
  latest in the order the references were durably written — is open and superseded references remain closed history; a
  reference recorded under the bare `delivery-pr/<repo>` name is read the same way. Where two references' write order
  was never recorded and they share one write instant, which one is latest cannot be known; the read's deterministic
  pick is not evidence of the later write. The repo's `merged/<repo>` marker records the landed revision, not the
  submitted branch tip. A landing that changes nothing lands at the target branch's revision, so that revision is its
  landed revision. A delivery that cannot establish its landed revision records no landing for that repository. A policy
  that deliberately parks for a person's merge may author an `awaiting-external-merge` marker in the same delivery epoch
  as its PR reference; only that marker signals a human merge wait. The hub projects these markers alongside per-repo
  landing facts: closed PRs stay in history, while landed rows name only repos with a landed revision. What each
  marker's content carries is the hub action contract's to state
  ([action purity](../../standards/hub-nodes/action-purity.md)).
- **Conflict is a judged, authored outcome**, not an engine special case: a dirty repository is one of the action's own
  outcome choices, routed to whatever edge the graph authors — a node that resolves the conflict, one that rebuilds, or
  any other — and the markers already recorded stay durable, outliving the conflict for a later attempt to reconcile
  against.
- **The policy is the action's.** Which policy a chunk gets is a fact about the graph it travels, and the policy is
  whatever its action does. A graph adopts a policy by declaring its action in `deliver`, never by an engine switch;
  [feature delivery](../../workflows/feature-delivery.md) describes the shipped policy. Each commit pointer is resolved
  to its own repository record; whether a chunk may mix forges, owners, base branches or credentials is the policy's to
  decide.
- **A chunk delivers one project's work.** The chunk belongs to exactly one project, and the repositories it lands in
  are the tenant's records, which a project reaches only through a link ([../projects.md](../projects.md) §What a
  project owns, and what it links). A chunk lands only in repositories its project links, as the links stand when the
  landing step begins: a chunk commit naming a repository its project does not link is refused before any push, naming
  the repository and the project ([../projects.md](../projects.md) §Where a chunk may land).
- **Environment retention.** The holding runner keeps the chunk's environments throughout delivery, until the outcome is
  known.

## Landing is not necessarily terminal

Landing is informational, not itself a terminal condition — only the graph's reserved terminal (`done`,
[statuses](../work/statuses.md)) is. The choice a delivery action answers on a clean landing may route straight to the
graph's reserved terminal or into a further node — the routing is authored, not fixed. A runner node routed after
landing runs in the holding runner's still-held environment; the terminal is reached by whatever choice the authored
routing eventually carries the chunk to.
