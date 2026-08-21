# Crash correctness

MVP acceptance criterion 4 promises that `kill -9` at every step boundary is **a tested operation, not a hope**. That
promise imposes four requirements on daemon code — built in from the first commit, because each is cheap on day one and
expensive to retrofit. Crash correctness is an orthogonal dimension, not a fifth test tier
([../verification/blizzard.md](../verification/blizzard.md)): the requirements below are *architecture*; the kill-9
sweep that exercises them is a verification method (`blizzard:crash-sweep`) in the matrix. Each rule follows the slot
skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## A steppable loop (`bzh:steppable-loop`)

**Rule.** The daemon loop's phases — the runner's REAP, PULL, FILL, ADVANCE, and the hub's coordinator loop — are
individually callable step functions, each a pure function of (store, clock, seam clients); the tick timer is merely one
driver of them.

**Why.** Tests drive the same step functions directly, one at a time, stopping exactly at a boundary — which is how
boundary-order and recovery logic get cheap in-process coverage and how the sweep arms a precise crash point. A loop
welded to its timer can only be tested by waiting on wall-clock ticks and cannot be stopped mid-step.

**Detect.** Loop phases reachable only through the tick timer or a `while True`; a step that reads the clock or a seam
from a module global rather than its parameters.

**Do.** `def fill(store, clock, seams) -> None` callable standalone; the tick driver calls `reap`, `pull`, `fill`,
`advance` in turn.

**Don't.** A single `tick()` that inlines all four phases with no separately callable boundary — no test can stop
between FILL and ADVANCE.

## An injected clock (`bzh:injected-clock`)

**Rule.** All time flows through a clock abstraction wired at the composition root (`bzh:dependency-injection`); no
direct `time.time()` / `datetime.now()` appears in loop, store, or domain code — **including SQLAlchemy column
defaults**.

**Why.** An injected clock lets tests advance time virtually, so lease TTLs, reap staleness thresholds, and an
"overnight" wait pass in milliseconds and deterministically; a direct `datetime.now()` anywhere — especially a column
default — reintroduces wall-clock non-determinism the sweep cannot control.

**Detect.** `datetime.now()`, `datetime.utcnow()`, `time.time()`, or `func.now()` / `server_default=func.now()` in loop,
store, domain, or model code; a timestamp written from anything but the injected clock.

**Do.** The clock is injected; timestamps come from `clock.now()`, and column values are set by the writing code from
that clock — not by a database default.

**Don't.** `created_at = Column(DateTime, default=datetime.utcnow)` — the store now stamps wall-clock time the virtual
clock can't move.

## A crash-point registry (`bzh:crash-point-registry`)

**Rule.** The dangerous windows carry stable names in a code-owned, **enumerable** registry — e.g.
`fill.after-env-acquire.before-claim`, `advance.after-buffer.before-flush`, `hubnode.after-step.before-marker`,
`reap.after-kill.before-expire`; under test scaffolding a daemon subprocess SIGKILLs itself on reaching the armed point,
selected via an environment variable and fenced so it can never fire outside a test-marked environment. The segment
before the point's first `.` is the **boundary family** the sweep partitions the registry on — it resolves which
scenario (the generic `build → deliver` sweep, or a dedicated scenario such as `resume.`, `abandon.`, `pause.`,
`hubnode.`) is the one that arms and reaches that point — so name a point for the boundary its reaching scenario opens,
never for the step whose source happens to call `.reached()`.

**Why.** An enumerable registry is what the sweep iterates — one run per armed point — and it doubles as the
authoritative list of windows the design claims are safe, so a newly-introduced dangerous window is a registry entry,
not a silent gap. The family prefix is what routes a point to the scenario that actually reaches its window, so naming
it for the wrong family leaves the registry entry with no real coverage behind it.

**Detect.** A crash-recovery claim about a window with no corresponding registry entry; a self-kill hook not gated
behind the test-environment fence; crash points hard-coded in the test rather than enumerated from the registry; a new
point prefixed with a family that already has coverage from an unrelated sibling point, when the point's own window only
opens under a dedicated scenario — the family-coverage check passes on the sibling's strength while the new point's
window goes unswept.

**Do.** Add the window's stable name to the registry, prefixed for the scenario that reaches it —
`pause.after-kill.before-park`, not `pull.after-pause-kill.before-park`, even though the call site sits inside the PULL
step's code; the sweep enumerates the registry and arms each in turn; the daemon self-kills only when the test fence is
set.

