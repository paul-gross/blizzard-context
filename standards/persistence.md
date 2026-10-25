# Persistence

The SQL surface and the migration policy of the blizzard stores. This file sits under the facts-only store invariant
`bzh:facts-not-status`, owned by
[../architecture/system-shape/store-facts.md](../architecture/system-shape/store-facts.md). Every rule follows the
Rule/Why/Detect/Do/Don't slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`) and carries its
stable `bzh:` id in its heading.

## Portable SQL (`bzh:sql-portable`)

**Rule.** The hub store and the runner store each run on sqlite or postgres, selected by configuration, and neither
daemon may depend on backend-specific behavior — in syntax or in result determinism. A select whose consumer depends on
the result's row order — an index into it, a newest or oldest read — carries an explicit total `order_by` on the query
itself; an unordered select is not made portable by passing on both backends. A runner outbox row's `seq` comes from the
runner's durable counter in `outbox_counters`, never from the backend's key generation: `insert_outbox_row`
(`src/blizzard/runner/store/internal/base.py`) is the one place that inserts into `outbound_buffer` or
`transcript_outbound_buffer`, advancing the counter in the row's transaction.

**Why.** sqlite is the fast local default and what tests run against; postgres support is held by staying inside
SQLAlchemy's portable surface, not by a second test matrix, so postgres costs a configuration switch and the local and
CI loops stay cheap. On ordering, sqlite's incidental rowid order coincides with insertion order — a select missing a
real `order_by` still comes back in write order, indistinguishable from deliberate ordering to any sqlite-backed test,
and only postgres's unordered contract exposes the gap.

**Exception.**

- **The engine factory.** `src/blizzard/foundation/store/engine.py` is the one place allowed to branch on the configured
  backend for driver and connection-level settings — never for query semantics; it owns those settings' values, and no
  store, domain, or migration code may name or hardcode one. A write path may still rely on the serialization guarantee
  those settings preserve rather than fail outright on contention: sqlite's single-writer lock, which the
  WAL/`busy_timeout` pair the factory sets preserves rather than removes, is what `lock_chunk_row`
  (`hub/store/internal/chunk_rows.py`, `bzh:store-exclusive-write`) already serializes concurrent callers on — a row
  lock on a row already known to exist, portable across both backends, only its sqlite implementation running through
  the factory.
- **Two runner tables that keep `sqlite_autoincrement=True`.** `in_flight_elicitations` and `host_outbound_buffer` set
  it on their integer primary key: a sqlite-only pragma admitted because the hazard it guards is itself sqlite-only, so
  no portable equivalent exists. The hazard: a bare sqlite `INTEGER PRIMARY KEY` reuses a deleted tail row's rowid.
  `in_flight_elicitations` rows are deleted on collect and relaunch while `pause_parks.interrupted_elicitation_id` names
  one by `id`, so a reissued id would point a park at another launch; `host_outbound_buffer` is the host's own fact lane
  whose `seq` the hub de-duplicates against a mark of its own, so a reissued `seq` would read as already seen. Postgres
  needs no equivalent: its `autoincrement=True` compiles to a sequence-backed `SERIAL`, which never reuses a value. The
  runner outboxes (`outbound_buffer`, `transcript_outbound_buffer`) are not in this list — their `seq` comes from
  `outbox_counters`. `test_dialect_table_options_are_all_admitted` in `tests/test_layering.py` fails a table that sets a
  dialect-specific option without being named here.

**Scope.** A bare sqlite key reuses a pruned row's rowid and a postgres sequence burns values, so a `seq` that came from
either could be reissued below one a consumer already treated as final, or leave a gap; a counter that only moves
forward behaves the same on both.

**Detect.** A dialect-specific column type, function, or `text()` SQL; a test asserting behavior only one backend gives;
a code path branching on the configured backend; a consumer indexing `[-1]` or `[0]` into a select carrying no explicit
total `order_by`; streaming (`yield_per`/`stream_results`) set on a connection rather than on one statement's execution
— mechanically flagged by `contracts/ast-grep/rules/statement-scoped-streaming.yml`. An insert into `outbound_buffer` or
`transcript_outbound_buffer` that goes around `insert_outbox_row` — `test_every_outbox_row_is_inserted_through_the_seam`
in `tests/test_layering.py` fails it.

**Do.** `ChunkFactsStore.load_facts` uses `select(s.chunk_pause_facts).where(...).order_by(s.chunk_pause_facts.c.id)`
because the fact projection it reconstitutes carries the chunk's pause history and a consumer indexes that list's tail.
The example shows the ordering a history read owes, not how to read a newest fact: a read that answers with only the
newest fact per key never fetches the history — [../architecture/read-cost.md](../architecture/read-cost.md)
`bzh:newest-per-key-read`.

