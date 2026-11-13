# Crash-correctness exemptions — hub writes (`bzh:crash-exemptions-hub`)

This register records, for each of the hub's own durable writes outside the transcript lane, which of the two grounds
[`../crash-correctness.md`](../crash-correctness.md) admits — no window at all, or a real window whose whole loss is
accepted and named — exempts it from `bzh:crash-point-registry`, and what stands in for a sweep point instead. That file
owns the registry, the invariant checker, and the obligation to record a decision here; a hub write inside the
transcript lane is recorded in [`./transcripts.md`](./transcripts.md) instead.

## Promote or demote, then stamp the position

`PromoteService.promote` (`blizzard/src/blizzard/hub/domain/operations/promote.py`) calls
`ChunkQueueStore.record_promote_with_position` (`blizzard/src/blizzard/hub/store/internal/chunk_queue_store.py`), which
inserts the `chunk_promoted.promoted_at` fact and an explicit `queue_positions` fact — the queue tail, or the slot after
a named anchor — in the one unit the promote opens, beside any renormalization its landing needs (`insert_promote_rows`,
`blizzard/src/blizzard/hub/store/internal/chunk_rows.py`). `DemoteService.demote`
(`blizzard/src/blizzard/hub/domain/operations/demote.py`) is the same shape through `record_demote_with_position` and
`insert_demote_rows`: the `chunk_demoted.demoted_at` fact and an explicit backlog position. No window: a crash ahead of
either unit's commit loses every fact it wrote together, and a retry re-derives the same landing from a fresh read.
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
caller's transaction, so none has a window of its own — each leaves its intents or terminal no-closer skip facts durable
together with the triggering fact. The callers are:

- a landing-marker artifact write, in whichever store records it;
- the `delivery_repo_landed` write, on the hub node's landing step and in a hub action's landing record;
- an admitted transition to the reserved `done` terminal, on the same tenant-scoped locked transaction as its intents;
- the `delivery_landed` write and the `finalize_delivery` terminal transition — seam methods no live path calls;
- an operator's hand-completion.

The only span open past any of them is the window between that commit and the drain, which
`close.after-enqueue.before-drain` arms — once, on the marker path, rather than once per enqueuing caller, because every
caller opens the identical span.

A terminal transition and its intents commit or roll back together, whether the transition comes from a hub node or a
later graph node. A no-code marker alone and a nonterminal transition enqueue nothing. Retried enqueues deduplicate, and
ephemeral chunks and already-terminal refs remain excluded.

Within one intent's own attempt, past `close.after-close.before-record`, one transaction — `record_work_item_closure` —
writes the outcome fact and, for a `closed`/`gone`/`skipped` outcome, retires the intent together; a second, separate
write follows for the outcome's dedupe-gated `event_log` row. Folding the outcome and the retirement into one
transaction is what keeps a second dangerous window closed here: written separately, a crash between them could leave
the intent transiently pending against an already-terminal ref, the exact shape
`hub:no-pending-intent-against-terminal-ref` flags — and the armed crash point is checked for invariants immediately
after the kill, before any recovery pass runs, so that shape would be a guaranteed trip, not a rare race. A crash before
the folded transaction commits loses nothing (the closer's own contract is idempotent, so the next pass's re-attempt is
a clean no-op — the GitHub closer's trace comment is deduped by a hidden per-chunk marker read before posting, so a
re-attempt after a posted comment, a failed close, or a crash here never double-posts); a crash after it, before the
event write, loses only the informational, append-only event, never the fact or the retirement.

