# Angular workspace command detail (`bzh:matrix-command-web`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` headings, test/spec-filename code spans, and `npm run` script names are machine-checked — keep each verbatim, inside its own section. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### web:typecheck

`npm run build` in `web/` — a real AOT compile of both Angular apps, the type check `web:unit-test`'s esbuild-based
vitest never performs. Run it after any change that adds or narrows a required field on a shared interface, or that
changes an exported function or method signature: the construction sites those changes break stay green under every
other web tier.

### web:client-drift

`npm run generate:client` in `web/` — openapi-ts codegen from `openapi/{hub,runner}.openapi.json` — then fail on any
unstaged diff in `web/` ([`../../../standards/frontend.md`](../../../standards/frontend.md), `bzh:generated-client`).
The check is a working-tree-vs-index `git diff`, not working-tree-vs-`HEAD` — a regeneration already `git add`ed passes.
The Python half regenerates the specs via `uv run blizzard-export-openapi --out-dir openapi` and fails the same way on
an unstaged diff in `openapi/`.

### web:structural-gate

`npm run structural-gate` in `web/` (`web/scripts/structural-gate.js`); every check in it is live.

One check is a `max-lines` ceiling — the ~400-line cap — over every Angular component file
([`../../../architecture/frontend-structure.md`](../../../architecture/frontend-structure.md),
`bzh:frontend-container-presentational`), with no exemptions — `MAX_LINES_EXEMPT_FILES` is empty.

The other check is a real-timer sweep over the specs the `test` target actually runs, failing a
`setTimeout`/`setInterval` whose delay is a non-zero integer literal — a real second spent inside the merge gate, and a
window guessed rather than chosen. Its boundaries: a delay held in a variable or expression is outside the pattern;
`setTimeout(…, 0)` is the macrotask-flush idiom and deliberately unmatched; and `*.shell-sweep.spec.ts` is out of scope,
since a real-Chromium frame wait is `web:shell-sweep`'s method. A genuinely time-driven spec is named in
`REAL_TIMER_EXEMPT_FILES` with its reason — today only `demo-director.spec.ts`, whose waits poll a real router harness
at the kiosk tour's own measured cadence. The tree is clean of the real-timer shape today, so the check carries a
fixture self-test (`assertRealTimerDetectorWorks`, must-catch and must-pass shapes) that refuses to run the gate at all
if the detector stops classifying (`bzh:case-pins-its-own-name`); the `max-lines` check fires on real files and needs no
equivalent.

### web:shell-sweep

<!-- The `*.shell-sweep.spec.ts` names cited in this section are a bidirectional machine-checked roster against the on-disk set under `web/projects/` — every cited name must stay cited here, every new spec file must be added, and no numeral or number-word count of the set may be stated anywhere. -->

`npm run shell-sweep` in `web/` (`web/scripts/shell-sweep.js`) — the tooled proof behind two classes of claim jsdom
cannot evaluate. The first class, the method's original reason to exist, is the narrow-viewport tier rule
(`bzh:narrow-viewport-tier-rule`, [`../tier-rules.md`](../tier-rules.md)) for components reachable from the mobile
shell's bottom nav: jsdom — `web:unit-test`'s environment — parses `@container` and media-query rules without evaluating
them and never lays out or clamps text, so no jsdom spec can prove a real collapse. The second class is a computed-style
claim no viewport width changes — most concretely a `:hover`/`:focus-visible` rule, since jsdom parses a pseudo-class
selector without ever resolving it against a simulated pointer. Both classes get the same fix: shell-sweep specs run
under `@angular/build:unit-test`'s real-browser mode — `--browsers=ChromiumHeadless`, backed by the
`@vitest/browser-playwright` and `playwright` dev dependencies — where layout, container/media collapse, line-clamping,
computed style, and hit-testing are all genuine. Each spec is named `*.shell-sweep.spec.ts`, is excluded from its
project's default `ng test` run via `web/angular.json`'s per-project `test.exclude` because jsdom cannot run it, and
mounts a real component tree.

