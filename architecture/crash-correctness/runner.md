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
unchanged layer and announce a changed one. `Spawner.spawn` (`blizzard/src/blizzard/runner/lifecycle/spawn.py`) is the
only caller: the fingerprint write sits inside the SPAWN step immediately after `record_identified_spawn`, once the
launched process's identity is durable, but lands only after the spawn call itself returns, so a durable fingerprint
always implies the prose actually reached the process. A dormant session's own wake
(`blizzard/src/blizzard/runner/lifecycle/dormant.py`) resumes the same session through `record_spawn` instead,
delivering a short wake message rather than a re-rendered preamble, so that path never reads or writes this table at
all.

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
and `_OPEN_TAKEOVER` through an `Unclosed` plain `NOT IN`, so N marks read as one — which is also why the loop and the
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

`Retention` (`blizzard/src/blizzard/runner/loop/steps.py`) runs four prunes, one for each of the append-only lanes named
below plus the worker-stdout file sweep, on a one-hour floor rather than every tick: `prune_outbound` deletes an acked
`outbound_buffer` row past its window but only below the lowest still-pending seq, and `prune_heartbeats` /
`prune_external_usage_samples` each compact their table to every lease's or slug's newest row past a shorter window. The
last-pass instant lives in memory, on a long-lived holder the loop's composition root builds once, and is recorded once
every lane has been attempted whatever each one's outcome. A restart forgets it, so the first tick after one runs a full
pass. Each prune is one `DELETE` statement in its own transaction, so a `kill -9` anywhere around it leaves the table
exactly as it was before the statement or exactly as it would be after — never a partially-applied delete. That is a
**no-window** write: there is no second half a crash could separate it from, and so no `bzh:crash-point-registry` entry
is owed.

None of the store prunes can delete a row a live reader still depends on. The outbound prune's pending-floor check keeps
every row a still-open fact might need; the heartbeat and usage-sample prunes keep each lease's or slug's newest row
unconditionally, which is the only row `latest_heartbeat` and `last_external_usage_attempt_at` ever read — so a crash
losing the retried prune's effect costs nothing beyond a few more rows lingering until the next pass, never a wrong
answer from either read. `Retention.run` also isolates each lane's own prune in its own `try`/`except`, so one lane
raising costs that lane's pass, not the other three, and it retries at the next floor.

## The graph-artifact mirror

`Spawner._mint` (`blizzard/src/blizzard/runner/lifecycle/spawn.py`) records a pinned mint's graph-scope declarations
into the runner's own `graph_artifacts` table, insert-if-absent keyed on `graph_id`, immediately before `record_lease` —
ahead of the lease those rows exist to serve. The presence check and every insert behind it are one transaction, so a
mint's declarations land all or none and the `graph_id`-granular check can never mistake a half-written set for a
complete one and skip the remainder for that mint's life. A crash between the artifact write and `record_lease` leaves
at most a complete orphan set keyed to an immutable mint, and the retried mint writes identical rows, insert-if-absent
making the retry a no-op past the first success. A `graph_artifacts` row owes the checker nothing because it is a
durable fact about an immutable mint, never revised once written, so agreement between readers after a crash is
structural.

The pin guarantee reaches exactly as far as the mint, and the window past it is accepted rather than repaired. A lease
already in flight resumes through `Spawner.preamble`, which re-mints only the capability token and never re-enters
`_mint`, so a lease whose mint predates any recorded rows resumes on an empty pin — the emptiness
`IReadGraphArtifactRepository.graph_artifacts_for_graph` (`blizzard/src/blizzard/runner/lifecycle/artifacts.py`) reports
from the read side. No engine code path reads a graph declaration at all — the runner's only reader is that
worker-facing route — so no admission, routing, epoch, or completion decision can observe the window. An empty pin fails
by name rather than answering emptily: `artifact get <name> --scope graph` is a `404` naming the pinned mint, which the
worker CLI raises as a non-zero `ClickException` (`blizzard/src/blizzard/runner/api/artifacts.py`,
`blizzard/src/blizzard/runner/cli/artifact.py`). What carries a worker through an empty pin is the fallback every prompt
pointing at a graph declaration owes (`bzh:graph-artifact-pointer-fallback`,
[`../../standards/worker-nodes/graph-artifact-pointers.md`](../../standards/worker-nodes/graph-artifact-pointers.md)),
which is written against a failed read and not only an empty one.

Should a graph-scope read ever become something the engine gates on, this accepted window turns into a repair owed,
because no fallback in authored prose can stand in for a decision the engine makes for itself.

## The elicitation relaunch record-before-launch gap

`Judgement._relaunch` (`blizzard/src/blizzard/runner/lifecycle/judgement/judgement.py`) re-launches a detached verdict
elicitation whose prior attempt exited without writing anything readable — the loss-recovery counterpart to the ordinary
first launch, whose own record-before-launch gap earns the `advance.after-elicit-record.before-launch` /
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