The sweep's per-intent backoff (`close_intent_attempts`) opens no window of its own. A `failed` outcome's attempt row
rides `record_work_item_closure`'s own transaction above — the same one that writes the outcome fact — so it is exactly
as durable as that fact and never separately lost. A due intent with no bound closer records a terminal `skipped`
outcome and retires in one transaction; a crash before commit leaves the intent pending for another pass. A `deferred`
attempt (the forge's rate budget turned the close away, so the row carries the `resume_at` the intent waits for) is the
same shape: `record_close_attempt_deferred` is its own single-statement transaction, with no outcome fact, no retirement
and no event beside it, so a crash before it commits loses nothing durable — the next pass re-attempts the intent, and
the budget turns it away again until its reset. Either way the ledger is append-only (`bzh:facts-not-status`): a crash
mid-sweep leaves some intents' backoff clocks ticked and others not, and the next pass reads each one's own history
fresh.

Per-ref close-once is `record_work_item_closure`'s own store-level uniqueness constraint on
`(chunk_id, source, ref, outcome)`, mirroring `record_hub_artifact`'s own idempotent-bool contract; retirement rides the
same transaction, so it carries no separate once-only claim of its own. `hub:no-double-terminal-closure` and
`hub:no-pending-intent-against-terminal-ref` are both legal-history invariants, not accepted false positives: the first
catches a broken idempotency guard letting a ref carry multiple terminal outcomes, the second a stuck retirement past
the point the folded transaction ever leaves one standing alone.

## A hub action pass's effect writes

`ActionPassDriver.drive` (`blizzard/src/blizzard/hub/delivery/action_pass.py`) writes each effect a pass records off the
action loop, one at a time, through the turn's task, and releases it back to the action only once it is durable; each
effect is one transaction of its own, so the windows are the spans between them. Three points name them:

| Point                              | Window                                                                                                                          |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `action.after-effect.before-write` | The action's forge write — a merge, a pull request opened, a check re-run — is done; the effect recording it is not yet durable |
| `action.after-write.before-resume` | An effect is durable; the action has not resumed                                                                                |
| `close.after-enqueue.before-drain` | A landing record and its close intents are durable in one transaction; no drain has run yet                                     |

A crash in any of them loses only the pass in flight: the next pass reads the forge and the node's markers and
converges, as it does after any crash, so an unwritten effect is written once on the re-take and a written one is
counted past. The kill-9 sweep (`tests/crash/test_kill9_sweep.py`) reaches the `action.` family through `test.sequence`
and through a two-repository `land` against the mock forge. Every landing record reaches
`close.after-enqueue.before-drain`, so the sweep opens the window between `land`'s two repositories there: killed with
the first landing durable and the second repository not yet merged, the restarted hub lands the second without merging
the first twice.

Landing recovery re-reads forge state and durable markers; a candidate is proven before reuse and cleanup follows a
durable landing record.

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

## A turn on a flow

`FlowDriver.tick` (`blizzard/src/blizzard/hub/delivery/flow_driver.py`) submits each chunk standing at a hub node while
`delivering` to its flows and starts the turns its submissions may take; the turn's task
(`blizzard/src/blizzard/hub/delivery/flow_turn.py`) runs the pass and ends the turn in the transaction that routes its
answer. A verdict's transition — or, on a cross-graph choice, the migration it records, with any gate it opens — and its
turn's end are one transaction, and a landing's `merged/<repo>` marker, its `delivery_repo_landed` row, its close
intents, its flow's `landed` fact, and its `flow-landed` event row are one more, so neither opens a window. The windows
that remain are the `flow.` family:

| Point                               | Durable                                     | Not yet                                          | Recovered by                                                                |
| ----------------------------------- | ------------------------------------------- | ------------------------------------------------ | --------------------------------------------------------------------------- |
| `flow.after-submit.before-turn`     | The submission, its flow rows, `submitted`  | Any turn                                         | The next tick takes the turn; the reconcile never submits it twice          |
| `flow.after-turn-start.before-pass` | The turn and its `turn-started` facts       | The pass                                         | Boot recovery ends the turn `interrupted`; the next turn takes a fresh pass |
| `flow.after-poll.before-turn-end`   | The turn and its `turn-started` facts       | The poll row and the turn's end, one transaction | Boot recovery ends the turn `interrupted`; the next turn polls afresh       |
| `flow.boot.after-interrupt`         | One tenant's open turns ended `interrupted` | The next tenant's, the driver                    | The next boot ends the rest; ending a turn already ended writes nothing     |

The windows inside a pass stay the `action.` family's above, with the turn's task as the writer. The kill-9 sweep
(`tests/crash/test_kill9_sweep.py`) arms each `flow.` point and lands the chunk on the restarted hub without merging
twice.

An empty-check observation is a marker effect written by the turn's `write_effect` through `record_hub_artifact` during
the pass, before the pending answer and turn end, not in their transaction. The sink waits for the marker to be durable;
a crash after that write replays against the node and epoch's existing marker and retains its first observation time. A
crash before the write leaves no observation and the next pass reads the forge again. The marker's shape is owned by
[action purity](../../standards/hub-nodes/action-purity.md).

## The boot recovery of open turns

`FlowDriver.recover_turns` runs from the hub daemon's startup, once in each open tenant before the hub serves and before
the driver's first tick. Every turn with no end belongs to the process that ran it, which crashed or shut down, since
one hub process serves the store ([`../system-shape/exclusive-writes.md`](../system-shape/exclusive-writes.md) §Known
debt). It ends each one `interrupted`, with a `turn-ended` fact on each flow it held, a `turn-interrupted` event, and
any withdrawal a lever deferred to it, then reconciles the tenant's lines in full. A submission still current keeps its
place, and its next turn takes a fresh pass that skips whatever its markers say is done.

Its one window is `flow.boot.after-interrupt`, between one tenant's recovery and the next. Both steps are idempotent, so
a boot that dies midway is finished by the next. Composition never calls it, so a CLI or test build over shared stores
cannot end a live daemon's turn.

## Tenant creation, one identity unit of work

`TenantAdministration.create` (`blizzard/src/blizzard/hub/domain/tenancy/administration.py`) writes a tenant's `tenants`
row, its packaged graphs, its `hub` work-ref sequence, its default project, its `standard` urgency with its position,
the tenant's settings naming `standard` as the default, and, when one is named, its first admin's membership, inside one
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
`chunks` plus `chunk_work_refs` — together. `WorkItemEditService.create`
(`blizzard/src/blizzard/hub/domain/work_items/editing.py`) opens one tenant unit of work that locks the chunk's
`WORK_REF` keys, and `mint_item` writes the item through the work-item repository, then the chunk through the chunk
record repository's own `mint`, both joining that unit ([`../repository-access.md`](../repository-access.md)
`bzh:unit-of-work`).

