<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Delivery-policy and forge e2e scenarios (`bzh:e2e-delivery-policy`)

What `deliver` does when the forge answers with a pending CI run, and the order a project lands its repositories in.

Every module in this file needs the sibling provisioned `blizzard-mock` worktree, skips without `BLIZZARD_E2E=1`, and
uses no browser.

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