`Judgement.collect` (`blizzard/src/blizzard/runner/lifecycle/judgement/judgement.py`) clears the in-flight elicitation
record, and sweeps its output files, only AFTER a collected reply is fully processed — never before. Clearing first
would open two windows. A crash between the clear and `_judged` completing would leave a lease with no elicitation
record and no buffered outcome, re-entering the ordinary judge path and launching a **second, redundant** elicitation —
a second model turn spent on a verdict already in hand, and one the usage ledger cannot show, since `judge` usage is
keyed `(lease, generation, kind)` and a judge elicitation opens no new generation, so the ledger ends with one `judge`
fact either way. And a staleness-exceeded branch that cleared the record before calling `Attempt.fail` would let a crash
in that gap silently reset the never-resettable staleness baseline on the next pass's fresh `_launch`.

The first window is closed by ordering, not by a registry point: `collect` clears the record and sweeps the files only
once `_judged` returns. The second is narrowed rather than closed: the staleness-exceeded branch calls `Attempt.fail`
directly, which kills and clears the record itself as one link in its own closing sequence — no separate write of
`collect`'s own precedes it — so the only span left is inside `Attempt.fail`
(`blizzard/src/blizzard/runner/lifecycle/attempt.py`), from the elicitation record's clear to the lease's closure — a
span the locally-paused escalation deferral, which returns without closing, never ends at all. A crash in that span, or
that deferral lifting, lands the lease back in the ordinary judge path with no elicitation record, so at most one
elicitation is spent again, on a fresh baseline, from a point the staleness bound was already past. That is the
accepted-loss ground: the loss is one re-spent elicitation, tolerable because it is bounded by the same threshold and
self-healing on the next pass, and its only durable trace is the
`elicitation past its staleness bound — failing attempt` warning the failing pass logs — the usage ledger cannot show
it, because a killed elicitation books no `judge` fact and the fresh one records the generation's only `judge` sample.
It is not a fresh window `bzh:crash-point-registry` owes a point to.

## The pause-park teardown

`Attempt.park_paused` (`blizzard/src/blizzard/runner/lifecycle/attempt.py`) only signals: a SIGINT to the worker's group
and to any in-flight elicitation's, then the durable park, which names that elicitation by record id. The registry point
`pause.after-interrupt.before-park` covers the one window there; recovery re-runs `park_paused`, whose guarded interrupt
re-signals only a still-live owned group. Completing the teardown is `DormantSession.on_unpause`'s first act
(`blizzard/src/blizzard/runner/lifecycle/dormant.py`), on every tick the park is open: a group still alive within
`SHUTDOWN_DRAIN_DEADLINE` of `parked_at` is left alone, one alive past it is SIGKILLed, and a named elicitation that has
exited books its `judge` usage against the paused generation through the recorder and is then cleared, its files swept —
the same usage-then-clear order as `Judgement.collect`. Those two writes are the teardown's only durable ones, and
neither opens a window: the usage write replays as an exact-replay no-op under its `(lease, generation, kind)` key, and
a crash between it and the clear leaves the record standing for the next tick to book (no-op) and clear again. The
deadline is read off the durable `parked_at`, so a runner restart resumes the countdown rather than restarting it. This
is the no-window ground; no registry point is owed.

The park's named-elicitation column is what the teardown reads to tell two standing records apart. An in-flight
elicitation record still standing under an open pause park is one of exactly two things: the park's own interrupted
record, which the park names, and which the teardown books and clears; or a usage-limit judge park's deliberately
standing record, which no park names, and which `on_unpause` answers with a fresh elicitation once the floor opens. A
named record that has since vanished, or a park naming none, leaves the teardown nothing to do.

## The usage-limit mark

`_mark` (`blizzard/src/blizzard/runner/lifecycle/usage_limit.py`) writes one row — a `subscription_usage_limits` row for
the subscription the runner spends, or a `runner_usage_limits` row for a runner spending none — in one transaction,
unique on the invocation it was classified from. A `kill -9` commits the mark or nothing, so it is a **no-window** write
and owes no registry point. The park stays after it, and the points `usagelimit.worker-after-mark.before-park` and
`usagelimit.judge-after-mark.before-park` cover the gap between mark and park: a crash there leaves the floor marked and
the lease unparked, and the next pass classifies the exit again, replays the mark as a no-op under its invocation key,
and completes the park. No brake is engaged on either side of the gap.

## The identity-failure-mark-before-close gap

`Reap.run`'s provisional-generation branch and `Spawner.spawn`'s `WorkerIdentityError` handler
(`blizzard/src/blizzard/runner/loop/steps.py`, `blizzard/src/blizzard/runner/lifecycle/spawn.py`) both call
`record_identity_failed` to close a durably-provisional generation as unidentified — the first ahead of `Attempt.fail`'s
own kill-then-close, the second ahead of re-raising `HarnessSpawnError` with the lease left open for REAP's next pass.
`record_identity_failed` is its own transaction, so in either caller a `kill -9` right after it commits, and before what
follows it completes, is a real span.

