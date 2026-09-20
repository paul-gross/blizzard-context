# Surfaces no tier reaches (`bzh:matrix-gaps`)

The matrix leaves the surfaces below uncovered on purpose. Each entry names the evidence standing in for a tier and why
a tier cannot reach it; each is a documented gap, not an invitation to invent a tier around it. A surface's
unreachability by any tier is re-tested each time a gap is entered here and never inherited by analogy from a sibling
gap, because tooling that lands later can automate part of what was manual and leave a narrower residue than the
original claim assumed.

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

The mint-only model contract — a session's model applied where the session is minted and on no resume after it — rests
on the harness restoring a resumed session's own model. The live OpenCode compatibility diagnostic now checks that the
requested provider/model and variant survive fresh and resumed exports, but it deliberately supplies them on every
invocation and therefore does not assert effective model stickiness when they are omitted. No tier asserts the effective
context accounting a harness ran under, because the mock façade sees argv and nothing else. `blizzard:e2e`'s
`test_session_modes_e2e.py::test_a_named_pool_threads_one_session_across_nodes_and_applies_model_at_mint_only` asserts
the flag — mint carries a model, resumes carry none — and stops there.

Standing in for a tier: what backs the surrounding export behavior is a one-time empirical observation of Claude Code
CLI 2.1.220 and the retained live OpenCode `1.18.25` compatibility evidence. Neither observation proves OpenCode session
stickiness when model flags are omitted; each harness also has a configuration that can defeat stickiness, which
`docs/deployment/worker-spawn.md` states as deployment requirements. Do not add a real-token tier to close this gap.

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
runner's admitted-version corpus directories (today just
`blizzard/src/blizzard/runner/harness/contracts/opencode/1.18.25/`) carries it — the admitted version's live runs never
compacted. A wrong spelling parses as absent, so the fallback silently stops firing rather than failing.

Standing in for a tier: the physical-removal path, which every retained fixture does exercise, is the primary evidence
for `transcript_cursor`; the tail-marker fallback is unverified until a live run compacts and the shape is captured.
Re-run `blizzard:manual-opencode-compatibility` long enough to force a compaction before treating the fallback as
proven, and do not add a tier that would assert a hand-authored spelling against itself.

## OpenCode transcript reads never distinguish `not_found`

`IHarnessTranscriptSource.turns_since`'s `TranscriptReadReason` names `not_found` and `unreadable` as distinct outcomes,
but `opencode export <session-id>` gives no confirmed signal separating "no such session" from any other export failure
— the compatibility probe's own `_export_session` (`opencode_probe.py`) does not distinguish them either, always folding
a non-zero exit into one generic error string. `OpenCodeTranscriptSource` therefore reports every export failure as
`unreadable`, never `not_found`, until a live run's exit code or stderr shape is captured and confirmed.

Standing in for a tier: `blizzard:unit-test` covers the chosen `unreadable` default against every failure shape this
parser can name; a live `opencode export` against a genuinely absent session id would be the evidence for a narrower
`not_found` path, and does not exist yet. Do not add a stderr-string match invented rather than captured from a run.

## OpenCode's analytics dialect has no proven read/skill tool-name mapping

`dialects.py`'s `_OPENCODE_EXPORT_1` registers only `KIND_AGENT_SPAWN` (`tool_name="task"`), fixture-proven off the
admitted-version corpus; its own comment says plainly that a read or a skill invocation "have no proven tool name yet" —
unlike `_CLAUDE_CODE_JSONL_2`, which maps all three kinds. Nothing stands in for the missing two: inventing a
`tool_name`/`argument_key` pair for either would be guessing at OpenCode's real tool vocabulary rather than reading it
off a captured run, exactly the shape "OpenCode transcript reads never distinguish `not_found`" above already refuses.
`blizzard:service-test`'s mixed-harness dispatch gate (`test_mixed_harness_dispatch_service.py`) deliberately exercises
only the one proven `agent-spawn` kind for this reason and does not close this gap.

Standing in for a tier: a live OpenCode run whose transcript actually reads a file or invokes a skill, captured into the
admitted-version corpus (`blizzard/src/blizzard/runner/harness/contracts/opencode/1.18.25/`) the same way the spawn
mapping itself was proven, is the only evidence that would extend `_OPENCODE_EXPORT_1` correctly. Do not add a mock- or
unit-invented tool name to close this — a mock's own vocabulary is authored, not observed, and would prove nothing about
what OpenCode actually calls its tools.

## The worker deny list

