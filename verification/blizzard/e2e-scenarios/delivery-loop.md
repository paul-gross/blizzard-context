<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Delivery-loop e2e scenarios (`bzh:e2e-delivery-loop`)

The scenarios for the canonical `build → review → deliver` shape, the chunk shapes that ride it, the graph edges that
carry a chunk past its own graph or past the land.

The migration module needs the sibling provisioned `blizzard-mock` worktree and skips without `BLIZZARD_E2E=1`; it runs
in the tag `release` workflow's full e2e tier, not the `gate`/`pr` single-repo checkout.

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

## test_review_cycle_e2e

The cycle where review fails once, then passes, and the chunk lands. It runs under both mock harnesses, and its
`fleet traces` and `runner traces` subtests prove what the acceptance loop's do.

- `test_review_cycle_fails_once_then_delivers` — proves the findings asset and the fail edge's `prompt_addendum` thread
  back into build's re-entry envelope — the addendum's committed marker lands on bare `main` — with build running twice
  before review passes and it lands.

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
