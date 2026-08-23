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
itself; an unordered select is not made portable by passing on both backends.

**Why.** sqlite is the fast local default and what tests run against; postgres support is held by staying inside
SQLAlchemy's portable surface, not by a second test matrix, so postgres costs a configuration switch and the local and
CI loops stay cheap. On ordering, sqlite's incidental rowid order coincides with insertion order — a select missing a
real `order_by` still comes back in write order, indistinguishable from deliberate ordering to any sqlite-backed test,
and only postgres's unordered contract exposes the gap.

**Exception.** One recorded exemption: `transcript_outbound_buffer`, the transcript lane's outbound buffer, sets
`sqlite_autoincrement=True` on its `seq` primary key — a sqlite-only pragma admitted because the hazard it guards is
itself sqlite-only, so no portable equivalent exists. The hazard: `transcript_outbound_buffer` prunes acked non-final
rows (unlike its sibling `outbound_buffer`, which never deletes), and a bare sqlite `INTEGER PRIMARY KEY` reuses a
pruned row's rowid, so a later insert could be reissued a `seq` a consumer already treated as final. Postgres needs no
equivalent: that column's `autoincrement=True` compiles there to a sequence-backed `SERIAL`, which never reuses a
deleted value, so the schema stays one portable surface in effect. `tests/test_pin_runner_store.py` pins the sqlite
autoincrement behavior; no postgres-side test exists because there is no postgres-side hazard to cover.

**Detect.** A dialect-specific column type, function, or `text()` SQL; a test asserting behavior only one backend gives;
a code path branching on the configured backend; a consumer indexing `[-1]` or `[0]` into a select carrying no explicit
total `order_by`.

**Do.** `chunk_store.load_facts` uses `select(s.chunk_pause_facts).where(...).order_by(s.chunk_pause_facts.c.id)`
because a consumer reads the newest pause fact via `[-1]`.

**Don't.** The same `select(s.chunk_pause_facts).where(...)` with the `order_by` dropped — sqlite's rowid order hides
the omission; postgres does not.

**See also.** `./wire.md` `bzh:utc-instants` — `UtcDateTime`, the column type that keeps every DateTime-family column
inside this rule while making instants UTC-aware.

## Manual migrations (`bzh:manual-migrations`)

**Rule.** Schema change is Alembic, applied manually through the CLI, never automatically at daemon startup.

- Daemons never migrate: at startup each daemon compares the store's revision to the one it expects and refuses to run
  on mismatch, naming the exact migrate command.
- There are two migration trees, one per store (hub, runner), with independent schemas and lifecycles, keeping the two
  stores' release cadences uncoupled.
- Every revision has explicit `upgrade()` and `downgrade()`; applying is idempotent at the revision level, and migration
  scripts stay inside `bzh:sql-portable`'s surface so one tree serves both backends.
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