One narrower window is named and accepted here: `WorkItemEditService.create` allocates the item's `ref` through
`WorkItemStore.allocate_ref` before that unit opens, under the allocator's own already-accepted gap-tolerant contract,
so a crash in between burns that one `ref`, never reused — the same price a bare `allocate_ref` call already pays with
no chunk attached.

The pairing owes the checker nothing because it is a single-transaction insert, not a derived cross-fact invariant to
recompute.

## The routine-run mint

`POST /api/routines/{routine_id}/run` writes the run item's `work_items` row, its resting chunk's rows — `chunks` plus
one `chunk_work_refs` row per work ref — and the run's own identity row (`work_item_runs`), together: four tables owned
across three repositories. `RunService.run` opens one tenant unit of work that locks the chunk's `WORK_REF` key, and
`mint_run` (`blizzard/src/blizzard/hub/domain/garden/run_mint.py`) writes the item and chunk through `mint_item`, then
the run identity through the run-context repository's own `record`, each repository joining that unit — the same domain
composition §The item-creation chunk mint takes, with all four tables in one transaction. `work_item_runs` is what
garden delivery's own read (`blizzard/src/blizzard/hub/domain/garden/run_context.py`) resolves a chunk's run identity
through; landing it outside this transaction would reopen exactly the window this section exists to close.

The chunk is written with no promote fact and no queue position: it rests `not_ready` until the standalone promote.

One narrower window is named and accepted here. `RunService.run` (`blizzard/src/blizzard/hub/domain/garden/runs/run.py`)
allocates the run's `ref` through `WorkItemStore.allocate_ref` before this unit opens, identical in shape to §The
item-creation chunk mint's own: under the allocator's own already-accepted gap-tolerant contract, a crash in between
burns that one `ref`, never reused. The run's effective scope carries no write of its own to window: the API edge
resolves it to an already-existing, already-related `Scope` — a read, refusing rather than minting one — before
`RunService.run` is ever called, so the domain layer opens no second write ahead of the unit.

