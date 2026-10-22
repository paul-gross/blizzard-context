# Periodic passes and lanes

A **lane** is a periodic pass or store-and-forward pass that moves facts toward a sink. On the hub, every pass hosted by
the `Sweep` driver is a lane: the annotation and event-derivation reconcilers, the close drain, the trace export sweep,
and the egress sweep. On the runner, every pass that moves facts off the runner is one: `OutboundDrain`,
`TranscriptDrain`, `LeaseTraceSweep`, and a registered host's own `HostLaneDrain`. The core phases (REAP, PULL, FILL,
ADVANCE, RESUME), the samplers, and `Retention` are not lanes. `bzh:steppable-loop` in
[`./crash-correctness.md`](./crash-correctness.md) governs loop phases; `bzh:probe-gated-pass` below governs the cost of
converging and pruning passes, including `Retention`. Each rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## What a lane owes around its body (`bzh:lane-contract`)

**Rule.** A lane honors five clauses around its body:

1. **Bound.** A lane draining a backlog — a set that grows while its sink is unavailable — takes at most a fixed number
   of items per pass and leaves the rest to the next pass. A converging pass over a live working set is bounded by that
   set, and `bzh:probe-gated-pass` governs its cost.
2. **Idempotent per item, with a named crash-point family.** Every item's effect is safe to replay. Every window between
   an external effect and its durable record is either a crash point under the lane's own family prefix
   (`bzh:crash-point-registry`) or a recorded exemption in the daemon's register.
3. **One failure shape per sink class.** The lane takes the shape its sink class names below, and takes its retry state
   from `blizzard/src/blizzard/foundation/lane_retry.py` rather than keeping its own.
4. **Isolation.** A lane's failure never escapes into its host's other work. The hub runs each `Sweep` as its own task
   with its own catch. A runner tick-step lane catches its own failures inside `run()`, so later tick steps still run. A
   runner driver catches per pass. A hub pass that serves many tenants carries this down to each tenant
   (`bzh:pass-isolates-tenants`).
5. **Hosting.** On the runner, a lane whose only sink is the hub is a step of the pass that owns its rows: a runner's
   lane is a step of that runner's tick, and the host's own lane, `HostLaneDrain`, is a step of the host tick, which
   runs on its own driver beside the runners' ticks. Either way the hub client bounds each call, and the pass's later
   steps consume its result. A lane whose sink is operator-configured, such as an exporter, runs on a dedicated driver,
   so a stalled sink never holds a tick. On the hub, every lane is a `Sweep`.

The failure shapes, by sink class:

| Sink class                                                  | Shape                                                                                                                                                                                                                    | Lanes                                                                      |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| Operator-configured, with an outage the operator can act on | Whole-pass backoff and an **outage latch**: one failed event when an outage starts, one recovered event when it ends. The first pass seeds the latch from the newest persisted latch, so a restart mid-outage is silent. | Hub trace export sweep, hub egress sweep, runner `LeaseTraceSweep`         |
| Per-item outcomes against a forge                           | Per-item backoff, persisted as attempt history and computed with the shared formula, plus per-item events. No latch: one item failing does not mean the sink is down.                                                    | Close drain                                                                |
| The hub as sink, or a local-store converging pass           | Retry on the next pass, with no backoff and no latch. A failed pass costs one bounded request, and an announcement would ride the channel that is failing.                                                               | `OutboundDrain`, `TranscriptDrain`, `HostLaneDrain`, the three reconcilers |

**Why.** A lane runs unattended for as long as its sink is down, so every clause bounds a cost that otherwise grows
without limit: an unbounded pass starves its host, an unreplayable item corrupts on the crash the sweep arms, an
announcement per failed pass floods the event log, and a lane that raises into its host takes the host's other work down
with it. One failure shape per sink class keeps an operator's reading of "failing" the same on every lane, and one
shared helper keeps the backoff formula and the latch transitions from drifting apart across copies.

**Detect.** A lane that reads or sends its whole backlog in one pass; a window between an effect and its record with
neither a registry point nor a recorded exemption; a lane whose own fields hold a failure count, a next-due instant, or
a failing flag; a failure event emitted per failed pass, or emitted again after a restart mid-outage; a lane step whose
raise reaches its host; a lane on a sink class that gives it a backoff or latch its class does not name.

**Do.** `TraceExportSweep` and `EgressSweep` (`blizzard/src/blizzard/hub/domain/observability/tracing/sweep.py`,
`blizzard/src/blizzard/hub/domain/observability/egress/sweep.py`) hold an `OutageLatch` from `foundation/lane_retry.py`,
ask it whether a pass is due, and announce only when it says a failure opens or a success closes an outage.
`CloseIntentDrainer` (`blizzard/src/blizzard/hub/domain/work_items/closure.py`) attempts a fixed number of due intents
per pass and computes each intent's due time with `backoff_delay`. `TranscriptDrain` catches every failure inside
`run()`.