Both halves are independently harmless. `record_identity_failed` finds the lease's newest still-open `lease_spawns` row
(`session_id IS NULL`) and stamps `identity_failed_at`; re-running it after a crash re-stamps the same row with a later
timestamp, never a second row. The lease itself sits open with `pid` set and `session_id` still `NULL` in the interim —
the exact shape `Reap.run`'s own provisional-generation branch re-scans on every tick, and the module's own contract
already promises to recover: "every step is idempotent... a crash mid-tick and a restart re-run the tick harmlessly;
startup recovery is REAP running first." A crash before `Attempt.fail` closes the lease leaves REAP's next pass
re-entering the identical branch, re-marking (harmlessly) and completing the close; a crash inside the spawn handler
leaves the same reapable shape, which REAP's ordinary sweep reaches on its own schedule whether or not the handler's own
marking landed first. `NoUnownedLiveLeaseProcess` inspects only CLOSED leases, so the open-but-marked or
open-and-unmarked interim never violates it — the invariant is owed only at the moment `Attempt.fail`'s own close lands,
by which point `record_identity_failed` has always already run at least once. The write earns no window at all: its
halves are independently harmless, and the existing REAP re-scan is the recovery, not a new registry point.

## The unresolvable-pool-owner escalation mint

`Spawner._escalate_unresolvable_resume_owner` (`blizzard/src/blizzard/runner/lifecycle/spawn.py`) mints a zero-budget,
never-spawned lease purely to give `Attempt.escalate_owner_unresolvable`
(`blizzard/src/blizzard/runner/lifecycle/attempt.py`) an existing lease to close, when an existing recorded session's
owner cannot be dispatched to at node entry — a named pool's head, or a plain, un-pooled resume's own latest session
alike; `SessionResolver.resolve_resume` surfaces both shapes through the same `ResumeTarget.owner_unresolvable`, so
`enter_node` routes both through this one mint. Between that mint's own `record_lease` and the escalation's own closure
landing, the lease sits exactly as any other post-mint, pre-spawn lease does, so `_CP_AFTER_MINT`
(`spawn.after-lease-mint.before-spawn`) is reused rather than duplicated: a `kill -9` here leaves the identical "lease
minted; worker not spawned" shape a `HarnessSpawnError`'d ordinary mint already leaves, which the sweep's generic
`spawn.` family coverage already exercises structurally. No distinct crash point is warranted — this mint is one more
caller of a window already armed.

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

This same pattern has a second entry point: `Spawner.escalate_no_acceptable_harness` /
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

## The selftest result

`SelfTestService._finish` (`blizzard/src/blizzard/runner/selftest/service.py`) writes a completed selftest run's
terminal outcome — status and error only — as one `selftest_results` row
(`blizzard/src/blizzard/runner/store/schema.py`), read back by `harness_id`, newest row wins. Run *state*, per-check
results included, is a process-local, restart-erased resource (`SelfTestRun`, held only in `SelfTestService`'s own
in-memory dict); nothing durable reads a run's own checks back, so they ride no further than that. Only the *terminal
outcome* of a completed run is durable, so the harness-health evaluator's daemon-start recalculation can see the last
completed result across a restart rather than treating every boot as a never-run selftest.

The write is one insert (`SelfTestResultStore.record_selftest_result`), so a `kill -9` either leaves the previous
recorded result standing or the new one complete — never a half-written row. This is a **no-window** write: there is no
second half a crash could separate it from, the same ground `Retention.run`'s prunes above rest on.

The write owes the invariant checker nothing: `latest_selftest_result` reads the newest row by primary key per
`harness_id`, an ordering comparison over append-only rows, never a derived cross-fact invariant. A run still
`"running"` when the daemon crashes is never recorded at all — `_finish` is the only write site, reached only once a run
resolves to `"passed"` or `"failed"` — so the table only ever holds terminal outcomes, and a lost in-flight run simply
leaves the prior harness's last completed result standing until the next one supersedes it.

## The provider-overload backoff facts

`OverloadStore.record_overload` and `.record_reset` (`blizzard/src/blizzard/runner/store/internal/overload_store.py`)
append to `overload_facts` / `overload_resets` (`blizzard/src/blizzard/runner/store/schema.py`), mirroring
`nudge_facts`'s own shape: `record_overload` is a check-then-insert keyed on
`(lease_id, epoch, invocation_kind,
invocation_identity)` inside one transaction, and `record_reset` is a lone insert in
its own transaction. Both are **no-window** writes: a `kill -9` on either commits the whole row or none of it, and
re-classifying the same exit on a later pass re-checks and writes nothing past the first success.

