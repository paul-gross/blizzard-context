# Worker command nodes

The authoring contract for a worker node — `executor: runner` (the default, [../domain/graphs.md](../domain/graphs.md) §Node) — that declares a `produces:` entry: the declaration instruction its prompt owes the worker (`blizzard runner artifact create` for an asset, `blizzard runner artifact commit` for a git commit), the fallback and hub-side backstop that exist when it doesn't, and the identity env the worker's declaration calls read.
[../domain/graphs.md](../domain/graphs.md) §Node and [../domain/artifacts.md](../domain/artifacts.md) own the concepts — the node-level `produces:` list and the asset artifact kind; this file owns the prompt-authoring obligation and hub backstop a graph author is held to, the same relationship [./hub-nodes.md](./hub-nodes.md) has to `executor: hub`.
Each rule follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## The declaration instruction (`bzh:worker-node-attach-instruction`)

**Rule.** A worker node's `produces:` list names artifacts the *worker* is expected to submit ([../domain/graphs.md](../domain/graphs.md) §Node); for every name on that list, the node's prompt (and its judgement prompt, when the two disagree on where the instruction lands) must instruct the worker to declare it. An `asset`-kind name is declared by running `blizzard runner artifact create --name <exact-produces-name>`, reading the asset's content from stdin. A `git_commit`-kind name (a build node's `produces: [{name: commit, kind: git_commit}]`) is declared by running `blizzard runner artifact commit --repo <r> --branch <b> --commit <sha>` after pushing the branch, plus `--env <id>` when the chunk holds more than one environment (with one, the runner infers it; with several, the same repo has a worktree in each and it is refused rather than guessed). `--repo <r>` is the repo's **name in the environment's repo manifest**, never an `owner/name` slug, a path, or a URL — the runner looks it up there to find both the worktree and the origin to verify against, and a name the manifest does not list is **rejected at declare time** with a `400` naming the repos it does, while the worker is still alive to re-run the verb. There is deliberately no `--forge`: the origin comes from the manifest, so a worker cannot supply it and cannot supply the wrong one. A `git_commit` declaration is satisfied by **kind** match, not name match — any `git_commit` artifact the worker declares covers the node's `git_commit`-kind name, whatever the declaration is called. A node declaring several asset names declares each under its own name — one `artifact create` call per name — rather than leaning on the judgement-assessment fallback (`bzh:worker-node-attach-fallback` below) to cover more than one.

**Why.** The completion assembly has no file convention for an artifact — it can only submit what the worker explicitly declares or, failing that, alias the whole node's judgement assessment to a name — so an un-instructed worker silently produces the weaker fallback instead of the artifact the graph actually asked for, and a multi-name node loses per-name provenance entirely if it relies on that alias.

**Scope.** Every asset-producing worker node carries this obligation; a `git_commit`-kind name carries it too, satisfied by any declared `git_commit` artifact rather than one instructed by exact name (`bzh:worker-node-produces-backstop` below). A hub node's step-level `produces` marker (`./hub-nodes.md` `bzh:hub-node-run-shape`, Scope) is recorded by the executor itself, never by a worker.

**Detect.** A worker node's `produces:` list naming an asset with no `artifact create --name <that name>` string anywhere in its prompt text; a multi-asset node's prompt instructing one declaration and expecting it to cover every declared name; a build node's prompt with no `artifact commit` instruction for its pushed branch.

