# An action pass under crash re-runs

How a hub node's action must behave when a crash re-runs its pass.

Parent: [../hub-nodes.md](../hub-nodes.md).

## Every pass is safe to redo (`bzh:hub-node-step-idempotence`)

**Rule.** Every hub action's pass must be safe to execute more than once with the same intended effect. The executor's
crash contract is at-least-once per pass: a `kill -9` between an effect reaching the outside world and its marker
becoming durable re-runs the whole pass on the next hub-advance, and nothing but the action's own markers tells the
re-run what is already done. An action spanning a chunk-sized dynamic loop — one iteration per repo the chunk submitted,
say — records each iteration's own marker as soon as that iteration's effect lands, and skips any iteration whose marker
its visit already shows, at the granularity a re-run needs.

**Why.** The `action.after-effect.before-write` and `action.after-write.before-resume` crash points
(`bzh:crash-point-registry` in [../../architecture/crash-correctness.md](../../architecture/crash-correctness.md))
bracket exactly this window. An action whose pass is not safe to redo turns an ordinary crash-recovery restart into a
double side effect — a double merge, a double push — with nothing in the design left to catch it.

**Detect.** An action invoking a non-idempotent side effect (a merge, a push, a non-idempotent POST) guarded by no
marker it records and checks; a multi-iteration action recording one marker for every iteration at once. The `action.*`
crash points are exercised by `blizzard:crash-sweep` ([../../verification/blizzard.md](../../verification/blizzard.md)),
the verification this rule is proven against.

**Do.** `land` is the reference shape — it checks every pending repo's mergeable state before pushing any of them,
records a `merged/<repo>` marker immediately after each push, skips a repo whose marker already exists, and treats a PR
a re-run finds already merged as success rather than a fresh conflict.

`garden_deliver` is a second shape: its idempotence key is a `garden-delivered` marker written by the hub itself, inside
the same transaction as the delta it materializes — a re-run's POST finds that marker already durable and answers
`recorded` having minted nothing a second time, with no separate re-run-skip logic in the action at all.

**Don't.** An action that pushes every repo in a loop with no per-repo marker — a crash between two repos' pushes
re-runs the pass from the top and pushes the first repo a second time.
