# Chunk

A chunk is the hub's unit of orchestrated work: it wraps one or more backlog items by work ref, travels a workflow
graph, and accumulates artifacts, questions, and decisions as it goes. Spoke of the [work hub](../work.md).

At most one runner holds a chunk at a time; [../execution.md](../execution.md) owns acquisition, tenure, and fencing. A
chunk stores no status: the current node derives from the newest movement fact — a transition, a migration's landing, or
a restart's target — and status derives from recorded facts (`bzh:facts-not-status`,
[../../architecture/system-shape/store-facts.md](../../architecture/system-shape/store-facts.md)).

## Work refs

A chunk never stores item contents: it holds work refs, and reads pass through to the backing work source. The work item
is the durable referent and the chunk is ephemeral — an unacquired chunk may be discarded or grouped away, and
re-ingesting the same item mints a fresh chunk. An item already wrapped by a live chunk cannot be ingested again.

A landed chunk's work refs are closed at their own source through its binding — best-effort, eventually convergent, not
atomic with the landing, and independent of whether the chunk keeps running. A chunk that lands and is only later
abandoned still closes its work items, because it was in fact delivered.

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
([../graphs.md#declared-sessions](../graphs.md#declared-sessions)) outranks the chunk defaults field by field. The
defaults are editable while the chunk is unclaimed and immutable thereafter — a wider window than the pin's.

### Intended migration

The intended migration property is null when no migration is queued, else an intent naming a mode (`auto` or `forced`),
a target graph, and, for `forced`, a target node. The operator can set, overwrite, or clear it at any non-terminal
status. Applying it re-pins the chunk and clears the intent in one atomic write; an eager cross-graph restart
([./restart.md](./restart.md)) clears it in its own write, superseding rather than firing it.
