# Crash-correctness exemptions — hub writes (`bzh:crash-exemptions-hub`)

This register records, for each of the hub's own durable writes outside the transcript lane, which of the two grounds
[`../crash-correctness.md`](../crash-correctness.md) admits — no window at all, or a real window whose whole loss is
accepted and named — exempts it from `bzh:crash-point-registry`, and what stands in for a sweep point instead. That file
owns the registry, the invariant checker, and the obligation to record a decision here; a hub write inside the
transcript lane is recorded in [`./transcripts.md`](./transcripts.md) instead.

## Promote or demote, then stamp the position

`PromoteService.promote` (`blizzard/src/blizzard/hub/domain/operations/promote.py`) calls
`ChunkQueueStore.record_promote_with_position_locked` (`blizzard/src/blizzard/hub/store/internal/chunk_queue_store.py`),
which inserts the `chunk_promoted.promoted_at` fact and an explicit `queue_positions` fact — the queue tail, or the slot
after a named anchor — in one write transaction (`insert_promote_rows`,
`blizzard/src/blizzard/hub/store/internal/chunk_rows.py`). `DemoteService.demote`
(`blizzard/src/blizzard/hub/domain/operations/demote.py`) is the same shape through `record_demote_with_position_locked`
and `insert_demote_rows`: the `chunk_demoted.demoted_at` fact and an explicit backlog position. No window: a crash ahead
of either transaction's commit loses both facts together, and a retry re-derives the same landing from a fresh read.
`queue_positions` is shared by both lists and newest-wins, so a demote that landed its fact without its position would
leave the chunk ranked by its stale ready-queue position.

`QueueRanking.effective_position`'s (`blizzard/src/blizzard/hub/domain/operations/queue.py`) fallback — an un-positioned
chunk sorts by its `chunk_promoted.promoted_at`, a real-world timestamp always far larger than any small
explicit-position float assigned to another chunk — guards a chunk promoted with no queue position by some other route,
not a crash inside this one transaction.

## The close-intent drain sweep

`CloseIntentDrainer.sweep()` (`blizzard/src/blizzard/hub/domain/work_items/closure.py`) retires pending `close_intents`
rows a landing or completion transaction enqueued. Its two windows are both registered:
`close.after-enqueue.before-drain` (a landing marker and its intents are durable; no drain has run yet) and
`close.after-close.before-record` (a close attempt returned; the outcome-and-retirement write has not landed yet), swept
by one dedicated scenario driving the built-in `hub` work source with no forge (`tests/crash/test_kill9_sweep.py`).

Every `enqueue_close_intents` call site (`blizzard/src/blizzard/hub/store/internal/chunk_rows.py`) rides its own
caller's transaction, so none has a window of its own — each leaves its intents durable together with the fact that
enqueued them. The callers are:

- a landing-marker artifact write, in whichever store records it;
- the `delivery_repo_landed` write, on the hub node's landing step and in a hub action's landing record;
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
closer's own contract is idempotent, so the next pass's re-attempt is a clean no-op — the GitHub closer's trace comment
is deduped by a hidden per-chunk marker read before posting, so a re-attempt after a posted comment, a failed close, or
a crash here never double-posts); a crash after it, before the event write, loses only the informational, append-only
event, never the fact or the retirement.