**Don't.** A new lane that hand-copies a failure counter, a next-due instant, and a failing flag, then re-implements the
doubling and the open/close transitions beside them, instead of taking the helper. The copies drift: one lane clamps the
doubling and another overflows on a long outage.

**See also.** [`./crash-correctness.md`](./crash-correctness.md) `bzh:steppable-loop` — each lane's pass is one of its
step functions — and `bzh:crash-point-registry` — the family prefix clause 2 names. `bzh:probe-gated-pass` below — the
cost of a converging pass. [`./clean-architecture.md`](./clean-architecture.md) `bzh:shared-kernel` — where the helper
lives.

## A probe-gated pass (`bzh:probe-gated-pass`)

**Rule.** A periodic pass converging a corpus toward a derived state checks a cheap change probe — a watermark, a
cursor, a signature — before it rescans its corpus, skips the rescan when the probe matches the previous pass's value,
and forces a full pass once a bounded floor has elapsed since the last one, so a missed signal can never become a
permanent skip. A periodic pass that prunes or expires what has aged past a window far longer than the floor instead
runs on the floor alone, with no probe.

**Why.** A reconciler runs forever at a fixed interval while the corpus it converges changes rarely, so an unprobed pass
pays the full rescan on every tick for a result the previous tick already produced. The floor is what makes the skip
safe: a probe that misses a change costs one floor's latency rather than correctness, and a pruning pass run on the
floor alone keeps aged rows at most one floor past its window.

**Scope.** This binds the pass itself — a periodic `sweep()` or tick step `run()` body, hub or runner alike — not the
`Sweep` driver in `blizzard/src/blizzard/hub/app.py`, which owns cadence and jitter and steps the pass as a black box. A
fixed cadence where a change signal would do is judged here, at the pass: the probe is what makes a fixed interval
cheap, so the answer to it is a gated pass, not a re-timed driver. A per-item resolution inside the pass is
[`./read-cost.md`](./read-cost.md) `bzh:bulk-reconstitution`'s, not this rule's. A pass over tenants reads one probe
statement for the hub and keeps its value and last full pass per tenant, so a tenant is judged on its own
(`bzh:pass-isolates-tenants`). Each pass shape owes:

| Shape                                                                                                                                                                | Example                                                                                                                         | Owes                                                                                                                                                                                                          |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rescans a corpus to converge a derived state from it                                                                                                                 | The hub's annotation and event-derivation reconcilers                                                                           | A probe and a floor                                                                                                                                                                                           |
| Prunes or expires what has aged past a window far longer than its floor                                                                                              | The runner's `Retention` step in `blizzard/src/blizzard/runner/loop/steps.py`, pruning its day-scale lanes on a one-hour floor  | A floor, not a probe                                                                                                                                                                                          |
| Enforces a window without pruning it                                                                                                                                 | The runner's `SpendCeiling` step, which engages the pause brake once rolling-window spend reaches its cap                       | Nothing here — it is outside this rule: it owes its reaction on the tick the cap is crossed, and a floor would let spend overshoot the cap for up to one floor                                                |
| Acts on work as it comes due — reaping a lease, advancing or filling, draining a queue or buffer, retrying an intent whose backoff has elapsed, sampling live leases | `CloseIntentDrainer.sweep` in `blizzard/src/blizzard/hub/domain/work_items/closure.py`; the runner's `Reap` and `Advance` steps | Nothing here — it is outside this rule: its due-set is the live work the pass exists to answer, often made due by time passing alone, so no change probe sees it and a floor would delay the reaction it owes |

**Detect.** A converging pass whose first statement is its full-corpus read, with no value compared against the previous
pass's, or one value folded across every tenant of a hub-wide pass; a pass whose skip has no floor behind it, so a probe
that lies once skips forever; a tick step that prunes a day-scale window unconditionally every tick. The fix is a probe
seam on the store — a max-watermark or a signature query answering in one statement — compared against the value the
pass last converged on (per tenant, for a pass over tenants), plus a recorded last-full-pass instant checked against the
floor; for a pruning pass, the recorded instant and the floor alone.

**Do.** `blizzard/src/blizzard/hub/domain/observability/analytics/derivation.py`'s `EventDerivationReconciler.sweep`
reads `derivation_signature()` first, converges only the tenants whose signature differs from their last converged one
or whose ten-minute floor is due, and records each converged tenant's signature and instant. An unchanged pass costs the
probe's one statement.

**Don't.** A converging `sweep()` that reads its whole corpus and every remote's state unconditionally on each pass, so
an idle fleet pays the whole diff every interval, changed or not.

**See also.** [`./crash-correctness.md`](./crash-correctness.md) `bzh:steppable-loop` — the pass this rule gates is one
of its step functions — and `bzh:injected-clock` there, whose clock the floor reads. [`./read-cost.md`](./read-cost.md)
`bzh:bulk-reconstitution` — what the pass owes per item once it does run. `bzh:lane-contract` above — what a lane owes
around its body.
