# Worker command nodes

The authoring contract for a worker node — `executor: runner` (the default, [../domain/graphs.md](../domain/graphs.md)
§Node) — that declares a `produces:` entry or points its worker at a graph-scoped declaration: the declaration
instruction its prompt owes the worker (`blizzard runner artifact create` for an asset,
`blizzard runner artifact commit` for a git commit), the fallback and hub-side backstop that exist when it doesn't, the
identity env the worker's declaration calls read, and the fallback a pointer at a graph artifact owes.
[../domain/graphs.md](../domain/graphs.md) §Node and [../domain/artifacts.md](../domain/artifacts.md) own the concepts —
the node-level `produces:` list and the asset artifact kind; this file owns the prompt-authoring obligation and hub
backstop a graph author is held to, the same relationship [./hub-nodes.md](./hub-nodes.md) has to `executor: hub`. Each
rule follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## The declaration instruction (`bzh:worker-node-attach-instruction`)

**Rule.** A worker node's `produces:` list names artifacts the *worker* is expected to submit
([../domain/graphs.md](../domain/graphs.md) §Node); for every name on that list, the node's prompt (and its judgement
prompt, when the two disagree on where the instruction lands) must instruct the worker to declare it. An `asset`-kind
name is declared by running `blizzard runner artifact create --name <exact-produces-name>`, reading the asset's content
from stdin. A `git_commit`-kind name (a build node's `produces: [{name: commit, kind: git_commit}]`) is declared by
running `blizzard runner artifact commit --repo <r> --branch <b> --commit <sha>` after pushing the branch, plus
`--env <id>` when the chunk holds more than one environment (with one, the runner infers it; with several, the same repo
has a worktree in each and it is refused rather than guessed). `--repo <r>` is the repo's **name in the environment's
repo manifest**, never an `owner/name` slug, a path, or a URL — the runner looks it up there to find both the worktree
and the origin to verify against, and a name the manifest does not list is **rejected at declare time** with a `400`
naming the repos it does, while the worker is still alive to re-run the verb. There is deliberately no `--forge`: the
origin comes from the manifest, so a worker cannot supply it and cannot supply the wrong one. A `git_commit` declaration
is satisfied by **kind** match, not name match — any `git_commit` artifact the worker declares covers the node's
`git_commit`-kind name, whatever the declaration is called. A node declaring several asset names declares each under its
own name — one `artifact create` call per name — rather than leaning on the judgement-assessment fallback
(`bzh:worker-node-attach-fallback` below) to cover more than one.

**Why.** The completion assembly has no file convention for an artifact — it can only submit what the worker explicitly
declares or, failing that, alias the whole node's judgement assessment to a name — so an un-instructed worker silently
produces the weaker fallback instead of the artifact the graph actually asked for, and a multi-name node loses per-name
provenance entirely if it relies on that alias.

**Scope.** Every asset-producing worker node carries this obligation; a `git_commit`-kind name carries it too, satisfied
by any declared `git_commit` artifact rather than one instructed by exact name (`bzh:worker-node-produces-backstop`
below). A hub node's step-level `produces` marker (`./hub-nodes.md` `bzh:hub-node-run-shape`, Scope) is recorded by the
executor itself, never by a worker.

**Detect.** A worker node's `produces:` list naming an asset with no `artifact create --name <that name>` string
anywhere in its prompt text; a multi-asset node's prompt instructing one declaration and expecting it to cover every
declared name; a build node's prompt with no `artifact commit` instruction for its pushed branch.

**Do.** `review.md` (the shipped `review` node's prompt): *"run `blizzard runner artifact create --name review-findings`
with the content on stdin"* — matching the node's own `produces: [review-findings]` in
`src/blizzard/hub/graphs/default.yaml` exactly. `build.md` (the shipped `build` node's prompt): push the branch, then
*"run `blizzard runner artifact commit --repo <repo> --branch <branch> --commit <sha>`"*, where `<repo>` is the repo's
name in the environment's manifest — matching the node's `produces: [{name: commit, kind: git_commit}]`. A node that
converges work before delivery (`pre-push`, `resolve`) instructs declaring **every** repo it touched **every** time,
including one whose rebase changed nothing: delivery fails on an empty commit set rather than reporting a landing, so a
silently omitted repo is a failed chunk rather than a quiet partial delivery. Every packaged graph's
`produces`-declaring node is held to the kind-appropriate current verb by a standing unit-tier guard
(`tests/test_packaged_prompts_attach.py`, cited in `blizzard:unit-test`,
[../verification/blizzard.md](../verification/blizzard.md)).

**Don't.** A prompt telling the worker to "write the findings as your judgement answer" or to a file — neither reaches
the declaration path, so the node falls back silently (`bzh:worker-node-attach-fallback`). A prompt still naming the
deprecated `blizzard runner attach` alias — the packaged-prompt guard rejects it outright.

## The judgement-assessment fallback (`bzh:worker-node-attach-fallback`)

**Rule.** An `asset`-kind `produces:` name with no explicit `artifact create` declaration is not left empty: the
completion assembly falls back to submitting the worker's judgement assessment as that name's asset content, undeclared.
This fallback is a legitimate landing artifact — nothing rejects its content — but it is a fallback, never the intended
path, and it cannot express more than one artifact: a node with several `produces:` names and one un-declared judgement
assessment aliases every missing name to the same text, losing the per-name distinction the node declared. A
`git_commit`-kind name has no such fallback — nothing stands in for a commit that was never pushed and declared.

**Why.** The engine cannot invent content a worker never produced, so it degrades to the one piece of prose every judged
node already has rather than failing the attempt outright — but that degradation is exactly the gap
`bzh:worker-node-produces-backstop` exists to catch.

**Detect.** A node with two or more asset `produces:` names where the prompt instructs at most one `artifact create`
call, or none.

**Do.** Author the prompt so every declared asset name gets its own `artifact create --name <name>` instruction
(`bzh:worker-node-attach-instruction`), leaving the fallback to cover only a genuinely un-instructed or non-compliant
run.

**Don't.** Design a multi-asset node assuming the fallback will "sort itself out" per name — it aliases one assessment
across every missing name, not one fallback per name.

## The `produces_mode` backstop (`bzh:worker-node-produces-backstop`)

**Rule.** The hub config's `produces_mode` (mirroring `route_token_mode`'s shape) gates what an undeclared `produces:`
name costs at completion time: under `enforce`, a submission with one or more `produces:` names lacking a covering
declaration is **rejected** outright; the shipped default is `warn`, which only logs the gap and lets the submission
proceed on the fallback where one exists. A `git_commit`-kind name is covered by **kind** match — any declared
`GIT_COMMIT` artifact satisfies it, whatever name that artifact itself carries — and never counts as missing once one is
declared.

**Why.** `enforce` exists as a rollout brake an operator opts into once every packaged and custom graph's prompts are
known to instruct the declaration correctly — landing it as the default would reject completions from graphs nobody has
audited yet.

**Detect.** A custom graph's worker node declaring `produces:` with a prompt that doesn't satisfy
`bzh:worker-node-attach-instruction`, running under a hub configured `produces_mode = "enforce"` — every completion from
that node fails until the prompt is fixed.

**Do.** Flip `produces_mode` to `enforce` only after auditing every graph the hub runs against
`bzh:worker-node-attach-instruction` — the packaged graphs already pass this audit via the standing guard cited above.

**Don't.** Ship a new custom worker node with a `produces:` name and an un-instructed prompt against a hub already
running `produces_mode = "enforce"` — expect every completion from that node to be rejected, not silently degraded.

## The `requires_checks` gate (`bzh:worker-node-checks-gate`)

**Rule.** A choice may declare `requires_checks: true`; selecting it while any of the node's `checks:` is red (the
runner runs them at worker exit — [../domain/graphs.md](../domain/graphs.md) §Judgement and choices, #114) is treated as
a **failure, not a judgement** — the engine consumes a retry and re-queues a fresh attempt rather than accepting the
edge, the red evidence injected into the re-attempt's judgement. Unlike `produces_mode`, this needs **no config flag**:
gating applies iff a choice declares `requires_checks`, so a graph that declares none is unaffected. It is enforced
twice off one shared predicate (`wire.completion.checks_gate_violated`) — the runner's own gate and the hub's completion
backstop, the same runner-gate-plus-hub-backstop shape `bzh:worker-node-produces-backstop` has — so a runner that skips
its gate is still fenced by the hub. A red check reported through a **non-gated** choice (`fail`) routes normally, its
context-rich fix path intact.

**Why.** Without the gate, enforcement of "checks are green" is social (prompt prose + the worker's honest self-report),
and prompt prose and the `checks:` YAML can silently drift; running the checks and gating the edge makes the graph
author's intent mechanical without taking routing authority from the worker — a red check still routes wherever the
worker's non-gated choices allow.

**Detect.** A custom single-application graph that wants "a green build cannot be routed to delivery" but leaves its
`pass` choice ungated — the worker can still select `pass` over a red check, exactly the drift the gate closes. (The
mint-time validator already rejects the ill-formed shapes — [../domain/graphs.md](../domain/graphs.md) §Judgement and
choices owns which — so they never reach here.)

**Do.** On a single-application graph (never a reusable one — `checks:` makes a graph application-specific,
`bzh:app-agnostic-graphs`), declare the node's `checks:` and set `requires_checks: true` on the choice that must not be
taken over red — typically build's `pass`, never its `fail`.

**Don't.** Reach for an engine-routed "check-failed" edge that overrides the worker's choice — rejected by design: it
would split routing authority between the graph author's choices and a mechanical router, and discard the worker's
context-rich `fail` reporting path.

## The worker's identity env (`bzh:worker-node-attach-env`)

**Rule.** Both declaration CLI calls the worker runs — `blizzard runner artifact create` and
`blizzard runner artifact commit` — read their identity from the spawn environment, not from arguments the node's prompt
has to thread:

| Var                    | Carries                                                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `BLIZZARD_LEASE_ID`    | The worker's current lease id — which chunk/node/attempt the declaration is recorded against.                        |
| `BLIZZARD_RUNNER_URL`  | The runner's local API the declaration posts to.                                                                     |
| `BLIZZARD_LEASE_TOKEN` | The lease's minted capability token, sent as `X-Blizzard-Lease-Token` — authorizes the call; sent only when present. |

**Why.** A prompt only ever names the declaration's own content (`--name <produces-name>`, or
`--repo`/`--branch`/`--commit`) — the identity triple is the runner's own concern, injected once at spawn, so a node's
author never has to carry or leak a lease id or token into authored prose.

**Scope.** `BLIZZARD_LEASE_ID` and `BLIZZARD_RUNNER_URL` are shared by every worker CLI the runner spawns with (`ask`,
`heartbeat`, `session-end`, every `artifact`/`chunk` verb). `BLIZZARD_LEASE_TOKEN` is narrower but not
declaration-specific either: every lease-scoped `artifact` verb (`create`, `commit`, `list`, `get`, `staged`) and
`chunk` verb (`history`) sends it as `X-Blizzard-Lease-Token` to authorize the call — `create`/`commit` are not the only
two that read it, only the two that durably record content rather than read it back. `--scope node|graph` is a separate
axis the `artifact` verbs do not all share. `list` serves either scope and reads both at once when the flag is omitted.
`get` reads both too, but only while `--node` is absent: a graph declaration has no producing node, so naming one
narrows the search to node scope on its own and graph scope is never consulted. `staged` is a read verb as well, but
node-scoped **by construction** — it reads back this node-step's own not-yet-published submissions, and a graph
declaration is never staged — so it refuses `--scope graph` exactly as the write verbs `create` and `commit` do: a
graph's declarations are baked at mint and read-only, so naming `graph` on any of the three reaches no call at all.

**Detect.** A node prompt instructing the worker to pass a lease id, runner URL, or token explicitly — there is nothing
in either declaration CLI's own signature (`src/blizzard/runner/cli.py`) for such an argument to bind to.

**Do.** *"run `blizzard runner artifact create --name <name>` with the content on stdin"* / *"run
`blizzard runner artifact commit --repo <repo> --branch <branch> --commit <sha>`"* — each CLI resolves lease id, runner
URL, and token itself.

**Don't.** *"run `blizzard runner artifact create --name <name> --lease <lease-id>`"* — no such flag exists; the worker
cannot supply an identity the CLI already has.

## A graph-artifact pointer carries its own fallback (`bzh:graph-artifact-pointer-fallback`)

**Rule.** A prompt that points a worker at a graph-scoped declaration —
`blizzard runner artifact get <name> --scope graph` — must also tell it what to do when that read does not answer, and
the instruction must carry the node-step to completion without the declaration's text. The pointer is therefore always
**additive**: whatever the worker needs in order to finish is stated in the prompt itself, and the declaration is the
fuller source it reads when it can.

**Why.** A pinned mint's declarations reach the runner's own store at spawn, so a lease already in flight when a runner
restarts onto a build that introduces a declaration holds a pin with nothing in it — the accepted window
`bzh:graph-scope-reads-local` ([../architecture/system-shape.md](../architecture/system-shape.md)) and the runner's
graph-artifact mirror entry in
[../architecture/crash-correctness/runner.md](../architecture/crash-correctness/runner.md) bound. A worker whose only
copy of a rule is behind that read has no way to finish its turn correctly.

**Scope.** Every prompt naming a graph-scope read, on a worker node or its judgement prompt alike. It says nothing about
node-scope reads: a node-scope miss means an upstream node produced nothing, which is a real condition of the chunk
rather than a window in the runner's own state.

**Detect.** A prompt whose graph-scope read has no adjacent clause covering a read that does not answer; a fallback
written only for an **empty** result. The two verbs that serve graph scope fail differently —
`artifact list --scope graph` answers empty, while `artifact get <name> --scope graph` exits **non-zero** with a `404`
named on stderr (`blizzard/src/blizzard/runner/api/artifacts.py`, raised by the worker CLI's shared call helper in
`blizzard/src/blizzard/runner/cli_worker.py`) — so a fallback conditioned on "comes back empty" leaves the `get` case,
the one a pointer at a named declaration actually takes, uncovered.

**Do.** *"The full docket this restates is retrievable directly:
`blizzard runner artifact get docket --scope graph --content`. If that read fails or comes back empty, proceed on the
restatement above."* — the restated slice stays in the prompt, so a worker that never runs the command, or runs it into
the window, still reads everything it needs.

**Don't.** *"The rules for folding findings are in the `docket` graph artifact — read it before you fold."* — the prompt
has delegated its own content to a read that can fail, and a worker inside the window has no rules at all.

**See also.** [`../architecture/system-shape.md`](../architecture/system-shape.md) `bzh:graph-scope-reads-local` — the
read path this defends and why it is local to the runner, and the accepted window that makes the defense necessary.

## See also

- [../domain/graphs.md](../domain/graphs.md) — the conceptual node model: the `executor` facet and the node-level
  `produces:` list this file's prompt obligation declares.
- [../domain/artifacts.md](../domain/artifacts.md) — the asset artifact kind `artifact create` submits, and the
  commit-pointer kind `artifact commit` declares.
- [./hub-nodes.md](./hub-nodes.md) — the parallel authoring contract for `executor: hub`, including the Scope note
  distinguishing its step-level `produces` marker from the node-level list this file governs.
- [../verification/blizzard.md](../verification/blizzard.md) — `blizzard:unit-test`, whose packaged-prompt declaration
  guard (`tests/test_packaged_prompts_attach.py`) proves `bzh:worker-node-attach-instruction` against every packaged
  graph, kind-branched by verb and rejecting the deprecated `blizzard runner attach` alias.
