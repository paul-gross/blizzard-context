# Recorded exemptions — the transcript lane's durable writes (`bzh:crash-exemptions-transcripts`)

Each entry states why a durable write opens no window `bzh:crash-point-registry` must name, and what stands in for a
sweep point instead — the register [../crash-correctness.md](../crash-correctness.md) §Recorded exemptions routes into.
Entries cite their siblings by issue number across all three files: [./runner.md](./runner.md) and [./hub.md](./hub.md).

- **The transcript lane's pump read (issue #246).** `TranscriptPump` (`src/blizzard/runner/loop/transcript_pump.py`)
  reads a segment's next batch of turns from the harness transcript source (`turns_since`, an external file read, not a
  store write) and then advances the segment's cursor and enqueues its delta(s) in one transaction
  (`record_transcript_deltas` — one ledger update plus N buffer-row inserts when an over-cap batch splits into several
  records) — a read-then-atomic-write shape a reviewer might expect a window between the two halves of. There is none:
  the read is not durable state of its own, so a `kill -9` between the read and the write loses nothing but the read
  itself, and the next tick re-reads from the *same* still-unadvanced cursor and produces the same batch (`turns_since`
  is a pure forward read of an immutable log, never destructive). The write half is already covered by the boundary the
  `transcript.*` crash-point family guards — the drain's own submit/ack window (`TranscriptDrain`,
  `src/blizzard/runner/loop/transcript_drain.py`), reachable by the generic sweep with no dedicated scenario since every
  lease closure enqueues a final marker regardless of `[transcripts] ship`. There is therefore **no new
  `bzh:crash-point-registry` entry** for the pump's own read-then-write shape and **no new `bzh:invariant-checker`
  assertion** beyond the lane's gapless-sequence and exactly-once checks the family's registered points already exercise
  — the same shape as the #95 jti, #125 event-emission, #149 preamble-fingerprint, #137 promote-then-tail-stamp, #216
  delivery-closure-sweep, and #230 marker-token exemptions.

- **The transcript pump's truncation-outcome writes (issue #246).** A record-cap shrink (`record_cap_exceeded`) or an
  unshippable record (`record_unshippable`) fires two SEPARATE transactions in sequence: `record_transcript_deltas` (the
  delta(s) themselves), then `mark_transcript_record_truncated` (the segment's own reason field, latched per (segment,
  reason)) — with `OutboundFacts.transcript_truncated` (the fact-lane `warning` event, never silent) following as a
  third, separate write again. A chunk-budget breach (`chunk_budget_exceeded`) is a DIFFERENT shape, not the same one
  with a different reason string: neither of `TranscriptPump._pump_one`'s two call sites ever writes a delta to the
  store — the pre-read guard returns before the source is even read, and the post-read (tipping) guard builds the
  record(s) in memory but never calls `record_transcript_deltas`. Each fires `stop_transcript_segment_shipping` (the
  reason field) then the same fact-lane warning; the write count on the tipping guard's branch is not fixed at two,
  though, since its own already-read batch can also carry a dropped sidechain, adding that warning's own latch write and
  fact-lane enqueue to the same branch. Neither the delta-then-reason-field window (record-cap/unshippable only) nor the
  budget breach's own reason-field write needs a registry entry: the former loses at most one occurrence's own note —
  `truncated_reason` is a worst-of display field, not a complete per-event log (`mark_transcript_record_truncated`'s own
  guard: the warning latches per reason, but the DISPLAYED reason keeps moving to whichever severity is highest so far)
  — and the delta write's own transaction already made the cursor/content durable regardless; the latter is re-derived
  from `chunk_transcript_shipped_bytes` fresh on every tick independent of any per-event write, so a `kill -9` before
  `stop_transcript_segment_shipping` lands simply leaves the segment un-stopped one tick longer, which re-evaluates the
  same still-over-budget total and retries the same write — no state lost, only delayed. The reason-field-write →
  fact-lane-enqueue window, by contrast, is real for all three reasons and is the one window this entry does not claim
  is safe: a `kill -9` there leaves the segment durably marked but the operator-facing warning permanently unsent, since
  neither write's own guard fires again on a later tick to retry a warning for a reason the segment already warned
  about. It stays out of `bzh:crash-point-registry` on a narrower ground than "no window" — nothing durable is ever
  wrong or lost, only an operator-convenience notification, recoverable by direct inspection of the segment field itself
  (e.g. via `blizzard runner artifact`/a future read surface) rather than by automatic retry — and closing it would mean
  a fourth transaction merging the reason-field write and the warning atomically, at a cost this slice does not spend
  given `[transcripts] ship = false` by default. The pump's **unlinked-sidechain warning** (`_warn_sidechains_dropped`)
  is the same shape one degree further, with its own two-write sequence: `mark_sidechain_dropped_warned` (a durable
  per-(segment, agent_id) latch, so a recurring unlinked subagent warns once, not every tick) then the fact-lane
  enqueue. A `kill -9` between the two permanently loses that one warning — the latch already reads as "warned" on the
  next tick, so nothing re-fires it. On the two budget-stop branches, this pair fires with no cursor write of its own at
  all (both return before any store write past the reason field). It is accepted on the same narrower ground and for the
  same price: an informational fact-lane event, the #125 exemption's shape, on a lane `[transcripts] ship = false` keeps
  cold by default. There is therefore **no new `bzh:crash-point-registry` entry**: the delta-then-reason-field and
  budget-breach windows degrade rather than break, matching the #137/#216/#230 exemptions in [./hub.md](./hub.md), and
  the last two are named, accepted gaps, recoverable by inspection rather than automatic retry, not windows this repo
  claims to have no exposure to at all.