**Don't.** Assert a window is crash-safe in prose without a registry entry the sweep can arm — the claim is untested.
Prefix a new point `pull.after-pause-kill.before-park` because that's where its `.reached()` call sits, instead of
`pause.after-kill.before-park` for the scenario whose window it actually guards.

### Recorded exemptions — durable state with no dangerous window

Not every durable write opens a window this registry must name; a write with **no unsafe partial-write window** has
nothing to arm, and that must be a *stated* position, not an implicit one (the "Don't" above bars asserting a window
*safe without arming it* — this is the distinct case of there being *no window at all*). Record such a decision here
when a change adds durable state that a reviewer would otherwise expect a sweep point for:

- **The runner's jti replay cache (issue #95).** The runner-store table `jwt_jti_seen(jti PK, aud, expires_at)` backs
  single-use of a hub-signed federation JWT across a restart within the 60s token window. Its "check-not-seen → insert →
  mint session" path is **one transaction under the `jti` primary key**, so no interleaving admits a replay: a crash
  *after* the insert but *before* the session mint loses only the runner-domain session, forcing a fresh, harmless
  re-bounce through the hub (a liveness annoyance, never a safety break — the row that would reject a replay is already
  durable). There is therefore **no `bzh:crash-point-registry` entry** for it, and **no new `bzh:invariant-checker`
  assertion**: jti uniqueness is a store-level PK constraint the engine enforces, not a derived cross-fact invariant the
  checker must recompute. This cache is not a loop step, so the loop-driven sweep families never reach it, and correctly
  so.

- **The runner's git-commit verify (issue #143, Phase 4).** The worker pushes its branch and declares it; ADVANCE's own
  git surface is a **read-only** re-derivation (`git ls-remote` against the origin the environment's repo manifest
  names) of a fact already durable in the `git_commit_declarations` table — it never pushes
  (`bzh:git-write-in-worker-seam`, [./system-shape.md](./system-shape.md)). A read `kill -9` at any point simply loses
  nothing durable — the declaration survives untouched, and the very next ADVANCE pass re-reads and re-verifies it from
  scratch, converging on the same result every time. There is therefore **no `bzh:crash-point-registry` entry** for this
  window: the registry no longer names `advance.before-artifact-push` / `advance.after-artifact-push.before-judgement`
  (the mutation window a runner-side push used to open), and neither does the bounded CI subset or the
  `test_ci_subset_covers_every_family` family-coverage list — `advance.` keeps its other members' coverage, so the
  family is not orphaned by their absence.

- **The runner's operational-event emission (issue #125, change K/L).** The runner surfaces its
  operationally-significant failures as `event.recorded` facts that ride the *existing* outbound buffer — exactly-once
  delivery is already held by the buffer's gapless-seq invariant and the hub's per-runner high-water mark, machinery the
  sweep and the checker already cover. The `Attempt.fail` retry/escalate events are enqueued **in the same transaction
  as the closure they describe** (the `record_local_pause`/`record_usage` atomic local+outbound precedent), so no
  partial-write window exists there. The one deliberately non-atomic emission — the reassign-**abandon** branch, whose
  closure lives one level down in the shared `Attempt.abandon` (plan-findings SF-6) — is still safe with **no arming
  needed**: an operational event is informational and append-only, and at-most-once-per-attempt is *structural*
  (`Attempt.fail` runs once per attempt — it closes/requeues/escalates the lease, so the next tick sees a different
  lease state, needing no durable guard fact), so a `kill -9` between that closure and its enqueue at worst loses one
  informational event that the next attempt's failure re-emits. There is therefore **no new `bzh:crash-point-registry`
  entry** and **no new `bzh:invariant-checker` assertion**: no new durable guard, no new dangerous window, and no new
  cross-fact invariant — the same shape as the #95 jti exemption above.

- **The runner's per-session preamble fingerprint (issue #149).** The runner-store table `session_preamble_facts`
  records, per harness session, a digest of the standing spawn-preamble prose that session was last sent, so a resumed
  spawn can skip an unchanged layer and announce a changed one. The write sits inside the SPAWN step, immediately after
  `record_spawn` — a position a reviewer would reasonably expect a sweep point for — but it lands **after the spawn call
  returns**, so a durable fingerprint always implies the prose actually reached the process. A `kill -9` that loses it
  leaves the session with no fingerprint, and the next resume reads `None` and renders all three layers in full:
  precisely the pre-issue-#149 behavior, a token cost rather than a safety break. The reverse order cannot mislead
  either — the fingerprint is keyed on the session, and the process had already received the prose before either write
  ran. There is therefore **no `bzh:crash-point-registry` entry** for it and **no new `bzh:invariant-checker`
  assertion**: no new durable guard, no new dangerous window, and no new cross-fact invariant — the same shape as the
  #95 jti and #125 event-emission exemptions above.

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
  shape as the #95 jti, #125 event-emission, and #149 preamble-fingerprint exemptions above.

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
  jti, #125 event-emission, #149 preamble-fingerprint, and #137 promote-then-tail-stamp exemptions above.

