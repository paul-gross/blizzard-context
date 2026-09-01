<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Operator-board-in-a-browser e2e scenarios (`bzh:e2e-board`)

The scenarios driving a real Chromium over the web app the hub serves — the operator board's views, its live SSE
updates, and the graph explorer.

The browser scenarios are skipped in the `gate`/`pr` single-repo checkout; the tag `release` workflow runs the full e2e
tier headless over the multi-repo checkout (Chromium via `uv run playwright install --with-deps chromium`; locally,
`uv run playwright install chromium`).

Except for the graphs-diagram and gardening-run-dialog modules, every browser scenario here needs the built bundle
`blizzard hub host` serves, the sibling provisioned `blizzard-mock` worktree (the transcript module needing only its
forge-registered repo, never spawning a runner), a local winter source, and installed Chromium, skipping cleanly without
any of them or without `BLIZZARD_E2E=1`; the in-process event-log function needs only the worktree and winter source;
for the board-browser and cost modules an unbuilt bundle fails loudly instead of skipping.

## test_board_browser_e2e

The browser half of the e2e tier: a real Chromium driven by Playwright over the served mission-control board,
`blizzard hub host` mounting the built Angular app at `/`.

- `test_board_browser_live_group_reorder_answer_and_pause` — loads the board once, never reloading, proving the status
  chip flips live over SSE as facts land and the detail drawer renders node history plus the artifact store. The same
  function proves two ready chunks are grouped from their cards in the READY lane — the ready queue is a board column,
  so a promoted chunk crosses from BACKLOG into READY rather than leaving the board — and the queue is reordered by
  dragging the grouped survivor's card to the lane's top with real pointer events (the `@angular/cdk` drop list the lane
  arms; the drop-to-anchor arithmetic is fenced at `web:unit-test` with a synthesized `CdkDragDrop`), the next FILL
  claiming the grouped plural-pointer survivor first, both honored. It also proves a parked chunk's question is answered
  from the board and the chunk resumes to `done`. It proves a running chunk is paused directly from its chunk detail
  dock — the claim-keeping, one-chunk lever, distinct from the runner-level brake: the chip flips to `paused` live with
  no reload (the one status a pause-parked chunk's chip shows —
  [domain/work/statuses.md](../../../domain/work/statuses.md) ranks `paused` below the human-gated statuses, so the
  proof needs a chunk caught genuinely running, not already parked on a question), the chunk relocates to the WAIT/HUMAN
  column, the claim survives the runner killing the worker and parking the lease, the dock names who paused it, and
  resuming from the dock returns it to a live, progressing status. And it proves the runner registry's pause/resume
  brake stops and then restarts new claims (MVP criterion 11), engaged before the survivor lands because the landing
  frees the runner's only agent slot in the same tick — FILL's reconcile releases the survivor's binding — so from that
  instant the brake alone holds the remaining ready chunk in the lane.

## test_board_cost_live_e2e

The cost/usage render half: the same served board, loaded once and never reloaded, over a chunk claimed straight through
`POST /api/fleet/routes`.

- `test_board_renders_cost_and_updates_live_over_sse` — proves the cost figures render off the live hub — the card's
  cost badge, the header's spend-today figure (`GET /api/spend?since=`), the detail dock's cost with the four token
  classes inline — and update live with no reload, the claim only a real browser over the real SSE spine can make: a
  fresh `usage.recorded` fact pushed to `POST /api/fleet/events` re-broadcasts `chunk-changed`, the `FleetLiveUpdates`
  spine invalidates the chunk read and `hubFleetSpendKey`, and card, header, and dock move in place. It also proves a
  cost-absent (crash/reap-path) row flips every figure to its `~`-marked lower bound, never a silently understated
  exact. The partial marking and the per-history-step `(node, epoch)` inline match are additionally fenced at the
  component tier: `chunk-detail-panel.spec.ts`, `board-header.spec.ts`, `board-shell.spec.ts`, `fleet-live.spec.ts`,
  `test_usage_facts_ingest.py`, `test_fleet_spend_api.py`, `test_hub_cli_status.py`.

## test_glance_board_e2e

The mobile glance board at a real ~390px width under `bzh:narrow-viewport-tier-rule` (a second consumer of that rule's
`narrow_viewport` fixture); `/board` routes to the glance shell.

- `test_the_glance_board_shows_loading_before_rows_and_never_empty_on_a_populated_fleet` — captures and holds open the
  `GET /api/chunks` read, proves the glance shell renders `needs-you-loading` and no `needs-you-empty` row while the
  read is in flight, then releases the held route, landing the row and clearing loading — the empty state never shown on
  a populated fleet.

## test_event_log_e2e

The operational event log, holding both in-process and browser-driven assertions.

- `test_a_verdict_less_exit_surfaces_a_critical_worker_lost_event` — the in-process half: a real mock worker's
  verdict-less exit exhausts its retry budget, the runner escalates, and the emission surfaces a critical `worker-lost`
  operational event that reads back off the live `GET /api/events` and fans out as an `event-logged` SSE frame read off
  the stream's replay tail — the runner-emit, hub-fold, read-and-fan-out chain, no browser.
- `test_the_events_tab_renders_filters_and_updates_live_in_the_browser` — seeds a mixed-severity feed through
  `POST /api/fleet/events`, opens the Events tab from `nav-events`, and proves rows render severity-then-recency (the
  critical row first though it arrived last), the severity filter narrows then restores, a fresh post-load event arrives
  live over SSE with no reload, and a row deep-links to its chunk.