**Don't.** The same `select(s.chunk_pause_facts).where(...)` with the `order_by` dropped — sqlite's rowid order hides
the omission; postgres does not.

**See also.** `./wire.md` `bzh:utc-instants` — `UtcDateTime`, the column type that keeps every DateTime-family column
inside this rule while making instants UTC-aware.

## Manual migrations (`bzh:manual-migrations`)

**Rule.** Schema change is Alembic, applied manually through the CLI, never automatically at daemon startup.

- Daemons never migrate: at startup each daemon compares the store's revision to the one it expects and refuses to run
  on mismatch, naming the exact migrate command. A revision absorbed by a baseline instead requires the floor release
  first; the baseline contract lives at `blizzard-product:/plans/release-engineering/release-lines/spec/fold.md`.
- There are two migration trees, one per store (hub, runner), with independent schemas and lifecycles, keeping the two
  stores' release cadences uncoupled.
- Every revision has explicit `upgrade()` and `downgrade()`; applying is idempotent at the revision level, and migration
  scripts stay inside `bzh:sql-portable`'s surface so one tree serves both backends.
- SQLite has no `ALTER` for a CHECK constraint, a column's nullability, or a foreign key, so changing one goes through
  Alembic's `batch_alter_table` table-copy recreate — load-bearing there, not a style choice, wherever a revision
  touches one. Putting a required key on a table that already holds rows follows `bzh:keyed-table-migration`.
- `blizzard hub init <dir>` creates and migrates the runtime environment and is idempotent; `blizzard hub migrate`
  applies pending revisions and `migrate --down <rev>` reverses; the same verbs exist under `blizzard runner`.

**Why.** Failing loud beats a daemon silently rewriting a schema out from under running data; manual CLI-driven
migration keeps schema change an explicit, reviewable, reversible step.

**Detect.** An `alembic upgrade` or `create_all` call on a daemon startup path; a revision whose `downgrade()` is a
stub; a single migration tree spanning both stores; dialect-specific migration SQL.

**Do.** The hub's startup guard, `Migrations.check_current` in `src/blizzard/hub/runtime.py` (the runner has its twin):

```python
def check_current(self) -> None:
    """Refuse to run on a store-revision mismatch, naming the migrate command."""
    self.runner.check_current(store=STORE_NAME, remedy=f"{MIGRATE_COMMAND} --dir {self.config.root}")
```

**Don't.** The same slot calling `self.runner.upgrade()` instead — the daemon migrating the store for itself.

**See also.** `blizzard/exemplars/python/exemplar/hub/store/migrations/versions/20261015_0900_permits.py`
([../exemplars/index.md](../exemplars/index.md)) — a revision adding two tables, as reference code; its test is
`blizzard/exemplars/python/exemplar/hub/store/migrations/tests/20261015_0900_permits_test.py`. Where a revision's test
lives, and when it retires, is `bzh:colocated-migration-tests` in
[../verification/blizzard/tier-rules.md](../verification/blizzard/tier-rules.md).

## Frozen revisions (`bzh:frozen-revisions`)

**Rule.** A revision whose table is reshaped by a later revision must not import that table from `schema.py`; it
declares its own frozen `sa.Table` literal.

- For a table the revision itself creates, the frozen literal carries every constraint the table had at that point in
  history — foreign keys included — never a narrowed subset.
- A revision that only reads a later-reshaped table (no create or drop of its own) instead freezes a narrow stub: just
  the columns its query names, nothing more.
- A bare `sa.ForeignKey` naming a table the revision doesn't itself create is resolved with a stub table in the same
  local `MetaData` — never added to `_TABLES`, never created or dropped.

**Why.** Importing `schema.py` makes a revision's historical shape track whatever the module says today, so one
migration tree produces two different schemas on a fresh store depending on when it is read.

**Detect.** A migration importing a later-reshaped table from `blizzard.{hub,runner}.store.schema`; a created table's
frozen literal narrower than `schema.py` declared at that point; a `NoReferencedTableError` fixed by deleting the
foreign key.

**Do.**

- Frozen-literal exemplar: hub migration `20260714_0819_delivery_pr_facts.py`'s `_frozen_metadata` block — a local
  `MetaData()`, a `chunks` stub carrying just the referenced column, and the frozen `delivery_pr_opened` table whose
  `sa.ForeignKey("chunks.chunk_id")` resolves against the stub.
- Read-only-stub exemplar: `20260715_1817_chunk_promoted.py`'s `chunks` table carries only `chunk_id` and `minted_at`,
  the two columns its back-fill selects.
- `20260713_1218_walking_skeleton_facts.py` is the original precedent for the frozen-literal idiom, applied to every
  table it creates.

**Don't.** Resolve a `NoReferencedTableError` by deleting the offending `sa.ForeignKey` — that ships a fresh store with
no constraint where `schema.py` declares one, a silent divergence a reviewer has to catch by hand.

