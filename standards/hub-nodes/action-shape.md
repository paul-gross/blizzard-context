# A hub node's `action:`

What an `executor: hub` node declares as its work, and what it may not declare.

Parent: [../hub-nodes.md](../hub-nodes.md).

## One catalogued `action:`, never a prompt (`bzh:hub-node-action-shape`)

**Rule.** An `executor: hub` node declares its work as one `action:` naming an action in the hub's action catalogue,
with an optional `with:` map carrying only the string or string-list arguments that action declares — every argument it
requires present — never as a `prompt` a worker interprets. `action:` and `with:` are legal only on `executor: hub`; a
hub node must not declare `prompt`, `checks`, or `judgement.prompt`, and must declare a judgement authoring the reserved
`failure` choice and every other choice its action can answer, reserved waits aside. `run:` is retired: a graph naming
it on a hub node is refused at mint, naming `action:` in its place. The mint-time validator rejects each violation, the
worker-only fields as meaningless on a node no agent ever works.

**Why.** A catalogued action is reviewable code whose answers are known before a graph is minted, so validation proves
every answer routes, and forbidding the worker-only fields keeps "structurally agentless" mechanically enforceable
instead of a convention a node could quietly violate.

**Scope.** No node kind here runs an agent turn — the `bzh:deterministic-shell` invariant in
[../../architecture/system-shape.md](../../architecture/system-shape.md). A hub node's outcome choices are authored
exactly like a worker node's own ([../../domain/graphs/edges.md](../../domain/graphs/edges.md)). The markers an action
records are its own effects, not the node-level `produces:` list
([../../domain/graphs/nodes.md](../../domain/graphs/nodes.md)), which names artifacts a worker node is expected to
submit. A stored hub node naming no action is carried onto one by migration where its retired `run:` translates, and
otherwise escalates its chunk `hub-action-missing` rather than running anything.

**Detect.** `action:` or `with:` authored on a node whose `executor` is not `hub`; a hub node naming no `action:`, an
uncatalogued one, or `run:`; a `with:` key the action does not declare, or a required one missing; a hub node also
declaring `prompt`, `checks`, or `judgement.prompt`; a hub node with no judgement, no `failure` choice, or no choice for
an answer its action can give.

**Do.** A `deliver` node that is `executor: hub` with `action: land` and a judgement authoring the
`landed`/`conflict`/`failure`/`inherited-failure` choices `land` can answer.

**Don't.** An `executor: hub` node carrying `prompt: Land every repo` beside its `action:` — the mint-time validator
refuses it, since no agent will ever read the prompt.