The composite owes the checker nothing because it is a single-transaction insert, not a derived cross-fact invariant to
recompute.

## The cadence mint

The cadence sweep mints a due errand's run through `CadenceMint.mint`
(`blizzard/src/blizzard/hub/domain/cadence/mint.py`), a domain unit of work over `IHubTransactions.begin()`. It writes
the same four tables §The routine-run mint writes, through the same `mint_run`, here joining the cadence unit's locked
transaction, and the run's identity row carries the errand's mark in that same write. For a promoting chore the unit
also writes the promote fact and the chunk's ready-list position, landed at the tail through the queue's own landing, so
a run minted promoted is never seen resting `not_ready`. Every write commits or none does: the same single-transaction
exemption §The routine-run mint takes, and the composite owes the checker nothing for the same reason.

The one window is the routine-run mint's own: the run's `ref` is allocated through `prepare_mint` before the transaction
opens, so a crash between them burns that one `ref`, never reused. A mint that loses its re-read inside the transaction,
the errand's last run moved since the pass judged it, writes nothing and burns its `ref` the same way. Planning refuses
before anything is allocated. The crash-point registry gains no point. A crash after the commit loses only the board's
push, which the board's next read recovers, and a hub restarted mid-pass judges every errand again on its first pass: a
minted errand's live run keeps it from being due (`bzh:errand-one-live-run`).

## Chunk delete, then hub-item withdrawal

`DeleteService.delete` (`blizzard/src/blizzard/hub/domain/operations/delete.py`) records `chunk_deleted`, releases the
chunk's outgoing dependency edges, and withdraws its open `hub:`-source items through their own repositories in one
tenant unit of work. A `forge:`-sourced pointer on the same chunk is left untouched — only `hub:`-source items close.

Both a direct delete and `WorkItemEditService.withdraw`'s cascade use this operation. The scoped tenant opener precedes
the chunk lock, and the fresh guard reads and writes follow on the same transaction (`bzh:store-exclusive-write`,
[`../system-shape/exclusive-writes.md`](../system-shape/exclusive-writes.md)); a claim cannot land during the delete.
The transaction seam and participation contract are owned by [`../repository-access.md`](../repository-access.md)
`bzh:unit-of-work`. There is no partial-write window within this unit to arm; this exemption does not claim a kill-9
test of the transaction.

`DeleteService.delete` also holds the residual per-tenant lock across that transaction — like the row lock above, a
guard against a concurrent writer rather than a crash;
[`../system-shape/exclusive-writes.md`](../system-shape/exclusive-writes.md) §Known debt owns who shares it and the race
it closes.

The pairing owes the checker nothing because it is a single-transaction insert-plus-update(s), not a derived cross-fact
invariant to recompute.

## Garden delivery, marker folded into its own transaction

`GardenDelivery.deliver` (`blizzard/src/blizzard/hub/domain/garden/delivery/materialize.py`) writes a garden run's whole
delta in one locked unit: `write_delivery_plan` writes the run's new `findings`, `finding_facts`, `finding_sets`,
`garden_proposals`, and `garden_proposal_findings` rows through their own repositories, then the delivery's own
`garden-delivered` marker artifact row through the delivery repository, every write joining the unit — five candidate
tables and the marker land together or not at all.

Unlike a marker an action records after its effect lands, the marker here is checked for existence and, if absent,
inserted as this same transaction's last statement. That is what makes a replay safe on either side of the commit: a
crash before commit loses the whole write, findings and marker alike, with nothing yet durable for a re-run to collide
with; a crash after commit leaves the marker already present, so the next `garden-deliver` pass
(`bzh:hub-node-step-idempotence`,
[`../../standards/hub-nodes/step-idempotence.md`](../../standards/hub-nodes/step-idempotence.md)) finds it on its own
idempotence check and returns `recorded` having minted nothing a second time.