- `test_the_events_grid_does_not_collapse_at_a_narrow_viewport` — proves the Events tab's time-first grid's
  narrow-viewport fallback: at a real ~390px width a long-message row stays bounded in height and the page gains no
  horizontal scroll.
- `test_the_rail_survives_a_reload_with_no_duplicate_or_missing_rows` — proves the board's rail Event log — a separate,
  pure-recency activity feed distinct from the Events tab — survives a reload: it seeds a mixed feed across fact
  families (a chunk transition, a question, a decision, a runner pause), confirms the rail renders a row for each over
  live SSE, reloads, and confirms the same rows remain — the on-mount `GET /api/activity` backfill re-seeding the ring
  from durable history — with no duplicate or missing row at the seam between backfill and the resumed live tee.

## test_transcript_tab_browser_e2e

The chunk board's Transcripts tab, seeding segments straight through `POST /api/fleet/transcripts` as a runner principal
— the shortest honest seeding, asserting nothing about how a segment got there — rather than through a live runner's
shipping lane, which ships disabled by default (`[transcripts] ship = false`) and is covered at the component tier by
`tests/test_transcript_pump.py` and `tests/test_transcript_drain.py`.

- `test_chunk_transcripts_tab_browser` — opens the tab on a bare-ingested chunk (no claim, lease, or transition)
  carrying one step of segments grouped under the tab's unmatched bucket rather than a history-matched step
  (`transcript-steps.spec.ts` unit-tests the grouping); it expands the first segment's collapsed-by-default thinking
  turn and a tool call to reach the sidechain nested inline under it — the card must actually open, since
  `to_contain_text` reads `textContent`, populated even behind a closed `<details>` — follows the continues-in link to
  the second segment, opens its unlinked sidechain standalone and back, then follows the continued-from link back,
  proving the tab, the lazy per-segment fetch, the thinking render, the nested-versus-standalone sidechain split, and
  the resume-seam links.

## test_graphs_diagram_browser_e2e

The graph-explorer diagram: a real Chromium over the served board visits `/graphs` and opens a minted graph's detail
from the explorer. The module needs no runner and no forge traffic — a diagram is a pure read of an immutable
`GraphView` — so it stands up only the served hub, needing just the built bundle and an installed Chromium; it skips
cleanly without `BLIZZARD_E2E=1` or without Chromium, but an unbuilt bundle fails loudly.

- `test_graphs_diagram_renders_in_the_browser` — asserts the `<fleet-graph-diagram>` SVG DAG renders against the built
  bundle from real minted data — every declared node drawn, the START marker's connector landing on the graph's own
  entry node (which node is the entry survives only as laid-out geometry), an advance edge, and the review-to-build
  back-edge derived as a `retry` edge, a structural kind no wire field carries — and names the ever-present
  `graph-diagram-fallback` path a layout failure shows instead of a broken page.
- `test_graphs_diagram_selection_in_the_browser` — proves node, edge, and self-loop selection over the same fixture
  extended with a self-loop (`build`'s own `retry` choice): clicking the `build` node selects it, marks its incident
  edges (self-loop included) `data-incident`, and fills the detail pane with its fields and prompt text; clicking a
  point on the advance edge's curve — computed off the visible path's `getPointAtLength`, offset from the label pill's
  midpoint — selects that edge, the one tier proving a click merely near a curve actually hits it (jsdom's
  `web:unit-test` does no geometry, proving only the companion-hit-path mechanism); the self-loop selects on the same
  terms; empty canvas clears the selection and restores the neutral hint.
- `test_diagram_geometry_matches_the_rendered_text` — proves every box the layout measurer sized fits the text Chromium
  actually drew, reconstructed from the rendered SVG's own advance widths rather than a canvas of its own (which would
  only prove Chromium's measurers agree with each other); it sweeps every graph blizzard ships, discovered from the tree
  so a new one is covered the day it lands, and a shipped graph rendering the diagram-unavailable fallback is admitted
  only when it routes an edge out of the graph — the one shape `layoutGraph` documents refusing, today the triage router
  — and is a layout regression otherwise.

## test_gardening_run_dialog_browser_e2e

The gardening run dialog (blizzard#399 D6), opened from the selected routine's own panel — the reachability surface
blizzard#397's routine-record panel superseded D7's provisional routines-list trigger with. Needs no runner or forge
traffic — a routine's own `run` mints a queued chunk, never executed here — so, like the graphs-diagram module, it
stands up only the served hub, needing just the built bundle and an installed Chromium.

- `test_gardening_run_dialog_browser` — mints a routine with a never-swept default scope, opens the dialog, and proves
  the delta-steering rule (D5) renders for real: the never-swept note shows and the delta radio is disabled. Mints a new
  scope through the dialog (D3), typing its slug and required description, and proves the CLI verb line names the live
  `blizzard hub routine run` invocation. Submits and proves the create-then-run ordering landed against the live hub —
  `GET /api/scopes` shows the new slug once the confirmation renders — and that the confirmation names a real
  `ch_`-prefixed chunk id and links to `/board/chunk/<id>`, rendering no board of its own. Closing the confirmation
  tears the dialog down back to the routines list.