The fact these rows feed — whether a lease is currently backing off — is derived at read time (`backing_off_facts`,
`blizzard/src/blizzard/runner/leases/overload.py`), never stored: an open fact closes by the lease's own current
generation (worker) or elicitation launch instant (judge) no longer matching the identity the fact recorded, not by a
separate closing write. A lease that closes without ever recording a later generation or elicitation launch closes the
fact a second way (`bzh:open-facts-declare-closure`): `OverloadStore.open_overload_facts` anti-joins `lease_closures`
directly, the same shape `ask_store.py` already uses, rather than leaning on every caller scoping its own read to
`list_active_leases()`. A crash between `record_overload` committing and the caller's own
`publish_lease_changed(cause="dormant")` — the same detached record-then-announce shape `park_on_ask`'s and `_wake`'s
own publishes already use, covered by this file's "Event emission" section — costs at most one missed live SSE
announcement; the next read of `backing_off_facts` (or `LeaseActivity.state`) derives `"backing-off"` from the durable
row regardless, so no operator-visible state is ever lost, only delayed to the next poll.

The write owes the invariant checker nothing: `backing_off_facts`'s own closure is an identity comparison over
append-only rows and existing repository reads (`lease_generations`, `in_flight_elicitations`), never a derived
cross-fact invariant a second writer could disagree with.

## The external-usage sampling pass

`ExternalUsageSamplePass` (`blizzard/src/blizzard/runner/usage/external_usage_sample.py`) runs on the host tick in
`runner host`, never in a runner's tick, over every `[[subscription]]` the host declares. Per slug it gates on the
newest attempt's cadence, samples, and records the attempt with its report in one transaction. Which lane is
`ExternalUsageAttemptLane`'s rule, beside the pass in `runner/usage/`. An unregistered host records through its first
registered runner's attempt handle — `record_external_usage_attempt` over that runner's bound connections — whose report
lands in that runner's `outbound_buffer`; a registered host records through
`HostLaneStore.record_host_external_usage_attempt`, whose report lands in `host_outbound_buffer`. Both are **no-window**
writes: a `kill -9` commits the attempt and its report or neither, and the next pass re-samples a slug whose attempt did
not commit.

## The host's lane

`HostLaneDrain` (`blizzard/src/blizzard/runner/lifecycle/host_lane_drain.py`) is a host-tick step on a registered host —
one holding a host token — and a lane (`bzh:lane-contract`) whose only sink is the hub. It pushes at most a fixed number
of the oldest `host_outbound_buffer` rows to `POST /api/fleet/host/events`, then records the mark the hub answers
through `HostLaneStore.record_host_high_water` (`blizzard/src/blizzard/runner/store/internal/host_lane_store.py`), which
writes `host_high_water_seen` and deletes every buffered row at or below the mark in one transaction. It drains only
while the host's latest report was answered with the host's own identity, so against a hub that refuses the host,
predates hosts, or answers as another host, the facts wait in the buffer and never ride a runner's lane.

The window between the hub applying a push and the mark landing is a **real window**, registered as
`hostlane.after-push.before-mark` and swept by `tests/crash/test_kill9_sweep.py`. A crash there leaves the pushed rows
buffered and no mark recorded; the next pass re-pushes them, the hub answers them already applied against its own
per-host mark, and the host clears them then. The mark write itself is a **no-window** write: the mark and the clearing
commit together, and a mark below the recorded one moves nothing back. A failed push leaves everything buffered for the
next pass, with no backoff and no latch, the shape the hub-as-sink class names.

The lane owes the invariant checker nothing: its rows carry the host's own `seq`, never a runner's, and the hub's mark
is what de-duplicates a replay.

## The host identity row

`HostRegistration` (`blizzard/src/blizzard/runner/hub/host_registration.py`), the host tick's first step on a registered
host, records the store's single `host_identity` row from the hub's first answered report, through
`HostIdentityStore.record_host_identity` (`blizzard/src/blizzard/runner/store/internal/host_identity_store.py`): the row
first, then the in-process holder, so a crash between them leaves the holder to be rebuilt from the row at the next
boot. The write is one transaction that inserts the row only when none exists, so a `kill -9` leaves no row or the whole
one. The row is never edited: offering the identity it holds writes nothing, and a later answer naming another host or
tenant is refused, held as a refusal of the host's credential, not an update. This is a **no-window** write.

The step's other outputs are held only in the process — its latest outcome and each runner's standing under the host,
folded into that runner's identity verdict — and are re-derived by the next report after a restart. The host reports
once before any runner ticks, so a runner its hub no longer holds is halted before it can claim across a restart. The
row owes the invariant checker nothing: it is the hub's own answer about the token.

## The credential-renewal window