The window this leaves is between `deliver`'s own commit and the action's resuming — already
`action.after-write.before-resume` in `bzh:crash-point-registry`, and already covered: the visit's next turn re-runs the
pass, and the in-transaction marker's own idempotence is what absorbs that re-run, so this write opens no window
`action.after-write.before-resume` doesn't already name.

The write owes the checker nothing because it is a single-transaction, multi-table insert, not a derived cross-fact
invariant to recompute — and, unlike most of this register's writes, whose idempotence marker an action records after
its effect lands, this one's marker is folded into its own transaction, which is what gives its replay idempotence in
the first place.

## Review findings delivery, marker folded into its own transaction

`ReviewFindingsMaterialize.deliver` (`blizzard/src/blizzard/hub/domain/garden/review/materialize.py`) mirrors the garden
delivery entry above: `write_review_plan` writes a review round's whole plan — the new `findings` and `finding_facts`
rows the round's `deferred` entries mint — through the finding repository, plus its own `review-findings-delivered`
marker artifact row through the delivery repository, all joining one locked unit. The idempotence check
(`already_delivered`, keyed on `chunk_id` alone, not `(chunk_id, node_id, epoch)`, since a chunk owes at most one
review-findings delivery) reads for the marker before writing, exactly as garden delivery's does, giving the same
before/after-commit replay safety: nothing durable on a pre-commit crash, and the next `record-findings` pass finding
its own marker and minting nothing further on one after.

This entry deviates from the garden precedent on one point: a scope a `deferred` entry names that does not yet exist is
minted inside this same unit through the scope repository (`domain/routines-and-scopes.md`'s own mint-on-name path for
review delivery), where garden delivery's own write instead reads the scope and refuses the whole delivery if it is
missing. A crash before this transaction commits therefore leaves neither the findings, the marker, nor any scope it
would have minted — the same all-or-nothing shape, just with one more table folded in.

The write owes the checker nothing for the same reason garden delivery's does: a single-transaction, multi-table insert
with its own in-transaction marker, not a derived cross-fact invariant to recompute.

## Garden proposal closure: pass, and accept-with-mint

`GardenProposalClosureStore.record_pass`/`record_accept_decline`
(`blizzard/src/blizzard/hub/store/internal/garden_proposal_closure_store.py`) each write one `garden_proposal_closures`
row on the connection of the unit the garden service opens, which declares the proposal's `GARDEN_PROPOSAL` key and
re-reads its closure under it before the domain decides. A crash before commit loses the whole write, with nothing yet
durable for a retried close to collide with; a crash after it leaves the closure already recorded, and a re-attempted
close re-reads it under the key and refuses as already-closed, exactly as a live race would.

The accept-with-mint path is a second writer of the same table: `GardenProposalClosureService.accept`
(`blizzard/src/blizzard/hub/domain/garden/proposals/closure.py`) opens one unit that writes the accepted-and-minted
`garden_proposal_closures` row through the closure repository, then the item's `work_items` row and its resting
`not_ready` chunk's rows through `WorkItemEditService.mint_drafted` — the same composition §The item-creation chunk mint
uses, plus the closure row folded into the same unit. The unit declares the proposal's `GARDEN_PROPOSAL` key and the
domain refuses an already-closed proposal from the closure it re-read under that key, so an already-closed proposal
mints nothing. It inherits §The item-creation chunk mint's one named gap unchanged: `prepare_mint`'s `allocate_ref`
still runs in its own transaction before this one opens, so a crash in between still burns one `ref`, never reused.

`GardenProposalClosureStore` is the one adapter that writes the closure table, for every close path; the
accept-with-mint unit composes its closure write with the item and chunk writes in the domain.

Both write paths owe the checker nothing because each is a single-transaction insert (plus, for accept-with-mint, the
item and chunk inserts), not a derived cross-fact invariant to recompute.

## Dependency edge declare and release

