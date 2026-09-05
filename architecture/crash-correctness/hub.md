# Crash-correctness exemptions — hub writes (`bzh:crash-exemptions-hub`)

This register records, for each of the hub's own durable writes outside the transcript lane, which of the two grounds
[`../crash-correctness.md`](../crash-correctness.md) admits — no window at all, or a real window whose whole loss is
accepted and named — exempts it from `bzh:crash-point-registry`, and what stands in for a sweep point instead. That file
owns the registry, the invariant checker, and the obligation to record a decision here; a hub write inside the
transcript lane is recorded in [`./transcripts.md`](./transcripts.md) instead.

## Promote, then tail-stamp

`PromoteService.promote` (`blizzard/src/blizzard/hub/domain/promote.py`) records the `chunk_promoted.promoted_at` fact
through `record_promote` and then, as a second write, an explicit `queue_positions` tail-position fact through
`record_queue_position`, stamping the newly-ready chunk past every currently-ready chunk.

A crash between those two writes leaves the chunk promoted with no explicit queue position, which is exactly the gap
`QueueService._effective_position`'s (`blizzard/src/blizzard/hub/domain/queue.py`) fallback covers: an un-positioned
chunk sorts by its `chunk_promoted.promoted_at`, a real-world timestamp always far larger than any small
explicit-position float assigned to another chunk, so it still reaches the tail of the ready queue and the window
degrades rather than breaks.

## The close-intent drain sweep

`CloseIntentDrainer.sweep()` (`blizzard/src/blizzard/hub/domain/work_closure.py`) retires pending `close_intents` rows a
landing or completion transaction enqueued. Its two windows are both registered: `close.after-enqueue.before-drain` (a
landing marker and its intents are durable; no drain has run yet) and `close.after-close.before-record` (a close attempt
returned; the outcome-and-retirement write has not landed yet), swept by one dedicated scenario driving the built-in
`hub` work source with no forge (`tests/crash/test_kill9_sweep.py::test_kill9_at_close_crash_point`).

Every `enqueue_close_intents` call site (`blizzard/src/blizzard/hub/store/internal/chunk_rows.py`) rides its own
caller's transaction, so none has a window of its own — each leaves its intents durable together with the fact that
enqueued them. The callers are:

- a landing-marker artifact write, in whichever store records it;
- the `delivery_repo_landed` write, on the hub node's landing step;
- the `delivery_landed` write and the `finalize_delivery` terminal transition — seam methods no live path calls, so a
  chunk reaches the terminal without either enqueuing anything;
- an operator's hand-completion.

The only span open past any of them is the window between that commit and the drain, which
`close.after-enqueue.before-drain` arms — once, on the marker path, rather than once per enqueuing caller, because every
caller opens the identical span.

Within one intent's own attempt, past `close.after-close.before-record`, one transaction — `record_work_item_closure` —
writes the outcome fact and, for a `closed`/`gone` outcome, retires the intent together; a second, separate write
follows for the outcome's dedupe-gated `event_log` row. Folding the outcome and the retirement into one transaction is
what keeps a second dangerous window closed here: written separately, a crash between them could leave the intent
transiently pending against an already-terminal ref, the exact shape `hub:no-pending-intent-against-terminal-ref` flags
— and the armed crash point is checked for invariants immediately after the kill, before any recovery pass runs, so that
shape would be a guaranteed trip, not a rare race. A crash before the folded transaction commits loses nothing (the
closer's own contract is idempotent, so the next pass's re-attempt is a clean no-op); a crash after it, before the event
write, loses only the informational, append-only event, never the fact or the retirement.

Per-ref close-once is `record_work_item_closure`'s own store-level uniqueness constraint on
`(chunk_id, source, ref, outcome)`, mirroring `record_hub_artifact`'s own idempotent-bool contract; retirement rides the
same transaction, so it carries no separate once-only claim of its own. `hub:no-double-terminal-closure` and
`hub:no-pending-intent-against-terminal-ref` are both legal-history invariants, not accepted false positives: the first
catches a broken idempotency guard letting a ref carry both `closed` and `gone`, the second a stuck retirement past the
point the folded transaction ever leaves one standing alone.

