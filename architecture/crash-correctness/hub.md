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

`CloseIntentDrainer.sweep()` (`blizzard/src/blizzard/hub/domain/work_closure.py`, blizzard#383) retires pending
`close_intents` rows a landing or completion transaction enqueued. Its two dangerous windows are both registered:
`close.after-enqueue.before-drain` (a landing marker and its intents are durable; no drain has run yet) and
`close.after-close.before-record` (a close attempt returned; its outcome is not yet recorded and its intent not yet
retired), swept by a dedicated scenario driving the built-in `hub` work source with no forge
(`tests/crash/test_kill9_sweep.py::test_kill9_at_close_crash_point`). This entry records the one span inside that second
window `close.after-close.before-record` does not itself arm — a real window whose whole loss is accepted and named, per
this file's own admitted ground.

Within one intent's own attempt, past that point, three things happen as separate writes rather than one transaction:
the outcome fact (`record_work_item_closure`), the intent's own retirement (`retire_close_intent`, `closed`/`gone` only
— a `failed` outcome retires nothing), and the outcome's dedupe-gated `event_log` row. A crash between the first two
leaves the intent transiently pending against an already-terminal ref — the exact shape
`hub:no-pending-intent-against-terminal-ref` flags — lost only until the next drain pass, which reaches it again:
`record_work_item_closure` replays as a no-op (the outcome already carries this exact key), and `retire_close_intent`
finishes what the crash interrupted. A crash between the second and third loses only the informational, append-only
event, never the fact or the retirement.

Per-ref close-once is `record_work_item_closure`'s own store-level uniqueness constraint on
`(chunk_id, source, ref,
outcome)`, mirroring `record_hub_artifact`'s own idempotent-bool contract; per-intent
retire-once is `retire_close_intent`'s own idempotent no-op, the same shape — neither is a derived cross-fact invariant.
`hub:no-double-terminal-closure` and `hub:no-pending-intent-against-terminal-ref` are: the first catches a broken
idempotency guard letting a ref carry both `closed` and `gone`, the second catches a stuck retirement past the point a
legal history ever leaves one.

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
`chunks` plus `chunk_work_refs` — together, a pairing spanning two tables `ChunkStore` otherwise owns. Both of those
inserts run on the same connection inside one `engine.begin()` in `WorkItemStore.create_with_chunk`
(`blizzard/src/blizzard/hub/store/internal/work_item_store.py`), through one repository adapter, which reaches into
`ChunkStore`'s row-insert body through the shared `insert_chunk_rows`
(`blizzard/src/blizzard/hub/store/internal/chunk_store.py`) free function rather than through `IWriteChunkRepository`'s
seam. That seam bypass is deliberate rather than a layering gap: it is what lets a single caller open one transaction
over both tables at all.

One narrower window is named and accepted here: `WorkItemEditService.create` allocates the item's `ref` through
`WorkItemStore.allocate_ref` before that transaction opens, under the allocator's own already-accepted gap-tolerant
contract, so a crash in between burns that one `ref`, never reused — the same price a bare `allocate_ref` call already
pays with no chunk attached.

The pairing owes the checker nothing because it is a single-transaction insert, not a derived cross-fact invariant to
recompute.

## Chunk delete, then hub-item withdrawal

`WorkItemStore.delete_chunk_and_withdraw_hub_items` (`blizzard/src/blizzard/hub/store/internal/work_item_store.py`)
writes the chunk's `chunk_deleted` row and closes every open `hub:`-source item it holds as withdrawn, both on one
`engine.begin()` connection — the same single-transaction shape `create_with_chunk` above uses for its own pairing. The
`chunk_deleted` insert runs through `record_deleted_row` (`blizzard/src/blizzard/hub/store/internal/chunk_store.py`), a
free function reaching into `ChunkStore`'s row-insert body the same way `insert_chunk_rows` does for the mint side; the
`work_items` closures reuse `WorkItemStore._close_conn`, the same connection-scoped update `close` itself calls. A
`forge:`-sourced pointer on the same chunk is left untouched — only `hub:`-source items close.

`DeleteService.delete` (`blizzard/src/blizzard/hub/domain/delete.py`) reaches this write from both a direct chunk delete
and `WorkItemEditService.withdraw`'s own cascade into an unacquired holder, always inside the same `threading.Lock`
`ClaimService`/`EditService`/`RestartService` already shared before this feature
(`blizzard/src/blizzard/hub/composition.py`) — the guard-check and the composite write happen under one held lock, so a
claim cannot land on a chunk this write is mid-way through deleting. That lock closes a same-process concurrency race,
not a crash window: the call sequence it guards only reads (`load_facts`) before acting, with no write of its own ahead
of the one atomic transaction — unlike `create_with_chunk`'s own sibling gap, `allocate_ref` running in its own
transaction before the insert it feeds, there is no narrower window here to name and accept.

The pairing owes the checker nothing because it is a single-transaction insert-plus-update, not a derived cross-fact
invariant to recompute.

## Proposed work items, riding the completion's own write

A node-step's proposed work items (`work_item_proposals`) ride whichever write already carries its artifacts:
`ChunkStore.record_transition`, `record_migration`, and `record_decision`
(`blizzard/src/blizzard/hub/store/internal/chunk_store.py`) each take the step's proposal rows on the same connection,
inside the same `engine.begin()`, as the transition, migration, or decision fact they accompany. Only the proposal
insert runs through a shared `_insert_proposals` helper — each write's own `ArtifactRow`s stay their own separate inline
loop. A crash before that commit loses the whole write, proposals included, exactly as it already loses the fact and its
artifacts; a crash after it has nothing left to lose. A consumer now reads these rows — the delivery-materialization
sweep below — but only once the chunk delivers, well after this write's own transaction has closed one way or the other,
so that consumer changes nothing about this write's own correctness.

The write owes the checker nothing because it is a single-transaction insert, not a derived cross-fact invariant to
recompute.

## A gate resolution's strike, riding the resolution's own write

`ChunkStore.record_decision_resolution` (`blizzard/src/blizzard/hub/store/internal/chunk_store.py`) inserts each struck
proposal's `work_item_strikes` row on the same connection, inside the same `engine.begin()`, as the
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
