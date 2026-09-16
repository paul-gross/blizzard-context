# Crash-correctness exemptions — runner writes (`bzh:crash-exemptions-runner`)

This register records, for each of the runner's own durable writes outside the transcript lane, which of the two grounds
[`../crash-correctness.md`](../crash-correctness.md) admits — no window at all, or a real window whose whole loss is
accepted and named — exempts it from `bzh:crash-point-registry`, and what stands in for a sweep point instead. That file
owns the registry, the invariant checker, and the obligation to record a decision here; a runner write inside the
transcript lane is recorded in [`./transcripts.md`](./transcripts.md) instead.

## The jti replay cache

The runner store's `jwt_jti_seen(jti PK, aud, expires_at)` table (`blizzard/src/blizzard/runner/store/schema.py`) keeps
a hub-signed federation JWT single-use across a runner restart inside the token's 60-second validity window. Its
check-not-seen, insert, and mint-session sequence is one transaction under the `jti` primary key, so no interleaving
admits a replay.

A crash after the jti row commits but before the session is minted loses only the runner-domain session: the row that
rejects a replay is already durable, so the forced re-bounce through the hub is harmless. The write owes the invariant
checker nothing, because uniqueness there is a primary-key constraint the engine enforces rather than a cross-fact
invariant to recompute.

## Git-commit verify

ADVANCE's git surface only re-derives, read-only, what the worker already made durable: the worker pushes its branch and
declares it into `git_commit_declarations` (`blizzard/src/blizzard/runner/store/schema.py`), and ADVANCE runs
`git ls-remote` against the origin the environment's repo manifest names. ADVANCE never pushes, because git mutation
belongs to the worker seam (`bzh:git-write-in-worker-seam`,
[`../system-shape/worker-boundary.md`](../system-shape/worker-boundary.md)).

A `kill -9` anywhere in the git verify loses nothing durable, and the next ADVANCE pass re-reads and re-verifies the
declaration from scratch, converging on the same result every time.

## Event emission

The runner surfaces its operationally-significant failures as `event.recorded` facts riding the outbound buffer that
already exists. An event riding that buffer inherits exactly-once delivery from the buffer's gapless-sequence invariant
and the hub's per-runner high-water mark, machinery the sweep and the checker already cover.

`Attempt.fail`'s retry and escalate events are enqueued in the same transaction as the closure they describe, on the
atomic local-plus-outbound precedent of `record_local_pause` and `record_usage`, so that branch opens no partial-write
window. The reassign-abandon branch is deliberately non-atomic, its closure sitting one level down in the shared
`Attempt.abandon`, and still needs no armed crash point: at-most-once-per-attempt is structural, since `Attempt.fail`
runs once per attempt and closes, requeues, or escalates the lease, leaving the next tick a different lease state and no
need of a durable guard fact. A crash between the abandon closure and its enqueue loses at most one informational,
append-only event, which the next attempt's failure re-emits.

`Attempt.escalate_owner_unresolvable`'s own `owner-unresolvable` event rides the identical `close` call `Attempt.fail`'s
branches already do, so it inherits the same atomic guarantee and needs no entry of its own beyond this one.

## The preamble fingerprint

The runner store's `session_preamble_facts` table (`blizzard/src/blizzard/runner/store/schema.py`) holds, per harness
session, a digest of the standing spawn-preamble prose that session was last sent, so a resumed spawn can skip an
unchanged layer and announce a changed one. The fingerprint write sits inside the SPAWN step immediately after
`record_spawn` but lands only after the spawn call returns, so a durable fingerprint always implies the prose actually
reached the process.

A crash that loses the fingerprint leaves the next resume reading `None` and rendering all three preamble layers in
full, a token cost rather than a safety break.

## The escalation and takeover closures

`Pull._reconcile_escalations` (`blizzard/src/blizzard/runner/loop/steps.py`) appends one `escalation_closures` row per
open local escalation whose chunk the hub reports `stopped`, durable state written from a loop step ahead of
`pull.before-flush`. `Pull._reconcile_takeovers` (same module) appends one `takeover_ends` row per open takeover whose
chunk the hub reports terminal, likewise written from a loop step ahead of `pull.before-flush`. Each of the two closure
writes is a lone insert in its own transaction, with nothing to pair it with atomically.

