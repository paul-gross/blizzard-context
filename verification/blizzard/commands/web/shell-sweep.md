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
cannot evaluate. Why jsdom cannot, and when a sweep run is admissible as a visual change's evidence, are
`bzh:visual-change-needs-a-render`'s (owner [`../../tier-rules.md`](../../tier-rules.md)); the classes that route here
are the narrow-viewport tier rule (`bzh:narrow-viewport-tier-rule`, same owner), a computed-style claim no viewport
width changes — most concretely a `:hover`/`:focus-visible` rule, which jsdom parses without resolving against a pointer
— and any other visual change. Every class gets the same fix: shell-sweep specs run under `@angular/build:unit-test`'s
real-browser mode (`--browsers=ChromiumHeadless`, backed by the `@vitest/browser-playwright` and `playwright` dev
dependencies), where layout, container/media collapse, line-clamping, computed style, and hit-testing are genuine.

No gate runs the sweep: it is in no CI workflow, in no `mise` task, and not in `blizzard:gate`, and its specs are
excluded from `ng test` by design. Every run of it is therefore one you invoke — run it when a change owes render
evidence, and re-run it over the roster whenever a swept surface moves, since nothing else will.

Each spec is named `*.shell-sweep.spec.ts`, mounts a real component tree, and is excluded from its project's default
`ng test` run via `web/angular.json`'s per-project `test.exclude`, because jsdom cannot run it. The roster:

- `app-nav-menu.shell-sweep.spec.ts` and `app-header.shell-sweep.spec.ts` cover the shared header shells — `hub`'s
  `BoardHeader` plus `AppNavMenu`, and `runner`'s `AppHeader`. At widths 1400px down to 320px, straddling every declared
  header breakpoint, and — runner only, the one content-dependent header width — usernames from authless to 64
  characters, the profile menu trigger must sit fully inside the viewport, `elementFromPoint` at its center must hit
  inside it, with no horizontal overflow and no page error. The sweep's shape follows `BoardHeader`'s geometry: a stat
  strip and trailing cluster sharing equal flex-shrink priority squeeze the menu near the strip's 1150px breakpoint —
  which is why the already-clipping stat strip carries an outsized `flex-shrink` (`board-header.css`'s `.stats` rule),
  and why the swept widths straddle that breakpoint. The specs are proven able to fail by reverting `BoardHeader`'s
  `.trailing` shrink fix (`flex: 0 1 auto; min-width: 0`, `board-header.css`), which reproduces the off-screen-menu
  symptom. `app-header.shell-sweep.spec.ts` additionally sweeps the connection cell's `degraded` state — the longest
  string that cell ever renders — over the same width range with a fixed username, asserting the cell reads `degraded`,
  the profile menu stays on-viewport, and the header itself carries no horizontal overflow.
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
    `chunk-transcripts-tab.css`'s `:host { position: relative }`.
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
  rule: the `:hover` tint backgrounds in `board-card.css` and `chunk-timeline.css`, the selected-row backgrounds pointed
  at `--tint-hover` instead of `--tint-selected`, and `chunk-artifacts.css`'s `:has()` re-scoped to
  `.artifact-plain:hover`.
- `local-panel-mobile.shell-sweep.spec.ts` covers the runner's mobile chunk list — `LocalPanelMobile` then `ChunkCard`,
  the component the narrow-viewport tier rule actually names, mounted beneath the persistent `MobileTabBar` (the rule's
  "mobile shell's bottom nav"). With five work items on a card, at 390px and 320px the `-webkit-line-clamp: 2` `.wi`
  lines must genuinely stack — distinct `top`s per line — with no horizontal overflow and no page error; proven able to
  fail by forcing `.wi` back to `display: inline` inside a `white-space: nowrap` container, which collapses every line
  onto one. The desktop `LocalPanelLayout`/`ChunkRow` pair is never reached below the mobile breakpoint and deliberately
  has no shell-sweep spec.
- `chunk-detail-page.shell-sweep.spec.ts` covers the runner-local chunk detail page (`ChunkDetailPage`): at 390px and
  320px it walks all four tabs — General, Node history, Artifacts, Transcripts — each checked for no horizontal
  overflow, exercising the General tab's `@media (min-width: 720px)` collapse and a long unbroken artifact key. Only
  General's own sections (`section-`-prefixed testids) are checked for stacking; Node history, Artifacts, and
  Transcripts — the last rendered through the shared `fleet-chunk-transcripts-container` — are each one nav-plus-viewer
  pane rather than a stack of independent panels, so the overflow check alone stands in for that tab. Its takeover case
  mounts a `needs_human` chunk with a wrapped takeover command and raw resume fallback. `fleet-kit-panel`'s body clips
  horizontally (`overflow-x: hidden`), so no takeover CSS can widen the tab; the claim is the opposite — at 320px each
  over-wide command must be reachable by scrolling its own box (`scrollLeft` round-trips past 0), or the clip amputates
  the string the operator must paste whole. Proven able to fail per half by dropping `overflow-x: auto` from
  `.takeover .cmd` and `.raw-fallback .cmd`.
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
- `routine-panel.shell-sweep.spec.ts` covers the gardening tab's routine panel (`FleetRoutinePanel`) — the record,
  strategy, trend, measurement, and last-swept blocks, mounted with a representative view model whose last-swept row
  carries two long per-repository revision hashes. At 1280px, 390px, and 320px every block must genuinely stack —
  distinct `top`s — with no horizontal overflow of the panel itself, and the last-swept table's own `scrollWidth` must
  stay within its `clientWidth` rather than the long hashes forcing it wider. Proven able to fail by dropping
  `table-layout: fixed`/`overflow-wrap: anywhere` from `routine-panel.css`'s table rule, which lets a long hash push the
  table past its section. Gardening sits in the hub's mobile bottom tab bar, so the narrow widths bind
  (`bzh:narrow-viewport-tier-rule`).
- `gardening-routines-page.shell-sweep.spec.ts` covers the container's own `.gr-layout` list-beside-panel grid, which
  `routine-panel.shell-sweep.spec.ts` never mounts since it stands `FleetRoutinePanel` up alone. At 1280px the list and
  panel must sit side by side; at 390px and 320px `.gr-layout`'s `@media (max-width: 480px)` rule must collapse them
  into a single stacked column, with no horizontal overflow of the layout itself. Proven able to fail by dropping that
  media rule from `gardening-routines-page.css`. Gardening sits in the hub's mobile bottom tab bar, so the narrow widths
  bind (`bzh:narrow-viewport-tier-rule`).
- `graph-detail.shell-sweep.spec.ts` covers the graphs container/presentational split's `GraphDetailLifecycle`, mounted
  directly with plain inputs. Its action-error line and entry line — blocks that were direct children of `.body`'s own
  `flex-direction: column; gap: 10px` (`graph-detail.css`) before the split — must genuinely stack with a real gap,
  proving `graph-detail-lifecycle.css`'s own `:host` flex column reproduces that spacing now that the container hands
  them only one flex slot; proven able to fail by setting that `:host`'s `gap` to `0`.
- `kit-dialog.shell-sweep.spec.ts` covers `KitDialog`, the workspace's first modal shell: the scrim genuinely covers the
  full viewport (`getBoundingClientRect` against `window.inner*`, not merely the panel's own box), the panel centres
  itself (near-equal left/right gaps) and its own `.body` scrolls a tall projection while the page behind it does not
  (`scrollTop` round-trips on the panel, stays `0` on `document.scrollingElement`), and
  `CdkTrapFocus`/`cdkTrapFocusAutoCapture` keep focus inside the panel on open and across eight real `Tab` presses —
  layout and real focus-management claims jsdom cannot make.
- `gardening-run-dialog.shell-sweep.spec.ts` covers the gardening run dialog's own three fields, mounted directly with
  plain inputs, at the 390px and 1024px widths the dialog is reachable at: the scope field's radio rows must genuinely
  stack, the footer's Cancel/Run buttons must sit side by side with Run's own right edge staying inside the panel's, the
  delta baseline block's finding-set-id line must sit above its per-repo landed-since lines, and the new-scope
  near-match warning must render below both new-scope inputs rather than overlapping them — real CSS layout claims jsdom
  cannot make.
- `garden-runs.shell-sweep.spec.ts` covers the gardening runs-and-findings tab's two presentational components, each
  mounted directly with plain inputs. `FleetRunList`'s escalated row, at 390px, must carry a genuinely different
  computed `background-color` from a normal row, while its `border-left-color` must equal the normal row's, since the
  left edge belongs to selection alone — computed-style claims no viewport width changes, since jsdom would accept the
  `rl-body--escalated` class name without ever evaluating it against `run-list.css`; proven able to fail by dropping
  that rule's `background` declaration. `FleetRunDelta`, at 390px, must stack its two finding-set blocks with distinct
  `top`s, and, within the first set, stack its added/observed/gone groups in that order with no overlap and no
  horizontal overflow of the delta itself; proven able to fail by forcing `run-delta.css`'s `.rd-groups`
  `flex-direction` to `row`. Gardening sits in the hub's mobile bottom tab bar, so the narrow width binds
  (`bzh:narrow-viewport-tier-rule`).
- `gardening-proposals-page.shell-sweep.spec.ts` covers the garden proposal docket container's own `.gp-layout`
  list-beside-panel grid: the list and panel sit side by side above 480px, and genuinely collapse into a single stacked
  column at 390px and 320px, with no horizontal overflow of the layout itself, and the detail panel's own evidence-row
  locus (`.pp-finding-locus`) wraps a long, unbroken path rather than widening the panel past its column.
- `gardening-proposal-pass-dialog.shell-sweep.spec.ts` covers the Pass dialog's own view, mounted directly with plain
  inputs: at 390px and 1024px the footer's Cancel/Pass buttons must genuinely sit side by side, neither overflowing the
  dialog panel.
- `gardening-proposal-accept-dialog.shell-sweep.spec.ts` covers the Accept dialog's own view, mounted directly with
  plain inputs: at 390px and 1024px the mint/decline radiogroup must genuinely stack its two options, the decline reason
  field must render below them once decline is chosen, and the footer's Cancel/Accept buttons must sit side by side,
  neither overflowing the dialog panel.
- `gardening-findings-triage.shell-sweep.spec.ts` covers the findings triage list (`FleetFindingList`), mounted directly
  with plain inputs. With every row selected through the real select-all checkbox (never by poking the component's own
  selection signal), the bulk bar's own buttons must, at 1400px, 390px, and 320px, stay inside the viewport and never
  overlap each other, and the list itself must carry no horizontal overflow — real CSS layout claims jsdom cannot make.
  Separately, a `gone`-flagged row must carry a genuinely different computed `background-color` from a plain row, while
  its `border-left-color` must equal the plain row's, since the left edge belongs to selection alone — computed-style
  claims no viewport width changes, since jsdom would accept the `fl-body--gone` class name without ever evaluating it
  against `finding-list.css`. Gardening sits in the hub's mobile bottom tab bar, so the narrow widths bind
  (`bzh:narrow-viewport-tier-rule`).
- `gardening-finding-triage-dialog.shell-sweep.spec.ts` covers the findings triage bulk-action dialog's own view,
  mounted directly with plain inputs, once per verb that carries a distinct field shape. At 1400px, 390px, and 320px the
  note field must render without overflowing the dialog panel, the `supersede` verb's extra absorbing-finding field must
  render below or beside the note field with no overlap, and the footer's Cancel/submit buttons must sit side by side
  without overflowing the panel — real CSS layout claims jsdom cannot make.
- `board-card-blocked.shell-sweep.spec.ts` covers `BoardCardComponent`'s blocked marking: mounted once with no
  `blockedOn` and once with one, at 800px (wider than any real board column) and at 390px/320px
  (`bzh:narrow-viewport-tier-rule`), the marking must render directly below the status row without moving the status's
  own position and without its own right edge overflowing the card — a real CSS layout claim jsdom cannot make, since
  `ChunkBlocked` mounts outside the card's own open button (a nested interactive element inside it is invalid HTML).
- `gardening-page-grids.shell-sweep.spec.ts` covers the three gardening sub-tabs that arrived with the five-way tab
  split and share one claim rather than each carrying its own file — Scopes, Runs, and Findings — each scoping the same
  `grid-template-columns` master/detail split and the same `@media (max-width: 720px)` collapse that Routines and
  Proposals each already carry a sweep for. Table-driven over the three pages: above 720px the list and detail sit side
  by side, and at 700px, 390px, and 320px they genuinely stack with no horizontal overflow of the layout — real CSS
  layout claims jsdom cannot make. Gardening sits in the hub's mobile bottom tab bar, so the narrow widths bind
  (`bzh:narrow-viewport-tier-rule`).
- `chunk-detail-header.shell-sweep.spec.ts` covers the dock header's action row, mounted with every control live at once
  — a routed, pausable, blocked chunk with a long runner identity — at 800px (wider than any real dock share) and at
  390px/320px (`bzh:narrow-viewport-tier-rule`): none of Pause, Complete, Delete, the prerequisite field, Declare,
  Release, the route/Detach group, or the close button may overflow the header's own right edge — a real CSS flex-wrap
  layout claim jsdom cannot make. The spec asserts its swept selector list against an exact count, so a control added to
  the row without being added to the list fails the fixture rather than passing unmeasured.
- `chunk-artifact-structured.shell-sweep.spec.ts` covers the two structured readings of a garden asset artifact —
  `ChunkArtifactDelta` and `ChunkArtifactSurvey` — mounted through `ChunkArtifactBody` inside a height-capped flex
  column. Each must bound itself at the cap and scroll its own overflow (`.rd-body`'s `scrollHeight` exceeding its
  `clientHeight`, its own bottom staying inside the capped page) rather than growing to its content, proving the
  flex/`min-height: 0` chain that runs from the body's host through the renderer's host and `.fd`/`.fs` column to the
  disclosure shell actually resolves. Both shapes are swept, never one: they render in the same slot, and a sizing rule
  naming only one of them is exactly the defect this catches. Proven able to fail by dropping either host tag from
  `chunk-artifact-body.css`'s shared sizing rule.
- `graph-explorer-list.shell-sweep.spec.ts` covers the explorer's two row levels once rebuilt on `KitSelectRow`, with
  the first lineage genuinely expanded so the nested level lays out. At 520px, 390px, and 320px a long graph name, its
  version count, its right-anchored short id, the version badge, and the retired filter chip must all stay inside the
  list's own right edge — a real layout claim, since both levels now render their content projected into another
  component's button rather than into a box this stylesheet owns.
- `chunk-neighborhood.shell-sweep.spec.ts` covers `ChunkNeighborhood`'s satisfied-vs-unmet edge marking, mounted
  directly with plain inputs, reading `design/tokens.css`'s real text and injecting it as a `<style>` element the way
  `hover-tint.shell-sweep.spec.ts` does, since a standalone component test never loads the global stylesheet its
  `var(--green)`/`var(--amber-hi)` badge colors resolve against. A satisfied prerequisite's badge must carry a genuinely
  different computed `color` from an unmet one's — a computed-style claim no viewport width changes, since jsdom would
  accept `[tone]="satisfiedTone(n)"` without ever resolving it against `kit-badge.ts`'s color ladder. Separately, at
  390px and 320px several neighbors in each direction must wrap onto their own lines within the panel's own right edge,
  with no horizontal overflow — the surface this mounts on is reachable from the mobile board
  (`bzh:narrow-viewport-tier-rule`).
- `finding-fact-timeline.shell-sweep.spec.ts` covers the finding detail panel's fact-chain timeline
  (`FleetFindingFactTimeline`), mounted directly with plain inputs: at 390px and 320px a long, unbroken triage note and
  an actor id must render for every fact row with no horizontal overflow — gardening sits in the hub's mobile bottom
  tab bar, so the narrow widths bind (`bzh:narrow-viewport-tier-rule`).
