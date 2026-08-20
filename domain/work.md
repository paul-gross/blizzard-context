# Work — the chunk and its lifecycle

The unit of work at the center of the model: the chunk, the statuses it derives, the transition record it moves by, and
the migration that re-pins it across graphs. Definitions, with the enforceable invariant written in the slot skeleton
owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`). Part of the [domain model](./index.md).

## Chunk

The hub's unit of orchestrated work: it wraps one or more backlog items from the backing work source by work ref,
travels a workflow graph, and accumulates artifacts, questions, and decisions as it goes.

- **The work item is the durable referent; the chunk is ephemeral.** An unacquired chunk may be discarded or grouped
  away, and re-ingesting the same item mints a fresh chunk — nothing of value lives only on an unstarted chunk. An item
  already wrapped by a live chunk cannot be ingested again.
- **The item's contents are never stored.** A chunk holds work refs; reads pass through to the backing work source.
- **A landed chunk's work items are closed at their own source.** Once a chunk has landed, its work refs are closed
  through their own work source's binding — best effort and eventually convergent, not immediate or atomic with the
  landing itself, and independent of whether the chunk continues to run afterward. A chunk that never lands closes
  nothing, whether or not it is later abandoned; one that lands and is only later abandoned still closes, because it was
  in fact delivered.
- **Pinned to exactly one immutable graph, once it has moved.** The pin is set at mint from a default and, while the
  chunk is unclaimed and has not yet moved, is a plain editable selection — the operator's pre-flight window to repin
  it, open across `not_ready` and unclaimed `ready` alike. Once the chunk has moved the pin is immutable and changes
  only when a [migration](#migration) applies — never silently. A chunk detached back to `ready` mid-graph is **past**
  that window, not back inside it: it stands on a node another graph need not contain, so only a migration, which
  resolves where it lands, can move it.
- **The default model preference and effort are chunk properties alongside the graph pin.** Both are minted **empty** —
  a fresh chunk expresses no preference at all, so the runner's own default applies — and are editable for as long as
  the chunk is unclaimed, immutable thereafter: a wider window than the graph pin's, since a default names no node to be
  stranded on. Like the pin, plain properties rather than a fact log. They are *defaults*, not a selection: they say
  what a surface that declares nothing inherits, and a graph's own [declared session](./graphs.md#declared-sessions)
  outranks them field by field. The vocabulary is the declaration's — a prioritized preference list of capability tiers
  or harness-native names, and a single effort value — so what a chunk default expresses and what a session declaration
  expresses are the same kind of thing.
- **The intended migration is a chunk property alongside the graph pin and the defaults.** Nullable — `null` when no
  migration is queued, otherwise an intent naming a mode (`auto` or `forced`), a target graph, and, for a forced intent,
  a target node. Unlike the graph pin's and the defaults' pre-flight windows, it is set, overwritten, or cleared by the
  operator at any non-terminal status. Applying it re-pins the chunk and clears the intent atomically, in the same write
  as the migration ([migration](#migration)); an eager cross-graph [restart](#restart) clears it in its own write the
  same way, by superseding it rather than firing it.
- **Nothing on it is a stored status.** Its current node derives from its newest movement fact — a transition, a
  [migration](#migration)'s landing, or a [restart](#restart)'s target — and its status derives from its recorded facts
  (`bzh:facts-not-status` in [../architecture/system-shape.md](../architecture/system-shape.md)).
- **Held by at most one runner at a time** — see [execution.md](./execution.md) for acquisition, tenure, and fencing.

## Statuses

The derived conditions a chunk can be in. A chunk has exactly one status at a time — the conditions are checked in a
fixed precedence, and none is ever stored. The exact fact vocabulary and derivation queries live in the code. This table
is the behavioral meaning.

| Status             | Meaning                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `not_ready`        | Minted and resting — visible on the board, never claimed. The chunk's graph pin and default model/effort are editable in place here, and stay so while it rests `ready` unclaimed — the pin only until the chunk first moves (see [Chunk](#chunk)); an explicit promote moves it to `ready`.                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `ready`            | Ingested into a chunk and unclaimed — in the hub's queue with no live route.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `running`          | Claimed by a runner and being worked.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `delivering`       | In the hub's own hands — queued for or undergoing delivery, or awaiting an external merge; the holding runner keeps its environments until the outcome is known.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `waiting_on_human` | Parked on **invited** human input — an open ask or an unresolved gate decision ([humans.md](./humans.md)); the reap clock is stopped.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `needs_human`      | Parked on **failure** — the system ran out of moves, runner- or hub-authored ([humans.md](./humans.md) §Escalation); a person must requeue or take over.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `paused`           | Held on an operator's per-chunk pause fact — on a live route the runner kills the worker but keeps the lease, route, epoch, environments, and retry budget so resume respawns in place; an unclaimed chunk is withheld from the queue instead. A restart recorded meanwhile still moves it (§Restart). Ranks below the human-gated statuses and above `delivering`/`running` ([execution.md](./execution.md)).                                                                                                                                                                                                                                                                                                                                  |
| `stopped`          | Abandoned by an operator — reachable from any point after acquisition, artifacts and history retained. Not necessarily final: an operator's later hand-completion (see `done`) can still supersede it, though neither fact is itself undoable (no `un-stop`, no `un-complete`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `done`             | Terminal — the chunk reached the graph's reserved terminal transition, or an operator wrote a `chunk.completed` fact directly (`chunk done` / the board's Complete, issue #294), reachable from any non-`done` status including `stopped`. Reaching it via the graph is ordinarily immediate once the commit artifacts land, but a graph may instead route further runner work after landing before reaching it, so landing itself is not necessarily terminal ([artifacts.md](./artifacts.md) §Landing is not necessarily terminal). When a chunk carries both a `chunk.stopped` and a `chunk.completed` fact, the later-recorded one decides, ties favoring the completion — so `done` can still follow a `stopped` chunk, never the reverse. |

Discarding or grouping an unacquired chunk is not a status: the chunk is simply gone from every listing, because the
work item remains the durable referent.

## Transition

One entry in a chunk's append-only movement record: the fact that a judgement at a node's exit selected an edge and the
chunk moved along it.

- **Every transition is fully formed.** The judgement is what selects the edge — the worker's verdict, the hub's own
  machinery at a hub node, or a human's choice at a gate — so there is no unjudged movement and no transition without a
  judgement.
- **At a gate there is no transition until the human decides.** The node-step's completion lands as an open decision,
  and the resolving choice writes the transition referencing it ([humans.md](./humans.md)).
- **Atomic with the step's artifacts.** A node-step's transition and its artifacts are committed as one write — a
  rejected transition's artifacts never exist ([artifacts.md](./artifacts.md)).
- **Fenced.** A transition carries its attempt's epoch and a stale one is rejected, never recorded (`bzh:epoch-fencing`
  in [execution.md](./execution.md)) — the movement record only ever advances on a live attempt's say-so.
- **Authored by the holder.** The holding runner reports the chunk's transitions; the hub's own executor authors them
  for hub-executed nodes.

## A migration is never a transition (`bzh:migration-not-transition`)

**Rule.** Movement between graphs, for a chunk that has moved at all, is a **migration** — its own recorded fact
re-pinning the chunk — never a transition: a transition moves a chunk along an edge within its pinned graph, and no edge
crosses graphs. While a chunk is unclaimed and has not yet moved, its graph pin (and its default model/effort) is a
plain editable property, not a pin this rule governs — that window closes at the chunk's first movement.

**Why.** Transitions are judged, fenced movement within one immutable definition; letting one span graphs would re-route
in-flight work without the explicit intent, record, and fencing that migration provides. Before the chunk has moved at
all, an *edit* re-routes no in-flight attempt and nothing a migration's fencing protects — repinning is pre-flight
selection, not movement, and the chunk stands on no node a re-pin could strand it away from. A chunk on its first
node-step has moved nowhere yet is claimed and running, which is why an eager restart re-pinning it is movement and
records one.

**Detect.** A design or change in which a transition's two nodes belong to different graphs, an edge targets a node of
another graph, or a chunk **that has already moved** has its graph pin change with no migration record — a re-queued
chunk resting `ready` included, which is where a status-only editability check lets one through.

**Do.** Re-pin via a migration record — either immediately, as an authored judgement choice's own trigger, landing on
the departed node's name-matched node or the target's entry node when no name matches; or later, deferred to the chunk's
next transition, via its own `intended_migration` property, landing on that transition's own destination node or a named
node for a forced intent; or, for an operator's eager cross-graph restart, now, on the node that restart resolves
(§Restart below) — only the last of those mints a fresh epoch, and in every case the landed node's own executor then
governs the chunk's status exactly as it would for an ordinary transition (§Migration below). Edit an unmoved chunk's
graph pin, or an unclaimed chunk's default model/effort, in place — that editing path writes no migration record. An
operator's eager restart is not that path: it is movement whatever the chunk has done before, so it records the re-pin
even for a chunk that has never moved.

**Don't.** Add a cross-graph edge, or update the pinned graph of a chunk that has already moved in place with no record
of the re-pin.

## Migration

The explicit re-pin of a chunk from one immutable graph to another, recorded as its own fact — never a transition
(`bzh:migration-not-transition`).

- **Intent and fact are separate.** An authored judgement choice about to be taken, or a chunk's own standing intended
  migration (see [Chunk](#chunk)), is intent — not yet a movement; the migration *record* written when one actually
  applies is the fact. The intent is a plain mutable property, like the graph pin and the defaults, not a fact log:
  setting it overwrites whatever was set before, and setting it to nothing clears it, so a chunk holds at most one live
  intent at a time, with no history of superseded ones to reconcile.
- **A judgement choice can trigger it immediately.** A node's authored judgement choice may target another graph rather
  than a sibling node (`to: graph:<name>` in [graphs.md](./graphs.md)); taking that choice is itself the trigger — the
  worker's verdict ends the attempt at that node and records one migration fact re-pinning the chunk (and, when the
  choice names a `model:`, re-pinning that as the chunk's default model preference) and landing it at the target's
  landing node (§Landing is by name below). The authored **choice** carries the cross-graph target, but when taken it
  records a **migration**, never a cross-graph transition, so `bzh:migration-not-transition` holds. A choice whose
  target names no enabled graph escalates the chunk to `needs_human` rather than dropping the movement.
- **A gate-resolved migration still closes the gate's decision.** When a *human gate's* resolved choice is itself the
  migrating choice, the migration closes that decision — or, when its target is unresolvable and the chunk escalates
  instead, the escalation does. A migration records no transition (`bzh:migration-not-transition`), so without this the
  decision would derive open forever ([humans.md](./humans.md) §Gate decision) and the chunk would never leave the gate.
- **A chunk's own intended migration can trigger one later, at its next transition.** Unlike an authored choice, which
  fires as its own verdict, a standing intent is consulted — never applied eagerly — when the chunk's next transition is
  judged, through the same path an ordinary worker verdict or a resolved gate decision takes; a chunk advancing through
  a hub node's own exit is not consulted this way, so an intent set on a chunk already in the hub's hands waits for its
  next worker-or-gate transition. An **auto** intent migrates only when that transition's own destination node name also
  exists on the target graph, landing on that same-named node; otherwise the transition applies unchanged on the current
  graph and the intent stays set for the transition after. A **forced** intent migrates unconditionally to its own named
  target node, regardless of what that transition's own destination would have been. When the intent's target graph
  cannot be resolved at consult time — never minted, or retired since the intent was set — the migration is skipped
  exactly like an auto no-match: the transition applies unchanged and the intent stays set, visible for the operator to
  cancel or re-aim. An operator's eager cross-graph restart clears a standing intent in the same write that re-pins the
  chunk, the way a fired intent clears itself: an eager move supersedes a parked one rather than leaving it to fire
  again later.
- **A graph can carry a standing follow-latest policy, which migrates chunks with nobody having asked.** A graph name is
  minted repeatedly — each mint a separate immutable definition — and a chunk stays pinned to the one it started on.
  **Follow-latest** is a standing policy saying chunks pinned to this graph drift to the newest enabled mint of the same
  *name* at their next transition, so a workflow edit reaches work already in flight instead of stranding it until each
  chunk is migrated by hand. It resolves at two levels: the graph's own setting where it states one, otherwise a
  fleet-wide default; a graph that states nothing inherits. The fleet-wide default is **off**, so adopting the policy is
  deliberate.
  - **An operator's own intent outranks it.** A chunk carrying a standing intended migration is never moved by the
    policy — including on a transition where that `auto` intent falls through for want of a name match. Someone who
    aimed a chunk has said where it goes.
  - **It only ever moves a chunk forward, and never past the end.** A chunk already on the newest mint, or one whose
    every newer mint is retired, is left alone — no error, no fact. Neither is a chunk whose own mint has been retired,
    where name resolution would otherwise hand back an *older* mint and rewind it. And a transition to the terminal is
    not followed at all: a chunk that has finished has no next node-step for a newer definition to govern, so following
    there would restart the whole workflow instead of completing it.
  - **The policy governs one hop, not a lineage.** It is read off the mint a chunk is pinned to, and the chunk lands on
    a newer mint carrying its own (inherited-by-default) setting — so a graph-level policy applies once. Sustaining the
    drift across a lineage is what the fleet-wide default is for.
- **No transition-borne trigger interrupts the attempt that produced it, or mints a fresh epoch at migration time.** The
  verdict carrying a migrating transition is accepted exactly as an ordinary one would be, and nothing about the
  submitting attempt is fenced or redone — a fresh epoch is only ever minted by a later claim, the same as for any other
  route-released re-queue. That holds for an authored choice, a standing intent and the follow-latest policy alike. They
  differ only in **where** they land — each anchors a different name, per §Landing is by name below: an authored choice
  lands on the departed node's own name-matched node because that node diverted rather than completed its own
  destination; a standing intent lands on the transition's own destination node (auto) or its own named node (forced),
  and the follow-latest policy on that same destination name, because in each of those the transition did complete
  normally and only where it lands is redirected.
- **The operator's eager cross-graph restart is the one trigger that does both.** It is not borne by a transition at
  all: it fences the running attempt out and mints its own epoch, because that is what a restart is (§Restart below).
  The re-pin is still a migration record — that is the half this section owns — and the forced clean re-entry is the
  restart's own fact beside it, both written in one store transaction, so a crash can never leave a chunk re-pinned but
  not moved, or moved but not re-pinned. Where it lands is the anchor question below, not this bullet's to answer.
- **Landing is by name.** Landing resolves a node by **name** on the target graph (`bzh:ids-exact-names-correlate` in
  [graphs.md](./graphs.md)) — the trigger picks which name is the anchor: an authored choice anchors the departed node's
  name, falling back to the target's entry node when no match; a standing intent anchors the transition's own
  destination node name for `auto` (no entry fallback — an unmatched name just leaves the transition unchanged, per the
  bullet above), or the intent's own named node for `forced`; an operator's eager restart anchors its own named node,
  else the chunk's **current** node name — with no entry fallback either way, because an operator naming where a chunk
  goes is told when that name is not there, and the one chunk that legally resolves to an entry node is one that has not
  moved at all (§Restart below); the follow-latest policy anchors that same destination name **with** the entry
  fallback, because unlike an intent it has nothing to stay set for — falling through would defer a standing policy
  forever, on exactly the graph whose shape changed enough to drop the node. **The landed node's own `executor` then
  governs exactly as it does for an ordinary transition** ([graphs.md](./graphs.md) §Node): landing on a hub-executed
  node derives `delivering`, not `ready` — the chunk stays in the hub's own hands, driven by the hub's own executor,
  same as any other arrival at that node — while landing on a runner node re-queues `ready`. This keys on the landed
  node's `executor`, never its name; the shipped `deliver` node is one hub-executed instance a migration can land on,
  not a special case.
- **An `auto` intent is a per-chunk request; a follow-latest policy is not.** The two are the reason a migration records
  **what moved the chunk**, not just that it moved: an authored choice, an operator's intent, an operator's eager
  restart, and the standing policy are otherwise indistinguishable in history, and the policy is the only one nobody
  asked for. Same-name is no tell either — an operator aiming an intent *by name* also lands on a newer same-name mint.
  So a chunk found on a graph it did not start on can always be traced to what put it there.

## Restart

An operator's forced move of a chunk onto a node, **now** — its own recorded fact, neither a transition nor a migration.

- **It is an event, not an intent.** Unlike a standing intended migration (§Migration above), consulted at the chunk's
  next transition, a restart has already happened when the call returns: there is nothing to cancel and nothing to
  overwrite, and a second one is a second move rather than a replacement of the first.
- **It can cross graphs, and re-pinning is still migration's job.** *Where* a chunk stands is a restart's to change;
  *which* graph it is on is a migration's to record. So a restart that names another graph is **both**: one migration
  fact for the re-pin and one restart fact for the forced clean re-entry, written together in a single store
  transaction, at one instant and one epoch, with the restart the newer of the two — so the chunk stands where the
  restart put it, on the graph the migration pinned it to, and no crash can land one half without the other. Naming no
  other graph, it is the restart fact alone. Either way there is nothing to wait for: unlike an intended migration, the
  move has happened when the call returns, so a chunk standing mid-graph on a superseded mint reaches the current one
  without first running a node-step to manufacture the transition an intent would need.
- **Raising the fence is how it preempts.** The epoch the move mints belongs to [execution.md](./execution.md) §Lease
  and epoch; what follows from it here is that the displaced attempt's next state-advancing write is rejected as stale
  (`bzh:epoch-fencing`) and the holding runner tears the attempt down on its next reconciliation. Nothing relies on the
  worker having really died.
- **The claim survives it** — what a route, a tenure and its environments outlive belongs to
  [execution.md](./execution.md) §Acquisition and the route. The consequence here: the same runner re-enters the node
  with the work already on disk. A chunk with **no** claim moves just as well, and simply waits in the queue at its new
  node for whoever claims it next.
- **Artifacts already durably recorded stay recorded.** Nothing rewinds what the chunk has produced. That is a narrower
  claim than it sounds: a step's artifacts land atomically with the transition it is judged into (§Transition,
  [artifacts.md](./artifacts.md)), so a step the move interrupts has no artifacts to keep — only the steps that already
  landed do.
- **It does not spend the node's retry budget.** A node's budget counts the attempts it *failed*, and a preempted
  attempt was superseded rather than failed — so restarting a stuck step never carries it toward `retries.exhausted`,
  and an operator cannot escalate the chunk they are rescuing by rescuing it too often.
- **The re-entry starts on a freshly minted session.** Restarting is how an operator hands a step clean context, so the
  node is entered on a new session rather than the one its declaration would have resumed, under the target node's
  currently declared configuration — the second override of the node's own `session` facet ([graphs.md](./graphs.md)
  §Node). That freshness derives from the move's own fact, so it holds for every re-entry into the forced visit, not
  only the first. Across graphs, "the target node's" means the **target graph's**: the re-entry is stamped with the
  model, effort and compaction window the graph it landed on declares, never the departed graph's.
- **Whatever parked or re-aimed the chunk is consumed with the move.** An open ask is answered — exactly one answer ever
  exists, so a person who already answered still wins — an open gate decision is closed by the move itself, and an open
  escalation is superseded exactly as a requeue supersedes one ([humans.md](./humans.md)). A cross-graph move also
  clears any standing intended migration (§Migration above). Nothing may survive to re-park or re-aim the chunk at a
  node it is no longer standing on.
- **The landed node's own `executor` governs**, exactly as it does for an ordinary transition or a migration's landing
  ([graphs.md](./graphs.md) §Node).
- **Where it lands.** A named node is resolved **by name** against the graph the move lands on — the named target graph
  when it crosses, the chunk's own otherwise — the way §Migration resolves its own forced landing. Unnamed, the move
  lands on the chunk's current node: restart this step, on clean context, is the common case, and across graphs that
  same node **name** is matched onto the target, which is `auto` migration's own landing rule.
- **What it refuses**, writing nothing either way:
  - **A terminal chunk** — there is nothing to re-enter.
  - **A named node the landing graph does not carry**, and, when it crosses, **a current node name the target graph does
    not match**. The operator said where the chunk goes; an unmatched name is a mistake rather than a landing to fall
    back from, and the target's entry node is never quietly substituted for it.
  - **A chunk standing on a node its own graph does not carry**, with no node named. Rewinding it to the entry would
    discard a real position rather than resolve it; naming a reachable node is the way out. The one chunk that legally
    resolves to an entry node is one that has **not moved at all** — it stands on nowhere, and the entry of whichever
    graph it lands on is where it would have started.
  - **A target graph that is unknown, retired, or the chunk's own current pin.** The last of those is the plain
    same-graph restart, asked for with a redundant flag rather than a move to make.
- **Two conditions suppress it, and neither refuses it.** A chunk **pause** outranks it: the chunk stays parked and the
  move is honored on the tick after the pause lifts. An open **takeover** defers it indefinitely — the person is inside
  that session, and killing it out from under them is worse than leaving the move pending. The hub holds no takeover
  state to refuse the request with, so deferral at the runner is the whole mechanism, and the chunk reads as moved while
  the human works on at the stale epoch ([humans.md](./humans.md) §Takeover).

## See also

- [./graphs.md](./graphs.md) — the immutable definition a chunk travels, and the node/edge/executor shape a migration's
  landing keys on.
- [./execution.md](./execution.md) — who holds a chunk, the lease behind each node-step attempt, and the epoch its
  transitions are fenced by.