`CredentialRenewalPass` (`blizzard/src/blizzard/runner/usage/credential_renewal.py`) runs on the host tick in
`runner host` (`HostTick`, `blizzard/src/blizzard/runner/loop/host_tick.py`), first after the host's report and ahead of
the usage sampling, so a slow vendor endpoint never delays it. It never runs in a runner's tick. Per slug it gates on
the newest claim's cadence, asks the renewer binding whether a renewal is due, then writes three steps in order: it
commits a claim through `ExternalUsageStore.claim_credential_renewal`, fires the renewal, and commits the outcome
through `ExternalUsageStore.record_credential_renewal_outcome`
(`blizzard/src/blizzard/runner/store/internal/host_external_usage_store.py`). The claim and the outcome are separate
append-only facts, and the claim is never updated. The renewal itself is the vendor CLI's own rewrite of its credential
file, driven as a bounded one-shot subprocess
(`blizzard/src/blizzard/runner/subscriptions/internal/openai_credential_renewer.py`): blizzard never opens that file for
writing (`bzh:subscriptions-no-write`).

The window runs from the claim, through the vendor's rewrite, to the outcome. It is a **real window**, and its loss is
**accepted**, an exemption rather than a crash point. A `kill -9` inside it loses only the outcome row. The claim is
already durable, so the slug's newest renewal reads as *unrecorded* in the runner-local diagnostics. The claim also
anchors the slug's renewal cadence, so the renewal is never repeated within that cadence. A claim that fails to commit
fires no renewal at all, and an outcome write that fails leaves the same standing claim a crash does. The credential
file is the vendor's own atomic, lock-guarded write either way, so a renewed token is on disk regardless, and the slug's
next sample reads it.

A renewal still in flight when `runner host` shuts down is the same case. The driver's `stop()` waits a bounded time,
then abandons the pass. The vendor child leads its own session and finishes its own atomic write, and the outcome it
would have recorded is lost, reading as unrecorded.

The writes owe the invariant checker nothing: both are append-only facts, and the outcome is never cross-checked against
the credential file it describes.

## The per-lease scratch directory

`IWorkerScratchDirs` (`blizzard/src/blizzard/runner/process/worker_scratch.py`), driven by `WorkerScratchDirs`
(`blizzard/src/blizzard/runner/process/internal/worker_scratch_dirs.py`), is filesystem state, not a store write:
`Spawner.preamble` and `Spawner._worker_preamble` (`blizzard/src/blizzard/runner/lifecycle/spawn.py`) call `ensure`
ahead of every resume and fresh spawn respectively, and `Attempt.close`
(`blizzard/src/blizzard/runner/lifecycle/attempt.py`) calls `remove` after `record_closure` commits, never before.

Both halves are independently harmless. `ensure` is idempotent — recreating an already-present directory is a no-op — so
a crash between it and the spawn it precedes leaves nothing to reconcile; the next `ensure` on the same lease id
recomputes the identical path. `remove` runs only once the closure is already durable, so a crash between the two leaves
an orphan directory behind a lease that is already closed, never a still-active lease with its directory gone.
`LoopWiring.context`'s own one-shot sweep (`blizzard/src/blizzard/runner/loop_wiring.py`), run only from
`PeriodicDriver`'s daemon-start build, ahead of its first tick, removes exactly that kind of orphan — anything under
`worker-tmp/` whose name is not a currently active lease id — and is not a candidate for `bzh:probe-gated-pass` or
`Retention`, since it runs once at daemon start rather than on a recurring cadence.

The write earns **no window at all**: neither half has a partner write to be separated from, and the worst either
ordering leaves a crash to interrupt is one orphan directory, collected at the next restart.

## The trace export sweep

`LeaseTraceSweep.sweep` (`blizzard/src/blizzard/runner/tracing/sweep.py`) tells closed leases to the configured
exporter, then appends a runner `trace_cursor` row recording how far it told. Its one dangerous window is registered:
`leasetrace.after-export.before-cursor` (the exporter accepted the batch; the cursor row that records it is not yet
appended), swept by one dedicated scenario against an in-test OTLP sink (`tests/crash/test_kill9_sweep.py`). A crash
there leaves the cursor unmoved, so the next pass re-reads and re-sends the same leases under the same span ids —
delivery is at-least-once, and a backend deduplicates on span id. A crash before the exporter accepts loses nothing
durable.

Its other writes earn **no window at all**:

- **The failure latch.** A `trace-export-failed` or `trace-export-recovered` announcement appends its
  `trace_export_latch` row and enqueues its `event.recorded` fact in one transaction, on the `record_local_pause`
  precedent, so a crash leaves both or neither. Losing both re-announces on the next state change. The restart behavior
  belongs to `bzh:lane-contract` ([../lanes.md](../lanes.md)).
- **Jump rows.** A cursor jump — on enable after a gap or at the lag cap — is one cursor-row append. A crash before it
  commits leaves the cursor where it was, and the next pass re-derives the same jump from a fresh read.
- **The window-skipped event.** It is enqueued before its jump row, so a crash between the two re-derives the jump and
  enqueues the note again — a duplicate informational event, never a lost cursor move.
- **The config-rejected event.** One enqueue per `runner host` start with no partner write; a crash before it commits is
  followed by a start that announces it again.

The sweep owes no probe or floor under `bzh:probe-gated-pass`: each pass reads only the closed leases past its own
cursor, never a corpus it would rescan to find nothing changed.

## The identity row

