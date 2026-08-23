# Workflow graphs

This spoke owns blizzard's two rules for authored workflow graphs; the macro-shape hub is
[../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Graphs are application-agnostic (`bzh:app-agnostic-graphs`)

**Rule.** A reusable workflow graph declares the shape of the work — node roles, what each node produces and under what
name, the declaration protocol, and the choice names a judgement selects between — never how a particular application is
built, tested, linted, or branched. The same reusable graph must drive twenty unrelated applications unchanged, and
anything that would stop it belongs in the workspace the work happens in.

**Why.** Blizzard leases a worker a poly-repo feature environment, not a checkout, and is not a build system — it holds
no model of any application. The repo is also the only place a toolchain answer stays correct, changing with that repo's
toolchain with no graph re-mint and no fleet-wide edit.

**Exception.** A graph may deliberately opt out of reusability by authoring `checks:` (necessarily toolchain commands):
the engine executes them at worker exit and gates a `requires_checks` choice on their results — real enforcement instead
of trusting the worker's self-report — at the price of forking per application and per differently-built repo, a trade
fit only for a single-application deployment, never for a graph meant for reuse. In a single-application graph a
deliberate `checks:` is the sanctioned opt-in, not a violation; what still violates there is toolchain specifics in
prompt prose rather than the `checks:` field, or naming an application file path.

**Scope.** Authored graph YAML, its prompts, and the `artifacts:` content a mint bakes in — authored text that reaches
the worker verbatim, fetched by name rather than carried in the prompt, and held to the same reusability bar as prompt
prose. The fleet protocol is not application knowledge and stays in any graph: the `blizzard runner` verbs —
`artifact create`, `artifact commit`, `artifact list` and `get` (with node or graph `--scope`), `ask`, `work-items`, and
chunk history — are blizzard's own surface, identical across every application it drives (`blizzard runner attach` is a
deprecated alias for `artifact create` — `bzh:worker-node-attach-instruction` in
[../../standards/worker-nodes.md](../../standards/worker-nodes.md) owns it). Naming a git or gh operation directly is
likewise permitted — VCS and forge mechanics are as invariant across applications as the fleet protocol — but permitted
is not warranted: state the check, and name the incantation only where the choice it encodes is the instruction.

**Detect.** In a graph meant to be reusable: a concrete toolchain command in `checks:` or prompt text (`mise run test`,
`pytest`); a prompt naming a language, framework, directory layout, or branch-naming convention; a graph whose name or
prose ties it to one application; a node instructing a specific file path inside the application; or a baked
`artifacts:` entry doing any of the same.

**Do.** Instruct the obligation and let the repo supply the specifics — "verify the change through the methods this
repository declares, and treat a missing method as a gap to surface" — while a single-application deployment wanting
enforced checks authors `checks:` on the node and gates its pass choice with `requires_checks: true`. Spell a command
out only when the exact predicate is the instruction and plausible alternatives answer a different question
(`git merge-base --is-ancestor`), when it encodes a policy rather than a mechanic (`--force-with-lease` over a bare
`--force`), or when it names a fact the worker cannot otherwise derive (`gh pr view --json mergeCommit`).

**Don't.** Author toolchain `checks:` — or toolchain-naming prompt prose — on a graph meant to be reused: the graph then
forks per application, which is the violation the rule exists to prevent. And don't spell out routine commands — they
cost tokens on every spawn and freeze assumptions the surrounding prose hedges, like a literal `origin/master` beside
"unless the repo records another".

**See also.** `bzh:pluggable-seams`, one level up — a reusable graph depends on the abstraction "this node verifies its
work", never on a concrete verification command.

## Graph-scope reads are local (`bzh:graph-scope-reads-local`)

**Rule.** A graph's baked-in `artifacts:` declarations reach the worker with no hub call in the read path: the mint
stores each entry's already-inlined content, the node envelope carries the whole set, `Spawner._mint` pins that set into
the runner's own store as it mints the lease, and the worker's `--scope graph` read is answered from that pin alone,
keyed on the lease's `graph_id`. Keying the pin on `graph_id`, not the lease, lets one copy serve every chunk and
attempt on that mint, even a lease pinned to a mint the graph's name has since moved past.

**Why.** A mint is immutable, so the hub never holds a newer answer; and a declaration authored to be consulted
repeatedly (a docket, a rubric) would otherwise put a round-trip — and a hub outage — in the path of prose the runner
already holds.

**Scope.** Node scope keeps its hub-proxied forward (the worker holds no hub credential of its own), so only the graph
half is local; node-scope artifacts are produced per attempt, the hub alone holds their newest version, and the mint
itself remains the hub's — the rule binds only the declarations' path from envelope to mint-time pin to the worker's
read route.

**Detect.** A graph-scope read path that consults the hub — a proxy forward, an envelope re-fetch, a re-read call, or a
design leaving the declarations off the envelope; or a graph-scope read that fails when the hub is unreachable.

**Do.** `_graph_rows` in `src/blizzard/runner/api/artifacts.py` resolves the rows through
`IReadRunnerStore.graph_artifacts_for_graph(lease.graph_id)` with no `HubProxy`; the service test
`test_graph_scoped_artifact_reads_from_the_runners_own_pin_with_the_hub_unreachable` holds that read with the hub
unreachable.

**Don't.** Answering graph scope through the same hub-proxy forward node scope uses, on the grounds that one read path
is simpler than two — every declaration read then fails with the hub, which is the property the rule exists to buy.

**See also.** `bzh:graph-artifact-pointer-fallback` in
[../../standards/worker-nodes.md](../../standards/worker-nodes.md) owns the fallback a prompt pointing at a baked
declaration owes, because a lease pinned before the runner recorded the declarations reads an empty pin.
