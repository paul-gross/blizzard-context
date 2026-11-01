<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Delivery-policy and forge e2e scenarios (`bzh:e2e-delivery-policy`)

No delivery-policy or forge e2e scenarios remain. Flow migration carry-over belongs to
`src/blizzard/hub/store/migrations/tests/20261027_0900_flows_test.py`, the migration-boundary boot-order proof in
`tests/test_flow_driver.py`, and the released-build upgrade rehearsal (`blizzard:rehearsal`). Flow invariant checks
remain in `tests/test_invariant_checker.py`.