- **The hub's marker-write capability token (issue #230).** `MarkerAuthority`
  (`src/blizzard/hub/delivery/marker_auth.py`) mints an in-memory, process-scoped token per
  `(chunk_id, node_id, epoch)`, immediately before that hub-node step's `run:` commands execute, and revokes it in a
  `finally` once the step's visit is done with it — never persisted, a fact a reviewer might otherwise expect a
  `bzh:crash-point-registry` window for, since the token gates a marker write that is itself durable. A `kill -9`
  mid-step orphans the land script it spawned, leaving that script holding a token minted by a process that no longer
  exists: its later marker-write POSTs then fail, verified against the restarted process's fresh, empty authority. That
  is safe, not a gap — the executor's at-least-once-per-step contract (`bzh:hub-node-step-idempotence` in
  [../standards/hub-nodes.md](../standards/hub-nodes.md)) re-runs that exact step from its own first command on the next
  hub-advance, minting a fresh token and re-recording the marker idempotently; no crash-sweep assertion depends on an
  orphan's rejected write landing. There is therefore **no `bzh:crash-point-registry` entry** for it and **no new
  `bzh:invariant-checker` assertion**: the token is in-memory, credential-shaped state with no durable form and no
  partial-write window of its own — the same shape as the #95 jti, #125 event-emission, #149 preamble-fingerprint, #137
  promote-then-tail-stamp, and #216 delivery-closure-sweep exemptions above.

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
  delivery-closure-sweep, and #230 marker-token exemptions above.

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
  budget-breach windows degrade rather than break, matching the #137/#216/#230 exemptions above, and the last two are
  named, accepted gaps, recoverable by inspection rather than automatic retry, not windows this repo claims to have no
  exposure to at all.

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
  marker-token exemptions above. The verb additionally refuses to run at all while a daemon holds the runtime's socket,
  so it never races the loop for the single-writer store.

- **The runner's escalation closures (blizzard#292).** `Pull._reconcile_escalations`
  (`blizzard/src/blizzard/runner/loop/steps.py`) appends one `escalation_closures` row per open local escalation whose
  chunk the hub reports `stopped` — new durable state written from a loop step, and written *before*
  `pull.before-flush`, a position a reviewer would reasonably expect a sweep point for. There is no dangerous window.
  The write is a lone insert in its own transaction with nothing to pair it with atomically: unlike the context-sample
  row above it enqueues no companion fact, because the closure is a purely local mirror of something the hub already
  holds — the hub's own `chunk.stopped` fact is what the two sides agree on, and this row only saves the runner from
  re-deriving it. A `kill -9` before it commits leaves the escalation open, and the next tick re-reads the same
  still-stopped chunk and writes the same mark, converging on the identical state; a `kill -9` after it commits has
  already reached the intended one. A crash that somehow admitted the row twice is equally harmless: the read is an
  `Unsuperseded` existence test, so N marks for a chunk read exactly as one. Nothing gates a spawn or a claim on the
  table — it suppresses a display read (`open_escalations`) and the `runner requeue` guard, never work admission — so a
  lost or duplicated row costs at most one tick of a stale panel row. There is therefore **no `bzh:crash-point-registry`
  entry** for it and **no new `bzh:invariant-checker` assertion**: no new durable guard, no new dangerous window, and no
  new cross-fact invariant — supersession is an ordering comparison over append-only rows, not a derived invariant to
  recompute — the same shape as the #95 jti, #125 event-emission, #149 preamble-fingerprint, #137
  promote-then-tail-stamp, #216 delivery-closure-sweep, #230 marker-token, and blizzard#250 backfill exemptions above.

