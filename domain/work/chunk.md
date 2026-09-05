# Chunk

A chunk is the hub's unit of orchestrated work: it wraps one or more backlog items by work ref, travels a workflow
graph, and accumulates artifacts, questions, and decisions as it goes. Spoke of the [work hub](../work.md).

At most one runner holds a chunk at a time; [../execution.md](../execution.md) owns acquisition, tenure, and fencing. A
chunk stores no status: the current node derives from the newest movement fact — a transition, a migration's landing, or
a restart's target — and status derives from recorded facts (`bzh:facts-not-status`,
[../../architecture/system-shape/store-facts.md](../../architecture/system-shape/store-facts.md)).

## Work refs

A chunk never stores item contents: it holds work refs, and reads pass through to the backing work source. The work item
is the durable referent and the chunk is ephemeral — an unacquired chunk may be grouped away or deleted, and
re-ingesting the same item mints a fresh chunk. An item already wrapped by a live chunk cannot be ingested again.

A landed chunk's work refs are closed at their own source through its binding — best-effort, eventually convergent, not
atomic with the landing, and independent of whether the chunk keeps running. A chunk that lands and is only later
abandoned still closes its work items, because it was in fact delivered.

## Materialization

A node-step's completion may carry proposed work items (`proposes_work_items`, [../graphs/nodes.md](../graphs/nodes.md))
— a `create` (a new item's title, body, and stated priority) or an `update` (an open item's pointer plus evidence to
append) — riding the completion alongside its artifacts. They accumulate inertly through the graph: nothing reads a
proposal row until the chunk delivers.

Delivery materializes them: it turns every accumulated, unstruck proposal of a chunk that has actually delivered — moved
into the graph's reserved terminal — into a real work item, best-effort, eventually convergent, and not atomic with the
landing. A `create` mints a `hub`-owned item authored by the fleet — the proposing runner, chunk, and node — resting on
its own fresh `not_ready` chunk, exactly as a human-filed item does. An `update` appends its evidence to the pointed-at
item's body and stamps its last-edit instant, when that item is open and its source can be edited; closed, withdrawn,
nonexistent, or unresolvably-sourced, it is recorded unresolved with its reason instead, and delivery is never blocked
by it. Every proposal is judged exactly once — replaying the same delivery mints no duplicate item and appends no
duplicate evidence — but carries no epoch filter: two proposals from two epochs of the same node both materialize, since
both rode a fence-accepted completion. A chunk that lands and is only later abandoned still materializes its proposals;
a chunk an operator marks done by hand, or one that never reaches delivery, never does. That is a narrower predicate
than Work refs' closure, which a hand-completion also fires: a hand-completed chunk that never delivered closes its refs
and materializes nothing.

An operator resolving a gate may strike some of the chunk's pending proposals — its proposals carrying neither a
materialization row nor a strike row yet — instead of passing them all. A strike is its own fact, recorded with the
resolving identity and decision inside the resolution's own first-write-wins write, never a mutation of the proposal's
own row and never a materialization outcome: it is a refusal *before* materialization ever judges the proposal,
permanent and exclusive of the judgment a `create`/`update`/unresolved outcome represents. A struck proposal never
materializes, on any later delivery; the loser of a concurrent resolution strikes nothing at all, the same
first-write-wins reading its choice takes. Striking is explicit — a resolution naming none passes every one of the
chunk's pending proposals, unstruck.

## Deletion

Deletion is gated on the same unacquired predicate as grouping — `not_ready` or unclaimed `ready` — so a chunk any
runner holds, a chunk parked on human input, or a chunk at a terminal status all refuse it alike; a deleted chunk is
ephemeral exactly as a grouped one is, leaving every read the moment the fact lands — the same vanishing Work refs
describes for a grouped chunk.

A hub item and its chunk live and die together, in both directions. Deleting a chunk withdraws every open `hub:`-source
pointer it holds — any `forge:`-source pointer on the same chunk survives untouched, since a chunk can carry pointers
from more than one source — and withdrawing a hub item deletes its unacquired holder chunk in the same stroke rather
than refusing the withdrawal. Two holders refuse it: a genuinely acquired, still-live holder, and an unacquired holder
that stands as another chunk's prerequisite — the same refusal deleting it directly meets
([./statuses.md](./statuses.md) §The blocked marking). A terminal holder's withdrawal deletes nothing.

## Operator-editable properties

The graph pin, the model/effort defaults, and the intended migration are plain mutable properties, not fact logs.

### Graph pin

A chunk is pinned to exactly one immutable graph, set at mint from a default. While the chunk is unclaimed and has never
moved — `not_ready` or unclaimed `ready` — the pin is a plain editable selection, the operator's pre-flight repin
window. Once the chunk has moved, the pin is immutable and changes only when a migration
([./migration.md](./migration.md)) applies. A chunk detached back to `ready` mid-graph is past that window: it stands on
a node another graph need not contain, so only a migration can move it.

### Model and effort defaults

The default model preference and default effort are chunk properties beside the graph pin, minted empty — no preference
expressed, so the runner's own default applies. They share the session declaration's vocabulary: a prioritized
preference list of capability tiers or harness-native names, plus one effort value; a graph's declared session
([../graphs/declared-sessions.md](../graphs/declared-sessions.md)) outranks the chunk defaults field by field. The
defaults are editable while the chunk is unclaimed and immutable thereafter — a wider window than the pin's.

### Intended migration

The intended migration property is null when no migration is queued, else an intent naming a mode (`auto` or `forced`),
a target graph, and, for `forced`, a target node. The operator can set, overwrite, or clear it at any non-terminal
status. Applying it re-pins the chunk and clears the intent in one atomic write; an eager cross-graph restart
([./restart.md](./restart.md)) clears it in its own write, superseding rather than firing it.
