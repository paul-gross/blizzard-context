# Exclusive writes

This spoke owns how an "exactly one wins" decision is enforced once the hub's store, not an in-process lock, is the one
thing every writer shares; the macro-shape hub is [../system-shape.md](../system-shape.md). Every rule here follows the
slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## An exactly-one-wins decision locks its row before it reads (`bzh:store-exclusive-write`)

**Rule.** A decision the hub commits to exactly once — a claim, or any write another such decision's guard reads consult
— runs in one write transaction that acquires its decision locks before every guard read *of that row's own chunk state*
the decision rests on, on that same connection. A read that resolves a different aggregate this lock does not cover (a
graph's retirement) is not a guard read this rule governs. Claim's early runner eligibility check is only a prompt
refusal: it rechecks eligibility under the registry key before writing the route. The scoped write's tenant-row lock
comes first (`bzh:tenant-scoped-store`), except when creating the tenant by inserting that row. A decision needing
multiple locks acquires them in a consistent order shared by its competitors, before the guards each protects; an
earlier decision lock may therefore precede a later one. Each row lock must target a row known to exist; the keyed-lock
protocol below handles missing rows.

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
record's create, edit, or enable reads that its secret is not retired, so both lock the secret's own row first
(`lock_secret_row`, `hub/store/internal/secret_store.py`). A macro-shape constraint on deployment topology, on what
holds once more than one hub process may share a store — not a `kill -9` crash-correctness requirement; one hub process
already serializes every one of these correctly today. The tenant-row lock ahead of the decision's lock changes neither
guarantee: on SQLite it already took the writer lock, and on Postgres scoped writers take the tenant row before their
decision locks. That common prefix alone does not prove the subsequent locks cannot invert. Dependency **release** needs
no row lock for cycle safety: it can only shrink the standing set and can never close a cycle. Its ordering against a
fold's edge rewrite also takes the dependency-graph key; the residual per-tenant lock remains in
[Known debt](#known-debt). A create whose only race is a duplicate of a tenant-chosen name is no decision under this
rule: the table's tenant-led primary key or unique constraint (`bzh:tenant-scoped-uniqueness`) admits exactly one
insert, and the store maps the losing insert's `IntegrityError` to the named conflict — `SecretStore.create`
(`hub/store/internal/secret_store.py`) is the pattern. A create that reads state before its insert — a cap, a parent's
state, a default it mints — stays a decision under this rule, in the keyed-lock form under **Do**.

Host retirement also requires a host-row transactional fence: release, runner reinstatement, placement (including
adoption and add with adoption), and adding a runner under a host must serialize their relevant host-state checks with
retirement on that host row, on the writing connection. The roster and refusal contract are owned by
[`../crash-correctness/hub.md`](../crash-correctness/hub.md) §Hosts: retire, and add with adopt. Host live-name
uniqueness for add and report/rename requires a name decision lock; the host row cannot serialize competing new hosts.
The implementation takes `host-live-name-registry/registry` and then `host-name/registry` for add and report. The row
fence and its competitors are inventoried below, not claimed fully audited.

**Detect.**

- An in-process lock (`threading.Lock` or equivalent) in `hub/`, guarding a check-then-act sequence against another
  writer — mechanically flagged by this rule's ast-grep rule (`contracts/ast-grep/rules/store-exclusive-write.yml`),
  which flags any `import threading` under `src/blizzard/hub/**`.
- A `.with_for_update()` call under `src/blizzard/hub/**` — it renders nothing on SQLite, so the guard read holds no
  writer lock. Mechanically flagged by `contracts/ast-grep/rules/store-no-for-update.yml`.
- A protected guard read before its decision lock, a chunk or keyed row locked before its tenant row, or competing
  transactions taking shared locks in opposite orders — the latter can deadlock on Postgres. Not mechanically checkable;
  judged at review.
- A locked transaction whose row lock targets a row that may not yet exist when two writers race to create it — a no-op
  `UPDATE` locks nothing on an empty table, so the exclusion never engages. Not mechanically checkable; judged at
  review. The remedy is the keyed-lock-row form under **Do**.

**Do.** `lock_chunk_row` (`hub/store/internal/chunk_rows.py`) — a no-op `UPDATE` on the chunk's own row, already minted
before any claim, edit, or dependency write can reach it — called after the tenant-row lock `ScopedConnections.write`
(`hub/store/scoped.py`) opens with and any earlier decision keys, with protected guard reads on the same connection.
`IChunkExclusiveWrites.locked` (`hub/domain/chunk/ports/exclusive.py`) is the place this crosses the domain seam: it
locks every named chunk id in sorted order (closing cross-writer deadlock on Postgres, where two writers naming the same
set in different orders could otherwise wait on each other) before yielding `ILockedChunkRead` — a domain-facing handle
carrying no connection. A sibling write repository's own `*_locked` method takes that same handle and recovers the real
connection through `conn_of` (`hub/store/internal/chunk_rows.py`), a package-private cast only the store layer ever
calls — the domain layer never sees a `Connection`.

Two specialized chunk handles add locks before yielding that same read interface:

- `locked_queue` takes the tenant-scoped `queue-positions/queue` key, then sorted chunk rows. Promote and demote use it;
  their position and promotion writes share its connection. Direct promotion takes the same key before its chunk row;
  queue and backlog position writes take the key without chunk-row locks. Backlog rechecks promotion under the key
  before inserting. This serializes the position writers with each other, not just writers of the same chunk.
- `locked_claim` takes `dependency_graph/standing`, reads the standing edges touching the candidate on that connection,
  locks the candidate and its standing prerequisites in sorted id order, then takes `host-live-name-registry/registry`.
  Claim re-reads edges, prerequisite facts, candidate facts, route and runner registration through the handle before
  recording its route. The graph key protects the edge set used to select prerequisite locks; the prerequisite rows
  fence changes to their facts and the registry key orders eligibility against participating registry writers. This is
  distinct from `locked`, which only locks the explicitly named rows.

A decision whose race has no existing row to lock — two ingests of one pointer, two first mints of one graph name —
locks a row of `keyed_locks` instead, through `lock_keys` (`hub/store/internal/chunk_rows.py`). The table is lock-only:
it holds no state, nothing reads it as a fact, and its rows are never deleted. For each key, in sorted order, the helper
checks for the row, inserts it if absent inside a savepoint that swallows `IntegrityError`, then runs a no-op `UPDATE`
on it. The lookup precedes the key lock; it is not a decision guard. The table is keyed `(tenant_id, namespace, key)`,
the scoped insert stamping the write's tenant, so two tenants locking one graph name each lock their own row
(`bzh:tenant-scoped-uniqueness`). Each decision keys by its own namespace: a pointer by `(source, ref)` encoded
injectively, a graph by its name. The domain seam is `IChunkExclusiveWrites.locked_work_refs` and
`IWriteGraphRepository.locked_name`, each yielding a handle of its own — never an `ILockedChunkRead`, so a handle that
holds no chunk-row lock cannot satisfy a chunk-row `*_locked` write.

The runner's store has no `keyed_locks` table, and the rule's scope names the hub; the runner applies the
lock-a-row-known-to-exist form by analogy. The operator's pause and lift, and the ceiling's self-engagement, each take a
no-op `UPDATE` on their own runner's `runner_identity` row before reading the brake on that same transaction
(`runner/store/internal/pause_store.py`); a runner holding no identity row yet has no neighbour to race. This needs no
migration, which keeps a rollback to the previous wheel free of any store step.

An epoch-fenced write takes the lock-then-guard form through `fence` (`hub/store/internal/chunk_rows.py`), which the
write calls on its own connection after the lock and its replay probe and before its first insert. It reads the terminal
facts and the newest epoch there, so a stop or restart cannot land between the guard and the write.

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
  stores in `hub/composition.py`'s `build_tenant_stores` — remains alongside a dependency-graph key; dependencies never
  cross tenants, so one tenant's lock never waits on another's. Each `import threading` it needs carries this rule's
  `ast-grep-ignore`. Its coverage and whether it can be removed remain unresolved. Its holders:
  - `DependencyService.declare` and `GroupService.group` — for the tenant-wide standing-dependency cycle check
    (`hub:no-standing-dependency-cycle`), which reasons over the tenant's whole graph: two disjoint writers racing on
    different rows can still together close a cycle neither alone would.
  - `DeleteService.delete`, for its whole transaction — the deleted chunk's row lock does not reach the other end of an
    outgoing edge the delete releases, so a concurrent fold of that other chunk, locking only its own survivor and merge
    ids, could otherwise remint the edge with the deleted chunk as its dependent.
  - `DependencyService.release` — the store also takes the dependency-graph key before resolving and releasing the
    standing edge. Both locks order it against `group`'s edge rewrite; the full writer coverage remains to be proven.
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

## Lock audit

This is a partial source census, not a proof that every competing writer participates or that every lock order is safe.
It enumerates `*_locked` definitions and direct call sites under `blizzard/src/blizzard`, including runner methods
outside the hub rule. Paths below are relative to that directory. Protocol declarations and their concrete
implementations are paired; a caller is a direct textual call, not necessarily the entry point that acquires the handle.
Production changes concurrently, so recheck the census against the worktree before relying on it.

| Definition: protocol → implementation                                                                                                                          | Direct callers                                                           |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `hub/domain/chunk/ports/route.py` → `hub/store/internal/chunk_route_store.py`: `record_route_locked`                                                           | `hub/domain/execution/claim.py`                                          |
| Same files: `record_route_released_locked`                                                                                                                     | `hub/domain/execution/decisions.py`, `release.py`, `detach.py`           |
| Same files: `record_retirement_release_locked`                                                                                                                 | `hub/domain/execution/detach.py`                                         |
| Same files: `record_route_token_locked`                                                                                                                        | `hub/domain/execution/claim.py`                                          |
| `hub/domain/chunk/ports/decisions.py` → `hub/store/internal/chunk_decisions_store.py`: `record_decision_locked`                                                | `hub/domain/execution/decisions.py`, `gate_arrival.py`                   |
| `hub/domain/chunk/ports/movement.py` → `hub/store/internal/chunk_movement_store.py`: `record_transition_locked`                                                | `hub/domain/execution/apply.py`                                          |
| Same files: `record_migration_locked`                                                                                                                          | `hub/domain/execution/apply.py`, `hub/delivery/hub_node.py`              |
| Same files: `record_restart_locked`                                                                                                                            | `hub/domain/operations/restart.py`                                       |
| Same files: `record_requeue_locked`                                                                                                                            | `hub/domain/execution/decisions.py`                                      |
| `hub/domain/chunk/ports/work_refs.py` → `hub/store/internal/chunk_work_refs_store.py`: `add_work_refs_locked`                                                  | `hub/domain/operations/queue.py`                                         |
| `hub/domain/chunk/ports/record.py` → `hub/store/internal/chunk_record_store.py`: `mint_locked`                                                                 | `hub/domain/chunk/ingest.py`                                             |
| Same files: `set_graph_locked`, `set_defaults_locked`, `set_intended_migration_locked`                                                                         | `hub/domain/operations/edit.py`                                          |
| `hub/domain/chunk/ports/hub_exec.py` → `hub/store/internal/chunk_hub_exec_store.py`: `record_hub_step_transition_locked`, `record_hub_node_poll_locked`        | `hub/delivery/hub_node.py`                                               |
| `hub/domain/chunk/ports/dependencies.py` → `hub/store/internal/chunk_dependencies_store.py`: `declare_locked`                                                  | `hub/domain/chunk/dependencies.py`                                       |
| Same files: `record_fold_locked`                                                                                                                               | `hub/domain/operations/queue.py`                                         |
| `hub/domain/chunk/ports/lifecycle.py` → `hub/store/internal/chunk_lifecycle_store.py`: `record_pause_locked`, `record_stop_locked`, `record_completion_locked` | `hub/domain/operations/pause.py`, `stop.py`, `complete.py`, respectively |
| `hub/domain/chunk/ports/escalations.py` → `hub/store/internal/chunk_escalations_store.py`: `record_bounce_locked`, `record_bounce_escalation_locked`           | `hub/delivery/hub_node.py`                                               |
| `hub/domain/chunk/ports/queue.py` → `hub/store/internal/chunk_queue_store.py`: `record_promote_with_position_locked`, `record_demote_with_position_locked`     | `hub/domain/operations/promote.py`, `demote.py`, respectively            |
| `hub/domain/chunk/model.py` → `hub/store/internal/work_item_store.py`: `delete_chunk_and_withdraw_hub_items_locked`                                            | `hub/domain/operations/delete.py`                                        |
| `hub/domain/delivery/ports/flows.py` → `hub/store/internal/flow_store.py`: `end_turn_locked`                                                                   | `hub/delivery/flow_turn.py`, `hub/domain/delivery/reconcile.py`          |
| `hub/domain/graph/model.py` → `hub/store/internal/graph_store.py`: `mint_locked`                                                                               | `hub/domain/graph/authoring.py`                                          |
| `runner/throttle/pause.py` → `runner/store/internal/pause_store.py`: `local_brake_locked`, `record_local_pause_locked`                                         | `runner/throttle/pause.py`                                               |
| `runner/transfer/rows.py` → `runner/store/internal/host_ingest_store.py`: `merge_host_rows_locked`, `record_host_ingest_locked`                                | `runner/store/internal/runner_transfer_store.py`                         |
| `hub/domain/execution/claim.py`: `_claim_locked`                                                                                                               | Same file                                                                |
| `hub/domain/operations/queue.py`: `_group_locked`                                                                                                              | Same file                                                                |
| `hub/delivery/hub_node.py`: `_escalate_locked`                                                                                                                 | Same file                                                                |
| `runner/throttle/pause.py`: `_write_locked`                                                                                                                    | Same file                                                                |

The transfer methods receive a transfer transaction handle; the suffix alone does not establish a decision-row lock.
`open_graph_gate_on_arrival` in `hub/domain/execution/gate_arrival.py` receives a chunk handle from its caller rather
than acquiring one itself. Indirect call chains and runtime dispatch have not been exhaustively traced.

### Decision, competitor, and proof bindings

These are traced examples, not a complete decision or competitor inventory. Paths are relative to
`blizzard/src/blizzard`, except tests, which are relative to the blizzard repository root. A test binding identifies
what the test exercises, not a recorded passing result.

| Decision and observed competitors                                        | Lock and connection ordering                                                                                                                                                                                                                                                                                       | Evidence and remaining boundary                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dependency declare versus group, delete, release, and work-ref admission | `locked_dependency_graph` takes the tenant-scoped `dependency_graph/standing` key before sorted chunk rows; `release` takes that key before its standing-edge read and update. `locked_work_refs` takes the same key before project and pointer keys. The reads and writes through each handle use its connection. | `hub/domain/chunk/dependencies.py`, `hub/domain/operations/queue.py`, `hub/domain/operations/delete.py`, `hub/store/internal/chunk_exclusive_store.py`, and `hub/store/internal/chunk_dependencies_store.py`; `tests/postgres_locks/test_dependency_decisions.py` checks blocking and a lock-omission control for selected entry points, not all pairwise outcomes or cycle safety. |
| Flow submit, take, close, end, withdrawal, and landing                   | The traced order and identifier lookup scope are described below.                                                                                                                                                                                                                                                  | `tests/postgres_locks/test_flow_decisions.py` exercises selected lock sites and competing outcomes, not every flow writer or order.                                                                                                                                                                                                                                                 |
| Chunk route creation or retirement release versus host registry changes  | `hub/store/internal/chunk_route_store.py` takes the host-registry key on the chunk handle's connection; `record_retirement_release_locked` does likewise. The caller's chunk lock therefore precedes that key.                                                                                                     | `tests/postgres_locks/test_retirement_order.py` and `test_retirement_holdings.py` bind selected outcomes and ordering described below; complete host, runner, and route competitor coverage and the lock graph remain open.                                                                                                                                                         |
| Secret retirement versus work-source and repository referrers            | `hub/store/internal/secret_store.py`, `work_source_record_store.py`, and `repository_record_store.py` use the secret row lock on their writing connection.                                                                                                                                                         | `tests/postgres_locks/test_secret_decisions.py` binds selected lock sites and referrer outcomes described below; repository edit and enable, other lifecycle and import paths remain to be audited.                                                                                                                                                                                 |

Further dispositions for the current worktree follow. They are audit leads and proof bindings, not a claim that the
audit is complete or that the tests have run. The detailed bindings below the table refine its open questions. The
current tenant mutex can hide missing participation; a component test alone does not establish Postgres decision
independence.

| Decision and competitors                                                                            | Observed exclusion, guard connection and order                                                                                                                                                                                                                                                                                                                                                                   | Proof binding and gap                                                                                                                                                                                                                                                                                                                                                                            |
| --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Host live-name availability and retirement roster                                                   | Host add and report take registry → `host-name` key and recheck live names on that connection. Release, retirement and placement, plus runner add/reinstate paths, include host-row updates through `locked_host_token_hash`; registry-key participation also matters. The precise roster and guard coverage remain to be traced for every path.                                                                 | `test_host_lifecycle_fencing.py` targets host-row blocking, post-wait retirement rechecks and competing names; `test_host_decisions.py` and `test_retirement_order.py` cover selected outcomes. These are not a complete roster or lock-order proof.                                                                                                                                             |
| Host and runner usage/high-water updates versus retirement and competing updates                    | Host and runner external usage and misses take registry before their respective keyed locks and check retirement on that connection. Host `set_high_water` and `set_runner_high_water` each take their own key before reading and inserting or advancing the mark; neither takes a chunk or registry lock in that transaction.                                                                                   | `test_retirement_order.py` targets stale usage after retirement; `test_sweep_fence.py` targets reinstatement against a sweep. Cross-family ordering and every usage read/insert competitor remain open.                                                                                                                                                                                          |
| Current and former slug claims, releases and moves by project and configured records                | `former_slugs.py` locks sorted slug keys in a table-specific namespace on the writing connection; claim's holder read and former-slug deletion and release's replacement run on that connection. Callers must lock both old and new names before using these bodies.                                                                                                                                             | `tests/postgres_locks/test_slug_decisions.py` targets move key locking. Audit all create, rename, import and retirement callers and their earlier reads; sorted keys inside one invocation do not prove ordering across invocations or other lock families.                                                                                                                                      |
| Source link/unlink versus ingest; competing link revisions                                          | `project_link_store.py` takes the project-source-links key for source link writes; `locked_work_refs` takes dependency-graph → project-source-links → sorted pointer keys on its handle connection. Link update uses a revision conditional update; first-link duplicate maps `IntegrityError` to a revision conflict. Repository links use the constraint/CAS but not the source-link key.                      | `test_dependency_decisions.py` covers selected key sites, not every ingest/link interleaving. Verify ingest's standing-link guard is read through the locked handle and audit all direct link writers, including imports.                                                                                                                                                                        |
| Pointer ingest versus pointer additions, deletion and dependency rewrites                           | `locked_work_refs` takes tenant-scoped `dependency_graph/standing`, optional project-source-links, then sorted pointer keys; group takes that same graph key before chunk rows when moving refs. `work_item_store.py` also takes that key at its lock sites. `mint_locked` uses the work-ref handle connection. Chunk-locked `add_work_refs_locked` is a separate entrypoint whose participation must be traced. | Component behavior and `test_dependency_decisions.py` do not by themselves prove all pointer competitors; a direct-lock Postgres proof and omission control are still needed for each uncovered path.                                                                                                                                                                                            |
| Graph-name mint/default mint versus graph authoring and retirement                                  | `graph_store.py` takes a graph-name key in `locked_name`, direct `mint`, and lifecycle handling; `mint_locked` and enabled-name and any-minted handle reads use the handle connection. Lifecycle resolves the name to select its key; audit the safety of that lookup and every writer changing these facts.                                                                                                     | `test_graph_lifecycle_name_lock.py` holds the name key without tenant admission and tests retire and reinstate, including omission controls and enabled-name visibility. `test_finding_graph_writers.py` binds selected direct writers. `test_graph_default_decision.py` covers default versus mint and unretire, with and without the competing writer's lock; its boundary is described below. |
| Chunk claim, edit, stop, restart, completion, delete, group, route, promote and epoch-fenced writes | `chunk_exclusive_store.py` locks sorted chunk rows on the scoped write connection; handle methods recover it through `conn_of`. Dependency graph operations take their key before chunk rows. Standalone fenced writers take a chunk row before `fence`; identify replay probes and any guard read on a separate connection individually.                                                                        | Component tests exercise domain behavior; `test_finding_graph_writers.py` covers selected direct writers. Map every guard-changing direct writer and provide direct-lock Postgres proofs and omission controls before treating the family as independent.                                                                                                                                        |
| Close versus admitted writes, concurrent closes and teardown                                        | Close and teardown have different lock orders; their traced interaction is described below. Founding inserts a tenant rather than locking a missing row.                                                                                                                                                                                                                                                         | `tests/test_tenant_teardown.py` and `tests/postgres_locks/test_admission.py` bind existing behavior; the latter tests exclusive admission, not shared admission or the post-wait deletion snapshot. `test_tenant_teardown_completion.py` covers close versus completion in both orders for the same and different target tenants; broader lifecycle races remain open.                           |
| Duplicate-only names and first links                                                                | Tenant-led unique constraints and primary keys arbitrate inserts that have no preceding mutable guard; stores map relevant `IntegrityError` to a conflict. This disposition does not extend to slug moves, secret referrers, caps, or default minting.                                                                                                                                                           | Component conflict tests bind the public refusal; confirm each candidate's constraint and error mapping individually rather than treating all creates as constraint-only.                                                                                                                                                                                                                        |
| Config import claim across tenants                                                                  | `config_import_store.py` checks for any existing global fact on the writing connection after the tenant-scoped config-authoring lock, then inserts fixed primary key `id=1` in a savepoint. A conflicting insert rechecks for a committed fact; rollback releases the claim with the rest of the import. The fixed global key, not a tenant mutex, arbitrates competing imports.                                 | `tests/postgres_locks/test_config_import_decision.py` binds competing claims, rollback and an omission variant; the complete import writer set remains to be audited.                                                                                                                                                                                                                            |
| Config authoring versus apply, import and other authoring                                           | `config_authoring_lock.py` takes tenant-keyed `config-authoring/config` on the writing connection. Sites include config apply/import, project and position, project links, forge, secret, repository, work source, routine, scope, routine-scope and review findings stores. Several sites are conditional; inspect each branch, guard and later row/key lock before assuming participation.                     | `test_config_authoring.py` targets transaction-entry contention for selected writers. Complete competing-writer coverage, cross-family ordering and same-connection guard reads remain open.                                                                                                                                                                                                     |
| Backlog position versus promote and demote                                                          | Queue and backlog writes take `queue-positions/queue`; backlog re-reads promotion there and excludes promoted chunks. Promote and demote use `locked_queue` (key → sorted chunk rows); direct `record_promote` takes key → chunk and rechecks. Position writers do not take chunk rows.                                                                                                                          | `test_backlog_promotion.py` holds the key directly and checks queue, backlog, direct promote and `locked_queue`, each with a lock-omission control. It does not prove all service-level interleavings or every position writer.                                                                                                                                                                  |
| Claim versus dependency, prerequisite, answer and runner eligibility changes                        | `locked_claim` takes dependency-graph key → standing-edge read → sorted candidate and prerequisite rows → host registry key; claim re-reads protected admission facts on the handle connection.                                                                                                                                                                                                                  | `test_claim_lock_transaction.py` and `test_claim_dependency_race.py` bind selected dependency cases. `test_claim_answer_race.py` and `test_claim_registry_race.py` bind selected answer and eligibility cases described below; all competitors and orders remain open.                                                                                                                           |
| Resume versus chunk writers                                                                         | `PauseService.resume` uses `locked` on the chunk and appends its resume fact on that handle, sampling the clock after acquiring the lock.                                                                                                                                                                                                                                                                        | `test_chunk_resume.py` observes a same-row wait, an unrelated-row negative control, and the persisted post-wait timestamp. It has no lock-omission control and does not prove every pause/resume competitor.                                                                                                                                                                                     |
| Chunk closure versus landing and other child writes                                                 | Closure and child writers use chunk-row locking in `chunk_rows.py` and delivery stores; the order matters before inserting foreign-key children. Trace each guard and writer on its transaction connection rather than inferring coverage from a helper name.                                                                                                                                                    | `test_closure_lock.py` targets closure and enqueue blocking with omission controls, and repo and delivery landing's chunk-before-child order. Full closure competitors and lock graph remain unresolved.                                                                                                                                                                                         |
| Forge lifecycle versus configured referrers                                                         | `forge_record_store.py` uses `lock_forge_row` for forge and referrer decisions; config-authoring precedes it at applicable entry points. Verify each referrer guard and mutation shares the connection and identify import and lifecycle competitors.                                                                                                                                                            | `test_forge_referrer_decisions.py` binds selected creation and retirement outcomes described below; an exhaustive forge/referrer race and omission proof remains open.                                                                                                                                                                                                                           |

**Additional decision bindings.** These refine the boundaries in the table; they do not certify the full families. Paths
are relative to `blizzard/src/blizzard` unless they start with `tests/`.

- **Restart versus direct answer.** `RestartService` plans open questions under the chunk lock;
  `ChunkMovementStore.record_restart_locked` checks each answer on that connection and inserts a missing one inside a
  savepoint. On `IntegrityError` it rechecks for an answer and suppresses the error only if one exists, preserving other
  integrity failures. `ChunkQuestionsStore.answer_question` resolves the question's immutable chunk association on the
  write connection and locks that chunk before inserting; a missing question locks no chunk. The tenant/question primary
  key arbitrates duplicate answers, and a losing direct answer reads back the winner. In
  `tests/postgres_locks/test_restart_answer_race.py`, shared tenant admission replaces exclusive admission. The locked
  case makes direct answer wait behind restart and return the automatic answer. The direct, restart and savepoint
  omission cases deliberately omit the answer's chunk lock to exercise the answer-row CAS: the direct winner survives
  restart, and a restart insert winner makes the answer wait and return the automatic answer. Removing the savepoint
  aborts restart in the direct-winner race; an invalid question also fails without adding a restart. The test checks
  persisted answers and restart facts; it is not a service-level proof of all answer, question, restart and delivery
  interleavings.
- **Claim versus answer and registry changes.** `tests/postgres_locks/test_claim_answer_race.py` substitutes shared
  tenant admission and pauses claim after its chunk update-lock. Direct answer waits; claim sees the unanswered question
  and refuses as waiting on a human. Omitting the answer lock lets the answer commit first and claim persist a route.
  This covers that ordering, not an answer winning before claim's lock or every status writer.
  `tests/postgres_locks/test_claim_registry_race.py` holds the registry key without tenant admission and changes
  capabilities, projects, version refusal or pause by direct SQL. Claim waits before its locked registration read;
  commit causes the corresponding refusal and no route, rollback permits a route, and omitting claim's registry lock
  reads stale eligibility and permits a route. Separate wait and omission cases exercise `record_pause`,
  `record_registration` and `record_version_refusal` against a held key. These are selected synthetic winner and store
  lock-site tests, not all registry writers, reverse winner orders or a complete cross-family lock-order proof.
- **Host live names.** `tests/postgres_locks/test_host_name_decisions.py` holds the registry key directly without tenant
  admission and writes a competing rename or retirement fact. A report or add waits for the holder; after commit the
  report retains its existing name when the requested name is taken, while add can reuse the retired host's name. A
  self-name report also waits and retains its name. The omission case removes both registry and name-key calls and
  completes without waiting; it does not isolate either lock or establish all add, rename and retirement competitors.
- **Host and runner fact high-water.** `tests/postgres_locks/test_fact_high_water_concurrency.py` holds each lane's
  high-water key directly without tenant admission; the corresponding store writer waits, and completes without that key
  in the omission control. With admission bypassed on both writers, a 9 written before a competing 3 stays at 9 for
  first insert and existing-row update. Without the key, the first-insert loser blocks on the unique insert and fails
  with an integrity error; the existing-row loser blocks on the row update and overwrites 9 with 3. The test identifies
  the blocking query and checks the persisted sequence and timestamp. It covers these store calls and orderings, not all
  fact ingestion, retirement or cross-family interactions.
- **Retirement sweep generation.** `ChunkRouteStore.record_retirement_release_locked` takes the registry key after the
  chunk row, then rechecks the runner's latest retirement generation and the current route on that connection.
  `tests/postgres_locks/test_sweep_fence.py` holds the registry key without tenant admission while directly inserting
  reinstatement and a new retirement generation. The sweep store body waits and leaves the route intact after commit;
  omitting its registry lock releases the route against the stale generation. This tests a synthetic lifecycle winner
  and one runner route, not the complete sweep service, host lifecycle, or all release and lock-order competitors.
- **Resolution first-write-wins.** `DecisionService.resolve` locks the chunk, then locks and reloads the decision and
  reads chunk facts on that connection before checking resolvability and recording the resolution. Other resolutions
  through `ChunkDecisionsStore` compete for the decision row. `tests/postgres_locks/test_decision_resolution.py` holds
  that row without admission, checks blocking, omission, and a committed winner's persisted fields, and races eight
  store calls. `tests/test_open_decisions_closure.py` covers stale decision objects after stop and transition;
  `tests/postgres_locks/test_resolve_chunk_contention.py` checks those two guards after waiting on the chunk row, with
  omission controls. The latter uses a separate transaction without admission, not every lifecycle service. A missing
  decision row takes no row lock.
- **Transcript high-water.** `TranscriptSegmentStore.set_high_water` takes `transcript-high-water/<runner_id>` after
  admission, reads the mark on that connection and inserts it if absent or advances it only for a larger sequence.
  `tests/postgres_locks/test_transcript_high_water.py` holds the key without admission, shows a wait and a lock-omission
  control for the first write, and checks that a committed 9 beats the waiting 3. It does not prove all transcript
  segment admission, byte-limit, natural-key or high-water callers and their interleavings.
- **Transcript segment admission.** `TranscriptIngestService.ingest` checks retirement, then `locked_ingest` takes
  sorted incoming chunk rows → host registry → natural-key → chunk-budget → runner-budget → runner high-water →
  segment-visibility keys. It rechecks runner and host retirement under the registry key. After the natural keys, it
  reads matching existing records to include their chunk, runner and superseded IDs in the later key sets; incoming
  segment and supersedes IDs are included too. High-water, epoch owners, chunk existence, natural-key state, byte sums,
  segment writes and the high-water update use the handle's single transaction. A missing chunk has no row to lock. In
  sequence order, after lease-owner and replay checks, an absent chunk with a non-accepted natural key raises
  `TranscriptChunkMissing` inside the transaction, rolling back the whole batch. An accepted natural key can pass that
  check. Unexpected write failures also roll back the transaction. Direct segment writes take the incoming chunk row and
  the natural-key, budget and visibility keys, but do not run the service's admission guards.
  `tests/postgres_locks/test_transcript_admission_locks.py` asserts key waits and selective omission controls for
  admission and direct refresh, including old and new supersedes targets; it does not race complete ingest outcomes.
  `tests/test_transcript_ingest_service.py` asserts missing-chunk batch rollback, retry and accepted-key behavior, a
  retirement recheck, lock selection and selected competing SQLite ingests. Postgres outcome and omission proofs for
  caps, replay, retirement, chunk creation/deletion and epoch-owner competitors, including teardown, full writer
  coverage and cross-family lock order remain open.
- **Transcript event replacement versus drop.** `TranscriptEventStore.replace_segment_events` locks the tenant-scoped
  `transcript-events-segment/<segment_id>` key before deleting and replacing one extractor version's events and marker.
  `drop_segments` locks all segment keys in sorted order before reading identities and deleting every version. Both use
  their write connection, and the common segment key spans extractor versions. Segment ingest and direct segment writes
  take the same visibility keys for affected segment and supersedes IDs. Under that key replacement rechecks visibility
  and the current fingerprint; drop rechecks visibility and skips visible IDs. The versioned fingerprint includes each
  record's content digest, chunk, node, epoch, spawn generation, normalizer, harness, model, effort and rejection state.
  Tenant and hub-wide candidacy reads use the same fingerprint. The service propagates replacement refusal, re-reads
  candidacy for `remaining` when an attempted re-derive fails, and counts only IDs processed by drop.
  `tests/postgres_locks/test_transcript_event_locks.py` asserts key waits, omission controls and tenant/segment key
  independence; `tests/test_transcript_event_store.py` asserts sequential stale fingerprint and visibility outcomes.
  `tests/test_transcript_event_derivation.py` asserts context-only changes invalidate replacements and both candidacy
  reads, and failed re-derives report a remaining candidate in selected scopes. These are test assertions, not recorded
  runs or a Postgres outcome proof for ingest versus replace/drop. `EventDerivationService` reads graph pins before
  replacement; neither the fingerprint nor candidacy detects a graph-pin-only change, and the store does not revalidate
  pins under the key. Graph-pin changes, teardown and other visibility writers, stale derivation interleavings and
  complete lock ordering remain open.
- **Source links and ingest.** `IngestService.ingest` first chooses a project on separate reads, then takes
  `locked_work_refs` and repeats the chosen project's standing-source-link check through `handle.source_links` on the
  write connection before `live_holders` and `mint_locked`. `tests/postgres_locks/test_ingest_source_link_race.py` holds
  a lower-level unlink, optionally relinks, commits or rolls back, and checks the waiting ingest's persisted outcome
  with and without the ingest's source-link key. The initial project inference and hub-item project reads are outside
  that lock; the test does not prove their behavior under concurrent changes or every link/import writer.
- **Group and pointer admission.** `GroupService.group` takes the cycle mutex and `locked_dependency_graph` before
  `_group_locked`; its `add_work_refs_locked` and `record_fold_locked` use that handle's connection, so this caller
  holds the graph key before adding refs. `tests/postgres_locks/test_group_pointer_decisions.py` bypasses admission on
  both sides and pauses the group after its uncommitted fold. Ingest and authored item creation wait for it; commit
  yields a conflict naming the survivor and rollback names the target. Omitting the admission side's graph key completes
  early with the target as holder. This does not cover all direct pointer writers or reverse winner orders.
- **Epoch fencing.** `tests/postgres_locks/test_chunk_epoch_fence.py` holds a chunk row without admission, writes a stop
  or restart through a locked store body, and checks that a question writer waits and refuses terminal or stale epoch
  after commit. Omitting the question writer's chunk lock admits the question before that commit. This proves the
  selected question path, not every fenced writer, replay path, or competing service.
- **Finding facts.** `finding_store.py` locks sorted existing finding rows before re-deriving expected liveness and
  writing facts; `record_facts` includes both fact targets and expected IDs in its initial set. `moved_findings` also
  takes sorted row locks before reading summaries. `tests/postgres_locks/test_finding_graph_writers.py` holds a finding
  row without admission and checks direct fact writes, including an extra expected finding, with lock-omission controls.
  Missing rows, every guarded garden writer and cross-family ordering are not covered by that test.

**Secret and forge referrers.** `test_secret_decisions.py` holds the secret row independently of tenant admission. For
work-source create, enable and edit it observes a wait, completion with the referrer lock omitted, and refusal after a
committed retirement fact. It checks persisted records and active referrers, including the old secret after a refused
edit. Repository create has the same wait, omission and retirement-refusal checks and persisted-referrer checks. Secret
retire and enable have row-lock omission controls; replace has a wait check only. These use direct lifecycle facts for
the retirement winner, not competing retirement services, and do not prove repository edit or enable.

`test_forge_referrer_decisions.py` covers repository and work-source creation against forge retirement, bypassing tenant
and config-authoring admission for the holder. A held forge row blocks creation; omitting the referrer's forge lock lets
it finish. A committed retirement makes creation raise `ForgeUnavailable`; a committed direct referrer insertion makes
retirement raise `ForgeInUse` with that referrer. The test checks forge state, record presence and active referrers. The
winner uses a lower-level lifecycle or insert body, not two concurrent public store calls; edit, enable, import and
other interleavings remain open. Source and repository create and edit check forge before secret on the same connection;
enable does likewise when applicable.

**Retirement and holdings.** Route creation and retirement release take chunk → registry; host and runner retirement
take registry and read holdings without chunk locks in `retirement_holdings.py`. `test_retirement_order.py` observes
waits for route creation versus non-forced host and runner retirement in both winner orders: a committed route makes
retirement refuse, while a committed retirement fact makes route creation refuse. It checks route and lifecycle state,
and has registry-lock omission controls for host retirement, runner retirement, claim and runner usage. The retirement
winner inserts a lifecycle fact directly; the route path uses the connection-level body, not the claim service.

`test_retirement_holdings.py` holds a chunk transaction with an uncommitted ordinary release, completion or terminal
status for both host and runner. Non-forced retirement finishes without waiting for that chunk and refuses on committed
holdings, leaving both tokens intact. After commit, retirement succeeds and clears the target token; the terminal-status
case retains the route. The terminal fact is inserted directly. These tests do not establish every reverse lock order,
forced-retirement interleaving or competitor.

**Flow association and order.** `FlowStore.submit` inserts a submission's chunk association and its held-flow rows in
one transaction; `take_turn` inserts the turn's submission association. The production flow writes traced in
`flow_store.py` and `flow_rows.py` do not reassign these associations or a flow's resource: ending a turn updates only
its end and outcome. This is application-level immutability, not a database constraint against arbitrary updates; tenant
teardown deletes these rows. The submission helper's pre-lock lookup resolves submission → chunk, and the turn helper
resolves turn → submission before that lookup, solely to select locks, not to decide openness. After chunk →
`flow-chunk`, held flows are read to select resource keys; their association and resource must remain immutable for that
selection to be safe. Closure, open-turn and scheduling guards are read after the relevant locks. A missing lookup takes
no flow locks; later guards handle the absent record where applicable. This reasoning does not cover arbitrary SQL, all
indirect callers, or teardown interleavings independently of tenant admission.

The reconciler discovers submission candidates and resolves resources before locking the chunk, then rechecks the graph
ID, status, node and epoch under its chunk handle and submits on that transaction. `tests/test_flow_changed_frames.py`
asserts stop and restart between candidate selection and submission.
`tests/postgres_locks/test_flow_submit_reconcile.py` asserts waits behind direct stop or restart facts, no submission
after commit, and stale submission when the reconciler's chunk lock is omitted. The competing movement is direct SQL,
not the service; resource freshness, other competitors and orders remain open. In the departure pass, the reconciler
computes withdrawal before calling `close`; the store locks the submission and rechecks for an open turn.
`tests/postgres_locks/test_flow_reconcile.py` asserts a wait behind an uncommitted `take_turn`, no closure after commit,
and a closure with the submission lock omitted, bypassing tenant admission on both sides. It does not prove freshness of
the precomputed withdrawal or all departure competitors. These bindings describe assertions, not recorded test runs.
`take_turn` receives eligibility and landing terms computed before its resource locks: its locked rechecks alone do not
establish freshness of those inputs. Identify their writers and intended snapshot semantics before claiming those
decisions are independently protected.

The traced order on the writing connection is chunk row → `flow-chunk` → `flow-arrival` → sorted `flow` resource keys,
omitting arrival where not needed. Submit takes all four; submission and turn helpers omit arrival, and withdrawal
selects submissions after the chunk and flow-chunk locks before taking their resource keys. `lock_keys` sorts keys.
`tests/postgres_locks/test_flow_decisions.py` binds selected key waits with omission controls, selected competing
outcomes with tenant admission bypassed, chunk-before-flow for submit and interrupted end, shared-resource turns, and
arrival allocation across chunks. It is not a complete competitor or deadlock proof, nor a recorded test result here.

`FlowStore.end_turn_locked` first looks up the open turn's submission chunk on the handle connection and rejects it if
the handle's `locked_ids` does not contain that chunk, before calling `lock_flow_turn`; a missing or ended turn returns
without a write. This avoids acquiring a different chunk under an already-held handle. `FlowStore.record_landing` calls
`write_landing_rows`, which locks the supplied chunk before invoking its landing callback on a non-replay write. The
callback checks the submission's chunk, takes `flow-chunk`, checks held-flow identity, and takes resource keys before
the landing write; replay can return before that callback. `tests/postgres_locks/test_flow_ownership.py` exercises
replay and mismatched ownership, a concurrent landing replay with tenant admission bypassed, and a synthetic holding
deletion under the flow-chunk key with a landing lock-omission control. The synthetic deletion is not a production
competitor; it does not prove all landing versus withdrawal, close, or teardown interleavings.

`test_flow_decisions.py::test_mismatched_chunk_never_waits_for_submission_chunk` holds the submission's chunk row while
landing or locked end is called with a different chunk, with tenant admission bypassed. Both reject the mismatch without
waiting for that row; the test checks the turn remains open and no landing or closure rows were inserted. This covers
those two mismatched calls, not all ownership checks or production competitors.

**Close versus teardown.** Close scans tenant IDs then update-locks existing tenant rows in sorted order before plain
reads of deletion facts and the last-open guard; it inserts a deletion fact only if none exists. Teardown first
update-locks an existing underway deletion fact; drain can update that fact, and completion then deletes the tenant row
and updates the fact. Thus completion can wait for a tenant row held by close while holding the deletion fact, but
close's read of that existing fact is a plain read, not a conflicting row lock, and close returns without updating it.
That traced pair has no reverse wait on the fact and hence no cycle from this apparent inversion.
`tests/postgres_locks/test_tenant_teardown_completion.py` observes PostgreSQL blocking for close and completion in both
orders, against the same tenant and a different close target. Same-tenant close returns `UNDERWAY` when first and
`DELETED` when second; the different-tenant close returns `CLOSED`. All four assert completion's count, deletion fact,
and removed tenant; the different-target cases also assert that target's underway fact. This is not a complete lifecycle
or isolation proof: the post-wait admission snapshot and broader lifecycle race proofs remain open.

**Selected claim and default outcomes.** `tests/postgres_locks/test_claim_dependency_race.py` observes claim wait behind
direct SQL holding the graph key for release or the prerequisite row for completion. In both cases a commit lets the
service claim and persist a route; rollback yields `ClaimDeniedDependency` naming the prerequisite and no route. These
four cases do not test the competing release or completion services or provide a lock-omission control.

`tests/postgres_locks/test_graph_default_decision.py` pauses `ensure_default` at `resolve_default`, after its locked
guard reads, while direct mint or unretire competes. With the competing writer's name lock it observes a wait; with that
lock omitted the writer completes before the decision resumes. In both variants mint yields a distinct default and two
same-name graphs; unretire yields `DefaultGraphRetired` and one same-name graph. The test checks an enabled graph
exists, but does not assert its identity or the outcome of a writer winning before the guard reads. Other default-mint
interleavings and writer coverage remain open.

Tenant-first ordering is not a proof of cross-family order: in particular chunk → host registry, dependency graph →
chunk, and chunk → flow keys must be compared against every competitor, including helpers reached through handles. The
other pre-lock lookups and the all-tenant close scan still need reconciliation with the guard discipline above. No
inventory here establishes a complete lock graph or permission to relax admission.

`ScopedConnections.write` takes tenant admission first, which can mask decision-level contention in a same-tenant test.
`tests/postgres_locks/test_admission.py` exercises that admission; tests bypassing it or holding a decision lock
directly address a different question. `lock_keys` itself reads for key existence before inserting or updating; the flow
lookup analysis above does not establish that all other pre-lock reads are safe.

### Decision-lock sites

The following are observed lock sites, not an exhaustive inventory of all check-then-act decisions:

- `hub/store/internal/chunk_exclusive_store.py`: `locked` locks sorted chunk rows; `locked_dependency_graph` takes the
  dependency-graph key before sorted chunk rows. Declare, group, and delete use the latter. `locked_claim` takes that
  key before discovering and locking the candidate and prerequisites, then takes the host registry key. `locked_queue`
  takes the queue key before chunk rows. `locked_work_refs` takes the dependency-graph key, an optional
  project-source-links key, then work-ref keys; ingest uses that handle.
- `hub/store/internal/graph_store.py`: `locked_name`, `mint`, and lifecycle handling lock the graph-name key; graph
  authoring uses `locked_name` for its mint.
- `hub/store/internal/config_authoring_lock.py`: the config-authoring key is shared by the authoring sites listed above.
- `hub/store/internal/host_registry_store.py`: `lock_host_registry` takes the `host-live-name-registry/registry` key.
  Host add, report, adoption, release, retirement, and token rotation call it; runner registry and chunk route stores
  also call it. `locked_host_token_hash` update-locks the host row before reading its token hash; host lifecycle and
  runner registry paths also call it. Add and report additionally take `host-name/registry`.
- `hub/store/internal/flow_store.py` and `flow_rows.py`: submit locks the chunk, flow-chunk key, arrival key, and
  resource keys; close and take-turn call `lock_flow_submission`; end-turn calls `lock_flow_turn`. The submission helper
  reads the chunk id, then locks the chunk and flow-chunk and resource keys. The turn helper first resolves its
  submission.
- `hub/store/internal/host_registry_store.py`, `runner_registry_store.py`, and `chunk_route_store.py` take keyed locks
  for the high-water and external-usage writes named at their `lock_keys` calls.
- `hub/store/internal/former_slugs.py` takes keys in a namespace derived from the records table; `project_link_store.py`
  takes a project-source-links key. `work_item_store.py` and `chunk_dependencies_store.py` also take the
  dependency-graph key.
- `hub/store/internal/secret_store.py`, `work_source_record_store.py`, and `repository_record_store.py` call
  `lock_secret_row` for secret retirement and referrer decisions.
- `hub/store/internal/transcript_event_store.py` locks segment visibility keys for replace and drop;
  `transcript_segment_store.py` takes those keys along with natural-key, budget and high-water keys for locked ingest,
  and takes the applicable decision and visibility keys for direct segment writes. The unresolved decision and graph-pin
  boundaries are described above.
- `hub/store/internal/finding_store.py` locks sorted finding rows for guarded facts; direct and garden callers still
  need a complete competitor and ordering audit.
- Direct chunk-row lock calls also occur in `chunk_rows.py`, `chunk_delivery_store.py`, `chunk_artifacts_store.py`,
  `chunk_movement_store.py`, `chunk_route_store.py`, `chunk_escalations_store.py`, `chunk_hub_exec_store.py`,
  `chunk_decisions_store.py`, `chunk_questions_store.py`, `review_findings_store.py`, and `garden_delivery_store.py`,
  all under `hub/store/internal/`.
- `runner/store/internal/pause_store.py` locks the runner identity row in `locked_brakes`; `runner/throttle/pause.py`
  reads and writes the local brake through that handle. `runner/lifecycle/claim.py` uses the workspace acquisition lock
  described above.

**Incomplete.** The census excludes tests, generated or dynamically dispatched calls, and other languages. It does not
enumerate every SQL no-op update, conditional update, uniqueness constraint, advisory lock, or in-process lock, nor
prove the absence of an unprotected decision. The current dependency-graph keyed-lock sites coexist with the in-process
`cycle_lock`; their coverage and the existing debt description need reconciliation after concurrent production changes
settle. Lock-order interactions, especially between chunk, host-registry, and flow locks, need a complete
competing-writer and deadlock analysis before claiming multi-process correctness.

## See also

- [../crash-correctness/hub.md](../crash-correctness/hub.md) — whether a write this rule's locks wrap has a crash
  window, which no lock here decides.
- [../../standards/persistence.md](../../standards/persistence.md) — `bzh:sql-portable`, which this rule's locked
  statement is itself held to.
- [../crash-correctness.md](../crash-correctness.md) — `bzh:invariant-checker`'s `hub:one-live-route-per-chunk`, the
  durable invariant this rule keeps true once more than one hub process shares a store.
