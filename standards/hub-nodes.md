# Hub command nodes

The authoring contract for `executor: hub` — the generic hub command node primitive: the `run:` step shape, the env-var
interface a step's command reads, the outcome protocol that maps a step's stdout/exit code to a routed edge, and the
per-step idempotence a `run:` command must honor. [../domain/graphs.md](../domain/graphs.md) §Node owns the concept — a
node's `executor` facet, and that a hub node is structurally agentless; this file owns the technical schema a change to
a `run:` script or a new hub node is held to, the same relationship [./wire.md](./wire.md) has to a route's timestamp
fields. Each rule follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## The `run:` step shape (`bzh:hub-node-run-shape`)

**Rule.** An `executor: hub` node declares its work as `run:`, a list of steps executed in order, never as a `prompt` a
worker interprets: each step is a `command` string, an optional human-readable `name` (defaults to the step's 1-based
position), and an optional `produces` — a marker name the executor itself records once the step exits 0, and the signal
a later re-run skips that step on (`bzh:hub-node-step-idempotence` below). `run:` is legal only on `executor: hub`; a
hub node must not declare `prompt`, `checks`, or `judgement.prompt`, and must declare a judgement — its outcome choices
are authored exactly like a worker node's own ([../domain/graphs.md](../domain/graphs.md) §Judgement and choices). No
node kind runs an agent turn here or anywhere else in this shape (`bzh:deterministic-shell` in
[../architecture/system-shape.md](../architecture/system-shape.md)).

**Why.** A declared command list is replayable and reviewable text, never a generated one — the same property that makes
the coordinator's own loop deterministic extends to the one node kind the hub runs itself; forbidding the worker-only
fields on a hub node keeps "structurally agentless" enforceable rather than a convention a node could quietly violate.

**Scope.** The step-level `produces` is a different fact from the node-level `produces:` list
([../domain/graphs.md](../domain/graphs.md) §Node) — the node-level list names artifacts a *worker* node is expected to
submit; a hub step's `produces` names a completion marker the executor records on its own, with no content the step
chooses.

**Detect.** `run:` authored on a node whose `executor` isn't `hub`; a hub node also declaring `prompt`, `checks`, or
`judgement.prompt`; a hub node with no judgement at all.

**Do.** `deliver` in `hub/graphs/default.yaml`: `executor: hub` with one `run:` step (`land-every-repo`,
`command: python3 -m blizzard.hub.graphs.scripts.land_default`) and a judgement authoring only the `landed`/`conflict`
choices its script can print.

**Don't.** An `executor: hub` node also carrying `prompt:` or `checks:` — the mint-time validator rejects both as
meaningless on a node no agent ever works.

## The injected env-var contract (`bzh:hub-node-env-contract`)

**Rule.** Every `run:` step's command is invoked with exactly this env — the only channel a step's command has into the
chunk's identity, prior work, and forge credential:

| Var                                                  | Carries                                                                                                                                                                                                                                     |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `BZ_HUB_CHUNK_ID`                                    | The chunk's id.                                                                                                                                                                                                                             |
| `BZ_HUB_WORKDIR`                                     | The per-chunk hub workdir — persists across a node's steps and across a re-run of the same node.                                                                                                                                            |
| `BZ_HUB_NODE_ID`                                     | The exact node's id.                                                                                                                                                                                                                        |
| `BZ_HUB_NODE_NAME`                                   | The node's name.                                                                                                                                                                                                                            |
| `BZ_HUB_EPOCH`                                       | The current attempt's epoch, as a string.                                                                                                                                                                                                   |
| `BZ_HUB_BASE_BRANCH`                                 | The branch the chunk's work lands against.                                                                                                                                                                                                  |
| `BZ_HUB_GIT_COMMITS`                                 | A JSON list of `{repo, branch, commit}` — the chunk's latest commit-pointer artifacts.                                                                                                                                                      |
| `BZ_HUB_ARTIFACT_NAMES`                              | A JSON list of artifact names already recorded for this node — a script's own re-run-skip input, alongside the executor's step-level skip.                                                                                                  |
| `BZ_HUB_MARKER_CALLBACK_URL`                         | `POST {name, content}` records a marker mid-run, authorized by `BZ_HUB_MARKER_TOKEN` below; wrapped by `blizzard hub record-marker NAME [CONTENT]`. A non-2xx response is fatal — the script must raise rather than swallow it and proceed. |
| `BZ_HUB_MARKER_TOKEN`                                | The capability token authorizing that POST: minted per `(chunk, node, epoch)` before this node visit's steps run, sent back as the `X-Blizzard-Marker-Token` header, and revoked once the visit ends.                                       |
| `BZ_FORGE_URL` / `BZ_FORGE_TOKEN` / `BZ_FORGE_OWNER` | The hub's own configured forge credential — present only when the hub is configured with one.                                                                                                                                               |

