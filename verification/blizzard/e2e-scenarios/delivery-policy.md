# e2e scenarios — delivery policy and the forge (`bzh:e2e-delivery-policy`)

<!-- one `##` section per `tests/e2e/` module, its bullets naming that module's test functions — machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s check C. -->

The scenarios that prove what `deliver` does when the forge answers with a red check, a conflict, or a pending CI run —
and the label projection that reports a chunk's state back to it.

## test_checks_gate_e2e

**Checks-gate enforcement** (#114): a graph whose `build` choice carries `requires_checks: true` proves the checks gate
— not the worker's own judged choice — decides whether a red check bounces the attempt back to `build` and re-queues it,
landing once the check goes green; a companion graph instead routes its failing check through a non-gated `fail` choice,
proving that path is an ordinary judged transition and the gate never fires. Its component-tier companion,
`test_checks_gate_agreement.py`, proves the runner's local gate and the hub's completion backstop reach the same verdict
over a decision matrix; this module proves the resulting predicate end to end against the real forge + hub + runner
instead. Reuses `test_acceptance_loop`'s live-stack scaffolding, skipping without `BLIZZARD_E2E=1` or a provisioned
sibling `blizzard-mock` worktree + local winter source; no browser.

- `test_checks_gate_bounces_a_red_pass_then_lands_when_green` — the gated `pass` choice is bounced while its check is
  red, build runs again, and it lands once the check is green (AC 4).
- `test_a_red_check_through_a_non_gated_fail_routes_normally` — a red check reported through the ungated `fail` choice
  routes back to `build` as an ordinary judged transition, the gate never firing, and the green re-entry lands (AC 5).

## test_delivery_conflict_e2e

**A delivery conflict at the default graph's `deliver` node lands zero repos** (#67): with the mock forge's
`merge_conflict` lever armed, the PR the build node opened is not cleanly mergeable — nothing lands, the bounce routes
back to `build` (#64), and the route is kept. Needs the sibling `blizzard-mock` worktree + a local winter source,
skipping without `BLIZZARD_E2E=1`; no browser.

- `test_conflict_lands_zero_repos_and_routes_the_bounce_envelope_back_to_build` — the chunk's route holds at `build`
  with a `bounce-envelope` artifact recorded and its cause set to `conflict`, the conflicted PR stays open and unmerged
  at the forge, and bare `main` never moves.

## test_delivery_pr_ci_e2e

**Delivery policy lives in YAML, not code** (#67): its graph differs from the default only in `deliver`'s `run:` script
and poll cadence, naming the same `land_pr_ci` script and choice names the shipped graph authors, yet drives every route
below through the same generic `executor: hub` primitive. Needs the sibling `blizzard-mock` worktree + a local winter
source, skipping without `BLIZZARD_E2E=1`; no browser.

- `test_pr_ci_pends_on_blocked_then_lands_when_green` — a blocked PR pends over several polls with exactly one
  unchanging `delivery-findings` artifact, then lands once the required check goes green.
- `test_pr_ci_routes_failure_on_a_terminally_failed_check` — a terminally failed check routes `failure` back to `build`
  well inside the timeout budget, ruling out a `poll_timeout`-driven trigger; the findings content distinguishes a plain
  CI failure from a red base check ("not this change").
- `test_pr_ci_self_heals_a_behind_branch_and_lands` — a behind-base PR fires `update-branch` and pends before healing,
  reaching `done` only once the `stale_branch` lever clears through that call.
- `test_pr_ci_bounces_a_dirty_conflict_back_to_build` — a real merge conflict routes the first recorded bounce, cause
  `conflict`, back to `build`, with nothing merged at the forge.

## test_forge_status_e2e

The **forge-status label projection** (#179): one work source opted into `annotate = true` with a 1s sweep interval, one
minted fixture, four properties.

- `test_forge_status_projection_e2e` — the happy path: ingest shows `blizzard:ingested`, driving the chunk through
  build/review/deliver flips it to `blizzard:in-progress` at some point before `done`, where both clear (a label-history
  snapshot taken every tick, since the sweep lands asynchronously on its own interval rather than in lockstep with a
  runner tick). A second chunk stopped before any runner ever claims it has its marker cleared on the next sweep. A
  label deleted by hand on the forge is re-asserted on the next sweep — the hub holds no annotation state of its own, so
  nothing needs repairing, only re-deriving. And the forge's own `unreachable` lever (not a process kill, which would
  also wipe its in-memory issue/label state and defeat "re-converges once the forge returns") stands in for an outage:
  the hub keeps serving reads and chunk transitions throughout, the daemon log shows a `sources_skipped` entry naming
  the source, and the label lands once the lever clears. Needs the sibling `blizzard-mock` worktree + a local winter
  source, skipping without `BLIZZARD_E2E=1`; its Phase 2/3 unit/component coverage is `tests/test_work_source.py` (the
  GitHub adapter's annotator half) and `tests/test_forge_status.py` (`derive_marker`, `live_work_refs()`,
  `AnnotationReconciler.sweep()`), and its background-driver unit coverage is `tests/test_annotation_loop.py`; the
  service-tier companion `tests/service/test_forge_status_service.py` proves the sweep starts only for an opted-in
  source, browserless, against the real mock forge.
