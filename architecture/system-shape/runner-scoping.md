# Runner scoping

This spoke owns how the runner store keeps every row inside the runner it belongs to — the seam its adapters hold, and
the one door to the tables that belong to the host rather than to a runner; the macro-shape hub is
[../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

A runner store holds two kinds of table. A **runner-scoped** table, declared `info={"scope": "runner"}` in
`blizzard/src/blizzard/runner/store/schema.py`, holds one runner's rows and carries `runner_id`, the hub-minted id its
`runner_identity` row names. A **host-scoped** table holds facts about the machine and its runtime directory — the
workspace prompt, the graph-artifact mirror, the token replay cache, daemon liveness, external usage samples, and a
registered host's own identity at its hub (`host_identity`), its own fact lane (`host_outbound_buffer`), the mark its
hub last answered on that lane (`host_high_water_seen`), and the runners it took in from other stores (`host_ingests`) —
and carries no runner key. Each host table also declares how a runner transfer treats its rows
(`info={"transfer": ...}`), which `blizzard/tests/test_runner_store_schema_declarations.py` holds every host table to.
How a table gains the key over rows it already holds is `bzh:keyed-table-migration`'s, in
[../../standards/persistence.md](../../standards/persistence.md).

## Adapters hold the bound seam (`bzh:runner-scoped-store`)

**Rule.** A `runner/store/internal/` adapter holds `RunnerStoreConnections` and builds every statement on a
runner-scoped table through its `select`, `exists`, `insert`, `update`, and `delete` builders, which apply the bound
runner to every runner-scoped table they name. The runner is a property of the connections instance — bound once, from
the host file's runner `id` — never an argument an adapter method takes or a value a caller supplies.

**Why.** An adapter that never writes the runner predicate by hand cannot forget it, and a key the seam stamps is the
binding the store was opened with rather than a value a caller can get wrong. Two runners sharing a store, or a store
carried from one runner to another, then cannot read or overwrite each other's rows.

**Scope.** The binding is set once and never changes (`RunnerAlreadyBound` refuses another id). Every composition binds
the stores to the configured runner's `id` before anything runs, the hub reachable or not: the host and tick graphs and
the offline read verbs. The invariant checker reads across runners through the exempt `runner_audit`, so it takes no
binding. The store never learns its runner from its own rows, and registration never adopts an id. A connection never
bound reads a runner-scoped table as empty and refuses a write with `RunnerUnbound`, so no writer lands an unowned row.
A runner transfer, which copies one runner's rows from one store into another and deletes them from one store, is
admitted: its adapter (`blizzard/src/blizzard/runner/store/internal/runner_transfer_store.py`) binds both stores'
connections to the moving runner and builds every statement through them, iterating the schema's runner-scoped tables
rather than a list of its own. How the binding survives a crash is
[../crash-correctness/runner.md](../crash-correctness/runner.md#binding-at-the-configured-id)'s to record.

**Detect.** The runner statement guard — a `before_execute` listener
(`blizzard/src/blizzard/runner/store/runner_guard.py`) the test suite switches on in every tier and production leaves
off — fails a select, update, or delete naming a runner-scoped table without a `runner_id` equality, and an insert into
one whose values lack `runner_id`, raising `UnscopedRunnerStatement`. Raw SQL is never walked. Only statements marked
runner-unscoped are exempt, and `bzh:host-stores-confined` confines the mark. A refusal is the finding, never something
to switch off: a test outside `blizzard/tests/test_runner_statement_guard.py` that borrows its `no_runner_guard` fixture
or unsets `BLIZZARD_RUNNER_GUARD` is itself the violation.
[The tier rules](../../verification/blizzard/tier-rules.md#the-runner-statement-guard-is-on-in-every-tier) own how the
test processes and spawned daemons install the guard. `blizzard/tests/test_runner_store_isolation.py` proves that runner
A's adapters read and change none of runner B's rows in one store. By eye: an adapter constructor typed `Engine`; an
adapter method taking a `runner_id` parameter; a raw `sa.select(table)` on a runner-scoped table inside an adapter.

**Do.** An adapter's read is `self._store.select(env_bindings, ...)`, and its insert is `self._store.insert(leases)`;
neither line names a runner, and both carry the bound one.

**Don't.** `list_leases(runner_id)` on a read repository — every caller now supplies the boundary, and the first one
passing the wrong id reads another runner's leases.

## Host tables only through `HostStores` (`bzh:host-stores-confined`)

**Rule.** A host-scoped table is reached only through `HostStores` (`blizzard/src/blizzard/runner/stores.py`), whose
members live in the `runner/store/internal/host_*.py` modules; no runner adapter names a host-scoped table, and no host
adapter names a runner-scoped one. The member exempt from the runner statement guard is a closed list of one, in its own
module:

- `runner_audit` (`host_runner_audit.py`) — the cross-runner reads, which cannot carry a runner equality: the invariant
  checker's audit of every runner's rows at once, and the foreign-store question of which runners the store's identity
  rows name, asked by `init` before any id is configured and by every verb that checks it: host start, `--check`, tick
  and the transcript verbs; and the shared pool's held read, `held_workspace_bindings`, every runner's held bindings in
  one workspace's pool.

**Why.** A host table is a door around the runner boundary by design; keeping every such door on one named seam, with
its exemptions a list a reviewer reads whole, turns "where can one runner's rows leak?" into a question with a short
answer.

**Scope.** Two cross-kind writes are admitted. `record_external_usage_attempt` (`host_external_usage_store.py`) writes a
usage sample, a host row, and its outbound report, a runner row, in one transaction. Its host statement is authored in
that host module and its outbound row is built through the runner builders, so the outbound row is stamped like any
other. A runner transfer's copy writes the moving runner's rows and the source's host rows on one destination
transaction, through one handle that carries no `Connection` to the domain: the runner half is built by the transfer
adapter's binding, and the host half by the `host_ingests` member (`host_ingest_store.py`), which merges the host rows
by each table's declared treatment and records an ingest; neither module names the other kind's tables. The
runner-unscoped mark itself — `RUNNER_UNSCOPED_OPTION`, or the `blizzard_runner_unscoped` string it stands for — appears
only in `runner/store/scoped.py`, the guard, the exempt member's module, and runner migrations. `scoped.py` declares the
mark. `blizzard/src/blizzard/runner/store/internal/invariants.py` reaches the store through the `runner_audit` member it
is handed, never by spelling the mark.

**Detect.** The host-store check in `blizzard/tests/test_layering.py` fails the unit tier on a runner adapter naming a
host-scoped table, a host adapter naming a runner-scoped one outside the admitted cross-kind write, and the
runner-unscoped mark spelled anywhere outside its admitted modules; the same module's planted-tree cases prove it
catches each form. By eye: a second exempt member, or a member added for a read a bound adapter could serve.

**Do.** The invariant checker's `runner:rows-name-registered-runner` reads every runner-scoped row through
`HostStores.runner_audit`.

**Don't.** A `list_all_leases` method on a runner adapter marked runner-unscoped so a status view can show "every
runner's" leases — it is a standing cross-runner read outside the closed list.

## See also

- [./tenancy.md](./tenancy.md) `bzh:tenant-scoped-store` — the hub's tenant seam; the runner guard and builders reuse
  the same key-scoping core (`blizzard/src/blizzard/foundation/store/`), configured for `runner_id`.
- [../crash-correctness.md](../crash-correctness.md) `bzh:invariant-checker` — the invariant every runner-scoped row is
  held to.
