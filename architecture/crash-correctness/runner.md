# Recorded exemptions — the runner's durable writes (`bzh:crash-exemptions-runner`)

Each entry states why a durable write opens no window `bzh:crash-point-registry` must name, and what stands in for a
sweep point instead — the register [../crash-correctness.md](../crash-correctness.md) §Recorded exemptions routes into.
Entries cite their siblings by issue number across all three files: [./hub.md](./hub.md) and
[./transcripts.md](./transcripts.md).

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
  (`bzh:git-write-in-worker-seam`, [./system-shape.md](../system-shape.md)). A read `kill -9` at any point simply loses
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
  cross-fact invariant — the same shape as the #95 jti exemption.

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
  #95 jti and #125 event-emission exemptions.

- **The runner's escalation closures (blizzard#292).** `Pull._reconcile_escalations`
  (`blizzard/src/blizzard/runner/loop/steps.py`) appends one `escalation_closures` row per open local escalation whose
  chunk the hub reports `stopped` — new durable state written from a loop step, and written *before*
  `pull.before-flush`, a position a reviewer would reasonably expect a sweep point for. There is no dangerous window.
  The write is a lone insert in its own transaction with nothing to pair it with atomically: unlike the context-sample
  row, it enqueues no companion fact, because the closure is a purely local mirror of something the hub already holds —
  the hub's own `chunk.stopped` fact is what the two sides agree on, and this row only saves the runner from re-deriving
  it. A `kill -9` before it commits leaves the escalation open, and the next tick re-reads the same still-stopped chunk
  and writes the same mark, converging on the identical state; a `kill -9` after it commits has already reached the
  intended one. A crash that somehow admitted the row twice is equally harmless: the read is an `Unsuperseded` existence
  test, so N marks for a chunk read exactly as one. Nothing gates a spawn or a claim on the table — it suppresses a
  display read (`open_escalations`) and the `runner requeue` guard, never work admission — so a lost or duplicated row
  costs at most one tick of a stale panel row. There is therefore **no `bzh:crash-point-registry` entry** for it and
  **no new `bzh:invariant-checker` assertion**: no new durable guard, no new dangerous window, and no new cross-fact
  invariant — supersession is an ordering comparison over append-only rows, not a derived invariant to recompute — the
  same shape as the #95 jti, #125 event-emission, #149 preamble-fingerprint, #137 promote-then-tail-stamp, #216
  delivery-closure-sweep, #230 marker-token, and blizzard#250 backfill exemptions.

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
  marker-token, blizzard#250 backfill, and blizzard#292 escalation-closure exemptions.

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
  promote-then-tail-stamp, #216 delivery-closure-sweep, #230 marker-token, and blizzard#250 backfill exemptions.

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
  than a cross-fact invariant to recompute — the same shape as the jti-replay and the other durable-fact exemptions.

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
  [../standards/worker-nodes.md](../../standards/worker-nodes.md)), which is written against a failed read and not only
  an empty one. Should a graph-scope read ever become something the engine gates on, the window turns from accepted into
  a repair: no fallback in authored prose can stand in for a decision the engine makes for itself. Backfilling on resume
  would close only the stretch before that next mint, and would buy it by making a second call site write a table whose
  sole writer being the mint is what the paragraph above rests on.
