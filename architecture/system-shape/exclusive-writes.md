# Exclusive writes

This spoke owns how an "exactly one wins" decision is enforced once the hub's store, not an in-process lock, is the one
thing every writer shares; the macro-shape hub is [../system-shape.md](../system-shape.md). Every rule here follows the
slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## An exactly-one-wins decision locks its row before it reads (`bzh:store-exclusive-write`)

**Rule.** A decision the hub commits to exactly once — a claim, or any write another such decision's guard reads consult
— runs in one write transaction whose first statement locks the write lock of a row already known to exist, before every
guard read the decision rests on, on that same connection.

**Why.** An in-process lock only serializes callers inside one process; the moment a second hub process shares the
store, two processes' own locks stop serializing each other, and the transaction is the only thing both still share.
Locking first is what makes the guard reads atomic with the write: on SQLite the lock takes the single writer lock
before any later read; on Postgres it takes the row lock a concurrent locker of the same row queues behind.

**Scope.** Governs the chunk claim and every writer it must exclude — edit, restart, delete, dependency declare/
release, group, stop, and complete. A macro-shape constraint on deployment topology, on what holds once more than one
hub process may share a store — not a `kill -9` crash-correctness requirement; one hub process already serializes every
one of these correctly today.

**Detect.**

- An in-process lock (`threading.Lock` or equivalent) in `hub/`, guarding a check-then-act sequence against another
  writer — mechanically flagged by this rule's ast-grep rule (`contracts/ast-grep/rules/store-exclusive-write.yml`),
  which flags any `import threading` under `src/blizzard/hub/**`.
- A locked transaction whose row lock targets a row that may not yet exist when two writers race to create it — a no-op
  `UPDATE` locks nothing on an empty table, so the exclusion never engages. Not mechanically checkable; judged at
  review.

**Do.** `lock_chunk_row` (`hub/store/internal/chunk_rows.py`) — a no-op `UPDATE` on the chunk's own row, already minted
before any claim, edit, or dependency write can reach it — called as the transaction's first statement, with every guard
read that follows it on the same connection.

**Don't.** A `threading.Lock` shared by `ClaimService` and `EditService`, serializing their read-then-write CAS in one
process — correct until a second hub process starts against the same store, at which point the two locks stop
serializing each other and the race reopens with nothing left to catch it.

## Known debt

Stated so a reviewer need not re-derive them:

- **The residual dependency-graph lock.** `DependencyService` and `GroupService` still take an in-process lock — renamed
  from `claim_lock`, built in `hub/app.py` — for the fleet-wide standing-dependency cycle check
  (`hub:no-standing-dependency-cycle`). That check reasons over the whole graph, so no single row's lock can close it:
  two disjoint declares racing on different rows can still together close a cycle neither alone would. Moving it onto a
  store-level singleton row needs a schema migration, not attempted here.
- **The hub-exec slot's empty-table gap.** `acquire_hub_exec_slot` (`hub/store/internal/chunk_hub_exec_store.py`) locks
  via a table-wide no-op `UPDATE` against `hub_exec_slot`, which carries no unique constraint (`hub/store/schema.py`).
  On an empty table that `UPDATE` matches and locks no row, so two concurrent acquires on a freshly-migrated store are
  unserialized on postgres — the asymmetry [../../standards/persistence.md](../../standards/persistence.md)'s
  engine-factory exception also records.
- **Running more than one hub process.** Every writer this spoke covers is migrated onto its rule, but no deployment
  topology stands up a second hub process against one store today.
- **The event broker, marker tokens, background sweeps, and migrate-on-boot.** Each is single-process by construction —
  an in-memory subscriber fan-out, a token minted once per process start, a sweep loop with no cross-process
  coordination, and a migration run assumed uncontended at boot — and none is touched here.

## See also

- [../../standards/persistence.md](../../standards/persistence.md) — `bzh:sql-portable`, which this rule's locked
  statement is itself held to.
- [../crash-correctness.md](../crash-correctness.md) — `bzh:invariant-checker`'s `hub:one-live-route-per-chunk`, the
  durable invariant this rule keeps true once more than one hub process shares a store.
