# The `run:` step shape

Parent: [../hub-nodes.md](../hub-nodes.md).

## The `run:` step shape (`bzh:hub-node-run-shape`)

**Rule.** An `executor: hub` node declares its work as `run:`, a list of steps executed in order, never as a `prompt` a
worker interprets: each step is a `command` string, an optional human-readable `name` (defaults to the step's 1-based
position), and an optional `produces` — a marker name the executor itself records once the step exits 0, and the signal
a later re-run skips that step on (`bzh:hub-node-step-idempotence` below). `run:` is legal only on `executor: hub`; a
hub node must not declare `prompt`, `checks`, or `judgement.prompt`, and must declare a judgement — its outcome choices
are authored exactly like a worker node's own ([../../domain/graphs/edges.md](../../domain/graphs/edges.md)). No node
kind runs an agent turn here or anywhere else in this shape (`bzh:deterministic-shell` in
[../../architecture/system-shape.md](../../architecture/system-shape.md)).

**Why.** A declared command list is replayable and reviewable text, never a generated one — the same property that makes
the coordinator's own loop deterministic extends to the one node kind the hub runs itself; forbidding the worker-only
fields on a hub node keeps "structurally agentless" enforceable rather than a convention a node could quietly violate.

**Scope.** The step-level `produces` is a different fact from the node-level `produces:` list
([../../domain/graphs/nodes.md](../../domain/graphs/nodes.md)) — the node-level list names artifacts a *worker* node is
expected to submit; a hub step's `produces` names a completion marker the executor records on its own, with no content
the step chooses.

**Detect.** `run:` authored on a node whose `executor` isn't `hub`; a hub node also declaring `prompt`, `checks`, or
`judgement.prompt`; a hub node with no judgement at all.

**Do.** `deliver` in `hub/graphs/default.yaml`: `executor: hub` with one `run:` step (`land-every-repo`,
`command: python3 -m blizzard.hub.graphs.scripts.land_default`) and a judgement authoring only the `landed`/`conflict`
choices its script can print.

**Don't.** An `executor: hub` node also carrying `prompt:` or `checks:` — the mint-time validator rejects both as
meaningless on a node no agent ever works.