`ChunkDependenciesStore.declare`/`.release` (`blizzard/src/blizzard/hub/store/internal/chunk_dependencies_store.py`)
each write `chunk_dependencies` in one transaction — `declare` a single insert of the fresh edge row, on the connection
of the locked unit `DependencyService` opens through `IChunkExclusiveWrites.locked` and hands over as the handle's
`transaction`; `release` a read of the standing row followed by its `released_at`/`released_by` update on the same
connection, inside its own `store.write` transaction. Neither has a partial-write span for a crash to land inside:
`declare`'s insert either lands whole or not at all, and `release`'s read-then-write has nothing outside the transaction
observing the read before the write commits.

`DependencyService` (`blizzard/src/blizzard/hub/domain/chunk/dependencies.py`) runs `declare` and `release` under locks
[`../system-shape/exclusive-writes.md`](../system-shape/exclusive-writes.md) (`bzh:store-exclusive-write`) owns — which
each holds, and why. None is a crash guard. `declare`'s guards wrap the same not-a-crash-window shape §Chunk delete,
then hub-item withdrawal already takes for its own composite write: its own re-derived reads — the dependent's status,
the prerequisite's ephemerality, the standing set the cycle check walks — all run inside the locked transaction before
the write, guarding against concurrent decisions rather than a crash mid-transaction. Those same locks serialize the
ephemerality read against every writer that can make a prerequisite ephemeral, grouping included, so
`NoStandingDependencyOntoEphemeralChunk` (`hub:no-standing-dependency-onto-ephemeral-chunk`) is a
`bzh:invariant-checker` assertion as a backstop against a regression in that serialization, not a guard against a live
gap.

Neither `declare` nor `release` earns a `bzh:crash-point-registry` entry — the "no window at all" ground: `declare`'s
insert and `release`'s read-then-write are each whole inside their own single transaction. `declare` alone introduces
two derived cross-fact invariants the engine enforces no constraint behind: a standing edge could close a cycle in the
dependency graph, or duplicate an already-standing ordered pair, with no schema-level constraint stopping either — so it
earns two `bzh:invariant-checker` assertions: `NoStandingDependencyCycle` (`hub:no-standing-dependency-cycle`) and
`NoDuplicateStandingDependency` (`hub:no-duplicate-standing-dependency`),
`blizzard/src/blizzard/hub/store/internal/invariants.py`. `release` only sets `released_at`/`released_by` on an
already-standing row, inside that same single transaction: it adds no standing edge, so it introduces no derived
invariant of its own.

### A fold's edge rewrite, riding its own `chunk_grouped` write

`ChunkDependenciesStore.record_fold_locked` (`blizzard/src/blizzard/hub/store/internal/chunk_dependencies_store.py`)
takes every target a fold carries and records each one's `chunk_grouped` row — via `record_grouped_row_conn`
(`blizzard/src/blizzard/hub/store/internal/chunk_rows.py`) — plus its own release/mint edge rewrite, on the fold's
already-locked connection (`bzh:store-exclusive-write`). `GroupService.group`
(`blizzard/src/blizzard/hub/domain/operations/queue.py`) opens that one locked transaction for the whole fold and calls
`record_fold_locked` exactly once inside it, covering every target the fold carries, so no target's `chunk_grouped` row
can ever commit ahead of a sibling target's own edge release/mint — the condition
`hub:no-standing-dependency-onto-ephemeral-chunk` forbids: a standing edge naming an already-grouped-away chunk.
`add_work_refs` runs in the same unit too, ahead of `record_fold_locked` in the same loop-then-once shape, so the fold's
work-ref merges and its edge rewrite share one transaction: no crash can leave some targets' work refs merged with none
of them grouped. The whole fold earns no `bzh:crash-point-registry` entry on the "no window at all" ground: there is
nothing for a crash to land partway through, across the whole fold, work refs included.

## Delivery-triggered finding closure, riding the close-intent drain

`HubWorkSource.close` (`blizzard/src/blizzard/hub/work_sources/internal/hub_work_source.py`) is `IWorkCloser`'s own
hub-native implementation, reached by §The close-intent drain sweep the same way any other closer is:
`WorkItemEditService.deliver` writes the item's `closed_at`/`closure` first, then, as a second write,
`GardenProposalDeliveryResolution.resolve_for_item` appends the accepted proposal's `delivered` `finding_facts` rows, if
the delivered item minted from one.

