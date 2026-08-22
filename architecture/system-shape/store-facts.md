# Store facts and their closure

The store-schema half of the system shape: what a daemon store may persist, and what obliges an open fact to close.
[`../system-shape.md`](../system-shape.md) owns the macro-shape invariants these two rules sit under, and each rule
follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Store facts, derive status (`bzh:facts-not-status`)

**Rule.** Both daemons' stores hold only durable **facts** — a thing that definitely happened at a definite time (a
lease created, a heartbeat received, a transition recorded, a verdict parsed). A chunk's **status** is always *derived*
by query from those facts, never written as a column.

**Why.** Written status lies after a crash: a process that wrote `running` and then died reports `running` forever,
while a status derived from "last heartbeat 20 minutes ago and the pid is dead" tells the truth however the process
ended — this single rule is what makes crash recovery correct rather than aspirational, and is what the invariant
checker (`bzh:invariant-checker`) asserts against.

**Detect.** A `status` / `state` column written by application code; a derived condition (running, waiting, stalled,
done) persisted rather than computed from underlying fact rows at read time.

**Do.** Persist `Lease`, `Heartbeat`, `Transition`, `Verdict` rows; compute chunk status by querying them (last
heartbeat age, pid liveness, latest transition).

**Don't.** Write a `chunk.status = "running"` column and update it as the chunk moves — the column outlives the truth
the instant the process dies.

**Recorded positions** — a case that looks like it might carry a derived condition but does not, stated so a reviewer
does not have to re-derive the same judgement:

- **Derived transcript events (blizzard#254).** `transcript_events` conforms to this rule rather than being exempt from
  it: each row is an immutable *observation* — a definite occurrence (a file read, a skill invocation, an agent spawn)
  at a definite time — never a *condition* that can go stale, the distinction the rule bars. Three properties are
  load-bearing: (a) nothing derives a status from a row and no admission, claim, or spawn is gated on one — dropping the
  whole table costs only query latency, never correctness; (b) it is fully re-derivable from `transcript_segments`, so
  its authority is always the segments, never itself; (c) its source's mutability is bounded and **observed**, not
  assumed — the paired `transcript_event_derivations` marker records a content fingerprint of what a derivation saw, so
  a segment whose stored content later changes underneath it (a rejected record accepted, a late record landing) is
  detected and re-derived by the standing sweep rather than silently going stale, the same crash-safety shape
  `bzh:crash-point-registry`'s own recorded exemptions ([../crash-correctness/](../crash-correctness/)) use for a
  converging reconciler with no state between passes.

- **Hub-owned work item closure (issue #357).** `work_items.closed_at`/`closure` are a plain nullable column pair on the
  item row, both unset while open and set together once on close — not an append-only fact table, and not exempt from
  this rule either: `work_items` is a **mutable entity** (title, body, and `edited_at` change in place, the same shape
  `chunks.graph_id` carries), not a fact log, so its closure is itself recorded state rather than a derivable condition
  — no query over other rows can produce it, the same terminal-instant shape `hub_exec_slot.released_at` already uses
  (`schema.py`, null while live).

## An open fact declares what closes it on a terminal chunk (`bzh:open-facts-declare-closure`)

**Rule.** Every runner-local **open** read — a fact that stands until something supersedes or closes it — declares what
closes it when the **hub** terminally ends the chunk (`stopped` or `done`). A read whose closers are all runner-local
events is incomplete, not merely narrow.

**Why.** The runner derives openness from its own facts, but the hub owns whether a chunk is still work. A
terminally-ended chunk produces no further runner-local event — no lease is minted, no worker exits, no binding is taken
— so a closer expressed only in runner-local terms can never fire, and the fact stands forever. This has shipped twice:
issue #202 (an ask-parked lease's park fact and a held binding never retired on a non-happy-path ending) and
blizzard#292 (an escalation never closed when its chunk was stopped, leaving a permanent `needs_human` alert on a real
fleet). Both were found by an operator, not by a test.

**Detect.** An `open_*` read, or an `Unsuperseded`/`Unclosed` predicate, whose superseding facts are all runner-local (a
lease mint, a spawn, a closure, a release), with no arm for the hub reporting the chunk terminal; a PULL step that
reconciles only `list_active_leases()` while the fact in question outlives its lease.

**Do.** State at each such read what retires it on a hub-terminal chunk. When no runner-local event can, mirror the
hub's answer into a local fact so the read itself stays hub-free — `escalation_closures`, written by
`Pull._reconcile_escalations`, is the reference shape.

**Don't.** Leave a later lease mint as the sole closer for a fact that outlives its lease — a terminally-ended chunk is
never claimed again, so that closer is unreachable by construction.