- **The runner's transcript backfill (blizzard#250).** `TranscriptBackfill`
  (`blizzard/src/blizzard/runner/loop/transcript_backfill.py`) is an operator verb, not a loop step, so no sweep family
  reaches it; it holds no state between runs, re-deriving its work list every time from `transcript_backfill_leases()`
  (the runner's own leases, minus the sessions already carrying a segment). Its one multi-write sequence —
  `open_transcript_segment`, then any number of `record_transcript_deltas`, then `finalize_transcript_segment` — is a
  position a reviewer would reasonably expect a sweep point for, and every interruption of it lands on the same
  recoverable state: an **open** segment. That is precisely the state the next run resumes, because finalization is
  conditional on the drain reporting it read the source to its end (`TranscriptPump.drain_segment` returning `True`),
  never on merely having attempted it — a segment is closed out only when there is nothing left to read, so a `kill -9`
  can leave a partial segment but never a *sealed* partial one. The resumed run continues from the segment's own
  persisted cursor and re-offers only ranges the hub's natural key `(segment_id, turn_range_start)` already dedupes.
  There is therefore **no `bzh:crash-point-registry` entry** for it and **no new `bzh:invariant-checker` assertion**:
  `TranscriptSegmentFinalizedExactlyOnce` already covers the finalize-plus-marker write, which is one transaction, and
  an unfinalized segment is a legal, resumable state rather than a violated invariant — the same shape as the #95 jti,
  #125 event-emission, #149 preamble-fingerprint, #137 promote-then-tail-stamp, #216 delivery-closure-sweep, and #230
  marker-token exemptions. The verb additionally refuses to run at all while a daemon holds the runtime's socket, so it
  never races the loop for the single-writer store.

- **The hub's transcript-event derivation sweep (blizzard#254).** `EventDerivationReconciler`
  (`blizzard/src/blizzard/hub/domain/analytics/derivation.py`) is not a loop step any sweep family reaches — it is the
  hub's own in-process `Sweep` driver, the same shape as its `AnnotationReconciler`/`DeliveryClosureReconciler` siblings
  — and holds no state of its own between passes, re-deriving its candidate set every time from
  `EventDerivationService.candidate_segment_ids()` (the visible segment set diffed against each segment's own derivation
  marker) rather than tracking what it has already reached. Its two durable write paths are each a single transaction:
  the per-segment replacement (`TranscriptEventStore.replace_segment_events` — delete this
  `(segment_id, extractor_version)` pair's rows, insert the fresh set, write the marker) and the drop of a segment that
  left the visible set (`drop_segment`). A `kill -9` at any point during either therefore leaves a segment either
  underived, fully derived (rows + marker together), or fully dropped (rows + markers together) — never half — and the
  next pass re-reaches it: an underived segment is still a candidate, and a dropped-but-not-yet-noticed segment is
  recomputed from `derived_segment_ids() - visible_segment_ids()` fresh every sweep. There is therefore **no
  `bzh:crash-point-registry` entry** for it, in the shape this registry already uses for the hub's own delivery-closure
  sweep (#216) and the runner's transcript backfill (blizzard#250): both are converging reconcilers with no state
  between passes. **No new `bzh:invariant-checker` assertion** either: per-segment-per-version uniqueness
  (`(segment_id, extractor_version, kind, turn_path, occurrence)`) is a store-level unique constraint the engine
  enforces, not a derived cross-fact invariant the checker must recompute — the same shape as the #95 jti, #125
  event-emission, #149 preamble-fingerprint, #137 promote-then-tail-stamp, #216 delivery-closure-sweep, #230
  marker-token, and blizzard#250 backfill exemptions.
