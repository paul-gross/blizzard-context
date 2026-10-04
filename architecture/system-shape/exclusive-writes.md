# Exclusive writes

This spoke owns how an "exactly one wins" decision is enforced once the hub's store, not an in-process lock, is the one
thing every writer shares; the macro-shape hub is [../system-shape.md](../system-shape.md). Every rule here follows the
slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## An exactly-one-wins decision locks its row before it reads (`bzh:store-exclusive-write`)

**Rule.** A decision the hub commits to exactly once — a claim, or any write another such decision's guard reads consult
— runs in one write transaction whose first statement locks the write lock of a row already known to exist, before every
guard read *of that row's own chunk state* the decision rests on, on that same connection. A read that gates admission
independently of the race itself (a paused runner, checked once before the lock opens) or that resolves a different
aggregate this lock does not cover (a graph's retirement) is not a guard read this rule governs: nothing about the
exactly-one-wins race depends on when it runs, so it may stay on its own connection, ahead of the lock, without
reopening anything the lock closes.

**Why.** An in-process lock only serializes callers inside one process; the moment a second hub process shares the
store, two processes' own locks stop serializing each other, and the transaction is the only thing both still share.
Locking first is what makes the guard reads atomic with the write: on SQLite the lock takes the single writer lock
before any later read; on Postgres it takes the row lock a concurrent locker of the same row queues behind.

**Scope.** Governs the chunk claim and every writer it must exclude — edit, restart, delete, dependency declare, group,
stop, complete, detach, and requeue — and the epoch-fenced writes (`bzh:epoch-fencing`), which the row lock serialises
against stop and restart. A macro-shape constraint on deployment topology, on what holds once more than one hub process
may share a store — not a `kill -9` crash-correctness requirement; one hub process already serializes every one of these
correctly today. Dependency **release** is exempt rather than uncovered: it can only shrink the standing set and can
never close a cycle, so nothing it writes needs a row lock.

**Detect.**

- An in-process lock (`threading.Lock` or equivalent) in `hub/`, guarding a check-then-act sequence against another
  writer — mechanically flagged by this rule's ast-grep rule (`contracts/ast-grep/rules/store-exclusive-write.yml`),
  which flags any `import threading` under `src/blizzard/hub/**`.
- A locked transaction whose row lock targets a row that may not yet exist when two writers race to create it — a no-op
  `UPDATE` locks nothing on an empty table, so the exclusion never engages. Not mechanically checkable; judged at
  review.

**Do.** `lock_chunk_row` (`hub/store/internal/chunk_rows.py`) — a no-op `UPDATE` on the chunk's own row, already minted
before any claim, edit, or dependency write can reach it — called as the transaction's first statement, with every guard
read that follows it on the same connection. `IChunkExclusiveWrites.locked` (`hub/domain/chunk/ports/exclusive.py`) is
the one place this crosses the domain seam: it locks every named chunk id in sorted order (closing cross-writer deadlock
on Postgres, where two writers naming the same set in different orders could otherwise wait on each other) before
yielding `ILockedChunkRead` — a domain-facing handle carrying no connection. A sibling write repository's own `*_locked`
method takes that same handle and recovers the real connection through `conn_of` (`hub/store/internal/chunk_rows.py`), a
package-private cast only the store layer ever calls — the domain layer never sees a `Connection`.

An epoch-fenced write takes the lock-then-guard form through `fence` (`hub/store/internal/chunk_rows.py`), which the
write calls on its own connection after the lock and its replay probe and before its first insert. It reads the terminal
facts and the newest epoch there, so a stop or restart cannot land between the guard and the write.

**Don't.** A `threading.Lock` shared by `ClaimService` and `EditService`, serializing their read-then-write CAS in one
process — correct until a second hub process starts against the same store, at which point the two locks stop
serializing each other and the race reopens with nothing left to catch it.

## Known debt

Stated so a reviewer need not re-derive them:

- **The residual fleet-wide lock.** One in-process `threading.Lock` — `cycle_lock`, built in `hub/composition.py` —
  stands where a row lock does not reach; each `import threading` it needs carries this rule's `ast-grep-ignore`. Moving
  any of its holders onto a store-level singleton row needs a schema migration. Its holders:
  - `DependencyService.declare` and `GroupService.group` — for the fleet-wide standing-dependency cycle check
    (`hub:no-standing-dependency-cycle`), which reasons over the whole graph: two disjoint writers racing on different
    rows can still together close a cycle neither alone would.
  - `DeleteService.delete`, for its whole transaction — the deleted chunk's row lock does not reach the other end of an
    outgoing edge the delete releases, so a concurrent fold of that other chunk, locking only its own survivor and merge
    ids, could otherwise remint the edge with the deleted chunk as its dependent.
  - `DependencyService.release` — as its only lock, being exempt from the row lock (Scope above).
  - `EgressSweep.sweep` and `EgressReset.reset` — the export's pass lock, which keeps an operator's cursor move from
    being overwritten by the advanced cursor a pass in flight appends. `egress_cursor` holds no row known to exist to
    lock, and the sweep it serializes against is itself a single-process background loop.
- **The hub-exec slot's empty-table gap.** `acquire_hub_exec_slot` (`hub/store/internal/chunk_hub_exec_store.py`) locks
  via a table-wide no-op `UPDATE` against `hub_exec_slot`, which carries no unique constraint (`hub/store/schema.py`).
  On an empty table that `UPDATE` matches and locks no row, so two concurrent acquires on a freshly-migrated store are
  unserialized on postgres; sqlite still serializes them, the statement taking its single writer lock whether or not a
  row matches.
- **Running more than one hub process.** No deployment topology stands up a second hub process against one store.
- **Single-process components outside this rule.** Each is single-process by construction, and this rule governs none of
  them:
  - **The event broker** — an in-memory subscriber fan-out.
  - **Marker-write tokens** — held by an in-memory authority, so a token verifies only in the process that minted it
    ([../crash-correctness/hub.md](../crash-correctness/hub.md) §The marker-write capability token).
  - **Background sweeps** — loops with no cross-process coordination.
  - **Migrate-on-boot** — a migration run assumed uncontended at boot.

## See also

- [../crash-correctness/hub.md](../crash-correctness/hub.md) — whether a write this rule's locks wrap has a crash
  window, which no lock here decides.
- [../../standards/persistence.md](../../standards/persistence.md) — `bzh:sql-portable`, which this rule's locked
  statement is itself held to.
- [../crash-correctness.md](../crash-correctness.md) — `bzh:invariant-checker`'s `hub:one-live-route-per-chunk`, the
  durable invariant this rule keeps true once more than one hub process shares a store.
