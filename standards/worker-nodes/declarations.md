# Declaring a worker node's produced artifacts

A worker node's `produces:` list names artifacts the worker itself is expected to submit —
[../../domain/graphs/nodes.md](../../domain/graphs/nodes.md) owns the concept.

Parent: [../worker-nodes.md](../worker-nodes.md).

## The prompt instructs every declaration (`bzh:worker-node-attach-instruction`)

**Rule.** For every name on a node's `produces:` list, the node's prompt surface — its main prompt and its judgement
prompt taken together — must instruct the worker to declare it under the kind-appropriate verb. A node declaring several
asset names gets one `artifact create` call per name, each under its own exact name, rather than leaning on the fallback
to cover more than one.

**Why.** The completion assembly has no file convention for an artifact: it can submit only what the worker explicitly
declares, or alias the whole node's judgement assessment to a name — so an un-instructed worker silently yields the
weaker fallback, and a multi-name node relying on the alias loses per-name provenance entirely.

**Scope.** Binds worker nodes; a hub node's step-level `produces` marker is recorded by the executor itself, never by a
worker ([../hub-nodes.md](../hub-nodes.md), `bzh:hub-node-run-shape` Scope). `--scope node|graph` is a separate axis the
`artifact` verbs do not all share:

| Verb                                 | Scope behavior                                                                                                                                                                                                                                                                                       |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `artifact create`, `artifact commit` | Write verbs, node-scope only — they refuse `--scope graph`, because a graph's declarations are baked at mint and read-only                                                                                                                                                                           |
| `artifact staged`                    | A read verb, but node-scoped by construction — it reads back this node-step's own not-yet-published submissions, and refuses `--scope graph` for the same reason                                                                                                                                     |
| `artifact list`                      | Serves either scope, and reads both at once when the flag is omitted                                                                                                                                                                                                                                 |
| `artifact get`                       | Reads both scopes when neither flag is given; `--node` names a *producing* node, which a graph declaration has none of, so supplying it settles the scope to node on its own — and pairing it with `--scope graph` is a contradiction refused with a `400` telling the caller to drop one of the two |

**Detect.** A produces asset name with no `artifact create --name <that name>` string anywhere in the prompt text; a
multi-asset prompt expecting one declaration to cover every name. A standing unit-tier guard,
`tests/test_packaged_prompts_attach.py` (cited in `blizzard:unit-test`,
[../../verification/blizzard.md](../../verification/blizzard.md)), holds every packaged graph's produces-declaring
prompt to the kind-appropriate current verb, deprecated aliases included.

**Do.**

- An `asset`-kind name: `blizzard runner artifact create --name <exact-produces-name>`, the asset's content on stdin.
- A `git_commit`-kind name (a build node's `produces: [{name: commit, kind: git_commit}]`): push the branch, then
  `blizzard runner artifact commit --repo <r> --branch <b> --commit <sha>`. A `git_commit` name is satisfied by kind
  match, not name match: any `git_commit` artifact the worker declares covers it, whatever the declaration is called,
  both at completion assembly and under the `produces_mode` backstop.
- For `artifact commit`: `--repo` takes the repo's name in the environment's repo manifest — never an `owner/name` slug,
  a path, or a URL — and the runner looks it up there to find both the worktree and the origin to verify against; a name
  the manifest does not list is rejected at declare time with a `400` naming the repos it does list, while the worker is
  still alive to correct and re-run. There is deliberately no `--forge` flag — the origin comes from the manifest, so a
  worker cannot supply the wrong one. `--env <id>` is needed only when the chunk holds more than one environment: with
  one, the runner infers it; with several, the same repo has a worktree in each, so the verb is refused rather than
  guessed.
- A node that converges work before delivery (the packaged `pre-push` and `resolve` nodes) instructs declaring every
  repo it touched, every time — including a repo whose rebase changed nothing: delivery fails on an empty commit set
  rather than reporting a landing, so an omitted repo fails the chunk.

**Don't.**

- *"Write your findings as your judgement answer"*, or *"save your findings to `findings.md`"* — neither reaches the
  declaration path, so the name falls back silently to the judgement assessment.
- *"`blizzard runner attach --name findings`"* — the deprecated alias; the standing guard rejects any prompt naming it
  outright.

## The judgement-assessment fallback (`bzh:worker-node-attach-fallback`)

**Rule.** An `asset`-kind produces name with no explicit `artifact create` declaration is not left empty: the completion
assembly falls back to submitting the worker's judgement assessment as that name's asset content, undeclared — a
legitimate landing artifact, but never the intended path.

**Why.** The fallback cannot express more than one artifact: a node with several produces names and one un-declared
judgement assessment aliases every missing name to the same text, losing the per-name distinction the node declared.

**Exception.** A `git_commit`-kind name has no fallback: nothing stands in for a commit that was never pushed and
declared.

## The `produces_mode` backstop (`bzh:worker-node-produces-backstop`)

**Rule.** The hub config key `produces_mode` gates what an undeclared produces name costs at completion time: under
`enforce`, a submission with any produces name lacking a covering declaration is rejected outright; the shipped default
`warn` only logs the gap and lets the submission proceed on the fallback where one exists.

**Why.** `enforce` is a rollout brake an operator opts into — shipping it as the default would reject completions from
unaudited graphs.

**Do.** Flip `produces_mode` to `enforce` only after auditing every graph the hub runs against
`bzh:worker-node-attach-instruction`; the packaged graphs already pass that audit via the standing guard.

## The worker's identity environment (`bzh:worker-node-attach-env`)

**Rule.** Both declaration CLIs read the worker's identity from the spawn environment, not from arguments the prompt
threads:

- `BLIZZARD_LEASE_ID` — the lease the declaration is recorded against.
- `BLIZZARD_RUNNER_URL` — the runner API it posts to.
- `BLIZZARD_LEASE_TOKEN` — the lease's capability token, sent as `X-Blizzard-Lease-Token` when present.

A prompt names only the declaration's own content flags (`--name`, or `--repo`/`--branch`/`--commit`).

**Why.** The identity triple is injected once at spawn, so a node author never carries or leaks a lease id or token into
authored prose.

**Detect.** A prompt instructing the worker to pass identity — for example `--lease <lease-id>` — names a flag that does
not exist: neither declaration CLI's signature has any argument a lease id, runner URL, or token could bind to.
