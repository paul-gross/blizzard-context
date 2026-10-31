<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Delivery-policy and forge e2e scenarios (`bzh:e2e-delivery-policy`)

What `deliver` does when the forge answers with a red check, a conflict, or a pending CI run, the order a project lands
its repositories in, plus the label projection reporting a chunk's state back to the forge.

Every module in this file needs the sibling provisioned `blizzard-mock` worktree, skips without `BLIZZARD_E2E=1`, and
uses no browser.

## test_delivery_conflict_e2e

A delivery conflict at the default graph's `deliver` node lands zero repos: with the mock forge's `merge_conflict` lever
armed, the PR the build node opened is not cleanly mergeable, nothing lands, the bounce routes back to `build`, and the
route is kept. Its `fleet traces` subtest proves what the [acceptance loop](./delivery-loop.md#test_acceptance_loop)'s
does, and — the hub running with platform spans on at a zero root sample ratio — also that the deliver step's
`hub run step` platform spans parent on that trace's exported `hub exec` span: the hub's inline derivation and the sweep
agree. Its `platform spans` subtest proves what the acceptance loop's does for worker commands under their step roots,
across the bounce, and scans the export for planted secrets; it skips with `fleet traces`. Route-token containment is
covered by `tests/test_runner_loop.py` and `tests/test_completion_assembly_attachments.py`.

- `test_conflict_lands_zero_repos_and_routes_the_bounce_envelope_back_to_build` — proves the chunk's route holds at
  `build` with a `bounce-envelope` artifact recorded, cause `conflict`; the conflicted PR stays open and unmerged at the
  forge; and bare `main` never moves.

## test_flow_record_e2e

The flow record, kept by the hub's own flow driver over a real hub: a chunk held pending at `deliver` — the mock forge's
`checks_pending` lever armed — then landed once the lever clears. Flow invariant checks are covered by
`tests/test_invariant_checker.py`; the migration-boundary boot order of pending visits is covered by
`tests/test_flow_driver.py::test_a_store_carried_across_the_flows_revision_boots_pending_visits_in_entry_order`.

- `test_a_store_walked_below_flows_submits_its_standing_chunks_in_deliver_order_and_lands_every_one` — proves the
  landing carry-over. Two chunks pending at `deliver` and one paused there when the store walks down, the pending two
  minted so their id order is the reverse, are carried back by the migrated hub's boot. The pending two are submitted in
  the order they entered `deliver`, and once the lever clears both land. The paused one lands once resumed. Every chunk
  lands with the `landed` outcome, its `merged/<repo>` marker, and its `delivery_repo_landed` row, and no turn is left
  open.

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

## test_policy_carry_over_e2e

A store held before repositories carried a landing policy, carried onto them by a real migrate and hub: a HEAD hub is
seeded through its doors and lands one single-repository chunk while a second waits mid-delivery behind the mock forge's
`checks_pending` lever; the store walks down to `20261029_0900_close_attempt_resume_at`, where no repository holds a
policy, no project an order, and no submission its terms, and the HEAD migrate and hub carry it back up.
`hub:landing-position-on-link`, `hub:submission-terms-standing`, and `hub:repository-references-in-tenant` hold on the
carried-over store and at the end.

- `test_a_store_held_before_landing_policies_carries_over_and_lands_its_chunks_as_before` — proves every carried
  repository reads `merge-on-checks` and every project its links unranked; once the lever is released the chunk waiting
  at the upgrade lands, a third chunk lands after it, and both show the outcome and marker kinds the first chunk did.

## test_landing_order_e2e

A project's landing order deciding the order a multi-repository chunk lands, against the mock forge's `toy-api` and
`toy-web` repositories and, where a scenario needs a third, `toy-lib` added through the forge's `POST /_repos`. Each
scenario reads the order the merges reached the forge in, and ends with `hub:landing-position-on-link`,
`hub:submission-terms-standing`, and `hub:repository-references-in-tenant` holding.

- `test_a_library_ranked_first_lands_before_its_consumer` — proves `toy-web`, ranked ahead of `toy-api` against slug
  order, lands first.
- `test_a_second_project_lands_the_same_repositories_in_its_own_order` — proves two projects linking both repositories
  in reverse orders each land their own chunk in their own order.
- `test_one_ranked_repository_lands_before_two_unranked_in_slug_order` — proves with only `toy-web` ranked, it lands
  first, then `toy-api` and `toy-lib` by slug.
- `test_a_relinked_repository_keeps_its_position` — proves unlinking a ranked repository drops it from the order, and
  relinking it restores its position, a chunk then landing in that order.
- `test_an_exhausted_gap_is_renumbered_and_the_order_lands` — proves moves that halve the gap after one repository until
  no midpoint is left make the next move renumber the order `1.0, 2.0, …` and take the midpoint, and a chunk lands in
  the order that leaves.
- `test_a_reorder_while_a_chunk_waits_behind_another_reaches_only_later_chunks` — proves two chunks waiting behind the
  checks, the second behind the first, both land in the order their first turns took despite a reorder, while a chunk
  whose first turn follows the reorder lands in the new order.
- `test_an_interrupted_turn_keeps_the_terms_its_first_turn_took` — proves a chunk reordered under after its first turn,
  while waiting behind the checks, lands in the order it first took once the hub restarts with the checks green.
- `test_an_exported_document_applies_back_writing_nothing` — proves a hub with a ranked and an unranked repository
  exports its configuration, and applying the document back writes no record and no position.

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
