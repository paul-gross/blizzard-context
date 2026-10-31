# A hub action's outcome

How a pass's answer selects a routed choice, and what happens when it waits or bounces the chunk.

Parent: [../hub-nodes.md](../hub-nodes.md).

## The choice a pass answers, or a reserved wait (`bzh:hub-node-outcome-protocol`)

**Rule.** Each pass of a hub node's action answers one choice — one of the node's authored judgement choices, or a
reserved wait — or an escalation in place of one. An authored choice routes through the node's authored edges exactly
like a worker's judged choice ([../../domain/graphs/edges.md](../../domain/graphs/edges.md)); `failure` is the reserved
choice every hub node authors, and `success` is a reserved name a node authors only when its action can answer it.

A reserved wait — one of the catalogue's `RESERVED_WAITS`, `pending` or `awaiting-merge` — is neither success nor
failure: no transition happens, the poll-attempt fact is recorded, and the turn ends, yielding its flows to the next in
line. A reserved wait is machinery-reserved and never authored as one of a node's own choices; only a node whose action
can answer one may carry `poll_interval` and `poll_timeout`. After a wait, the action runs a fresh pass — skipping the
work its own markers already record ([./step-idempotence.md](./step-idempotence.md), `bzh:hub-node-step-idempotence`) —
once `poll_interval` has elapsed since the last attempt (default 30s, overridable per node). A wait itself spends no
retry and no bounce budget; only a poll timeout or an incomplete-delivery crossing does.

Exceeding `poll_timeout` (default three hours, measured from the start of the current consecutive `pending` run) stops
polling and kicks the chunk back: a bounce fact is recorded and the chunk re-routes through the node's `failure` edge. A
chunk is also kicked back when an authored edge routes to a non-terminal node while any repo among the node's own
commits has no `merged/<repo>` marker the action recorded yet. This incomplete-delivery kick-back records its bounce
fact and a `bounce-envelope` artifact but lets the chunk travel the authored choice's own edge — it is detected from the
landed-marker fact, never from the choice name, so no outcome name is privileged. Either kick-back escalates to
`needs_human` once the node's `bounce_cap` (default 5, overridable per node) is crossed. An answer the node authors no
edge for escalates the chunk at once, naming the choice, rather than re-polling.

An `awaiting-merge` poll yields the flows while a person decides a parked change; it is not charged against the pending
run's timeout. The repository's separate park timeout applies to the review wait.

**Why.** A typed answer leaves no parsing to go wrong, and fixing "an authored choice, or a reserved wait" as the whole
vocabulary lets mint-time validation prove every answer routes. The shared bounce-cap ladder keeps a stuck or
repeatedly-conflicting delivery from bouncing a chunk forever.

**Detect.** A node authoring `pending` or another reserved wait as one of its own choices; an action answering a choice
outside its catalogued answers; poll keys on a node whose action can never wait.

**Do.**

- `land` answers `conflict` before its push stage ever starts, so nothing lands when one repo is dirty.
- `land` answers `pending` while it waits for an unsettled PR; the action owns its forge-state decisions and other
  outcomes.

**Don't.** A graph authoring a `pending` choice with an edge back to its own node — the wait is the machinery's, and the
mint-time validator refuses the choice.
