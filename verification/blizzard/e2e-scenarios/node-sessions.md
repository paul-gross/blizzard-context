<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Node-sessions e2e scenarios (`bzh:e2e-node-sessions`)

What a node's session carries across an entry: which session a node resumes, and what a resumed spawn re-sends.

Both modules run in-process, one tick at a time, with no browser; each needs the sibling provisioned `blizzard-mock`
worktree plus a local winter source, skips without `BLIZZARD_E2E=1`, and runs in the tag `release` workflow's full e2e
tier.

The mock records each turn's user text into a Claude-Code-shaped transcript at `<root>/mock-claude-code/<sid>.jsonl` —
an untagged prompt's text being the runner's preamble verbatim — so a session's transcript is the ordered record of what
each turn was sent, its facts-table header discriminating a spawn turn from a resume-with-message turn.

## test_session_modes_e2e

Node session modes over a `build → review → build` fail-cycle whose `build` node carries `session: resume:build` — the
packaged default's own setting — and whose `review` node is `session: fresh`.

- `test_session_modes_resume_targeted_and_fresh_across_a_cycle` — reopens the runner store after the chunk lands to map
  each node-step lease's `session_id`, and reads the mock harness's persisted per-session `turns` at
  `<workspace>/.blizzard-mock-harness/sessions/<sid>.json`. It proves the two `build` leases share one session id whose
  turns grew past a single visit (spawn plus judgement resume) — the re-entry resumed build's own session in place
  rather than re-spawning, where a regression dropping `resume:build` or failing to thread `session_source` from store
  to envelope yields two distinct build ids (that negative case was verified by hand). It also proves the two `fresh`
  review visits carry two distinct session ids disjoint from build's, first arrival at build spawned fresh, and
  `latest_session_id(chunk, None)` — what bare `resume` would inherit — is a review session, not build's: the concrete
  reason the targeted `resume:<node>` form exists.
- `test_a_named_pool_threads_one_session_across_nodes_and_applies_model_at_mint_only` — proves a named pool — `build`
  carries `fresh:code`, minting a session per entry; `review` carries `resume:code`, continuing the head `build` just
  minted, a pairing no `resume:<node>` form expresses — and proves off the mock's recorded argv that every mint carries
  the resolved model and no resume does.

## test_resume_preamble_e2e

Resume-time spawn-preamble elision over the same fail-cycle shape, the one entering `build` twice on one session. This
is the only tier seeing the preamble a real harness process received across a real `--resume`; the component tier
asserts the `prompt_prefix` handed a fake adapter, proving wiring but not delivery. The standing layers are padded to
realistic size (the collapse banner is ~450 chars of real prose), so against one-line prompts the elision is not a
saving and none is asserted. Both functions fail under mutation — disabling the elision fails both, freezing layer 2's
digest fails only the announcement one — so neither passes vacuously.

- `test_resumed_node_entry_announces_a_replaced_workspace_prompt` — the correctness half: an operator replaces the
  workspace prompt through the live `PUT /api/workspace-prompt` door between the two entries, and the second spawn leads
  with the updated-since-your-previous-turn announcement, carries the new prose, drops the superseded prose, and keeps
  layer 1 collapsed.
- `test_resumed_node_entry_elides_unchanged_standing_layers` — the efficiency half: with both standing layers unchanged
  between the two entries, the resumed spawn collapses them to a single line, re-sends neither, announces nothing, and
  still carries its own freshly minted lease id with the previous attempt's absent.
