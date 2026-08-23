# Nodes

A node is one station in one graph, in the definition routed from [../graphs.md](../graphs.md); same-named nodes in
different graphs are distinct, correlated only by name. Definitional — a taxonomy of the node's facets and what each
governs (`canon:rule-shape` §File kinds). Part of the [domain model](../index.md). There is no node type — the
distinctions are structural: a gate is a node with a human-judged judgement, a hub-executed node one whose executor is
the hub.

The facets:

- **`name`** — the cross-graph correlator: migration landing, artifact series, and runner-side gate configuration key on
  it.
- **`prompt`** — the node's invariant identity: what a worker at this station is asked to do. The arriving edge adds
  arrival context.
- **`session`** — how the worker's session starts on entry: `fresh` spawns a new session every time, and `resume` (the
  default) resumes the chunk's most-recent session on this runner. Either token may carry a name — `fresh:<name>`
  references a declared session, and `resume:<name>` names a declared session or a node, continuing the declared lineage
  or resuming the named node's most-recent leased session ([./declared-sessions.md](./declared-sessions.md) owns how the
  name resolves), and validation rejects a `<node>` the graph does not carry or a `<session>` naming no declaration. Any
  resume form falls back to spawning fresh when no matching session exists — never an error or stall. `session` governs
  entry only: a within-node retry always spawns fresh, and an operator restart forces a fresh session for the visit it
  lands ([../work/restart.md](../work/restart.md)).
- **`executor`** — names who runs the steps: a runner (the default) or the hub. A hub-executed node declares `run:`
  command steps, never an agent turn (contract: [../../standards/hub-nodes.md](../../standards/hub-nodes.md)); the
  shipped deliver node is just this shape.
- **`checks`** — deterministic commands the runner runs at worker exit and injects into the exit judgement as durable
  facts, so the worker judges against mechanical truth; a `requires_checks` choice may gate on them. `checks_cwd` (where
  checks run, relative to the leased env's workdir) and `checks_timeout` (per-check seconds) configure checks and are
  legal only on a node declaring `checks:`. Authoring `checks:` makes a graph application-specific by design — checks
  are necessarily toolchain commands (`bzh:app-agnostic-graphs` in
  [../../architecture/system-shape.md](../../architecture/system-shape.md)).
- **`produces`** — names the artifacts the node must submit ([../artifacts.md](../artifacts.md)); a worker node's prompt
  must instruct submitting each by name ([../../standards/worker-nodes.md](../../standards/worker-nodes.md)).
- **`retries`** — the bounded failure budget — crashes, verdict-less exits, reaps — and where exhaustion escalates; a
  judged failure edge never consumes it.
- **`judgement`** — how the exit is judged and the choices it produces — owned by [./edges.md](./edges.md).
