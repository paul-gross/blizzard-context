<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Delivery-policy and forge e2e scenarios (`bzh:e2e-delivery-policy`)

What `deliver` does when the forge answers with a red check, a conflict, or a pending CI run, plus the label projection
reporting a chunk's state back to the forge.

Every module in this file needs the sibling provisioned `blizzard-mock` worktree plus a local winter source, skips
without `BLIZZARD_E2E=1`, and uses no browser.

## test_delivery_conflict_e2e

A delivery conflict at the default graph's `deliver` node lands zero repos: with the mock forge's `merge_conflict` lever
armed, the PR the build node opened is not cleanly mergeable, nothing lands, the bounce routes back to `build`, and the
route is kept.

- `test_conflict_lands_zero_repos_and_routes_the_bounce_envelope_back_to_build` — proves the chunk's route holds at
  `build` with a `bounce-envelope` artifact recorded, cause `conflict`; the conflicted PR stays open and unmerged at the
  forge; and bare `main` never moves.

## test_delivery_pr_ci_e2e

Delivery policy lives in YAML, not code: the module's graph differs from the default only in `deliver`'s `run:` script
and poll cadence, names the same `land_pr_ci` script and choice names the shipped graph authors, and drives every route
through the same generic `executor: hub` primitive.

- `test_pr_ci_bounces_a_dirty_conflict_back_to_build` — proves a real merge conflict routes the first recorded bounce,
  cause `conflict`, back to `build`, with nothing merged at the forge.
- `test_pr_ci_pends_on_blocked_then_lands_when_green` — proves a blocked PR pends over several polls with exactly one
  unchanging `delivery-findings` artifact, then lands once the required check goes green.
- `test_pr_ci_routes_failure_on_a_terminally_failed_check` — proves a terminally failed check routes `failure` back to
  `build` well inside the timeout budget, ruling out a `poll_timeout` trigger, the findings content distinguishing a
  plain CI failure from a red base check ("not this change").
- `test_pr_ci_self_heals_a_behind_branch_and_lands` — proves a behind-base PR fires `update-branch` and pends before
  healing, reaching `done` only once the `stale_branch` lever clears through that call.

## test_checks_gate_e2e

Checks-gate enforcement: a graph whose `build` choice carries `requires_checks: true` shows the gate — not the worker's
judged choice — decides whether a red check bounces the attempt back to `build`, landing once green; a companion graph
routes its failing check through a non-gated `fail` choice, an ordinary judged transition where the gate never fires.
The component-tier companion `test_checks_gate_agreement.py` proves the runner's local gate and the hub's completion
backstop agree over a decision matrix; this module, reusing `test_acceptance_loop`'s live-stack scaffolding, proves the
resulting predicate against the real forge, hub, and runner.

- `test_checks_gate_bounces_a_red_pass_then_lands_when_green` — proves the gated `pass` choice is bounced while its
  check is red, build runs again, and the chunk lands once the check is green.
- `test_a_red_check_through_a_non_gated_fail_routes_normally` — proves a red check reported through the ungated `fail`
  choice routes back to `build` as an ordinary judged transition, the gate never firing, and the green re-entry lands.

## test_forge_status_e2e

The forge-status label projection: one work source opted into `annotate = true` with a 1s sweep interval, over one
minted fixture. The unit/component companions are `tests/test_work_source.py` (the GitHub adapter's annotator half),
`tests/test_forge_status.py`, and `tests/test_annotation_loop.py` (the background driver); the service-tier
`tests/service/test_forge_status_service.py` proves the sweep starts only for an opted-in source, browserless, against
the real mock forge.

- `test_forge_status_projection_e2e` — proves the happy path: ingest shows `blizzard:ingested`, the build/review/deliver
  drive flips it to `blizzard:in-progress` before `done`, where both clear — snapshotting label history every tick
  because the sweep lands asynchronously on its own interval, not in lockstep with runner ticks. The same function
  proves a chunk stopped before any runner claims it has its marker cleared on the next sweep, and a hand-deleted label
  is re-asserted on the next sweep — the hub holds no annotation state, so it re-derives rather than repairs. It stands
  in an outage with the forge's own `unreachable` lever — a process kill would wipe the forge's in-memory issue/label
  state and defeat proving re-convergence — and proves the hub keeps serving reads and transitions throughout, the
  daemon log records a `sources_skipped` entry naming the source, and the label lands once the lever clears.
