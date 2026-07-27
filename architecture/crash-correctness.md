# Crash correctness

MVP acceptance criterion 4 promises that `kill -9` at every step boundary is **a tested operation, not a hope**.
That promise imposes four requirements on daemon code — built in from the first commit, because each is cheap on day one and expensive to retrofit.
Crash correctness is an orthogonal dimension, not a fifth test tier ([../verification/blizzard.md](../verification/blizzard.md)): the requirements below are *architecture*; the kill-9 sweep that exercises them is a verification method (`blizzard:crash-sweep`) in the matrix.
Each rule follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## A steppable loop (`bzh:steppable-loop`)

**Rule.** The daemon loop's phases — the runner's REAP, PULL, FILL, ADVANCE, and the hub's coordinator loop — are individually callable step functions, each a pure function of (store, clock, seam clients); the tick timer is merely one driver of them.

**Why.** Tests drive the same step functions directly, one at a time, stopping exactly at a boundary — which is how boundary-order and recovery logic get cheap in-process coverage and how the sweep arms a precise crash point. A loop welded to its timer can only be tested by waiting on wall-clock ticks and cannot be stopped mid-step.

**Detect.** Loop phases reachable only through the tick timer or a `while True`; a step that reads the clock or a seam from a module global rather than its parameters.

**Do.** `def fill(store, clock, seams) -> None` callable standalone; the tick driver calls `reap`, `pull`, `fill`, `advance` in turn.

**Don't.** A single `tick()` that inlines all four phases with no separately callable boundary — no test can stop between FILL and ADVANCE.

## An injected clock (`bzh:injected-clock`)

**Rule.** All time flows through a clock abstraction wired at the composition root (`bzh:dependency-injection`); no direct `time.time()` / `datetime.now()` appears in loop, store, or domain code — **including SQLAlchemy column defaults**.

**Why.** An injected clock lets tests advance time virtually, so lease TTLs, reap staleness thresholds, and an "overnight" wait pass in milliseconds and deterministically; a direct `datetime.now()` anywhere — especially a column default — reintroduces wall-clock non-determinism the sweep cannot control.

**Detect.** `datetime.now()`, `datetime.utcnow()`, `time.time()`, or `func.now()` / `server_default=func.now()` in loop, store, domain, or model code; a timestamp written from anything but the injected clock.

**Do.** The clock is injected; timestamps come from `clock.now()`, and column values are set by the writing code from that clock — not by a database default.

**Don't.** `created_at = Column(DateTime, default=datetime.utcnow)` — the store now stamps wall-clock time the virtual clock can't move.

## A crash-point registry (`bzh:crash-point-registry`)

**Rule.** The dangerous windows carry stable names in a code-owned, **enumerable** registry — e.g. `fill.after-env-acquire.before-claim`, `advance.after-buffer.before-flush`, `hubnode.after-step.before-marker`, `reap.after-kill.before-expire`; under test scaffolding a daemon subprocess SIGKILLs itself on reaching the armed point, selected via an environment variable and fenced so it can never fire outside a test-marked environment. The segment before the point's first `.` is the **boundary family** the sweep partitions the registry on — it resolves which scenario (the generic `build → deliver` sweep, or a dedicated scenario such as `resume.`, `abandon.`, `pause.`, `hubnode.`) is the one that arms and reaches that point — so name a point for the boundary its reaching scenario opens, never for the step whose source happens to call `.reached()`.

**Why.** An enumerable registry is what the sweep iterates — one run per armed point — and it doubles as the authoritative list of windows the design claims are safe, so a newly-introduced dangerous window is a registry entry, not a silent gap. The family prefix is what routes a point to the scenario that actually reaches its window, so naming it for the wrong family leaves the registry entry with no real coverage behind it.

**Detect.** A crash-recovery claim about a window with no corresponding registry entry; a self-kill hook not gated behind the test-environment fence; crash points hard-coded in the test rather than enumerated from the registry; a new point prefixed with a family that already has coverage from an unrelated sibling point, when the point's own window only opens under a dedicated scenario — the family-coverage check passes on the sibling's strength while the new point's window goes unswept.

**Do.** Add the window's stable name to the registry, prefixed for the scenario that reaches it — `pause.after-kill.before-park`, not `pull.after-pause-kill.before-park`, even though the call site sits inside the PULL step's code; the sweep enumerates the registry and arms each in turn; the daemon self-kills only when the test fence is set.

**Don't.** Assert a window is crash-safe in prose without a registry entry the sweep can arm — the claim is untested. Prefix a new point `pull.after-pause-kill.before-park` because that's where its `.reached()` call sits, instead of `pause.after-kill.before-park` for the scenario whose window it actually guards.

### Recorded exemptions — durable state with no dangerous window

Not every durable write opens a window this registry must name; a write with **no unsafe partial-write window** has nothing to arm, and that must be a *stated* position, not an implicit one (the "Don't" above bars asserting a window *safe without arming it* — this is the distinct case of there being *no window at all*). Record such a decision here when a change adds durable state that a reviewer would otherwise expect a sweep point for:

