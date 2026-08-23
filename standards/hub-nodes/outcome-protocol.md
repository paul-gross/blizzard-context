# The outcome protocol

Parent: [../hub-nodes.md](../hub-nodes.md).

## The outcome protocol (`bzh:hub-node-outcome-protocol`)

**Rule.** A step's own **last non-blank stdout line** is the node's authored choice when it names one of the node's
judgement choices; a step exiting 0 with no such line falls through to the next step, and a run where no step ever names
one defaults to the reserved `success` choice; a step exiting nonzero is always `failure`, the other reserved default,
unless its last line explicitly names one of the node's own choices. Exit 0 with the last line reading the reserved
literal `pending` is neither success nor failure: no marker, no transition — the poll-attempt fact is recorded, the
fleet-wide `hub_exec_slot` is released immediately, and the whole node re-runs (skipping any step whose `produces`
marker already exists) once `poll_interval` has elapsed since the last attempt (default 30s, overridable per node).
`pending` is never authored as a node's own choice — like `success`/`failure` it is machinery-reserved. Exceeding
`poll_timeout` (default 30 minutes, measured from the *first* recorded pending attempt) stops polling and kicks the
chunk back, exactly as an authored edge to a non-terminal node does while any of that node's own commits' repos has no
`merged/<repo>` marker artifact recorded yet — the convention a landing script's `record-marker` calls are expected to
follow: both record a bounce fact and re-route through the node's `failure` edge, escalating to `needs_human` once the
node's `bounce_cap` (default 5, overridable per node) is crossed. Pending itself spends no retry and no bounce budget;
only a timeout or an incomplete-delivery crossing does. The resulting choice routes through the node's authored edges
exactly like a worker's judged choice ([../../domain/graphs/edges.md](../../domain/graphs/edges.md)).

**Why.** A subprocess has no structured return channel but stdout and an exit code; fixing "last stdout line, or a
reserved literal" as the entire vocabulary lets a script report freely to a human on stderr while still selecting
exactly one router-legible outcome, and the shared bounce-cap ladder keeps a stuck or repeatedly-conflicting delivery
from bouncing a chunk forever.

**Detect.** A `run:` script printing its choice anywhere but the last stdout line; a node authoring `pending` as one of
its own choices; a script relying on exit code alone to select among more than the two reserved defaults.

**Do.** `land_pr_ci.py` prints the reserved `pending` while any repo's PR isn't yet `mergeable_state: clean` and no
repo's check runs have completed with a terminal conclusion, `conflict` immediately once a repo's PR reads `dirty` — a
real merge conflict — rather than waiting out `poll_timeout`, `failure` immediately once a `blocked`/`unstable` repo's
check run has completed failing rather than waiting out `poll_timeout` (issue #232), and `landed` once every repo has
merged; `land_default.py` prints `conflict` before its push stage ever starts, so nothing lands when one repo is dirty.

**Don't.** A script exiting nonzero while printing `landed` to try to force that edge — a nonzero exit only ever selects
one of the node's own explicitly-authored choices or falls back to `failure`, never a success outcome by accident.