**Do.** `review.md` (the shipped `review` node's prompt): *"run `blizzard runner artifact create --name review-findings` with the content on stdin"* — matching the node's own `produces: [review-findings]` in `src/blizzard/hub/graphs/default.yaml` exactly. `build.md` (the shipped `build` node's prompt): push the branch, then *"run `blizzard runner artifact commit --repo <repo> --branch <branch> --commit <sha>`"*, where `<repo>` is the repo's name in the environment's manifest — matching the node's `produces: [{name: commit, kind: git_commit}]`. A node that converges work before delivery (`pre-push`, `resolve`) instructs declaring **every** repo it touched **every** time, including one whose rebase changed nothing: delivery fails on an empty commit set rather than reporting a landing, so a silently omitted repo is a failed chunk rather than a quiet partial delivery. Every packaged graph's `produces`-declaring node is held to the kind-appropriate current verb by a standing unit-tier guard (`tests/test_packaged_prompts_attach.py`, cited in `blizzard:unit-test`, [../verification/blizzard.md](../verification/blizzard.md)).

**Don't.** A prompt telling the worker to "write the findings as your judgement answer" or to a file — neither reaches the declaration path, so the node falls back silently (`bzh:worker-node-attach-fallback`). A prompt still naming the deprecated `blizzard runner attach` alias — the packaged-prompt guard rejects it outright.

## The judgement-assessment fallback (`bzh:worker-node-attach-fallback`)

**Rule.** An `asset`-kind `produces:` name with no explicit `artifact create` declaration is not left empty: the completion assembly falls back to submitting the worker's judgement assessment as that name's asset content, undeclared. This fallback is a legitimate landing artifact — nothing rejects its content — but it is a fallback, never the intended path, and it cannot express more than one artifact: a node with several `produces:` names and one un-declared judgement assessment aliases every missing name to the same text, losing the per-name distinction the node declared. A `git_commit`-kind name has no such fallback — nothing stands in for a commit that was never pushed and declared.

**Why.** The engine cannot invent content a worker never produced, so it degrades to the one piece of prose every judged node already has rather than failing the attempt outright — but that degradation is exactly the gap `bzh:worker-node-produces-backstop` exists to catch.

**Detect.** A node with two or more asset `produces:` names where the prompt instructs at most one `artifact create` call, or none.

**Do.** Author the prompt so every declared asset name gets its own `artifact create --name <name>` instruction (`bzh:worker-node-attach-instruction`), leaving the fallback to cover only a genuinely un-instructed or non-compliant run.

**Don't.** Design a multi-asset node assuming the fallback will "sort itself out" per name — it aliases one assessment across every missing name, not one fallback per name.

## The `produces_mode` backstop (`bzh:worker-node-produces-backstop`)

**Rule.** The hub config's `produces_mode` (mirroring `route_token_mode`'s shape) gates what an undeclared `produces:` name costs at completion time: under `enforce`, a submission with one or more `produces:` names lacking a covering declaration is **rejected** outright; the shipped default is `warn`, which only logs the gap and lets the submission proceed on the fallback where one exists. A `git_commit`-kind name is covered by **kind** match — any declared `GIT_COMMIT` artifact satisfies it, whatever name that artifact itself carries — and never counts as missing once one is declared.

**Why.** `enforce` exists as a rollout brake an operator opts into once every packaged and custom graph's prompts are known to instruct the declaration correctly — landing it as the default would reject completions from graphs nobody has audited yet.

**Detect.** A custom graph's worker node declaring `produces:` with a prompt that doesn't satisfy `bzh:worker-node-attach-instruction`, running under a hub configured `produces_mode = "enforce"` — every completion from that node fails until the prompt is fixed.

**Do.** Flip `produces_mode` to `enforce` only after auditing every graph the hub runs against `bzh:worker-node-attach-instruction` — the packaged graphs already pass this audit via the standing guard cited above.

**Don't.** Ship a new custom worker node with a `produces:` name and an un-instructed prompt against a hub already running `produces_mode = "enforce"` — expect every completion from that node to be rejected, not silently degraded.

## The worker's identity env (`bzh:worker-node-attach-env`)

**Rule.** Both declaration CLI calls the worker runs — `blizzard runner artifact create` and `blizzard runner artifact commit` — read their identity from the spawn environment, not from arguments the node's prompt has to thread:

| Var | Carries |
|-----|---------|
| `BLIZZARD_LEASE_ID` | The worker's current lease id — which chunk/node/attempt the declaration is recorded against. |
| `BLIZZARD_RUNNER_URL` | The runner's local API the declaration posts to. |
| `BLIZZARD_LEASE_TOKEN` | The lease's minted capability token, sent as `X-Blizzard-Lease-Token` — authorizes the call; sent only when present. |

**Why.** A prompt only ever names the declaration's own content (`--name <produces-name>`, or `--repo`/`--branch`/`--commit`) — the identity triple is the runner's own concern, injected once at spawn, so a node's author never has to carry or leak a lease id or token into authored prose.

**Scope.** These three vars are shared by every worker CLI the runner spawns with (`ask`, `heartbeat`, `session-end`), not declaration-specific; `artifact create` and `artifact commit` are the two that also read `BLIZZARD_LEASE_TOKEN`, since both durably record content rather than a soft-fail signal.

**Detect.** A node prompt instructing the worker to pass a lease id, runner URL, or token explicitly — there is nothing in either declaration CLI's own signature (`src/blizzard/runner/cli.py`) for such an argument to bind to.

**Do.** *"run `blizzard runner artifact create --name <name>` with the content on stdin"* / *"run `blizzard runner artifact commit --repo <repo> --branch <branch> --commit <sha>`"* — each CLI resolves lease id, runner URL, and token itself.

**Don't.** *"run `blizzard runner artifact create --name <name> --lease <lease-id>`"* — no such flag exists; the worker cannot supply an identity the CLI already has.

## See also

- [../domain/graphs.md](../domain/graphs.md) — the conceptual node model: the `executor` facet and the node-level `produces:` list this file's prompt obligation declares.
- [../domain/artifacts.md](../domain/artifacts.md) — the asset artifact kind `artifact create` submits, and the commit-pointer kind `artifact commit` declares.
- [./hub-nodes.md](./hub-nodes.md) — the parallel authoring contract for `executor: hub`, including the Scope note distinguishing its step-level `produces` marker from the node-level list this file governs.
- [../verification/blizzard.md](../verification/blizzard.md) — `blizzard:unit-test`, whose packaged-prompt declaration guard (`tests/test_packaged_prompts_attach.py`) proves `bzh:worker-node-attach-instruction` against every packaged graph, kind-branched by verb and rejecting the deprecated `blizzard runner attach` alias.
