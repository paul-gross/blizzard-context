# Documented gaps — what no tier proves (`bzh:matrix-gaps`)

Surfaces the matrix deliberately leaves uncovered, each with the evidence that stands in for a tier and the reason a
tier cannot reach it. Each is a documented gap, not an invitation to invent a tier around it.

- **Real-forge worker-push is covered by dogfooding, not CI (issue #143, R6).** Since Phase 4 the worker — not the
  runner — pushes its branch before declaring it (`blizzard runner artifact commit`); CI's `blizzard:e2e` and
  `blizzard:crash-sweep` rows only ever exercise that push against the `file://` mock origins the fixture workspace
  mints, never a real forge. A push failure specific to a real remote (auth, a real GitHub branch-protection rule,
  network) is therefore a gap no CI tier closes — it is exercised only by the dogfood deployment
  (`workspace:/context/project/local-instance.md`), whose build transcripts already show the worker pushing to real
  GitHub. A documented gap, not invented around: do not add a real-forge CI tier to close it.
- **Harness session stickiness is covered by evidence, not by a tier (issue #144).** The mint-only model contract — a
  session's model applied where the session is minted and on no resume after it — rests on the harness *restoring* a
  resumed session's own model. No tier asserts the **effective** model a harness ran under: the mock façade sees argv
  and nothing else, so `blizzard:e2e`'s named assertion in `test_session_modes_e2e.py`'s
  `test_a_named_pool_threads_one_session_across_nodes_and_applies_model_at_mint_only` asserts the **flag** (mint carries
  a model, resumes carry none) and stops there. What backs the underlying claim is a one-time empirical observation of
  Claude Code CLI 2.1.220 plus source reads of opencode 1.18.8 and codex, recorded in the issue. A stickiness regression
  in a future CLI would therefore run a whole mechanical lineage on the wrong model with every tier green — and each
  harness additionally has a *configuration* that defeats stickiness (`ANTHROPIC_MODEL` env, an opencode agent model
  pin, a codex `config.toml` model), which is why `docs/deployment/worker-spawn.md` states them as deployment
  requirements. A documented gap, not invented around: do not add a real-token tier to close it. The companion finding
  is that **effort is not sticky** in the same CLI — measured, not assumed — which is why effort is reasserted on every
  invocation while model is not.
- **Compaction is covered by evidence, not by a tier (blizzard#343).** The declared window travels to the harness as a
  per-invocation flag (`--autocompact`, reasserted like effort, never sticky-by-omission), but whether it actually
  compacts a session's context near that value is *effective* harness behavior no CI tier can see: the mock façade sees
  argv and nothing else, so the mock-visible tiers (`blizzard:unit-test`'s command-list pins,
  `blizzard:component-test`'s wire/stamp round-trip) prove only that the flag is built and threaded, never that it does
  anything. Closing that gap is `blizzard:manual-autocompact-window`, the same shape as
  [`blizzard:manual-external-usage-probe`](./manual.md): a live procedure, not a placeholder for a future tier — the
  thing it proves (an external harness's live compaction behavior) is structurally outside a hermetic, network-free CI
  tier's reach.
- **Sidechain and thinking-turn *normalization* is proven only against hand-authored fixtures (blizzard#245).** Pinned
  at `blizzard:unit-test` and by the component-tier projection golden tests, both fed by the same hand-authored record
  fixtures; `blizzard-mock`'s `ClaudeTranscriptWriter`
  (`blizzard-mock/src/blizzard_mock/harness/facades/_transcript.py`) deliberately mints none of the shapes involved, so
  no mock-driven `blizzard:service-test` or `blizzard:e2e` tier exercises the *normalizer* against them, and each could
  in principle drift from a future Claude Code CLI with every one of those tiers still green.
  `test_transcript_tab_browser_e2e` (blizzard#248) does not close this gap: it proves the board's *rendering* of
  thinking turns and both sidechain shapes end to end, but seeds them as hand-authored `TurnSegmentView` JSON posted
  straight to `POST /api/fleet/transcripts`, so no normalizer output ever reaches it. The forward-read lane's own
  consumer is `turns_since(since=<position>)` called through the transcript outbound lane's pump (issue #246) —
  `TranscriptPump` (`blizzard/src/blizzard/runner/loop/transcript_pump.py`) calls it every tick per open segment and
  carries the returned `next_position` forward as the next call's `since`. What `blizzard:component-test`
  (`tests/test_transcript_pump.py`) actually proves is narrower than that sounds: it binds a scriptable
  `FakeTranscriptSource` (`blizzard/tests/runner_fakes.py`) that returns canned batches by session id, never calling
  `Position.of`, `FileRead.forward`, or the past-EOF clamp — so the test proves the pump's own cursor-carry *plumbing*
  (it hands the fake's opaque token back on the next call), not the position codec, the shared batch budget, or the
  past-EOF clamps inside `ClaudeCodeTranscriptSource.turns_since` itself — those three are pinned at no tier at all.
  `blizzard:service-test`'s
  `tests/service/test_runner_service.py::test_transcript_route_failure_never_blocks_the_fact_lane` proves the two lanes'
  independence (a wedged transcript route buffers rather than blocking the fact lane, and drains clean on recovery), but
  its only transcript-lane assertions are a buffer-depth threshold satisfied by `record_closure`'s own-segment final
  marker alone; it witnesses no delta content, cursor, or carry-forward, so it proves lane independence, not this claim.
  The panel's `read_turns` (`blizzard/src/blizzard/runner/transcripts/internal/projected_transcript_repository.py`), by
  contrast, still calls `turns_since(..., since=None)` exactly once per read and never loops on the position it mints —
  that read path's own carry-forward remains unexercised. Dogfooding exercises neither by default: the lane ships
  disabled (`[transcripts] ship = false`) even with the hub-side segment store now landed — turning it on is a separate
  rollout decision. **`blizzard runner transcript backfill` and `blizzard runner transcript reship` (blizzard#250) are
  the lane's second and third consumers, and the heaviest exercise of exactly the three unpinned pieces above.** Both
  call the same `TranscriptPump.drain_segment` with `deadline=None` against a *complete historical file from offset 0*,
  looping until the source reports it caught up — so a real run drives the position codec, the shared batch budget, and
  the past-EOF clamps harder than the tick's per-segment window ever does. Its own `blizzard:component-test`
  (`tests/test_transcript_backfill.py`) inherits the same `FakeTranscriptSource` limitation as the pump's, so it proves
  the backfill's classification, dedupe, resume, and finalize-only-when-caught-up decisions — not those three pieces
  either. The verb is also the first path that *requires* `ship = true` (it refuses otherwise), so running it against a
  real `~/.claude/projects` is the "turn it on" event this bullet says has not happened; an operator who runs it has
  exercised the forward-read lane for real, and that run is evidence no tier here records. Exactly which shapes, and
  why, is stated once — `src/blizzard_mock/harness/README.md` §"Conversation transcripts", not restated here. A
  documented gap, not invented around: do not add a real-corpus CI tier reading a developer's `~/.claude/projects`
  (neither hermetic nor reproducible) to close it.
- **Operator-doc control-flow accuracy is a documented gap, not a method (`bzh:operator-doc-claims-unverified`, issue
  #279).** `docs/` states reachability, precondition, and failure claims about daemon behavior, and nothing mechanical
  can judge whether one is *true*: `blizzard:restatement-sweep` checks a fact has one home rather than that it is
  correct, and `blizzard-context:registry-drift` proves agreement, never adequacy. Two hand-walks in a row have found
  inverted or invented claims (a `kill -9` described as costing in-flight agent context when the daemon re-attaches it;
  a runner-scoped ceiling described as raising a chunk escalation; adapters named that are not in the tree). Until a
  method exists, a change to daemon control flow owes a walk of the `docs/` claims it touches — trace each precondition
  to its guard, each reachability claim to its dispatch site, each failure claim to its raising path — and a claim a fix
  commit *writes* owes the same walk as one it edits. A documented gap, not invented around: do not add a doc-linting
  tier that would score prose without reading the code.
- **Per-block prose caps are enforced by hand, not by the ratchet (`bzh:prose-budget`).** `mise run prose-check` gates
  each root's prose *total* against the committed baseline; the per-block caps are reported only under `--blocks`, and
  nothing runs that automatically. The two measures are independent — a change can hold every total and still carry an
  over-cap block, and a baseline re-record absorbs the total while leaving the block standing. Gating `--blocks`
  repo-wide is not the fix: it scopes to every block in the tree rather than the ones a change wrote, so it fails on
  prose the change never touched and stops being read. Until a method that scopes to a diff exists, a change owes a
  `--blocks` run and a check that no block it added or edited is over cap, and a re-record is warranted only once that
  holds.