## The marker-write capability token

`MarkerAuthority` (`blizzard/src/blizzard/hub/delivery/marker_auth.py`) mints an in-memory, process-scoped token per
`(chunk_id, node_id, epoch)` immediately before that hub-node step's `run:` commands execute and revokes it in a
`finally` once the step's visit is done with it — never persisted, yet gating a marker write that is itself durable.

A crash mid-step orphans the land script the step spawned, leaving it holding a token minted by a process that no longer
exists, so its later marker-write POSTs fail against the restarted process's fresh, empty authority. That rejection is
safe rather than a gap: the executor's at-least-once-per-step contract (`bzh:hub-node-step-idempotence`,
[`../../standards/hub-nodes/step-idempotence.md`](../../standards/hub-nodes/step-idempotence.md)) re-runs that exact
step from its own first command on the next hub-advance, minting a fresh token and re-recording the marker idempotently,
and no crash-sweep assertion depends on an orphan's rejected write landing.

The token needs neither mechanism because it is in-memory, credential-shaped state with no durable form and no
partial-write window of its own.

## The item-creation chunk mint

`POST /api/work-sources/hub/items` writes the item's `work_items` row and its resting `not_ready` chunk's rows —
`chunks` plus `chunk_work_refs` — together, a pairing spanning two tables `ChunkRecordStore` and `ChunkWorkRefsStore`
otherwise split between them. Both of those inserts run on the same connection inside one `engine.begin()` in
`WorkItemStore.create_with_chunk` (`blizzard/src/blizzard/hub/store/internal/work_item_store.py`), through one
repository adapter, which reaches into the shared `insert_chunk_rows`
(`blizzard/src/blizzard/hub/store/internal/chunk_rows.py`) free function rather than through the chunk-seam adapters'
own write methods. That seam bypass is deliberate rather than a layering gap: it is what lets a single caller open one
transaction over both tables at all.

One narrower window is named and accepted here: `WorkItemEditService.create` allocates the item's `ref` through
`WorkItemStore.allocate_ref` before that transaction opens, under the allocator's own already-accepted gap-tolerant
contract, so a crash in between burns that one `ref`, never reused — the same price a bare `allocate_ref` call already
pays with no chunk attached.

The pairing owes the checker nothing because it is a single-transaction insert, not a derived cross-fact invariant to
recompute.

## The routine-run mint

`POST /api/routines/{routine_id}/run` writes the run item's `work_items` row, its resting chunk's rows — `chunks` plus
one `chunk_work_refs` row per work ref — the promote-then-tail-stamp pair (`chunk_promoted` plus `queue_positions`), and
the run's own identity row (`work_item_runs`), together: five inserts spanning six tables `WorkItemStore`/the chunk-seam
adapters/`RunContextStore` otherwise own across three repositories. All five run on the same connection inside one
`engine.begin()` in `WorkItemStore.create_with_chunk_and_promote`
(`blizzard/src/blizzard/hub/store/internal/work_item_store.py`), reusing the shared free functions `insert_chunk_rows`
and `insert_promote_rows` (`blizzard/src/blizzard/hub/store/internal/chunk_rows.py`) and `insert_run_context_row`
(`blizzard/src/blizzard/hub/store/internal/run_context_store.py`) — the same seam-bypass shape §The item-creation chunk
mint already takes, widened from one table to three: what lets a single caller open one transaction over all six at
once. `work_item_runs` is what garden delivery's own read (`blizzard/src/blizzard/hub/domain/run_context.py`) resolves a
chunk's run identity through; landing it outside this transaction would reopen exactly the window this section exists to
close.

The tail position itself is computed before the write, by the same rule `PromoteService.promote` stamps by
(`tail_position`, `blizzard/src/blizzard/hub/domain/promote.py`) — the already-accepted check-then-act shape §Promote,
then tail-stamp names, widened to a second caller rather than copied.

