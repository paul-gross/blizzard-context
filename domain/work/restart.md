# Restart

A restart is an operator's forced move of a chunk onto a node, now — its own recorded fact, neither a transition nor a
migration. Spoke of the [work hub](../work.md).

It is an event, not an intent: unlike a standing intended migration ([./migration.md](./migration.md)), a restart has
happened when the call returns — nothing to cancel, and a second restart is a second move, not a replacement. The move
completes on return: a chunk mid-graph on a superseded mint reaches the current one without running a node-step to
manufacture an intent's transition. Where a chunk stands is a restart's to change; which graph it is on, a migration's
to record.

## Where it lands

Unnamed, it lands on the chunk's current node — the common case, restart this step on clean context — and crossing
graphs, that node name is matched onto the target: auto migration's landing rule, with an unmatched name refused (see
[What it refuses](#what-it-refuses)). A named node resolves by name against the landing graph — the named target when
crossing, the chunk's own otherwise — as a forced intent's landing resolves
([./migration.md#standing-intent](./migration.md#standing-intent)). Only a never-moved chunk legally resolves to an
entry node — standing nowhere, the entry is where it would have started.

## What it does

It preempts by raising the fence: the minted epoch belongs to [../execution/fencing.md](../execution/fencing.md), the
displaced attempt's next state-advancing write is rejected as stale (`bzh:epoch-fencing`), and the holding runner tears
it down at next reconciliation — nothing relies on the worker having really died. The claim survives
([../execution/acquisition.md](../execution/acquisition.md)), so the same runner re-enters the node with the work
already on disk. A chunk with no claim moves just as well and waits in the queue at its new node.

The re-entry starts on a freshly minted session — handing the step clean context is the point — not the session the
node's declaration would have resumed, under the target node's currently declared configuration (its session facet,
[../graphs/nodes.md](../graphs/nodes.md)). Freshness derives from the move's own fact: every re-entry into the forced
visit is fresh, not only the first. Across graphs the re-entry is stamped with the model, effort, and compaction window
the landing graph declares, never the departed graph's. The landed node's own executor governs, exactly as for an
ordinary transition or a migration's landing ([../graphs/nodes.md](../graphs/nodes.md)).

The move consumes whatever parked or re-aimed the chunk: an open ask is answered (exactly one answer ever exists — an
earlier answerer still wins), an open gate decision closes, and an open escalation is superseded as by a requeue
([../humans/asks.md](../humans/asks.md), [../humans/gates.md](../humans/gates.md),
[../humans/escalation.md](../humans/escalation.md)). A cross-graph move also clears any standing intended migration
([./migration.md](./migration.md)); nothing survives to re-park or re-aim the chunk at a node it no longer stands on.

It spends no retry budget: the budget counts failed attempts and a preempted attempt was superseded, not failed —
restarting a stuck step never carries it toward `retries.exhausted`. Durably recorded artifacts stay; a step's artifacts
land atomically with its judged transition ([./transitions.md](./transitions.md), [../artifacts.md](../artifacts.md)),
so an interrupted step has none to keep — only landed steps do.

## What it records

A restart naming another graph writes a migration fact for the re-pin and a restart fact for the forced clean re-entry,
and the two land atomically — one instant, one epoch, the restart the newer — so no crash lands one half without the
other. Naming no other graph, it is the restart fact alone; a refused restart writes nothing.

## What it defers

A pause suppresses rather than refuses it: the chunk stays parked and the move is honored on the tick after the pause
lifts. An open takeover also suppresses it indefinitely — the person is inside that session, and killing it under them
is worse than a pending move. The hub holds no takeover state to refuse with — deferral at the runner is the whole
mechanism — and the chunk reads as moved while the human works at the stale epoch
([../humans/takeover.md](../humans/takeover.md)).

## What it refuses

- A terminal chunk: there is nothing to re-enter.
- An unknown or retired target graph, or the chunk's current pin — the last a plain same-graph restart with a redundant
  flag.
- A named node the landing graph does not carry — and, crossing, an unmatched current node name: the mistake is never
  quietly replaced with the target's entry node.
- With no node named, a chunk standing on a node its own graph lacks: rewinding to entry would discard a real position;
  name a reachable node instead.
