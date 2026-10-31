# Delivery

How a chunk's work lands, and why landing is not itself the end. A spoke of the [artifacts hub](../artifacts.md).

Delivery is graph-authored content, not built-in engine machinery: a hub node (`executor: hub` plus `action:`,
[nodes](../graphs/nodes.md)) whose declared action is the delivery policy, authoring its outcome choices exactly like a
worker node's judgement ([edges](../graphs/edges.md)).

- **Resources and flows.** A hub step holds the resources it acts on — for a landing, each target branch it lands on —
  and each resource has one flow: an arrival-ordered line of the visits that hold it. A visit is submitted to its flows
  when its chunk reaches the hub node, and runs as a turn once it is next on every flow it holds, so steps on different
  branches run side by side, chunks on one branch land in arrival order, and a step holding no branch waits on none. A
  `pending` answer ends the turn and yields the branch to the next in line until its poll is due. A visit takes one turn
  at a time, and a turn runs only while its chunk still stands at the node, so a re-submitted completion or a
  hub-advance never starts a second run, nor re-runs a node the chunk has left.
- **Only a `delivering` chunk is driven.** A chunk standing at a hub node is submitted to its flows and takes turns
  there only while it is `delivering` ([../work/statuses.md](../work/statuses.md)): a paused chunk waits for its resume,
  and one escalated, stopped, or done is never driven through it.
- **Per-repository landing, with reconciliation.** A delivery action that lands a multi-repository chunk serially per
  repository records its own `merged/<repo>` marker immediately after each push; a re-run — after a crash, or a
  kicked-back redelivery — skips every repository whose marker is already durable. The engine imposes no per-repository
  landing shape of its own, but reconciles landed and matching no-code resolutions to distinguish finished work from
  incomplete delivery ([outcome protocol](../../standards/hub-nodes/outcome-protocol.md)). Even chunk-atomicity —
  checking every repository merges before pushing any — is one action's construction, not a property of delivery: a
  policy could advance repositories one at a time and accept a partial land, recovered the same way, per repository.
- **Delivery references.** A policy that opens a PR records it as a `delivery-pr/<repo>/<number>` marker — durable,
  idempotent, written mid-run as soon as the PR is known, before any wait or merge; it is a review reference, not a
  signal that a person must merge. A replacement PR gets its own marker, so the latest recorded reference for a repo —
  latest in the order the references were durably written — is open and superseded references remain closed history; a
  reference recorded under the bare `delivery-pr/<repo>` name is read the same way. Where two references' write order
  was never recorded and they share one write instant, which one is latest cannot be known; the read's deterministic
  pick is not evidence of the later write. The repo's `merged/<repo>` marker records a real landed revision, not the
  submitted branch tip. A delivery that cannot establish its landed revision records no landing for that repository. A
  policy that deliberately parks for a person's merge may author an `awaiting-external-merge` marker in the same
  delivery epoch as its PR reference; only that marker signals a human merge wait. The hub projects these markers
  alongside per-repo landing facts: closed PRs stay in history, while landed rows name only repos with a landed
  revision. What each marker's content carries is the hub action contract's to state
  ([action purity](../../standards/hub-nodes/action-purity.md)).
- **No code to land.** An empty commit set completes without a landing. A submitted repository resolves without a merge
  only when its submitted commit is proven contained in the intended base and its current branch and head are safe; an
  unreadable or refused comparison is not proof. Its durable no-code evidence matches the current declaration, so replay
  skips that work but a changed declaration does not. Resolved repositories need no flow resource and count as finished
  for reconciliation, not as landings. A PR reference for a no-code resolution is history, not an open landing wait.
  Mixed delivery records landing facts, revisions, events, and traces only for repositories actually merged.
- **Conflict is a judged, authored outcome**, not an engine special case: a dirty repository is one of the action's own
  outcome choices, routed to whatever edge the graph authors — a node that resolves the conflict, one that rebuilds, or
  any other — and the markers already recorded stay durable, outliving the conflict for a later attempt to reconcile
  against.
- **The policy is the repository's.** How a change lands is a fact about the repository it lands in: each repository
  record carries a landing policy, and the `land` action runs each repository's own. A policy is accepted only on a
  forge that offers its required capabilities. The policies are:

  | Policy            | Landing behavior                                                                                      |
  | ----------------- | ----------------------------------------------------------------------------------------------------- |
  | `merge-on-checks` | Default; opens a change, updates it from the base, and merges when checks are green.                  |
  | `fast-forward`    | Checks the work revision, or a proven merge candidate when the base diverged, then advances the base. |
  | `park`            | Opens a change for a person to merge and observes its outcome.                                        |

  The graph still decides where landing happens, by declaring its action in `deliver`;
  [feature delivery](../../workflows/feature-delivery.md) describes the shipped graph. Each commit pointer is resolved
  to its own repository record, which names the forge record it lands on, so a chunk may mix forges, owners, base
  branches and credentials.
- **Landing follows the project's order.** A multi-repository visit steps every unlanded repository's policy, then lands
  them in its project's landing order ([../projects.md](../projects.md) §Where a chunk may land). The order and each
  repository's policy are the visit's terms, taken at its first turn and kept through every retry and restart, so an
  edit made while a visit waits reaches only the next visit.
- **A chunk delivers one project's work.** A chunk lands only in repositories its project links, and a commit naming one
  it does not link is refused before any push — [../projects.md](../projects.md) §Where a chunk may land owns the rule,
  the moment the links are read, and the refusal.
- **Environment retention.** The holding runner keeps the chunk's environments throughout delivery, until the outcome is
  known.

## Landing is not necessarily terminal

Landing is informational, not itself a terminal condition — only the graph's reserved terminal (`done`,
[statuses](../work/statuses.md)) is. The choice a delivery action answers on a clean landing may route straight to the
graph's reserved terminal or into a further node — the routing is authored, not fixed. A runner node routed after
landing runs in the holding runner's still-held environment; the terminal is reached by whatever choice the authored
routing eventually carries the chunk to.
