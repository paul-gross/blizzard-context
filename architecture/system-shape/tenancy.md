# Tenancy

This spoke owns how the hub store keeps every tenant's rows inside that tenant — the key a table carries, the seam that
applies it, what stays global, and the few reads and passes that span tenants; the macro-shape hub is
[../system-shape.md](../system-shape.md). What a tenant is, and who may enter one, is the domain model's
([../../domain/tenancy.md](../../domain/tenancy.md)). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

The hub keeps one database for every tenant, and SQLite enforces no row-level boundary of its own, so the boundary is
the store seam's: an unscoped read must be hard to write, not merely wrong.

## Every tenant-owned table carries its tenant (`bzh:tenant-keyed-table`)

**Rule.** Every hub table not on the global list (`bzh:global-tables-closed`) carries `tenant_id NOT NULL` with a
foreign key to `tenants`, on every row directly — a child row included — and has an index whose leading column is
`tenant_id`. The scoped seam (`bzh:tenant-scoped-store`) stamps the key; no caller supplies it, so no domain type,
request model, or wire schema carries a `tenant_id` into a write.

**Why.** The filter has to be expressible on the table a statement actually reads — a tenant found through a join is
exactly the predicate a hand-written query forgets. A key a caller supplies is a key a caller can get wrong, while a key
the seam stamps is the scope the repository was opened with.

**Scope.** A listing or range index leads with `tenant_id`, so one tenant's feed never scans another's rows, and so does
an index a scoped read looks rows up through by a hub- or runner-minted id: every scoped read carries `tenant_id = ?`,
and SQLite, planning without statistics, picks whichever tenant-led index sits beside an id-led one and walks every row
the tenant holds per call. An index that also serves an `ORDER BY` carries the ordering columns after the lookup ones. A
primary key or unique constraint led by `tenant_id` counts as the table's tenant-led index, and a plain `tenant_id`
index that a tenant-led lookup index makes redundant is dropped. Two kinds stay hub-wide: the `(at, id)` cursor index of
a pass that pages across tenants in cursor order, kept beside the tenant-led one, and a credential's `token_hash` index,
which a hub-scoped read resolves before any tenant is known.