A crash before either closure commits leaves the escalation or takeover open, and the next tick re-reads the same
still-stopped or still-terminal chunk and writes the same mark; a crash after it commits is already at the intended
state. Nothing gates a spawn or a claim on `escalation_closures` — it suppresses a display read (`open_escalations`) and
the `runner requeue` guard, never work admission — so a lost or duplicated row costs one tick of a stale panel row. The
escalation closure is also a purely local mirror of a fact the hub already holds: the hub's own `chunk.stopped` fact is
what the two sides agree on, and the row only spares the runner re-deriving it.

The takeover closure rests on narrower ground, because its correctness matters rather than its freshness: the
open-takeover fact gates REAP's and ADVANCE's per-tick skip of a taken-over chunk, and a resumed session's worker-verb
reach through the worker-authorization resolver. `record_takeover_end` is the same call the CLI's end-PATCH already
makes on the ordinary hand-back path, so the loop's closure is a second caller of an existing idempotent write. A
closure row admitted twice is equally harmless — `escalation_closures` reads through an `Unsuperseded` existence test
and `OPEN_TAKEOVER` through an `Unclosed` plain `NOT IN`, so N marks read as one — which is also why the loop and the
CLI's end-PATCH racing to close one takeover is safe rather than conflicting.

Neither closure table owes the invariant checker anything: supersession is an ordering comparison and
closure-by-`NOT IN` an existence comparison, both over append-only rows, not derived cross-fact invariants.

## Context samples

`ContextSample` (`blizzard/src/blizzard/runner/loop/steps.py`) appends one `context_samples` row per sampled reading of
a running lease's session context, and on a first crossing of the configured `[context] warn_tokens` enqueues an
`event.recorded` fact in the same transaction as the row (`record_context_sample`). Pairing the sample row with its
warning atomically is what makes the crossing report correct rather than merely cheap: a warning buffered without its
row would re-fire every tick, and a row without its warning would suppress the warning permanently.

`context_samples` is append-only and purely observational, read only by the sampler's own cadence-and-dedupe state
(`context_sample_state`), so no status derives from it, no spawn is gated on it, and a lost row costs one point on a
diagnostic curve the next interval re-samples.

## Retention pruning

`Retention` (`blizzard/src/blizzard/runner/loop/steps.py`) runs three prunes every tick, one per append-only lane with
no retention policy of its own before now: `prune_outbound` deletes an acked `outbound_buffer` row past its window but
only below the lowest still-pending seq, and `prune_heartbeats` / `prune_external_usage_samples` each compact their
table to every lease's or slug's newest row past a shorter window. Each prune is one `DELETE` statement in its own
transaction, so a `kill -9` anywhere around it leaves the table exactly as it was before the statement or exactly as it
would be after — never a partially-applied delete. That is a **no-window** write: there is no second half a crash could
separate it from, and so no `bzh:crash-point-registry` entry is owed.

None of the three can delete a row a live reader still depends on. The outbound prune's pending-floor check keeps every
row a still-open fact might need; the heartbeat and usage-sample prunes keep each lease's or slug's newest row
unconditionally, which is the only row `latest_heartbeat` and `last_external_usage_attempt_at` ever read — so a crash
losing the retried prune's effect costs nothing beyond a few more rows lingering until the next tick's pass, never a
wrong answer from either read. `Retention.run` also isolates each lane's own prune in its own `try`/`except`, so one
lane raising costs that lane's pass, not the tick's other two.

## The graph-artifact mirror

`Spawner._mint` (`blizzard/src/blizzard/runner/loop/spawn.py`) records a pinned mint's graph-scope declarations into the
runner's own `graph_artifacts` table, insert-if-absent keyed on `graph_id`, immediately before `record_lease` — ahead of
the lease those rows exist to serve. The presence check and every insert behind it are one transaction, so a mint's
declarations land all or none and the `graph_id`-granular check can never mistake a half-written set for a complete one
and skip the remainder for that mint's life. A crash between the artifact write and `record_lease` leaves at most a
complete orphan set keyed to an immutable mint, and the retried mint writes identical rows, insert-if-absent making the
retry a no-op past the first success. A `graph_artifacts` row owes the checker nothing because it is a durable fact
about an immutable mint, never revised once written, so agreement between readers after a crash is structural.

