# The lane contract

A **lane** is a periodic pass or store-and-forward pass that moves facts toward a sink. On the hub, every pass hosted by
the `Sweep` driver is a lane: the annotation, event-derivation, and materialization reconcilers, the close drain, the
trace export sweep, and the egress sweep. On the runner, every pass that moves facts off the runner is one:
`OutboundDrain`, `TranscriptDrain`, and `LeaseTraceSweep`. The core phases (REAP, PULL, FILL, ADVANCE, RESUME), the
samplers, and `Retention` are not lanes; `bzh:steppable-loop` and `bzh:probe-gated-pass` in
[`../crash-correctness.md`](../crash-correctness.md) and [`../repository-access.md`](../repository-access.md) govern
them. Each rule follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

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
   runner driver catches per pass.
5. **Hosting.** On the runner, a lane whose only sink is the hub is a tick step: the hub client bounds each call, and
   the tick's next phases consume its result. A lane whose sink is operator-configured, such as an exporter, runs on a
   dedicated driver, so a stalled sink never holds the tick. On the hub, every lane is a `Sweep`.

The failure shapes, by sink class:

| Sink class                                                  | Shape                                                                                                                                                                                                                    | Lanes                                                              |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| Operator-configured, with an outage the operator can act on | Whole-pass backoff and an **outage latch**: one failed event when an outage starts, one recovered event when it ends. The first pass seeds the latch from the newest persisted latch, so a restart mid-outage is silent. | Hub trace export sweep, hub egress sweep, runner `LeaseTraceSweep` |
| Per-item outcomes against a forge                           | Per-item backoff, persisted as attempt history and computed with the shared formula, plus per-item events. No latch: one item failing does not mean the sink is down.                                                    | Close drain                                                        |
| The hub as sink, or a local-store converging pass           | Retry on the next pass, with no backoff and no latch. A failed pass costs one bounded request, and an announcement would ride the channel that is failing.                                                               | `OutboundDrain`, `TranscriptDrain`, the three reconcilers          |

**Why.** A lane runs unattended for as long as its sink is down, so every clause bounds a cost that otherwise grows
without limit: an unbounded pass starves its host, an unreplayable item corrupts on the crash the sweep arms, an
announcement per failed pass floods the event log, and a lane that raises into its host takes the host's other work down
with it. One failure shape per sink class keeps an operator's reading of "failing" the same on every lane, and one
shared helper keeps the backoff formula and the latch transitions from drifting apart across copies.

**Detect.** A lane that reads or sends its whole backlog in one pass; a window between an effect and its record with
neither a registry point nor a recorded exemption; a lane whose own fields hold a failure count, a next-due instant, or
a failing flag; a failure event emitted per failed pass, or emitted again after a restart mid-outage; a lane step whose
raise reaches its host; a lane on a sink class that gives it a backoff or latch its class does not name.

**Do.** `TraceExportSweep` and `EgressSweep` (`blizzard/src/blizzard/hub/domain/tracing/sweep.py`,
`blizzard/src/blizzard/hub/domain/egress/sweep.py`) hold an `OutageLatch` from `foundation/lane_retry.py`, ask it
whether a pass is due, and announce only when it says a failure opens or a success closes an outage.
`CloseIntentDrainer` (`blizzard/src/blizzard/hub/domain/work_closure.py`) attempts a fixed number of due intents per
pass and computes each intent's due time with `backoff_delay`. `TranscriptDrain` catches every failure inside `run()`.

**Don't.** A new lane that hand-copies a failure counter, a next-due instant, and a failing flag, then re-implements the
doubling and the open/close transitions beside them, instead of taking the helper. The copies drift: one lane clamps the
doubling and another overflows on a long outage.

**See also.** [`../crash-correctness.md`](../crash-correctness.md) `bzh:steppable-loop` — each lane's pass is one of its
step functions — and `bzh:crash-point-registry` — the family prefix clause 2 names.
[`../repository-access.md`](../repository-access.md) `bzh:probe-gated-pass` — the cost of a converging pass.
[`../clean-architecture.md`](../clean-architecture.md) `bzh:shared-kernel` — where the helper lives.
