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
  from the queue. Ranks below the human-gated statuses and above `delivering` and `running`
  ([../execution.md](../execution.md)).
- **`waiting_on_human`** — parked on invited human input — an open ask or unresolved gate decision
  ([../humans.md](../humans.md)); the reap clock stops.
- **`needs_human`** — parked on failure: the system ran out of moves, runner- or hub-authored, and a person must requeue
  or take over ([../humans.md#escalation](../humans.md#escalation)).
- **`stopped`** — abandoned by an operator: reachable from any point after acquisition, artifacts and history retained.
- **`done`** — terminal: the graph's reserved terminal transition, or an operator's directly recorded `chunk.completed`
  fact (chunk done, the board's Complete), reachable from any non-done status including `stopped`.

`stopped` is not necessarily final — a later hand-completion can supersede it — though neither fact is undoable: no
un-stop, no un-complete. With both a `chunk.stopped` and a `chunk.completed` fact recorded, the later one decides, ties
favoring completion.

Landing is not itself terminal: a graph may route further runner work after it before `done`
([../artifacts.md#landing-is-not-necessarily-terminal](../artifacts.md#landing-is-not-necessarily-terminal)).

Discarding or grouping an unacquired chunk is not a status: the chunk simply vanishes from every listing, the work item
remaining the durable referent.
