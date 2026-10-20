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

## The store contract on Postgres

`blizzard:store-contract` reflects a SQLite store only, so a revision that diverges from `schema.py` on Postgres alone
passes it. Standing in: `bzh:sql-portable` and `blizzard:manual-postgres-migrations`. It closes when the rehearsal's
Postgres leg reflects a migrated store through the same producer.

## Per-block prose caps

`bzh:prose-budget`'s `mise run prose-check` fails each root's prose total against the committed baseline, and the
per-block caps are reported only under `--blocks`. Neither half runs automatically: the command is in no CI workflow and
not in `blizzard:gate`, so a total drifts on `master` unratcheted until the next change re-records the baseline and
absorbs it — `blizzard:restatement-sweep` is invoked the same way, by hand. The two halves are independent: a change can
hold every total and still carry an over-cap block, and a baseline re-record absorbs the total while leaving the block
standing.

Standing in for a tier: a change owes a `--blocks` run and a check that no block it added or edited is over cap, and a
baseline re-record is warranted only once that holds. Gating `--blocks` repo-wide is not the fix, because it scopes to
every block in the tree rather than the ones a change wrote, so it fails on prose the change never touched and stops
being read.

## Session stickiness, effective model, and context accounting

The session-model contract — owned by [declared sessions](../../domain/graphs/declared-sessions.md#model-preference) —
is proven at the flag, never at the model a harness ran under. Where the runner supplies no model on resume — OpenCode,
whose resume passes only the session — the contract rests on that harness restoring a resumed session's own model, and
nothing asserts that restoration. The live OpenCode compatibility diagnostic checks that the requested provider/model
and variant survive fresh and resumed exports, but it deliberately supplies them on every invocation and therefore does
not assert effective model stickiness when they are omitted, as the runner's resumes omit them. No tier asserts the
effective context accounting a harness ran under, because the mock façade sees argv and nothing else. `blizzard:e2e`'s
`test_session_modes_e2e.py::test_a_named_pool_threads_one_session_across_nodes_and_reasserts_its_model` asserts the flag
on the Claude Code façade — the mint and every resume carry the same resolved model — and stops there.

Standing in for a tier: what backs the surrounding export behavior is a one-time empirical observation of Claude Code
CLI 2.1.220 and the retained live compatibility evidence for the runner's admitted range (currently `>=1.18.25,<2.0`).
Neither observation proves OpenCode session stickiness when model flags are omitted; each harness also has a
configuration that can defeat stickiness, which `docs/deployment/worker-spawn.md` states as deployment requirements. Do
not add a real-token tier to close this gap.

## The declared compaction window

The declared compaction window travels to the harness as the per-invocation `--autocompact` flag, reasserted on every
invocation and never sticky by omission. The mock-visible tiers — `blizzard:unit-test`'s command-list pins and
`blizzard:component-test`'s wire/stamp round-trip — prove only that the flag is built and threaded, never that it
compacts anything.

Standing in for a tier: `blizzard:manual-autocompact-window` closes this as a live procedure, the same shape as
[`blizzard:manual-external-usage-probe`](./manual.md#blizzardmanual-external-usage-probe) — an external harness's live
compaction behavior sits outside a hermetic, network-free CI tier's reach.

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

`test_mixed_harness_dispatch_service.py` records a proof the mock hub's fidelity leaves unreachable: a bare node
honoring the chunk's own declared default all the way through spawn. `blizzard-mock-hub`'s own `envelope()` route,
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
deliberately mints none of the shapes involved, so no mock-driven `blizzard:service-test` or `blizzard:e2e` exercises
the normalizer, which could drift from a future Claude Code CLI with every tier green. `test_transcript_tab_browser_e2e`
does not close it either: it seeds hand-authored `TurnSegmentView` JSON straight to `POST /api/fleet/transcripts`, so no
normalizer output ever reaches it. OpenCode's own `opencode.transcript.normalizer` is a separate code path this gap does
not reach either way — it is exercised by `blizzard-mock`'s `OpenCodeTranscriptWriter` through a real mock-driven
`blizzard:service-test`, which this one is not.

Standing in for a tier: sidechain and thinking-turn normalization is proven only against hand-authored fixtures, pinned
at `blizzard:unit-test` and by the component-tier projection golden tests, both fed by the same record fixtures — which
transcript shapes are involved, and why, is owned by `blizzard-mock`'s `src/blizzard_mock/harness/README.md`
§"Conversation transcripts". Do not add a real-corpus CI tier reading a developer's `~/.claude/projects`, which is
neither hermetic nor reproducible.

## Claude Code's transcript source position codec, batch budget, and EOF clamps

The position codec, the shared batch budget, and the past-EOF clamps inside `ClaudeCodeTranscriptSource.turns_since` are
pinned at no tier at all. Every component-tier test of the transcript lane binds a scriptable `FakeTranscriptSource`
(`blizzard/tests/runner_fakes.py`), so `tests/test_transcript_pump.py` and `tests/test_transcript_backfill.py` reach the
pump's and the backfill's own decisions and never those three pieces. `OpenCodeTranscriptSource` is a distinct
implementer this gap does not name: its own export-identity cursor, bound token, and `not_found`/`unreadable` split are
pinned at `blizzard:unit-test` — "OpenCode transcript reads never distinguish `not_found`" above covers what that tier
does not.

Standing in for a tier: `blizzard runner transcript reship` and `blizzard runner transcript backfill` drive
`TranscriptPump.drain_segment` with `deadline=None` over a complete historical file from offset 0 until the source
catches up, exercising the three unpinned pieces harder than a tick ever does. The backfill verb is the first path that
requires `ship = true`, so an operator running it against a real `~/.claude/projects` produces evidence of the
forward-read lane that no tier records — which dogfooding does not supply by default, since the transcript lane ships
disabled (`[transcripts] ship = false`).

## The query-plan assertions never run under postgres

`tests/test_finding_store.py`'s `test_list_for_query_plans_as_an_index_search` and
`test_count_by_class_query_plans_as_an_index_search` assert `EXPLAIN QUERY PLAN` on sqlite — the backend every component
test runs against — that `list_for`'s routine+scope read and `count_by_class`'s routine+class read use
`ix_findings_routine_scope`/`ix_findings_routine_class` rather than a table scan.
`tests/test_chunk_fact_table_indexes.py` asserts the same shape over the twenty-one `chunk_id`-filtered fact tables the
`20260829_1930_fact_tables_chunk_id_index` revision indexes, extended by the `20260913_1300_hub_store_hot_path_indexes`
revision's own cases: the three `(chunk_id, epoch)` composites by exact name, the artifacts/graph-choices/transcript-
segments/chunk-work-refs/close-intents hot-path reads, and each of `activity_facts_since`'s eighteen per-source ordered
reads. `tests/test_chunk_usage_statements.py` and its `EXPLAIN QUERY PLAN` case over the spend `_stmt` builder assert
`ix_usage_facts_recorded_at_id` the same way. `tests/test_store_read_index_gate.py`'s scan gate and
`tests/test_runner_store_indexes.py`'s named-index pins assert the same `EXPLAIN QUERY PLAN` shape across every hub and
runner read method's own table vocabulary, plan-classified through the same sqlite backend. No tier runs any of these
assertions against postgres, so whether the portable index declarations actually earn an index scan under postgres's own
planner stays unproven.

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
`blizzard:e2e` and `blizzard:crash-sweep` only ever exercise that push against the `file://` mock origins the fixture
workspace mints, never against a real forge.

Standing in for a tier: a push failure specific to a real remote — auth, a GitHub branch-protection rule, network — is
exercised by the dogfood deployment (`workspace:/context/project/local-instance.md`), whose build transcripts show the
worker pushing to real GitHub. Do not add a real-forge CI tier.

## A garden node prompt's wording

The packaged `garden-routine` prompts carry the routine's whole method: `survey.md` resolves the routine's name as an
axis against the target project's gardening-axes registry, follows that entry's Criteria pointer, and records its
declared Measurement, and `propose.md` rules what a proposal's `findings` may cite and how its `class` is spelled. The
same gap holds for the packaged `ideation` graph's prompts: its `survey`/`reconcile`/`propose` carry the charter
resolution and proposal-classing behavior that replaces `garden-routine`'s standard-judged method — resolving the
target's own charter rather than a standard, and classing a proposal as `direction`/`tweak`/`retire` rather than citing
findings a fix answers. The declared methods reach the mechanical half only — `blizzard:unit-test`'s packaged-prompt
byte bars (`blizzard/tests/test_prompt_byte_bars.py`) and its `blizzard hub` verb guard, `blizzard:component-test`'s
graph mint and choice-edge resolution, and `blizzard:e2e`'s `test_garden_routine_runs_end_to_end_on_all_six_paths` and
`test_ideation_e2e`'s own run, whose scripted node bodies deliberately exercise no model at all. That `survey` actually
resolves its axis from the target's registry rather than improvising a yardstick, that `propose` actually cites the refs
its own run just minted, or that `ideation`'s `survey`/`reconcile`/`propose` actually resolve the target's charter and
class a proposal correctly, is asserted by nothing: a prompt is an input to a model no tier runs.

Standing in for a tier: a live routine run against a real fleet, whose delivered finding set and docket are read back
and judged against what the axis entry declares — the dogfood deployment
(`workspace:/context/project/local-instance.md`) is where that evidence is produced, and a prompt rewrite owes one
before its wording is treated as proven. Do not answer this with a tier that scores prompt prose against a rubric, and
do not read the scripted e2e path as evidence about the model: it asserts the machinery a model's output flows through,
which is the half that already has a tier.

## The review-fail, deliver-conflict, and inherited-CI-failure loops' prompt behavior

`bas-hwf`'s `iterate` and `pre-push` prompts, together with `build.md`/`review.md`/`review.judgement.md`/
`retrospective.md`, carry this lane's whole method for the review-fail loop, the deliver-conflict loop, and their
retiering off the frontier tier `build` alone still runs on. The declared methods reach the mechanical half only —
`blizzard:unit-test`'s packaged-prompt byte bars and `tests/test_basic_harness_workflow_graph.py`'s mint-validation and
routing pins, and `blizzard:component-test`'s graph mint and choice-edge resolution. That `iterate` actually answers
review's findings as a cold read rather than assuming `build`'s own reasoning, that `pre-push`'s severity triage lands
correctly, or that `retrospective` can reconstruct the journey from the chunk's asset trail alone — with no lineage
memory of `build` or `iterate`, unlike `bas-dwf`'s `pre-push` — is asserted by nothing: a prompt is an input to a model
no tier runs.

The same residue covers `adv-dwf`'s `build.from-deliver.md`, `bas-dwf`'s `build.from-deliver.md`, and `bas-hwf`'s
`iterate.from-deliver.md` — the `deliver` → repair-node addenda a base-inherited CI failure routes through on every lane
— and each lane's `pre-push.md` rebase-to-empty qualifier. `land_pr_ci`'s own classification is proven by
`blizzard:unit-test`'s scripted-forge cases and `tests/test_graph_authoring.py`'s per-lane edge/addendum pins; that a
worker reads the addendum's repair charge correctly, or applies the loop bound's chunk-history check rather than
repeating the repair a second time, is not. Nor is whether a `failure` bounce's own-defect case is actually triaged
`significant` rather than treated as a plain rebase, or whether a repair worker reads `delivery-findings` at all. No
tier asserts that a repair worker reads a foreign-advance `failure` correctly, rather than adopting the foreign commit
under `resolved`.

Every lane's `retrospective.md` verifies landing by the PR's own merge state and its merged sha's reachability from
base, never the sha pre-push declared — no tier reads this leg back; a worker misreading it (checking the wrong sha, or
skipping the merge-state read) is silent until a live chunk exposes it.

`adv-dwf`'s `verify.md` and `review.md`, with their `*.from-pre-push.md` addenda, scope a second or later visit to the
delta since the tip the gate's own prior report recorded, and let a delta that reaches nothing a declared method covers
pass without a re-run. The byte bars and `tests/test_adw_docket.py`'s pointer census hold the prompts' mechanics; that a
re-visiting worker diffs from the recorded tip rather than trusting `build`'s account of its fix, scopes by the change's
own commits once a rebase or base merge intervenes, re-runs every method the delta reaches or the prior report records
as failed, and records the scoping decision in the new report is asserted by nothing — a scoping that quietly skips a
method the delta touches passes the same as an honest one until a live chunk exposes it.

`adv-dwf`'s `mutation.md`, `mutation.judgement.md`, and `review.from-mutation.md`, and the survivor bullet in
`build.from-review.md`, carry the delivery-time mutation report's whole method: run the project's declared diff-scoped
method from each repo's newest declared tip, publish a report that always exists, sort survivors under the project's
classification, and answer a real survivor with the killing assertion or a recorded equivalence. The byte bars, the edge
and addendum pins in `tests/test_packaged_graph_sessions.py`, and the delta mode's own unit cases reach the mechanical
half. That a worker uses the declared tip rather than its worktree's reset HEAD, states the reason where no method is
declared, carries a prior report forward only when the change's functions did not move, and raises each survivor as
`should-fix` rather than `blocking` is proven for one path by `blizzard:manual-live-node`; the `build.from-review.md`
bullet is reachable only on a review-`fail` round, which that run does not force, and is asserted by nothing.

Standing in for a tier: a live chunk run through each lane on the dogfood deployment
(`workspace:/context/project/local-instance.md`), whose transitions, bounces, and retrospective are read back and judged
against the routing these prompts intend. That evidence is only producible once the landed graph directory is re-minted,
so this entry records a standing obligation on the lanes' wording rather than a phase gate. Do not answer this with a
tier that scores prompt prose against a rubric.

## The cross-repo OpenCode lever roster

`blizzard-mock`'s `opencode_surface.levers.Lever`/`CATALOG` and `blizzard`'s `_fake_binary`
(`tests/service/test_opencode_compatibility_service.py`) kwarg roster are two independently maintained 1:1 mirrors of
the same misbehaviour vocabulary — `_fake_binary` claims its mapping is exhaustive against the `Lever` enum, but
`blizzard` deliberately holds no dependency on `blizzard-mock` (`tests/support.py::github_double`'s established stance),
so nothing mechanical can diff the two rosters. A member added on one side with no matching update on the other drifts
silently: a new `blizzard-mock` lever goes untested by `blizzard`'s diagnostic cases, or a stale `blizzard` kwarg
targets a retired lever name and fails loudly only when `mock-opencode emit` rejects it at runtime.

Standing in for a tier: `_fake_binary`'s own `len(lever_flags)` assertion pins the count as a trip-wire, and
`bzh:opencode-lever-roster-extends-both-sides` in [`./companion-changes.md`](./companion-changes.md) obligates a roster
change to land both sides in the same commit family. Neither closes the gap mechanically — the count can hold while a
name silently swaps — so a roster change's correctness rests on the author following the companion-changes rule, not on
a tier that would need the cross-repo import `tests/support.py::github_double`'s established stance forbids.

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
hub): one real node-step observed showing its `~`-marked figure on the board and in `hub chunk show`, the estimate
folded into the billed amount. Nothing repeats that observation automatically, so the change's author owes it by hand.
Do not add a real-token/live-OpenCode CI tier to close this — an external harness's live pricing behavior sits outside a
hermetic, network-free CI tier's reach.

## Per-key non-serialization of keyed write locks

`keyed_locks` rows (`bzh:store-exclusive-write`) serialize two ingests of one pointer, or two first mints of one graph
name, while letting writers of different keys proceed. That per-key property holds only on Postgres. Every tier runs on
SQLite, whose single writer lock serializes every writer whatever its key, so no tier can observe a writer of a
different key proceeding, or a concurrent insert of one key losing to an `IntegrityError`.

Standing in for a tier: the per-key structure, asserted at `blizzard:component-test` on what is written — each ingest
locks only the `keyed_locks` rows of its own pointers — together with the same-key interleaving, which SQLite does
exercise. Do not add a Postgres tier to close this.

## Tenancy's migrations and locks under Postgres

Every tier runs on SQLite, whose single writer lock serializes every writer, and no tier runs a migration or a
concurrent write against Postgres. The tenancy mechanisms below therefore hold on SQLite by construction and stay
unverified on Postgres, where each statement of a READ COMMITTED transaction reads its own snapshot and foreign keys are
enforced:

- **The migration chain.** The tenancy revisions, `20261008_1100_tenants` through
  `20261008_1720_tenant_deletion_closed_at` (`src/blizzard/hub/store/migrations/versions/`), reach head and return to
  base on an empty Postgres store under `blizzard:manual-postgres-migrations`. Their backfills over populated rows have
  run on SQLite only.
- **A scoped write's closed-tenant check.** A scoped write opens with one statement,
  `UPDATE tenants … WHERE tenant_id = :t AND NOT EXISTS (<the tenant's deletion fact>)` (`_lock_open_tenant`,
  `src/blizzard/hub/store/scoped.py`). On Postgres a write that blocks on a close's lock of that row re-checks, once the
  close commits, the row against its condition, but evaluates the `NOT EXISTS` against the snapshot taken before it
  blocked, so it can still write into the tenant just closed. The drain removes that late row on its next pass, and a
  completion that meets it first fails on the foreign key until the next sweep pass. Closing the hole portably costs a
  separate existence read after the row lock, on every scoped write.
- **The drain under enforced foreign keys.** The drain deletes children before parents in the schema's own dependency
  order (`DRAIN_ORDER`, `src/blizzard/hub/store/internal/tenant_teardown_store.py`) and relies on no cascade, because
  SQLite runs with `foreign_keys` off. No tier drains with foreign keys enforced, so an order that breaks one surfaces
  only on Postgres, as a failed batch.
- **The hub-execution slot's per-tenant lock.** `acquire_hub_exec_slot`
  (`src/blizzard/hub/store/internal/chunk_hub_exec_store.py`) reads the tenant's live slots and inserts one under the
  scoped write's tenant-row lock, so two acquires in one tenant queue on that row while another tenant's never waits.
  That the row lock alone keeps one live slot per tenant is unverified on Postgres; on SQLite the writer lock serializes
  every acquire.
- **The last-open-tenant check.** A tenant's close (`TenantTeardownStore.close`, same file as the drain) refuses to
  close the last open tenant. Two closes of the last two open tenants could each see the other still open and both
  commit, leaving none; the close guards against that by locking every `tenants` row in `tenant_id` order before the
  check, so a second close queues behind the first and reads its committed deletion fact. On SQLite the writer lock
  serializes the two closes whatever the lock order, so no tier can tell whether the ordered locks hold on Postgres.

Standing in for a tier: each mechanism's interleavings that SQLite can run, at `blizzard:component-test`, and the
portable SQL `bzh:sql-portable` holds each statement to. The hosted hub runs SQLite (`blizzard-infra`'s
`deploy/compose.yaml`), so dogfooding exercises none of them on Postgres. The gap stays open, not permanent: it closes
the day some tier gains a Postgres-backed run, which `packaging/docker/compose.yaml` already makes possible.

## Projects' migration and writes under Postgres

The projects mechanisms below have the same exposure as tenancy's: every tier runs on SQLite, with one writer lock and
foreign keys off, so each holds there by construction and stays unverified on Postgres.

- **The projects revision.** `20261008_1800_projects` (`src/blizzard/hub/store/migrations/versions/`) reaches head and
  returns to base on an empty Postgres store under `blizzard:manual-postgres-migrations`; its backfills over populated
  rows have run on SQLite only. There its eight-table `project_id` addition is a `batch_alter_table` rebuild; on
  Postgres it becomes native `ALTER`s. Its correlated `UPDATE` stamping each row with its tenant's project, and the new
  `fk_<table>_projects` keys, have never run where foreign keys are enforced. Nor has the tenant drain over rows those
  keys bind.
- **The slug move.** A project's slug move (`update_project`, `src/blizzard/hub/store/internal/project_store.py`) runs
  in one transaction. It reads for a current holder of the new slug, deletes the new slug's former-slug row, updates the
  project, then records the slug it left. Under READ COMMITTED each statement reads its own snapshot. What two
  concurrent writes touching one slug leave is unverified: a uniqueness refusal in place of `ProjectSlugTaken`, or a
  former-slug row the other write removed.
- **The project columns revision.** `20261008_1900_project_columns` adds `runner_registrations.projects` and
  `delivery_repo_landed.repository_name` with native `ADD COLUMN`s, and backfills each runner's `projects` as JSON text
  naming its tenant's one project, paged along `runner_id`. Neither the added columns nor the JSON text backfill has run
  on Postgres.
- **The project color revision.** `20261018_1200_project_color` adds `projects.color` as nullable, fills it per tenant
  in keyset pages along `project_id`, then tightens it to `NOT NULL` in a `batch_alter_table`. A hand run on Postgres
  reached head, returned to base, and ran the backfill over populated rows. No tier repeats that run, so a later change
  to the revision is unverified on Postgres until someone runs it again.
- **The work-source identity revision.** The revision giving each work source its `wsrc_<ulid>` id, slug, and name, and
  rekeying every reference to it, has had its backfill run on SQLite only. A work source's slug move takes the project
  slug move's shape, so it shares that move's race under READ COMMITTED, equally unverified.
- **An ingest against a link or unlink.** An ingest takes the `keyed_locks` key of the project it mints into before its
  pointers' keys, and every source link or unlink takes the same project's key (`PROJECT_SOURCE_LINKS_LOCK_NAMESPACE`,
  `src/blizzard/hub/store/internal/project_link_store.py`), so the links an ingest read stand until it commits. That an
  unlink racing an ingest under READ COMMITTED waits on the key rather than committing between the ingest's link read
  and its mint is unverified; SQLite's writer lock serializes the two whatever the key.
- **A landed repository row's keys.** `delivery_repo_landed`'s foreign keys to its chunk and its tenant have never been
  enforced, and its `repository_id` carries neither a unique key nor a foreign key to the repository record: that a
  landing names a repository its project linked is held by the invariant checker's `hub:landed-repository-linked`
  (`src/blizzard/tools/invariants.py`) alone, and its behavior under enforced keys is unverified.
- **The question and decision project revision.** `20261014_0900_question_decision_project` adds `project_id` to
  `questions` and `decisions`, filling each from the row's chunk in bounded keyset pages. It reaches head and returns to
  base under `blizzard:manual-postgres-migrations`; its backfill over populated rows has run on SQLite only. The
  correlated `UPDATE` and the new `fk_questions_projects` and `fk_decisions_projects` keys have never run where foreign
  keys are enforced, and a question or decision written while a chunk's row lock is contended is unverified under
  concurrent writes there.
- **The `?project=` read plans.** Every read a `?project=` narrows has its `EXPLAIN QUERY PLAN` shape asserted on SQLite
  only, so whether Postgres's planner uses the project read indexes for it stays unproven, as
  [§The query-plan assertions never run under postgres](#the-query-plan-assertions-never-run-under-postgres) states for
  every index.
- **The secret-row lock.** Secret retire and every work-source or repository write naming a secret lock that secret's
  row (`lock_secret_row`, `src/blizzard/hub/store/internal/secret_store.py`) before their guard reads. That the lock,
  not the tenant-row lock ahead of it, makes a retire and a referrer's enable exclude each other under READ COMMITTED is
  asserted statically, by the lock statement compiled under the Postgres dialect (`tests/test_secret_row_lock.py`), and
  run on SQLite only, where the writer lock serializes the two whatever the row lock.

Standing in for a tier: the revisions' migration and carry-over tests, the slug-move and link tests on SQLite, and the
portable SQL `bzh:sql-portable` holds each statement to. The gap closes as the tenancy one above does.

## The hosts revision under Postgres

The hosts mechanisms below have the same exposure as projects': every tier runs on SQLite, with one writer lock and
foreign keys off, so each holds there by construction and stays unverified on Postgres.

- **The hosts revision.** `20261012_1000_hosts` (`src/blizzard/hub/store/migrations/versions/`) reaches head and returns
  to base on an empty Postgres store under `blizzard:manual-postgres-migrations`. Its `runner_registrations` change is a
  `batch_alter_table` rebuild on SQLite and native `ALTER`s on Postgres, and the new `fk_runner_registrations_hosts` key
  has never run where foreign keys are enforced. Nor has the tenant drain over rows that key binds.
- **The runner-bindings revision.** `20261012_1100_runner_bindings` chains after the hosts revision and adds nullable
  `runner_registrations.bindings` and `subscription` columns, a `batch_alter_table` rebuild on SQLite and native
  `ALTER`s on Postgres. It reaches head and returns to base under the same `blizzard:manual-postgres-migrations` run;
  that rebuild over a table the `fk_runner_registrations_hosts` key binds has never run where foreign keys are enforced.
- **The host fact lane revision.** `20261013_0900_host_fact_lane` chains after the work-source identity revision and
  creates `host_high_water`, `host_external_usage`, and `host_external_usage_misses`, each tenant-keyed and carrying no
  key on `host_id`. It reaches head and returns to base under the same `blizzard:manual-postgres-migrations` run; the
  upserts that refresh a `(host_id, slug)` row in place have only run under SQLite's writer lock.
- **The runner-version revision.** `20261019_0900_runner_version` chains after the project-color revision and adds
  nullable `runner_registrations` columns for the reported version, the refusal reason, and when it was judged, a
  `batch_alter_table` rebuild on SQLite and native `ALTER`s on Postgres. It reaches head and returns to base under the
  same `blizzard:manual-postgres-migrations` run; that rebuild over a table the `fk_runner_registrations_hosts` key
  binds has never run where foreign keys are enforced.
- **A live host name's uniqueness.** `HostRegistryStore.add` reads the tenant's live host names and inserts under the
  scoped write's tenant-row lock, so two adds of one name queue on that row. That the lock alone keeps a name unique
  among live hosts is unverified on Postgres; SQLite's writer lock serializes every add. A report reads the other live
  names outside any lock and so can record a name an add took in between on either backend.
- **An adoption racing another.** `HostRegistryStore` places a runner with an `UPDATE … WHERE host_id IS NULL` and rolls
  the write back on a runner that matched no row. That two adoptions of one runner under READ COMMITTED leave it under
  exactly one host is unverified; SQLite's writer lock serializes them.

Standing in for a tier: the revision's own test, the adoption and name tests on SQLite, and the portable SQL
`bzh:sql-portable` holds each statement to. The gap closes as the tenancy one above does.

## The runner key revision under Postgres

The runner store runs on SQLite or Postgres by configuration (`bzh:sql-portable`), and every tier runs it on SQLite, so
the runner key holds there by construction. The chain's runner-key revisions and the outbox counter have been executed
by hand on Postgres under `blizzard:manual-postgres-runner-migrations`; what that run could not reach stays unverified:

- **The runner scope revision.** `20261011_1000_runner_scope` (`src/blizzard/runner/store/migrations/versions/`) adds a
  nullable `runner_id` to every runner-scoped table but `runner_identity`, and backfills it from the store's identity
  row in bounded batches. On SQLite each addition is a `batch_alter_table` rebuild; on Postgres it is native `ALTER`s.
  The hand run took a populated store with an identity row down below it and back to head, so its backfill ran, and took
  the chain's downgrades to base.
- **The tightening revision.** `20261013_1000_runner_scope_tighten` stamps any row still lacking a runner, makes
  `runner_id` `NOT NULL`, re-keys the tables and adds the unique constraints. The hand run executed it on Postgres over
  a populated store with more outbound rows than one batch, compared the migrated schema with the one an empty store at
  the parent shape migrates to, ran the invariant checker, and ran the down-and-up round trip, whose downgrade restores
  the parent schema exactly, primary-key names included.
- **The counter allocation.** `insert_outbox_row` (`src/blizzard/runner/store/internal/base.py`) advances a runner's
  lane under READ COMMITTED. Eight threads racing the first allocation of a new runner's lane were issued `1` through
  `8`, with the counter at `8` and the invariants holding.
- **The downgrade's probe check.** A store written past the probe's seq refuses the downgrade, naming the pre-migrate
  backup, and the refusal leaves the schema and the counters unchanged. A store written only up to the probe downgrades,
  and the restored autoincrement issues a seq above the counter's.
- **A sequence gap.** The counter seed probes the outbox's own sequence, and a Postgres sequence burns values, so the
  seed can sit above the highest seq a pending row holds and leave a gap above it. The seed is conservative, and the
  hub's ingest tolerates a gap. It is accepted.
- **The host-ingests revision.** `20261015_1000_host_ingests` creates the empty host-scoped `host_ingests` table and its
  downgrade drops it. It has not been executed on Postgres; it creates one table of portable column types and writes no
  data.
- **The empty-store upgrade.** The runner chain cannot reach head on Postgres from an empty store: the Boolean
  `server_default` in `20260920_0200_usage_cost_is_share.py` is `0`, which Postgres rejects. The hand run builds the
  tightening revision's parent shape from `src/blizzard/runner/store/schema.py` as it stood then, so no revision below
  `20261011_1000_runner_scope` has been upgraded on Postgres; only their downgrades have run. A fix to that revision
  belongs to a change of its own.

Standing in for a tier: the revisions' migration tests
(`src/blizzard/runner/store/migrations/tests/20261011_1000_runner_scope_test.py`,
`20261013_1000_runner_scope_tighten_test.py`, `20261015_1000_host_ingests_test.py`) and the seam's component tests on
SQLite, and the portable SQL `bzh:sql-portable` holds each statement to. The hand run is not repeatable from a durable
script, since the matrix carries the method and no driver. The gap closes as the tenancy one above does.

## What the project lens and the project columns do not cover

Two project boundaries are drawn by no tier because the system does not draw them:

- **The lens is not an access boundary.** The board's project lens narrows what a view reads, and a call naming no
  project reads the whole tenant; access is decided by the tenant alone. Nothing proves a person sees only a project's
  records, because nothing restricts them to one — a stated non-goal, not a missing check.
