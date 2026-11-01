# Repository access

These rules refine the dependency-inversion seam [`./clean-architecture.md`](./clean-architecture.md) owns
(`bzh:dependency-inversion`): they govern who may hold which repository and what crosses the domain boundary. For read
cost, see [`./read-cost.md`](./read-cost.md); for periodic-pass cadence, see [`./lanes.md`](./lanes.md). Each rule below
uses the slot skeleton `winter-canon:/rule-shape.md` owns (`canon:rule-shape`), with its `bzh:` id carried in its
heading.

## Split every repository seam (`bzh:repository-split`)

**Rule.** Every repository seam splits into a read-only Protocol and a write Protocol, and a collaborator depends on the
narrowest one its job needs.

**Why.** The Protocol a service depends on makes its intent enforceable at type-check time, and is what the layer gate
`bzh:controller-read-only` keys on.

**Detect.** One repository Protocol exposing both queries and mutations, or a read-path service holding a write-capable
one.

**Scope.** A seam whose reads only project other concepts' own fact tables, with no mutation of its own, stays read-only
rather than pairing with an empty write half: `blizzard/src/blizzard/hub/domain/chunk/ports/facts.py`'s
`IReadChunkFactsRepository` has no write counterpart because `load_facts`/`load_all_facts` project the union of the
other seams' own writes, and splitting that projection per concept would turn one bounded read into one per seam. A hub
Protocol carries no tenant in its signatures: the tenant is the instance's, opened per tenant
(`bzh:tenant-scoped-store`, [./system-shape/tenancy.md](./system-shape/tenancy.md)), so the read half a controller holds
cannot widen to another tenant either.

**Do.** `blizzard/src/blizzard/hub/domain/chunk/ports/record.py` pairs `IReadChunkRecordRepository` with
`IWriteChunkRecordRepository`, the write variant extending the read one; the composition root binds the write variant
only where mutation is required.

**Don't.** One combined repository injected everywhere, handing a controller that only lists chunks the power to delete
them.

**See also.** `blizzard/exemplars/python/exemplar/hub/domain/permits/model.py`
([../exemplars/index.md](../exemplars/index.md)) — a read/write Protocol pair, implemented by the exemplar `PermitStore`
and bound in the exemplar `composition.py`. [`./system-shape/exclusive-writes.md`](./system-shape/exclusive-writes.md)
`bzh:store-exclusive-write` — the one seam where a write Protocol splits further than read and write; read it before
adding or calling a `*_locked` method.

## Controllers hold read repositories only (`bzh:controller-read-only`)

**Rule.** Access is layer-gated — controllers at the API and CLI edges hold read-only repositories only, and write
repositories belong to the domain layer alone.

**Why.** A controller able to write around the domain can violate an invariant the domain exists to protect.

**Scope.** A controller answering a query straight from a read model is fine: reads bypass no invariant.

