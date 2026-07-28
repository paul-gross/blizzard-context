# Workflow graphs

The definition chunks travel: graphs, nodes, edges, judgements, and choices.
Definitions, with the enforceable invariant written in the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).
Part of the [domain model](./index.md).

## Graph

One identity, two parts:

- **An immutable definition** — the nodes, edges, prompts, and judgements. Every edit creates a new graph; an existing definition never changes, so anything pinned to it can trust it forever.
- **Mutable operational metadata beside it** — `enabled`, the graph's only mutable surface.

There is **no graph family or version tree**: graphs are standalone, and any graph may migrate its chunks to any graph so long as the node mapping gets them over.
What looks like "versions of a workflow" is emergent, not modeled: nothing on a graph links it to a successor — a migration is what moves a chunk onto another graph that happens to share its name (which one, when several do, is the `enabled` bullet below) ([work.md](./work.md) §Migration owns how and when a chunk migrates).

- **`enabled` gates being resolved as a migration target.** A retired graph is excluded from every name-based resolution (the default pin at mint, an authored choice's `graph:<name>` target, a migration's target-by-name lookup) and refuses an explicit id-named target too — its own chunks continue undisturbed; only new targeting is blocked. Among the enabled graphs sharing a name, resolution picks the **newest**. Graphs are created enabled.

## Node

One station in one graph — "build", "review", "deliver".
A node belongs to exactly one immutable graph; same-named nodes in different graphs are distinct nodes correlated only by name.
There is no node *type*: what a type would encode is structural — a gate is a node whose judgement is human-judged, and a node whose `executor` is the hub itself is one the hub runs directly, no agent, ever ([standards/hub-nodes.md](../standards/hub-nodes.md)).

