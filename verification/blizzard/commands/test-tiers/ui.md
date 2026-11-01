# `blizzard:ui` detail (`bzh:matrix-tier-ui`)

<!-- the `###` section below is machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` heading, every test-filename code span, and each `mise run` name with its paired command span are machine-checked registrations — keep them verbatim, inside the section. -->

The UI spoke of the test-tier hub [`../test-tiers.md`](../test-tiers.md). Read
[`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

### blizzard:ui

`mise run ui` (`npx playwright test --project='ui*'`) builds the board through `web-build` and runs the Playwright
package's `ui` projects: a real Chromium page against the board the test's hub serves out of
`src/blizzard/static/{hub,runner}`. It depends on `web-build` because the projects drive the built bundle, never the
sources (see [`../../pre-push.md`](../../pre-push.md#the-browser-tiers-run-the-built-bundle)). Chromium comes from
`npx playwright install chromium` in `tests/`.

The projects are generated beside the service projects. `ui` rides the default hub profile's shared hub, and a
`ui-<profile>` project exists for each `tests/ui/` subfolder named after a hub profile, riding that profile's hub with
one worker. A UI test configures its hub through a profile, never ad hoc (`bzh:service-config-is-a-profile`). Only the
`ui*` projects carry a browser: no `service-*` or harness project does, and the service tier's `--project='service-*'`
selection lists none of them. A spec imports `test` and `expect` from the harness facade, the same bans as a service
spec apply, and `page` is allowed. The facade's UI fixture (`tests/harness/ui.ts`) supplies the page's `baseURL` from
the test's hub, opens the page in the test's own tenant rather than at the board's tenant picker, and the `wideViewport`
and `narrowViewport` sizes, read from `tests/harness/viewports.json`, the one home the e2e tier's viewport fixtures read
as well. A UI test asserts what the board renders. Its hub is always real; a scenario that needs runners behind the
board steps real runner hosts through the `runnerHosts` fixture, as `tests/ui/auth/runner-federation.spec.ts` does.

The job `upper-tiers / ui (blizzard:ui)` runs on every pull request's full suite and is a required check. Its roster:

- `tests/ui/flow-lanes.spec.ts::test_the_delivery_band_shows_a_branch_line_and_collapses_live_once_it_lands` — a stepped
  real host brings two chunks to one branch line, held by the mock forge. The board loads once: the lane and card place
  lines show arrival order, then both chunks land and the lane collapses live after the lever clears. Its title opens
  the flow record in the dock with both landings.
- `tests/ui/shell.spec.ts` — the smoke that the served bundle renders the desktop board shell at the wide viewport and
  the glance board at the narrow one, rather than the placeholder the hub serves when no bundle is built. It is the
  evidence that Chromium installed, the bundle was built and served, and the fixture works.
- `tests/ui/event-log.spec.ts::test_the_events_tab_renders_filters_and_updates_live_in_the_browser` — seeds a
  mixed-severity feed through `POST /api/fleet/events`, opens the Events tab from `nav-events`, and proves rows render
  newest-first (the critical row first because it arrived last), the severity filter narrows then restores, a fresh
  post-load event from a second runner arrives live over SSE with no reload, and a row deep-links to its chunk.
- `tests/ui/event-log.spec.ts::test_the_events_grid_does_not_collapse_at_a_narrow_viewport` — proves the Events tab's
  time-first grid's narrow-viewport fallback: at a real ~390px width a long-message row stays bounded in height and the
  page gains no horizontal scroll.
- `tests/ui/event-log.spec.ts::test_activity_rail_tracks_claim_transition_and_fact_burst_across_reload` — opens the real
  board before a mock runner claims and completes a node, then pushes lease and usage facts through ingest. Checks the
  distinct claim and transition, spend refresh without extra activity rows, one row for a shared-key question
  notification, and matching durable activity identities and row count after reload.
- `tests/ui/event-log.spec.ts::test_the_rail_survives_a_reload_with_no_duplicate_or_missing_rows` — on a fresh hub,
  proves the Activity rail survives a reload: it renders every durable row on first load, the hub restarts with a fresh
  replay ring over the same store, and the reload's `GET /api/activity` backfill restores the same rows with no
  duplicate or missing one.
- `tests/ui/migration.spec.ts::test_cross_graph_migration_renders_the_two_graph_timeline_and_explorer` — a stepped
  runner drives a chunk through a cross-graph migration to `done`; the served board's done card opens its detail dock
  showing the chunk id, one migration step and a per-graph label in the timeline, and the `/graphs` explorer still lists
  both graphs of the history.
- `tests/ui/auth/login-session.spec.ts::test_browser_login_dance_and_mid_stream_session_expiry` — on the `ui-auth` hub,
  with the stub IdP's profile lever choosing who the browser resolves to: the signed-out landing shows one provider
  button; an uninvited dance is refused as `invite_only` with no `bz_session`; invited as guest through
  `POST /api/invitations` and the board's `/invite/<token>` page, the board is read-only with Promote hidden; promoted
  through `PUT /api/members/{user_id}`, a reload shows Promote; and a second page's logout through `nav-logout` sends
  the first, still-open page to `/login` with no reload.
- `tests/ui/auth/runner-federation.spec.ts::test_multi_daemon_sso_bounce` — two adopted runner hosts under one runner
  name: a sessionless browser visit to A bounces through the hub and the stub IdP into A's own session, with the
  hub-signed token never in a URL. The captured callback token is refused at B (audience-bound), refused on replay at A
  (single-use), and refused under a wrong state. After `POST /api/auth/rotate-signing-key`, a bounce into B works with
  no restart, and A's session cookie stays in the jar beside B's.
- `tests/ui/auth/runner-federation.spec.ts::test_runner_session_reacquisition_e2e` — an adopted runner restarted in
  place invalidates an open tab's session; with no navigation or reload, the panel's own stream reconnect is refused and
  the session-recovery seam re-federates through `GET /api/auth/login`, ending with a fresh runner session cookie.
- `tests/ui/auth/runner-federation.spec.ts::test_one_sign_in_at_a_registered_host_reaches_both_runners_pages` — a
  registered host running two runners is the panel's one sign-in client: the legacy `/runners/<id>/board` link bounces
  to `authorize` with the host id as `client`, exactly one host session cookie results, and the second runner's board
  loads with no second bounce.
- `tests/ui/project-lens.spec.ts` — `test_project_lens_deep_links_resolve_in_the_browser`. The board's project lens in a
  real router against the hub's own project resolution. Creates a project, then moves it to a new slug. Proves a deep
  link to `/p/default/board` opens the board under the `default` project's lens; a link naming the project by the slug
  it has left, or by its id, is rewritten in place to its current slug; and a link naming no project of the tenant opens
  the same view on All, with a notice.
- `tests/ui/actions/gardening-run-dialog.spec.ts` — `test_gardening_run_dialog_browser`. The gardening run dialog,
  opened from the selected routine's own panel, on the `actions` hub, since the routine's graph names a test action.
  Mints a routine with a never-swept default scope, links a second scope into its related set ahead of time, and mints a
  third scope left unlinked. Proves the dialog offers only the related set, with the unlinked scope and the mint escape
  hatch both absent; that the never-swept note shows and the delta radio is disabled; that submitting on the linked
  scope lands the run against it, read back from the hub; and that the confirmation names a real `ch_`-prefixed chunk
  id, links to `/p/default/board/chunk/<id>`, renders no board of its own, and closes back to the routines list.
- `tests/ui/transcript-tab.spec.ts` — `test_chunk_transcripts_tab_browser`. The chunk board's Transcripts tab, over
  segments seeded straight through `POST /api/fleet/transcripts` as a runner principal rather than a live runner's
  shipping lane, which ships disabled by default and is covered at the component tier by `tests/test_transcript_pump.py`
  and `tests/test_transcript_drain.py`. Opens the tab on a bare-issued chunk, with no claim, lease or transition, so its
  one step of segments groups under the unmatched bucket. Expands the first segment's collapsed-by-default thinking
  turn, and opens a tool call to reach the sidechain nested inline under it, since `toContainText` reads `textContent`,
  populated even behind a closed `<details>`. Follows the continues-in link to the second segment, opens its unlinked
  sidechain standalone and back, then follows the continued-from link back.
- `tests/ui/triage-history.spec.ts` — `test_triage_migration_selects_transcript_and_artifact`. The packaged default
  graph routes a claimed triage step into a lane. Syncs the packaged graphs, then claims, mints a lease, completes on
  `basic` with a `triage-findings` artifact, and ships a transcript segment, all as a runner; a hub read confirms the
  authored-edge migration and the artifact carry the triage step's origin and epoch. Opens the Node history tab, selects
  the migration, and reads the triage transcript and artifact at the wide and the narrow viewport, including the narrow
  drill-down's Back control, and fails on any failed API response.
- `tests/ui/board-cost-live.spec.ts` — `test_board_renders_cost_and_updates_live_over_sse`. The board, loaded once and
  never reloaded, over a chunk claimed straight through `POST /api/fleet/routes`, with spend shipped as `usage.recorded`
  facts to `POST /api/fleet/events` as a runner. Proves the card's cost badge, the header's spend-today figure
  (`GET /api/spend?since=`) and the detail dock's cost with the four token classes inline update live off the event
  stream; that a row with neither a billed nor an estimated amount flips every figure to its `+`-marked lower bound,
  never a silently understated exact; and, on a second, subscription-only chunk, that an estimate renders as one
  `~`-marked figure on the card and the dock, folds into the header's fleet total under both marks, and marks no chunk
  partial. The partial marking and the per-step inline match are also fenced in `web:unit-test` and
  `blizzard:component-test`.
- `tests/ui/glance-board.spec.ts` —
  `test_the_glance_board_shows_loading_before_rows_and_never_empty_on_a_populated_fleet` and
  `test_the_glance_board_shows_a_cost_estimate_never_a_plain_billed_zero`. The mobile glance board at the narrow
  viewport under `bzh:narrow-viewport-tier-rule`, where `/board` routes to the glance shell. The first steps a runner
  host until a verdict-less build escalates its chunk to `needs_human`, then captures and holds open the
  `GET /api/chunks` read, proves the glance shell renders `glance-list-loading` and no `glance-list-empty` row while the
  read is in flight, and releases it, landing the card and clearing loading: the empty state is never shown on a
  populated fleet. The second claims a chunk as a runner and ships it a subscription-only `usage.recorded` fact, an
  estimate with no billed cost, and proves the "Fleet spend · today" panel and the running chunk's card both render the
  one `~`-marked figure, never a plain billed `$0.00`.
- `tests/ui/graphs-diagram.spec.ts` — `test_graphs_diagram_renders_in_the_browser`,
  `test_graphs_diagram_selection_in_the_browser` and `test_diagram_geometry_matches_the_rendered_text`. The graph
  explorer's diagram over a live hub. The first opens a minted build, review and deliver graph from `/graphs` and proves
  its SVG DAG draws every declared node, the START connector lands on the entry node, an advance edge renders, and the
  review-to-build back-edge is derived as a `retry` edge. The second proves node, edge and self-loop selection over the
  same graph, clicking a point on a rendered curve off its label's midpoint, since jsdom cannot hit-test geometry; empty
  canvas clears the selection. The third syncs the packaged graphs, enumerates them from `GET /api/graphs`, and proves
  each renders a diagram, or the fallback only when an edge leaves the graph, and that a graph authoring a targeted
  resume renders its `resume:<node>` meta line. The measurer contract the boxes are sized by is held by
  `web:shell-sweep`.
- `tests/ui/runner-panel-live.spec.ts` — `test_runner_panel_updates_live_over_sse_with_no_reload`. The runner's own
  panel, served by a real `blizzard-runner host` the test steps, its page pointed at the host's URL rather than the
  hub's. Loads the panel's board at `/board` once, never reloading, over an empty board; then promotes a chunk and steps
  the host once, and the chunk's card must arrive well inside the panel's one-minute poll backstop, so the publish,
  stream, `RunnerLiveUpdates` registry and re-read chain alone can have put it there. The host then steps the chunk to
  `done`, and the card settles in the Done lane with no live worker line.
- `tests/ui/board-browser.spec.ts` — `test_board_browser_live_group_reorder_answer_and_pause`. The mission-control board
  over a runner host the test steps, loaded once and never reloaded until its own `?chunk=` URL is mounted fresh.
  Promotes three chunks from the board and proves decorative grips and no retired controls in the backlog and ready
  lanes; groups two through `POST /api/chunks/{id}/group` and watches the merged card vanish and the survivor carry both
  pointers' chips live; drags the survivor's card to the ready lane's top with real pointer moves, and proves the queue
  and the next claim honour both. The survivor parks on a question, crosses to the waiting lane live, is answered from
  the dock, and runs to `done`, the dock then rendering its node history and artifacts and linking to the chunk page's
  Artifacts tab. The runner's hub brake, set and released from the Fleet tab in a second page, holds the remaining ready
  chunk through four host passes and then lets it be claimed; that chunk is paused from the dock, keeping its claim and
  naming who paused it, and resumed. The graph ends at review, and the worker's branch and its `LANDED.md` are read back
  from the runner host's own origin: the host's origins are not the hub forge's repositories, so this entry does not
  prove landing through the forge — a pull request opened and merged onto `main`. The dock's geometry is held by
  `web:shell-sweep`.
