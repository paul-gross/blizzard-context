# e2e scenarios — node sessions (`bzh:e2e-sessions`)

<!-- one `##` section per `tests/e2e/` module, its bullets naming that module's test functions — machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s check C. -->

The scenarios that prove what a node's session carries across an entry: which session a node resumes, and what a resumed
spawn re-sends.

## test_session_modes_e2e

**Node session modes** (#115): a `build → review → build` fail-cycle whose `build` node carries `session: resume:build`
(the packaged default's own setting) and `review` is `session: fresh`.

- `test_session_modes_resume_targeted_and_fresh_across_a_cycle` — after the chunk lands, the scenario reopens the runner
  store to map each node-step lease's `session_id` and reads the mock harness's persisted per-session `turns`
  (`<workspace>/.blizzard-mock-harness/sessions/<sid>.json`), proving: the two `build` leases share **one** session id
  whose turns grew past a single visit (spawn + judgement resume) — the re-entry **resumed build's own session in
  place**, not re-spawned (a regression dropping `resume:build`, or failing to thread `session_source` through the
  store→envelope, re-spawns fresh and yields two distinct build ids — the assertion's negative case, verified by hand);
  the two `fresh` review visits carry **two distinct** session ids disjoint from build's; first arrival at build spawned
  fresh (the chunk's first lease can resume nothing); and `latest_session_id(chunk, None)` (what bare `resume` would
  inherit) is a **review** session, not build's — the concrete reason the targeted form exists (plan Q4). It drives the
  loop in-process one tick at a time like the other in-process scenarios — no browser — so it needs the sibling
  `blizzard-mock` worktree + a local winter source and runs in the tag `release` full e2e tier, skipped without
  `BLIZZARD_E2E=1`.
- `test_a_named_pool_threads_one_session_across_nodes_and_applies_model_at_mint_only` — a named pool: `build` carries
  `fresh:code` and mints a session on each entry, `review` carries `resume:code` and continues the head `build` just
  minted — a pairing no `resume:<node>` form expresses — and the mint-only model contract holds off the mock's own
  recorded argv: every mint carries the resolved model, no resume does.

## test_resume_preamble_e2e

**Resume-time spawn-preamble elision** (#149), over `test_session_modes_e2e`'s `build → review → build` fail-cycle shape
(the one that enters `build` twice on **one** session). It reads what the harness process *actually received*: the mock
records each turn's user text into a Claude-Code-shaped transcript (`<root>/mock-claude-code/<sid>.jsonl`), and for an
untagged prompt that text is the runner's preamble verbatim — so one session's transcript is the ordered record of what
each of its turns was sent, and the facts-table header discriminates a spawn turn from a resume-with-message turn. This
is the only tier that sees the preamble a **real** harness process received across a **real** `--resume`: the component
tier asserts the `prompt_prefix` the loop hands a *fake* adapter, which proves the wiring but not the delivery. Both
functions were verified to fail under mutation — disabling the elision fails both, and freezing layer 2's digest fails
only the announcement one — so neither passes vacuously. The standing layers are deliberately padded to realistic size:
the collapse banner is real prose (~450 chars), so against one-line prompts the elision is *not* a saving, and asserting
one would assert something false. Like the other non-browser scenarios it needs the sibling `blizzard-mock` worktree + a
local winter source, skipping without `BLIZZARD_E2E=1`.

- `test_resumed_node_entry_elides_unchanged_standing_layers` — **the efficiency half**: with both standing layers set
  and unchanged between the two entries, the resumed node-entry spawn collapses them to a single line, re-sends neither,
  announces nothing, and still carries its own freshly minted lease id with the previous attempt's absent.
- `test_resumed_node_entry_announces_a_replaced_workspace_prompt` — **the correctness half**: an operator replaces the
  workspace prompt through the live `PUT /api/workspace-prompt` door *between* the two entries, and the second spawn
  leads with the updated-since-your-previous-turn announcement, carries the new prose, drops the superseded prose, and
  keeps layer 1 collapsed.