`WorkerSettings.document`'s `permissions.deny` list travels to the harness as a JSON settings file on every worker
invocation path. The mock-visible tiers — `blizzard:unit-test`'s exact-list pin and `blizzard:component-test`'s
prefix-parity check — prove only that the file is built and threaded, never that `claude -p` itself honors a
`permissions.deny` entry.

Standing in for a tier: `blizzard:manual-worker-deny-list` closes this as a live procedure, the same shape as
[`blizzard:manual-autocompact-window`](./manual.md#blizzardmanual-autocompact-window) — an external harness's live
permission enforcement sits outside a hermetic, network-free CI tier's reach.

## Claude Code transcript normalization

`blizzard-mock`'s `ClaudeTranscriptWriter` (`blizzard-mock/src/blizzard_mock/harness/facades/_transcript.py`)
deliberately mints none of the shapes involved, so no mock-driven `blizzard:service-test` or `blizzard:e2e` exercises
the normalizer, which could drift from a future Claude Code CLI with every tier green. `test_transcript_tab_browser_e2e`
does not close it either: it seeds hand-authored `TurnSegmentView` JSON straight to `POST /api/fleet/transcripts`, so no
normalizer output ever reaches it. OpenCode's own `opencode_normalizer` is a separate code path this gap does not reach
either way — it is exercised by `blizzard-mock`'s `OpenCodeTranscriptWriter` through a real mock-driven
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
`ix_usage_facts_recorded_at` the same way. `tests/test_store_read_index_gate.py`'s scan gate and
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
declared methods reach the mechanical half only — `blizzard:unit-test`'s packaged-prompt byte bars
(`blizzard/tests/test_prompt_byte_bars.py`) and its `blizzard hub` verb guard, `blizzard:component-test`'s graph mint
and choice-edge resolution, and `blizzard:e2e`'s `test_garden_routine_runs_end_to_end_on_all_six_paths`, whose scripted
node bodies deliberately exercise no model at all. That `survey` actually resolves its axis from the target's registry
rather than improvising a yardstick, or that `propose` actually cites the refs its own run just minted, is asserted by
nothing: a prompt is an input to a model no tier runs.

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

The same residue now also covers `adv-dwf`'s `build.from-deliver.md`, `bas-dwf`'s `build.from-deliver.md`, and
`bas-hwf`'s `iterate.from-deliver.md` — the `deliver` → repair-node addenda a base-inherited CI failure routes through
on every lane — and each lane's `pre-push.md` rebase-to-empty qualifier. `land_pr_ci`'s own classification is proven by
`blizzard:unit-test`'s scripted-forge cases and `tests/test_graph_authoring.py`'s per-lane edge/addendum pins; that a
worker reads the addendum's repair charge correctly, or applies the loop bound's chunk-history check rather than
repeating the repair a second time, is not.

Standing in for a tier: a live chunk run through each lane on the dogfood deployment
(`workspace:/context/project/local-instance.md`), whose transitions, bounces, and retrospective are read back and judged
against the routing these prompts intend. That evidence is only producible once the landed graph directory is re-minted,
so this entry records a standing obligation on the lanes' wording rather than a phase gate. Do not answer this with a
tier that scores prompt prose against a rubric.

## The cross-repo OpenCode lever roster

`blizzard-mock`'s `opencode_surface.levers.Lever`/`CATALOG` and `blizzard`'s `tests/service/support.py::_fake_binary`
kwarg roster are two independently maintained 1:1 mirrors of the same 26-member misbehaviour vocabulary — `_fake_binary`
claims its mapping is exhaustive against the `Lever` enum, but `blizzard` deliberately holds no dependency on
`blizzard-mock` (`tests/support.py::github_double`'s established stance), so nothing mechanical can diff the two
rosters. A member added on one side with no matching update on the other drifts silently: a new `blizzard-mock` lever
goes untested by `blizzard`'s diagnostic cases, or a stale `blizzard` kwarg targets a retired lever name and fails
loudly only when `mock-opencode emit` rejects it at runtime.

Standing in for a tier: `_fake_binary`'s own `assert len(lever_flags) == 26` pins the count as a trip-wire, and
`bzh:opencode-lever-roster-extends-both-sides` in [`./companion-changes.md`](./companion-changes.md) obligates a roster
change to land both sides in the same commit family. Neither closes the gap mechanically — the count can stay 26 while a
name silently swaps — so a roster change's correctness rests on the author following the companion-changes rule, not on
a tier that would need the cross-repo import `tests/support.py::github_double`'s established stance forbids.