Two narrower windows are named and accepted here. `RunService.run` (`blizzard/src/blizzard/hub/domain/routine_run.py`)
allocates the run's `ref` through `WorkItemStore.allocate_ref` before this transaction opens, identical in shape to §The
item-creation chunk mint's own: under the allocator's own already-accepted gap-tolerant contract, a crash in between
burns that one `ref`, never reused. It also resolves the run's effective scope through `ScopeRegistry.ensure`
(`blizzard/src/blizzard/hub/domain/scopes.py`) before the same transaction opens, its own separate write when the slug
is unseen; a crash between that mint and this transaction leaves an idempotently-minted scope with no run against it —
mint-on-name means the next attempt at the same name reuses it rather than re-minting, so nothing is burned, only a
retry owed.

The composite owes the checker nothing because it is a single-transaction insert, not a derived cross-fact invariant to
recompute.

## Chunk delete, then hub-item withdrawal

`WorkItemStore.delete_chunk_and_withdraw_hub_items` (`blizzard/src/blizzard/hub/store/internal/work_item_store.py`)
writes the chunk's `chunk_deleted` row and closes every open `hub:`-source item it holds as withdrawn, both on one
`engine.begin()` connection — the same single-transaction shape `create_with_chunk` above uses for its own pairing. The
`chunk_deleted` insert runs through `record_deleted_row` (`blizzard/src/blizzard/hub/store/internal/chunk_rows.py`), a
free function shared the same way `insert_chunk_rows` is for the mint side; the `work_items` closures reuse
`WorkItemStore._close_conn`, the same connection-scoped update `close` itself calls. A `forge:`-sourced pointer on the
same chunk is left untouched — only `hub:`-source items close.

`DeleteService.delete` (`blizzard/src/blizzard/hub/domain/delete.py`) reaches this write from both a direct chunk delete
and `WorkItemEditService.withdraw`'s own cascade into an unacquired holder, always inside the same `threading.Lock`
`ClaimService`/`EditService`/`RestartService` share (`blizzard/src/blizzard/hub/composition.py`) — the guard-check and
the composite write happen under one held lock, so a claim cannot land on a chunk this write is mid-way through
deleting. That lock closes a same-process concurrency race, not a crash window: the call sequence it guards only reads —
`load_facts` and `list_standing_edges()` — before acting, with no write of its own ahead of the one atomic transaction —
unlike `create_with_chunk`'s own sibling gap, `allocate_ref` running in its own transaction before the insert it feeds,
there is no narrower window here to name and accept.

The same transaction also releases the deleted chunk's own standing outgoing dependency edges, via
`release_outgoing_edges_conn` (`blizzard/src/blizzard/hub/store/internal/chunk_dependencies_store.py`) called on the
same `conn` right after `record_deleted_row` — still inside the one `engine.begin()`, so a deleted dependent's own edges
never survive it.

The pairing owes the checker nothing because it is a single-transaction insert-plus-update(s), not a derived cross-fact
invariant to recompute.

## Proposed work items, riding the completion's own write

A node-step's proposed work items (`work_item_proposals`) ride whichever write already carries its artifacts:
`ChunkMovementStore.record_transition`/`record_migration`
(`blizzard/src/blizzard/hub/store/internal/chunk_movement_store.py`) and `ChunkDecisionsStore.record_decision`
(`blizzard/src/blizzard/hub/store/internal/chunk_decisions_store.py`) each take the step's proposal rows on the same
connection, inside the same `engine.begin()`, as the transition, migration, or decision fact they accompany. Only the
proposal insert runs through a shared `insert_proposals` helper
(`blizzard/src/blizzard/hub/store/internal/chunk_rows.py`) — each write's own `ArtifactRow`s stay their own separate
inline loop. A crash before that commit loses the whole write, proposals included, exactly as it already loses the fact
and its artifacts; a crash after it has nothing left to lose. A consumer reads these rows — the delivery-materialization
sweep below — but only once the chunk delivers, well after this write's own transaction has closed one way or the other,
so that consumer changes nothing about this write's own correctness.

The write owes the checker nothing because it is a single-transaction insert, not a derived cross-fact invariant to
recompute.

## A gate resolution's strike, riding the resolution's own write

