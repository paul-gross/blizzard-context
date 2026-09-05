# Statuses

What each status means, and the condition a chunk in that state derives it from. Spoke of the [work hub](../work.md).

A chunk has exactly one status at a time — a derived condition, checked in fixed precedence, never stored. The exact
fact vocabulary and derivation queries live in the code.

- **`not_ready`** — minted and resting: visible on the board, never claimed; an explicit promote moves it to `ready`.
- **`ready`** — ingested and unclaimed: in the hub's queue with no live route.
- **`running`** — claimed by a runner and being worked.
- **`delivering`** — in the hub's own hands: queued for or undergoing delivery, or awaiting an external merge — the
  runner keeping its environments until the outcome is known.
- **`paused`** — held on an operator's per-chunk pause fact: on a live route the runner kills the worker but keeps the
  lease, route, epoch, environments, and retry budget so resume respawns in place, while an unclaimed chunk is withheld
  from the queue. A pause is admitted at every status but `done`, `stopped`, and `delivering` — a delivery already in
  the hub's own hands runs to its outcome — and a resume is never refused. Ranks below the human-gated statuses and
  above `delivering` and `running` ([../execution/pause.md](../execution/pause.md)).
- **`waiting_on_human`** — parked on invited human input — an open ask or unresolved gate decision
  ([../humans/asks.md](../humans/asks.md), [../humans/gates.md](../humans/gates.md)); the reap clock stops.
- **`needs_human`** — parked on failure: the system ran out of moves, runner- or hub-authored, and a person must requeue
  or take over ([../humans/escalation.md](../humans/escalation.md)).
- **`stopped`** — abandoned by an operator: reachable from any status but `done` and `stopped`, acquired or not,
  artifacts and history retained.
- **`done`** — terminal: the graph's reserved terminal transition, or an operator's directly recorded `chunk.completed`
  fact (chunk done, the board's Complete), reachable from any non-done status including `stopped`.

`stopped` is not necessarily final — a later hand-completion can supersede it — though neither fact is undoable: no
un-stop, no un-complete. With both a `chunk.stopped` and a `chunk.completed` fact recorded, the later one decides, ties
favoring completion.

Landing is not itself terminal: a graph may route further runner work after it before `done`
([../artifacts/delivery.md#landing-is-not-necessarily-terminal](../artifacts/delivery.md#landing-is-not-necessarily-terminal)).

Deleting or grouping an unacquired chunk is not a status: the chunk simply vanishes from every listing, the work item
remaining the durable referent.

## The blocked marking

A chunk with a standing dependency edge whose prerequisite has not reached `done` carries a **blocked marking** — a
nullable field naming that one prerequisite, read beside `status` on the chunk read and on the queue and backlog
listings. It is not a status and never gates one: a blocked chunk keeps the status it derives, the rank it holds, and
the list it lives in, and stays exactly as groupable, deletable, and editable as it was a moment earlier. The marking
names its immediate prerequisite only — where that prerequisite is itself blocked, the chain is not walked, so an
operator following the root follows the naming one hop at a time.

Only a dependent read at `not_ready` or `ready` — `PRE_CLAIM_STATUSES` — derives a marking. The marking answers why a
chunk cannot yet be claimed, and that question stops applying the moment a chunk is claimed, running, delivering,
human-gated, paused, or terminal — even though a standing edge declared while it was still pre-claim persists unreleased
through all of that. Declaring is itself only ever admitted in that same window, so the gate does not shrink what a
marking can name; it only stops repeating the answer once the question no longer holds.

A chunk currently named as another's prerequisite cannot itself be deleted while that edge stands — deletion refuses
409, naming the dependents. Deleting the *dependent* chunk is unaffected by this and stays exactly as deletable as the
sentence above already promises.

Folding a chunk away carries its standing edges onto the survivor rather than releasing them outright — the blocked
marking a dependent carries continues to resolve through the survivor after the fold, never left naming a chunk that no
longer exists.

## The neighborhood

A chunk's **neighborhood** is its own standing dependency edges one hop each way — `prerequisites` and `dependents` —
read beside the chunk itself rather than confined to the blocked marking's pre-claim window: present, and possibly
non-empty in either direction, for a chunk at any status. Each entry names a neighbor's own id, its derived status, and
whether the edge is **satisfied** — never stored, derived fresh the same way the blocked marking is: a prerequisite edge
is satisfied when that neighbor reads `done`; a dependent edge is satisfied when the chunk itself does, so every
dependent reads the same satisfaction as one another. A neighbor absent from the fleet's statuses — the same residual
race the blocked marking's conservative read guards against — still draws, unsatisfied, with a null status, rather than
being dropped. Like the blocked marking, the neighborhood takes no further hop past its own edges: a prerequisite's own
prerequisites are not walked into it.
