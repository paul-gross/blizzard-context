# `web:shell-sweep` detail (`bzh:matrix-command-web-shell-sweep`)

<!-- the `###` section below is machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` heading, spec-filename code spans, and `npm run` script names are machine-checked — keep each verbatim, inside the section. -->

The detail spoke for the real-Chromium sweep and its checked spec roster, under the Angular workspace hub,
[`../web.md`](../web.md). Read [`../../../blizzard.md`](../../../blizzard.md) first for the short command and the
method-id inventory; [`../../commands.md`](../../commands.md) routes to the other methods' detail.

### web:shell-sweep

<!-- The `*.shell-sweep.spec.ts` names cited in this section are a bidirectional machine-checked roster against the on-disk set under `web/projects/` — every cited name must stay cited here, every new spec file must be added, and no numeral or number-word count of the set may be stated anywhere. -->

`npm run shell-sweep` in `web/` (`web/scripts/shell-sweep.js`) — the tooled proof behind the classes of claim jsdom
cannot evaluate. One class is the narrow-viewport tier rule (`bzh:narrow-viewport-tier-rule`, owner
[`../../tier-rules.md`](../../tier-rules.md)) for components reachable from the mobile shell's bottom nav: jsdom,
`web:unit-test`'s environment, parses `@container` and media-query rules without evaluating them and never lays out or
clamps text, so no jsdom spec can prove a real collapse. The other is a computed-style claim no viewport width changes —
most concretely a `:hover`/`:focus-visible` rule, which jsdom parses without resolving against a pointer. Both classes
get the same fix: shell-sweep specs run under `@angular/build:unit-test`'s real-browser mode
(`--browsers=ChromiumHeadless`, backed by the `@vitest/browser-playwright` and `playwright` dev dependencies), where
layout, container/media collapse, line-clamping, computed style, and hit-testing are genuine.

Each spec is named `*.shell-sweep.spec.ts`, mounts a real component tree, and is excluded from its project's default
`ng test` run via `web/angular.json`'s per-project `test.exclude`, because jsdom cannot run it. The roster:

- `app-nav-menu.shell-sweep.spec.ts` and `app-header.shell-sweep.spec.ts` cover the shared header shells — `hub`'s
  `BoardHeader` plus `AppNavMenu`, and `runner`'s `AppHeader`. At widths 1400px down to 320px, straddling every declared
  header breakpoint, and — runner only, the one content-dependent header width — usernames from authless to 64
  characters, the profile menu trigger must sit fully inside the viewport, `elementFromPoint` at its center must hit
  inside it, with no horizontal overflow and no page error. The sweep's shape follows `BoardHeader`'s geometry: a stat
  strip and trailing cluster sharing equal flex-shrink priority squeeze the menu near the strip's 1150px breakpoint —
  which is why the already-clipping stat strip carries an outsized `flex-shrink` (`board-header.ts`'s `.stats` rule),
  and why the swept widths straddle that breakpoint. The specs are proven able to fail by reverting `BoardHeader`'s
  `.trailing` shrink fix (`flex: 0 1 auto; min-width: 0`, `board-header.ts`), which reproduces the off-screen-menu
  symptom.
- `app-nav.shell-sweep.spec.ts` covers the runner's top tab strip (`AppNav`). Its `KitTabStrip`/`KitTab` chrome carries
  no `@container` rule, so the claim is narrower: from 1400px to 320px both static labels render and the strip never
  overflows its own width.
- `chunk-page-layout.shell-sweep.spec.ts` covers the hub chunk detail page, reached from the mobile board — the General
  tab, whose `@media (min-width: 720px)` grid puts work item and issues in a shared left column with node history beside
  them, and the Transcripts tab — routed for real via `RouterTestingHarness` under a height-capped stand-in for the app
  `.layout`, since a standalone mount cannot see these regressions. Its cases:
  - General tab: at 390px and 320px the work-item, issues, and node-history panels must genuinely stack — distinct
    `top`s at a common `left` — with no horizontal overflow; at 1024px node history's `left` must sit at or past the
    work-item column's `right`, while work item and issues keep distinct `top`s in their shared column. Proven able to
    fail by moving node history's explicit grid placement (`grid-column: 1; grid-row: 3`) into the work-item/issues
    column.
  - Transcripts-tab stacking: the nav-beside-viewer split collapses below `@media (min-width: 720px)` — with one stubbed
    segment open at 390px, the step nav's `top` must sit above the segment body's, with no horizontal overflow; proven
    able to fail by forcing `.tx-tab`'s base `flex-direction` to `row`.
  - Scroll: serves a 60-turn segment at 390×700 — the tab's box must stay bounded by the viewport, and `.tx-view` must
    genuinely scroll (`scrollTop` round-trips past 0); proven able to fail by deleting the transcripts container's
    `:host { display: contents }`, which leaves the tab's box unbounded. This case polls a bounded `pumpUntil` instead
    of the shared `settle()`: under zoneless stability a query enabled after the first stable report makes
    `whenStable()` hang though the DOM rendered, while `pumpUntil` still throws if content never renders.
  - Centering: renders the permission notice — its absolutely-centered status line must center on the tab's box, not the
    browser viewport, measured as the nearer center since the host fills the tab body; proven able to fail by deleting
    `chunk-transcripts-tab.ts`'s `:host { position: relative }`.
  - Error status: `fleet-kit-async-state`'s absolutely-centered `placement="center"` must resolve against the back row's
    sibling rather than paint across the 44px back bar, and the issue pane's error text must stay inside its section at
    phone widths.
- `chunk-artifacts-tab-layout.shell-sweep.spec.ts` covers the hub Artifacts tab's composed chain through a real router,
  proving `.art-tab`'s `height: 100%` resolves against a definite containing block and an overflowing artifact nav list
  genuinely scrolls.
- `chunk-facts-alignment.shell-sweep.spec.ts` covers the chunk detail facts/usage table pair — `ChunkFacts` with
  `ChunkTokenBreakdown` projected as its sibling `<dl class="kv">` — a geometry check that the shared
  `--kv-label-col`/`--chunk-facts-pad` custom properties keep the tables' columns aligned when a long wrapped Runner
  value gives them different content widths.
- `hover-tint.shell-sweep.spec.ts` covers the `--tint-hover`/`--tint-selected` tokens where they compose —
  `BoardCardComponent`, `ChunkTimeline`'s history rows, and `ChunkArtifacts`'s artifact rows — a computed-style proof: a
  real Playwright pointer (`userEvent.hover`) must distinguish hovered from resting `background-color` and, on the board
  card and `ChunkTimeline`'s `selected` row, from a selected-but-unhovered row's. It also pins that hovering an
  `.artifact-link` washes its row while a contentless `.artifact-plain` row stays unwashed. The tokens live in the
  global stylesheet `web/projects/fleet/src/lib/design/tokens.css`, loaded by every app build but by no standalone
  component test, so the spec reads the sheet's real text via `commands.readFile` — the vitest browser command exposed
  for exactly this — and injects it as a `<style>` element. Every assertion is proven able to fail by reverting its own
  rule: the `:hover` tint backgrounds in `board-card.ts` and `chunk-timeline.ts`, the selected-row backgrounds pointed
  at `--tint-hover` instead of `--tint-selected`, and `chunk-artifacts.ts`'s `:has()` re-scoped to
  `.artifact-plain:hover`.
- `local-panel-mobile.shell-sweep.spec.ts` covers the runner's mobile chunk list — `LocalPanelMobile` then `ChunkCard`,
  the component the narrow-viewport tier rule actually names, mounted beneath the persistent `MobileTabBar` (the rule's
  "mobile shell's bottom nav"). With five work items on a card, at 390px and 320px the `-webkit-line-clamp: 2` `.wi`
  lines must genuinely stack — distinct `top`s per line — with no horizontal overflow and no page error; proven able to
  fail by forcing `.wi` back to `display: inline` inside a `white-space: nowrap` container, which collapses every line
  onto one. The desktop `LocalPanelLayout`/`ChunkRow` pair is never reached below the mobile breakpoint and deliberately
  has no shell-sweep spec.
- `chunk-detail-page.shell-sweep.spec.ts` covers the runner-local chunk detail page (`ChunkDetailPage`): at 390px and
  320px it walks the General, Artifacts, and Transcripts tabs, each of which must stack its sections with no horizontal
  overflow — exercising the General tab's `@media (min-width: 720px)` collapse and a long unbroken artifact key. Its
  takeover case mounts a `needs_human` chunk with a wrapped takeover command and raw resume fallback.
  `fleet-kit-panel`'s body clips horizontally (`overflow-x: hidden`), so no takeover CSS can widen the tab; the claim is
  the opposite — at 320px each over-wide command must be reachable by scrolling its own box (`scrollLeft` round-trips
  past 0), or the clip amputates the string the operator must paste whole. Proven able to fail per half by dropping
  `overflow-x: auto` from `.takeover .cmd` and `.raw-fallback .cmd`.
- `runner-view.shell-sweep.spec.ts` covers the runner registry's rate-limit pace bars (`RunnerPanelView`): a row
  carrying two sampled windows, each a stacked utilization/elapsed bar pair, must at the board right rail's ~390px width
  stack both windows' bars within the fleet panel's width, with no overflow and no page error.
- `transcript-panel.shell-sweep.spec.ts` covers the runner's `TranscriptPanel` in closed-lease-from-hub states: at 390px
  and 320px a truncated archived read must render the archived badge and truncation banner (`transcript-archived-badge`,
  `transcript-truncated`), and a hub-unreachable read (`hub_unreachable: true`) its degrade banner
  (`transcript-hub-unreachable`), each with no element or panel overflow; proven able to fail by adding
  `white-space: nowrap` to `.degrade-banner`.
- `session-recovery-view.shell-sweep.spec.ts` covers `SessionRecoveryView`, which the runner app renders in place of the
  whole panel when a federation bounce could not complete silently: at 390px and 320px its headline/detail block and
  retry control must render with no view-wide horizontal overflow; proven able to fail by adding `white-space: nowrap`
  to `.detail`.
- `board-card-control-row.shell-sweep.spec.ts` covers `BoardCardComponent`'s control row: mounted as a `not_ready` card
  with `canControl` true — the one status PROMOTE and DELETE render on together, and so the denser case than `ready`'s
  DELETE-alone row — at the full 390px and 320px viewport widths (not a board column's own narrower fractional share of
  one) the two controls must sit side by side, non-overlapping, with DELETE's own right edge staying inside the card's,
  rather than collapsing into an overlapping or overflowing pair; a real CSS flex-row layout claim jsdom cannot make.