**Detect.** A router or CLI handler injecting a write repository, or a mutation performed in an edge handler instead of
delegated. `tests/test_layering.py` fails the unit tier on `IWriteSessionStore` named anywhere other than
`foundation/operator_sessions/` (the Protocol's own package) and the composition roots — `login`/`logout` take the
`SessionService` application service instead, never the raw seam.

**Do.** `blizzard/src/blizzard/hub/api/queue.py` stays read-only over the store and delegates its writes to the queue
domain services, which hold the write chunk repository.

**Don't.** An API route that constructs a chunk and saves it through a write repository.

## Name the unit of work at the domain seam (`bzh:unit-of-work`)

**Rule.** When one domain operation must commit work across repositories together, let the domain orchestrator open a
named unit of work and pass its opaque transaction to each participant.

**Why.** The domain names the atomic operation without acquiring a database connection or making one repository own
another's behavior. One transaction makes its participating reads and writes share visibility and commit or roll back
together.

**Scope.** The hub's tenant-scoped seam is `IHubTransactions` and `Transaction` in
`blizzard/src/blizzard/hub/domain/kernel/transactions.py`. The identity unit has its own seam in
`blizzard/src/blizzard/hub/auth/identity_transaction.py`; its tenant participation is described in
[./crash-correctness/hub.md](./crash-correctness/hub.md). A single repository's self-contained write need not open a
domain unit.

**Detect.** A multi-repository atomic operation hidden in one adapter, or a domain service carrying a SQLAlchemy
connection. Review the transaction boundary and each participant; no general mechanical gate enforces this rule.

**Do.** `DeleteService.delete` opens `IHubTransactions.begin` and coordinates chunk, dependency, and item repositories
with the resulting token.

**Don't.** Make the item adapter delete a chunk and release another repository's dependencies to manufacture atomicity.

**See also.** `bzh:transaction-participation`, `bzh:transaction-graduation`, `bzh:short-locked-unit`,
`bzh:tenant-scoped-store` ([./system-shape/tenancy.md](./system-shape/tenancy.md)).

## Participate through the supplied transaction (`bzh:transaction-participation`)

**Rule.** A repository participating in a unit of work uses the supplied transaction for every participating read and
write, without opening or committing an independent transaction.

**Why.** A separate connection can miss earlier writes or commit even when the unit rolls back. Validating the token
keeps its authority confined to its store, tenant, and lifetime.

**Scope.** A repository may also offer a standalone call that opens its own transaction when no token is supplied.
Connections and token resolution stay in the store layer; `connection_for` in
`blizzard/src/blizzard/hub/store/transactions.py` validates the token and any required lock coverage.

**Detect.** A participant ignores its token, opens a second write, accepts a token from another scope or after its
lifetime, or resolves a connection in domain code. Review the adapter and callers; no general mechanical gate enforces
this rule.

**Do.** `WorkItemStore.withdraw_open` joins a supplied transaction or opens its own scoped write when called alone.

**Don't.** Call a standalone committing repository method from inside a unit expecting rollback to undo it.

**See also.** `bzh:unit-of-work`, `bzh:transaction-graduation`.

## Declare locks before participating (`bzh:transaction-graduation`)

**Rule.** Graduate a hub unit requiring exclusive resources once, before any repository statement, by declaring its
complete lock set; pass the resulting locked token to its participants.

**Why.** Taking a partial set and later acquiring more can invert another writer's order and deadlock. The locked token
lets adapters verify authority over each resource they mutate.

**Scope.** `lock_chunks`, `lock_keys`, and `lock_set` graduate the unit; the store sorts chunk ids and then
namespace-key pairs. The original token is superseded, and a graduated token cannot acquire further locks. The scoped
tenant opener precedes graduation; lock ordering and the remaining legacy seams are owned by
[./system-shape/exclusive-writes.md](./system-shape/exclusive-writes.md) `bzh:store-exclusive-write`.

**Detect.** A repository statement before graduation, a second graduation, use of the superseded token, or a locked
mutation without coverage of its resource. `blizzard/tests/test_hub_transactions.py` exercises token lifetime, scope,
graduation, and coverage.

**Do.** `DeleteService.delete` calls `transaction.lock_chunks` before reading fresh facts and passes the locked token to
the repositories.

**Don't.** Lock one chunk, read a repository, then attempt to add another chunk to the lock set.

**See also.** `bzh:transaction-participation`, `bzh:short-locked-unit`, `bzh:store-exclusive-write`.

## Keep locked units short and local (`bzh:short-locked-unit`)

**Rule.** Keep a locked unit of work short and perform no network I/O while it is open; do external calls outside the
transaction, then re-read and validate any race-sensitive facts under its locks.

**Why.** A remote call can wait indefinitely while holding locks needed by other writers. Moving it outside the unit
requires a fresh guard because state can change before the lock is acquired.

**Scope.** This applies to the entire locked scope, including calls made through collaborators, not just repository
methods. The ordinary tenant unit opens through the tenant-open guard: it refuses a closed tenant and holds its row lock
until commit or rollback, so close and a concurrent ordinary write serialize. Only tenant teardown's drain and
completion use the teardown opener for a closed tenant; an ordinary unit must not bypass the guard or use that opener.
The scoped store contract is owned by `bzh:tenant-scoped-store`
([./system-shape/tenancy.md](./system-shape/tenancy.md)).

**Detect.** A network client call inside a locked transaction, or an ordinary unit opened without the tenant-open guard
or through the teardown opener. Review the full scope and its collaborators; no general mechanical gate checks network
calls inside a unit.

**Do.** `DeleteService.delete` reads fresh facts and performs its local repository writes inside the locked unit.

**Don't.** Hold a chunk lock while waiting for a forge API response, or use teardown's opener to write to a closed
tenant.

**See also.** `bzh:unit-of-work`, `bzh:transaction-graduation`, `bzh:store-exclusive-write`.

## Keep sibling adapters independent (`bzh:sibling-adapter-independence`)

**Rule.** Coordinate distinct repositories through their domain-facing seams, not by importing or invoking a sibling's
adapter implementation or private helpers.

**Why.** Adapter-to-adapter dependencies hide the domain operation and couple persistence implementations. A shared
transaction lets each repository own its own facts without sacrificing atomicity.

**Scope.** Existing composite mint methods in `WorkItemStore` use shared store helpers; they remain current
implementation, not a pattern for new cross-repository operations.

**Detect.** An adapter imports a sibling adapter or its private write helper to perform another repository's mutation.
Review the operation and move coordination to the domain seam.

**Do.** `DeleteService.delete` invokes each repository's own write under one transaction.

**Don't.** Put chunk deletion, dependency release, and item withdrawal in the item adapter.

**See also.** `bzh:unit-of-work`, `bzh:transaction-participation`.

## Domain operations take objects (`bzh:domain-takes-objects`)

**Rule.** Domain operations receive already-loaded, typed domain objects, never raw identifiers; resolving an identifier
to its object is an edge concern, done before the domain is invoked.

**Why.** A domain that takes objects cannot fail on a missing or malformed id mid-rule, and its signatures state exactly
which entities a rule operates on.

**Exception.** A parameter that resolves not to the entity the operation is about, but to a guard the domain must itself
evaluate as part of its own business rule. `ClaimService.claim`'s `runner_id: str` resolves a paused-runner denial check
inline — a claim-denial rule that belongs in the domain, not at the edge — so it stays a raw id, reasoned and registered
at its own site with `# ast-grep-ignore: bzh:domain-takes-objects`.

**Scope.** A layer that holds no entity type for the identifier at all — the runner's chunk-keyed operations, where no
`Chunk` type exists locally (`bzh:facts-not-status` keeps each per-concept table independent) — still resolves at the
edge: it mints a typed scope naming exactly the facts the rule reads, rather than loading an aggregate that does not
exist. The scope is data, not behavior, and never grows into one.

**Detect.** A domain signature typed `chunk_id: str` rather than `chunk: Chunk`, or a domain method loading an entity
from an id it was passed. `bzh:domain-takes-objects` is tooled by `blizzard:structural-gate`'s ast-grep scan
([`../verification/blizzard.md`](../verification/blizzard.md)), scoped to `hub/domain/` and the runner's domain core
(`bzh:domain-core`): one glob per top-level `bzh:domain-package-layers` runner node, with `**/internal/**` ignored.
`blizzard/tests/test_layering.py` holds those globs equal to the runner layer table, so a new node is in scope with no
edit to the rule.

**Do.** `blizzard/src/blizzard/hub/domain/operations/complete.py` declares `complete(self, chunk: Chunk, *, by: str)`;
the controller resolves that chunk through a read repository first. Where no aggregate exists,
`blizzard/src/blizzard/runner/api/chunk_scope.py` mints the typed scope instead — `TakeoverService.open` takes a
`TakeoverOpenScope` resolved there, never a bare `chunk_id`.

**Don't.** `advance(chunk_id: str)`, loading the chunk inside the domain.