`ChunkDecisionsStore.record_decision_resolution` (`blizzard/src/blizzard/hub/store/internal/chunk_decisions_store.py`)
inserts each struck proposal's `work_item_strikes` row on the same connection, inside the same `engine.begin()`, as the
`decision_resolutions` row it accompanies — the same one-transaction shape §Proposed work items above takes for a step's
own proposals. A crash before that commit loses the whole write, strikes included, exactly as it already loses the
resolution; a crash after it has nothing left to lose. The delivery-materialization sweep below reads
`work_item_strikes` to exclude a struck proposal forever, but only once the chunk delivers, well after this write's own
transaction has closed one way or the other, so that read changes nothing about this write's own correctness.

The write owes the checker nothing because it is a single-transaction insert, not a derived cross-fact invariant to
recompute.

## The delivery-materialization sweep

`WorkItemMaterializationReconciler.sweep` (`blizzard/src/blizzard/hub/domain/work_item_materialization.py`) re-derives
its candidate set — every not-yet-judged proposal of a chunk that has delivered
([`../../domain/work/chunk.md`](../../domain/work/chunk.md) §Materialization) — from the store on every pass and holds
no state between passes: no durable outbox of its own, unlike the close-intent drain above. A crash mid-pass loses only
that pass's remaining work; the next pass re-reads the same candidate set minus whatever the crashed pass already
committed, and converges the same way a re-run always would. No new dangerous window opens, so this sweep earns no
`bzh:crash-point-registry` entry of its own.

Its two write paths are each a single atomic transaction, not a read-then-write pair a crash could split:

- **Mint.** `WorkItemStore.materialize_create` inserts the proposal's `work_item_materializations` outcome row, the
  item's `work_items` row, and its resting `not_ready` chunk's rows, all on one `engine.begin()` connection — the same
  shape §The item-creation chunk mint's `create_with_chunk` uses, plus the outcome row folded into the same transaction.
  It inherits that section's one named gap unchanged: `allocate_ref` still runs in its own transaction before this one
  opens, so a crash in between still burns one `ref`, never reused.
- **Append.** `WorkItemStore.materialize_update` appends the proposal's evidence to the item's body, stamps `edited_at`,
  and inserts the outcome row, all on one `engine.begin()` connection, reaching `work_items`' own update and
  `work_item_materializations`' insert through one repository adapter — the same seam bypass §The item-creation chunk
  mint and §Chunk delete, then hub-item withdrawal both name as deliberate, not a layering gap, since it is what lets a
  single caller open one transaction over both. The append itself is one SQL-level concatenation (`body || evidence`)
  rather than a read-then-write pair, so there is no gap between reading the old body and writing the new one for a
  crash, or a concurrent editor, to land inside.

Each composite's own idempotency guard — checking the outcome row's existence before minting or appending — is what
makes a replayed sweep write nothing a second time; a crash after either transaction commits leaves the proposal already
judged, and the next pass's candidate read excludes it.

Both write paths owe the checker nothing because each is a single-transaction insert (plus, for the append, one update),
not a derived cross-fact invariant to recompute.

## Garden delivery, marker folded into its own transaction

`GardenDeliveryStore.deliver` (`blizzard/src/blizzard/hub/store/internal/garden_delivery_store.py`) writes a garden
run's whole delta in one `store.write("deliver")` transaction: the run's new `findings`, `finding_facts`,
`finding_sets`, `garden_proposals`, and `garden_proposal_findings` rows, plus the delivery's own `garden-delivered`
marker artifact row, all on the same connection — five candidate tables and the marker land together or not at all.

Unlike most of this register's writes, the marker here is not the executor's own after-the-fact `produces:` bookkeeping
— it is checked for existence and, if absent, inserted as this same transaction's last statement. That is what makes a
replay safe on either side of the commit: a crash before commit loses the whole write, findings and marker alike, with
nothing yet durable for a re-run to collide with; a crash after commit leaves the marker already present, so the next
`garden_deliver.py` POST (`bzh:hub-node-step-idempotence`,
[`../../standards/hub-nodes/step-idempotence.md`](../../standards/hub-nodes/step-idempotence.md)) finds it on its own
idempotence check and returns `recorded` having minted nothing a second time.

