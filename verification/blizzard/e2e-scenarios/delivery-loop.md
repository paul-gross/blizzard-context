<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Delivery-loop e2e scenarios (`bzh:e2e-delivery-loop`)

The scenarios for the canonical `build → review → deliver` shape, the chunk shapes that ride it, the graph edges that
carry a chunk past its own graph or past the land, and the first offer that brings a freshly set-up runner into it.

The spike, post-merge, and migration modules each need the sibling provisioned `blizzard-mock` worktree and skip without
`BLIZZARD_E2E=1`, and run in the tag `release` workflow's full e2e tier, not the `gate`/`pr` single-repo checkout.

## test_acceptance_loop

The happy path: build, then a scripted-PASS review, then deliver, to landed. It also proves its fleet traces — the
`fleet traces` subtest reads the hub's exported spans back from a real `otelcol-contrib` — when a collector is present,
and that subtest alone skips without one. It runs under both mock harnesses — Claude Code, and OpenCode with every
runner node on a graph-level session pinned to it — and its `runner traces` subtest proves the runner's lease spans nest
on the hub's step roots by id alone, each invocation carrying its harness, model and token counts; that subtest skips
with `fleet traces`. Its `platform spans` subtest runs the hub and the runner with platform spans at a zero root sample
ratio, the runner joined to the hub through `runner init` and ticking over the one traced process graph its local API
serves, and proves every worker command's span sits under its step's root with the runner's request as its child; a
`runner work-items` command carries on to the runner's call to the hub, the hub's request under it and a store query
under that. It scans the raw exported file for planted secrets and the sentinel body of the review's findings artifact;
that subtest skips with `fleet traces`. Route-token containment is covered by `tests/test_runner_loop.py` and
`tests/test_completion_assembly_attachments.py`.

- `test_acceptance_loop_one_chunk_ingest_to_landed` — asserts that the commit is reachable from bare `main`, that the
  hub's facts derive `done`, that the merged PR's body names the issue's forge reference and the chunk id, and that bare
  `main`'s merge commit message carries the same reference.
- `test_a_tail_sampling_decision_wait_splits_or_keeps_the_chunk_trace` (ids `short` and `whole-chunk`) — runs the loop
  behind a collector whose `tail_sampling` keeps a trace only if it holds a step root, with the hub and runner settling
  for three seconds, and reads what the collector received against what it kept. A one-second `decision_wait` decides on
  the chunk trace's first platform span, before any root, so it keeps no step root and no worker command span; a
  `decision_wait` longer than the whole chunk keeps the step roots and the platform chain. It skips without a collector.
- `test_build_worker_reads_work_item_through_the_passthrough` — the build worker fetches its issue body and comment
  through the runner-to-hub work-item pass-through and commits the fetched text, asserted reachable from bare `main` —
  MVP criterion 1 at the e2e tier.

## test_basic_workspace

A chunk runs through the built-in folder-backed provider against a local bare git origin, with a trap that fails if any
child invokes winter. The mock harness owns creation of the feature branch; the provider allocates detached worktrees.

- `test_basic_workspace_chunk_lands_without_winter` — builds, reviews, and delivers a real chunk to bare `main` from a
  plain workspace directory, with the hub deriving `done` and no winter workspace or CLI invocation.

## test_runner_serves_default_e2e

A freshly set-up runner is offered work on its first registration, with no configuration edit between. Needs the sibling
provisioned `blizzard-mock` worktree for its forge.

- `test_a_freshly_initialized_runner_is_offered_a_default_chunk_on_first_registration` — joins a runner to a real hub
  daemon through `blizzard-runner init`, whose scaffolded config serves `default`; one `blizzard-runner tick` registers
  it, leaves the config byte-for-byte as scaffolded, and stores the hub's resolved answer in the runner's own store. The
  hub's matched peek, asked under the runner's own token, then offers it the promoted chunk of `default`, naming the
  project's id and slug.

## test_review_cycle_e2e

The cycle where review fails once, then passes, and the chunk lands. It runs under both mock harnesses, and its
`fleet traces` and `runner traces` subtests prove what the acceptance loop's do.

- `test_review_cycle_fails_once_then_delivers` — proves the findings asset and the fail edge's `prompt_addendum` thread
  back into build's re-entry envelope — the addendum's committed marker lands on bare `main` — with build running twice
  before review passes and it lands.

## test_post_merge_node_e2e

The authored post-merge edge: a graph whose `deliver` hub command node authors `landed → verify`, a post-merge runner
node. The crash-tier companion is `tests/crash/test_kill9_sweep.py::test_kill9_at_action_crash_point_through_land` — the
`action.after-write.before-resume` window, after `land` marks a repo landed but before it resumes, shared by every hub
action.

- `test_authored_landed_edge_runs_a_post_merge_node_after_landing` — merges every repo to bare `main`, then the runner
  advances the held chunk into `verify` in its warm environment after the land — the transition history reads
  `build → deliver (landed) → verify → done` — and the informational `landed` detail stays true at `done`.

## test_migration_e2e

The cross-graph migration: a source graph (`default-delivery`) whose `build` node authors a cross-graph judgement
choice, `to: graph:triage-delivery`, handing the chunk off. The crash-tier companion is
`test_kill9_at_migrate_crash_point`, the `migrate.after-record.before-response` window. The two-graph timeline on the
served board runs as `tests/ui/migration.spec.ts`. Its `fleet traces` subtest proves what the acceptance loop's does.

- `test_cross_graph_migration_repins_requeues_and_lands_under_the_new_graph` — proves taking the choice records a
  migration (never a transition), re-pins `graph_id`, and re-queues the chunk at the target graph's own `build` node
  (name-match, else entry), which commits and delivers to bare `main`; asserted at both ends — the change reachable from
  `main` exactly once (the target's branch is the only landing one) and the hub showing the `migrations` step, the
  two-graph history, the re-pinned `graph_id`, and `done`.

## test_review_findings_delivery_e2e

The `record-findings` node: a review round's mixed delta lands, then mints exactly its deferred entry.

- `test_review_finding_delta_mints_exactly_its_deferred_entry_at_landing` — the real packaged `bas-dwf` graph, `deliver`
  and `record-findings` unscripted (the real `land`/`record-findings` actions and hub route run for real); a scripted
  review publishes a `review-finding-delta` holding one `deferred`, one `fixed`, and one `refuted` entry; after landing,
  `GET /api/findings` shows exactly one review-sourced finding, carrying the deferred entry's severity, class, locus,
  and the chunk that raised it — the `fixed`/`refuted` entries mint nothing.

## test_spike_terminal_e2e

The non-code spike chunk (MVP criterion 10): a read-only `spike` node produces a `spike-notes` asset and routes into the
same `deliver` node a code chunk uses; with nothing to land, the chunk derives `done` with no PR and asset artifacts
only.

- `test_spike_chunk_terminates_with_only_asset_artifacts` — asserts the write-up becomes the `spike-notes` asset's
  content, the artifacts carry no `git_commit` kind, the forge never sees a PR, and bare `main` never moves.
