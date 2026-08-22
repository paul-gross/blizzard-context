<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Delivery-loop e2e scenarios (`bzh:e2e-delivery-loop`)

The scenarios for the canonical `build → review → deliver` shape, the chunk shapes that ride it, and the graph edges
that carry a chunk past its own graph or past the land.

The spike, post-merge, and migration modules each need the sibling provisioned `blizzard-mock` worktree plus a local
winter source, skip without `BLIZZARD_E2E=1`, and run in the tag `release` workflow's full e2e tier, not the `gate`/`pr`
single-repo checkout.

## test_acceptance_loop

The happy path: build, then a scripted-PASS review, then deliver, to landed.

- `test_acceptance_loop_one_chunk_ingest_to_landed` — asserts both that the commit is reachable from bare `main` and
  that the hub's facts derive `done`.
- `test_build_worker_reads_work_item_through_the_passthrough` — the build worker fetches its issue body and comment
  through the runner-to-hub work-item pass-through and commits the fetched text, asserted reachable from bare `main` —
  MVP criterion 1 at the e2e tier.

## test_review_cycle_e2e

The cycle where review fails once, then passes, and the chunk lands.

- `test_review_cycle_fails_once_then_delivers` — proves the findings asset and the fail edge's `prompt_addendum` thread
  back into build's re-entry envelope — the addendum's committed marker lands on bare `main` — with build running twice
  before review passes and it lands.

## test_post_merge_node_e2e

The authored post-merge edge: a graph whose `deliver` hub command node authors `landed → verify`, a post-merge runner
node. The crash-tier companion is `tests/crash/test_kill9_sweep.py::test_kill9_at_hub_command_node_crash_point` — the
`hubnode.after-marker.before-next` window, after a hub node marks a repo landed but before it moves on, shared by every
hub command node.

- `test_authored_landed_edge_runs_a_post_merge_node_after_landing` — merges every repo to bare `main`, then the runner
  advances the held chunk into `verify` in its warm environment after the land — the transition history reads
  `build → deliver (landed) → verify → done` — and the informational `landed` detail stays true at `done`.

## test_migration_e2e

The cross-graph migration: a source graph (`default-delivery`) whose `build` node authors a cross-graph judgement
choice, `to: graph:triage-delivery`, handing the chunk off. The crash-tier companion is
`test_kill9_at_migrate_crash_point`, the `migrate.after-record.before-response` window. The scenario's git and
fleet-truth assertions run in-process regardless; with Chromium installed it also drives the served board and `/graphs`
explorer to prove the two-graph timeline renders, degrading to the in-process assertions — never skipping the module —
without Chromium, and taking no built-bundle guard, so that browser half fails loudly on an unbuilt bundle.

- `test_cross_graph_migration_repins_requeues_and_lands_under_the_new_graph` — proves taking the choice records a
  migration (never a transition), re-pins `graph_id`, and re-queues the chunk at the target graph's own `build` node
  (name-match, else entry), which commits and delivers to bare `main`; asserted at both ends — the change reachable from
  `main` exactly once (the target's branch is the only landing one) and the hub showing the `migrations` step, the
  two-graph history, the re-pinned `graph_id`, and `done`.

## test_spike_terminal_e2e

The non-code spike chunk (MVP criterion 10): a read-only `spike` node produces a `spike-notes` asset and routes into the
same `deliver` node a code chunk uses; with nothing to land, the chunk derives `done` with no PR and asset artifacts
only.

- `test_spike_chunk_terminates_with_only_asset_artifacts` — asserts the write-up becomes the `spike-notes` asset's
  content, the artifacts carry no `git_commit` kind, the forge never sees a PR, and bare `main` never moves.
