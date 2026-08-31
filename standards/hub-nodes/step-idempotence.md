# A step under crash re-runs

How a `run:` step's command must behave when a crash re-runs it.

Parent: [../hub-nodes.md](../hub-nodes.md).

## Every step's command is safe to redo (`bzh:hub-node-step-idempotence`)

**Rule.** Every `run:` step's command must be safe to execute more than once with the same intended effect. The
executor's crash contract is at-least-once per step, never per script: a `kill -9` between a step's side effect and its
`produces` marker (or a mid-run `record-marker` call) becoming durable re-runs that exact step from its own first
command on the next hub-advance, and only a step whose marker already exists is skipped. A step spanning a chunk-sized
dynamic loop — one iteration per repo the chunk submitted, say — marks each iteration's own completion via the mid-run
`record-marker` callback, at the granularity a re-run needs to skip already-done iterations; a single step-level
`produces` cannot express that finer granularity.

**Why.** The `hubnode.after-step.before-marker` and `hubnode.after-marker.before-next` crash points
(`bzh:crash-point-registry` in [../../architecture/crash-correctness.md](../../architecture/crash-correctness.md))
bracket exactly this window. A step whose command is not safe to redo turns an ordinary crash-recovery restart into a
double side effect — a double merge, a double push — with nothing in the design left to catch it.

**Detect.** A `run:` step invoking a non-idempotent side effect (a merge, a push, a non-idempotent POST) guarded by
neither a `produces` marker nor internal `record-marker` granularity; a multi-iteration step relying on one step-level
`produces` to gate every iteration at once. The `hubnode.*` crash points are exercised by `blizzard:crash-sweep`
([../../verification/blizzard.md](../../verification/blizzard.md)), the verification this rule is proven against.

**Do.** `land_default.py` is the reference shape — it checks every pending repo's mergeable state before pushing any of
them, records a `merged/<repo>` marker via the callback immediately after each push, and treats a PR a re-run finds
already merged as success rather than a fresh conflict.

`garden_deliver.py` is a second shape: its idempotence key is a `garden-delivered` marker written by the hub itself,
inside the same transaction as the delta it materializes, rather than by the executor's own `produces` bookkeeping
afterward — a re-run's POST finds that marker already durable and returns `recorded` having minted nothing a second
time, with no separate re-run-skip logic in the script at all.

**Don't.** A step that pushes every repo in a loop with no per-repo marker — a crash between two repos' pushes re-runs
the step from the top and pushes the first repo a second time.
