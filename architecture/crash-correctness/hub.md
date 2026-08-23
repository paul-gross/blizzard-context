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

## The delivery closure sweep

`DeliveryClosureReconciler.sweep()` (`blizzard/src/blizzard/hub/domain/work_closure.py`) is not a loop step any sweep
family reaches, and it holds no state between passes, re-deriving its candidate set every time from
`closable_work_refs()` — a chunk's own landing facts and node artifacts — and each ref's own `work_item_closures` rows.
A ref a crash left unreached is retried on the next pass, with an idempotent forge close, converging on the outcome an
uninterrupted run would have reached.

Within one ref's attempt the outcome fact (`record_work_item_closure`) and its dedupe-gated `event_log` row are two
separate writes rather than one transaction, so a crash between them loses only the informational, append-only event,
never the fact. A later sweep calling `record_work_item_closure` against an already-recorded outcome returns `False` and
emits nothing, so neither a duplicate event nor a silently-missing durable record follows.

Per-ref close-once is a store-level uniqueness constraint on `(chunk_id, source, ref, outcome)`, mirroring
`record_hub_artifact`'s own idempotent-bool contract, not a derived cross-fact invariant.

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
