# Store facts

This spoke owns the store-schema half of the system shape — what a daemon store may persist, and what obliges an open
fact to close; the macro-shape hub is [../system-shape.md](../system-shape.md). Every rule here follows the slot
skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Facts, not status (`bzh:facts-not-status`)

**Rule.** Both daemons' stores hold only durable facts — things that definitely happened at a definite time — and a
chunk's status is always derived by query from those facts, never written as a column.

**Why.** Written status lies after a crash — a process that wrote "running" and then died reports running forever, while
a status derived from heartbeat age and pid liveness tells the truth however the process ended. This is what makes crash
recovery correct; the invariant checker (`bzh:invariant-checker`) asserts against it.

**Detect.** A `status` or `state` column written by application code, or a derived condition (running, waiting, stalled,
done) persisted rather than computed from underlying fact rows at read time.

**Do.** Persist `Lease`, `Heartbeat`, `Transition`, and `Verdict` rows and compute chunk status by querying them — last
heartbeat age, pid liveness, latest transition.

**Don't.** A `chunk.status = "running"` column updated as the chunk moves — the column outlives the truth the instant
the process dies.

### Recorded positions

Stated so a reviewer need not re-derive them:

- `transcript_events` conforms to `bzh:facts-not-status` rather than being exempt — each row is an immutable observation
  of a definite occurrence at a definite time, never a condition that can go stale. Three properties carry the
  judgement: nothing derives a status from its rows and no admission, claim, or spawn is gated on one, so dropping the
  table costs only query latency, never correctness; it is fully re-derivable from `transcript_segments`, which stay the
  authority; and its source's mutability is observed rather than assumed — `transcript_event_derivations` records a
  fingerprint of the content each derivation saw, so a segment whose stored content later changes is detected and
  re-derived by the standing sweep.
- `work_items.closed_at` and `work_items.closure` are a plain nullable column pair, unset while the item is open and set
  together once on close — conforming because `work_items` is a mutable entity (title, body, and `edited_at` change in
  place), not a fact log, so closure is recorded state no query over other rows can produce, the same terminal-instant
  shape `hub_exec_slot.released_at` uses.

## Open facts declare their closure (`bzh:open-facts-declare-closure`)

**Rule.** Every runner-local open read — a fact that stands until something supersedes or closes it — declares what
closes it when the hub terminally ends the chunk (stopped or done).

**Why.** The runner derives openness from its own facts, but the hub owns whether a chunk is still work, and a
terminally-ended chunk produces no further runner-local event — no lease minted, no worker exit, no binding taken — so a
closer expressed only in runner-local terms can never fire and the fact stands forever. This failure has shipped twice
on real fleets — an ask-parked lease's park fact and held binding never retired after a non-happy-path ending, and an
escalation left a permanent `needs_human` alert after its chunk was stopped — both found by an operator, not by a test.

**Detect.** An `open_*` read, or an `Unsuperseded`/`Unclosed` predicate, whose superseding facts are all runner-local (a
lease mint, a spawn, a closure, a release) with no arm for the hub reporting the chunk terminal; or a PULL step that
reconciles only `list_active_leases()` while the fact in question outlives its lease.

**Do.** State at each open read what retires it on a hub-terminal chunk, and when no runner-local event can, mirror the
hub's answer into a local fact so the read itself stays hub-free — `escalation_closures`, written by
`Pull._reconcile_escalations`, is the reference shape.

**Don't.** Leave a later lease mint as the sole closer for a fact that outlives its lease: a terminally-ended chunk is
never claimed again, so that closer is unreachable by construction.
