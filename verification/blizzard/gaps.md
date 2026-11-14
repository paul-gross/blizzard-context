# Surfaces no tier reaches (`bzh:matrix-gaps`)

The matrix leaves the surfaces below uncovered on purpose. Each entry names the evidence standing in for a tier and why
a tier cannot reach it; each is a documented gap, not an invitation to invent a tier around it. A surface's
unreachability by any tier is re-tested each time a gap is entered here and never inherited by analogy from a sibling
gap, because tooling that lands later can automate part of what was manual and leave a narrower residue than the
original claim assumed.

A change that closes a gap deletes its entry in the same change, and one that narrows a gap rewrites its entry to the
residue that remains. A change that adds a mechanism an open gap already covers adds it to that entry rather than
entering it anew. An entry left behind for a closed gap tells the next reader to keep owing evidence nothing needs any
longer.

## `docs/` claims about daemon behavior (`bzh:operator-doc-claims-unverified`)

`docs/` states reachability, precondition, and failure claims about daemon behavior, and nothing mechanical can judge
whether one is true: `blizzard:restatement-sweep` checks that a fact has one home rather than that it is correct, and
`blizzard-context:registry-drift` proves agreement, never adequacy. Hand-walking the operator docs repeatedly turns up
inverted or invented claims.

Standing in for a tier: a change to daemon control flow owes a walk of the `docs/` claims it touches, tracing each
precondition to its guard, each reachability claim to its dispatch site, and each failure claim to its raising path — a
claim a fix commit writes owes the same walk as one it edits. Do not answer this with a doc-linting tier that would
score prose without reading the code.

## Per-block prose caps

`bzh:prose-budget`'s caps are checked by `blizzard/tests/guards/test_layering.py` on `blizzard/exemplars/python` only.
No command checks `blizzard/src`, `blizzard/tests`, `blizzard-mock/src`, or `blizzard-mock/tests`, where a large backlog
of over-cap blocks stands.

Standing in for a tier: a change shows that no block it added or edited is over cap, counting with
`blizzard/scripts/prose_caps.py`. Gating the whole tree is not the fix, because it fails on prose the change never
touched and stops being read.

## Session stickiness, effective model, and context accounting

