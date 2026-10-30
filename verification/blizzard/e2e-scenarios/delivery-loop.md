<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Delivery-loop e2e scenarios (`bzh:e2e-delivery-loop`)

The scenarios for the canonical `build → review → deliver` shape, the chunk shapes that ride it, and the graph edges
that carry a chunk past its own graph or past the land.

The remaining modules need the sibling provisioned `blizzard-mock` worktree and skip without `BLIZZARD_E2E=1`, and run
in the tag `release` workflow's full e2e tier, not the `gate`/`pr` single-repo checkout.

## test_review_findings_delivery_e2e

The `record-findings` node: a review round's mixed delta lands, then mints exactly its deferred entry.

- `test_review_finding_delta_mints_exactly_its_deferred_entry_at_landing` — the real packaged `bas-dwf` graph, `deliver`
  and `record-findings` unscripted (the real `land`/`record-findings` actions and hub route run for real); a scripted
  review publishes a `review-finding-delta` holding one `deferred`, one `fixed`, and one `refuted` entry; after landing,
  `GET /api/findings` shows exactly one review-sourced finding, carrying the deferred entry's severity, class, locus,
  and the chunk that raised it — the `fixed`/`refuted` entries mint nothing.
