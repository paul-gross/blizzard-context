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

**Why.** sqlite is the fast local default and test backend, while postgres support stays within SQLAlchemy's portable
surface rather than a second test matrix; a bare sqlite key reuses a pruned rowid and a postgres sequence burns values,
so only a durable counter avoids reissuing a `seq` below one already consumed or leaving a gap on both backends.
sqlite's incidental rowid order coincides with insertion order — a select missing a real `order_by` still comes back in
write order, indistinguishable from deliberate ordering to any sqlite-backed test, and only postgres's unordered
contract exposes the gap.

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
  first.
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

**See also.** The exemplar's hub migration and its test ([../exemplars/index.md](../exemplars/index.md)) — a revision
adding two tables, as reference code. Where a revision's test lives, and when it retires, is
`bzh:colocated-migration-tests` in [../verification/blizzard/tier-rules.md](../verification/blizzard/tier-rules.md).

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

**Do.** A revision creating `delivery_pr_opened`, whose foreign key names a table it does not create:

```python
_frozen_metadata = sa.MetaData()
sa.Table("chunks", _frozen_metadata, sa.Column("chunk_id", sa.String(), primary_key=True))  # stub: the referenced key only
_delivery_pr_opened = sa.Table(
    "delivery_pr_opened",
    _frozen_metadata,
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("chunk_id", sa.String(), sa.ForeignKey("chunks.chunk_id"), nullable=False),
)
```

A revision that only back-fills from `chunks` freezes the same way, its stub carrying just the columns its select names.

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
  [the runner store's](../verification/blizzard/gaps.md#the-runner-store-under-postgres) for a runner key — and
  [../verification/blizzard/gaps.md](../verification/blizzard/gaps.md) owns that list and what a change owes it. The
  entry describes the revision by the key it adds, never by its id (`bzh:no-revision-citations`). A column the revision
  adds may close a gap listed there.

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

```python
#: Every column this revision keys, frozen as it runs — never read from schema.metadata.
_KEYED: tuple[tuple[str, str], ...] = (("chunks", "tenant_id"), ("artifacts", "tenant_id"))

for table, column in _KEYED:
    if _is_nullable(bind, table, column):  # re-entry guard: skip a table already tight
        with op.batch_alter_table(table) as batch:  # default recreate="auto"
            batch.alter_column(column, nullable=False)
```

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

**See also.** The exemplar's permit revision migration ([../exemplars/index.md](../exemplars/index.md)) — an expansion
as reference code: a `NOT NULL` column with a server default added to a table that holds rows.

## No revision named in agent context (`bzh:no-revision-citations`)

**Rule.** Agent context never names a specific store migration revision — by revision id, file stem, or slug — nor a
colocated migration test's file, whether as an exemplar, a precedent, evidence, or a pointer. State the schema change or
the idiom itself; where a concrete reference is needed, point at a durable artifact instead:

- the exemplar migration and its test, routed by [../exemplars/index.md](../exemplars/index.md);
- a test module outside the migration trees, such as one under `blizzard/tests/`;
- a tool, or a verification method by its id;
- the store contracts, `blizzard/contracts/store/hub.json` and `runner.json`, for a table's current shape.

**Why.** A fold deletes every revision below its floor together with its colocated test, so a citation to one dangles
the moment the history is folded, and nothing flags it. The exemplars sit outside every fold
(`bzh:exemplar-conformance`) and the contracts track the current schema, so a pointer at either ages forward with its
target.

**Scope.** Binds every agent-facing markdown file — this harness and any other blizzard agent context. Leaves alone what
the code holds — a revision's `down_revision`, a migration's own docstring — and operator docs and change notes. A
passage may still describe a revision by the change it makes — *"the revision adding `graph_nodes.action`"* — where the
passage stands only as long as that revision does, as a `gaps.md` entry its fold closes.

**Detect.**

- A `YYYYMMDD_HHMM_` revision stem anywhere outside the exemplars tree — `grep -rnE '[0-9]{8}_[0-9]{4}_[a-z]'` over the
  markdown, ignoring hits under a `blizzard/exemplars/` path or in `exemplars/index.md`'s rows.
- A path into `src/blizzard/{hub,runner}/store/migrations/versions/` or `.../migrations/tests/` that names a file.
- A revision named by its slug — *"the `flows` revision"* — or a method step whose `--down` target is a literal id
  rather than a role such as *"the revision's parent"* or `base`.

The fix rewrites the passage to the change itself, or moves the pointer onto one of the durable artifacts above.

**Do.** *"A revision that keys a populated table guards each table on re-entry, as the exemplar's hub migration guards
each table and index it creates."*

**Don't.** A `Do` slot citing a dated revision file as its idiom's exemplar; a gap entry whose evidence is a list of
colocated test filenames; a manual method that seeds or downgrades to a named revision — each dangles the day a fold
absorbs the revision it names.
