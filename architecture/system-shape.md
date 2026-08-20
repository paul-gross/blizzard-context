# System shape

The macro-shape invariants of the running system — the split between the deterministic code that coordinates and the
intelligent work it drives, the seam every external system sits behind, and the store-schema rule that makes crash
recovery correct. These are the foundations the daemon loops (`bzh:steppable-loop` … in
[./crash-correctness.md](./crash-correctness.md)) are built on. Each rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Deterministic shell, intelligent core (`bzh:deterministic-shell`)

**Rule.** Coordination — the runner tick, the hub coordinator, the workflow transitions, the store reads and writes — is
**deterministic** code with no model calls; the **intelligent** work (the harness doing a node-step) is confined to the
leaf where a worker runs, behind the harness seam. Orchestration decides *what* to run and *where*; it never itself
reasons with an LLM.

**Why.** A deterministic shell is replayable, unit-testable without tokens, and crash-recoverable — the whole
crash-correctness harness depends on the loop being a pure function of (store, clock, seams). Pushing model judgement
into the coordinator would make the loop non-deterministic and untestable, and would spend tokens on control flow.

**Detect.** A model call, a prompt, or an LLM client inside a runner loop step, the hub coordinator, a transition, or a
store method; orchestration logic that branches on freshly-generated model output rather than on a parsed verdict fact.

**Do.** The worker (harness seam) produces a verdict; the coordinator reads the parsed verdict fact from the store and
picks the workflow edge deterministically.

**Don't.** The coordinator prompts a model to decide the next node — control flow is now non-deterministic and cannot be
replayed under the crash sweep.

## Every external system behind a seam (`bzh:pluggable-seams`)

**Rule.** Every external system is reached only through an interface — a seam — with the reference stack as its first
binding: the work source (at the hub), the workspace provider, the coding harness, delivery (the forge), and the human
channel are all Protocols, and their concrete bindings (GitHub, winter, Claude Code) are swappable adapters selected by
configuration. A seam is the external-system application of dependency inversion (`bzh:dependency-inversion`).

**Why.** A seam is what lets tests bind the mock fleet in place of the real stack — the entire service and e2e strategy
runs seams-mocked, spending no tokens and touching no network — and lets a runner swap winter worktrees for plain
worktrees without touching the loop. Code that calls a vendor SDK directly cannot be tested without that vendor and
cannot be re-bound.

**Detect.** A vendor SDK, the GitHub API, or a `claude`/harness binary invoked directly from a loop step, the domain, or
a store — rather than through an injected seam Protocol; a test that cannot run without a real external system because
no seam exists to bind a mock to.

**Do.** The runner depends on `IWorkspaceProvider`, `IHarness`, and the forge seam; production binds winter / Claude
Code / GitHub, tests bind the `blizzard-mock` fleet.

**Don't.** A FILL step that shells out to `claude -p` directly — the loop can no longer be exercised against the mock
harness and every service test now needs real tokens.

**Recorded positions** — a case that looks like it might need a configured, external binding but does not, stated so a
reviewer does not have to re-derive the same judgement:

- **The built-in `hub` work source (issue #357).** `HubWorkSource` still implements `IWorkSource` — the seam this rule
  requires — but its binding is in-process and always seated, never a `[[work_source]]` entry with a credential: its own
  store *is* the item's system of record, not a cache of an external one, so there is no external system for a config
  entry to point at. The concrete wiring stays at the composition root (`hub/app.py::build_hosted_app`) exactly as
  `bzh:dependency-injection` requires for every other binding — only the walk that seats it differs (outside the
  configured-entry loop, in `WorkSourceEntry.registry`), not the seam itself. Its **editor** capability (`IWorkEditor`,
  blizzard#358) is seated the same way and carries the same judgement one step further, on two counts.

  First, *why it is structural rather than an opt-in*: `annotate`/`close` are each a configured source's own opt-in key,
  but no `[[work_source]]` field could ever opt a source into editing. The reason is not that editing reaches the hub's
  own store — `annotate`/`close` are configured opt-ins that also write to an external store, so store locality alone
  doesn't distinguish editing from them. What actually closes the seam is the *return type*: all five `IWorkEditor`
  methods return `WorkItemRecord`, the hub repository's own record type (a `wi_<ulid>` id, a hub-user-or-fleet author, a
  closure) — unlike `IWorkSource.fetch`, which returns a seam-local `WorkItem` dataclass any binding can answer.
  `editor(name) is None` is therefore *structurally never edited* for every source but `hub`, not merely *not opted in*
  — a capability seated with no flag at all is still one seam, one composition root, no different in kind from the
  source itself.

  Second, *why the same gate also covers `list`/`get`* (the read half) rather than only the three write verbs:
  `IWorkSource` itself declares no enumeration method at all, so today no non-`hub` binding — including the configured
  GitHub adapter, whose `fetch` answers one pointer at a time — has any way to serve `list()`/`get()` regardless of the
  editor gate. Gating reads alongside writes changes nothing observable while that holds; the day a binding gains a real
  enumeration capability, the read half is what splits out of `IWorkEditor`, not before.

## Store facts, derive status (`bzh:facts-not-status`)

**Rule.** Both daemons' stores hold only durable **facts** — a thing that definitely happened at a definite time (a
lease created, a heartbeat received, a transition recorded, a verdict parsed). A chunk's **status** is always *derived*
by query from those facts, never written as a column.