- `app-nav-menu.shell-sweep.spec.ts` and `app-header.shell-sweep.spec.ts` cover the app's two shared header shells —
  `hub`'s `BoardHeader` plus `AppNavMenu`, and `runner`'s `AppHeader`. For every viewport width from 1400 down to 320px
  (straddling every declared header breakpoint) and — runner shell only, the one content-dependent header width —
  signed-in username lengths from authless through 64 characters, they assert the profile menu trigger sits fully inside
  the viewport, `elementFromPoint` at the menu's own center hit-tests inside it, the header carries no horizontal
  overflow, and no page error fired. Proven able to fail: reverting `BoardHeader`'s `.trailing` shrink fix
  (`flex: 0 1 auto; min-width: 0`, `board-header.ts`) reproduces the off-screen-menu symptom, and restoring it passes
  again. The class also covers shrink-priority collisions — a stat strip and trailing cluster sharing equal flex-shrink
  priority squeeze the menu near the strip's 1150px breakpoint, which is why the already-clipping stat strip carries an
  outsized `flex-shrink` (`board-header.ts`'s `.stats` rule) and why the swept widths straddle that breakpoint.
- `app-nav.shell-sweep.spec.ts` covers the runner shell's top tab strip (`AppNav`, the `Board`/`Events` routed tabs
  above `<router-outlet>`); `KitTabStrip`/`KitTab` chrome carries no `@container` rule, so the claim is narrower: from
  1400px down to 320px both static labels render and the strip never overflows its own width.
- `chunk-page-layout.shell-sweep.spec.ts` covers the hub's chunk detail page, reachable from the mobile board's glance
  row — its General tab (`ChunkGeneralTab`), whose `@media (min-width: 720px)` grid places work item and issues in a
  shared left column with node history beside them — and drives the Transcripts tab through its composed chain:
  `ChunkPage`, `ChunkTranscriptsContainer`, `ChunkTranscriptsTab`, routed for real via `RouterTestingHarness` under a
  height-capped stand-in for `App`'s `.layout`, because a standalone `TestBed.createComponent` mount never assembles the
  container's own box into the chain and cannot see the regressions below.
  - The General-tab case asserts, at 390px and 320px, that the work-item, issues, and node-history panels genuinely
    stack — distinct `getBoundingClientRect().top` values at a common `left` — with no horizontal overflow; at 1024px,
    that node history's `left` sits at or past the work-item column's `right` while work item and issues keep distinct
    `top`s in their shared column. Proven able to fail by moving node history's explicit grid placement
    (`grid-column: 1; grid-row: 3`) into the work-item/issues column.
  - The page-level error status is pinned against the back bar — `fleet-kit-async-state`'s absolutely-centered
    `placement="center"` must resolve against the back row's sibling, or it paints the failure text across the 44px back
    bar — and the issue pane's own error text must stay within its section at phone widths.
  - The Transcripts-tab stacking case covers `ChunkTranscriptsTab`, whose nav-beside-viewer split collapses to a stack
    below `@media (min-width: 720px)`: with one stubbed segment open at 390px it asserts the step nav's `top` sits above
    the segment body's own — genuinely stacked, not beside — with no horizontal overflow. Proven able to fail by forcing
    `.tx-tab`'s base `flex-direction` to `row`.
  - The composed-chain scroll case serves a 60-turn segment at 390×700 and asserts the tab's own box stays bounded by
    the viewport — a definite height reached it — and that `.tx-view` is a genuine scroll container, `scrollTop`
    round-tripping past 0. Proven able to fail by deleting `ChunkTranscriptsContainer`'s `:host { display: contents }`,
    which leaves the tab's box unbounded. The case waits on its own bounded `pumpUntil` rather than the shared
    `settle()` helper, and the difference is load-bearing: a TanStack query enabled late — after the app has already
    reported stable once — registers a pending task Angular's zoneless stability never retires, so `whenStable()` hangs
    though the DOM has rendered; no layout claim is relaxed, since `pumpUntil` throws if the content never renders.
  - The composed-chain centering case renders the permission notice and asserts its absolutely-centered status line
    centers on the tab's box rather than the browser viewport's, measured as which of the two centers it sits nearer —
    containment cannot tell them apart, since the host fills the tab body and the viewport's center falls inside it too.
    Proven able to fail by deleting `chunk-transcripts-tab.ts`'s own `:host { position: relative }`.
- `chunk-artifacts-tab-layout.shell-sweep.spec.ts` covers the hub Artifacts tab's composed chain — `ChunkPage` →
  `ChunkArtifactsTab` → `ChunkArtifactsPanel` — through a real router, proving `.art-tab`'s `height: 100%` resolves
  against a definite containing block and that an overflowing artifact nav list genuinely scrolls.
- `chunk-facts-alignment.shell-sweep.spec.ts` covers the chunk detail facts/usage table pair — `ChunkFacts` with
  `ChunkTokenBreakdown` content-projected as its sibling `<dl class="kv">`, composed as `chunk-detail-panel.html`
  composes them: a real-Chromium geometry check that the shared `--kv-label-col`/`--chunk-facts-pad` custom properties
  keep the two tables' columns aligned when a long wrapped Runner value gives them different content widths.
