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
from `chunk_transcript_shipped_bytes_for_chunks`, read once per run into a local per-run mirror, fresh every tick, so a
crash before `stop_transcript_segment_shipping` lands leaves the segment un-stopped one tick longer and the next
evaluation of the same over-budget total retries the same write: delayed, never lost.

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
family reaches. It holds one piece of process-local state between passes — the last pass's `DerivationSignature`, a
cheap aggregate of `transcript_segments` row count, max `id`, max `received_at`, and `chunks` row count — purely to
decide whether to skip a pass. That state is never persisted and is lost on every process restart, which is harmless: a
fresh reconciler always runs its first pass in full (this is also what covers an `EXTRACTOR_VERSION` bump, since that
changes derivation markers, not this signature), and a forced floor runs a full pass at least every ten minutes by the
injected clock regardless of what the signature reports. The probe is an optimization only; correctness rests on that
floor, so a same-instant rewrite the signature happens to miss is still picked up within one floor period. Whenever a
full pass does run, it re-derives its candidates from `EventDerivationService.candidacy()` — one bulk read of the
visible segment set's stored `content_digest`s against each segment's current-version marker, with no content byte read.
A segment's digest is written by the same `transcript_segments` INSERT/UPDATE that writes its
`(turn_range_start, rejected, content)`, so it opens no write window of its own — it is exactly as durable as the row it
fingerprints.

Its two durable write paths are each one transaction: `TranscriptEventStore.replace_segment_events`, which deletes that
`(segment_id, extractor_version)` pair's rows, inserts the fresh set, and writes the marker; and `drop_segments`, one
set-scoped transaction for every segment that left the visible set, reusing the same candidacy read's
`visible_segment_ids` rather than evaluating it a second time. A crash in either path leaves a segment underived, fully
derived, or fully dropped, never half, and the next pass re-reaches it: an underived segment is still a candidate, and a
dropped-but-unnoticed one is recomputed from `derived_segment_ids()` minus the next pass's own fresh candidacy read.

Per-segment-per-version uniqueness on `(segment_id, extractor_version, kind, turn_path, occurrence)` is a store-level
unique constraint the engine enforces, not a derived cross-fact invariant the checker must recompute.

## Invocation boundaries

`invocation_boundaries` (`blizzard/src/blizzard/runner/store/schema.py`) records one durable start marker per
fleet-driven invocation — a worker spawn generation, a resume generation, a judgement, or a nudge — written by
`InvocationBoundaryStore.record_boundary_open` before that invocation's process launches, so interrupted-usage recovery
has a durable range to read even if the launch itself is the thing that crashes.

Spawn's and a plain resume's own boundary writes (`Spawner.spawn`, `DormantSession._wake`) are genuinely new pre-launch
writes, each guarded by its own registered point (`spawn.after-boundary-record.before-spawn`,
`resume.wake.after-boundary-record.before-launch`) in the family its scenario already belongs to — no new family, since
neither opens a window a fresh generic or RESUME sweep scenario does not already reach.

Judgement's and the nudge's own boundary writes take the narrower ground instead: each is its own transaction,
immediately after an *existing* pre-launch write — `record_elicitation_launch` (`Judgement._launch`) and
`record_nudge_fired` (`Judgement.run`) respectively — reached before that write's own existing crash point
(`advance.after-elicit-record.before-launch`, `nudge.after-fired-fact.before-resume`). The gap between the two
transactions is a real window, not a joined write: a crash inside it leaves the existing fact durable but no boundary.
What that loses is bounded and recoverable — recovery reads it exactly like a session with no boundary at all, a source
that answers "unmeasured" rather than a wrong answer — so it is accepted and named here (the second ground above) rather
than separately instrumented.

Closing rides `Attempt.close`, the one funnel every closure path (`abandon`, `preempt`, `fail`, and the rest) shares:
`close_boundaries_for_lease` runs BEFORE `record_closure`, so a crash between the two just re-enters this same
idempotent closure path on the next pass rather than opening a window of its own — the same ground
`_pump_lease_before_close`, sitting right beside it, already stands on. This is what answers
`bzh:open-facts-declare-closure` for a boundary a hub-terminal chunk leaves open: `Pull._reconcile_leases` calling
`Attempt.abandon` on a `STOPPED` chunk reaches the same funnel as any other closure, so no separate hub-terminal mirror
is needed. `InvocationBoundaryClosedWhenLeaseClosed` (`blizzard/src/blizzard/tools/invariants.py`) is the checker
assertion this closure obligation earns.