The window this leaves is between `deliver`'s own commit and the hub-node executor's separate step-completion
bookkeeping — already `hubnode.after-step.before-marker` in `bzh:crash-point-registry`, and already covered: the next
hub-advance re-runs the step from its own first command, and the in-transaction marker's own idempotence is what absorbs
that re-run, so this write opens no window `hubnode.after-step.before-marker` doesn't already name.

The write owes the checker nothing because it is a single-transaction, multi-table insert, not a derived cross-fact
invariant to recompute — and, unlike most of this register's writes, whose idempotence marker rides the executor's own
after-the-fact bookkeeping, this one's marker is folded into its own transaction, which is what gives its replay
idempotence in the first place.

## Garden proposal closure: pass, and accept-with-mint

`GardenProposalClosureStore.record_pass`/`record_accept_decline`
(`blizzard/src/blizzard/hub/store/internal/garden_proposal_closure_store.py`) each write one `garden_proposal_closures`
row in its own `store.write` transaction, checking the proposal's existing closure first as its own idempotence guard —
the same shape §The delivery-materialization sweep's outcome-row check uses. A crash before commit loses the whole
write, with nothing yet durable for a retried close to collide with; a crash after it leaves the closure already
recorded, and a re-attempted close reads it back through `get` and refuses as already-closed, exactly as a live race
would.

The accept-with-mint path is a second writer of the same table: `WorkItemStore.accept_create`
(`blizzard/src/blizzard/hub/store/internal/work_item_store.py`) writes the accepted-and-minted
`garden_proposal_closures` row, the item's `work_items` row, and its resting `not_ready` chunk's rows, all on one
`engine.begin()` connection — the same shape §The delivery-materialization sweep's mint path uses, plus the closure row
in place of the materialization outcome row, reaching `insert_garden_proposal_closure_row` the same way that mint path
reaches `insert_materialization_row`. The closure row is checked and inserted first, so an already-closed proposal mints
nothing. It inherits §The item-creation chunk mint's one named gap unchanged: `prepare_mint`'s `allocate_ref` still runs
in its own transaction before this one opens, so a crash in between still burns one `ref`, never reused.

Two adapters writing one table is deliberate, not a layering gap: only the item's own adapter can enclose the item and
chunk inserts in the accept-with-mint transaction, so that path could never fold into `GardenProposalClosureStore`
alone.

Both write paths owe the checker nothing because each is a single-transaction insert (plus, for accept-with-mint, the
item and chunk inserts), not a derived cross-fact invariant to recompute.

## Dependency edge declare and release

`ChunkDependenciesStore.declare`/`.release` (`blizzard/src/blizzard/hub/store/internal/chunk_dependencies_store.py`)
each write `chunk_dependencies` in one `store.write` transaction — `declare` a single insert of the fresh edge row,
`release` a read of the standing row followed by its `released_at`/`released_by` update on the same connection, inside
the one transaction. Neither has a partial-write span for a crash to land inside: `declare`'s insert either lands whole
or not at all, and `release`'s read-then-write has nothing outside the transaction observing the read before the write
commits.

`DependencyService` (`blizzard/src/blizzard/hub/domain/dependencies.py`) holds both writes under the same
`threading.Lock` `ClaimService`/`EditService`/`RestartService` share (`blizzard/src/blizzard/hub/composition.py`) — the
same concurrency guard §Chunk delete, then hub-item withdrawal already takes for its own composite write, not a
crash-window mechanism: it serializes two racing declarations, a declaration racing a release, or a declaration racing
`DeleteService.delete`'s own hold of the same lock (the prerequisite deleted between the caller's resolve and
`declare`'s hold of the lock). `declare`'s own under-lock read of the dependent's re-derived status runs before its one
atomic transaction, the same shape §Chunk delete, then hub-item withdrawal states for its own guard-check-then-write,
rather than protecting against a crash mid-transaction. The prerequisite's re-derived ephemerality read is closed the
same way: `GroupService` (`blizzard/src/blizzard/hub/domain/queue.py`) holds the same shared lock for its whole fold, so
`declare`'s ephemerality read is serialized against every writer that can make a prerequisite ephemeral, grouping
included. `NoStandingDependencyOntoEphemeralChunk` (`hub:no-standing-dependency-onto-ephemeral-chunk`) is a
`bzh:invariant-checker` assertion as a backstop against a regression in that serialization, not a guard against a live
gap.