**Detect.** The tenant schema gate — a `blizzard:unit-test` over `schema.metadata` (`tests/test_tenant_schema_gate.py`)
— fails a table outside the global list whose `tenant_id` is missing, nullable, or without its foreign key, or that has
no index led by `tenant_id`. The test-suite statement guard (`bzh:tenant-scoped-store`'s Detect) fails an insert into a
tenant-owned table whose values lack `tenant_id`. The read-index gate (`tests/test_store_read_index_gate.py`, a
`blizzard:component-test`) reads a plan that seeks only the tenant prefix, or walks a whole named index in order, as
reading the table whole, beside a bare scan and an automatic index; a read that walks by design names its reason in an
`IndexWalkAllowance` (`tests/store_scan_allowlist.py`), scoped to that one read. By eye: a `tenant_id` field on a domain
dataclass, a request body, or a wire model that a write path reads; an adapter passing `tenant_id=` into `.values(...)`
itself.

**Do.** A fact table under a chunk carries `tenant_id` beside `chunk_id`, stamped by the scoped `insert` the adapter
built; the domain call that wrote it passed only the fact.

**Don't.** A fact table that omits `tenant_id` because "its chunk already has one" — every read of it now has to join
`chunks` to stay inside the tenant, and the first one that doesn't leaks.

## The global list is closed (`bzh:global-tables-closed`)

**Rule.** A hub table that carries no tenant key is named in `GLOBAL_TABLES` (`src/blizzard/hub/store/schema.py`), its
entry stating why it is global; nothing else is global. A table joins the list only when its rows are read before any
tenant is known or concern no tenant at all — the tenant boundary itself, hub-level identity, and the hub's own
machinery.

**Why.** Every table must be accounted for, or a table added without thought is silently hub-wide. A closed list with a
reason per entry makes "global" a decision a reviewer sees in the diff rather than a default anyone inherits.

**Scope.** A global table may carry a `tenant_id` as data without being tenant-owned — a membership names the tenant it
grants into, yet is read hub-wide to list a person's tenants. Outside the store, and not on the list: Alembic's version
table and the packaged artifacts served from the wheel. Packaged graphs are not global; each tenant holds its own.

**Detect.** The tenant schema gate fails a table that is neither keyed nor on the list, and a table on the list that
also carries a `tenant_id` column, save the entries the gate itself names as carrying it as data. By eye: a list entry
whose reason is "simpler" or "shared" rather than a fact about when its rows are read.

**Do.** `hub_event_log` is on the list because its rows are the hub's own occurrences — startup, migration, a tenant's
teardown, the exports' failures — which concern no tenant and which no tenant member reads.

**Don't.** Putting a configured record's table on the list so two tenants can share one row — sharing across tenants is
what the boundary forbids; each tenant configures its own.

## Adapters hold scoped connections only (`bzh:tenant-scoped-store`)

**Rule.** A `hub/store/internal/` adapter for a tenant-owned table holds `ScopedConnections` and nothing wider, and
builds every statement through its `select`, `insert`, `update`, `delete`, and `scope_join` builders, which apply the
scope's tenant to every tenant-owned table they name. The tenant is a property of the repository instance a caller was
handed — opened per tenant through `HubCore.open(scope)` — never an argument a method takes.

**Why.** Domain code that never writes the filter by hand cannot forget it, and a controller holding a read repository
cannot widen the scope it was given (`bzh:controller-read-only`). Repository Protocols keep their shape
(`bzh:repository-split`), because the tenant travels on the instance rather than through the signature.

**Scope.** The scope is the tenant and nothing narrower: a project filter is an ordinary argument of the read that
applies it, never part of the scope. Services are built from one tenant's `TenantStores`, never from the unscoped core
(`bzh:dependency-injection`). A write on a closed tenant's scope is refused inside its own transaction, so a writer that
opened its stores before the close cannot write behind the drain.

**Detect.** The test-suite statement guard — a `before_execute` listener (`src/blizzard/hub/store/tenant_guard.py`) the
test suite switches on in every tier that opens a hub store, and production leaves off — fails a select, update, or
delete naming a tenant-owned table without a `tenant_id` equality in its `WHERE` or join `ON`, and an insert whose
values lack `tenant_id`, raising `UnscopedTenantStatement`. Raw SQL is never walked. Only statements marked hub-scoped
are exempt: `HubScopedReads` (`bzh:hub-scoped-reads-confined`), the invariant checker's cross-tenant audits, and
migrations. `tests/test_layering.py` confines the exemption by name: `HUB_SCOPED_OPTION`, or the `blizzard_hub_scoped`
string it stands for — spelled as an import, a name, an attribute, a keyword argument, or a string — appears only in
`hub/tenancy.py`, `hub/store/tenant_guard.py`, the `hub/store/internal/hub_scoped_*.py` modules, `tools/invariants.py`,
and `hub/store/migrations/`; the same test fails a `ScopedConnections` constructed outside `hub/store/` and an import of
the guard outside `hub/store/` and `hub/app.py`, which installs it. By eye: an adapter constructor typed
`HubStoreConnections` or `Engine`; a repository method taking a `tenant` parameter; a raw `sa.select(table)` on a
tenant-owned table inside an adapter. A guard refusal is the finding, never something to switch off: a test outside
`tests/test_tenant_guard.py` that borrows its `no_hub_guard` fixture or unsets `BLIZZARD_TENANT_GUARD` is itself the
violation. [The tier rules](../../verification/blizzard/tier-rules.md#the-tenant-statement-guard-is-on-in-every-tier)
own how the test processes and spawned daemons install the guard.

**Do.** An adapter's listing reads `conn.select(s.chunks).where(...)`, and the domain asks for `stores.chunks.list(...)`
on the `TenantStores` its request resolved — neither line names a tenant.

**Don't.** `list_chunks(tenant_id, ...)` on a read repository — every caller now supplies the boundary, and one
supplying the wrong value reads another tenant's chunks.

## Cross-tenant reads go through one seam (`bzh:hub-scoped-reads-confined`)

**Rule.** A read that must span tenants goes through `HubScopedReads`, a read-only seam whose members form a closed
list, and nothing outside the hub-level modules it serves may hold it. A member exists only for a read that must happen
before a tenant is known, or that by its nature covers every tenant.

**Why.** Every cross-tenant read is a hole in the boundary by design; keeping them on one named seam with a fixed
membership turns "where can a tenant leak?" into a list a reviewer can read whole.

**Scope.** The members are of these kinds and no others:

- resolving a credential to its tenant — a runner's or a host's bearer token, a runner id at sign-in, an invitation
  token, a hub-executed node's marker — each returning the tenant beside its principal;
- a sweep's corpus read (`bzh:sweep-acts-in-row-tenant`), and the status reads of the hub's exports, whose cursors every
  tenant's rows share;
- tenant administration — whether a tenant is open, and the open tenants with their names.

A read of a global table is an ordinary hub-level read, not a member: memberships and hub administrators are global
(`bzh:global-tables-closed`), so listing a person's tenants or the hub administrators reads through the identity
repositories the hub-level services hold. Tenant deletion's own reads are hub-level the same way: the deletions a
teardown has yet to finish are read from `tenant_deletions` on the hub-level connections
(`TenantTeardownStore.underway`), not through the seam. A write never goes through it; a pass that must write across
tenants loops over open tenants and writes through each one's own stores.

**Detect.** The ast-grep rule `bzh:hub-scoped-reads-confined` (`contracts/ast-grep/rules/hub-scoped-reads-confined.yml`,
run by `blizzard:structural-gate`) refuses any naming of the seam — `HubScopedReads`, any `hub_scoped_*` module, helper,
or factory, or the `HubCore` field — whether as an import, an annotation, an attribute, or a string spelled for
`importlib` or `getattr`; its `ignores` are the allowlist. The member groups live in
`hub/store/internal/hub_scoped_<kind>.py` and are taken whole, through `build_hub_scoped_reads`:
`tests/test_layering.py` fails an import of one member group anywhere outside those modules. By eye: a member added for
a read a tenant-scoped repository could serve; a member that writes; an allowlist entry added for a route under a
tenant's own family.

**Do.** A runner's or a host's bearer token resolves through a `HubScopedReads` member to its registration and that
registration's tenant; the request then opens that tenant's stores and does everything else through them.

**Don't.** Adding a `list_all_chunks` member so a board view can show "everything" — no tenant-member view spans
tenants, and the member would be a standing cross-tenant read with no reason to exist.

## Uniqueness a tenant can observe is per tenant (`bzh:tenant-scoped-uniqueness`)

**Rule.** Every primary key, unique constraint, and unique index on a tenant-owned table holds `tenant_id`, or holds a
column the schema marks hub-unique (`info={"hub_unique": True}`) — a hub-minted ULID or an autoincrement surrogate, the
table's own or a foreign key to one.

**Why.** A natural key a tenant chooses — a name, a slug, a work ref, an id a runner minted — is one two tenants can
both claim; unique across the hub, the second tenant's write fails on a row it cannot see, and the failure tells it the
row exists. A key holding a hub-minted id is already unique within one tenant, because the row it names belongs to
exactly one.

**Scope.** A non-unique lookup by a tenant-chosen name is rebuilt led by `tenant_id` too, so resolving the name runs
within the tenant. Identity uniqueness — usernames, emails, provider subjects — lives on global tables and stays
hub-wide. A table whose natural key other tables' foreign keys point at takes a surrogate id instead of a composite key,
so a later narrowing changes one unique constraint rather than every child.

**Detect.** The tenant schema gate fails a tenant-owned table whose primary key, unique constraint, or unique index
holds neither `tenant_id` nor a hub-unique column. By eye: a column holding a hub-minted id without a foreign key and
without the hub-unique mark; a lock or sequence table keyed by a name a tenant chooses without the tenant.

**Do.** `keyed_locks` is keyed `(tenant_id, namespace, key)`: two tenants locking the same graph name each lock their
own row.

**Don't.** `keyed_locks` keyed `(namespace, key)` — the second tenant's insert loses to the first's, its tenant-scoped
lock `UPDATE` then matches nothing, and its write runs unserialized.

## A sweep acts on each row through that row's tenant (`bzh:sweep-acts-in-row-tenant`)

**Rule.** A hub sweep stays one pass per hub (`bzh:steppable-loop`): it reads its corpus through `HubScopedReads`,
leaving closed tenants out, and makes each write for a row through the stores and services of that row's own tenant. A
pass never holds one tenant's scope while acting on another tenant's row.

**Why.** One pass per hub keeps the loop's cost and crash points independent of how many tenants exist, and acting
through the row's own tenant is what keeps a write the pass makes on the same side of the boundary as the row that
caused it.

**Scope.** A probe that gates a pass (`bzh:probe-gated-pass`) is read hub-wide, in one statement, and its value is per
tenant (`bzh:pass-isolates-tenants`). A hub-wide job that is not a sweep — boot slot release, key coverage, key rotation
— loops over open tenants and acts through each one's stores. Trace export and fact egress write nothing into any
tenant's store; their rows carry their tenant's id instead. A one-tenant pass is the same pass narrowed to one tenant:
it reads the same hub-scoped probe and corpus and acts only in that tenant.

**Detect.** No structural gate reaches it: the statement guard sees a scoped write as scoped whichever tenant it was
opened for. A reviewer asks of each write a pass makes: whose scope is this, and is it the tenant of the row being acted
on? A sweep's service test seeds two tenants and asserts each write lands in its row's tenant.

**Do.** The close drain reads every pending close across open tenants, then for each one opens the services of the
tenant the close belongs to and issues the close through that tenant's work-source client and event log.

**Don't.** A pass that opens the first row's tenant's stores before its loop and reuses them for every row — the second
tenant's annotations are written into the first tenant's event log.

## A hub-wide pass keeps one tenant out of every other's outcome (`bzh:pass-isolates-tenants`)

**Rule.** A hub-wide pass that converges or drains work per tenant keeps three things per tenant: its convergence state
(a tenant is due on its own probe value and last full pass alone), its share of the pass's budget (a fair share across
the tenants with due work), and its fault boundary (a raise from one tenant's open, read, or write is caught at that
tenant, logged naming it, and counted as that tenant unconverged or failed, and the pass goes on to the next tenant).

**Why.** The hub runs one pass for every tenant, so any state, budget, or failure the pass shares is a channel through
which one tenant's broken source or burst of work changes what the pass does for another — the wall
([../../domain/tenancy.md](../../domain/tenancy.md)) holding for the store and not for the hub's own loops.

**Scope.** It binds the forge-status and event-derivation reconcilers, the close drain, and tenant teardown. Trace
export and fact egress are outside it: each advances one cursor in fact order, which is the order their sink receives,
so each holds the cursor on any fact it cannot place; isolating them needs a cursor per tenant, which is a separate
change. Boot loops and key rotation fail fast by design and are not periodic passes. The probe read stays hub-wide and
one statement (`bzh:sweep-acts-in-row-tenant`), and a pass skips its corpus reads when no tenant is due. A one-tenant
pass reads and writes only its own tenant's convergence entry, never rebinding or pruning state across tenants, and
leaves the close drain's rotation unmoved.

**Detect.** The poisoned-tenant fixture, `tests/pass_isolation.py`, is a `blizzard:component-test`: it runs a pass twice
on the virtual clock, once with a tenant whose units raise, report unconverged, or hold a burst of due work, and once
without that tenant, and fails when any other tenant's recorded calls differ. It also interleaves a poisoned tenant's
one-tenant passes with timed passes and fails the same way. Every pass this rule binds uses it. By eye: a convergence
flag folded across tenants, one probe value for the hub, a budget sliced from one ordered list, or a catch around a
pass's whole tenant loop rather than inside it.

**Do.** The close drain groups due intents by tenant and takes one in turn from each, starting at a rotating tenant,
until it reaches its pass limit, so a tenant with a burst never takes another's slots.

**Don't.** `converged &= reconcile(tenant)` across the tenants: one tenant that never converges keeps every tenant's
probe from being recorded, and the healthy ones redo their full pass every interval.

## See also

- [../../standards/persistence.md](../../standards/persistence.md) `bzh:keyed-table-migration` — how a revision puts the
  tenant key on a table that already holds rows.
- [./exclusive-writes.md](./exclusive-writes.md) `bzh:store-exclusive-write` — how an exactly-one-wins decision locks
  its row, a lock taken inside one tenant's scope like any other write.
