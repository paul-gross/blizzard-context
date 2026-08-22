# Migration — re-pinning a chunk across graphs

The invariant below is written in the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`). Part of
[work.md](../work.md), the chunk and its lifecycle.

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
([restart.md](./restart.md)) — only the last of those mints a fresh epoch, and in every case the landed node's own
executor then governs the chunk's status exactly as it would for an ordinary transition
([migration.md](./migration.md)). Edit an unmoved chunk's graph pin, or an unclaimed chunk's default model/effort, in
place — that editing path writes no migration record. An operator's eager restart is not that path: it is movement
whatever the chunk has done before, so it records the re-pin even for a chunk that has never moved.

**Don't.** Add a cross-graph edge, or update the pinned graph of a chunk that has already moved in place with no record
of the re-pin.

## The migration fact

The explicit re-pin of a chunk from one immutable graph to another, recorded as its own fact — never a transition
(`bzh:migration-not-transition`).

- **Intent and fact are separate.** An authored judgement choice about to be taken, or a chunk's own standing intended
  migration (see [chunk.md](./chunk.md)), is intent — not yet a movement; the migration *record* written when one
  actually applies is the fact. The intent is a plain mutable property, like the graph pin and the defaults, not a fact
  log: setting it overwrites whatever was set before, and setting it to nothing clears it, so a chunk holds at most one
  live intent at a time, with no history of superseded ones to reconcile.
- **A judgement choice can trigger it immediately.** A node's authored judgement choice may target another graph rather
  than a sibling node (`to: graph:<name>` in [graphs.md](../graphs.md)); taking that choice is itself the trigger — the
  worker's verdict ends the attempt at that node and records one migration fact re-pinning the chunk (and, when the
  choice names a `model:`, re-pinning that as the chunk's default model preference) and landing it at the target's
  landing node (§Landing is by name below). The authored **choice** carries the cross-graph target, but when taken it
  records a **migration**, never a cross-graph transition, so `bzh:migration-not-transition` holds. A choice whose
  target names no enabled graph escalates the chunk to `needs_human` rather than dropping the movement.
- **A gate-resolved migration still closes the gate's decision.** When a *human gate's* resolved choice is itself the
  migrating choice, the migration closes that decision — or, when its target is unresolvable and the chunk escalates
  instead, the escalation does. A migration records no transition (`bzh:migration-not-transition`), so without this the
  decision would derive open forever ([humans.md](../humans.md) §Gate decision) and the chunk would never leave the
  gate.
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
  all: it fences the running attempt out and mints its own epoch, because that is what a restart is
  ([restart.md](./restart.md)). The re-pin is still a migration record — that is the half this section owns — and the
  forced clean re-entry is the restart's own fact beside it, both written in one store transaction, so a crash can never
  leave a chunk re-pinned but not moved, or moved but not re-pinned. Where it lands is the anchor question below, not
  this bullet's to answer.
- **Landing is by name.** Landing resolves a node by **name** on the target graph (`bzh:ids-exact-names-correlate` in
  [graphs.md](../graphs.md)) — the trigger picks which name is the anchor: an authored choice anchors the departed
  node's name, falling back to the target's entry node when no match; a standing intent anchors the transition's own
  destination node name for `auto` (no entry fallback — an unmatched name just leaves the transition unchanged, per the
  bullet above), or the intent's own named node for `forced`; an operator's eager restart anchors its own named node,
  else the chunk's **current** node name — with no entry fallback either way, because an operator naming where a chunk
  goes is told when that name is not there, and the one chunk that legally resolves to an entry node is one that has not
  moved at all ([restart.md](./restart.md)); the follow-latest policy anchors that same destination name **with** the
  entry fallback, because unlike an intent it has nothing to stay set for — falling through would defer a standing
  policy forever, on exactly the graph whose shape changed enough to drop the node. **The landed node's own `executor`
  then governs exactly as it does for an ordinary transition** ([graphs.md](../graphs.md) §Node): landing on a
  hub-executed node derives `delivering`, not `ready` — the chunk stays in the hub's own hands, driven by the hub's own
  executor, same as any other arrival at that node — while landing on a runner node re-queues `ready`. This keys on the
  landed node's `executor`, never its name; the shipped `deliver` node is one hub-executed instance a migration can land
  on, not a special case.
- **An `auto` intent is a per-chunk request; a follow-latest policy is not.** The two are the reason a migration records
  **what moved the chunk**, not just that it moved: an authored choice, an operator's intent, an operator's eager
  restart, and the standing policy are otherwise indistinguishable in history, and the policy is the only one nobody
  asked for. Same-name is no tell either — an operator aiming an intent *by name* also lands on a newer same-name mint.
  So a chunk found on a graph it did not start on can always be traced to what put it there.
