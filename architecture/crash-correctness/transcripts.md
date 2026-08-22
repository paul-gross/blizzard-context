# Crash-correctness exemptions — the transcript lane (`bzh:crash-exemptions-transcripts`)

This register records, for each durable write in the transcript lane on either daemon, which of the two grounds
[`../crash-correctness.md`](../crash-correctness.md) admits — no window at all, or a real window whose whole loss is
accepted and named — exempts it from `bzh:crash-point-registry`, and what stands in for a sweep point. That file owns
the registry, the invariant checker, and the obligation to record a decision here.

## The pump read

`TranscriptPump` (`blizzard/src/blizzard/runner/loop/transcript_pump.py`) reads a segment's next batch of turns from the
harness transcript source through `turns_since` — an external file read, not a store write — then advances the cursor
and enqueues the deltas in one `record_transcript_deltas` transaction. A crash between the read and the write loses only
the read, since `turns_since` is a pure forward read of an immutable log and the next tick re-reads from the same
unadvanced cursor for the same batch.

The write half sits behind the boundary the `transcript.*` crash-point family already guards — the drain's submit/ack
window in `TranscriptDrain` (`blizzard/src/blizzard/runner/loop/transcript_drain.py`), which the generic sweep reaches
with no dedicated scenario, because every lease closure enqueues a final marker regardless of `[transcripts] ship`. The
pump needs no invariant-checker assertion beyond the lane's gapless-sequence and exactly-once checks that the family's
registered points already exercise.

## Truncation outcomes

A record-cap shrink (`record_cap_exceeded`) or an unshippable record (`record_unshippable`) fires three separate
transactions in sequence: `record_transcript_deltas`, then `mark_transcript_record_truncated` for the segment's own
reason field, latched per segment and reason, then `OutboundFacts.transcript_truncated`, the fact-lane `warning` event.

A chunk-budget breach (`chunk_budget_exceeded`) is a different write shape, not the same one under another reason
string: neither of `TranscriptPump._pump_one`'s two call sites writes a delta at all, and each fires
`stop_transcript_segment_shipping` and then the same fact-lane warning. A budget breach's reason field is re-derived
from `chunk_transcript_shipped_bytes` fresh every tick, so a crash before `stop_transcript_segment_shipping` lands
leaves the segment un-stopped one tick longer and the next evaluation of the same over-budget total retries the same
write: delayed, never lost.

The delta-then-reason-field window, which only the record-cap and unshippable paths have, costs at most one occurrence's
own note, since `truncated_reason` is a worst-of display field rather than a per-event log and the delta write already
made cursor and content durable.

The window between the reason-field write and the fact-lane enqueue is the one window this register does not claim is
safe, and it belongs to every reason that latches through `mark_transcript_record_truncated` and then enqueues the
fact-lane warning — the latch is the discriminator, not the reason string. A crash inside it leaves the segment durably
marked while the operator-facing warning goes permanently unsent, no guard firing again to retry a warning for a reason
already warned about. It stays out of `bzh:crash-point-registry` on the narrower ground that nothing durable is wrong or
lost, only an operator-convenience notification, recoverable by reading the segment's own durable `truncated_reason`
field (`blizzard/src/blizzard/runner/store/schema.py`) rather than by automatic retry.

The pump's unlinked-sidechain warning (`_warn_sidechains_dropped`) repeats that shape one degree further, pairing a
durable per-segment-per-`agent_id` latch (`mark_sidechain_dropped_warned`, so a recurring unlinked subagent warns once
rather than every tick) with the fact-lane enqueue; a crash between them permanently loses that one warning, accepted on
the same ground and at the same price.

## The backfill verb

`TranscriptBackfill` (`blizzard/src/blizzard/runner/loop/transcript_backfill.py`) is an operator verb rather than a loop
step, so no sweep family reaches it, and it holds no state between runs, re-deriving its work list every time from
`transcript_backfill_leases()` — every session-bearing lease the runner holds, each flagged with whether its session
already carries a segment — with `TranscriptBackfill.run` skipping the flagged ones.

Its one multi-write sequence is `open_transcript_segment`, then any number of `record_transcript_deltas`, then
`finalize_transcript_segment`, and every interruption of it lands on the same recoverable state: an open segment. An
open segment is what the next run resumes, because finalization is conditional on the drain reporting it read the source
to its end (`TranscriptPump.drain_segment` returning `True`) rather than on having attempted it, so a crash can leave a
partial segment but never a sealed one. The resumed run continues from the segment's own persisted cursor and re-offers
only ranges the hub's natural key `(segment_id, turn_range_start)` already dedupes.

Backfill needs no new checker assertion: `TranscriptSegmentFinalizedExactlyOnce`
(`blizzard/src/blizzard/foundation/store/invariants.py`) already covers the finalize-plus-marker write, which is one
transaction, and an unfinalized segment is a legal, resumable state rather than a violated invariant.

## The hub's event-derivation sweep

`EventDerivationReconciler` (`blizzard/src/blizzard/hub/domain/analytics/derivation.py`) is not a loop step any sweep
family reaches, and holds no state between passes, re-deriving its candidates from
`EventDerivationService.candidate_segment_ids()`, the visible segment set diffed against each segment's derivation
marker.

Its two durable write paths are each one transaction: `TranscriptEventStore.replace_segment_events`, which deletes that
`(segment_id, extractor_version)` pair's rows, inserts the fresh set, and writes the marker; and `drop_segment` for a
segment that left the visible set. A crash in either path leaves a segment underived, fully derived, or fully dropped,
never half, and the next pass re-reaches it: an underived segment is still a candidate, and a dropped-but-unnoticed one
is recomputed from `derived_segment_ids()` minus `visible_segment_ids()` every sweep.

Per-segment-per-version uniqueness on `(segment_id, extractor_version, kind, turn_path, occurrence)` is a store-level
unique constraint the engine enforces, not a derived cross-fact invariant the checker must recompute.
