# e2e scenarios — the operator board in a browser (`bzh:e2e-board`)

<!-- one `##` section per `tests/e2e/` module, its bullets naming that module's test functions — machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s check C. -->

The scenarios that drive a real Chromium over the web app the hub serves — the operator board's views, its live SSE
updates, and the graph explorer.

## test_board_browser_e2e

The **browser half of the e2e tier**: a real Chromium driven by Playwright over the served mission-control board
(`blizzard hub host` mounts the built Angular app at `/`).

- `test_board_browser_live_group_reorder_answer_and_pause` — loaded once and never reloaded, it proves the status chip
  flips live over SSE as facts land, the detail drawer renders node history + the artifact store, two ready chunks are
  **grouped** from their cards in the board's **READY lane** — #137 folded the ready queue back onto the board as a
  column, so a promoted chunk crosses from BACKLOG into READY rather than leaving the board — and the queue is
  **reordered** by dragging the grouped survivor's card to the top of that lane with real pointer events (the
  `@angular/cdk` drop list the lane arms; the drop → anchor arithmetic itself is fenced at `web:unit-test` with a
  synthesized `CdkDragDrop`), so the next FILL claims the grouped plural-pointer survivor first (both honored), a parked
  chunk's question is **answered from the board** and it resumes to `done`; a running chunk is **paused directly from
  its chunk detail dock** — the claim-keeping, one-*chunk* lever, distinct from the runner-level brake below: its chip
  flips to `paused` live over SSE with no reload (the one status a pause-parked chunk's chip actually shows —
  [../../../domain/work.md](../../../domain/work.md) §Statuses explains why `paused` ranks below the human-gated
  statuses, so the proof needs a chunk caught genuinely running, not one already parked on a question) and relocates to
  the WAIT/HUMAN column, the claim survives (its route holds after the runner kills the worker and parks the lease), the
  dock names who paused it, and resuming it from the dock returns it to a live, progressing status; and the runner
  registry's **pause/resume** brake stops and then restarts new claims (MVP criterion 11) — engaged *before* the
  survivor lands, because the landing frees the runner's only agent slot in the same tick (FILL's reconcile releases the
  survivor's binding, blizzard#202), so from that instant the brake is the only thing holding the remaining ready chunk
  in the lane.

Needs the built bundle `blizzard hub host` serves + the sibling provisioned `blizzard-mock` worktree + a local winter
source + an installed Chromium; it skips cleanly without `BLIZZARD_E2E=1`, without Chromium, without the provisioned
worktree, or without the winter source — but an unbuilt bundle fails loudly instead of skipping.

## test_board_cost_live_e2e

