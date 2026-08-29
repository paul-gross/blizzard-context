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

## Session stickiness and the effective model

The mint-only model contract — a session's model applied where the session is minted and on no resume after it — rests
on the harness restoring a resumed session's own model. No tier asserts the effective model or the effective context
accounting a harness ran under, because the mock façade sees argv and nothing else. `blizzard:e2e`'s
`test_session_modes_e2e.py::test_a_named_pool_threads_one_session_across_nodes_and_applies_model_at_mint_only` asserts
the flag — mint carries a model, resumes carry none — and stops there.

Standing in for a tier: what backs the stickiness claim is a one-time empirical observation of Claude Code CLI 2.1.220
plus source reads of opencode 1.18.8 and codex. Each harness also has a configuration that defeats stickiness, which
`docs/deployment/worker-spawn.md` states as deployment requirements. Do not add a real-token tier to close this gap.

## The declared compaction window

The declared compaction window travels to the harness as the per-invocation `--autocompact` flag, reasserted on every
invocation and never sticky by omission. The mock-visible tiers — `blizzard:unit-test`'s command-list pins and
`blizzard:component-test`'s wire/stamp round-trip — prove only that the flag is built and threaded, never that it
compacts anything.

Standing in for a tier: `blizzard:manual-autocompact-window` closes this as a live procedure, the same shape as
[`blizzard:manual-external-usage-probe`](./manual.md#blizzardmanual-external-usage-probe) — an external harness's live
compaction behavior sits outside a hermetic, network-free CI tier's reach.

## The worker deny list

`WorkerSettings.document`'s `permissions.deny` list travels to the harness as a JSON settings file on every worker
invocation path. The mock-visible tiers — `blizzard:unit-test`'s exact-list pin and `blizzard:component-test`'s
prefix-parity check — prove only that the file is built and threaded, never that `claude -p` itself honors a
`permissions.deny` entry.

Standing in for a tier: `blizzard:manual-worker-deny-list` closes this as a live procedure, the same shape as
[`blizzard:manual-autocompact-window`](./manual.md#blizzardmanual-autocompact-window) — an external harness's live
permission enforcement sits outside a hermetic, network-free CI tier's reach.

## Transcript normalization

`blizzard-mock`'s `ClaudeTranscriptWriter` (`blizzard-mock/src/blizzard_mock/harness/facades/_transcript.py`)
deliberately mints none of the shapes involved, so no mock-driven `blizzard:service-test` or `blizzard:e2e` exercises
the normalizer, which could drift from a future Claude Code CLI with every tier green. `test_transcript_tab_browser_e2e`
does not close it either: it seeds hand-authored `TurnSegmentView` JSON straight to `POST /api/fleet/transcripts`, so no
normalizer output ever reaches it.

Standing in for a tier: sidechain and thinking-turn normalization is proven only against hand-authored fixtures, pinned
at `blizzard:unit-test` and by the component-tier projection golden tests, both fed by the same record fixtures — which
transcript shapes are involved, and why, is owned by `blizzard-mock`'s `src/blizzard_mock/harness/README.md`
§"Conversation transcripts". Do not add a real-corpus CI tier reading a developer's `~/.claude/projects`, which is
neither hermetic nor reproducible.

## The transcript source's position codec, batch budget, and EOF clamps

The position codec, the shared batch budget, and the past-EOF clamps inside `ClaudeCodeTranscriptSource.turns_since` are
pinned at no tier at all. Every component-tier test of the transcript lane binds a scriptable `FakeTranscriptSource`
(`blizzard/tests/runner_fakes.py`), so `tests/test_transcript_pump.py` and `tests/test_transcript_backfill.py` reach the
pump's and the backfill's own decisions and never those three pieces.

Standing in for a tier: `blizzard runner transcript reship` and `blizzard runner transcript backfill` drive
`TranscriptPump.drain_segment` with `deadline=None` over a complete historical file from offset 0 until the source
catches up, exercising the three unpinned pieces harder than a tick ever does. The backfill verb is the first path that
requires `ship = true`, so an operator running it against a real `~/.claude/projects` produces evidence of the
forward-read lane that no tier records — which dogfooding does not supply by default, since the transcript lane ships
disabled (`[transcripts] ship = false`).

## The finding table's postgres query plan

`tests/test_finding_store.py`'s `test_list_for_query_plans_as_an_index_search` and
`test_count_by_class_query_plans_as_an_index_search` (blizzard#390) assert `EXPLAIN QUERY PLAN` on sqlite — the backend
every component test runs against — that `list_for`'s routine+scope read and `count_by_class`'s routine+class read use
`ix_findings_routine_scope`/`ix_findings_routine_class` rather than a table scan.
`tests/test_chunk_fact_table_indexes.py` (blizzard#421) asserts the same shape over the twenty-one `chunk_id`-filtered
fact tables the `20260829_1930_fact_tables_chunk_id_index` revision indexes. No tier runs either assertion against
postgres, so whether the portable index declarations actually earn an index scan under postgres's own planner stays
unproven.

Standing in for a tier: every index declaration here is `bzh:sql-portable` — ordinary SQLAlchemy `Index()` DDL, not a
sqlite-specific construct — so a postgres planner choosing a table scan over one would be a planner-statistics anomaly
(e.g. an empty table) rather than a declaration defect. Do not add a postgres-backed component tier to close this; the
dogfood deployment's postgres store is the evidence a real-scale table would surface a genuine regression against.

## The worker's push to a real forge

The worker, not the runner, pushes its branch before declaring it (`blizzard runner artifact commit`), and
`blizzard:e2e` and `blizzard:crash-sweep` only ever exercise that push against the `file://` mock origins the fixture
workspace mints, never against a real forge.

Standing in for a tier: a push failure specific to a real remote — auth, a GitHub branch-protection rule, network — is
exercised by the dogfood deployment (`workspace:/context/project/local-instance.md`), whose build transcripts show the
worker pushing to real GitHub. Do not add a real-forge CI tier.