- **The runner's jti replay cache (issue #95, decision D4).** The runner-store table `jwt_jti_seen(jti PK, aud, expires_at)` backs single-use of a hub-signed federation JWT across a restart within the 60s token window. Its "check-not-seen → insert → mint session" path is **one transaction under the `jti` primary key**, so no interleaving admits a replay: a crash *after* the insert but *before* the session mint loses only the runner-domain session, forcing a fresh, harmless re-bounce through the hub (a liveness annoyance, never a safety break — the row that would reject a replay is already durable). There is therefore **no `bzh:crash-point-registry` entry** for it, and **no new `bzh:invariant-checker` assertion**: jti uniqueness is a store-level PK constraint the engine enforces, not a derived cross-fact invariant the checker must recompute. This cache is not a loop step, so the loop-driven sweep families never reach it, and correctly so.

- **The runner's git-commit verify (issue #143, Phase 4).** The worker pushes its branch and declares it; ADVANCE's own git surface is a **read-only** re-derivation (`git ls-remote` against the origin the environment's repo manifest names) of a fact already durable in the `git_commit_declarations` table — it never pushes (`bzh:git-write-in-worker-seam`, [./system-shape.md](./system-shape.md)). A read `kill -9` at any point simply loses nothing durable — the declaration survives untouched, and the very next ADVANCE pass re-reads and re-verifies it from scratch, converging on the same result every time. There is therefore **no `bzh:crash-point-registry` entry** for this window: the registry no longer names `advance.before-artifact-push` / `advance.after-artifact-push.before-judgement` (the mutation window a runner-side push used to open), and neither does the bounded CI subset or the `test_ci_subset_covers_every_family` family-coverage list — `advance.` keeps its other members' coverage, so the family is not orphaned by their absence.

- **The runner's operational-event emission (issue #125, change K/L).** The runner surfaces its operationally-significant failures as `event.recorded` facts that ride the *existing* outbound buffer — exactly-once delivery is already held by the buffer's gapless-seq invariant and the hub's per-runner high-water mark, machinery the sweep and the checker already cover. The `_fail_attempt` retry/escalate events are enqueued **in the same transaction as the closure they describe** (the `record_local_pause`/`record_usage` atomic local+outbound precedent), so no partial-write window exists there. The one deliberately non-atomic emission — the reassign-**abandon** branch, whose closure lives one level down in the shared `_abandon_reassigned` (plan-findings SF-6) — is still safe with **no arming needed**: an operational event is informational and append-only, and at-most-once-per-attempt is *structural* (`_fail_attempt` runs once per attempt — it closes/requeues/escalates the lease, so the next tick sees a different lease state, needing no durable guard fact), so a `kill -9` between that closure and its enqueue at worst loses one informational event that the next attempt's failure re-emits. There is therefore **no new `bzh:crash-point-registry` entry** and **no new `bzh:invariant-checker` assertion**: no new durable guard, no new dangerous window, and no new cross-fact invariant — the same shape as the #95 jti exemption above.

- **The runner's per-session preamble fingerprint (issue #149).** The runner-store table `session_preamble_facts` records, per harness session, a digest of the standing spawn-preamble prose that session was last sent, so a resumed spawn can skip an unchanged layer and announce a changed one. The write sits inside the SPAWN step, immediately after `record_spawn` — a position a reviewer would reasonably expect a sweep point for — but it lands **after the spawn call returns**, so a durable fingerprint always implies the prose actually reached the process. A `kill -9` that loses it leaves the session with no fingerprint, and the next resume reads `None` and renders all three layers in full: precisely the pre-issue-#149 behavior, a token cost rather than a safety break. The reverse order cannot mislead either — the fingerprint is keyed on the session, and the process had already received the prose before either write ran. There is therefore **no `bzh:crash-point-registry` entry** for it and **no new `bzh:invariant-checker` assertion**: no new durable guard, no new dangerous window, and no new cross-fact invariant — the same shape as the #95 jti and #125 event-emission exemptions above.

## A facts-level invariant checker (`bzh:invariant-checker`)

**Rule.** A checker of assertions evaluated over both stores' facts after any crash → restart → recover cycle holds the durable invariants: no duplicate env binding, at most one accepted transition per node-step epoch, no double delivery with per-repo lands idempotent and per-repo `pr.opened` idempotent, every derived status computable with exactly one match, a gapless outbound-buffer sequence, and usage attributed exactly once per `(lease, generation, kind)`.

**Why.** Because both stores are facts-only (`bzh:facts-not-status`), the checker is essentially a library of SQL assertions plus the status-derivation queries themselves — and a failure names the exact violated invariant rather than a vague corruption. It is the assertion the sweep runs after every armed crash, alongside the scenario's own expected outcome.

**Detect.** A crash test that asserts only "the process restarted" or "the chunk eventually landed" without checking the facts-level invariants; a new durable invariant added to the design with no assertion in the checker.

**Do.** After restart-and-recover, run the checker's SQL assertions over both stores; a violation reports which invariant broke.

**Don't.** Rely on the scenario's happy-path outcome alone — a double-delivery or duplicate-binding bug can leave the chunk looking landed while an invariant is silently violated.

## See also

- [./system-shape.md](./system-shape.md) — `bzh:facts-not-status` and `bzh:deterministic-shell`, the invariants these requirements rest on.
- [../verification/blizzard.md](../verification/blizzard.md) — `blizzard:crash-sweep`, the method that composes the four requirements into the criterion-4 proof, and the division of labor with the unit and component tiers.
