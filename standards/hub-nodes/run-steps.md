# A hub node's `run:` steps

What an `executor: hub` node declares as its work, and what it may not declare.

Parent: [../hub-nodes.md](../hub-nodes.md).

## `run:` steps, never a prompt (`bzh:hub-node-run-shape`)

**Rule.** An `executor: hub` node declares its work as `run:` — an ordered list of steps — never as a `prompt` a worker
interprets. `run:` is legal only on `executor: hub`; a hub node must not declare `prompt`, `checks`, or
`judgement.prompt`, and must declare a judgement — the mint-time validator rejects each violation as meaningless on a
node no agent ever works. Each step is a `command` string, an optional human-readable `name` defaulting to the step's
1-based position, and an optional `produces` naming a completion marker the executor itself records once the step exits
0 — the signal a later re-run skips that step on ([./step-idempotence.md](./step-idempotence.md),
`bzh:hub-node-step-idempotence`).

**Why.** A declared command list is replayable, reviewable text rather than a generated one, and forbidding the
worker-only fields keeps "structurally agentless" mechanically enforceable instead of a convention a node could quietly
violate.

**Scope.** No node kind here runs an agent turn — the `bzh:deterministic-shell` invariant in
[../../architecture/system-shape.md](../../architecture/system-shape.md). A hub node's outcome choices are authored
exactly like a worker node's own ([../../domain/graphs/edges.md](../../domain/graphs/edges.md)). The step-level
`produces` is a different fact from the node-level `produces:` list
([../../domain/graphs/nodes.md](../../domain/graphs/nodes.md)): the node-level list names artifacts a worker node is
expected to submit, while a hub step's `produces` is a completion marker the executor records on its own, with no
content the step chooses.

**Detect.** `run:` authored on a node whose `executor` is not `hub`; a hub node also declaring `prompt`, `checks`, or
`judgement.prompt`; a hub node with no judgement at all.

**Do.** The `deliver` node in `src/blizzard/hub/graphs/basic-development-workflow/graph.yaml` is `executor: hub` with
the single `run:` step `land-every-repo` (`command: python3 -m blizzard.hub.graphs.scripts.land_ff`) and a judgement
authoring only the `landed`/`conflict`/`failure` choices its script can print.

**Don't.** An `executor: hub` node carrying `prompt: Land every repo` beside its `run:` list — the mint-time validator
refuses it, since no agent will ever read the prompt.
