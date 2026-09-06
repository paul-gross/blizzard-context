# Workflow graphs

This spoke owns blizzard's rule for authored workflow graphs; the macro-shape hub is
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
`artifact create`, `artifact commit`, `artifact list` and `get` (with node, graph, or system `--scope`), `ask`,
`work-items`, `garden findings`, `garden proposals`, and chunk history — are blizzard's own surface, identical across
every application it drives (`blizzard runner attach` is a deprecated alias for `artifact create` —
`bzh:worker-node-attach-instruction` in
[../../standards/worker-nodes/declarations.md](../../standards/worker-nodes/declarations.md) owns it). Naming a git or
gh operation directly is likewise permitted — VCS and forge mechanics are as invariant across applications as the fleet
protocol — but permitted is not warranted: state the check, and name the incantation only where the choice it encodes is
the instruction.

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
work", never on a concrete verification command. `bzh:graph-scope-reads-local` and `bzh:system-scope-reads-live` in
[./artifact-scopes.md](./artifact-scopes.md) own what a graph-scope read costs against a system-scope read's opposite
liveness rule.