- **The runner's takeover closures (issue #291).** `Pull._reconcile_takeovers`
  (`blizzard/src/blizzard/runner/loop/steps.py`) appends one `takeover_ends` row per open takeover whose chunk the hub
  reports terminal — new durable state written from a loop step, and written *before* `pull.before-flush`, a position a
  reviewer would reasonably expect a sweep point for. There is no dangerous window, but on a narrower ground than the
  blizzard#292 escalation-closure sibling above: unlike that write, this one is not purely a local display mirror — the
  fact it closes gates REAP's and ADVANCE's per-tick skip of a taken-over chunk (`loop/steps.py:157-158`, `:406-407`,
  `:425-426`) and, since the worker-authorization resolver this same change adds, a resumed session's own worker-verb
  reach — so its correctness matters, not merely its freshness, and this entry does not lean on #292's "gates no work
  admission" clause to justify skipping the registry. It is still safe with no window to arm: the write is a lone
  idempotent insert in its own transaction, with nothing to pair it with atomically — the exact `record_takeover_end`
  call the CLI's own end-PATCH already makes on the ordinary hand-back path, so this is a second caller of an existing,
  already-idempotent write, not a new write shape. A `kill -9` before it commits leaves the takeover open, and the next
  tick re-reads the same still-terminal chunk and writes the same mark, converging on the identical state; a `kill -9`
  after it commits has already reached the intended one. A crash that somehow admitted the row twice is equally
  harmless: `OPEN_TAKEOVER` is an `Unclosed` existence test (a plain `NOT IN`), so N marks for one takeover id read
  exactly as one — and the CLI's own end-PATCH is idempotent for the same reason, so the two closers racing each other
  is exactly this safe-twice case, never a conflicting write. There is therefore **no `bzh:crash-point-registry` entry**
  for it and **no new `bzh:invariant-checker` assertion**: closure-by-`NOT IN` is a plain existence comparison over an
  append-only table, not a derived cross-fact invariant to recompute — the same shape as the #95 jti, #125
  event-emission, #149 preamble-fingerprint, #137 promote-then-tail-stamp, #216 delivery-closure-sweep, #230
  marker-token, blizzard#250 backfill, and blizzard#292 escalation-closure exemptions above.

- **The runner's live session-context samples.** `ContextSample` (`blizzard/src/blizzard/runner/loop/steps.py`) appends
  one `context_samples` row per sampled reading of a running lease's session context, and on a first crossing of the
  configured `[context] warn_tokens` enqueues an `event.recorded` fact in the **same transaction** as the row
  (`record_context_sample`) — new durable state plus a new outbound enqueue, a position a reviewer would reasonably
  expect a sweep point for. There is no dangerous window in either half. The table is append-only, purely observational,
  and read by exactly one caller, the sampler's own cadence-and-dedupe state (`context_sample_state`): nothing derives a
  status from it, no spawn is gated on it, and losing a row costs one point on a diagnostic curve that the next interval
  re-samples. The atomic pairing is what makes the crossing report safe rather than merely cheap — a warning buffered
  without its row would re-fire every tick, and a row without its warning would suppress the warning permanently, so the
  two must land together and do. A `kill -9` before the transaction commits loses the sample and the warning alike, and
  the next tick re-reads the same still-over-line transcript and re-emits both. Beyond the buffer, exactly-once delivery
  is already held by the gapless-seq invariant and the hub's high-water mark, and the event itself is informational and
  append-only — the #125 event-emission shape exactly. There is therefore **no `bzh:crash-point-registry` entry** for it
  and **no new `bzh:invariant-checker` assertion**: no new durable guard, no new dangerous window, and no new cross-fact
  invariant — the same shape as the #95 jti, #125 event-emission, #149 preamble-fingerprint, #137
  promote-then-tail-stamp, #216 delivery-closure-sweep, #230 marker-token, and blizzard#250 backfill exemptions above.

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
  marker-token, and blizzard#250 backfill exemptions above.

