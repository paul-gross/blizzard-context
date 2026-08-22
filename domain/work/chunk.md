# Chunk — the unit of orchestrated work

Part of [work.md](../work.md), the chunk and its lifecycle.

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
  only when a [migration](./migration.md) applies — never silently. A chunk detached back to `ready` mid-graph is
  **past** that window, not back inside it: it stands on a node another graph need not contain, so only a migration,
  which resolves where it lands, can move it.
- **The default model preference and effort are chunk properties alongside the graph pin.** Both are minted **empty** —
  a fresh chunk expresses no preference at all, so the runner's own default applies — and are editable for as long as
  the chunk is unclaimed, immutable thereafter: a wider window than the graph pin's, since a default names no node to be
  stranded on. Like the pin, plain properties rather than a fact log. They are *defaults*, not a selection: they say
  what a surface that declares nothing inherits, and a graph's own [declared session](../graphs.md#declared-sessions)
  outranks them field by field. The vocabulary is the declaration's — a prioritized preference list of capability tiers
  or harness-native names, and a single effort value — so what a chunk default expresses and what a session declaration
  expresses are the same kind of thing.
- **The intended migration is a chunk property alongside the graph pin and the defaults.** Nullable — `null` when no
  migration is queued, otherwise an intent naming a mode (`auto` or `forced`), a target graph, and, for a forced intent,
  a target node. Unlike the graph pin's and the defaults' pre-flight windows, it is set, overwritten, or cleared by the
  operator at any non-terminal status. Applying it re-pins the chunk and clears the intent atomically, in the same write
  as the migration ([migration](./migration.md)); an eager cross-graph [restart](./restart.md) clears it in its own
  write the same way, by superseding it rather than firing it.
- **Nothing on it is a stored status.** Its current node derives from its newest movement fact — a transition, a
  [migration](./migration.md)'s landing, or a [restart](./restart.md)'s target — and its status derives from its
  recorded facts (`bzh:facts-not-status` in [../architecture/system-shape.md](../../architecture/system-shape.md)).
- **Held by at most one runner at a time** — see [execution.md](../execution.md) for acquisition, tenure, and fencing.