The **cost/usage render half** (epic #57 / #60): the same served board, loaded once and never reloaded, over a chunk
claimed straight through `POST /api/fleet/routes`.

- `test_board_renders_cost_and_updates_live_over_sse` — proves the P4 figures render end to end off the live hub — the
  card's **cost badge**, the header's **spend-today** figure (`GET /api/spend?since=`), and the detail dock's **cost +
  the four token classes inline** (issue #182 retired the expand toggle) — and, the claim only a real browser over the
  real SSE spine can make, that they **update live over SSE with no reload**: a fresh `usage.recorded` fact pushed to
  `POST /api/fleet/events` re-broadcasts `chunk-changed`, the `FleetLiveUpdates` spine invalidates the chunk read
  **and** `hubFleetSpendKey`, and card + header + dock all move in place; a cost-absent (crash/reap-path) row then flips
  every figure to its `~`-marked **lower bound**, never a silently-understated exact. The **partial marking** and the
  per-history-step `(node, epoch)` inline match are additionally fenced at the component tier
  (`chunk-detail-panel.spec.ts`, `board-header.spec.ts`, `board-shell.spec.ts`, `fleet-live.spec.ts`,
  `test_usage_facts_ingest.py`, `test_fleet_spend_api.py`, `test_hub_cli_status.py`). It needs the sibling provisioned
  `blizzard-mock` worktree and a local winter source, so it is skipped in the `gate`/`pr` single-repo checkout; **the
  tag `release` workflow runs the full e2e tier headless** over the multi-repo checkout (Chromium installed via
  `uv run playwright install --with-deps chromium`), and the master `push` workflow runs the sibling service + crash
  tiers. Needs the built bundle `blizzard hub host` serves + the sibling provisioned `blizzard-mock` worktree + a local
  winter source + an installed Chromium (locally: `uv run playwright install chromium`); it skips cleanly without
  `BLIZZARD_E2E=1`, without Chromium, without the provisioned worktree, or without the winter source — but an unbuilt
  bundle fails loudly instead of skipping.

## test_event_log_e2e

The **operational event log** (#125): the module holds in-process and browser-driven assertions.

- `test_a_verdict_less_exit_surfaces_a_critical_worker_lost_event` — the in-process half: drives a real mock worker to a
  **verdict-less** exit that exhausts its retry budget, so the runner escalates and its Phase-3 emission surfaces a
  **critical** `worker-lost` operational event that both reads back off the live `GET /api/events` **and** fans out on
  the SSE spine as an `event-logged` frame (read off the stream's replay tail) — the runner-emit → hub-fold →
  read-and-fan-out chain end to end, no browser.
- `test_the_events_tab_renders_filters_and_updates_live_in_the_browser` — proving the **Events tab**: a real Chromium
  over the **built** bundle seeds a mixed-severity feed straight through `POST /api/fleet/events`, opens the **Events
  tab** from `nav-events`, and proves the rows render **severity-then-recency** (the critical row first though it
  arrived last), the severity filter narrows then restores the list, a fresh event pushed after load **arrives live over
  SSE with no reload**, and a row **deep-links** to its chunk.
- `test_the_rail_survives_a_reload_with_no_duplicate_or_missing_rows` — proving the board's **rail** Event log — the
  separate, pure-recency activity feed (#213 Phase 5), distinct from the Events tab above — survives a reload: it drives
  several fact families (a chunk transition, a question, a decision, a runner pause) to seed a mixed feed, loads the
  board once and confirms the rail's Event log panel renders a row for each over the live SSE spine, then **reloads the
  page** and confirms the same rows are still there — the panel's on-mount `GET /api/activity` backfill re-seeding the
  ring from durable history — with **no duplicate and no missing row at the seam** between the backfilled history and
  the live tee that resumes after reload.
- `test_the_events_grid_does_not_collapse_at_a_narrow_viewport` — issue #155's narrow-viewport fallback for the Events
  tab's time-first grid (#153/#154): at a real ~390px width a long-message row stays bounded in height and the page
  gains no horizontal scroll.

The browser-driven assertions above — every function but the in-process
`test_a_verdict_less_exit_surfaces_a_critical_worker_lost_event` — need the built bundle + the sibling `blizzard-mock`
worktree + a local winter source + an installed Chromium, skipping cleanly without any of them; the in-process function
needs the sibling `blizzard-mock` worktree + a local winter source. The file runs in the tag `release` full e2e tier,
skipped without `BLIZZARD_E2E=1`.

## test_glance_board_e2e

**The mobile glance board** (#181 Phase 5) at a real ~390px width (`bzh:narrow-viewport-tier-rule`): `/board` routes to
the glance shell, and a held-open `GET /api/chunks` proves the loading-vs-empty distinction — while the read is in
flight the "Needs you" lane shows loading, never empty (AC 4). A second consumer of `bzh:narrow-viewport-tier-rule`'s
`narrow_viewport` fixture. Needs the built bundle + the sibling `blizzard-mock` worktree + a local winter source + an
installed Chromium, skipping cleanly without any of them, or without `BLIZZARD_E2E=1`.

- `test_the_glance_board_shows_loading_before_rows_and_never_empty_on_a_populated_fleet` — with the chunks read captured
  and held open, the glance shell renders `needs-you-loading` and no `needs-you-empty` row; releasing the held route
  lands the row and clears loading, the empty state never shown in between.

## test_transcript_tab_browser_e2e

The **chunk board's Transcripts tab** (blizzard#248 Phase 3): a real Chromium over the served board, seeded by posting
segments straight through `POST /api/fleet/transcripts` as a runner principal rather than through a live runner's own
shipping lane (#246), which ships disabled by default (`[transcripts] ship = false`) and is covered at the component
tier by `tests/test_transcript_pump.py` and `tests/test_transcript_drain.py`. What this scenario proves is the **tab**,
so it seeds the hub the shortest honest way and asserts nothing about how a segment got there.

- `test_chunk_transcripts_tab_browser` — opens the tab on a bare-ingested chunk (no claim, lease, or transition)
  carrying one step's worth of segments, grouped under the tab's *unmatched* bucket rather than a history-matched step
  (`transcript-steps.spec.ts` proves that grouping unit-tested), opens the step's first segment (a collapsed-by-default
  thinking turn it expands, and a tool call it expands to reach the sidechain nested inline under it — `to_contain_text`
  reads `textContent`, populated even behind a closed `<details>`, so the card must actually open for the assertion to
  prove the nested content is reachable, not just present in the DOM), follows the continues-in link to the step's
  second segment, opens that segment's *unlinked* sidechain standalone and back again, then follows the continued-from
  link back to the first segment — proving the tab, the lazy per-segment fetch, the collapsed/expanding thinking render,
  the nested-vs-standalone sidechain split, and the resume-seam links all real, end to end.

Needs the built bundle `blizzard hub host` serves + the sibling provisioned `blizzard-mock` worktree (its
forge-registered repo only — no runner is ever spawned) + a local winter source + an installed Chromium; it skips
cleanly without `BLIZZARD_E2E=1`, without Chromium, without the provisioned worktree, or without the winter source.

## test_graphs_diagram_browser_e2e

The **graph-explorer diagram**: a real Chromium over the served board visits `/graphs`, opens a minted graph's detail
from the explorer.

- `test_graphs_diagram_renders_in_the_browser` — asserts the `<fleet-graph-diagram>` SVG DAG renders against the *built*
  bundle from real minted data (every declared node drawn, the START marker's connector landing on the graph's own entry
  node — blizzard#207 replaced the per-node entry ring with it, so which node is the entry survives only as laid-out
  geometry — an advance edge, and the review→build back-edge derived as a `retry` edge — a structural kind no wire field
  carries), naming the ever-present `graph-diagram-fallback` path a layout failure shows instead of a broken page.
  Unlike `test_board_browser_e2e` it needs **no runner and no forge traffic** — a diagram is a pure read of an immutable
  `GraphView` — so it stands up only the served hub. Needs the built bundle (hence `mise run e2e`'s
  `depends = ["web-build"]`) + an installed Chromium; it skips cleanly without `BLIZZARD_E2E=1` or without Chromium —
  but an unbuilt bundle fails loudly instead of skipping.
- `test_graphs_diagram_selection_in_the_browser` (blizzard#159, **node/edge/self-loop selection**) — drives the same
  fixture — extended with a self-loop, `build`'s own `retry` choice — through: clicking the `build` node selects it,
  marks its incident edges (including its self-loop) `data-incident`, and fills the detail pane with its fields and
  prompt text; clicking a point on the advance edge's rendered curve, computed off the visible path's own
  `getPointAtLength` and offset from the midpoint the label pill sits near, selects that edge — the one tier that can
  prove a click merely *near* a curve (not exactly on the thin visible stroke) actually hits it, since jsdom's
  `web:unit-test` tier does no geometry and only proves the companion-hit-path *mechanism*; clicking the self-loop
  selects it on the same terms; and clicking empty canvas clears the selection and restores the neutral hint.
- `test_diagram_geometry_matches_the_rendered_text` (#157) — every box the layout measurer sized fits the text Chromium
  actually drew, reconstructed from the rendered SVG's own advance widths rather than a canvas of its own, which would
  only prove Chromium's measurers agree with each other. It sweeps every graph blizzard ships, discovered from the tree
  so a new one is covered the day it lands; a shipped graph that renders the diagram-unavailable fallback instead is
  admitted **only** when it routes an edge out of the graph (a cross-graph `to: graph:<name>` migration target, which
  `layoutGraph` documents as the one shape it refuses — today the triage router), and is a layout regression otherwise.