The sweep's per-intent backoff (`close_intent_attempts`) opens no window of its own. A `failed` outcome's attempt row
rides `record_work_item_closure`'s own transaction above — the same one that writes the outcome fact — so it is exactly
as durable as that fact and never separately lost. A `skipped` attempt (no closer bound for the ref's source) has no
outcome fact and no retirement to fold alongside, so `record_close_attempt_skipped` is its own single-statement
transaction; a crash before it commits loses nothing durable (the intent was already pending and stays pending), and
there is nothing after it to lose. Either way the ledger is append-only (`bzh:facts-not-status`): a crash mid-sweep
leaves some intents' backoff clocks ticked and others not, and the next pass reads each one's own history fresh.

Per-ref close-once is `record_work_item_closure`'s own store-level uniqueness constraint on
`(chunk_id, source, ref, outcome)`, mirroring `record_hub_artifact`'s own idempotent-bool contract; retirement rides the
same transaction, so it carries no separate once-only claim of its own. `hub:no-double-terminal-closure` and
`hub:no-pending-intent-against-terminal-ref` are both legal-history invariants, not accepted false positives: the first
catches a broken idempotency guard letting a ref carry both `closed` and `gone`, the second a stuck retirement past the
point the folded transaction ever leaves one standing alone.

## A hub action pass's effect writes

`ActionPassDriver.take` (`blizzard/src/blizzard/hub/delivery/action_pass.py`) writes each effect a pass records on the
caller's thread, one at a time, and releases it back to the action only once it is durable; each effect is one
transaction of its own, so the windows are the spans between them. Four points name them:

| Point                                    | Window                                                                                                                          |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `action.after-effect.before-write`       | The action's forge write — a merge, a pull request opened, a check re-run — is done; the effect recording it is not yet durable |
| `action.after-write.before-resume`       | An effect is durable; the action has not resumed                                                                                |
| `close.after-enqueue.before-drain`       | A landing record and its close intents are durable in one transaction; no drain has run yet                                     |
| `hubnode.after-poll.before-slot-release` | The poll-attempt fact is durable; the tenant's slot is not yet released                                                         |

A crash in any of them loses only the pass in flight: the next pass reads the forge and the node's markers and
converges, as it does after any crash, so an unwritten effect is written once on the re-take and a written one is
counted past. The kill-9 sweep (`tests/crash/test_kill9_sweep.py`) reaches the `action.` family through `test.sequence`
and through a two-repository `land` against the mock forge. Every landing record reaches
`close.after-enqueue.before-drain`, so the sweep opens the window between `land`'s two repositories there: killed with
the first landing durable and the second repository not yet merged, the restarted hub lands the second without merging
the first twice.

## The trace export sweep

`TraceExportSweep.sweep` (`blizzard/src/blizzard/hub/domain/observability/tracing/sweep.py`) tells closed node steps to
the configured exporter, then appends a `trace_cursor` row recording how far it told. Its one dangerous window is
registered: `trace.after-export.before-cursor` (the exporter accepted the batch; the cursor row that records it is not
yet appended), swept by one dedicated scenario against an in-test OTLP sink (`tests/crash/test_kill9_sweep.py`). A crash
there leaves the cursor unmoved, so the next pass re-reads and re-sends the same steps under the same span ids —
delivery is at-least-once, and a backend deduplicates on span id. A crash before the exporter accepts loses nothing
durable.

Its other writes are exempt:

- **Event-log rows.** The `trace-export-failed`, `trace-export-recovered`, and `trace-window-skipped` rows are
  informational, append-only, and each a single-statement write. A crash before one commits loses only that row: a lost
  failure or recovery row is recorded again on the next state change, and a lost skip row loses only the note, never the
  cursor move it describes, because the jump row follows it.
- **Jump rows.** A cursor jump — on enable after a gap or at the lag cap — is one cursor-row append with no partner
  write. A crash before it commits leaves the cursor where it was, and the next pass re-derives the same jump from a
  fresh read.
- **Idle-advance rows.** A pass that read closing facts but told nothing appends one cursor row moving past the newest
  instant it read, or to the frontier. It is a single-statement write with no partner. A crash before it commits leaves
  the cursor where it was, and the next pass re-reads the same facts and re-derives the same row.

The sweep owes no probe or floor under `bzh:probe-gated-pass`: each pass reads only the closed steps past its own cursor
— the rows it has not yet told — never a corpus it would rescan to find nothing changed.

## The forge-status annotation sweep

`AnnotationReconciler.sweep` (`blizzard/src/blizzard/hub/domain/observability/forge_status.py`) writes forge labels and
keeps a durable memory of the sources it annotates. It has no registered crash point: each effect and its record pair
has no window that loses anything.

- **Label writes on an annotating source** have no hub record. The forge's own markers are the record, and every full
  pass re-reads them, so a crash between two writes leaves a gap the next full pass closes.
- **A departure's clear before it is forgotten** replays as a no-op. A crash between them leaves the source remembered;
  the next pass re-reads its markers, clears any remainder, and then forgets it.
- **An entrant is remembered before its first label write.** A crash after the entry write leaves a remembered source
  with nothing to clear. The entry write is ordered ahead of the effects so that a crash plus the source then being
  disabled can never orphan labels no memory names.

Each tenant's probe and last-pass instant live in memory only. A restart runs a full pass, so no durable probe state is
owed under `bzh:probe-gated-pass`'s floor.

## The egress export sweep

`EgressSweep.sweep` (`blizzard/src/blizzard/hub/domain/observability/egress/sweep.py`) writes closed steps, usage, and
the events dataset's derivations and drops as immutable files, commits a manifest naming them, then appends an
`egress_cursor` row recording how far it wrote. Its two dangerous windows are registered, both swept by one dedicated
scenario against a real temporary directory (`tests/crash/test_kill9_sweep.py`):

- `egress.after-write.before-commit`: the pass's files are placed; the manifest that lists them is not.
- `egress.after-commit.before-cursor`: the files and the manifest are placed; the cursor row that records them is not.

A crash at either leaves the cursor unmoved, so the next pass re-reads the same rows and writes them again to new file
names — delivery is at-least-once, and a reader keeps the copy with the latest `exported_at`. The killed pass's files
are never opened or replaced again; a loader that reads only files a manifest names never sees the first pass's unlisted
files. The scenario asserts the re-written rows equal the killed pass's rows apart from `exported_at`, and that every
cursor row names files and a manifest that exist and agree.

The events dataset keeps the no-probe claim: it reads derivation markers and drops past its cursor through their
time-leading indexes, never a corpus it would rescan to find nothing changed.

Its other writes are exempt:

- **Event-log rows.** The `egress-write-failed`, `egress-write-recovered`, and `egress-config-rejected` rows are
  informational, append-only, and each a single-statement write. A crash before one commits loses only that row: a lost
  failure or recovery row is recorded again on the next state change, and a rejection is recorded again on the next
  start.
- **Operator reset.** `EgressReset` appends one cursor row, then records its `egress-cursor-reset` event; it holds the
  sweep's pass lock across the append, so the move is never overwritten by a pass in flight. A crash between the two
  writes keeps the move and loses only the informational event row; the cursor is a fact, and `status` shows it.
- **Anchor and idle rows.** The first pass's anchor row, and an advance that wrote no rows, are each one cursor-row
  append with no partner write. A crash before one commits leaves the cursor where it was, and the next pass derives the
  same row from a fresh read.
- **Schema widening.** When the current schema widens a dataset's existing `_schema/` document with nullable columns,
  `DirectoryEgressWriter` (`blizzard/src/blizzard/hub/egress/internal/files.py`) swaps the document whole for the wider
  one in one atomic `os.replace`, with no partner write. A crash before the swap leaves the narrower document, which the
  next pass that writes the dataset swaps again.

The sweep owes no probe or floor under `bzh:probe-gated-pass`: each pass reads only the closed steps and usage past its
own cursors — the rows it has not yet written — never a corpus it would rescan to find nothing changed.

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

## The boot release of live hub-execution slots

`HubNodeExecutor.release_orphaned_slots` runs from the hub daemon's startup, once in each open tenant before the hub
serves, and releases that tenant's live `hub_exec_slot` rows in one statement. The slot is not reentrant, so a row left
live by a `kill -9` mid-node would otherwise defer the chunk's own resume until `slot_stale_after`; at boot such a row
belongs to a run the dead process held, since one hub process serves the store
([`../system-shape/exclusive-writes.md`](../system-shape/exclusive-writes.md) §Known debt).

It has no window: the release is a single statement, and a crash before it commits leaves the same rows for the next
boot to release. Composition never calls it, so a CLI or test build over shared stores cannot release a live daemon's
slot.

## Tenant creation, one identity unit of work

`TenantAdministration.create` (`blizzard/src/blizzard/hub/domain/tenancy/administration.py`) writes a tenant's `tenants`
row, its packaged graphs, its `hub` work-ref sequence, and, when one is named, its first admin's membership, inside one
identity unit of work (`blizzard/src/blizzard/hub/auth/identity_transaction.py`). The tenant's writes join the unit's
own connection through `ScopedConnections.founding` (`blizzard/src/blizzard/hub/store/scoped.py`), which opens by
inserting the scope's `tenants` row where every other scoped write locks it, so each later write in the unit locks the
row just inserted. No window: a crash ahead of the commit loses the tenant and everything minted into it together, and
the in-memory open-tenant set is refreshed only after the commit.

## Invitation acceptance, one identity unit of work

`AuthService.accept_invitation` (`blizzard/src/blizzard/hub/auth/service.py`) resolves or creates the person, grants the
invitation's role unless they already hold a membership in its tenant, records the invitation accepted, and mints their
session, all in one identity unit of work; the tenant-owned invitation fact joins it through
`IdentityWrites.tenant_connections`. No window: a crash ahead of the commit leaves the invitation live and nothing of
the sign-in written, and a retried sign-in accepts it afresh. The claim of a configured superuser that follows is a unit
of work of its own, opened after this one commits: a crash between them leaves the target unclaimed, and the person's
next sign-in claims it.

## Tenant deletion: close, drain, complete

Deleting a tenant (`blizzard/src/blizzard/hub/domain/tenancy/teardown.py`) runs three phases, each committing on its
own: the close records the tenant's deletion fact, the drain removes the tenant's rows a bounded batch per transaction,
and the completion removes the `tenants` row and the tenant's memberships and stamps `deleted_at`. The deletion fact is
the resume marker: while it stands without `deleted_at`, the `tenant_teardown` sweep carries the drain on from wherever
the tables stand, so a crash in any of the three windows is finished after restart — after the close and before any
drain (`teardown.after-close.before-drain`), between two batches (`teardown.after-batch.before-next`), and after the
drain and before the completion (`teardown.after-drain.before-complete`). A batch and its addition to the fact's
`rows_removed` commit together, and every batch walks the tables from the top, so a re-walk neither redoes a committed
batch nor counts a row twice. The `tenant-closed` and `tenant-deleted` hub events are recorded after their phase
commits, so a crash between a phase and its event loses only that event row. The close's in-memory effects need no
recovery: a restarted hub opens only the tenants with no deletion fact.

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
one `chunk_work_refs` row per work ref — and the run's own identity row (`work_item_runs`), together: inserts spanning
four tables `WorkItemStore`/the chunk-seam adapters/`RunContextStore` otherwise own across three repositories. Every one
of them runs on the same connection inside one `engine.begin()` in `WorkItemStore.create_run_with_chunk`
(`blizzard/src/blizzard/hub/store/internal/work_item_store.py`), reusing the shared free functions `insert_chunk_rows`
(`blizzard/src/blizzard/hub/store/internal/chunk_rows.py`) and `insert_run_context_row`
(`blizzard/src/blizzard/hub/store/internal/run_context_store.py`) — the same seam-bypass shape §The item-creation chunk
mint already takes, widened from one table to three: what lets a single caller open one transaction over all four at
once. `work_item_runs` is what garden delivery's own read (`blizzard/src/blizzard/hub/domain/garden/run_context.py`)
resolves a chunk's run identity through; landing it outside this transaction would reopen exactly the window this
section exists to close.

The chunk is written with no promote fact and no queue position: it rests `not_ready` until the standalone promote.

One narrower window is named and accepted here. `RunService.run` (`blizzard/src/blizzard/hub/domain/garden/runs/run.py`)
allocates the run's `ref` through `WorkItemStore.allocate_ref` before this transaction opens, identical in shape to §The
item-creation chunk mint's own: under the allocator's own already-accepted gap-tolerant contract, a crash in between
burns that one `ref`, never reused. The run's effective scope carries no write of its own to window: the API edge
resolves it to an already-existing, already-related `Scope` — a read, refusing rather than minting one — before
`RunService.run` is ever called, so the domain layer opens no second write ahead of the transaction.

The composite owes the checker nothing because it is a single-transaction insert, not a derived cross-fact invariant to
recompute.

## Chunk delete, then hub-item withdrawal

`WorkItemStore.delete_chunk_and_withdraw_hub_items_locked`
(`blizzard/src/blizzard/hub/store/internal/work_item_store.py`) writes the chunk's `chunk_deleted` row and closes every
open `hub:`-source item it holds as withdrawn, both on the handle's already-locked connection — the same
single-transaction shape `create_with_chunk` above uses for its own pairing. The `chunk_deleted` insert runs through
`record_deleted_row` (`blizzard/src/blizzard/hub/store/internal/chunk_rows.py`), a free function shared the same way
`insert_chunk_rows` is for the mint side; the `work_items` closures reuse `WorkItemStore._close_conn`, the same
connection-scoped update `close` itself calls. A `forge:`-sourced pointer on the same chunk is left untouched — only
`hub:`-source items close.

`DeleteService.delete` (`blizzard/src/blizzard/hub/domain/operations/delete.py`) reaches this write from both a direct
chunk delete and `WorkItemEditService.withdraw`'s own cascade into an unacquired holder, always inside the same locked
transaction `ClaimService`/`EditService`/`RestartService` share (`bzh:store-exclusive-write`,
[`../system-shape/exclusive-writes.md`](../system-shape/exclusive-writes.md)) — the chunk's row lock is the
transaction's first statement, ahead of the guard reads and the composite write alike, so a claim cannot land on a chunk
this write is mid-way through deleting. That row lock closes a cross-process concurrency race — a single-writer lock the
store itself enforces, not a Python object a second hub process could ever share — not a crash window: the call sequence
it guards only reads — `handle.facts` and `handle.standing_edges()` — before acting, with no write of its own ahead of
the one atomic transaction — unlike `create_with_chunk`'s own sibling gap, `allocate_ref` running in its own transaction
before the insert it feeds, there is no narrower window here to name and accept.

The same transaction also releases the deleted chunk's own standing outgoing dependency edges, via
`release_outgoing_edges_conn` (`blizzard/src/blizzard/hub/store/internal/chunk_dependencies_store.py`) called on the
same `conn` right after `record_deleted_row` — still inside the one `engine.begin()`, so a deleted dependent's own edges
never survive it. `DeleteService.delete` also holds the residual fleet-wide lock across that transaction — like the row
lock above, a guard against a concurrent writer rather than a crash;
[`../system-shape/exclusive-writes.md`](../system-shape/exclusive-writes.md) §Known debt owns who shares it and the race
it closes.

The pairing owes the checker nothing because it is a single-transaction insert-plus-update(s), not a derived cross-fact
invariant to recompute.

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

## Review findings delivery, marker folded into its own transaction

`ReviewFindingsStore.deliver` (`blizzard/src/blizzard/hub/store/internal/review_findings_store.py`) mirrors the garden
delivery entry above: it writes a review round's whole plan — the new `findings` and `finding_facts` rows the round's
`deferred` entries mint — plus its own `review-findings-delivered` marker artifact row, all on the same
`store.write("deliver")` connection. The idempotence check (`already_delivered`, keyed on `chunk_id` alone, not
`(chunk_id, node_id, epoch)`, since a chunk owes at most one review-findings delivery) reads for the marker before
writing, exactly as garden delivery's does, giving the same before/after-commit replay safety: nothing durable on a
pre-commit crash, and the next `review_deliver.py` POST finding its own marker and minting nothing further on one after.

This entry deviates from the garden precedent on one point: a scope a `deferred` entry names that does not yet exist is
minted inside this same transaction (`domain/routines-and-scopes.md`'s own mint-on-name path for review delivery), where
garden delivery's own write instead reads the scope and refuses the whole delivery if it is missing. A crash before this
transaction commits therefore leaves neither the findings, the marker, nor any scope it would have minted — the same
all-or-nothing shape, just with one more table folded in.

The write owes the checker nothing for the same reason garden delivery's does: a single-transaction, multi-table insert
with its own in-transaction marker, not a derived cross-fact invariant to recompute.

## Garden proposal closure: pass, and accept-with-mint

`GardenProposalClosureStore.record_pass`/`record_accept_decline`
(`blizzard/src/blizzard/hub/store/internal/garden_proposal_closure_store.py`) each write one `garden_proposal_closures`
row in its own `store.write` transaction, checking the proposal's existing closure first as its own idempotence guard. A
crash before commit loses the whole write, with nothing yet durable for a retried close to collide with; a crash after
it leaves the closure already recorded, and a re-attempted close reads it back through `get` and refuses as
already-closed, exactly as a live race would.

The accept-with-mint path is a second writer of the same table: `WorkItemStore.accept_create`
(`blizzard/src/blizzard/hub/store/internal/work_item_store.py`) writes the accepted-and-minted
`garden_proposal_closures` row, the item's `work_items` row, and its resting `not_ready` chunk's rows, all on one
`engine.begin()` connection — the same shape §The item-creation chunk mint's `create_with_chunk` uses, plus the closure
row folded into the same transaction. The closure row is checked and inserted first, so an already-closed proposal mints
nothing. It inherits §The item-creation chunk mint's one named gap unchanged: `prepare_mint`'s `allocate_ref` still runs
in its own transaction before this one opens, so a crash in between still burns one `ref`, never reused.

Two adapters writing one table is deliberate, not a layering gap: only the item's own adapter can enclose the item and
chunk inserts in the accept-with-mint transaction, so that path could never fold into `GardenProposalClosureStore`
alone.

Both write paths owe the checker nothing because each is a single-transaction insert (plus, for accept-with-mint, the
item and chunk inserts), not a derived cross-fact invariant to recompute.

## Dependency edge declare and release

`ChunkDependenciesStore.declare_locked`/`.release`
(`blizzard/src/blizzard/hub/store/internal/chunk_dependencies_store.py`) each write `chunk_dependencies` in one
transaction — `declare_locked` a single insert of the fresh edge row, on the connection `IChunkExclusiveWrites.locked`
already opened and row-locked; `release` a read of the standing row followed by its `released_at`/`released_by` update
on the same connection, inside its own `store.write` transaction. Neither has a partial-write span for a crash to land
inside: `declare_locked`'s insert either lands whole or not at all, and `release`'s read-then-write has nothing outside
the transaction observing the read before the write commits.

`DependencyService` (`blizzard/src/blizzard/hub/domain/chunk/dependencies.py`) runs `declare_locked` and `release` under
locks [`../system-shape/exclusive-writes.md`](../system-shape/exclusive-writes.md) (`bzh:store-exclusive-write`) owns —
which each holds, and why. None is a crash guard. `declare_locked`'s guards wrap the same not-a-crash-window shape
§Chunk delete, then hub-item withdrawal already takes for its own composite write: its own re-derived reads — the
dependent's status, the prerequisite's ephemerality, the standing set the cycle check walks — all run before its one
atomic transaction, never protecting against a crash mid-transaction. Those same guards serialize the ephemerality read
against every writer that can make a prerequisite ephemeral, grouping included, so
`NoStandingDependencyOntoEphemeralChunk` (`hub:no-standing-dependency-onto-ephemeral-chunk`) is a
`bzh:invariant-checker` assertion as a backstop against a regression in that serialization, not a guard against a live
gap.

Neither `declare` nor `release` earns a `bzh:crash-point-registry` entry — the "no window at all" ground: `declare`'s
insert and `release`'s read-then-write are each whole inside their own single transaction. `declare` alone introduces
two derived cross-fact invariants the engine enforces no constraint behind: a standing edge could close a cycle in the
dependency graph, or duplicate an already-standing ordered pair, with no schema-level constraint stopping either — so it
earns two `bzh:invariant-checker` assertions: `NoStandingDependencyCycle` (`hub:no-standing-dependency-cycle`) and
`NoDuplicateStandingDependency` (`hub:no-duplicate-standing-dependency`), `blizzard/src/blizzard/tools/invariants.py`.
`release` only sets `released_at`/`released_by` on an already-standing row, inside that same single transaction: it adds
no standing edge, so it introduces no derived invariant of its own.

### A fold's edge rewrite, riding its own `chunk_grouped` write

`ChunkDependenciesStore.record_fold_locked` (`blizzard/src/blizzard/hub/store/internal/chunk_dependencies_store.py`)
takes every target a fold carries and records each one's `chunk_grouped` row — via `record_grouped_row_conn`
(`blizzard/src/blizzard/hub/store/internal/chunk_rows.py`) — plus its own release/mint edge rewrite, on the fold's
already-locked connection (`bzh:store-exclusive-write`). `GroupService.group`
(`blizzard/src/blizzard/hub/domain/operations/queue.py`) opens that one locked transaction for the whole fold and calls
`record_fold_locked` exactly once inside it, covering every target the fold carries, so no target's `chunk_grouped` row
can ever commit ahead of a sibling target's own edge release/mint — the condition
`hub:no-standing-dependency-onto-ephemeral-chunk` forbids: a standing edge naming an already-grouped-away chunk.
`add_work_refs_locked` runs on the same connection too, ahead of `record_fold_locked` in the same loop-then-once shape,
so the fold's work-ref merges and its edge rewrite share one transaction: no crash can leave some targets' work refs
merged with none of them grouped. The whole fold earns no `bzh:crash-point-registry` entry on the "no window at all"
ground: there is nothing for a crash to land partway through, across the whole fold, work refs included.

## Delivery-triggered finding closure, riding the close-intent drain

`HubWorkSource.close` (`blizzard/src/blizzard/hub/work_sources/internal/hub_work_source.py`) is `IWorkCloser`'s own
hub-native implementation, reached by §The close-intent drain sweep the same way any other closer is:
`WorkItemEditService.deliver` writes the item's `closed_at`/`closure` first, then, as a second write,
`GardenProposalDeliveryResolution.resolve_for_item` appends the accepted proposal's `delivered` `finding_facts` rows, if
the delivered item minted from one.

A crash between those two writes leaves the item delivered with its proposal's findings still live — not a gap, the same
shape §The close-intent drain sweep's own `close.after-close.before-record` window already covers: the intent's own
retirement fact has not landed either, so the sweep retries `close` for the same ref, `deliver` replays as the store's
own `closed_at IS NULL` no-op, and `resolve_for_item` runs again. Its own gate is `has_delivery_for_proposal` (a
`finding_facts` row already carrying the proposal's id), not any one finding's current state, so that retry completes an
interrupted closure exactly once and a finding a person reopens afterward is never silently re-closed by a later,
unrelated repeat of the same close.

## Runner fact ingest: the high-water mark, persisted per fact

`FactIngestService.ingest` (`blizzard/src/blizzard/hub/domain/execution/facts.py`) walks a runner's pushed batch in seq
order and, for each fact that applies, writes that fact's own domain row and then, as a second write, advances
`runner_high_water` to that fact's seq through `set_runner_high_water` — inside the same loop iteration, before moving
to the next fact, rather than once after the whole batch.

The span between a fact's domain write landing and its own mark-write committing is a real window, and what a crash
inside it loses is bounded to that one fact: a replay resubmits every seq the runner's own ack never confirmed, the
replayed seq reads at or below the now-stale mark as not-yet-advanced, and `_apply` runs again against a domain write
most kinds do not gate on a natural key — `usage.recorded` sums tokens with no dedupe key of its own, for one — so the
replay double-applies exactly that one fact. Persisting the mark inside the loop rather than after it is what keeps that
bound at one fact regardless of how many rode in the same batch: a crash after the third fact's mark commits, mid-way
through a ten-fact push, leaves the ninth and tenth facts simply unapplied, re-submitted and applied cleanly on the next
push, not double-applied alongside the third.

The loss is tolerable because it is bounded to the one fact already in flight when the crash lands, silent only in the
sense that no dedicated alarm names it, and recoverable by nothing more than the runner's own ordinary retry — the exact
shape a lost-ack replay already produces for every other fact kind, at the same one-fact cost. A rejected fact never
advances the mark past it and is excluded from this window, since `_apply` returning false skips the mark-write for that
seq entirely and the loop moves on to the next one.

This is a real window whose whole loss is accepted and named, not the no-window ground: each `set_runner_high_water`
call is its own transaction, so a crash can land between it and either the domain write just before it or the next
fact's domain write just after — a span that exists and can lose a bounded, non-durable amount, not a span with nothing
left to separate. The write owes the checker nothing beyond what it already carries: `runner_high_water` is a per-runner
scalar the store already treats as idempotently overwritable, not a derived cross-fact invariant to recompute.

The host's fact lane has the same window and the same accepted one-fact loss. `HostFactIngestService.ingest`
(`blizzard/src/blizzard/hub/domain/execution/host_facts.py`) writes each fact's usage row, then advances
`host_high_water` through `HostRegistryStore.set_high_water` inside the same loop iteration. A crash between the two
replays that one fact, and the replay costs nothing: a sample or miss upsert refreshes its `(host_id, slug)` row in
place, so re-applying it re-writes the row and counts nothing twice. No crash point is registered for it.

## Hosts: retire, and add with adopt

`HostRetirementService.retire` (`blizzard/src/blizzard/hub/domain/execution/host_retirement.py`) decides the refusal in
the `Host` model over every live runner's holdings before it writes, then writes in two steps. First,
`HostRegistryStore.record_retirement` appends the host's retire fact and revokes its token in one transaction, so the
host can add no runner from that instant. Second, `FleetService.retire` runs once per runner under the host.

The span between the two steps is a real window whose whole loss is accepted and named: a crash inside it leaves a host
retired with runners under it that are not. The loss is bounded to those runners staying live a while longer, and
nothing is corrupted — re-running `retire` over the retired host writes no second host fact and runs each runner's
retire again, which retires any left standing and finishes any interrupted release of their chunks, as a runner's own
re-run does. A sweep point would arm a span an operator's re-run already closes, so none is registered.

`HostEnrollmentService.add` with `--adopt` has no window. `HostRegistryStore.add` inserts the host and places every
adopted runner in one scoped write transaction, and a runner that came to stand under a host first rolls the whole write
back, so a crash or a refusal loses the host and its adoptions together.
