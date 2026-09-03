<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Garden-routine e2e scenarios (`bzh:e2e-garden`)

The scenarios for the packaged `garden-routine` graph — the garden pass blizzard's routines run: survey → reconcile →
propose → a hub-executed delivery that ends in findings and proposals rather than commits.

The module needs the sibling provisioned `blizzard-mock` worktree plus a local winter source, and skips without
`BLIZZARD_E2E=1`.

## test_garden_routine_e2e

The real packaged `garden-routine` YAML with only its prompts swapped for scripts — name, nodes, edges, session pools,
and the `garden_deliver` command all reach the mint verbatim — run as a real routine (`POST /routines/{id}/run`) against
a live hub, one chunk per authored path.

- `test_garden_routine_runs_end_to_end_on_all_six_paths` — seven runs of one routine: `found` mints the survey's
  candidates as findings through reconcile's delta; `clean` routes survey straight to deliver and records the empty
  delta's measurement and revisions (asserted in the hub's `finding_sets`); `excessive` runs twice, the second bail-out
  converging as an `observed` on the finding already live — still exactly one `excessive-scope` row — before the
  hand-out proposal cites it; `invalid` has delivery reject an unknown `fin_` id, write the `garden-delivery-failure`
  artifact, and bounce to reconcile, where the corrected delta exists only if the `invalid` edge's `prompt_addendum`
  actually threaded into re-entry; `virgin` runs against a scope this routine has never touched, where reconcile's own
  `add` ops carry the survey candidates' submission-local refs and propose's docket cites those refs rather than any
  live id — the delivered proposal's `findings` resolve to exactly the `fin_` ids this same delivery minted, proving a
  run can answer the findings it just opened; and `no-strategy` mirrors `excessive`'s bail-out shape for an axis the
  target's gardening-axes registry declares no entry for — survey's whole output is one `undeclared-axis` candidate, and
  the run still delivers with that gap landing as the finding. After `found` delivers, `GET /api/runs` reports its row
  (routine, scope, mode, `done` outcome, and the delivered finding-set it published) and `GET /api/runs/{chunk_id}`
  reads its delta back as the two `stale-docstring` findings, an `added` group with empty `observed`/`gone`. Session
  policy is asserted off the runner's own store: reconcile never shares survey's session, propose resumes the match head
  its reconcile minted, and the bounced re-entry mints a fresh one.