| Facet | Meaning |
|-------|---------|
| name | The cross-graph correlator — what migration landing, artifact series, and runner-side gate configuration key on. |
| executor | Who runs the node's steps: a runner (the default), or the hub itself — a hub-executed node declares its steps as `run:`, a shipped command list, never an agent turn ([standards/hub-nodes.md](../standards/hub-nodes.md)). The shipped `deliver` node is one instance of this shape, not a distinct kind. |
| prompt | The node's invariant identity — what a worker at this station is asked to do; the arriving edge contributes arrival context on top. |
| checks | The deterministic checks (tests, lint) the **runner** executes at worker exit, before the exit judgement — each result a durable fact, injected into the judgement so the worker judges against mechanical truth, and a `requires_checks` choice may be gated on them (#114). Authoring `checks:` (necessarily toolchain commands) makes a graph application-specific by design — see `bzh:app-agnostic-graphs`. Node-level `checks_cwd` (where they run, relative to the leased env's workdir) and `checks_timeout` (per-check seconds) configure them; both are legal only on a node that declares `checks:`. |
| judgement | How the node's exit is judged and the choices it can produce — see [Judgement and choices](#judgement-and-choices). |
| retries | The bounded failure budget — crashes, verdict-less exits, reaps — and where exhaustion escalates; a *judged* failure edge never consumes it. |
| produces | The artifact names the node is expected to submit ([artifacts.md](./artifacts.md)) — on a worker node, the prompt must instruct the worker to submit each by name ([standards/worker-nodes.md](../standards/worker-nodes.md)). |
| session | Whether the node's steps resume the chunk's agent session or start cold, and which session: `fresh` spawns a brand-new session on every entry; `resume` (the default) resumes the chunk's most-recent session on this runner, whichever node-step last ran, regardless of which node; `resume:<node>` resumes the most-recent session recorded for a lease of the named node — e.g. `build` re-entered after a fresh-session `review` resumes its own prior build session, not the reviewer's — and graph validation rejects a `<node>` absent from the graph. Any resume form falls back to spawning fresh when no matching session exists (first arrival at the graph, a chunk reassigned to a runner that never held the session, or the named node has never run) — never an error, never a stall. Governs node **entry** only: a within-node retry always spawns fresh. |

## Edge

A directed, outcome-keyed connection between two nodes of the **same graph** — cross-graph movement is a migration, never an edge (`bzh:migration-not-transition` in [work.md](./work.md)).

- **Keyed by exactly one choice** of the source node's judgement, and every choice a judgement can produce has exactly one edge — resolution is checked when the graph is created, so an edge can never dangle and a judgement can never select nothing.
- **Exactly one entry node** per graph; **cycles are intentional** — build → review → build is the shape, not a validation error.
- An edge carries **arrival context**: prose appended to the target node's prompt so the worker knows how it got there.

## Judgement and choices

The evaluation at a node's exit that selects the outgoing edge.

- **Judged by the worker** (the default): elicited when the worker declares done, informed by the node's `checks:` (run at exit and injected — the `checks` facet above); the worker selects exactly one of the node's choices. A missing or unparseable selection is a **failure, not a judgement** — it consumes a retry rather than an edge. So is selecting a `requires_checks` choice while any check is red (below): the engine refuses the edge and re-elicits with the red evidence in hand, consuming a retry exactly like an unparseable verdict — never an engine-owned override of the worker's routing.
- **Judged by a human**: the structural mark of a gate — the person renders the judgement by picking from the same choices, presented as buttons ([humans.md](./humans.md)).
- **Judged by a hub-executed node's own script**: its declared `run:` steps select one of the node's authored choices by exit code and stdout, the same fused choice/edge shape a worker's judgement uses — e.g. the shipped `deliver` node's script selecting `landed` or `conflict` ([artifacts.md](./artifacts.md), [standards/hub-nodes.md](../standards/hub-nodes.md)).

A **choice** is one selectable outcome of one node's judgement, scoped to that judgement — never a global registry: `pass` in build and `pass` in review are different choices that happen to share a name.
Each choice keys exactly one outgoing edge; its description is what sharpens a worker's judgement and what a gate renders as button text.

- **A choice may require green checks.** A choice may declare `requires_checks: true` (e.g. build's `pass`; its `fail` would not) — the engine then refuses to accept that edge while any of the node's `checks:` is red, treating the selection as a failure that consumes a retry and re-queues a fresh attempt (never accepting the edge, never overriding the worker's choice). A red check reported through a **non-gated** choice (`fail`, with the worker's assessment of *why*) routes normally — that context-rich path stays open. Graph validation rejects `requires_checks` on a node with no `checks:` and on hub/human-judged nodes.
- **A choice may target another graph.** A choice's `to:` normally names a sibling node or the reserved terminal; it may instead name `graph:<name>` — a cross-graph **migration** target. Taking that choice re-pins the chunk to the named graph and lands it at the target's landing node (name-matched, else the target's entry), the landed node's disposition governed by [work.md](./work.md) §Landing is by name — recording a migration fact, never a transition — so `bzh:migration-not-transition` in [work.md](./work.md) still holds (the authored choice carries the target; the *movement* is a migration, not an edge to another graph's node, which stays forbidden). A choice may also carry an optional `model:` the migration re-pins the chunk to. The target is resolved by **name** when taken (late-bound, the same binding ingest uses, `bzh:ids-exact-names-correlate`), so authoring a choice whose target graph is not yet minted is a mint-time warning, not an error.

## Ids are exact, names correlate (`bzh:ids-exact-names-correlate`)

**Rule.** Exact references — a transition's nodes, an artifact's provenance, an edge's choice — carry **ids**, which pin one immutable definition; continuity across graphs — migration landing, artifact series, runner-side gate selection — keys on **names**. Never the reverse.

**Why.** An id names exactly one thing in exactly one immutable graph, so an exact reference can never dangle or drift; a name is the only thing same-purpose entities in different graphs share, so it is the only key correlation can use.

**Detect.** A design that matches an exact reference by name — two graphs' `build` nodes conflated — or that correlates across graphs by id, such as a migration expecting the target graph to contain the same node id.

**Do.** A transition records the exact ids of its two nodes; an authored-choice migration lands the chunk on the target graph's node whose *name* matches the one it left.

**Don't.** Key an artifact series on the node id — the series would break at every migration or re-published graph, though the work is the same station's.

## See also

- [./work.md](./work.md) — the chunk that travels this definition, and the migration that moves it between definitions.
- [../standards/hub-nodes.md](../standards/hub-nodes.md) — the technical authoring schema for a hub-executed node: the `run:` step shape, the injected env-var contract, the outcome protocol, and the per-step idempotence rule.
- [../standards/worker-nodes.md](../standards/worker-nodes.md) — the technical authoring contract for a worker node's `produces:` list: the prompt's declaration instruction, the fallback, and the enforcement backstop.
