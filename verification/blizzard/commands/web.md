# Angular workspace command detail (`bzh:matrix-command-web`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->

The `web:` scope's checks — the generated-client drift guard, the structural gate, and the real-Chromium shell sweep.
Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to every other method's detail.

### web:client-drift

`npm run generate:client` in `web/` (openapi-ts codegen from `openapi/{hub,runner}.openapi.json`), then fail on any
unstaged diff in `web/` ([../../standards/frontend.md](../../../standards/frontend.md), `bzh:generated-client`). The
check is a working-tree-vs-index `git diff`, not a working-tree-vs-`HEAD` one — a regeneration already `git add`ed
passes. The Python half regenerates the specs via `uv run blizzard-export-openapi --out-dir openapi` and fails the same
way on an unstaged diff in `openapi/`.

### web:structural-gate

`npm run structural-gate` in `web/` (`web/scripts/structural-gate.js`) — each check below is **live**:

- a `max-lines` ceiling over every Angular component file (the ~400-line cap,
  [../../architecture/frontend-structure.md](../../../architecture/frontend-structure.md)
  `bzh:frontend-container-presentational`);
- a real-timer sweep (issue #275) over the specs the `test` target actually runs, failing a `setTimeout`/`setInterval`
  whose delay is a **non-zero integer literal** — a real second spent inside the merge gate, and a window guessed rather
  than chosen. A delay held in a variable or expression is outside the pattern; `setTimeout(…, 0)` is the
  macrotask-flush idiom and is deliberately not matched; `*.shell-sweep.spec.ts` is out of scope (a real-Chromium frame
  wait is `web:shell-sweep`'s method); a genuinely time-driven spec is named in `REAL_TIMER_EXEMPT_FILES` with its
  reason, today only `demo-director.spec.ts`, whose waits poll a real router harness at the kiosk tour's own measured
  cadence. The tree is clean of the shape today, so this check alone would pass with its detector deleted — it carries a
  fixture self-test (`assertRealTimerDetectorWorks`, must-catch and must-pass shapes including a nested call in the
  callback) that refuses to run the gate at all if the detector stops classifying them, which is what keeps it a guard
  rather than a decoration (`bzh:case-pins-its-own-name`). The remaining check fires on real files today and needs no
  equivalent.

The `max-lines` half armed in phase 3 of the WEBARCH epic (blizzard#77) once the chunk-detail decomposition (#79) and
the panel splits (#80) brought every in-scope component file under the cap. `board-shell.ts` was the one named script
exemption — over the cap but outside both #79's and #80's file lists, a standing gap rather than a silent pass — and
**#137 closed it**: extracting `board-card.ts` and `board-column.ts` as presentational children brought the file under
the cap and deleted its `MAX_LINES_EXEMPT_FILES` entry, so the `max-lines` half now covers every in-scope component file
with **no exemptions**.

### web:shell-sweep

`npm run shell-sweep` in `web/` (`web/scripts/shell-sweep.js`) — the tooled proof behind two classes of claim jsdom
cannot evaluate. The first, and the method's original reason to exist, is the narrow-viewport tier rule
(`bzh:narrow-viewport-tier-rule`, [tier rules](../tier-rules.md)) for components reachable from the mobile shell's
bottom nav: jsdom (`web:unit-test`'s environment) parses `@container`/media-query rules without evaluating them and
never actually lays out or clamps text, so no jsdom spec can prove a real collapse. The second is a computed-style claim
no viewport width changes — most concretely a `:hover`/`:focus-visible` rule, since jsdom parses a pseudo-class selector
without ever resolving it against a simulated pointer, so no jsdom spec can prove a hovered element reads differently
from a resting or a selected one either. Both classes share the same gap and the same fix: this method runs its specs
under `@angular/build:unit-test`'s real-browser mode instead (`--browsers=ChromiumHeadless`, backed by the
`@vitest/browser-playwright` + `playwright` dev dependencies, pinned to the same `1.61.x` release the Python
`tests/e2e/` tier already caches a Chromium build for), where layout, `@container`/media-query collapse, line-clamping,
computed style, and hit-testing are all genuine. Each spec — named `*.shell-sweep.spec.ts` and excluded from its
project's default `ng test` run (`web/angular.json`'s per-project `test.exclude`), since jsdom cannot run it — mounts a
real component tree.

`app-nav-menu.shell-sweep.spec.ts` and `app-header.shell-sweep.spec.ts` cover the app's two shared header shells
(`hub`'s `BoardHeader` + `AppNavMenu`, `runner`'s `AppHeader`) and, for every combination of viewport width (1400 down
to 320px, straddling every breakpoint the header declares) and — for the runner shell only, the one with a
content-dependent header width — signed-in username length (authless through 64 characters), assert the profile menu
trigger sits fully inside the viewport, `elementFromPoint` at the menu's own center hit-tests inside it, the header
itself carries no horizontal overflow, and no page error fired. Proven able to fail (issue #171): reverting
`BoardHeader`'s `.trailing` shrink fix (`flex: 0 1 auto; min-width: 0`, `board-header.ts`) reproduces the exact
off-screen-menu symptom the historical fix (issue #163) was for; restoring it passes again. The sweep's own first real
run surfaced a second, narrower instance of the same defect class — the hub shell's stat strip and trailing cluster
shared an equal flex-shrink priority, so a busy header (both spend cells shown) let the menu absorb a few px of squeeze
right above the strip's own 1150px breakpoint — closed by giving the stat strip (which already clips via
`overflow: hidden`) an outsized `flex-shrink` so it absorbs a narrowing header before the trailing cluster gives up
anything (`board-header.ts`'s `.stats` rule and its own comment).

`local-panel-mobile.shell-sweep.spec.ts` (issue #176) covers the runner's mobile chunk list — `LocalPanelMobile` →
`ChunkCard`, the component the rule actually names (`local-panel.ts`'s `mode()` mounts `LocalPanelMobile` beneath the
persistent `MobileTabBar`, the rule's "mobile shell's bottom nav"; the desktop `LocalPanelLayout` → `ChunkRow` pair is
never reached below the mobile breakpoint and has no `*.shell-sweep.spec.ts` of its own —
`app-header.shell-sweep.spec.ts` mounts `AppHeader` alone, with no chunk rows in its tree). It mounts a chunk card
carrying five work items and, at 390px and 320px, asserts the five per-line `-webkit-line-clamp: 2` `.wi` lines actually
stack — five distinct `getBoundingClientRect().top` values — with no horizontal overflow (`scrollWidth <= clientWidth`)
and no page error. Proven able to fail: forcing `.wi` back to `display: inline` inside a `white-space: nowrap` container
collapses all five lines onto one (`tops were 322, 322, 322, 322, 322: expected 1 to be 5`); restoring the per-line
clamp passes again.

`chunk-page-layout.shell-sweep.spec.ts` (blizzard#203) covers the hub's chunk detail page — reachable from the mobile
board's glance row, the rule's "mobile shell's bottom nav" — specifically its General tab (`ChunkGeneralTab`), whose
`@media (min-width: 720px)` grid places work item and issues in a shared left column with node history beside them. It
mounts the tab with a fixture chunk and, at 390px and 320px, asserts the work-item/issues/node-history panels genuinely
stack — three distinct `getBoundingClientRect().top` values at a common `left` — with no horizontal overflow; at 1024px
it asserts node history's `left` sits at or past the work-item column's `right` (genuinely beside it, not below), while
work item and issues keep two distinct `top`s in that shared column. Proven able to fail: moving node history's explicit
grid placement into the work-item/issues column (`grid-column: 1; grid-row: 3`) collapses the 1024px case:

```text
node history's left (8) is not beside the work-item column (right edge 508): expected 8 to be greater than or equal to 508
```

Restoring its own column passes again. The same spec's fourth case (blizzard#251) mounts a `needs_human` chunk carrying
both a runner-composed wrapped takeover command and its raw resume fallback — realistically long strings, an absolute
runtime dir and worktree path apiece. The tab's no-horizontal-overflow half is structural — `fleet-kit-panel`'s body
clips horizontally (`kit-panel.ts` `overflow-x: hidden`), so no takeover CSS can widen it — which makes the load-bearing
claim the opposite one: at 320px, each command wider than the viewport must be **reachable by scrolling its own box**
(`scrollLeft` round-trips past 0), or the panel clip silently amputates the tail of the string the operator must paste
whole — asserted for the wrapped primary and, expanded, for the raw fallback, with the tab's no-overflow guard kept
before and after. Proven able to fail on both halves: dropping `overflow-x: auto` from `.takeover .cmd` fails the
collapsed half ("wrapped command is clipped, not scrollable: expected 0 to be greater than 0"), dropping it from
`.raw-fallback .cmd` fails the expanded half the same way; restoring each passes again. The same spec's fifth case
(blizzard#248) covers the same page's Transcripts tab (`ChunkTranscriptsTab`), whose nav-beside-viewer split collapses
to a stack below `@media (min-width: 720px)`: it mounts the tab with one stubbed segment already open and, at 390px,
asserts the step nav's `top` sits above the segment body's own (genuinely stacked, not beside it) with no horizontal
overflow. Proven able to fail: forcing `.tx-tab`'s base `flex-direction` to `row` (the wide-viewport rule with no
narrow-viewport collapse) fails the stacking assertion; restoring the narrow-first default passes again.

The same spec's sixth and seventh cases (blizzard#248) cover the same tab through its **composed chain** — `ChunkPage` →
`ChunkTranscriptsContainer` → `ChunkTranscriptsTab`, routed for real via `RouterTestingHarness` under a stand-in for
`App`'s own height-capped `.layout`. They exist because the fifth case mounts the tab standalone via
`TestBed.createComponent`, which never assembles the container's own box into the chain, and so could see neither
regression below. The sixth serves a 60-turn segment at 390×700 and asserts the tab's own box stays bounded by the
viewport (a definite height reached it) and that `.tx-view` is a genuine scroll container (`scrollTop` round-trips
past 0) — proven able to fail by deleting `ChunkTranscriptsContainer`'s `:host { display: contents }`:

```text
the tab's own box is unbounded (5331.125px) — the flex/height chain never reached it: expected 5331.125 to be less than or equal to 700
```

Restoring it passes again. The sixth waits on its own bounded `pumpUntil` rather than the shared `settle()` helper, and
that difference is load-bearing rather than incidental: its segment-content read is second-order — enabled only once the
*index* query has resolved and named the segment's finality — and a TanStack query enabled that late, after the app has
already reported stable once, registers a pending task Angular's zoneless stability never retires. `whenStable()` then
waits forever even though change detection has gone quiet and the DOM has rendered, which is what hung this case before.
Established by removing the gate so the read fires immediately, which makes the same case pass under `settle()`
unchanged — a one-off diagnostic, not a standing test. No layout claim is relaxed by waiting the other way — `pumpUntil`
throws if the content never renders. The seventh renders the permission notice and asserts its absolutely-centered
status line centers on the **tab's** box rather than the browser viewport's — measured as which of the two centers it
sits nearer, since containment alone cannot tell them apart (the host fills the tab body, so the viewport's own center
falls inside it too) and since `.status` is a `<p>` whose un-reset user-agent top margin offsets it from either center
by a line. Proven able to fail by deleting `chunk-transcripts-tab.ts`'s own `:host { position: relative }`:

```text
status line centered on 463, nearer the viewport's center (450) than the tab's own (506.5) — it has no positioned ancestor: expected 43.5 to be less than 13
```

Restoring it passes again. That mutation is why the case is measured this way: against the containment assertion it
originally shipped with, deleting `position: relative` left all seven cases green.

`runner-view.shell-sweep.spec.ts` (blizzard#218) covers the runner registry's rate-limit pace bars (`RunnerPanelView`):
a row carrying two sampled windows (`5h`, `7d`), each rendering a stacked utilization/elapsed bar pair. At the board
right rail's own ~390px width it asserts the two bars for both windows are genuinely stacked (two distinct rows, not
overlapping) and stay within the fleet panel's own width, with no horizontal overflow and no page error — the class of
claim jsdom cannot make good on, since it lays out flex children without ever checking whether they actually clip.

`transcript-panel.shell-sweep.spec.ts` (blizzard#249) covers the runner's transcript panel (`TranscriptPanel`),
reachable from the mobile chunk-detail screen (`local-panel-mobile.spec.ts`'s `data-testid="detail-transcript"`) —
specifically its two new closed-lease-from-hub states. At 390px and 320px it mounts a truncated archived read and
asserts both the archived badge (`transcript-archived-badge`) and the truncation banner (`transcript-truncated`) render
with no horizontal overflow on either element or the panel as a whole, then mounts a hub-unreachable read
(`hub_unreachable: true`, no local answer) and asserts its degrade banner (`transcript-hub-unreachable`) renders with no
panel overflow. Proven able to fail: adding `white-space: nowrap` to `.degrade-banner` reproduces exactly that overflow
at both widths (`555 > 390`/`555 > 320`); restoring it passes again.

`session-recovery-view.shell-sweep.spec.ts` (blizzard#312) covers the runner's session-recovery surface
(`SessionRecoveryView`), rendered by the runner `App` in place of the whole panel when a federation bounce could not be
silently completed — reachable at every width the shell itself is. At 390px and 320px it mounts the view standalone and
asserts the headline/detail block (`session-recovery`) and the retry control (`session-recovery-retry`) both render,
with no horizontal overflow on the view as a whole. Proven able to fail: adding `white-space: nowrap` to `.detail`
reproduces exactly that overflow at 320px (`343 > 320`); restoring the wrap passes again.

`app-nav.shell-sweep.spec.ts` (issue #313) covers the runner shell's own top tab strip (`AppNav`), the `Board`/`Events`
routed tabs the desktop shell renders above `<router-outlet>`. `KitTabStrip`/`KitTab`'s chrome carries no `@container`
rule of its own, so this is a narrower claim than the header sweeps beside it: across every width from 1400px down to
320px it asserts only that both static labels render and that the strip never overflows its own width.

`chunk-detail-page.shell-sweep.spec.ts` (issue #318) covers the runner-local chunk detail page (`ChunkDetailPage`),
reachable from the machine panel's chunk rows. At 390px and 320px it walks all three tabs — General, Artifacts,
Transcripts — and asserts each stacks its own sections (distinct `getBoundingClientRect().top` values) with no
horizontal overflow, which is what evaluates the General tab's `@media (min-width: 720px)` two-column collapse and the
Artifacts tab's long unbroken artifact key. Its second case pins the page-level error status against the back bar: the
status line is `fleet-kit-async-state`'s absolutely-centered `placement="center"`, so centering it against a box whose
only in-flow content is the 44px back bar paints `FAILED TO LOAD CHUNK` across `‹ Board` — it must resolve against the
back row's sibling instead. Its third case asserts the issue pane's own error text stays within its section at phone
widths.

`hover-tint.shell-sweep.spec.ts` covers the shared `--tint-hover`/`--tint-selected` design tokens across their three
composition sites — `BoardCardComponent`, `ChunkTimeline`'s history rows, and `ChunkArtifacts`'s artifact rows — the
first spec proving a computed-style claim rather than a layout one: a real pointer (`userEvent.hover`,
Playwright-backed) distinguishes a hovered element's resolved `background-color` from its resting one, and — on the
board card, and again on `ChunkTimeline` once blizzard#315 gave it a `selected` row of its own (`activatable`,
`selectedKey`) — from a selected-but-unhovered row's own. It also pins the artifact list's asymmetry: hovering a
`.artifact-link` washes its row, hovering a contentless `.artifact-plain` row (nothing an expand would reveal — no
control to hover) does not. Proven able to fail on all five assertions: dropping the `background: var(--tint-hover)`
half of `board-card.ts`'s `.card:hover` rule reproduces
`hover produced no background
change from resting (rgba(0, 0, 0, 0.25))`; pointing `.card.selected`'s background at
`--tint-hover` instead of `--tint-selected` reproduces
`a selected card (...) reads identical to a hovered-but-unselected one (...)`; dropping the same half of
`chunk-timeline.ts`'s `.step:hover` rule reproduces the same shape of failure on the history row; pointing
`.step.selected`'s background at `--tint-hover` instead of `--tint-selected` reproduces the same
selected-reads-identical-to-hovered failure there too; and re-scoping `chunk-artifacts.ts`'s `:has()` selector from
`.artifact-link:hover` to `.artifact-plain:hover` reproduces it on the artifact row while the plain-row half stops
distinguishing at all. Restoring each rule passes again. The design tokens are a global stylesheet
(`web/projects/fleet/src/lib/design/tokens.css`), loaded by every app's own build but never by a standalone component
test — a plain module import of the `.css` file does not reach the document either under this builder (it lands as an
unreferenced lazy chunk); the spec instead reads the sheet's real text through `commands.readFile`, the vitest browser
command this builder exposes for exactly this, and injects it as a `<style>` element itself.