Beyond these keys a step inherits the hub daemon's own environment, with one strengthened guarantee: the executor
prepends the hub interpreter's own bin directory to `PATH`, so a bare `python3` in a `run:` command always resolves to
the interpreter the hub itself runs under — the one that can import `blizzard` — regardless of how the daemon was
launched (a systemd unit invoking the venv binary by absolute path carries no venv on its inherited `PATH`).

**Why.** A `run:` step is an ordinary subprocess with no access to the hub's domain objects; naming the whole env here
means a graph author never guesses at an undocumented field, and a reviewer can tell a script reading anything else is
reading nothing.

**Detect.** A `run:` script referencing an env var not in this table; a script hardcoding a forge URL or token instead
of reading the injected credential; a marker-write POST sent with no `BZ_HUB_MARKER_TOKEN` header at all; a
`record_marker`-style closure whose POST result is never checked — the discarded-response shape a marker write used to
take, where a dropped or unauthorized write was swallowed and the script proceeded to report success anyway.

**Do.** `land_default.py` reads `BZ_HUB_GIT_COMMITS`/`BZ_HUB_ARTIFACT_NAMES` to compute which repos still need landing
and `BZ_FORGE_URL`/`BZ_FORGE_TOKEN`/`BZ_FORGE_OWNER` to talk to the forge directly — no forge seam, by design
(`bzh:deterministic-shell` in [../architecture/system-shape.md](../architecture/system-shape.md)): this script *is* the
policy. `land_common.MarkerWriter` (the one marker channel every land script holds, as `LandRun.markers`) treats any
non-2xx as fatal, raising rather than returning, so a merge can never land with no durable record of it.

**Don't.** A script assuming a field this table doesn't list — there is nothing else in its environment to read. A
script that posts the marker write and moves on without inspecting the response — a non-2xx there means the write never
happened, and proceeding to print a success choice anyway is exactly the shape issue #230 closed.

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
exactly like a worker's judged choice ([../domain/graphs.md](../domain/graphs.md) §Judgement and choices).

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

## At-least-once, per step (`bzh:hub-node-step-idempotence`)

**Rule.** Every `run:` step's command must be safe to execute more than once with the same intended effect. The
executor's crash contract is at-least-once **per step**, never per script: a `kill -9` between a step's side effect and
its `produces` marker (or a mid-run `record-marker` call) becoming durable re-runs that exact step from its own first
command on the next hub-advance; only a step whose marker already exists is skipped. A step spanning a chunk-sized
dynamic loop — one iteration per repo the chunk submitted, say — marks each iteration's own completion via the mid-run
`record-marker` callback, at the granularity a re-run needs to skip already-done iterations; a single step-level
`produces` cannot express that finer granularity.

**Why.** The `hubnode.after-step.before-marker` and `hubnode.after-marker.before-next` crash points
(`bzh:crash-point-registry` in [../architecture/crash-correctness.md](../architecture/crash-correctness.md)) bracket
exactly this window; a step whose command isn't safe to redo turns an ordinary crash-recovery restart into a double side
effect — a double merge, a double push — with nothing in the design left to catch it.

**Detect.** A `run:` step invoking a non-idempotent side effect (a merge, a push, a non-idempotent POST) with no
`produces` marker and no internal `record-marker` granularity guarding a re-run; a multi-iteration step relying on one
step-level `produces` to gate every iteration at once.

**Do.** `land_default.py` — the reference shape: check every pending repo's mergeable state before pushing any of them,
record a `merged/<repo>` marker via the callback immediately after each push, and treat a PR a re-run finds already
merged as success rather than a fresh conflict (re-pushing a landed merge is a no-op).

**Don't.** A step that pushes every repo in a loop with no per-repo marker — a crash between two repos' pushes re-runs
the step from the top and pushes the first repo a second time.

## See also

- [../domain/graphs.md](../domain/graphs.md) — the conceptual node model this file's schema instantiates: the `executor`
  facet, judgement and choices, and the ids-exact/names-correlate rule an artifact series and a migration key on.
- [../architecture/system-shape.md](../architecture/system-shape.md) — `bzh:deterministic-shell`, the invariant a hub
  node's agentlessness realizes.
- [../architecture/crash-correctness.md](../architecture/crash-correctness.md) — `bzh:crash-point-registry`, the
  `hubnode.*` family these steps' crash points belong to.
- [../verification/blizzard.md](../verification/blizzard.md) — `blizzard:crash-sweep`, which exercises the `hubnode.*`
  points this file's idempotence rule is proven against.