Neither `declare` nor `release` earns a `bzh:crash-point-registry` entry — the "no window at all" ground: `declare`'s
insert and `release`'s read-then-write are each whole inside their own single transaction. `declare` alone introduces
two derived cross-fact invariants the engine enforces no constraint behind: a standing edge could close a cycle in the
dependency graph, or duplicate an already-standing ordered pair, with no schema-level constraint stopping either — so it
earns two new `bzh:invariant-checker` assertions: `NoStandingDependencyCycle` (`hub:no-standing-dependency-cycle`) and
`NoDuplicateStandingDependency` (`hub:no-duplicate-standing-dependency`), `blizzard/src/blizzard/tools/invariants.py`.
`release` only sets `released_at`/`released_by` on an already-standing row, inside that same single transaction: it can
only shrink the standing set and can never close a cycle, so it introduces no derived invariant of its own.

### A fold's edge rewrite, riding its own `chunk_grouped` write

`ChunkDependenciesStore.record_fold` (`blizzard/src/blizzard/hub/store/internal/chunk_dependencies_store.py`) takes
every target a fold carries and records each one's `chunk_grouped` row — via `record_grouped_row_conn`
(`blizzard/src/blizzard/hub/store/internal/chunk_rows.py`) — plus its own release/mint edge rewrite, all targets on one
connection inside one `engine.begin()`, the same shape `WorkItemStore.delete_chunk_and_withdraw_hub_items` reaches for
its own delete-plus-withdrawal pairing above. `GroupService.group` (`blizzard/src/blizzard/hub/domain/queue.py`) calls
it exactly once per fold, covering every target the fold carries in that one transaction, so no target's `chunk_grouped`
row can ever commit ahead of a sibling target's own edge release/mint — the condition
`hub:no-standing-dependency-onto-ephemeral-chunk` forbids: a standing edge naming an already-grouped-away chunk. It
earns no `bzh:crash-point-registry` entry on the "no window at all" ground: there is nothing left for a crash to land
partway through, across the whole fold. `add_work_refs` stays its own separate write ahead of the fold's one dependency
transaction, per target. A crash inside that narrower window leaves some targets' work refs unmerged and none of them
grouped yet; re-running the fold against the survivor converges rather than compounds, since the edge-rewrite's own
duplicate-detection treats a pair already resulting as nothing further to mint, so replaying an interrupted fold cannot
double-mint an edge it already carried.

## Delivery-triggered finding resolution, riding the close-intent drain

`HubWorkSource.close` (`blizzard/src/blizzard/hub/work_sources/internal/hub_work_source.py`) is `IWorkCloser`'s own
hub-native implementation, reached by §The close-intent drain sweep the same way any other closer is:
`WorkItemEditService.deliver` writes the item's `closed_at`/`closure` first, then, as a second write,
`GardenProposalDeliveryResolution.resolve_for_item` appends the accepted proposal's `resolved` `finding_facts` rows, if
the delivered item minted from one.

A crash between those two writes leaves the item delivered with its proposal's findings still live — not a gap, the same
shape §The close-intent drain sweep's own `close.after-close.before-record` window already covers: the intent's own
retirement fact has not landed either, so the sweep retries `close` for the same ref, `deliver` replays as the store's
own `closed_at IS NULL` no-op, and `resolve_for_item` runs again. Its own gate is `has_resolution_for_proposal` (a
`finding_facts` row already carrying the proposal's id), not any one finding's current state, so that retry completes an
interrupted resolution exactly once and a finding a person reopens afterward is never silently re-resolved by a later,
unrelated repeat of the same close.
