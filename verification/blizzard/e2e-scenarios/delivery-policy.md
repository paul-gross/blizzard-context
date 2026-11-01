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