- **The runner's graph-artifact mirror write.** `Spawner._mint` (`blizzard/src/blizzard/runner/loop/spawn.py`) records
  the pinned mint's graph-scope declarations into the runner's own `graph_artifacts` table, insert-if-absent keyed on
  `graph_id`, immediately before `record_lease` — a position a reviewer would reasonably expect a sweep point for, since
  the write lands ahead of the lease it exists to serve. There is no dangerous window, and what closes it is that the
  presence check and every insert behind it are **one transaction**: a mint's declarations land all or none, so the
  `graph_id`-granular check can never read a half-written set as a complete one and skip the remainder for the mint's
  whole life. A `kill -9` between the two writes therefore leaves only a complete orphan set keyed to an immutable mint,
  and the retry that re-attempts the mint writes the identical rows again — insert-if-absent makes the retry a no-op
  past the first success — before it reaches `record_lease` a second time. No lease **this path mints** can therefore
  hold a mint whose declarations are absent or partial, and no crash ever loses a row such a lease depends on. There is
  therefore **no `bzh:crash-point-registry` entry** for it and **no new `bzh:invariant-checker` assertion**: the row is
  a durable fact about an immutable mint, never revised once written, so read-after-crash agreement is structural rather
  than a cross-fact invariant to recompute — the same shape as the jti-replay and the other durable-fact exemptions
  above.

  The guarantee reaches exactly as far as the mint, and the window past it is **accepted, not repaired**. A lease
  already in flight when the runner restarts resumes through `Spawner.preamble` — from `Dormant._wake` and
  `Judgement._elicit` — which re-mints only the capability token and never re-enters `_mint`, so a lease carried across
  a deploy that introduces this write is resumed without ever acquiring a pin;
  `IReadRunnerStore.graph_artifacts_for_graph` (`blizzard/src/blizzard/runner/store/repository.py`) states the same
  thing from the read side, reading empty for a mint pinned before the runner ever recorded one. Three properties bound
  it. Only leases live across the upgrade are affected. The two verbs that serve graph scope answer that empty pin
  differently (`blizzard/src/blizzard/runner/api/artifacts.py`): `artifact list --scope graph` returns the empty set,
  the same answer a graph declaring nothing gives, while `artifact get <name> --scope graph` is a `404` naming the
  pinned mint, which the worker CLI raises as a `ClickException` (`blizzard/src/blizzard/runner/cli_worker.py`) — a
  non-zero exit with the miss on stderr, not an empty answer. And it self-heals, since the presence check is keyed on
  `graph_id` — the next mint against that graph writes the whole set, which the still-running lease then reads through
  its own `graph_id` like any other.

  A named command failure rather than an empty answer is what the acceptance rests on, and it holds: no engine code path
  reads a graph declaration at all — the runner's only reader is that worker-facing route — so no admission, routing,
  epoch, or completion decision can observe the window, and the one reader that can is a worker mid-turn, for which a
  failure it can see and name is something to act on rather than a wrong answer to proceed from. What carries it through
  is the fallback every prompt pointing at a graph declaration owes (`bzh:graph-artifact-pointer-fallback`,
  [../standards/worker-nodes.md](../standards/worker-nodes.md)), which is written against a failed read and not only an
  empty one. Should a graph-scope read ever become something the engine gates on, the window turns from accepted into a
  repair: no fallback in authored prose can stand in for a decision the engine makes for itself. Backfilling on resume
  would close only the stretch before that next mint, and would buy it by making a second call site write a table whose
  sole writer being the mint is what the paragraph above rests on.

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
  a derived cross-fact invariant to recompute — the same shape as the durable-fact exemptions above, minus the jti
  exemption's particular mechanism.

## A facts-level invariant checker (`bzh:invariant-checker`)

**Rule.** A checker of assertions evaluated over both stores' facts after any crash → restart → recover cycle holds the
durable invariants: no duplicate env binding, at most one accepted transition per node-step epoch, no double delivery
with per-repo lands idempotent and per-repo `pr.opened` idempotent, every derived status computable with exactly one
match, a gapless outbound-buffer sequence, and usage attributed exactly once per `(lease, generation, kind)`.

**Why.** Because both stores are facts-only (`bzh:facts-not-status`), the checker is essentially a library of SQL
assertions plus the status-derivation queries themselves — and a failure names the exact violated invariant rather than
a vague corruption. It is the assertion the sweep runs after every armed crash, alongside the scenario's own expected
outcome.

**Detect.** A crash test that asserts only "the process restarted" or "the chunk eventually landed" without checking the
facts-level invariants; a new durable invariant added to the design with no assertion in the checker.

**Do.** After restart-and-recover, run the checker's SQL assertions over both stores; a violation reports which
invariant broke.

**Don't.** Rely on the scenario's happy-path outcome alone — a double-delivery or duplicate-binding bug can leave the
chunk looking landed while an invariant is silently violated.

## See also

- [./system-shape.md](./system-shape.md) — `bzh:facts-not-status` and `bzh:deterministic-shell`, the invariants these
  requirements rest on.
- [../verification/blizzard.md](../verification/blizzard.md) — `blizzard:crash-sweep`, the method that composes the four
  requirements into the criterion-4 proof, and the division of labor with the unit and component tiers.