The pin guarantee reaches exactly as far as the mint, and the window past it is accepted rather than repaired. A lease
already in flight resumes through `Spawner.preamble`, which re-mints only the capability token and never re-enters
`_mint`, so a lease whose mint predates any recorded rows resumes on an empty pin — the emptiness
`IReadGraphArtifactRepository.graph_artifacts_for_graph` (`blizzard/src/blizzard/runner/domain/artifacts.py`) reports
from the read side. No engine code path reads a graph declaration at all — the runner's only reader is that
worker-facing route — so no admission, routing, epoch, or completion decision can observe the window. An empty pin fails
by name rather than answering emptily: `artifact get <name> --scope graph` is a `404` naming the pinned mint, which the
worker CLI raises as a non-zero `ClickException` (`blizzard/src/blizzard/runner/api/artifacts.py`,
`blizzard/src/blizzard/runner/cli_worker.py`). What carries a worker through an empty pin is the fallback every prompt
pointing at a graph declaration owes (`bzh:graph-artifact-pointer-fallback`,
[`../../standards/worker-nodes/graph-artifact-pointers.md`](../../standards/worker-nodes/graph-artifact-pointers.md)),
which is written against a failed read and not only an empty one.

Should a graph-scope read ever become something the engine gates on, this accepted window turns into a repair owed,
because no fallback in authored prose can stand in for a decision the engine makes for itself.

## The elicitation relaunch record-before-launch gap

`Judgement._relaunch` (`blizzard/src/blizzard/runner/loop/judgement.py`) re-launches a detached verdict elicitation
whose prior attempt exited without writing anything readable — the loss-recovery counterpart to the ordinary first
launch, whose own record-before-launch gap earns the `advance.after-elicit-record.before-launch` /
`advance.after-elicit-launch` registry points because the generic sweep scenario reaches it on every ordinary judgement.
A relaunch's own gap does not: it opens only once a prior elicitation has already been launched, exited, and left an
unreadable output file — a condition the generic scenario never creates, so `bzh:crash-point-registry`'s family-coverage
concern applies and this write earns a recorded decision instead of a dedicated family.

A `kill -9` between `record_elicitation_relaunch` (pid cleared, a fresh `output_path`, `relaunch_count` incremented) and
the new process actually starting leaves the in-flight record with `pid` unset — the same shape `Judgement.collect`
already reads as "not running" on every ordinary poll. The next `Judgement.collect` pass over this lease therefore reads
the still-empty output at the new path, finds no running process, and calls `_lost` again: it relaunches once more if
under the staleness bound, or fails the attempt if past it — the exact recovery a live relaunch takes, replayed. The
write earns **no window at all**: its halves are independently harmless, because the record's own read path already
treats an unset pid as "not yet running" rather than as evidence a process must exist, so nothing downstream needs the
two writes to have landed atomically. The one cost a crash in this gap can add is one extra wasted relaunch attempt
should the killed process have actually started before the crash — bounded by the same staleness threshold
(`ELICITATION_STALENESS_THRESHOLD`, 15 minutes) every ordinary relaunch already accepts, and never durable in
consequence since the orphaned attempt's own output file is simply never read once a newer `output_path` supersedes it.

## The elicitation-clear-after-collect ordering

`Judgement.collect` (`blizzard/src/blizzard/runner/loop/judgement.py`) clears the in-flight elicitation record, and
sweeps its output files, only AFTER a collected reply is fully processed — never before. Clearing first would open two
windows. A crash between the clear and `_judged` completing would leave a lease with no elicitation record and no
buffered outcome, re-entering the ordinary judge path and launching a **second, redundant** elicitation — a second model
turn spent on a verdict already in hand, and one the usage ledger cannot show, since `judge` usage is keyed
`(lease, generation, kind)` and a judge elicitation opens no new generation, so the ledger ends with one `judge` fact
either way. And a staleness-exceeded branch that cleared the record before calling `Attempt.fail` would let a crash in
that gap silently reset the never-resettable staleness baseline on the next pass's fresh `_launch`.

