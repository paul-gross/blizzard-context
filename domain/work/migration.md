# Migration

A migration is the explicit re-pin of a chunk from one immutable graph to another, recorded as its own fact. Spoke of
the [work hub](../work.md); the invariant below is written in the slot skeleton owned by `winter-canon:/rule-shape.md`
(`canon:rule-shape`).

A graph name is minted repeatedly, each mint a separate immutable definition, and a chunk stays pinned to the mint it
started on. A migration records what moved the chunk, not just that it moved: choice, intent, eager restart, and
follow-latest are otherwise indistinguishable in history, and follow-latest is the only one nobody asked for. Same-name
landing is no tell — an intent aimed by name also lands on a newer same-name mint — so the recorded trigger is what
traces a chunk to whatever put it on a graph it did not start on.

## Movement between graphs is a migration (`bzh:migration-not-transition`)

**Rule.** Once a chunk has moved at all, movement between graphs is a migration — its own recorded fact re-pinning the
chunk — never a transition: transitions move along edges within the pinned graph, and no edge crosses graphs.

**Why.** Transitions are judged, fenced movement within one immutable definition — a cross-graph one would re-route
in-flight work without migration's explicit intent, record, and fencing; a pre-flight edit re-routes no in-flight
attempt.

**Exception.** While a chunk is unclaimed and has never moved, its graph pin is a plain editable property outside the
invariant; the window closes at first movement, and editing it writes no migration record. The chunk's default model and
effort are [./chunk.md](./chunk.md)'s to govern, not this invariant's.

**Detect.** A transition whose nodes belong to different graphs, an edge targeting another graph's node, or an
already-moved chunk whose pin changes with no migration record — a re-queued chunk resting `ready` included.

**Do.**

| Chunk                      | What is written                                    |
| -------------------------- | -------------------------------------------------- |
| Has moved, crossing graphs | One migration record — the trigger and the new pin |
| Unclaimed, never moved     | The graph pin itself, edited in place; no record   |

**Don't.** Add a cross-graph edge, or update a moved chunk's pinned graph without recording the re-pin.

## Triggers

Intent and fact are separate: an authored judgement choice about to be taken, or a standing intended migration
([./chunk.md](./chunk.md)), is intent, not movement; the record written when one applies is the fact. No
transition-borne trigger — authored choice, standing intent, or follow-latest — interrupts the attempt that produced it
or mints an epoch: the verdict is accepted as an ordinary one, and a fresh epoch comes only from a later claim, as for
any route-released re-queue.

### Authored choice

A node's authored judgement choice may target another graph (`to: graph:<name>`,
[../graphs/edges.md](../graphs/edges.md)); taking it is the trigger — the verdict ends the attempt there and records one
migration fact re-pinning the chunk. The landing anchors the departed node's name — that node diverted rather than
completed its own destination — falling back to the target's entry node when nothing matches. A choice whose target
names no enabled graph escalates the chunk to `needs_human` rather than dropping the movement. A migrating choice naming
a model re-pins that too, as the chunk's default model preference.

When a human gate's resolved choice is the migrating choice, the migration closes the gate's decision — the escalation
does when the target is unresolvable — since a migration records no transition, nothing else would ever close it
([../humans.md#gate-decision](../humans.md#gate-decision)).

### Standing intent

A standing intent is consulted, never applied eagerly, when the chunk's next transition is judged — worker verdict and
resolved gate decision alike. A hub node's own exit consults no intent, so an intent set on a chunk in the hub's hands
waits for its next worker-or-gate transition. A chunk holds at most one live intent — setting overwrites, clearing
removes — with no history of superseded ones to reconcile.

A forced intent anchors its own named node and migrates to it unconditionally, whatever the transition's destination
would have been. An auto intent anchors the transition's own destination node name with no entry fallback: it migrates
only when that name also exists on the target graph, landing on the same-named node; an unmatched name leaves the
transition to apply unchanged on the current graph, and the intent stays set. An intent whose target graph cannot be
resolved at consult time — never minted or since retired — is skipped like an auto no-match: the transition applies
unchanged and the intent stays set, visible to cancel or re-aim.

### Follow-latest

Follow-latest is a standing policy under which chunks pinned to a graph drift to the newest enabled mint of the same
name at their next transition, so a workflow edit reaches work already in flight. It resolves at two levels — the
graph's own setting where it states one, otherwise a fleet-wide default a silent graph inherits — and the fleet-wide
default is off, so adopting the policy is deliberate. It governs one hop, not a lineage: it is read off the pinned mint,
and the chunk lands on a newer mint with that mint's own inherited-by-default setting — the fleet-wide default is what
sustains drift across a lineage.

The landing anchors the transition's same destination name with the entry fallback: the policy has nothing to stay set
for, and falling through would defer it forever on exactly the graph that changed enough to drop the node.

Follow-latest only moves forward: a chunk on the newest mint, or with every newer mint retired, is left alone — no
error, no fact — as is one whose own mint is retired, where name resolution would hand back an older mint and rewind it.
It never follows a transition to the terminal: a finished chunk has no next node-step to govern, and following would
restart the workflow instead of completing it. A chunk carrying a standing intended migration is never moved by
follow-latest — even when that auto intent fell through for want of a name match.

### Eager restart

An operator's eager cross-graph restart ([./restart.md](./restart.md)) is the one migration trigger not borne by a
transition: it fences the running attempt and mints its own epoch, and its re-pin is still a migration record, written
atomically with the restart's own fact. It records the re-pin as a migration even for a chunk that has never moved, and
it clears a standing intent in the same write that re-pins the chunk, the way a fired intent clears itself — an eager
move supersedes a parked one. Its landing anchors its named node, else the chunk's current node name, with no entry
fallback: an operator naming a target is told when the name is absent, and only a chunk that has never moved legally
resolves to an entry node.

## Landing

Every landing resolves a node by name on the target graph (`bzh:ids-exact-names-correlate`,
[../graphs/ids-and-names.md](../graphs/ids-and-names.md)); the trigger picks the anchoring name. The landed node's own
executor then governs, exactly as for an ordinary transition ([../graphs/nodes.md](../graphs/nodes.md)), and status
after landing keys on that executor, never the node's name — the shipped deliver node is one hub-executed instance, not
a special case. Landed off a transition-borne trigger, a hub-executed node derives `delivering` — the chunk stays in the
hub's hands — while a runner node re-queues `ready`; how an eager restart's landing re-enters its node is
[./restart.md](./restart.md)'s own.