## Keying a table that holds rows (`bzh:keyed-table-migration`)

**Rule.** A revision that puts a required key column — `tenant_id`, or any column a later read filters every row by — on
a table that already holds rows adds it nullable, backfills it in batches of bounded size, and only then tightens it:
`NOT NULL`, the foreign key, and the indexes and unique constraints rebuilt around it.

- **Freeze before keying.** Every earlier revision that imports a table the keying reshapes is frozen
  (`bzh:frozen-revisions`) in a change of its own, before the key lands in `schema.py`. The keying revision carries its
  own frozen list of the tables it keys; it never derives that list from `schema.metadata` at migration time.
- **Name every constraint.** Each foreign key, unique constraint, primary key, and index the revision creates carries an
  explicit name of at most 63 characters, Postgres's identifier limit. An existing unnamed constraint is dropped by the
  name reflection reports for it.
- **Tighten one table per batch, with `recreate="auto"`.** Each table is its own `batch_alter_table` under the default
  `recreate="auto"`: SQLite copies the table, Postgres alters it in place. `recreate="always"` is refused — it forces
  the copy on Postgres too, dropping an autoincrement column's sequence.
- **Guard each table on re-entry.** Before reshaping a table, the revision inspects it and skips the step already done —
  the column present, the constraint already named, the column already non-null.
- **Record it as unverified on Postgres.** The revision joins the Postgres-unverified list of the key it adds —
  [tenancy's](../verification/blizzard/gaps.md#tenancys-migrations-and-locks-under-postgres) for a tenant key,
  [projects'](../verification/blizzard/gaps.md#projects-migration-and-writes-under-postgres) for a project key,
  [the runner key's](../verification/blizzard/gaps.md#the-runner-key-revision-under-postgres) for a runner key — and
  [../verification/blizzard/gaps.md](../verification/blizzard/gaps.md) owns that list and what a change owes it. A
  column the revision adds may close a gap listed there.

**Why.** A required column added in one step to a populated table either fails or writes one unbounded statement, and a
key nothing backfilled cannot be tightened. Each store's migration chain runs in one transaction, so no revision
boundary commits on its own and a failure promises no known revision; the per-table guards are what let a rerun pick up
where it stopped.

**Scope.** Binds the hub and runner trees alike, and any later key of the same shape — a project id added to a populated
table included. A table the revision itself creates is created tight and needs none of this.

**Detect.**

- A revision adding a `nullable=False` column to an existing table in one `add_column`, or backfilling it with one
  `UPDATE` over the whole table.
- A foreign key, unique constraint, or index created without a `name=`, or with a name over 63 characters.
- `recreate="always"` in a keying revision; one `batch_alter_table` reshaping several tables.
- A keying step with no inspection guard ahead of it, or a keying revision that imports from `schema.py` or computes its
  table list from `schema.metadata`.

**Do.**

- Hub migration `20261006_1200_runner_minted_ids.py` — a frozen tuple naming every column it rewrites, and its
  tightening `batch_alter_table` left on the default `recreate="auto"`.
- `20260907_1000_event_log_runner_id_nullable.py` — the inspection guard (`_is_nullable`) ahead of its table's batch, so
  a rerun skips the reshape and goes on to the backfill.

**Don't.** `op.add_column("chunks", sa.Column("tenant_id", sa.String(), nullable=False, server_default="ten_…"))` — one
statement rewrites every row at once, the default outlives the backfill it stood in for, and the foreign key it still
lacks needs a second unguarded copy.

## Expand, then contract (`bzh:store-expand-contract`)

**Rule.** A schema revision only expands: a table, a nullable column or one with a server default, an index, or a value.
Everything else is a contraction — a table or column dropped or renamed, a type changed, a column made `NOT NULL`
without a server default, a unique or check constraint added to a table that already existed, a primary key or foreign
key changed. A contraction is a break (`bzh:released-surface-additive`,
[../architecture/system-shape/released-surfaces.md](../architecture/system-shape/released-surfaces.md)): it passes only
where the window admits a break, and only on a table or column every supported release marks deprecated, with
`info={"deprecated": "<line>"}` on its `Table` or `Column` in `schema.py`.

**Why.** A daemon refuses a store whose revision is not its own (`bzh:manual-migrations`), so a release inside the
window meets a newer store only by walking the store back (`docs/rollback.md`). A walk back across an expansion loses
nothing; across a contraction it does.

**Detect.** `blizzard:compat` reports a contraction as a finding on the `store` surface, from `contracts/store/hub.json`
and `contracts/store/runner.json`.

**Do.** Add the new column or table beside the old, move readers and writers over, mark the old deprecated, and drop it
in a later change that the window admits.

**Don't.** Rename a column or tighten a constraint on an existing table in one revision.
