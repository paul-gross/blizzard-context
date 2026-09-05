# A hub step's outcome

How a step's output selects a routed choice, and what happens when it polls or bounces the chunk.

Parent: [../hub-nodes.md](../hub-nodes.md).

## The last stdout line, or a reserved literal (`bzh:hub-node-outcome-protocol`)

**Rule.** A step's last non-blank stdout line is the node's authored choice when it names one of the node's judgement
choices; the resulting choice routes through the node's authored edges exactly like a worker's judged choice
([../../domain/graphs/edges.md](../../domain/graphs/edges.md)). A step exiting 0 without naming a choice falls through
to the next step, and a run in which no step ever names one defaults to the reserved `success` choice. A step exiting
nonzero always yields `failure`, the other reserved default, unless its last stdout line explicitly names one of the
node's own choices — a nonzero exit can never select a success outcome by accident, however the script prints.

Exit 0 with the last line reading the reserved literal `pending` is neither success nor failure: no marker is recorded,
no transition happens, the poll-attempt fact is recorded, and the fleet-wide `hub_exec_slot` is released immediately.
`pending`, like `success` and `failure`, is machinery-reserved and never authored as one of a node's own choices. After
a `pending`, the whole node re-runs — skipping any step whose `produces` marker already exists
([./step-idempotence.md](./step-idempotence.md), `bzh:hub-node-step-idempotence`) — once `poll_interval` has elapsed
since the last attempt (default 30s, overridable per node). Pending itself spends no retry and no bounce budget; only a
poll timeout or an incomplete-delivery crossing does.

Exceeding `poll_timeout` (default 30 minutes, measured from the first recorded pending attempt) stops polling and kicks
the chunk back: a bounce fact is recorded and the chunk re-routes through the node's `failure` edge. A chunk is also
kicked back when an authored edge routes to a non-terminal node while any repo among the node's own commits has no
`merged/<repo>` marker artifact recorded yet — the convention a landing script's `record-marker` calls are expected to
follow. This incomplete-delivery kick-back records its bounce fact and a `bounce-envelope` artifact but lets the chunk
travel the authored choice's own edge — it is detected from the landed-marker fact, never from the choice name, so no
outcome name is privileged. Either kick-back escalates to `needs_human` once the node's `bounce_cap` (default 5,
overridable per node) is crossed.

**Why.** A subprocess has no structured return channel but stdout and an exit code, and fixing "last stdout line, or a
reserved literal" as the entire vocabulary lets a script report freely to a human on stderr while still selecting
exactly one router-legible outcome. The shared bounce-cap ladder keeps a stuck or repeatedly-conflicting delivery from
bouncing a chunk forever.

**Detect.** A `run:` script printing its choice anywhere but the last stdout line; a node authoring `pending` as one of
its own choices; a script relying on exit code alone to select among more than the two reserved defaults.

**Do.**

- `land_default.py` prints `conflict` before its push stage ever starts, so nothing lands when one repo is dirty.
- `land_pr_ci.py` prints `pending` while any repo's PR is not yet `mergeable_state: clean` and no repo's check runs have
  completed with a terminal conclusion; prints `conflict` immediately once a repo's PR reads `dirty` — a real merge
  conflict — rather than waiting out `poll_timeout`; prints `failure` immediately once a `blocked`/`unstable` repo's
  check run has completed failing; and prints `landed` once every repo has merged.

**Don't.** A land script that prints `landed` and then a trailing summary line to stdout — the summary is now the last
line, names no choice, and the step falls through as if it had said nothing.
