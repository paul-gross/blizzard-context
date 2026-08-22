# What a graph carries

The two rules governing authored workflow graphs: the application knowledge a reusable graph must not hold, and the read
path its baked-in artifact declarations take to the worker. [`../system-shape.md`](../system-shape.md) owns the
macro-shape invariants these two rules sit under, and each rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## A graph carries workflow, never application knowledge (`bzh:app-agnostic-graphs`)

**Rule.** A **reusable** workflow graph declares the *shape of the work* — node roles, what each node produces and under
what name, the declaration protocol, and the choice names a judgement selects between — and never how a particular
application is built, tested, linted, or branched: the same reusable graph must drive twenty unrelated applications
unchanged, and anything that would stop it belongs in the workspace the work happens in, not the graph. A graph **may**
deliberately opt out of that reusability by authoring `checks:` (necessarily toolchain commands): the engine executes a
node's `checks:` at worker exit and gates a `requires_checks` choice on their results, so `checks:` is a real enforced
seam — but a graph that authors it thereby becomes **application-specific by design**, forking per application (and per
repo when a chunk spans repos that build differently). That opt-out is a narrow, deliberate trade — reusability for
mechanical enforcement — appropriate only to a single-application deployment (e.g. this workspace's own dogfood fleet),
never to a graph meant to be reused.

**Why.** Blizzard orchestrates agents working in a **poly-repo capable workspace** — a worker is leased a feature
environment, not a checkout, and one chunk may span several repos at once. Blizzard is not a build system and holds no
model of any application in that workspace. The moment a *reusable* graph names a toolchain, that graph forks per
application, and it forks again per repo the instant a chunk spans two repos that build differently; the repo is also
the only place the answer stays correct, changing when that repo's toolchain changes with no graph re-mint and no
fleet-wide edit. This is the same inversion as `bzh:pluggable-seams`, one level up — a reusable graph depends on the
abstraction "this node verifies its work", never on a concrete verification command. Authoring `checks:` is knowingly
accepting the fork in exchange for the engine enforcing "checks are green" mechanically instead of trusting the worker's
self-report — a cost worth paying only where the fleet drives one known application.

**Scope.** Governs authored graph YAML, its prompts, and the `artifacts:` content a mint bakes in — a third class of
authored text that reaches a worker session verbatim, fetched by name rather than carried in the prompt, and held to the
same reusability bar as prompt prose. The **fleet protocol** is not application knowledge and stays in the graph:
`blizzard runner artifact create --name <n>` (an asset), `blizzard runner artifact commit` (a git commit),
`blizzard runner artifact list`/`get` (reading declared inputs back, narrowed to node or graph scope with `--scope`;
`bzh:graph-scope-reads-local` below owns what a graph-scope read costs), `blizzard runner ask`, the work-item proxy
(`blizzard runner work-items`), and `blizzard runner chunk history` (the chunk's own transition/migration/bounce
timeline) are blizzard's own surface, identical across every application it drives. `blizzard runner attach` is a
deprecated alias for `artifact create` ([../../standards/worker-nodes.md](../../standards/worker-nodes.md)
`bzh:worker-node-attach-instruction`) — no packaged prompt names it. Naming a `git`/`gh` operation directly is
permitted, not a violation: VCS and forge mechanics are as invariant across applications as the fleet protocol itself,
unlike a language-specific toolchain. But permitted is not the same as warranted, and the packaged prompts spend that
permission narrowly: **state the check, name the incantation only where the choice it encodes is the instruction.** A
competent agent writes `git status`, `git fetch`, or a PR-state read from the sentence that asks for it, so spelling
those out costs tokens on every spawn and — worse — freezes an assumption the surrounding prose is careful to hedge (a
literal `origin/master` beside prose that says "unless the repo records another"). Spell a command out when the exact
predicate *is* the instruction and the plausible alternatives answer a different question
(`git merge-base --is-ancestor`, where comparing tips or grepping log is a different check), when it is a policy rather
than a mechanic (`--force-with-lease` over a bare `--force`), or when it names a fact the worker cannot otherwise derive
(`gh pr view --json mergeCommit`, the only handle on the merge commit a gate check keys on).

**Detect.** In a graph meant to be **reusable**: a concrete toolchain command in `checks:` or prompt text
(`mise run test`, `npm run lint`, `pytest`); a prompt naming a language, framework, directory layout, or branch-naming
convention; a graph whose name or prose ties it to one application; a node instructing a specific file path inside the
application; a baked `artifacts:` entry doing any of the same, which reads to the worker exactly as prompt prose does.
In a **single-application** graph a deliberate `checks:` is **not** this violation — it is the sanctioned, enforced
opt-in below; what still violates even there is smuggling toolchain specifics into *prompt prose* rather than the
`checks:` field, or a prompt naming a file path inside the application.

**Do.** For a reusable graph, instruct the *obligation* and let the repo supply the specifics — "verify the change
through the methods this repository declares, and treat a missing method as a gap to surface"; a competent agent reads
the repo's own conventions, and blizzard's job is the loop around the work, not teaching the agent to do it. For a
single-application deployment that wants the engine to enforce green checks mechanically, author `checks:` on the node
and gate its `pass` choice with `requires_checks: true` — accepting, deliberately, that the graph is thereby
application-specific (it forks per application and per differently-built repo).

**Don't.** Author `checks: [mise run lint, mise run test]` on a build node of a graph you intend to **reuse** across
applications, or a prompt telling the worker to run named toolchain commands — both bind a reusable graph to one repo's
tooling, the reusability the rule protects. The engine executes `checks:` and gates on them, so the enforcement is real
— but so is the per-application fork it imposes, which is precisely why it belongs only in a single-application graph,
never a reusable one.

## A graph-scope artifact read never leaves the runner (`bzh:graph-scope-reads-local`)

**Rule.** A graph's baked-in `artifacts:` declarations reach the worker with no hub call in the read path: the mint
stores each entry's already-inlined content, the node envelope carries the whole set, `Spawner._mint` pins that set into
the runner's own store as it mints the lease, and the worker's `--scope graph` read is answered from that pin alone,
keyed on the lease's `graph_id`. Node scope keeps its hub-proxied forward — the worker holds no hub credential of its
own — so only the graph half is local.

**Why.** A mint is immutable, so the hub never holds a newer answer worth fetching, and a declaration authored to be
consulted repeatedly (a docket, a rubric) would otherwise put a round-trip — and a hub outage — in the path of prose the
runner is already holding. Keying the pin on `graph_id` rather than the lease is what lets one copy serve every chunk
and every attempt on that mint, including a lease pinned to a mint the graph's name has since moved past.

**Scope.** The declarations' path only — envelope → mint-time pin → the worker's read route. The mint itself is the
hub's, and node-scope artifacts are unaffected: they are produced per attempt, so the hub is the only place their newest
version exists.

**Detect.** A graph-scope read path that consults the hub — a proxy forward, an envelope re-fetch, or a "re-read the
declarations" call; a design that leaves the declarations off the envelope and has the runner ask the hub for them at
spawn or at read time; a graph-scope read that fails when the hub is unreachable.

**Do.** `_graph_rows` (`blizzard/src/blizzard/runner/api/artifacts.py`) resolves the rows through
`IReadRunnerStore.graph_artifacts_for_graph(lease.graph_id)` and reaches no `HubProxy`;
`blizzard/tests/service/test_runner_service.py::test_graph_scoped_artifact_reads_from_the_runners_own_pin_with_the_hub_unreachable`
holds that with the hub unreachable, beside a node-scope read of the same lease that `503`s under the same outage.

**Don't.** Answer graph scope through the same `HubProxy` forward node scope uses, on the grounds that one read path is
simpler than two — every declaration read then fails with the hub, which is the property this rule exists to buy.

**See also.** [`../../standards/worker-nodes.md`](../../standards/worker-nodes.md) `bzh:graph-artifact-pointer-fallback`
— the fallback a prompt pointing at a declaration owes, because a lease pinned before the runner recorded the mint's
declarations reads an empty pin.