**Why.** Written status lies after a crash: a process that wrote `running` and then died reports `running` forever,
while a status derived from "last heartbeat 20 minutes ago and the pid is dead" tells the truth however the process
ended — this single rule is what makes crash recovery correct rather than aspirational, and is what the invariant
checker (`bzh:invariant-checker`) asserts against.

**Detect.** A `status` / `state` column written by application code; a derived condition (running, waiting, stalled,
done) persisted rather than computed from underlying fact rows at read time.

**Do.** Persist `Lease`, `Heartbeat`, `Transition`, `Verdict` rows; compute chunk status by querying them (last
heartbeat age, pid liveness, latest transition).

**Don't.** Write a `chunk.status = "running"` column and update it as the chunk moves — the column outlives the truth
the instant the process dies.

**Recorded positions** — a case that looks like it might carry a derived condition but does not, stated so a reviewer
does not have to re-derive the same judgement:

- **Derived transcript events (blizzard#254).** `transcript_events` conforms to this rule rather than being exempt from
  it: each row is an immutable *observation* — a definite occurrence (a file read, a skill invocation, an agent spawn)
  at a definite time — never a *condition* that can go stale, the distinction the rule bars. Three properties are
  load-bearing: (a) nothing derives a status from a row and no admission, claim, or spawn is gated on one — dropping the
  whole table costs only query latency, never correctness; (b) it is fully re-derivable from `transcript_segments`, so
  its authority is always the segments, never itself; (c) its source's mutability is bounded and **observed**, not
  assumed — the paired `transcript_event_derivations` marker records a content fingerprint of what a derivation saw, so
  a segment whose stored content later changes underneath it (a rejected record accepted, a late record landing) is
  detected and re-derived by the standing sweep rather than silently going stale, the same crash-safety shape
  `bzh:crash-point-registry`'s own recorded exemptions ([./crash-correctness.md](./crash-correctness.md)) use for a
  converging reconciler with no state between passes.

- **Hub-owned work item closure (issue #357).** `work_items.closed_at`/`closure` are a plain nullable column pair on the
  item row, both unset while open and set together once on close — not an append-only fact table, and not exempt from
  this rule either: `work_items` is a **mutable entity** (title, body, and `edited_at` change in place, the same shape
  `chunks.graph_id` carries), not a fact log, so its closure is itself recorded state rather than a derivable condition
  — no query over other rows can produce it, the same terminal-instant shape `hub_exec_slot.released_at` already uses
  (`schema.py`, null while live).

## An open fact declares what closes it on a terminal chunk (`bzh:open-facts-declare-closure`)

**Rule.** Every runner-local **open** read — a fact that stands until something supersedes or closes it — declares what
closes it when the **hub** terminally ends the chunk (`stopped` or `done`). A read whose closers are all runner-local
events is incomplete, not merely narrow.

**Why.** The runner derives openness from its own facts, but the hub owns whether a chunk is still work. A
terminally-ended chunk produces no further runner-local event — no lease is minted, no worker exits, no binding is taken
— so a closer expressed only in runner-local terms can never fire, and the fact stands forever. This has shipped twice:
issue #202 (an ask-parked lease's park fact and a held binding never retired on a non-happy-path ending) and
blizzard#292 (an escalation never closed when its chunk was stopped, leaving a permanent `needs_human` alert on a real
fleet). Both were found by an operator, not by a test.

**Detect.** An `open_*` read, or an `Unsuperseded`/`Unclosed` predicate, whose superseding facts are all runner-local (a
lease mint, a spawn, a closure, a release), with no arm for the hub reporting the chunk terminal; a PULL step that
reconciles only `list_active_leases()` while the fact in question outlives its lease.

**Do.** State at each such read what retires it on a hub-terminal chunk. When no runner-local event can, mirror the
hub's answer into a local fact so the read itself stays hub-free — `escalation_closures`, written by
`Pull._reconcile_escalations`, is the reference shape.

**Don't.** Leave a later lease mint as the sole closer for a fact that outlives its lease — a terminally-ended chunk is
never claimed again, so that closer is unreachable by construction.

## Worker environments are allowlisted, never inherited (`bzh:worker-env-allowlist`)

**Rule.** A worker/judge/resume child environment is built from an explicit allowlist — a fixed base set plus deliberate
additions (locale variables) plus the operator's declared passthrough — never from a full copy of the daemon's own
`os.environ`.

**Why.** The runner process holds daemon credentials (a hub bearer token, forge tokens); a child built by copying the
parent environment carries any such secret into every worker/judge/resume invocation by default, where a still-untrusted
harness prompt or transcript can leak it. Building the child from an allowlist makes a daemon credential's absence
structural rather than a property some filter has to remember to apply.

**Scope.** Governs the spawn/judge/resume environment construction on the runner side of the harness seam
(`bzh:pluggable-seams`); it does not bound what a harness binary itself may read from its own process environment once
launched.

**Detect.** `os.environ` (or `env=None`/omitted `env=`, which inherits the parent) passed directly into a `subprocess`
call that launches a worker, judge, or resume harness process, rather than through the one allowlist-building function.

**Do.** `_allowlisted_env(passthrough)` in `blizzard/runner/harness/internal/claude_code_adapter.py` builds every child
env from the base allowlist + `LC_*` + `env_passthrough`; identity variables (`BLIZZARD_LEASE_ID`, …) are then added
explicitly per spawn.

**Don't.** `subprocess.Popen(cmd, env=os.environ)` (or a bare `env=dict(os.environ)`) handed to a worker launch — the
child now inherits `BZ_HUB_TOKEN` and every other daemon secret by accident.

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
deprecated alias for `artifact create` ([../standards/worker-nodes.md](../standards/worker-nodes.md)
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

**See also.** [`../standards/worker-nodes.md`](../standards/worker-nodes.md) `bzh:graph-artifact-pointer-fallback` — the
fallback a prompt pointing at a declaration owes, because a lease pinned before the runner recorded the mint's
declarations reads an empty pin.

## Git mutation lives in the worker seam (`bzh:git-write-in-worker-seam`)

**Rule.** Only the worker mutates git — it commits its work and pushes its branch. The runner's own git surface is
**read-only**: it confirms what the worker declared (`git ls-remote` against the origin the environment's repo manifest
names), it never commits and never pushes. The worker declares what it pushed — `(env, repo, branch, commit)`, through
the runner's local declaration channel — and the runner's read-only verify is what turns that declaration into a
submitted artifact.

**Why.** The runner is the deterministic shell (`bzh:deterministic-shell`) and holds the only credentialed copy of the
leased environment, but it cannot know what a worker's turn actually produced without either trusting the worker's
say-so blindly or **inferring** it from git residue — and residue is lossy: a detached worktree's
`git rev-parse --abbrev-ref HEAD` returns the literal string `HEAD`, which a runner that both infers *and* pushes turns
into a wedge the instant it tries to push a branch named `HEAD`. Splitting the two roles — the worker states a fact
about what it did, the runner independently confirms that fact against the forge it can already see — gets both
properties at once: the runner never fabricates a pointer from ambiguous residue, and it never merely trusts an
unverified claim either.

**Scope.** Governs the runner's `IWorktreeGit` seam (`runner/loop/worktree.py`) and its ADVANCE collection step. The
runner still holds the only credentialed copy of the leased environment; it is only the git mutation *within* that
environment that moves to the worker.

**Detect.** A runner-side `git push`, `git commit`, or any git call that resolves *which* branch/commit to act on from
repository state (`git rev-parse --abbrev-ref HEAD`, "HEAD is ahead of base") rather than from a declaration the worker
made through the local API.

**Do.** The worker pushes its branch, then declares it —
`blizzard runner artifact commit --repo <r> --branch <b> --commit <sha>` — and the runner's
`IWorktreeGit.verify(origin_url, branch, commit)` confirms it read-only (`git ls-remote`, no working directory
consulted) before submitting the `GIT_COMMIT` artifact. The `origin_url` comes from the environment's repo manifest,
which the workspace provider owns (`IWorkspaceProvider.repos`), never from the worker and never from whatever directory
the caller happens to stand in.

**Don't (the second inference).** Deriving a repo's origin from the *caller's* cwd rather than from the manifest. The
verb once defaulted `--forge` to `git remote get-url origin` in the worker's process cwd; workers are spawned at the
workspace root, so git walked up past the environment and returned the enclosing workspace repo for every repo alike — a
plausible-looking wrong value rather than an error, which failed the comparison and dropped every declaration. Reading
`origin` from a directory nobody chose is the same lossy-residue mistake as reading `HEAD` from one, and the fix is the
same shape: look the fact up where it is owned instead of inferring it from ambient state.

**Don't.** A runner step that walks the leased environment's repo worktrees looking for one whose `HEAD` is ahead of the
base branch and pushes whatever it finds — inference from residue this shape avoids.

## See also

- [./crash-correctness.md](./crash-correctness.md) — the daemon requirements built on `bzh:facts-not-status` and
  `bzh:deterministic-shell`.
- [../standards/persistence.md](../standards/persistence.md) — `bzh:sql-portable`, the portable-SQL rule the facts-only
  stores are held to.