A crash between those two writes leaves the item delivered with its proposal's findings still live — not a gap, the same
shape §The close-intent drain sweep's own `close.after-close.before-record` window already covers: the intent's own
retirement fact has not landed either, so the sweep retries `close` for the same ref, `deliver` re-reads the item under
its `WORK_ITEM` key and replays as the domain's `NOOP`, and `resolve_for_item` runs again. Its own gate is
`has_delivery_for_proposal` (a `finding_facts` row already carrying the proposal's id), not any one finding's current
state, so that retry completes an interrupted closure exactly once and a finding a person reopens afterward is never
silently re-closed by a later, unrelated repeat of the same close.

## Runner and host fact ingest: each fact and its high-water mark in one unit

`FactIngestService.ingest` (`blizzard/src/blizzard/hub/domain/execution/facts.py`) walks a runner's pushed batch in seq
order. Each fact that applies lands in its own unit, opened through `IHubTransactions.begin`. The unit writes the fact's
domain row, then advances `runner_high_water` to that fact's seq through `set_runner_high_water`, and both commit
together before the loop moves to the next fact.

No window: a crash ahead of a unit's commit loses the fact's row and its mark advance together. A replay resubmits every
seq the runner's own ack never confirmed. Seqs at or below the mark answer `already_applied`. The rest, the in-flight
fact among them, apply once against the mark the crash left. Committing per fact, not once after the whole batch, keeps
what a push already committed when the crash lands: a crash mid-way through a ten-fact push after the third fact's unit
commits leaves three facts applied, and the replay applies only the other seven. A rejected fact never advances the
mark, so its unit commits nothing.

The advance moves the mark only from the seq the push last read or set (`bzh:write-reestablishes-read`), so an
overlapping push of the same runner's can neither re-apply a seq the other committed nor move the mark back. The write
owes the checker nothing: `runner_high_water` is a per-runner scalar, not a derived cross-fact invariant to recompute.

The host's fact lane holds the same ground. `HostFactIngestService.ingest`
(`blizzard/src/blizzard/hub/domain/execution/host_facts.py`) lands each fact that applies in its own unit: the sample or
miss upsert on its `(host_id, slug)` row, then the advance of `host_high_water` through
`HostRegistryStore.set_high_water`, conditioned on the seq the push last read or set. A crash ahead of the unit's commit
loses the upsert and the advance together, and an overlapping push of the same host's can neither overwrite a newer
sample with an older one nor move the mark back.

## Hosts: retire, and add with adopt

`HostRetirementService.retire` (`blizzard/src/blizzard/hub/domain/execution/host_retirement.py`) decides the refusal in
the `Host` model over every live runner's holdings before it writes, then writes in two steps. First,
`HostRegistryStore.record_retirement` appends the host's retire fact and revokes its token in one transaction, so the
host can add no runner from that instant. Second, `FleetService.retire` runs once per runner under the host, read after
the first step commits.

The span between the two steps is a real window whose whole loss is accepted and named: a crash inside it leaves a host
retired with runners under it that are not. The loss is bounded to those runners staying live a while longer, and
nothing is corrupted — re-running `retire` over the retired host writes no second host fact and runs each runner's
retire again, which retires any left standing and finishes any interrupted release of their chunks, as a runner's own
re-run does. A sweep point would arm a span an operator's re-run already closes, so none is registered. The re-run finds
those runners because `runner_registrations.host_id` stays their durable roster: every write that places a runner under
a host, releases one, or reinstates one lands only on the host's and the runner's lifecycle versions it was decided on
(`bzh:write-reestablishes-read`), and `Host.release` refuses an unretired runner from a retired host.

`HostEnrollmentService.add` with `--adopt` has no window. `HostRegistryStore.add` inserts the host and places every
adopted runner in one scoped write transaction, and a runner that came to stand under a host first rolls the whole write
back, so a crash or a refusal loses the host and its adoptions together.
