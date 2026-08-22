# e2e scenarios — the delivery loop (`bzh:e2e-delivery-loop`)

<!-- one `##` section per `tests/e2e/` module, its bullets naming that module's test functions — machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s check C. -->

The canonical `build → review → deliver` shape, the chunk shapes that ride it, and the graph edges that carry a chunk
past its own graph or past the land.

## test_acceptance_loop

The happy path: build → review (scripted PASS) → deliver → landed.

- `test_acceptance_loop_one_chunk_ingest_to_landed` — asserts the commit is reachable from bare `main` **and** the hub's
  facts derive `done`.
- `test_build_worker_reads_work_item_through_the_passthrough` — the build worker fetches its issue body and comment
  through the runner→hub work-item pass-through and commits the fetched text, asserted reachable from bare `main` (MVP
  criterion 1 at the e2e tier).

## test_review_cycle_e2e

Review fails once, then passes and the chunk lands.

- `test_review_cycle_fails_once_then_delivers` — the findings asset + fail-edge `prompt_addendum` thread back into
  build's re-entry envelope (the addendum's committed marker lands on bare `main`), build runs twice, then review passes
  and it lands.

## test_spike_terminal_e2e

**A non-code spike chunk** (MVP criterion 10's second sentence): a read-only `spike` node produces a `spike-notes` asset
and routes into the same `deliver` node a code chunk uses; with nothing to land, the chunk derives `done` with no PR and
asset artifacts only. Needs the sibling `blizzard-mock` worktree + a local winter source, skipping without
`BLIZZARD_E2E=1`; no browser.

- `test_spike_chunk_terminates_with_only_asset_artifacts` — the investigation write-up becomes the `spike-notes` asset's
  content, the chunk's artifacts carry no `git_commit` kind, the forge sees no PR ever opened, and bare `main` never
  moves.

## test_post_merge_node_e2e

The **authored post-merge edge**: a graph whose `deliver` hub command node authors `landed → verify` (a post-merge
runner node).

- `test_authored_landed_edge_runs_a_post_merge_node_after_landing` — merges every repo to bare `main`, then the runner
  advances the held chunk into `verify` in its warm environment and runs it *after* the land — the chunk's transition
  history reads `build → deliver (landed) → verify → done`, so `verify` demonstrably ran post-merge, and its
  informational `landed` detail stays true at `done`; its crash-tier companion is
  `tests/crash/test_kill9_sweep.py::test_kill9_at_hub_command_node_crash_point` (the `hubnode.after-marker.before-next`
  window — the per-step window after a hub node marks a repo landed but before it moves on, shared by every hub command
  node). It needs no browser, but like the others it needs the sibling provisioned `blizzard-mock` worktree and a local
  winter source, so it is skipped in the `gate`/`pr` single-repo checkout and runs in the tag `release` workflow's full
  e2e tier.

## test_migration_e2e

The **cross-graph migration** (#90): a source graph (`default-delivery`) whose `build` node authors a cross-graph
judgement choice (`to: graph:triage-delivery`) hands the chunk off.

- `test_cross_graph_migration_repins_requeues_and_lands_under_the_new_graph` — taking it records a migration (never a
  transition), re-pins `graph_id` to the target, and re-queues the chunk at the target graph's own `build` node
  (name-match-else-entry), which commits + delivers to bare `main`; asserted at both ends (the change reachable from
  `main` exactly once — the target's is the only landing branch; the hub's `migrations` step + two-graph history +
  re-pinned `graph_id` + `done`). Its crash-tier companion is `test_kill9_at_migrate_crash_point` (the
  `migrate.after-record.before-response` window); the served board renders the two-graph timeline
  (`MigrationView`/history union) and the `/graphs` explorer is unaffected (it reads graphs, not chunks), both covered
  generically by `test_board_browser_e2e`/`test_graphs_diagram_browser_e2e`. Like the others it needs the sibling
  `blizzard-mock` worktree + a local winter source and runs in the tag `release` full e2e tier. Its git + fleet-truth
  assertions run in-process regardless; when Chromium is installed it additionally drives the served board and the
  `/graphs` explorer to prove the two-graph timeline renders, degrading — never skipping the module — to the in-process
  assertions alone when Chromium is absent; it takes no built-bundle guard, so that browser half fails loudly rather
  than skipping if the bundle is unbuilt.
