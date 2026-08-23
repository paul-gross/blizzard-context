# At-least-once, per step

Parent: [../hub-nodes.md](../hub-nodes.md).

## At-least-once, per step (`bzh:hub-node-step-idempotence`)

**Rule.** Every `run:` step's command must be safe to execute more than once with the same intended effect. The
executor's crash contract is at-least-once **per step**, never per script: a `kill -9` between a step's side effect and
its `produces` marker (or a mid-run `record-marker` call) becoming durable re-runs that exact step from its own first
command on the next hub-advance; only a step whose marker already exists is skipped. A step spanning a chunk-sized
dynamic loop — one iteration per repo the chunk submitted, say — marks each iteration's own completion via the mid-run
`record-marker` callback, at the granularity a re-run needs to skip already-done iterations; a single step-level
`produces` cannot express that finer granularity.

**Why.** The `hubnode.after-step.before-marker` and `hubnode.after-marker.before-next` crash points
(`bzh:crash-point-registry` in [../../architecture/crash-correctness.md](../../architecture/crash-correctness.md))
bracket exactly this window; a step whose command isn't safe to redo turns an ordinary crash-recovery restart into a
double side effect — a double merge, a double push — with nothing in the design left to catch it.

**Detect.** A `run:` step invoking a non-idempotent side effect (a merge, a push, a non-idempotent POST) with no
`produces` marker and no internal `record-marker` granularity guarding a re-run; a multi-iteration step relying on one
step-level `produces` to gate every iteration at once.

**Do.** `land_default.py` — the reference shape: check every pending repo's mergeable state before pushing any of them,
record a `merged/<repo>` marker via the callback immediately after each push, and treat a PR a re-run finds already
merged as success rather than a fresh conflict (re-pushing a landed merge is a no-op).

**Don't.** A step that pushes every repo in a loop with no per-repo marker — a crash between two repos' pushes re-runs
the step from the top and pushes the first repo a second time.
