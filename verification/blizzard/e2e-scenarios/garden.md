<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Garden e2e scenarios (`bzh:e2e-garden`)

The scenarios for blizzard's packaged garden graphs — `garden-routine`'s survey → reconcile → propose → a hub-executed
delivery that ends in findings and proposals rather than commits, and `ideation`'s parallel survey → reconcile → propose
→ deliver, which judges a target against its own charter rather than a standard and proposes ideas in three graph-owned
classes (`direction`/`tweak`/`retire`) rather than findings-driven fixes.

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

## test_ideation_e2e

The real packaged `ideation` YAML with only its prompts swapped for scripts — name, nodes, edges, session pools, and the
delivery command all reach the mint verbatim — run as a real routine (`POST /routines/{id}/run`) against a live hub
minted with a gardening-axes registry declaring an `ideation:` axis, one chunk per authored path.

- `test_ideation_runs_end_to_end_on_all_authored_paths` — eight runs of one routine: the declared-axis path carries
  survey → reconcile → propose → deliver to a docket of proposals spanning all three graph-owned classes (`direction`,
  `tweak`, `retire`), every proposal's `findings` empty, and the delivered finding set records the measurement with no
  revisions and no finding rows (asserted in the hub's `finding_sets`); the operator then closes two of the delivered
  proposals — one accepted without minting a work item, one passed with a reason — before a second run's reconcile reads
  that passed proposal and its reason back through `garden proposals --state all` and drops the matching candidate,
  routing straight to deliver without ever reaching propose; the empty-survey path delivers the skeleton delta with no
  candidates at all; the undeclared-axis path has survey itself park the chunk on `waiting_on_human` with a
  `blizzard runner ask` question naming the missing axis, and once a human answers it the chunk reaches `done` with no
  finding set and no proposals — the reserved terminal, never a delivery; propose's own decline path delivers the
  skeleton with no proposals attached; the invalid path has delivery reject the docket and bounce to propose rather than
  reconcile — the opposite of `garden-routine`'s `invalid`, which returns to reconcile — where the corrected docket
  delivers only if the `invalid` edge's `prompt_addendum` actually threaded into re-entry; the failure path has delivery
  crash, bounce to propose, which republishes the same docket unchanged, and the retry delivers it; and a second
  consecutive `invalid` or `failure` at deliver escalates via `blizzard runner
  ask` rather than retrying a third time.
  Session policy is asserted off the runner's own store: reconcile never shares survey's session, and propose resumes
  reconcile's.