The first window is closed by ordering, not by a registry point: `collect` clears the record and sweeps the files only
once `_judged` returns. The second is narrowed rather than closed: the staleness-exceeded branch calls `Attempt.fail`
directly, which kills and clears the record itself as one link in its own closing sequence — no separate write of
`collect`'s own precedes it — so the only span left is inside `Attempt.fail`
(`blizzard/src/blizzard/runner/loop/attempt.py`), from the elicitation record's clear to the lease's closure — a span
the locally-paused escalation deferral, which returns without closing, never ends at all. A crash in that span, or that
deferral lifting, lands the lease back in the ordinary judge path with no elicitation record, so at most one elicitation
is spent again, on a fresh baseline, from a point the staleness bound was already past. That is the accepted-loss
ground: the loss is one re-spent elicitation, tolerable because it is bounded by the same threshold and self-healing on
the next pass, and its only durable trace is the `elicitation past its staleness bound — failing attempt` warning the
failing pass logs — the usage ledger cannot show it, because a killed elicitation books no `judge` fact and the fresh
one records the generation's only `judge` sample. It is not a fresh window `bzh:crash-point-registry` owes a point to.

## The unresolvable-pool-owner escalation mint

`Spawner._escalate_unresolvable_resume_owner` (`blizzard/src/blizzard/runner/loop/spawn.py`) mints a zero-budget,
never-spawned lease purely to give `Attempt.escalate_owner_unresolvable`
(`blizzard/src/blizzard/runner/loop/attempt.py`) an existing lease to close, when an existing recorded session's owner
cannot be dispatched to at node entry — a named pool's head, or a plain, un-pooled resume's own latest session alike;
`SessionResolver.resolve_resume` surfaces both shapes through the same `ResumeTarget.owner_unresolvable`, so
`enter_node` routes both through this one mint. Between that mint's own `record_lease` and the escalation's own closure
landing, the lease sits exactly as any other post-mint, pre-spawn lease does, so `_CP_AFTER_MINT`
(`spawn.after-lease-mint.before-spawn`) is reused rather than duplicated: a `kill -9` here leaves the identical "lease
minted; worker not spawned" shape a `HarnessSpawnError`'d ordinary mint already leaves, which the sweep's generic
`spawn.` family coverage already exercises structurally. No distinct crash point is warranted — the window is not new,
only a new caller of one already armed.

A crash in that window is recovered by REAP's ordinary orphan sweep (`Reap.run`,
`blizzard/src/blizzard/runner/loop/steps.py`): any lease with no recorded pid or session is `Attempt.fail`'d regardless
of why it was minted. This lease's session is `None` (never spawned), so `_owner_block` finds nothing to short-circuit
the retry check on; its `retries_max` is pinned to `0`, so `retried (0) < retries_max (0)` is false and the retry branch
never fires; the ordinary exhausted-retries path runs, closing `ESCALATED` and calling `escalate()` — composing no
takeover, the same "escalated before any worker session existed" shape any other never-spawned lease reaches. A later
re-entry of the same node — this same `enter_node` call replayed, or a genuine post-recovery retry — costs nothing
beyond `open_escalation_for_chunk`'s own read: an already-open escalation short-circuits
`_escalate_unresolvable_resume_owner` before it mints again, and supersession (a later lease minted for the chunk) is
the only way that escalation ever closes.

The synchronous, no-crash path closes this same mint through `escalate_owner_unresolvable` directly rather than through
`fail`, so it takes that method's own detached/paused precedence (mirroring `fail`'s) instead: a chunk the hub no longer
routes here abandons the mint in place rather than escalating it, and a runner paused between the mint above and this
close leaves the lease open for REAP's same orphan sweep to resolve, exactly as the crash case above already does.

D12 (blizzard#432) gives this same pattern a second entry point: `Spawner.escalate_no_acceptable_harness` /
`Attempt.escalate_no_acceptable_harness`, reached when a fresh mint's `HarnessSelector` exhausts the node's acceptable
harness set with nothing servable, and from `Attempt.requeue`'s own membership guard — a retry whose lease's owner has
fallen out of a since-edited acceptable set, never a candidate to resume under. Its `_mint` call passes
`harness_id=None`, the same escalation-only mode `_escalate_unresolvable_resume_owner`'s call never needs: no owner is
chosen, so no stamps resolve (model, effort, and compaction window all land `None`) and no mint owner is recorded,
leaving `leases.harness_id` at its already-nullable unset value. It shares this section's whole crash-correctness
account otherwise: the same `_CP_AFTER_MINT` window, the same REAP recovery through the ordinary exhausted-retries path
(a zero-budget lease with no session composes no takeover, same as any other never-spawned lease), and the same
`open_escalation_for_chunk` guard ahead of the mint, so a chunk already escalated this way cannot loop a second mint on
top of the first.
