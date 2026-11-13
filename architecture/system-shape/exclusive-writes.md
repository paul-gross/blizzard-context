# Exclusive writes

This spoke owns how a hub write keeps true the decision it acts on — an "exactly one wins" decision above all — once the
hub's store, not an in-process lock, is the one thing every writer shares; the macro-shape hub is
[../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## A decision's write re-establishes its read (`bzh:write-reestablishes-read`)

**Rule.** Make every hub write that acts on a domain decision re-establish, as it lands, the facts the decision read. In
preference order:

1. **Compare-and-set.** The domain decides from the entity it holds and hands the write the version or monotonic token
   it read — a revision, an epoch, a high-water seq. The store writes only while that token still holds and otherwise
   raises a typed conflict, which the domain maps to a refusal or a retry.
2. **Decide inside the unit.** Where no one token covers what the decision read, the domain service opens the unit,
   graduates it once (`bzh:transaction-graduation`, [../repository-access.md](../repository-access.md)), re-reads the
   guards through repositories with the token, decides in domain code, and writes with the same token.

**Why.** A fact read before the write's transaction can change before the write lands, and a write that re-checks
nothing commits a decision on state that no longer holds. A conditioned write costs one predicate and holds no lock
across reads, so it comes first.

**Scope.** The entities the edge resolves (`bzh:domain-takes-objects`) are decision inputs only through one of these two
forms. An exactly-one-wins decision taking the second form locks in the order `bzh:store-exclusive-write` owns; a
compare-and-set write needs no lock of its own, its conditional update being the check and the write at once. A create
whose only race is a duplicate key is no decision here (`bzh:store-exclusive-write`'s Scope).

**Detect.** Not mechanically checkable; judged at review:

- A service or route that reads an entity or fact, decides on it, then calls a write carrying neither the token it read
  nor a unit graduated before a fresh re-read.
- A typed conflict caught and dropped, or retried without deciding again on the fresh state.
- A store method re-evaluating the decision's predicate to make the write safe — a `bzh:store-refuses-stale` violation,
  not a fix for this one.

**Do.**

- Compare-and-set: `ScopeLifecycle.retire` (`hub/domain/garden/scopes.py`) decides on the scope it was handed and calls
  `record_lifecycle` with `from_revision=scope.revision`; `ScopeStore.record_lifecycle`
  (`hub/store/internal/scope_store.py`) moves the revision only from that value, raising `ConfigRevisionConflict`
  (`hub/domain/config/errors.py`) with the current one otherwise.
- Inside the unit: `DeleteService.delete` (`hub/domain/operations/delete.py`) takes the chunk its route resolved, locks
  it, re-reads its facts, standing edges, and record under the locked token, decides with `require_deletable`, and
  writes with that token.

**Don't.** A service that checks the chunk it was handed is not terminal, then appends a fact on a fresh scoped write —
a stop committing between the check and the append is silently outlived.

**See also.** `blizzard/exemplars/python/exemplar/hub/domain/permits/service.py`
([../../exemplars/index.md](../../exemplars/index.md)) — compare-and-set as reference code: each verb decides on the
permit it was handed and writes at that permit's revision, refusing `PermitChanged` with `409`.

## The store refuses stale writes, never disallowed ones (`bzh:store-refuses-stale`)

**Rule.** Let a hub store method refuse a write only as stale — a version or monotonic token that moved, a uniqueness
constraint, an insert-if-absent that found its row — never by evaluating a domain predicate (terminal, open, retired,
closed) to admit or refuse it. The domain decides the predicate, from facts the store reads for it
(`bzh:write-reestablishes-read`).

**Why.** A predicate restated in the store is a second owner of a business rule (`bzh:domain-orchestration-split`,
[../clean-architecture.md](../clean-architecture.md)), and it drifts from the domain's own decision without either
failing. Freshness is a property of the row the store holds; legality is the concept's.

**Scope.** Binds what admits or refuses a write. A read that returns a status-family fact, or filters a projection by
one, decides no write.

**Detect.** A store write method that reads a status-family fact — `is_terminal`, a closure, a retirement — and returns
or raises a refusal from it. Judged at review; no mechanical check. The fix returns the fact to the domain and
conditions the write on a token or moves the decision inside the unit (`bzh:write-reestablishes-read`).

**Do.** `ScopeStore.record_lifecycle` refuses on the revision alone; whether retiring an already-retired scope writes
anything is `Scope.set_retired`'s decision (`hub/domain/garden/scopes.py`), made before the store is called.

**Don't.** A store `append_answer` that runs the chunk's terminal check in its `WHERE` and returns a terminal refusal —
the terminal rule now has two owners, and the store's copy keeps refusing after the domain's changes.

**See also.** `blizzard/exemplars/python/exemplar/hub/store/internal/permit_store.py`
([../../exemplars/index.md](../../exemplars/index.md)) — `PermitStore.record_fact` refuses on the permit's revision
alone, raising `PermitChanged`, and judges no permit state.

## An exactly-one-wins decision locks its row before it reads (`bzh:store-exclusive-write`)

**Rule.** A decision the hub commits to exactly once — a claim, or any write another such decision's guard reads consult
— runs in one write transaction that locks a row before every decision guard read on that same connection. After the
tenant-row opener, a known row is locked by a no-op update; a keyed lock may first select and conditionally insert its
lock row under a savepoint before the no-op update. None of these acquisition reads is a decision guard read. A read
that gates admission independently of the race itself (a paused runner, checked once before the lock opens) or that
resolves a different aggregate this lock does not cover (a graph's retirement) is not a guard read this rule governs:
nothing about the exactly-one-wins race depends on when it runs, so it may stay on its own connection, ahead of the
lock, without reopening anything the lock closes. The scoped write's own opening lock on its tenant's row
(`bzh:tenant-scoped-store`) precedes decision-lock acquisition; every write on a tenant's stores issues it first — save
the one that creates the tenant, which inserts that row instead.

**Why.** An in-process lock only serializes callers inside one process; the moment a second hub process shares the
store, two processes' own locks stop serializing each other, and the transaction is the only thing both still share.
Locking first is what makes the guard reads atomic with the write: on SQLite the lock takes the single writer lock
before any later read; on Postgres it takes the row lock a concurrent locker of the same row queues behind.

**Scope.** Governs the chunk claim and every writer it must exclude — edit, restart, delete, dependency declare, group,
stop, complete, detach, and requeue — and the epoch-fenced writes (`bzh:epoch-fencing`), which the row lock serialises
against stop and restart. It also governs the route-token rekey, whose holder and ended-chunk guards are re-read under
the chunk's lock, and three decisions whose guard reads facts the write itself creates: chunk ingest's pointer-held
refusal, the default graph's first mint, and promote's promotability judgment. It governs the secret-retire /
referrer-write pair too: a secret's retire reads that no active work source or repository references it, and each such
record's create, edit, or enable reads that its secret is not retired, so the domain unit of each declares the secret's
`SECRET` key before it reads. The forge-retire / referrer-write pair beside it does the same on the forge's `FORGE` key:
a forge's retire reads that no enabled record names it, and each referrer's write reads that its forge is live. Three
more keyed namespaces guard closure judgments. A garden proposal's edit, attach, detach, pass, and accept each declare
its `GARDEN_PROPOSAL` key (`garden_proposal_lock`) and re-read its closure under it; the minting accept hands that key
to `WorkItemEditService.accept_create`, which declares it beside its own. Garden delivery declares the plan's chunk and
the `FINDING` key (`finding_lock`) of every finding it expects, and the finding exit declares the `FINDING` keys of
every finding it records facts for. A work item's edit, withdraw, and deliver each declare its `WORK_ITEM` key
(`work_item_lock`) and re-read the item's closure under it. The chunk delete pre-reads the chunk's hub-source refs,
declares the chunk and those refs' `WORK_ITEM` keys, and re-reads the record under them; a ref outside the declared keys
ends the run before any write, and the delete runs again over the union. Each of these stores' writes takes the
`LockedTransaction` and judges no closure itself. The flow pair is governed too: a turn's admission and a submission's
close read their flows' open turns and the queue ahead, so their unit declares the submission's chunk and a `FLOW` key
per flow it holds; a stop, completion, or restart reads its chunk's waiting submissions under the chunk lock, which a
turn also declares. A macro-shape constraint on deployment topology, on what holds once more than one hub process may
share a store — not a `kill -9` crash-correctness requirement; one hub process already serializes every one of these
correctly today. The tenant-row lock ahead of the decision's lock changes neither guarantee: on SQLite it already took
the writer lock, and on Postgres every writer takes the tenant row first and its chunk or keyed rows after, so the order
two writers lock in never inverts. Dependency **release** needs no row lock for cycle safety: it can only shrink the
standing set and can never close a cycle. Its ordering against a fold's edge rewrite still depends on the residual
per-tenant lock in [Known debt](#known-debt). A create whose only race is a duplicate of a tenant-chosen name is no
decision under this rule: the table's tenant-led primary key or unique constraint (`bzh:tenant-scoped-uniqueness`)
admits exactly one insert, and the store maps the losing insert's `IntegrityError` to the named conflict —
`SecretStore.create` (`hub/store/internal/secret_store.py`) is the pattern. A create that reads state before its insert
— a cap, a parent's state, a default it mints — stays a decision under this rule, in the keyed-lock form under **Do**.

**Detect.**

- An in-process lock (`threading.Lock` or equivalent) in `hub/`, guarding a check-then-act sequence against another
  writer — mechanically flagged by this rule's ast-grep rule (`contracts/ast-grep/rules/store-exclusive-write.yml`),
  which flags any `import threading` under `src/blizzard/hub/**`.
- A `.with_for_update()` call under `src/blizzard/hub/**` — it renders nothing on SQLite, so the guard read holds no
  writer lock. Mechanically flagged by `contracts/ast-grep/rules/store-no-for-update.yml`.
- A decision guard read ahead of its decision lock, an unrelated statement ahead of lock acquisition, or a write that
  locks a chunk or keyed row before its tenant's row. Opposite lock orders can deadlock. Not mechanically checkable;
  judged at review.
- A locked transaction whose row lock targets a row that may not yet exist when two writers race to create it — a no-op
  `UPDATE` locks nothing on an empty table, so the exclusion never engages. Not mechanically checkable; judged at
  review. The remedy is the keyed-lock-row form under **Do**.

**Do.** A lock on a concept no tenant owns — the identity lock, the tenant-lifecycle lock — is a seeded row of the
`hub_locks` table, taken by `lock_hub` (`hub/store/locking.py`) and declared through `lock_set(hub=)` on a tenant unit
or `begin(hub=)` on the identity unit; the migration seeds it and `lock_hub` never inserts. The order is `IDENTITY`,
then the tenant's rows (its row, then chunk and keyed rows), then `TENANT_LIFECYCLE`: a tenant unit names only
`TENANT_LIFECYCLE`, an identity unit takes `IDENTITY` first and names only `TENANT_LIFECYCLE`.

**Do.** `lock_chunk_row` (`hub/store/locking.py`) — a no-op `UPDATE` on the chunk's own row, already minted before any
claim, edit, or dependency write can reach it — called as the first statement after the tenant-row lock
`ScopedConnections.write` (`hub/store/scoped.py`) opens with, with every guard read that follows it on the same
connection. `IHubTransactions.begin` opens a tenant unit; its `lock_set` declares the complete set once before any
repository statement, ordering chunk ids before sorted keys. The resulting opaque token goes to each participating
repository (`bzh:transaction-graduation`, [../repository-access.md](../repository-access.md)); this order prevents
writers naming the same resources in different orders from deadlocking on Postgres. Store adapters resolve the token,
not the domain. `IChunkExclusiveWrites` and its `*_locked` methods are this seam's legacy form
(`bzh:transaction-participation`).

A decision whose race has no existing row to lock — two ingests of one pointer, two first mints of one graph name —
locks a row of `keyed_locks` instead, through `lock_keys` (`hub/store/locking.py`). Every namespace is a `LockNamespace`
member, and every key a `LockKey`, in `hub/domain/kernel/locks.py`. The table is lock-only: it holds no state, nothing
reads it as a fact, and its rows are never deleted. For each distinct key, in sorted order, the helper first selects the
row, inserts it if absent inside a savepoint that swallows `IntegrityError`, then runs a no-op `UPDATE` to lock it
before any decision guard read. The table's key is per tenant (`bzh:tenant-scoped-uniqueness`). Each decision keys by
its own namespace: a pointer by `(source, ref)` encoded injectively, a graph by its name, a queue list's ranking by the
list, and a transcript ingest by the calling runner's lane (`transcript_lane`) and each chunk its batch names
(`transcript_chunk`) — a lane holds no row until its first mark, and a record may name a chunk the hub no longer holds.
A flow is keyed by its resource (`flow_lock`, `hub/domain/delivery/flows.py`). A cadence mint keys its errand by chore
and scope, encoded injectively (`cadence_errand`), in one `lock_set` beside, for a promoting chore, both ranking locks
and the fresh chunk's id, which names no row yet and so contends with nothing. The canonical sort takes chunk ids first,
then keys by namespace, so `cadence_errand` is taken ahead of the ranking locks, and an operator's promote, which takes
its chunk and then the ranking locks, waits on the mint at the ranking locks rather than deadlocking with it. The
urgency's three namespaces (`blizzard/src/blizzard/hub/domain/urgency/ports.py`) are `urgency`, keyed by urgency id, and
`urgency_order` and `tenant_settings`, each on one fixed key; they sort after `queue_ranking` and before `work_ref`,
`cadence_errand` ahead of them all. A retire takes the settings lock, the retiring urgency's, and `move_to`'s, and
re-reads the default and the open chunks under them. In the same `lock_set` it locks the open chunk rows it moves, read
ahead of the unit: chunk ids sort ahead of keys, so it takes each row before the urgency keys, in the order a chunk edit
takes its row and then the urgency it names, and the two never deadlock. A re-read that finds an open chunk outside the
locked set — one that took the urgency after the read ahead — writes nothing, and the retire runs its unit again over
the wider set. A settings edit takes the settings lock and the named urgency's. A mint takes the settings lock, the
urgency a read ahead of its unit found as the default, and every urgency a link of its chain named ahead of it, retired
or not — the stated one, the chore's override, the routine's default — beside its own lock set; under them it re-reads
each and resolves the chain (`blizzard/src/blizzard/hub/domain/urgency/chain.py::resolve_chain`) over what it re-read. A
chunk edit naming an urgency opens through `IChunkExclusiveWrites.locked` with `keys=`, taking the chunk row and that
urgency's key and no settings lock, and re-reads the urgency under them. A routine or cadence write that newly names
urgencies — a routine's default, a chore override its stored cadence names on no chore — opens a unit locking each one's
key and re-checks each live under it (`UrgencyReferences.held`); a configuration apply adds those keys to its plan's
locks and refuses an entry as stale when such an urgency's revision has moved since the plan read it. A reference the
write leaves is guarded by the record's own revision, which a retire clearing the reference moves. Every change of the
default and every retire takes the settings lock, so a mint's re-read default is live, and a retire never runs beside a
write taking up the urgency it retires. Create and both reorders take the `urgency_order` lock, re-reading the order
under it. A new decision graduates its unit with `lock_keys`, or `lock_set` when it spans namespaces; the existing ones
reach it through the legacy handles `IChunkExclusiveWrites.locked_work_refs` and `IWriteGraphRepository.locked_name`,
each its own type — never an `ILockedChunkRead`, so a handle that holds no chunk-row lock cannot satisfy a chunk-row
`*_locked` write.

The runner's store has no `keyed_locks` table, and the rule's scope names the hub; the runner applies the
lock-a-row-known-to-exist form by analogy. The operator's pause and lift, the ceiling's self-engagement, and the
takeover open each take a no-op `UPDATE` on their own runner's `runner_identity` row before reading their guard on that
same transaction (`runner/store/internal/pause_store.py`, `runner/store/internal/takeover_store.py`); a runner holding
no identity row yet has no neighbour to race.

An epoch-fenced write takes the lock-then-guard form through `fence` (`hub/store/internal/chunk_rows.py`), which the
write calls on the caller's locked unit after the lock and its replay probe and before its first insert. It applies the
caller's terminal verdict — decided by the domain from chunk facts read under the same lock — and reads the newest epoch
there, so a stop or restart cannot land between the guard and the write.

**Don't.** A `threading.Lock` shared by `ClaimService` and `EditService`, serializing their read-then-write CAS in one
process — correct until a second hub process starts against the same store, at which point the two locks stop
serializing each other and the race reopens with nothing left to catch it.

## A pool draw runs under its workspace's host-wide lock (`bzh:pool-acquisition-exclusive`)

**Rule.** The draw from a workspace's environment pool — from the read of the host's held environments to the recorded
binding — runs under that workspace's one in-process acquisition lock, shared by every runner the host serves. A runner
that cannot take the lock without waiting skips its claim for that tick and does not wait for it.

**Why.** `bzh:environment-held-once` needs one arbiter of the pool, and the runner store has no row both runners' draws
could lock, so the host's in-process lock is the arbiter. A runner that waited on the lock inside its claim would hold
the tick before its Advance and transcript steps ran, stalling the leases it already serves for as long as another
runner's draw takes.

**Scope.** Governs `ReadyQueue.claim_one` (`runner/lifecycle/claim.py`) and any later path that draws an environment
from a pool. The hub claim that follows the draw runs outside the lock. Exactly-once still rests on `require_unheld`,
which the draw runs under the lock.

**Detect.**

- A pool draw outside the workspace's acquisition lock. Not mechanically checkable; judged at review.
- A blocking acquisition of the lock from a loop step. Not mechanically checkable; judged at review.
- A second process serving one data directory, which voids the premise.

**Do.** `IWorkspaceAcquisition.try_acquisition_lock` yields whether the lock was taken; `claim_one` returns `False`,
"nothing more this tick", when it was not, and the next tick tries again.

**Don't.** Block on the lock inside the claim, or draw from the pool without it because the pool looks free.

## Known debt

Stated so a reviewer need not re-derive them:

- **The residual per-tenant lock.** One in-process `threading.Lock` per tenant — `cycle_lock`, built with the tenant's
  stores in `hub/composition.py`'s `build_tenant_stores` — stands where a row lock does not reach; dependencies never
  cross tenants, so one tenant's lock never waits on another's. Each `import threading` it needs carries this rule's
  `ast-grep-ignore`. Moving any of its holders onto a store-level row needs a schema migration. Its holders:
  - `DependencyService.declare` and `GroupService.group` — for the tenant-wide standing-dependency cycle check
    (`hub:no-standing-dependency-cycle`), which reasons over the tenant's whole graph: two disjoint writers racing on
    different rows can still together close a cycle neither alone would.
  - `DeleteService.delete`, for its whole transaction — the deleted chunk's row lock does not reach the other end of an
    outgoing edge the delete releases, so a concurrent fold of that other chunk, locking only its own survivor and merge
    ids, could otherwise remint the edge with the deleted chunk as its dependent.
  - `DependencyService.release` — as its only lock. Without a row lock for cycle safety (Scope above), release is
    ordered against `group`'s edge rewrite by this lock alone, which keeps a fold from reminting an edge released
    between the fold's read of the standing set and its write.
- **The export's pass lock.** `EgressSweep.sweep` and `EgressReset.reset` share one hub-wide in-process lock, built in
  `hub/composition.py`, which keeps an operator's cursor move from being overwritten by the advanced cursor a pass in
  flight appends. `egress_cursor` holds no row known to exist to lock, and the sweep it serializes against is itself a
  single-process background loop.
- **Running more than one hub process.** No deployment topology stands up a second hub process against one store.
- **Single-process components outside this rule.** Each is single-process by construction, and this rule governs none of
  them:
  - **The event broker** — an in-memory subscriber fan-out.
  - **Background sweeps** — loops with no cross-process coordination.
  - **Migrate-on-boot** — a migration run assumed uncontended at boot.
  - **The open-tenant set and the tenant cache** — the open tenants with their names, and each opened tenant's stores
    and services, held in memory (`hub/open_tenants.py`, `TenantCache` in `hub/composition.py`). A tenant another
    process created is read on the first lookup that misses it, but a rename refreshes only the process that made it.
  - **The boot recovery of open turns** — an open turn at startup is taken to belong to a dead process's run and is
    ended `interrupted` before the hub serves ([../crash-correctness/hub.md](../crash-correctness/hub.md) §The boot
    recovery of open turns).
  - **The flow driver's sweep of open turns** — each tick ends `interrupted` every open turn that started before the
    previous tick began and whose task is not in the driver's in-memory set of running turns; a turn another process is
    running would be in no set this process holds.

## See also

- [../crash-correctness/hub.md](../crash-correctness/hub.md) — whether a write this rule's locks wrap has a crash
  window, which no lock here decides.
- [../repository-access.md](../repository-access.md) — `bzh:unit-of-work` and `bzh:transaction-graduation`, the domain
  seam for composing repository writes and declaring their locks.
- [../../standards/persistence.md](../../standards/persistence.md) — `bzh:sql-portable`, which this rule's locked
  statement is itself held to.
- [../crash-correctness.md](../crash-correctness.md) — `bzh:invariant-checker`'s `hub:one-live-route-per-chunk`, the
  durable invariant this rule keeps true once more than one hub process shares a store.
