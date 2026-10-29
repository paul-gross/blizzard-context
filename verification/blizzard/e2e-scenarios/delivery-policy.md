<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Delivery-policy and forge e2e scenarios (`bzh:e2e-delivery-policy`)

What `deliver` does when the forge answers with a red check, a conflict, or a pending CI run, plus the label projection
reporting a chunk's state back to the forge.

Every module in this file needs the sibling provisioned `blizzard-mock` worktree, skips without `BLIZZARD_E2E=1`, and
uses no browser.

## test_delivery_conflict_e2e

A delivery conflict at the default graph's `deliver` node lands zero repos: with the mock forge's `merge_conflict` lever
armed, the PR the build node opened is not cleanly mergeable, nothing lands, the bounce routes back to `build`, and the
route is kept. Its `fleet traces` subtest proves what the [acceptance loop](./delivery-loop.md#test_acceptance_loop)'s
does, and — the hub running with platform spans on at a zero root sample ratio — also that the deliver step's
`hub run step` platform spans parent on that trace's exported `hub exec` span: the hub's inline derivation and the sweep
agree. Its `platform spans` subtest proves what the acceptance loop's does for worker commands under their step roots,
across the bounce, and scans the export for the same planted tokens; it skips with `fleet traces`.

- `test_conflict_lands_zero_repos_and_routes_the_bounce_envelope_back_to_build` — proves the chunk's route holds at
  `build` with a `bounce-envelope` artifact recorded, cause `conflict`; the conflicted PR stays open and unmerged at the
  forge; and bare `main` never moves.

## test_delivery_pr_ci_e2e

Delivery policy lives in YAML, not code: the module's graph differs from the default only in `deliver`'s poll cadence
and routing, names the same `land` action and choice names the shipped graph authors, and drives every route through the
same generic `executor: hub` primitive. Its `fleet traces` subtest proves what the acceptance loop's does.

- `test_pr_ci_bounces_a_dirty_conflict_back_to_build` — proves a real merge conflict routes the first recorded bounce,
  cause `conflict`, back to `build`, with nothing merged at the forge.
- `test_pr_ci_bounces_a_poll_timeout_back_to_build` — proves a PR blocked past the node's few-second `poll_timeout` is a
  kick-back: the bounce carries cause `poll-timeout` and the chunk re-enters `build`, with nothing merged at the forge
  and bare `main` never moving; its traces subtest shows the deliver step's `hub poll pending` events, its `bounce`
  event, and the next `build` step linked `bounce`.
- `test_pr_ci_pends_on_blocked_then_lands_when_green` — proves a blocked PR pends over several polls with exactly one
  unchanging `delivery-findings` artifact, then lands once the required check goes green.
- `test_pr_ci_routes_failure_on_a_terminally_failed_check` — proves a terminally failed check routes `failure` back to
  `build` well inside the timeout budget, ruling out a `poll_timeout` trigger, the findings content distinguishing a
  plain CI failure from a red base check ("not this change").
- `test_pr_ci_self_heals_a_behind_branch_and_lands` — proves a behind-base PR, with the base really moved, fires
  `update-branch` and pends before healing, the head advancing past the submitted commit by a merge of the base and
  reaching `done` only once the `stale_branch` lever clears through that call.
- `test_pr_ci_refuses_a_foreign_commit_on_the_head` — proves a commit pushed onto the PR's branch after submission
  routes `failure` back to `build`, the `delivery-findings/foreign-head` artifact naming that commit, with nothing
  merged at the forge and bare `main` never moving.
- `test_pr_ci_lands_an_unstable_pr_once_checks_are_green` — proves a PR the forge reports `unstable` is mergeable: once
  its required checks read green it merges and the chunk reaches `done`.
- `test_pr_ci_waits_on_a_draft_or_hooked_pr` — proves a green PR the forge reports `draft` or `has_hooks`, one case
  each, pends over repeated polls with no bounce, nothing merged at the forge and bare `main` never moving.
- `test_pr_ci_waits_on_a_startup_failure_check_then_lands` — proves a check concluded `startup_failure` pends rather
  than routing `failure`, and the chunk lands once the check reads green.
- `test_pr_ci_routes_conflict_when_updating_a_behind_branch_conflicts` — proves a behind PR whose base really conflicts
  with the change meets a refused `update-branch` and routes the first bounce, cause `conflict`, back to `build`, with
  nothing merged at the forge.
- `test_pr_ci_escalates_a_rejected_credential_as_forge_auth` — proves the forge rejecting the repository's credential
  escalates the chunk to `needs_human` at `deliver` with cause `forge-auth`, the detail naming the repository, rather
  than bouncing it.
- `test_pr_ci_escalates_a_repository_the_forge_does_not_know_as_forge_config` — proves a repository record whose forge
  does not know it escalates the chunk to `needs_human` with cause `forge-config`, the detail naming that forge, nothing
  merged.
- `test_pr_ci_waiting_on_pending_checks_reads_conditionally_one_lookup_a_pass` — proves a landing pending over ten polls
  spends no counted forge call on a landing read after its first pass, every one answered `304`, and makes its
  already-merged lookup as one head-filtered read a pass, nothing merged.
- `test_pr_ci_does_not_merge_ahead_of_a_check_that_starts_after_the_others_finish` — proves a revision whose one check
  is green, gaining a second pending check before the next pass, is not merged until that check is green, then lands.
- `test_pr_ci_bounces_a_revision_with_no_check_at_its_poll_timeout` — proves a revision armed with no check is never
  green: it pends and bounces at the node's poll timeout, cause `poll-timeout`, nothing merged.

## test_hub_actions_e2e

A hub node that names an action, through a real hub process: `land` against the mock forge, and the two test actions the
hub admits only behind `BLIZZARD_TEST_ACTIONS=1` beside `BLIZZARD_CRASH_FENCE=1`, which the e2e launcher sets.

- `test_land_lands_a_chunk_against_the_mock_forge` — proves `land` opens the chunk's PR and merges it: the chunk reaches
  `done` reporting the repository landed at bare `main`'s new tip, through one merged PR, the change on `main` exactly
  once.
- `test_test_actions_drive_hub_nodes` — proves `test.answer` routes its `choice` in one pass, and `test.sequence` waits
  on its first pass and answers `done` on its second, recording `test-sequence/0` and `test-sequence/1`.
- `test_a_hub_without_the_test_fences_refuses_the_test_actions` — proves a hub started without both fences refuses a
  graph naming either test action at mint, each as an unknown action.

## test_run_carry_over_e2e

A store held before hub nodes named actions, carried onto them by a real migrate and hub: a HEAD hub pins one chunk per
shipped `run:` command and one to an empty `run:`, the `land_pr_ci` one left waiting on `pending`; the store walks down
to `20261023_0901_hub_actions`, each hub node is rewritten to the `run:` row it was minted as, and the HEAD migrate and
hub carry it.

- `test_a_store_held_before_actions_carries_over_and_lands_every_chunk` — proves every pinned chunk lands with its
  script's choice and markers once its hub node is carried onto the action its `run:` named.

## test_forge_carry_over_e2e

A store held before forges were records, carried onto them by a real migrate and hub: a HEAD hub seeded through its
doors with the old address fields — the fixture work source's `api_base` and its repository's `forge_api_url`, both the
mock forge's `http://127.0.0.1:<port>` — lands one chunk; the store walks down to `20261024_0900_hub_legacy_run`, where
no forge exists, and the HEAD migrate and hub carry it.

- `test_a_store_held_before_forges_carries_over_and_lands_a_chunk_as_before` — proves both records name one forge for
  that origin, its port kept in its slug, and a second chunk lands against the mock forge with the same deliver choices
  and marker kinds as the chunk landed before the carry-over.

## test_flow_record_e2e

The flow record, kept by the hub's own flow driver over a real hub: a chunk held pending at `deliver` — the mock forge's
`checks_pending` lever armed — and a store walked below `20261027_0900_flows`, carried back by a real migrate and hub.
After each step the three flow invariants — `hub:one-turn-per-flow`, `hub:one-turn-per-visit`, and
`hub:flow-line-standing` — hold, and once the chunk lands no turn is open.

- `test_a_held_chunk_is_submitted_and_its_landing_supersedes_it` — proves a chunk held at the hub node is submitted to
  its branch's flow and polls through turns, and once the lever clears, the turn that lands it closes that submission
  `landed`.
- `test_a_store_walked_below_flows_submits_its_pending_chunks_in_the_order_they_entered_deliver` — proves two chunks
  pending at `deliver` when the store walks down, minted so their id order is the reverse, are submitted on the migrated
  hub's boot in the order they entered `deliver`, both still delivering.

## test_flow_turns_e2e

Every hub step taken as a turn on the flows of the branches it lands on, by the hub's own flow driver against the mock
forge. Each scenario ends with the flow invariants holding and no turn open.

- `test_two_repositories_land_side_by_side` — proves chunks on two repositories hold disjoint flows and both keep
  turning while held, and one lands while the other still waits.
- `test_two_chunks_on_one_branch_land_in_arrival_order` — proves two chunks held on one branch, come due together on a
  hub restarted with the checks green, land in the order they arrived.
- `test_a_garden_delivery_lands_while_a_chunk_is_held_on_a_branch` — proves a garden run's delivery, which holds no
  branch, lands while a chunk is held pending on one.
- `test_two_chunks_each_landing_both_repositories_both_land` — proves two chunks each landing the same two repositories
  share both flows and both land.
- `test_a_pending_chunk_yields_its_branch_until_its_next_poll` — proves a pending chunk is not next again before its
  next poll, and another chunk on its branch takes a turn in every gap between its turns.
- `test_a_chunk_whose_runner_is_gone_lands_and_records_its_findings` — proves the hub alone lands a chunk whose runner
  is gone after build and takes it through `record-findings`.
- `test_a_chunk_paused_at_a_hub_node_takes_no_turn_until_resumed` — proves a chunk that reaches `deliver` paused takes
  no turn there, and lands once resumed.

## test_checks_gate_e2e

Checks-gate enforcement: a graph whose `build` choice carries `requires_checks: true` shows the gate — not the worker's
judged choice — decides whether a red check bounces the attempt back to `build`, landing once green; a companion graph
routes its failing check through a non-gated `fail` choice, an ordinary judged transition where the gate never fires.
The component-tier companion `test_checks_gate_agreement.py` proves the runner's local gate and the hub's completion
backstop agree over a decision matrix; this module, reusing the shared live-stack scaffolding in
`tests/fleet_launchers.py`, proves the resulting predicate against the real forge, hub, and runner.

- `test_checks_gate_bounces_a_red_pass_then_lands_when_green` — proves the gated `pass` choice is bounced while its
  check is red, build runs again, and the chunk lands once the check is green.
- `test_a_red_check_through_a_non_gated_fail_routes_normally` — proves a red check reported through the ungated `fail`
  choice routes back to `build` as an ordinary judged transition, the gate never firing, and the green re-entry lands.

## test_forge_status_e2e

The forge-status label projection: one work source opted into `annotate = true` with a 1s sweep interval, over one
minted fixture. The unit/component companions are `tests/test_work_source.py` (the GitHub adapter's annotator half),
`tests/test_forge_status.py`, and `tests/test_annotation_loop.py` (the background driver); the service-tier
`tests/service/hub/forge-status.spec.ts` proves only an opted-in source's issues are labelled, browserless, against the
real mock forge.

- `test_forge_status_projection_e2e` — proves the happy path: ingest shows `blizzard:ingested`, the build/review/deliver
  drive flips it to `blizzard:in-progress` before `done`, where both clear — snapshotting label history every tick
  because the sweep lands asynchronously on its own interval, not in lockstep with runner ticks. The same function
  proves a chunk stopped before any runner claims it has its marker cleared on the next sweep, and a hand-deleted label
  is re-asserted within one full-pass floor (five sweep intervals) — the hub holds only in-memory probe state, so it
  re-derives rather than repairs. It stands in an outage, longer than the floor, with the forge's own `unreachable`
  lever — a process kill would wipe the forge's in-memory issue/label state and defeat proving re-convergence — and
  proves the hub keeps serving reads and transitions throughout, the daemon log records a `sources_skipped` entry naming
  the source, and the label lands once the lever clears.

## test_forge_budget_e2e

The shared forge rate budget: one work source opted into `annotate = true` with a 1s sweep interval and the repository
it delivers to, both naming one forge and one secret, so the annotation sweep, the close drain and `land` spend one
budget. The scenario drives the mock forge's `rate_budget`, `rate_limited` and `secondary_rate_limited` levers. The unit
companions are `tests/test_forge_budget.py`, `tests/test_forge_registry.py`,
`tests/test_github_work_source_rate_gate.py` and `tests/test_flow_driver.py`. Bucket routing for a resource other than
`core` is proven only there, because the mock forge answers `core` alone.

- `test_a_low_budget_turns_the_sweep_away_while_a_landing_proceeds` — proves a remaining set below two fifths of the
  limit, once the sweep's next answer teaches it to the hub, turns the sweep away with no request sent. A newly ingested
  chunk is never labelled, past the full-pass floor, and `GET /api/forges/<forge>`'s reading does not move. A landing of
  that chunk still proceeds to bare `main`, its answers lowering the reading. The landed chunk's close is turned away
  too. Its one attempt is `deferred` with its resume at the window's reset, and a second pass makes no attempt before
  the reset. No closure fact is written, the intent stays pending, and the issue stays open. Across every turn-away the
  log holds exactly one `forge-budget-low` warning.
- `test_a_rate_refused_landing_pends_until_the_refusal_lifts_then_lands` — proves, one case each for `rate_limited` and
  `secondary_rate_limited`, that a landing the forge refuses for its rate answers `pending` with nothing merged. Its
  next poll is the refusal's `Retry-After`. Once the lever clears, the spent budget still holds the landing until the
  refusal lifts. A primary refusal's no-remaining reading holds it on to the window's reset, the last pending poll
  naming that reset. The landing then reaches bare `main`, and the log holds exactly one `forge-rate-limited` warning.
