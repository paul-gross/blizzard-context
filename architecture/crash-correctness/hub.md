# Recorded exemptions — the hub's durable writes (`bzh:crash-exemptions-hub`)

Each entry states why a durable write opens no window `bzh:crash-point-registry` must name, and what stands in for a
sweep point instead — the register [../crash-correctness.md](../crash-correctness.md) §Recorded exemptions routes into.
Entries cite their siblings by issue number across all three files: [./runner.md](./runner.md) and
[./transcripts.md](./transcripts.md).

- **The hub's promote-then-tail-stamp write (issue #137).** `PromoteService.promote` records the
  `chunk_promoted.promoted_at` fact (`record_promote`) and then, as a second write, an explicit `queue_positions`
  tail-position fact (`record_queue_position`) stamping the newly-ready chunk past every currently-ready chunk. A
  `kill -9` between the two writes leaves the chunk promoted but with no explicit queue position — a position a reviewer
  would reasonably expect a sweep point for — but `QueueService._effective_position`'s fallback (also issue #137)
  already covers exactly that gap: an un-positioned chunk sorts by its `chunk_promoted.promoted_at`, a real-world
  timestamp, which is always far larger than any small explicit-position float ever assigned to another chunk, so the
  chunk still lands at the tail of the ready queue — the same practical outcome the missed tail-stamp was for. There is
  therefore **no new `bzh:crash-point-registry` entry** and **no new `bzh:invariant-checker` assertion**: no new durable
  guard is needed, the window degrades rather than breaks, and there is no new cross-fact invariant to check — the same
  shape as the #95 jti, #125 event-emission, and #149 preamble-fingerprint exemptions.

- **The hub's delivery closure sweep (issue #216).** `DeliveryClosureReconciler.sweep()` is not a loop step any sweep
  family reaches; like the forge-status annotation sweep it sits beside, it holds no state of its own between passes,
  re-deriving its candidate set every time from `closable_work_refs()` (a chunk's own landing facts and node artifacts)
  and each ref's own `work_item_closures` rows. A `kill -9` between passes loses nothing durable: a ref not yet reached
  is simply retried, with an idempotent forge close, on the next pass, converging on the outcome it would have reached
  uninterrupted. Within one ref's own attempt, the outcome fact (`record_work_item_closure`) and its dedupe-gated
  `event_log` row are two separate writes, not one transaction — a `kill -9` between them loses only the event, never
  the fact: the event is informational and append-only, the same shape the #125 event-emission exemption already covers,
  and a later sweep's `record_work_item_closure` call against an *already-recorded* outcome correctly returns `False`
  and emits nothing, so neither a duplicate event nor a silently-missing durable record follows either way. There is
  therefore **no new `bzh:crash-point-registry` entry** and **no new `bzh:invariant-checker` assertion**: per-ref
  close-once is a store-level uniqueness constraint (`(chunk_id, source, ref, outcome)`, mirroring
  `record_hub_artifact`'s own idempotent-bool contract), not a derived cross-fact invariant — the same shape as the #95
  jti, #125 event-emission, #149 preamble-fingerprint, and #137 promote-then-tail-stamp exemptions.

- **The hub's marker-write capability token (issue #230).** `MarkerAuthority`
  (`src/blizzard/hub/delivery/marker_auth.py`) mints an in-memory, process-scoped token per
  `(chunk_id, node_id, epoch)`, immediately before that hub-node step's `run:` commands execute, and revokes it in a
  `finally` once the step's visit is done with it — never persisted, a fact a reviewer might otherwise expect a
  `bzh:crash-point-registry` window for, since the token gates a marker write that is itself durable. A `kill -9`
  mid-step orphans the land script it spawned, leaving that script holding a token minted by a process that no longer
  exists: its later marker-write POSTs then fail, verified against the restarted process's fresh, empty authority. That
  is safe, not a gap — the executor's at-least-once-per-step contract (`bzh:hub-node-step-idempotence` in
  [../standards/hub-nodes.md](../../standards/hub-nodes.md)) re-runs that exact step from its own first command on the
  next hub-advance, minting a fresh token and re-recording the marker idempotently; no crash-sweep assertion depends on
  an orphan's rejected write landing. There is therefore **no `bzh:crash-point-registry` entry** for it and **no new
  `bzh:invariant-checker` assertion**: the token is in-memory, credential-shaped state with no durable form and no
  partial-write window of its own — the same shape as the #95 jti, #125 event-emission, #149 preamble-fingerprint, #137
  promote-then-tail-stamp, and #216 delivery-closure-sweep exemptions.

- **The hub's item-creation chunk mint (blizzard#359).** `POST /api/work-sources/hub/items` now writes the item's
  `work_items` row and its resting `not_ready` chunk's rows (`chunks` + `chunk_work_refs`) together — a position a
  reviewer would reasonably expect a sweep point for, since the pairing spans two tables `ChunkStore` otherwise owns.
  There is no dangerous window: both inserts run on the **same connection inside one `engine.begin()`**
  (`WorkItemStore.create_with_chunk`), through **one repository adapter** — `WorkItemStore`, the sole implementor of
  `IWriteWorkItemRepository` — which reaches into `ChunkStore`'s own row-insert body via the shared `insert_chunk_rows`
  free function rather than going through `IWriteChunkRepository`'s seam. That bypass is deliberate, not a layering gap:
  it is what lets a single caller open a single transaction over both tables at all, the same one-transaction shape
  `ChunkStore.record_stop` already carries for its own cross-table write (`chunk_stopped` + `route_released` +
  `hub_exec_slot`), just reached from the item side instead of the chunk side. A `kill -9` mid-write leaves neither row
  durable — no orphan item with no chunk, no orphan chunk with no item — and the caller sees the write fail rather than
  a partial success to retry against. The one narrower window this entry does name, and accepts:
  `WorkItemEditService.create` allocates the item's `ref` (`WorkItemStore.allocate_ref`) *before* that transaction
  opens, under that allocator's own already-accepted gap-tolerant contract (a first-allocation optimistic-insert, a
  losing concurrent first allocation falling through to an increment-and-`RETURNING` path on the now-present row) — a
  crash between the allocation and the transaction burns that one `ref`, never reused, exactly the price a bare
  `allocate_ref` call already pays with no chunk attached. That allocator's shape is its own thing, not this file's #95
  jti exemption's check-then-insert-under-a-primary-key sequence — the two share only the conclusion that a burned
  identifier is an accepted cost, not the mechanism. There is therefore **no new `bzh:crash-point-registry` entry** for
  the composite write, and **no new `bzh:invariant-checker` assertion**: the pairing is a single-transaction insert, not
  a derived cross-fact invariant to recompute — the same shape as the durable-fact exemptions, minus the jti exemption's
  particular mechanism.
