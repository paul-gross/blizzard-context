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
as well. This differs from `blizzard:e2e`, which drives a hub, runner and CLI together under pytest: a UI test needs
only a hub, and asserts what the board renders.

The job `upper-tiers / ui (blizzard:ui)` runs on every pull request's full suite and is a required check. Its roster:

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
- `tests/ui/migration.spec.ts::test_the_migrated_chunks_two_graph_history_renders_on_the_served_board` — a mock runner
  drives a chunk through a cross-graph migration to `done`; the served board's done card opens its detail dock showing
  the chunk id, one migration step and a per-graph label in the timeline, and the `/graphs` explorer still lists both
  graphs of the history.