The session-model contract — owned by [declared sessions](../../domain/graphs/declared-sessions.md#model-preference) —
is proven at the flag, never at the model a harness ran under. Where the runner supplies no model on resume — OpenCode,
whose resume passes only the session — the contract rests on that harness restoring a resumed session's own model, and
nothing asserts that restoration. The live OpenCode compatibility diagnostic checks that the requested provider/model
and variant survive fresh and resumed exports, but it deliberately supplies them on every invocation and therefore does
not assert effective model stickiness when they are omitted, as the runner's resumes omit them. No tier asserts the
effective context accounting a harness ran under, because the mock façade sees argv and nothing else.
`blizzard:service-test`'s
`tests/service/fleet/session-modes.spec.ts::test_a_named_pool_threads_one_session_across_nodes_and_reasserts_its_model`
asserts the flag on the Claude Code façade — the mint and every resume carry the same resolved model — and stops there.

Standing in for a tier: what backs the surrounding export behavior is a one-time empirical observation of Claude Code
CLI 2.1.220 and the retained live compatibility evidence for the runner's admitted range (currently `>=1.18.25,<2.0`).
Neither observation proves OpenCode session stickiness when model flags are omitted; each harness also has a
configuration that can defeat stickiness, which `docs/deployment/worker-spawn.md` states as deployment requirements. Do
not add a real-token tier to close this gap.

## The declared compaction window

The declared compaction window is applied on each invocation. Mock-visible unit and component tests prove configuration
composition and stamp propagation, but not that a harness compacts at the resulting threshold. OpenCode's compatibility
diagnostic also proves configuration acceptance rather than the threshold itself.

Standing in for a tier: `blizzard:manual-autocompact-window` provides a live procedure, the same shape as
[`blizzard:manual-external-usage-probe`](./manual.md#blizzardmanual-external-usage-probe) — an external harness's live
compaction behavior sits outside a hermetic, network-free CI tier's reach. The procedure is evidence only when run and
its threshold contrast is observed; a configuration echo or a documented procedure alone does not close the gap.

## OpenCode's compaction tail marker

The OpenCode compatibility diagnostic treats a compaction part's tail marker as a logical prune when history rows are
retained rather than removed. That field is read as `tail_start_id`, a snake_case key in a payload family that is
otherwise strictly camelCase (`sessionID`, `messageID`, `callID`, `parentID`), and no captured fixture under any of the
runner's committed corpus directories — the runner's admitted range (currently `>=1.18.25,<2.0`) is backed by only the
one, `blizzard/src/blizzard/runner/harness/contracts/opencode/1.18.25/` — carries it: that corpus version's live runs
never compacted. A wrong spelling parses as absent, so the fallback silently stops firing rather than failing.

Standing in for a tier: the physical-removal path, which every retained fixture does exercise, is the primary evidence
for `transcript_cursor`; the tail-marker fallback is unverified until a live run compacts and the shape is captured.
Re-run `blizzard:manual-opencode-compatibility` long enough to force a compaction before treating the fallback as
proven, and do not add a tier that would assert a hand-authored spelling against itself.

## OpenCode transcript reads never distinguish `not_found`

`IHarnessTranscriptSource.turns_since`'s `TranscriptReadReason` names `not_found` and `unreadable` as distinct outcomes,
but `opencode export <session-id>` gives no confirmed signal separating "no such session" from any other export failure
— the compatibility probe's own `_export_session` (`opencode/compatibility/probe.py`) does not distinguish them either,
always folding a non-zero exit into one generic error string. `OpenCodeTranscriptSource` therefore reports every export
failure as `unreadable`, never `not_found`, until a live run's exit code or stderr shape is captured and confirmed.

Standing in for a tier: `blizzard:unit-test` covers the chosen `unreadable` default against every failure shape this
parser can name; a live `opencode export` against a genuinely absent session id would be the evidence for a narrower
`not_found` path, and does not exist yet. Do not add a stderr-string match invented rather than captured from a run.

## A bare node's chunk-declared default at spawn

`tests/service/runner/mixed-harness-dispatch.spec.ts` records a proof the mock hub's fidelity leaves unreachable: a bare
node honoring the chunk's own declared default all the way through spawn. `blizzard-mock-hub`'s own `envelope()` route,
unlike the real hub's `EffectiveSession.of`, never bakes the chunk's `default_harnesses` back onto the node before
handing the envelope to the runner, so while a bare node's matched peek does honor the chunk's own declared default
(proven), the SPAWN that follows falls through to `Spawner.spawn`'s own no-`session_harnesses` fallback — this runner's
own configured default, never the chunk's declared one. Baking `default_harnesses` onto the envelope's node the way
`EffectiveSession.of` does would close it.

Standing in for a tier: none. Do not invent the behavior at the unit or component tier: it is a hub-side routing
decision this suite means to prove against the real production `HttpHubClient`/`Spawner.spawn` path, never a hand-built
substitute.

## The worker deny list

`WorkerSettings.document`'s `permissions.deny` list travels to the harness as a JSON settings file on every worker
invocation path. The mock-visible tiers — `blizzard:unit-test`'s exact-list pin and `blizzard:component-test`'s
prefix-parity check — prove only that the file is built and threaded, never that `claude -p` itself honors a
`permissions.deny` entry.

Standing in for a tier: `blizzard:manual-worker-deny-list` closes this as a live procedure, the same shape as
[`blizzard:manual-autocompact-window`](./manual.md#blizzardmanual-autocompact-window) — an external harness's live
permission enforcement sits outside a hermetic, network-free CI tier's reach.

## Headless permission handling

The runner composes OpenCode's `ask` rules to `deny` in `normal` autonomy, and relies on `claude -p` refusing an `ask`
rule as a tool error. The mock-visible tiers prove only the composed document and argv against a fake resolver; whether
a real CLI returns a tool error rather than rejecting the turn, or resolves the request under `--auto`, is outside a
hermetic CI tier's reach.

Standing in for a tier: `blizzard:manual-headless-permission-refusal` closes this as a live procedure.

## The Claude Code bundle

The runner composes an operator's `claude-code/` bundle with its own wiring and passes the result to every unattended
invocation. The mock-visible tiers prove only that composition produces the expected document and that the argv carries
it; `blizzard-mock`'s `claude_code` facade parses `--mcp-config`, `--agents`, and `--plugin-dir` and executes the
composed hooks, but loads no MCP server, plugin, agent, or ambient settings file. Whether the real CLI honors the
composed file beside user, project, and managed settings is outside a hermetic CI tier's reach.

Standing in for a tier: `blizzard:manual-claude-code-bundle` closes this as a live procedure.

## Claude Code telemetry precedence

When an `OTEL_*` destination is named in both Claude Code's process env and a settings document's `env`, which wins is
undocumented behavior of the CLI, and the telemetry it exports carries scope names and trace parenting the runner admits
on. `blizzard-mock`'s `claude_code` facade executes `--settings` hooks but never applies settings `env`, so a facade
test could pin only the facade, and no hermetic tier runs the real exporter.

Standing in for a tier: `blizzard:manual-claude-code-harness-telemetry` closes this as a live procedure. Do not add a
facade test that claims to pin the precedence.

Observed on `claude` 2.1.288 to 2.1.289:

- `--settings` env and user-settings env each beat a same-named process env for all three signals (outcome A for both
  sources); a process signal-specific endpoint beats a settings generic one.
- Scopes: `com.anthropic.claude_code` (metrics), `com.anthropic.claude_code.events` (logs),
  `com.anthropic.claude_code.tracing` (traces). The resource's own `service.name` is `claude-code`.
- Spans carry the `TRACEPARENT` trace id and the root span parents on the env span; a `Bash` subprocess's `TRACEPARENT`
  names that tool's `claude_code.tool.execution` span. `claude_code.interaction` parents on the step root.
- With `ENABLE_BETA_TRACING_DETAILED` on, `BETA_TRACING_ENDPOINT` takes traces and logs from the documented exporters,
  as OTLP/JSON, while metrics stay on the documented exporter.
- Without `CLAUDE_CODE_ENABLE_TELEMETRY` and `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA` a named destination receives nothing;
  with only the first, metrics and logs arrive and traces do not.
- The node's judgement turn, a `--resume` of the same session, exported metrics and logs but no spans.

## Claude Code transcript normalization

`blizzard-mock`'s `ClaudeTranscriptWriter` (`blizzard-mock/src/blizzard_mock/harness/facades/_transcript.py`)
deliberately mints none of the shapes involved, so no mock-driven `blizzard:service-test` exercises the normalizer,
which could drift from a future Claude Code CLI with every tier green.
`tests/ui/transcript-tab.spec.ts::test_chunk_transcripts_tab_browser` does not close it either: it seeds hand-authored
`TurnSegmentView` JSON straight to `POST /api/fleet/transcripts`, so no normalizer output ever reaches it. OpenCode's
own `opencode.transcript.normalizer` is a separate code path this gap does not reach either way — it is exercised by
`blizzard-mock`'s `OpenCodeTranscriptWriter` through a real mock-driven `blizzard:service-test`, which this one is not.

Standing in for a tier: sidechain and thinking-turn normalization is proven only against hand-authored fixtures, pinned
at `blizzard:unit-test` and by the component-tier projection golden tests, both fed by the same record fixtures — which
transcript shapes are involved, and why, is owned by `blizzard-mock`'s `src/blizzard_mock/harness/README.md`
§"Conversation transcripts". Do not add a real-corpus CI tier reading a developer's `~/.claude/projects`, which is
neither hermetic nor reproducible.

## Claude Code's transcript source position codec, batch budget, and EOF clamps

The position codec, the shared batch budget, and the past-EOF clamps inside `ClaudeCodeTranscriptSource.turns_since` are
pinned at no tier at all. Every component-tier test of the transcript lane binds a scriptable `FakeTranscriptSource`
(`blizzard/tests/support/runner_fakes.py`), so `tests/component/runner/transcripts/test_transcript_pump.py` and
`tests/component/runner/transcripts/test_transcript_backfill.py` reach the pump's and the backfill's own decisions and
never those three pieces. `OpenCodeTranscriptSource` is a distinct implementer this gap does not name: its own
export-identity cursor, bound token, and `not_found`/`unreadable` split are pinned at `blizzard:unit-test` — "OpenCode
transcript reads never distinguish `not_found`" above covers what that tier does not.

Standing in for a tier: `blizzard runner transcript reship` and `blizzard runner transcript backfill` drive
`TranscriptPump.drain_segment` with `deadline=None` over a complete historical file from offset 0 until the source
catches up, exercising the three unpinned pieces harder than a tick ever does. The backfill verb is the first path that
requires `ship = true`, so an operator running it against a real `~/.claude/projects` produces evidence of the
forward-read lane that no tier records — which dogfooding does not supply by default, since the transcript lane ships
disabled (`[transcripts] ship = false`).

## The query-plan assertions never run under postgres

`tests/component/hub/store/internal/test_finding_store.py`'s `test_list_for_query_plans_as_an_index_search` and
`test_count_by_class_query_plans_as_an_index_search` assert `EXPLAIN QUERY PLAN` on sqlite — the backend every component
test runs against — that `list_for`'s routine+scope read and `count_by_class`'s routine+class read use
`ix_findings_tenant_project_routine_scope`/`ix_findings_tenant_project_routine_class` rather than a table scan.
`tests/component/hub/store/internal/test_chunk_fact_table_indexes.py` asserts the same shape over the twenty
`chunk_id`-filtered fact tables' indexes and the hub store's hot-path indexes: the three `(chunk_id, epoch)` composite
searches, the artifacts/graph-choices/transcript-segments/chunk-work-refs/close-intents hot-path reads, and each of
`activity_facts_since`'s eighteen per-source ordered reads.
`tests/component/hub/store/internal/test_chunk_usage_store.py`'s `EXPLAIN QUERY PLAN` case over `usage_total_stmt`
builder asserts `ix_usage_facts_tenant_recorded_at_id` the same way. `tests/component/test_store_read_index_gate.py`'s
scan gate classifies its hub and runner census recipes, with non-SQL methods exempted, and
`tests/component/runner/store/test_indexes.py` pins selected named indexes on the same sqlite backend. No tier runs any
of these assertions against postgres, so whether the portable index declarations actually earn an index scan under
postgres's own planner stays unproven.

Standing in for a tier: every index declaration here is `bzh:sql-portable` — ordinary SQLAlchemy `Index()` DDL, not a
sqlite-specific construct — so a postgres planner choosing a table scan over one would be a planner-statistics anomaly
(e.g. an empty table) rather than a declaration defect. Do not add a postgres-backed component tier to close this: the
hosted hub runs SQLite, not postgres (`blizzard-infra`'s `deploy/compose.yaml`), so dogfooding never exercises the
postgres planner. Blizzard's own `packaging/docker/compose.yaml` reference deployment does run postgres, but no test
tier watches its planner either — an adopter's compose stack is not something any of blizzard's own tiers connects to.
The gap stays open, not permanent: it closes the day some tier gains a postgres-backed component run, which the
reference compose image already makes possible.

## The worker's push to a real forge

The worker, not the runner, pushes its branch before declaring it (`blizzard runner artifact commit`), and
`blizzard:service-test` and `blizzard:crash-sweep` only ever exercise that push against the `file://` mock origins the
fixture workspace mints, never against a real forge.

Standing in for a tier: a push failure specific to a real remote — auth, a GitHub branch-protection rule, network — is
exercised by the dogfood deployment (`workspace:/context/project/singleton-instance.md`), whose build transcripts show
the worker pushing to real GitHub. Do not add a real-forge CI tier.

## A garden node prompt's wording

The packaged `garden-routine` prompts carry the routine's whole method: `survey.md` resolves the routine's slug as an
axis against the target project's gardening-axes registry, follows that entry's Criteria pointer, and records its
declared Measurement, and `propose.md` rules what a proposal's `findings` may cite and how its `class` is spelled. The
same gap holds for the packaged `ideation` graph's prompts: its `survey`/`reconcile`/`propose` carry the charter
resolution and proposal-classing behavior that replaces `garden-routine`'s standard-judged method — resolving the
target's own charter rather than a standard, and classing a proposal as `direction`/`tweak`/`retire` rather than citing
findings a fix answers. The declared methods reach the mechanical half only — `blizzard:unit-test`'s packaged-prompt
byte bars (`blizzard/tests/guards/test_prompt_byte_bars.py`) and its `blizzard hub` verb guard,
`blizzard:component-test`'s graph mint and choice-edge resolution, and `blizzard:service-test`'s
`test_garden_routine_runs_end_to_end_on_all_six_paths` and `test_ideation_runs_end_to_end_on_all_authored_paths`, whose
scripted node bodies deliberately exercise no model at all. That `survey` actually resolves its axis from the target's
registry rather than improvising a yardstick, that `propose` actually cites the refs its own run just minted, or that
`ideation`'s `survey`/`reconcile`/`propose` actually resolve the target's charter and class a proposal correctly, is
asserted by nothing: a prompt is an input to a model no tier runs.

Standing in for a tier: a live routine run against a real fleet, whose delivered finding set and docket are read back
and judged against what the axis entry declares — the dogfood deployment
(`workspace:/context/project/singleton-instance.md`) is where that evidence is produced, and a prompt rewrite owes one
before its wording is treated as proven. Do not answer this with a tier that scores prompt prose against a rubric, and
do not read the scripted mock-harness path as evidence about the model: it asserts the machinery a model's output flows
through, which is the half that already has a tier.

## The review-fail, deliver-conflict, and inherited-CI-failure loops' prompt behavior

`bas-hwf`'s `iterate` and `pre-push` prompts, together with `build.md`/`review.md`/`review.judgement.md`/
`retrospective.md`, carry this lane's whole method for the review-fail loop, the deliver-conflict loop, and their
retiering off the frontier tier `build` alone still runs on. The declared methods reach the mechanical half only —
`blizzard:unit-test`'s packaged-prompt byte bars and `tests/unit/hub/graphs/test_basic_harness_workflow_graph.py`'s
mint-validation and routing pins, and `blizzard:component-test`'s graph mint and choice-edge resolution. That `iterate`
actually answers review's findings as a cold read rather than assuming `build`'s own reasoning, that `pre-push`'s
severity triage lands correctly, or that `retrospective` can reconstruct the journey from the chunk's asset trail alone
— with no lineage memory of `build` or `iterate`, unlike `bas-dwf`'s `pre-push` — is asserted by nothing: a prompt is an
input to a model no tier runs.

The same residue covers `adv-dwf`'s `build.from-deliver.md`, `bas-dwf`'s `build.from-deliver.md`, and `bas-hwf`'s
`iterate.from-deliver.md` — the `deliver` → repair-node addenda a base-inherited CI failure routes through on every lane
— and each lane's `pre-push.md` rebase-to-empty qualifier. The `land` action's own classification is proven by
`blizzard:unit-test`'s `land` action cases over a scripted forge and `tests/unit/hub/domain/graph/test_authoring.py`'s
per-lane edge/addendum pins; that a worker reads the addendum's repair charge correctly, or applies the loop bound's
chunk-history check rather than repeating the repair a second time, is not. Nor is whether a `failure` bounce's
own-defect case is actually triaged `significant` rather than treated as a plain rebase, or whether a repair worker
reads `delivery-findings` at all. No tier asserts that a repair worker reads a foreign-advance `failure` correctly,
rather than adopting the foreign commit under `resolved`.

Every lane's `retrospective.md` verifies landing by the PR's own merge state and its merged sha's reachability from
base, never the sha pre-push declared — no tier reads this leg back; a worker misreading it (checking the wrong sha, or
skipping the merge-state read) is silent until a live chunk exposes it.

`adv-dwf`'s `verify.md` and `review.md`, with their `*.from-pre-push.md` addenda, scope a second or later visit to the
delta since the tip the gate's own prior report recorded, and let a delta that reaches nothing a declared method covers
pass without a re-run. The byte bars and `tests/unit/hub/graphs/test_adw_docket.py`'s pointer census hold the prompts'
mechanics; that a re-visiting worker diffs from the recorded tip rather than trusting `build`'s account of its fix,
scopes by the change's own commits once a rebase or base merge intervenes, re-runs every method the delta reaches or the
prior report records as failed, and records the scoping decision in the new report is asserted by nothing — a scoping
that quietly skips a method the delta touches passes the same as an honest one until a live chunk exposes it.

`adv-dwf`'s `mutation.md`, `mutation.judgement.md`, and `review.from-mutation.md`, and the survivor bullet in
`build.from-review.md`, carry the delivery-time mutation report's whole method: run the project's declared diff-scoped
method from each repo's newest declared tip, publish a report that always exists, sort survivors under the project's
classification, and answer a real survivor with the killing assertion or a recorded equivalence. The byte bars, the
session pins in `tests/unit/hub/graphs/test_packaged_graph_sessions.py`, and the delta mode's own unit cases reach the
mechanical half. That a worker uses the declared tip rather than its worktree's reset HEAD, states the reason where no
method is declared, carries a prior report forward only when the change's functions did not move, and raises each
survivor as `should-fix` rather than `blocking` is proven for one path by `blizzard:manual-live-node`; the
`build.from-review.md` bullet is reachable only on a review-`fail` round, which that run does not force, and is asserted
by nothing.

Standing in for a tier: a live chunk run through each lane on the dogfood deployment
(`workspace:/context/project/singleton-instance.md`), whose transitions, bounces, and retrospective are read back and
judged against the routing these prompts intend. That evidence is only producible once the landed graph directory is
re-minted, so this entry records a standing obligation on the lanes' wording rather than a phase gate. Do not answer
this with a tier that scores prompt prose against a rubric.

## The cross-repo OpenCode lever roster

`blizzard-mock`'s `opencode_surface.levers.Lever`/`CATALOG` and `blizzard`'s `_fake_binary`
(`tests/service/harnesses/test_opencode_compatibility_service.py`) kwarg roster are two independently maintained 1:1
mirrors of the same misbehaviour vocabulary — `_fake_binary` claims its mapping is exhaustive against the `Lever` enum,
but `blizzard` deliberately holds no dependency on `blizzard-mock` (`tests/support/scaffolding.py::github_double`'s
established stance), so nothing mechanical can diff the two rosters. A member added on one side with no matching update
on the other drifts silently: a new `blizzard-mock` lever goes untested by `blizzard`'s diagnostic cases, or a stale
`blizzard` kwarg targets a retired lever name and fails loudly only when `mock-opencode emit` rejects it at runtime.

The same gap holds for OpenCode 2: `opencode2_core.levers.Lever` and `_LEVERS`
(`tests/service/harnesses/test_opencode2_compatibility_service.py`), with its `len(_LEVERS)` pin as the trip-wire.

Standing in for a tier: `_fake_binary`'s own `len(lever_flags)` assertion pins the count as a trip-wire, and
`bzh:opencode-lever-roster-extends-both-sides` in [`./companion-changes.md`](./companion-changes.md) obligates a roster
change to land both sides in the same commit family. Neither closes the gap mechanically — the count can hold while a
name silently swaps — so a roster change's correctness rests on the author following the companion-changes rule, not on
a tier that would need the cross-repo import `tests/support/scaffolding.py::github_double`'s established stance forbids.

## The OpenCode subscription cost estimate against a live step

`OpenCodeAdapter`'s zero-cost estimate — the price-cache seam, the tier rule, and the per-step split between `cost_usd`
and `estimated_cost_usd` — is pinned at `blizzard:unit-test` against a fake `IOpenCodePriceCatalog` and hand-authored
`models.json` fixtures, and in the same tier by a real `OpenCodeAdapter` over that fake catalog driven through
`UsageRecorder.record_worker` into a real runner store's outbound payload. No tier proves either half of this against a
real OpenCode subscription step: that `resolve_price_cache_path`'s resolved location is actually the cache file the
worker's own OpenCode process wrote to (never a stale or differently-scoped cache a test fixture only assumes matches),
and that the computed estimate agrees with what OpenCode itself would have billed a non-subscription call for the same
step. A fake catalog proves the tier rule is applied correctly to whatever entry it is handed; it proves nothing about
whether that entry, or its resolved path, is real.

Standing in for a tier: a change to the estimation path — the price cache, its path resolution, or the adapter's
per-step pricing — owes `blizzard:manual-runner` together with `web:manual-board`, run against a local runner with a
real OpenCode subscription binding and a local hub (`workspace:/context/project/hub-data-modes.md`; never the hosted
hub): one real node-step observed showing its `~`-marked figure on the board and in `hub chunk get`, the estimate folded
into the billed amount. Nothing repeats that observation automatically, so the change's author owes it by hand. Do not
add a real-token/live-OpenCode CI tier to close this — an external harness's live pricing behavior sits outside a
hermetic, network-free CI tier's reach.

## Projects' migration and writes under Postgres

The projects mechanisms below have the same exposure as tenancy's: every tier runs on SQLite, with one writer lock and
foreign keys off, so each holds there by construction and stays unverified on Postgres.

- **The project keys.** The `fk_<table>_projects` foreign keys, `fk_questions_projects` and `fk_decisions_projects`
  among them, have never been enforced against a written row, since every tier leaves foreign keys off. Nor has the
  tenant drain run over rows those keys bind.
- **The slug move.** A project's slug move (`update_project`, `src/blizzard/hub/store/internal/project_store.py`) runs
  in one transaction. It reads for a current holder of the new slug, deletes the new slug's former-slug row, updates the
  project, then records the slug it left. Under READ COMMITTED each statement reads its own snapshot. What two
  concurrent writes touching one slug leave is unverified: a uniqueness refusal in place of `ProjectSlugTaken`, or a
  former-slug row the other write removed.
- **A work source's slug move.** It takes the project slug move's shape, so it shares that move's race under READ
  COMMITTED, equally unverified.
- **An ingest against a link or unlink.** An ingest takes the `keyed_locks` key of the project it mints into before its
  pointers' keys, and every source link or unlink takes the same project's key (`project_source_links_lock`,
  `src/blizzard/hub/domain/projects/links.py`), so the links an ingest read stand until it commits. That an unlink
  racing an ingest under READ COMMITTED waits on the key rather than committing between the ingest's link read and its
  mint is unverified; SQLite's writer lock serializes the two whatever the key.
- **A landed repository row's keys.** `delivery_repo_landed`'s foreign keys to its chunk and its tenant have never been
  enforced, and its `repository_id` carries neither a unique key nor a foreign key to the repository record: that a
  landing names a repository its project linked is held by the invariant checker's `hub:landed-repository-linked`
  (`src/blizzard/hub/store/internal/invariants.py`) alone, and its behavior under enforced keys is unverified.
- **A chunk's captured targets.** A chunk's repository targets are inserted once under its row lock — at its claim, in
  the route's own transaction, and at a delivery's submission (`ChunkTargetsStore.capture`,
  `src/blizzard/hub/store/internal/chunk_targets_store.py`) — reading the held rows and inserting only the missing ones.
  That the row lock alone, not a SQLite writer lock, keeps a claim and a submission racing on Postgres from both
  inserting one repository's row is unverified; the `(tenant_id, chunk_id, repository_id)` unique key would refuse the
  second insert, a refusal no path handles.
- **A link's base-branch write.** A link's `base_branch` edit compares and sets the link's revision (`record_link`,
  `src/blizzard/hub/store/internal/project_link_store.py`); that two concurrent edits under READ COMMITTED leave one
  winner and one revision conflict is unverified.
- **A question or decision under a contended chunk lock.** A question or decision written while its chunk's row lock is
  contended is unverified under concurrent writes on Postgres.
- **The `?project=` read plans.** Every read a `?project=` narrows has its `EXPLAIN QUERY PLAN` shape asserted on SQLite
  only, so whether Postgres's planner uses the project read indexes for it stays unproven, as
  [§The query-plan assertions never run under postgres](#the-query-plan-assertions-never-run-under-postgres) states for
  every index.
- **The forge and secret keys.** A forge or secret retire, and every work-source or repository write naming one, declare
  its `FORGE` or `SECRET` key in their domain unit before any read. That each verb declares its keys is asserted by unit
  test (`tests/unit/hub/domain/config/test_record_verb_locks.py`), and that the shared key makes a retire and a
  referrer's enable exclude each other under READ COMMITTED by `blizzard:postgres-uow-concurrency`'s forge and secret
  pairs. The verbs themselves run on SQLite only, where the writer lock serializes the two whatever the key.

Standing in for a tier: the slug-move and link tests on SQLite, and the portable SQL `bzh:sql-portable` holds each
statement to. The gap closes as the tenancy one above does.

## Hosts under Postgres

The hosts mechanisms below have the same exposure as projects': every tier runs on SQLite, with one writer lock and
foreign keys off, so each holds there by construction and stays unverified on Postgres.

- **The host key.** The `fk_runner_registrations_hosts` key has never been enforced against a written row, nor has the
  tenant drain run over rows it binds.
- **The host fact lane's upserts.** `host_high_water`, `host_external_usage`, and `host_external_usage_misses` are each
  tenant-keyed and carry no key on `host_id`; the upserts that refresh a `(host_id, slug)` row in place have only run
  under SQLite's writer lock.
- **The registration columns added above the baseline.** The revisions adding nullable `runner_registrations` columns —
  for the reported version, the refusal reason and when it was judged; `agents`; `declining` — are each a
  `batch_alter_table` rebuild on SQLite and native `ALTER`s on Postgres. They reach head and return to base under
  `blizzard:manual-postgres-migrations`; those rebuilds over a table the `fk_runner_registrations_hosts` key binds have
  never run where foreign keys are enforced.
- **The host column added above the baseline.** The revision adding the nullable `hosts.urls` column is a
  `batch_alter_table` rebuild on SQLite and a native `ALTER` on Postgres. A hand run under
  `blizzard:manual-postgres-migrations` took it to head, down to base and up again, and walked it down and up over a
  populated host row, which kept its `url` and read `NULL` in the new column; no tier repeats that run. The rebuild has
  never run over a `hosts` table that rows in other tables bind where foreign keys are enforced.
- **A live host name's uniqueness.** `HostRegistryStore.add` reads the tenant's live host names and inserts under the
  scoped write's tenant-row lock, so two adds of one name queue on that row. That the lock alone keeps a name unique
  among live hosts is unverified on Postgres; SQLite's writer lock serializes every add. A report reads the other live
  names outside any lock and so can record a name an add took in between on either backend.
- **An adoption racing another.** `HostRegistryStore` places a runner with an `UPDATE … WHERE host_id IS NULL` and rolls
  the write back on a runner that matched no row. That two adoptions of one runner under READ COMMITTED leave it under
  exactly one host is unverified; SQLite's writer lock serializes them.

Standing in for a tier: the registration-column revisions' colocated tests, the adoption and name tests on SQLite, and
the portable SQL `bzh:sql-portable` holds each statement to. The gap closes as the tenancy one above does.

## The runner store under Postgres

The runner store runs on SQLite or Postgres by configuration (`bzh:sql-portable`), and every tier runs it on SQLite, so
its runner key and counters hold there by construction. `blizzard:store-baseline` builds the runner baseline from an
empty Postgres store and holds it to `contracts/store/runner.json`; what that proof and the hand runs under
`blizzard:manual-postgres-runner-migrations` leave unverified:

- **The counter allocation.** `insert_outbox_row` (`src/blizzard/runner/store/internal/base.py`) advances a runner's
  lane under READ COMMITTED. Eight threads racing the first allocation of a new runner's lane were issued `1` through
  `8`, with the counter at `8` and the invariants holding.
- **The usage-limit floor tables.** The revision creating the empty `subscription_usage_limits`,
  `subscription_floor_clears`, `runner_usage_limits`, and `runner_floor_clears` tables, whose downgrade drops them, has
  not been executed on Postgres; it creates four tables of portable column types and writes no data.
- **The fact append sequence.** The revision adding a nullable `seq` to `env_bindings`, `binding_releases`,
  `pause_parks`, `pause_park_resumes`, `requeues` and `leases` creates `fact_counters` and numbers every existing row
  per runner, openers before closers at a tied instant. The hand run seeded its parent shape with two runners holding
  same-instant ties across all three closure pairs, upgraded it, and found every held binding, open park and pending
  requeue unchanged, each counter at its runner's row count, and the invariants holding. It then took the revision down,
  which restored the parent schema with every row kept, up again to the same schema, and re-ran the upgrade over the
  numbered store, which changed nothing. Two writers racing the first allocation of a new runner's fact counter were not
  run on Postgres; the allocation is the outbox counter's, which that run covers.
- **The takeover entries.** The revision creating `takeover_entries`, with a foreign key to `takeovers`, inserts an
  entry for every takeover open at that moment; its downgrade drops the table. It has not been hand-run under
  `blizzard:manual-postgres-runner-migrations`: its colocated test walks it forward, back and forward again on SQLite
  only, and it uses portable column types and `INSERT … SELECT`. SQLite leaves foreign keys off, so the foreign key is
  enforced on Postgres alone and no tier exercises it.
- **The lease-row lock of a declaration.** A declaration's admission and an outcome's capture each run as one write
  transaction whose first statement is a no-op update of the lease's `leases` row (`LeaseLockStore.locked`,
  `src/blizzard/runner/store/internal/lease_lock_store.py`), so the admission either commits before the capture and is
  carried, or queues behind it and is refused. SQLite's single writer lock serializes the two whatever the row, and
  `tests/component/runner/test_declaration_admission_races.py` runs a second thread against a held capture unit there.
  No tier shows that Postgres queues the second writer on the row and reads the buffered submission once it commits.
- **The empty-store upgrade.** `blizzard:store-baseline` applies the baseline alone. No run has carried an empty
  Postgres store from the baseline to head, so a revision above the baseline has run on Postgres only where a bullet
  above says so.

Standing in for a tier: `blizzard:store-baseline` for the baseline, the colocated migration tests of the revisions above
it and the seam's component tests on SQLite, and the portable SQL `bzh:sql-portable` holds each statement to. The hand
run is not repeatable from a durable script, since the matrix carries the method and no driver. The gap closes as the
tenancy one above does.

## Hub actions' columns under Postgres

Every tier runs the two hub action revisions on SQLite only: the first adds `graph_nodes.action` and
`graph_nodes.action_args`, and the second adds `graph_nodes.legacy_run` and carries each stored hub row with no action
onto one.

- **What a hand run reached.** On a throwaway Postgres 16 cluster under `blizzard:manual-postgres-migrations`, the chain
  reached head, returned to base, and reached head again, with one translatable and one untranslatable hub row seeded at
  the first of the two revisions: the first came out carrying its script's action, the second keeping its `run:` in
  `legacy_run`.
- **What no tier repeats.** No CI tier runs that pass, so a later change to either revision is unverified on Postgres
  until someone runs it again, and neither revision's backfill has run there over more than those two rows.

Standing in for a tier: the second revision's colocated migration test and `blizzard:store-contract`, both on SQLite,
and the portable SQL `bzh:sql-portable` holds each statement to.

## The flow tables under Postgres

Every tier runs the revision creating the flow tables on SQLite only. It creates `flows`, `flow_submissions`,
`flow_submission_flows`, `flow_submission_closures`, `hub_turns`, and `flow_facts`, with their indexes, and writes no
row.

- **What a hand run reached.** On a throwaway Postgres 16 cluster under `blizzard:manual-postgres-migrations`, an empty
  store reached head at the revision, returned to base leaving only `alembic_version`, and reached head again. It then
  stepped down to the revision's parent, which left none of the six tables, and up to head once more.
- **What no tier repeats.** No CI tier runs that pass, so a later change to the revision is unverified on Postgres until
  someone runs it again. No row was written through the tables there either, so the foreign keys SQLite never enforces
  have not met a submission, a closure, or a turn on Postgres.

Standing in for a tier: the revision's colocated migration test and `blizzard:store-contract`, both on SQLite, and the
portable SQL `bzh:sql-portable` holds each statement to.

## The hub-execution slot's drop under Postgres

Every tier runs the revision dropping the hub-execution slot table on SQLite only. It drops the table, its tenant index
and its rows; its downgrade recreates the table empty, with its index and both foreign keys.

- **What a hand run reached.** On a throwaway Postgres 16 cluster under `blizzard:manual-postgres-migrations`, an empty
  store reached head at the revision with no slot table, stepped down to the revision's parent leaving the table empty
  with its primary key, its tenant index, and both foreign keys, and reached head again with the table gone.
- **What no tier repeats.** No CI tier runs that pass, so a later change to the revision is unverified on Postgres until
  someone runs it again. No slot row was seeded there, so the drop of a populated table has not met Postgres.

Standing in for a tier: the revision's colocated migration test, which seeds a row, and `blizzard:store-contract`, both
on SQLite, and the portable SQL `bzh:sql-portable` holds each statement to.

## Landing-policy operator guidance

The policy-selection page's capability preconditions follow `hub/domain/config/landing_policies.py` and the runtime
capability guard in `hub/delivery/flow_turn.py`. Its fast-forward candidate, protected-write and orphan-pruning claims
follow `hub/delivery/actions/landing/fast_forward.py` and the forge ref calls in `hub/forge/internal/github_landing.py`.
Its park timeout and human-merge claims follow `hub/delivery/actions/landing/park.py` and the wait cadence in
`hub/domain/delivery/flows.py`; rollback settlement is enforced by the downgrade of the hub revision adding the park
wait, which refuses while a repository or an open submission holds a policy other than `merge-on-checks`. The mock-forge
service specs and policy crash sweep reach the principal paths, but no tier verifies an operator's push-CI configuration
or the manual orphan-branch pruning step.

## The runner host's invariant read under Postgres

The runner host's invariant route opens its single read through the same dialect-aware opener as the hub's, which on
Postgres sets `REPEATABLE READ` and read-only before the first statement. Every tier runs the runner store on SQLite, so
only the `BEGIN` branch runs there.

- **What the hand run reaches.** `blizzard:manual-postgres-invariants` runs the hub on Postgres, so the hub half's
  `REPEATABLE READ` read runs there, across tenants. It runs the runner host on its default SQLite store.
- **What no run reaches.** No run has carried the runner chain from an empty Postgres store to head
  ([§The runner store under Postgres](#the-runner-store-under-postgres)), so no method hosts a runner on Postgres, and
  the runner route's `REPEATABLE READ` branch is unexercised.

Standing in for a tier: the hub half's run of the same opener under `blizzard:manual-postgres-invariants`, and the
runner half's single-read component tests on SQLite. The gap closes the day a method hosts a runner on Postgres, or some
tier gains a Postgres-backed runner run.

## The no-CI opt-in columns under Postgres

The migration adds non-null, default-false `allow_no_ci` columns to repositories and frozen flow submission terms. On a
disposable Postgres cluster, the hub chain passed head → base → head, and a seeded parent store passed upgrade →
downgrade → upgrade. No CI tier repeats those Postgres runs; the colocated migration test runs on SQLite.

## Landing policies' columns under Postgres

Every tier runs the revision adding landing policies on SQLite only. It adds `repositories.landing_policy` and
`hub_node_poll.kind`, each added nullable with its server default, filled in bounded pages, and tightened to `NOT NULL`
keeping that default. It adds nullable `repositories.park_timeout_hours` and `hub_node_poll.last_polled_at`, and creates
`project_repository_positions` and `flow_submission_terms` empty. On SQLite each tightening is a `batch_alter_table`
rebuild; on Postgres it is a native `ALTER`.

- **What a hand run reached.** On a throwaway Postgres 16 cluster under `blizzard:manual-postgres-migrations`, an empty
  store reached head, returned to base leaving only `alembic_version`, and reached head again. It then stepped down to
  the revision's parent, seeded 2,500 `repositories` rows and 2,500 `hub_node_poll` rows, and came back up to head.
  Every row read `merge-on-checks` and `pending`, both columns read `NOT NULL` with their defaults, and a row inserted
  without either column read its default. A second step down kept every seeded row and dropped the four columns and both
  tables.
- **What no tier repeats.** No CI tier runs that pass, so a later change to the revision is unverified on Postgres until
  someone runs it again. No row was written through the two new tables there, so their foreign keys onto a link and a
  submission have not been enforced against a row.

Standing in for a tier: the revision's colocated migration test and `blizzard:store-contract`, both on SQLite, and the
portable SQL `bzh:sql-portable` holds each statement to.

## Routines' slug under Postgres

Every tier runs the revision adding a routine's slug on SQLite only. It adds `routines.slug` nullable with a server
default, fills it from `name` in bounded pages, and tightens it to `NOT NULL` keeping that default. It replaces
`uq_routines_project_name` with `uq_routines_project_slug` and rebuilds the tenant-wide handle index on the slug. On
SQLite the tightening and the constraint swap are one `batch_alter_table` rebuild; on Postgres they are native `ALTER`s.

- **What a hand run reached.** On a throwaway Postgres 16 cluster under `blizzard:manual-postgres-migrations`, an empty
  store reached head, returned to base leaving only `alembic_version`, and reached head again. It then stepped down to
  the revision's parent, seeded 2,500 `routines` rows, half with a non-slug name, and a finding keyed by one of them,
  and came back up to head. Every slug read its row's name, the column read `NOT NULL` with its default, the slug
  constraint and index stood in place of the name's, the finding row was unchanged, and a second routine of an
  already-held slug was refused by the constraint. A step down after one routine was renamed restored the name
  constraint and index, dropped the column, and read every name as its slug, so the rename was the only loss.
- **What no tier repeats.** No CI tier runs that pass, so a later change to the revision is unverified on Postgres until
  someone runs it again.

Standing in for a tier: the revision's colocated migration test and `blizzard:store-contract`, both on SQLite, and the
portable SQL `bzh:sql-portable` holds each statement to.

## Cadences under Postgres

Every tier runs the revision adding the cadence tables on SQLite only. It creates `cadences`, `cadence_chores`,
`cadence_chore_scopes`, and `cadence_lifecycle_facts`, each tenant-keyed with its foreign keys and a tenant-led index,
and backfills nothing. On Postgres, foreign keys are enforced, DDL is transactional, and identifiers stop at 63
characters.

- **What a hand run reached.** On a throwaway Postgres 16 cluster under `blizzard:manual-postgres-migrations`, an empty
  store reached head with the four tables and their primary, unique, and foreign-key constraints, returned to base
  leaving only `alembic_version`, empty, and reached head again. It then stepped down to the revision's parent, which
  dropped the four tables, and came back up to head. A hosted hub app over that store created a cadence with a chore,
  edited the chore keeping its id, refused a stale `If-Match` with `409`, retired and re-enabled the cadence, refused a
  second cadence of the same slug, and wrote one change row for each write.

## Credentials under Postgres

Every tier runs the revision adding the credential tables on SQLite only. It creates `credentials`,
`credential_former_slugs`, and `credential_lifecycle_facts`, each tenant-keyed with its foreign keys, and adds a
nullable `credential_id` to `repositories` and `work_sources`, and backfills nothing. On Postgres, foreign keys are
enforced, DDL is transactional, and identifiers stop at 63 characters.

- **What a hand run reached.** On a throwaway Postgres 16 cluster, an empty store reached head under
  `blizzard hub init`. A hub hosted over it held two tenants, each with a secret, a forge, a repository, and a
  credential `ConfigAuthoring.create_credential` wrote, which the repository named by a SQL update.
  `blizzard:manual-postgres-invariants`, steps 1–2, then ran: `GET /api/admin/invariants` answered `200` with no
  violation, and after one tenant's `credentials.authority` was rewritten by SQL it answered `200` with
  `hub:credential-authority-derived` naming that tenant and credential.
- **What `blizzard:rehearsal` now covers.** Its Postgres leg, on every `master` push, migrates a supported release's
  store through the credential revisions, including the carry-over, and reads the journey's repository and work source
  and the credential each names through the routes, then ingests and lands with the carried-over credential.
- **What no tier repeats.** No CI tier runs the invariant pass under Postgres, and none writes a credential, or a
  referrer's `credential_id`, through the credential routes there.

Standing in for those: the revision's colocated migration test, `blizzard:store-contract`, and the credential
invariants' component tests, all on SQLite, and the portable SQL `bzh:sql-portable` holds each statement to.

## Errand marks under Postgres

Every tier runs the revision adding the errand marks on SQLite only. It adds nullable `cadence_id` and `chore_id` to
`work_item_runs` with a tenant-led index over its tenant, chore, and scope, and a nullable `linked_at` to
`routine_scopes`, and backfills nothing: a run minted by hand and a link made before the stamp both read null. Its
upgrade is native `ADD COLUMN`s on either backend; its downgrade is a `batch_alter_table` rebuild of each table on
SQLite and native `ALTER`s on Postgres.

- **What a hand run reached.** None yet: `blizzard:manual-postgres-migrations` has not been run over this revision, so
  head, base, and head again, and a step from its parent with seeded `work_item_runs` and `routine_scopes` rows, are
  each unverified on Postgres.
- **What no tier repeats.** No CI tier runs that pass, so the revision stays unverified on Postgres until someone runs
  it.

Standing in for a tier: the revision's colocated migration test and `blizzard:store-contract`, both on SQLite, and the
portable SQL `bzh:sql-portable` holds each statement to.

## Forge references required under Postgres

Every tier runs the revision that keys repositories and work sources on their forge on SQLite only. It refuses, before
any write, a record whose `forge_id` is null, names no forge, or names another tenant's forge. It then drops
`repositories.forge_api_url` and `work_sources.api_base` and `web_base`, tightens both `forge_id` columns to `NOT NULL`
under a foreign key onto `forges`, and rekeys `uq_repositories_tenant_coordinate` and
`uq_work_sources_tenant_provider_locator` on the forge. Its downgrade refuses a tenant holding one locator on two
forges, then refills the address columns from each record's forge and restores the address-keyed constraints. On SQLite
each table is one `batch_alter_table` rebuild; on Postgres the same batch is native `ALTER`s.

- **What a hand run reached.** On a throwaway Postgres 16 cluster under `blizzard:manual-postgres-migrations`, an empty
  store reached head, returned to base leaving only `alembic_version`, and reached head again. It then stepped down to
  the revision's parent, seeded 1,200 repositories and 1,200 work sources split across two forges, one of them retired,
  with half of each record kind retired, and came back up to head. Every record kept its `forge_id`, both columns read
  `NOT NULL`, both foreign keys and both rekeyed constraints stood, and the address columns were gone. At head, a second
  work source of an already-held locator on the other forge made the step down refuse, naming the tenant and both
  sources, with nothing written. Once the locator was changed by hand, the step down refilled every address from its
  forge, a null `web_base` included, read `forge_api_url` `NOT NULL` again, and restored both address-keyed constraints
  with the foreign keys dropped. A work source set back to no forge at the parent made the step up refuse, naming it.
- **What no tier repeats.** No CI tier runs that pass, so a later change to the revision is unverified on Postgres until
  someone runs it again.

Standing in for a tier: the revision's colocated migration test and `blizzard:store-contract`, both on SQLite, and the
portable SQL `bzh:sql-portable` holds each statement to.

## The project lens is not an access boundary

The board's project lens narrows what a view reads, and a call naming no project reads the whole tenant; access is
decided by the tenant alone. Nothing proves a person sees only a project's records, because nothing restricts them to
one — a stated non-goal, not a missing check.

## Refusals absent from a supported release's document

`blizzard:compat` compares declared refusal status, media and schemas on the selected wire and API surfaces, but a
supported release's OpenAPI document can omit a refusal its runner parses. An absent declaration supplies no baseline
shape for comparison; it is not evidence that the refusal is compatible.

Standing in for a tier: the open-vocabulary gate (`tests/guards/test_open_response_vocabulary.py`) checks parsed
vocabularies, and `blizzard:rehearsal` exercises released clients against candidate refusals as described in
[commands/rehearsal.md](./commands/rehearsal.md). Other undeclared historical refusal paths still owe the by-hand
judgement [../../workflows/judging-a-break.md](../../workflows/judging-a-break.md) describes.

## An older client reading a newer response value

No method runs a client from a supported release against a value its vocabulary gained. `blizzard:rehearsal` upgrades
each release's daemons onto the candidate but stages no gained value, and a live env cannot stage one either, since its
own build knows every value it can write. That an open field tolerates an unknown value is proven only inside the tree.

Standing in for a tier: the unit and component tests that feed an unknown value through the parse, the runner's
lifecycle decisions, the drain, and a proxy route (`tests/unit/wire/test_open_response_vocabulary_paths.py`,
`tests/component/runner/test_open_response_vocabulary_paths.py`, `tests/unit/runner/test_unknown_vocabulary_rules.py`),
and the open mark a release's document carries for each position its clients tolerate.