The store's `runner_identity` row records the runner the host file's `[[runner]] id` names: the name and tenant the hub
last answered for it. Three callers write it, all through `RunnerIdentityStore.record_runner_identity`
(`blizzard/src/blizzard/runner/store/internal/identity_store.py`): `runner init`
(`blizzard/src/blizzard/runner/cli/runtime.py`), `Registration.run`
(`blizzard/src/blizzard/runner/lifecycle/registration.py`) and `IdentityCheck.run`
(`blizzard/src/blizzard/runner/lifecycle/identity_check.py`). None adopts an id: the store is bound to the configured id
before anything runs, and the write refuses an identity naming another runner (`RunnerAlreadyBound`). Registration
refreshes the name and tenant under the configured id, and a reply naming another runner writes nothing and turns the
verdict to a mismatch. The check judges the token's runner against the configured id, never against the row, and writes
only to fill in the tenant a matching answer names. `init` writes the row from the hub's answer whether it added the
runner or kept it, so a configured runner has its row before it writes anything. Nothing ever overwrites the id: `init`
writes the host file's `id` only into an entry that has none, or over a stale one under `--allow-readd` with a store
that is fresh (set aside for the re-add) or names only the joined runner; a held token naming another runner than the
configured id stops `init` before it writes a token, host-file id or identity row (the store itself may already have
been adopted or migrated by then), and a start, `host --check` or `tick` over a store whose identity rows name any
runner other than the configured one refuses that runner untouched. The bound runner's row is updated in place, or
inserted when none exists, in one transaction, so a `kill -9` leaves the previous row or the new one, never neither and
never both. The in-process identity holder is updated only after the row commits, and is restart-erased and reseeded
from the row at boot. This is a **no-window** write: there is no partner write a crash could separate it from, and a
lost write is made again by the next registration or matching check.

The verdict the row is checked against is held only in the process: `IdentityVerdictHolder`
(`blizzard/src/blizzard/runner/hub/identity.py`) is either `UNCHECKED`, `MATCHED` or `MISMATCHED`, and starts every
process `UNCHECKED`. A crash therefore loses it, and the restart re-derives it from a fresh check. The check is the head
of every tick (`blizzard/src/blizzard/runner/loop/tick.py`): it asks the hub which runner the token belongs to and
compares that id with the row's, before any other hub call. One function, `tick_scope`
(`blizzard/src/blizzard/runner/lifecycle/identity_check.py`), then decides from the verdict whether the rest of the tick
runs every step, the registration alone beside the local steps, or the local steps alone. Until the verdict is
`MATCHED`, every call through `VerifiedHubClient` (`blizzard/src/blizzard/runner/hub/verified.py`) answers a
`HubClientError`, so an unchecked loop behaves exactly as it does during a hub outage, taking only the outage paths
every step already owns. The transcript operator verbs, backfill and reship, build their own process graph and run the
same check once before their first hub call (`LoopWiring` in `blizzard/src/blizzard/runner/loop_wiring.py`).

The runner's hub proxy (`blizzard/src/blizzard/runner/api/hub_proxy.py`) is a first contact of its own. While the loop
has not checked, `ProxyIdentityCheck` (`blizzard/src/blizzard/runner/lifecycle/identity_check.py`) has the proxy ask the
hub which runner the token belongs to through the runner's own token-identity reader — retrying a silent hub within the
forward's own budget — and judges the answer against the configured id. It remembers a match for the process, so the
proxy asks once. A hub that does not answer — an outage, or a `401` that is not the hub's typed refusal — fails a
proxied read with a 503 naming the outage; a refused token, a hub without the identity read, or a mismatch forwards
nothing and answers 503 naming the reason. The proxy writes neither the row nor the verdict: once the loop has checked,
its verdict prevails, and a `MISMATCHED` one answers 503 without contacting the hub.

A `MISMATCHED` runner also skips the steps that drive leases or deliver facts until a check matches again, and a hub
that does not answer leaves the verdict as it stood. Nothing durable is lost to any of this: restoring the right token
or hub resumes the runner from what its store already holds.

While refusing, each check first re-reads the token from the runtime dir's `.env` through `HubTokenHolder.reread`
(`blizzard/src/blizzard/runner/hub/held_token.py`), so a corrected token takes effect without a restart. The re-read
only reads the file and swaps the token in memory; a token the process environment supplied overrides the file, and so
stays fixed until a restart.

The write owes the invariant checker nothing: the row is the hub's own answer about the token, never derived from other
facts.

### Binding at the configured id

The store binds to its runner (`bzh:runner-scoped-store`) from configuration: every composition binds the stores to the
entry's `id` before anything runs, the hub reachable or not — the host and tick graphs and the offline read verbs. The
invariant checker reads across runners through the exempt `runner_audit`, so it takes no binding. The binding is
in-process, never changes once set, and is never read back from the identity row. A connection never bound reads a
runner-scoped table as empty and refuses a write with `RunnerUnbound`, so no write lands before the id it must carry
exists. A `kill -9` leaves nothing to reconcile: the binding is reseeded from the host file at the next boot.

