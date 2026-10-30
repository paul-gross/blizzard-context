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

Every browser scenario here needs the built bundle `blizzard hub host` serves and installed Chromium, skipping cleanly
without either or without `BLIZZARD_E2E=1`; for the board-browser module an unbuilt bundle fails loudly instead of
skipping. Except for the graphs-diagram module, every scenario also needs the sibling provisioned `blizzard-mock`
worktree. The in-process event-log function needs only the worktree, no built bundle or Chromium.

## test_board_browser_e2e

The browser half of the e2e tier: a real Chromium driven by Playwright over the served mission-control board,
`blizzard hub host` mounting the built Angular app at `/`.

- `test_board_browser_live_group_reorder_answer_and_pause` — loads the board once, never reloading, proving the status
  chip flips live over SSE as facts land and the detail drawer renders node history plus the artifact store. Its runner
  registry lists the runner `runner init` added as never connected, then online once its first pull registers it, with
  no reload. The same function groups two ready chunks through `POST /api/chunks/{id}/group`, then observes the survivor
  live in the READY lane after the merged card vanishes. It asserts decorative grips in the ranked BACKLOG and READY
  lanes and no retired board controls, then reorders the grouped survivor's whole card to the READY lane's top with real
  pointer events (the `@angular/cdk` drop list the lane arms; the drop-to-anchor arithmetic is fenced at `web:unit-test`
  with a synthesized `CdkDragDrop`), the next FILL claiming the grouped plural-pointer survivor first, both honored. It
  also proves a parked chunk's question is answered from the board and the chunk resumes to `done`. It proves a running
  chunk is paused directly from its chunk detail dock — the claim-keeping, one-chunk lever, distinct from the
  runner-level brake: the chip flips to `paused` live with no reload (the one status a pause-parked chunk's chip shows —
  [domain/work/statuses.md](../../../domain/work/statuses.md) ranks `paused` below the human-gated statuses, so the
  proof needs a chunk caught genuinely running, not already parked on a question), the chunk relocates to the WAIT/HUMAN
  column, the claim survives the runner interrupting the worker and killing only a survivor of that interrupt while
  parking the lease, the dock names who paused it, and resuming from the dock returns it to a live, progressing status.
  While the dock is open on that chunk it also asserts none of the three retired dependency-UI testids (the prerequisite
  field, Declare, Release) render. And it proves the runner's pause/resume brake, driven from the Fleet tab in a second
  page of the same browser context while the board page, never reloaded, shows the rail flip live (`data-hub-paused`,
  the stop glyph), stops and then restarts new claims (MVP criterion 11), engaged before the survivor lands because the
  landing frees the runner's only agent slot in the same tick — FILL's reconcile releases the survivor's binding — so
  from that instant the brake alone holds the remaining ready chunk in the lane.

## test_event_log_e2e

The operational event log's in-process half; its browser half runs as `tests/ui/event-log.spec.ts`.

- `test_a_verdict_less_exit_surfaces_a_critical_worker_lost_event` — the in-process half: a real mock worker's
  verdict-less exit exhausts its retry budget, the runner escalates, and the emission surfaces a critical `worker-lost`
  operational event that reads back off the live `GET /api/events` and fans out as an `event-logged` SSE frame read off
  the stream's replay tail — the runner-emit, hub-fold, read-and-fan-out chain, no browser.

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
  — and is a layout regression otherwise. Graphs that author targeted resume sessions must render that metadata, and at
  least one shipped graph must keep that branch of the proof live.
