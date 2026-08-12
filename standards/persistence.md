# Persistence

The rules a store schema and its migrations are held to.
These sit under the facts-only store invariant (`bzh:facts-not-status`, [../architecture/system-shape.md](../architecture/system-shape.md)); this file governs the *SQL surface* and the *migration policy* that invariant is realized through.
Each rule follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Stay inside SQLAlchemy's portable surface (`bzh:sql-portable`)

**Rule.** The hub store and the runner store each run on **sqlite or postgres**, selected by configuration; neither daemon may depend on backend-specific behavior, in **syntax or in result determinism**.
sqlite is the fast local default and what tests run against; postgres support is held by staying inside SQLAlchemy's portable surface — **not** by a second test matrix.
A select whose consumer depends on the result's row order — an index into it, a "newest"/"oldest" read — carries an explicit total `order_by` on the query itself; an unordered select is not made portable by parsing on both backends when only one of them returns it in a determinate order.

**Why.** One portable schema means postgres support costs a configuration switch, not a duplicated test suite, and the fast sqlite default keeps the local and CI loops cheap. sqlite's incidental rowid order coincides with insertion order, though, so a select missing a real `order_by` still comes back in the order its rows were written — no sqlite-backed test can tell that apart from a query that ordered them on purpose, and only postgres's unordered contract exposes the gap.

**Detect.** A dialect-specific column type, function, or `text()` SQL that only one backend supports; a test asserting behavior that holds on postgres but not sqlite (or vice versa); a code path branching on the configured backend; a select whose consumer indexes into the result (`[-1]`, `[0]`) or otherwise assumes an order, with no explicit total `order_by` on the query itself.

**Do.** Model with SQLAlchemy's portable types and expressions; run tests against sqlite; treat postgres as the same schema under a different URL; give a select an explicit `order_by` whenever its consumer depends on the result's order — `select(s.chunk_pause_facts).where(...).order_by(s.chunk_pause_facts.c.id)`, the query `chunk_store.load_facts` uses for the pause fact a consumer reads as "newest" via `[-1]`.

**Don't.** Reach for a postgres-only type or a sqlite-only pragma that changes correctness — the schema is no longer one portable surface and now needs two test runs. Drop the `order_by` from a select whose consumer indexes `[-1]`/`[0]` or otherwise assumes an order — sqlite's rowid order hides the omission, postgres does not.

**Recorded exemptions** — a sqlite-only pragma admitted because the hazard it guards is itself sqlite-only, so no portable equivalent exists to reach for:

- **The transcript lane's outbound buffer (`transcript_outbound_buffer`, issue #246).** `sqlite_autoincrement=True` on its `seq` primary key guards a real, sqlite-only correctness hazard: this table prunes acked, non-final rows (unlike its sibling `outbound_buffer`, which never deletes), and a bare sqlite `INTEGER PRIMARY KEY` reuses a pruned row's rowid — a later insert could be reissued a `seq` a consumer already treated as final. Postgres needs no equivalent: this column's `autoincrement=True` compiles there to a sequence-backed `SERIAL`, which never reuses a deleted row's value by construction, so the schema stays one portable surface in effect even though this one pragma is sqlite-only syntax. `tests/test_pin_runner_store.py` pins the sqlite behavior; no postgres-side test exists because there is no postgres-side hazard to cover.

## Migrations are manual, Alembic, CLI-driven (`bzh:manual-migrations`)

**Rule.** Schema change is **Alembic**, applied manually through the CLI — never automatically at daemon startup.

- **Two migration trees**, one per store (hub, runner): independent schemas, independent lifecycles.
- Every revision has explicit `upgrade()` and `downgrade()`; applying is idempotent at the revision level, and scripts stay inside the portable SQL surface (`bzh:sql-portable`) so one tree serves sqlite and postgres.
- `blizzard hub init <dir>` creates and migrates the runtime environment and is idempotent; `blizzard hub migrate` applies pending revisions (`migrate --down <rev>` reverses). The same verbs exist under `blizzard runner`.
- **Daemons never migrate.** At startup each daemon compares the store's revision to the one it expects and **refuses to run on mismatch**, naming the exact migrate command.

**Why.** A version skew that fails loud — naming the command to fix it — beats a daemon that silently rewrites a schema out from under running data; manual, CLI-driven migration keeps the schema change an explicit, reviewable, reversible step. Two trees keep the hub's and runner's schemas from coupling their release cadences.

**Detect.** An `alembic upgrade` (or `create_all`) call on a daemon's startup path; a revision missing a real `downgrade()`; a single migration tree spanning both stores; dialect-specific migration SQL.

**Do.** Write paired `upgrade`/`downgrade` revisions per store tree; apply them through `blizzard hub migrate` / `blizzard runner migrate`; let the daemon refuse to start on revision mismatch.

**Don't.** Auto-migrate on boot, or ship a revision whose `downgrade()` is a stub — an unattended migration can corrupt data, and a stubbed downgrade makes a rollback impossible.

## A revision freezes its own literal, never head-of-tree `schema.py` (`bzh:frozen-revisions`)

**Rule.** A revision whose table is reshaped by a later revision must not import that table from `schema.py`; it declares its own frozen `sa.Table` literal, carrying every constraint the table had at that point — including foreign keys — never a narrowed subset. A bare `sa.ForeignKey` naming a table this revision doesn't itself create is resolved with a stub table in the same local `MetaData` — never added to `_TABLES`, never created or dropped — not by dropping the constraint.

**Why.** Importing `schema.py` makes a revision's *historical* shape track whatever the module says today, so a later reshape silently changes what an old revision recreates on a fresh store — the same migration tree then produces two different schemas depending on when it's read.

**Detect.** A migration importing a table from `blizzard.{hub,runner}.store.schema` that a later revision in the same tree reshapes; a frozen `sa.Table` literal whose constraint set — especially a foreign key — is narrower than `schema.py` declared for that table at this revision's point in history; a `NoReferencedTableError` resolved by deleting the offending `sa.ForeignKey` instead of adding a resolution stub.

**Do.** The `_frozen_metadata` block in `blizzard`'s `src/blizzard/hub/store/migrations/versions/20260714_0819_delivery_pr_facts.py` (lines 40–60): a local `MetaData()`, a `chunks` stub table carrying just the referenced column, and the frozen `delivery_pr_opened` table whose `sa.ForeignKey("chunks.chunk_id")` resolves against the stub. `20260713_1218_walking_skeleton_facts.py` is the original precedent for the same idiom, applied there to every table it creates.

**Don't.** Hitting `NoReferencedTableError` on a bare `sa.ForeignKey` and concluding the fix is to drop the FK — that ships a fresh store with no constraint where `schema.py`'s has one, a silent divergence a reviewer has to catch by hand.

## See also

- [`./wire.md`](./wire.md) — `bzh:utc-instants`, the `UtcDateTime` column type that keeps every `DateTime`-family column inside this file's portable-SQL rule while making instants UTC-aware.