The tightening revision (`blizzard/src/blizzard/runner/store/migrations/versions/20261013_1000_runner_scope_tighten.py`)
makes `runner_id` `NOT NULL` on every runner-scoped table, so a row naming no runner cannot exist. It stamps any row a
previous release left naming none from the identity row, and refuses a store that holds such rows and no identity row.
The upgrade is one transaction from its first data write — the backfill, the counter seeding, and every batch rebuild —
so a stopped run rolls all of it back and leaves the store at the parent revision, the outboxes keyed as they were and
no counter rows written. Only DDL ahead of the first data write commits alone, so at most an empty `outbox_counters`
survives, and, in a store with no identity row, the first batch's `CREATE TABLE _alembic_tmp_*` as well: with no row to
backfill from there is no data write ahead of that batch, so its table copy commits alone. Idempotence covers the rerun
over that surviving DDL: it creates `outbox_counters` only when absent, stamps only rows still naming no runner, and
skips a table already tight. `_seed_counters` skips an outbox already keyed `(runner_id, seq)` on the ground that its
counter was seeded before the rebuild; that holds only because the seeding and the rebuild commit together.
`_clear_stale_copy` drops a table copy a batch left behind. In a store with no identity row it is required, not
insurance: the committed `_alembic_tmp_*` would otherwise make the rerun's batch fail on a table that exists. It owes no
registry point.

### The host store adoption

`blizzard runner migrate` adopts a pre-host `data/runner.db` as `data/host.db` (`Runtime._upgrade`,
`blizzard/src/blizzard/runner/runtime.py`) under the directory's lock: it folds the write-ahead log into the database
and renames the database and each sibling through `move_sqlite`, then applies the pending revisions. This is a
**no-window** write. The presence of `host.db` decides the outcome: before the rename the pre-host store is whole under
its old name, and after it the host store is whole under the new one, so a re-run either adopts again or migrates in
place. A directory holding a pre-host `blizzard-runner.toml` and no `blizzard-host.toml` is refused untouched.

A crash cannot leave both files. The database moves in one rename after the checkpoint, so `runner.db` is gone the
moment `host.db` exists; what a crash can leave behind is an empty `-wal` or `-shm` sibling, which a re-run migrates
past, since adoption needs `runner.db` to exist. A populated `host.db` beside a `runner.db` is therefore never a crash
state: `_upgrade` refuses it, naming both files, and touches nothing, because only an operator can decide which one is
the runner's store. `store reset` and `migrate --down` refuse a directory whose `host.db` is absent while `runner.db`
exists, so neither can create the second file.

### The `init` id write

`runner init` writes the joined runner's id into the host file between the token and the identity row
(`write_runner_id`, `blizzard/src/blizzard/runner/host_file.py`). Each file write is atomic: the token's `.env` and the
host file are each written whole to a temporary file and renamed over the original, so a crash leaves the old file or
the new one. A crash between any two steps leaves a state running `init` again completes, keeping the runner the token
names; a stale configured id is rewritten only under `--allow-readd`, with a store that is fresh or names only that
runner, and any other mismatch is refused with nothing written. This is a **no-window** write.

### The outbox counter advance

Every outbox `seq` is allocated by the one seam, `insert_outbox_row`
(`blizzard/src/blizzard/runner/store/internal/base.py`), which advances the bound runner's lane in `outbox_counters` in
the same transaction as the row. This is a **no-window** write: a crash leaves both the row and its advance or neither,
so a rolled-back `seq` is returned and a counter that never moves backwards never reissues a pruned row's. The invariant
checker's `runner:outbox-counter-above-seq` asserts that no retained row sits above its counter.

### Held-binding completion

`CompleteHeldBindings` (`blizzard/src/blizzard/runner/loop/steps.py`), a step ahead of FILL that runs
`HeldBindingCompletion` (`blizzard/src/blizzard/runner/lifecycle/held_binding_completion.py`), gives each held
`env_bindings` row lacking them its workspace and its chunk's project. One probe finds the incomplete held rows, and
with none nothing else runs. Every completion is one update over the rows in a single transaction, and each column it
sets is guarded by `COALESCE`, so it fills only an empty column. This is a **no-window** write: a crash leaves each row
either completed or still incomplete, and the next tick completes it. A row the hub cannot answer yet, or whose
`workdir` matches no listed workspace, keeps its gap and its lease, so it still counts against bindings: an unknown
project against every binding on its workspace, an unknown workspace against every binding of the runner.

## The store reset

