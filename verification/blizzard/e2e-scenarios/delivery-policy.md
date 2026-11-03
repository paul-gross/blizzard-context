<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Delivery-policy and forge e2e scenarios (`bzh:e2e-delivery-policy`)

No delivery-policy or forge e2e scenarios remain. Their Playwright replacements are in the
[service-test roster](../commands/test-tiers/service.md). Landing-policy carry-over belongs to the landing-policy
migration's colocated test and the released-build upgrade rehearsal (`blizzard:rehearsal`). Flow migration carry-over
belongs to the flows migration's colocated test, the migration-boundary boot-order proof in `tests/test_flow_driver.py`,
and the released-build upgrade rehearsal (`blizzard:rehearsal`). Flow invariant checks remain in
`tests/test_invariant_checker.py`.