- `chunk-detail-page.shell-sweep.spec.ts` covers the runner-local chunk detail page (`ChunkDetailPage`), reachable from
  the machine panel's chunk rows: at 390px and 320px it walks the General, Artifacts, and Transcripts tabs, asserting
  each stacks its own sections with no horizontal overflow — evaluating the General tab's `@media (min-width: 720px)`
  two-column collapse and the Artifacts tab's long unbroken artifact key. Its takeover case mounts a `needs_human` chunk
  carrying a runner-composed wrapped takeover command and its raw resume fallback at realistic lengths;
  `fleet-kit-panel`'s body clips horizontally (`kit-panel.ts` `overflow-x: hidden`), so no takeover CSS can widen the
  tab and the load-bearing claim is the opposite one: at 320px each over-wide command must be reachable by scrolling its
  own box (`scrollLeft` round-trips past 0) or the clip silently amputates the string the operator must paste whole —
  asserted for the wrapped primary and the expanded raw fallback. Proven able to fail on each half by dropping
  `overflow-x: auto` from `.takeover .cmd` and from `.raw-fallback .cmd`.
- `transcript-panel.shell-sweep.spec.ts` covers the runner's transcript panel (`TranscriptPanel`), reachable from the
  mobile chunk-detail screen, in its closed-lease-from-hub states: at 390px and 320px a truncated archived read renders
  the archived badge (`transcript-archived-badge`) and truncation banner (`transcript-truncated`), and a hub-unreachable
  read (`hub_unreachable: true`) renders its degrade banner (`transcript-hub-unreachable`), each with no element or
  panel overflow. Proven able to fail by adding `white-space: nowrap` to `.degrade-banner`.
- `local-panel-mobile.shell-sweep.spec.ts` covers the runner's mobile chunk list — `LocalPanelMobile` then `ChunkCard`,
  the component the tier rule actually names (`local-panel.ts`'s `mode()` mounts it beneath the persistent
  `MobileTabBar`, the rule's "mobile shell's bottom nav"); the desktop `LocalPanelLayout`/`ChunkRow` pair is never
  reached below the mobile breakpoint and has no shell-sweep spec of its own. It mounts a chunk card carrying five work
  items and, at 390px and 320px, asserts the per-line `-webkit-line-clamp: 2` `.wi` lines genuinely stack — distinct
  `getBoundingClientRect().top` values per line — with no horizontal overflow and no page error. Proven able to fail by
  forcing `.wi` back to `display: inline` inside a `white-space: nowrap` container, which collapses every line onto one.
- `session-recovery-view.shell-sweep.spec.ts` covers the runner's session-recovery surface (`SessionRecoveryView`),
  rendered by the runner `App` in place of the whole panel when a federation bounce could not be silently completed: at
  390px and 320px the headline/detail block (`session-recovery`) and retry control (`session-recovery-retry`) must
  render with no view-wide horizontal overflow. Proven able to fail by adding `white-space: nowrap` to `.detail`.
- `runner-view.shell-sweep.spec.ts` covers the runner registry's rate-limit pace bars (`RunnerPanelView`): a row
  carrying two sampled windows (`5h`, `7d`), each a stacked utilization/elapsed bar pair; at the board right rail's
  ~390px width both windows' bars must genuinely stack and stay within the fleet panel's width, with no horizontal
  overflow and no page error — jsdom lays out flex children without ever checking clipping.
- `hover-tint.shell-sweep.spec.ts` covers the shared `--tint-hover`/`--tint-selected` design tokens across their three
  composition sites — `BoardCardComponent`, `ChunkTimeline`'s history rows, and `ChunkArtifacts`'s artifact rows —
  proving a computed-style claim rather than a layout one: a real Playwright-backed pointer (`userEvent.hover`)
  distinguishes a hovered element's resolved `background-color` from its resting one and, on the board card and on
  `ChunkTimeline`'s own `selected` row (`activatable`, `selectedKey`), from a selected-but-unhovered row's. It also pins
  the artifact list's asymmetry: hovering an `.artifact-link` washes its row, while hovering a contentless
  `.artifact-plain` row — nothing an expand would reveal, no control to hover — does not. The design tokens live in the
  global stylesheet `web/projects/fleet/src/lib/design/tokens.css`, loaded by every app's build but never by a
  standalone component test — a plain `.css` module import lands as an unreferenced lazy chunk under this builder — so
  the spec reads the sheet's real text through `commands.readFile`, the vitest browser command exposed for exactly this,
  and injects it as a `<style>` element. Proven able to fail on every assertion by reverting each rule: the
  `background: var(--tint-hover)` halves of `board-card.ts`'s `.card:hover` and `chunk-timeline.ts`'s `.step:hover`, the
  `.card.selected`/`.step.selected` backgrounds pointed at `--tint-hover` instead of `--tint-selected`, and
  `chunk-artifacts.ts`'s `:has()` selector re-scoped from `.artifact-link:hover` to `.artifact-plain:hover`.