`blizzard runner store reset` (`blizzard/src/blizzard/runner/cli/store.py`) runs while the daemon is down, refused while
anything answers on the runtime's socket. It moves the store aside through `set_aside_sqlite`
(`blizzard/src/blizzard/runner/runtime.py`) and never deletes. It first checkpoints the write-ahead log into the
database (`PRAGMA wal_checkpoint(TRUNCATE)`), so the database holds the whole store. Then it renames the database
(`data/host.db` by default) and each present `-wal`, `-shm` and `-journal` sibling to the same `<name>.<UTC stamp>`
name, refusing up front when any target is taken. Last, `Runtime.reset_store` migrates a fresh store to head under the
old name.

This is a **no-window** write. Each rename is atomic, and after the checkpoint the database moves whole in its one
rename, so a crash between renames leaves a sibling behind that holds nothing a fresh store at the old name would
replay. A crash before the fresh store is migrated leaves a store the daemon's startup revision guard refuses, naming
the migrate command. Either way the old store is already whole under its stamped name, and re-running the reset, or the
migrate it names, completes the job.

`store reset --runner <name|id>` resets one runner alone through `Runtime.reset_runner`
(`blizzard/src/blizzard/runner/runtime.py`). It migrates a new archive store under a temporary name beside the host's,
copies the runner's rows into it in one transaction, folds the archive into one file, and renames it to
`<store>.<runner>.<UTC stamp>`. Only then does it delete the runner's rows from the host store, in one transaction that
keeps its outbox counters. This is a **no-window** write. Before the rename no archive name exists, and a re-run removes
the temporary file and starts again. After the rename and before the delete, the archive is complete and the rows are
still in place, so a re-run writes another archive and deletes them, losing nothing.

## The ingest

`blizzard runner ingest` (`blizzard/src/blizzard/runner/ingest.py`) moves one runner between stores and host files that
share no transaction, holding this host's lock for the whole run, and the source's when the source is a host directory;
a runner directory that has not graduated takes no lock, so it is held only by probing its `runner.sock`. It reads the
source only through a backup copy, so the source is written by the last step alone. The steps run in this order:

1. Copy the runner's rows into this host's store in one transaction that also appends its `host_ingests` row: the
   runner, the source, and the source's last `daemon_liveness` stamp.
2. Append the runner's `[[workspace]]`.
3. Append its `[[subscription]]`.
4. Copy the path files under `runners/<name>/` and append its `[[runner]]`.
5. Write its token into this host's `.env`.
6. Remove its token from the source's `.env`.
7. Delete its rows from the source, only from the runner tables the source's schema has, and move a source left with no
   runner aside whole. A runner directory that has not graduated holds that one runner in a store at the schema it ran,
   so its store is moved aside whole, unedited.

Each edit from 2 to 6 is skipped when the file already holds it, so a re-run completes whatever an interrupted run left.
The re-run is keyed on the record, not on the files: a runner whose identity row this host holds, with a newest
`host_ingests` row from the same source and an unchanged source stamp, skips step 1. A source that no longer holds the
runner gets only its move-aside. A moved stamp refuses, naming both stores, since the source ran after the copy. Two
windows are **real windows**, each an armed crash point. `ingest.after-copy.before-config` falls after step 1, with the
rows in both stores and no configuration here yet. `ingest.after-config.before-removal` falls after step 6, with the
token here and the rows still in the source. Without its token the source cannot run this runner, but a source host
serving other runners still moves its host-wide stamp, and the re-run then refuses; the recovery is
`store reset --runner` here, then a fresh ingest.

## The add-then-write-token window

`runner init` joins a runner that holds no token, or one holding a token its hub does not know under `--allow-readd`.
`RunnerBootstrap.join` (`blizzard/src/blizzard/runner/hub/bootstrap.py`) adds the runner at the hub, which commits the
new registration and its token hash before answering. It then writes the token the hub returns to the runtime dir's
`.env` through `HubTokenFile.write` (`blizzard/src/blizzard/runner/hub/internal/token_file.py`). The token write itself
is atomic, a fsynced temp file renamed over the original, so the file holds the old token or the new one, never half of
either.

A store belongs to the runner that wrote it, so a runner added in place of another never inherits its store. Under
`--allow-readd` with a token the hub does not know, `join` sets the store aside through `IRunnerStoreAside.set_aside`
before adding the runner, never after; that is the store reset's own move, described above. The same applies to a runner
holding no token over a store whose identity row names a runner: init stops and names that runner, unless
`--allow-readd` is given, which sets the store aside first. A crash between the set-aside and the add leaves the unknown
token, or no token, over a fresh store, and re-running init adds the runner afresh. The other order could leave a token
the hub knows over a store naming another runner, which the identity check refuses until the store is reset.

The window between the add and the write is a **real window**, and its loss is **accepted** and named. A `kill -9` or a
failed write inside it leaves the hub holding a runner as never connected, under a token nobody holds, while `.env`
keeps what it had. A failed write exits naming `blizzard hub runner retire <id> --hub-url <hub>`; after a crash the same
runner shows as never connected in `hub runner list`, and retiring it by its id is the recovery either way. The loss is
one inert registry row: it holds no route and claims nothing, and re-running init adds the runner afresh over the
already fresh store. No crash point stands in for it.
