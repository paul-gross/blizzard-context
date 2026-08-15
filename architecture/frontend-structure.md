# Frontend structure

The Angular suite's where-does-it-go / what-depends-on-what map — the frontend analog of
[./clean-architecture.md](./clean-architecture.md)'s dependency-inversion for the daemon side. This is the **sole
owner** of the container/presentational split (`canon:one-owner`): [../standards/frontend.md](../standards/frontend.md)
cites the rules here rather than restating them. Each rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Container/presentational split (`bzh:frontend-container-presentational`)

**Rule.** A component that injects a query or mutation (a **container**) renders no inline domain markup of its own — it
maps loading/error state and forwards data down to a **presentational** sibling (inputs/outputs only, no injection) that
owns the template.

**Why.** A presentational component is testable with plain inputs and no client stub, and is reusable across a container
that reads live data and one a spec drives with a fixture — collapsing the two into one component forces every test of
the markup through a query/mutation double, and forces every future consumer to carry the data layer along with the
view.

**Exception.** A header-slot mini-container — a small component projected into a shared header's
`[header-trailing]`-style slot, whose entire template is kit primitives (`fleet-kit-badge`, `fleet-kit-button`, …) with
no bespoke domain markup (rows, cards, forms) of its own — may inject its own query/mutation without splitting out a
presentational sibling. The slot itself is the composition boundary the host (`BoardHeader`) already exposes; a
container/presentational split below it buys no testability the plain-kit template doesn't already have, only an extra
file. This is narrow: the moment such a component grows a row, card, or form, it re-enters the rule.

**Detect.** A component file that both calls an `inject*Query`/`inject*Mutation` and carries a multi-line `template:`
with domain markup (rows, cards, forms) rather than delegating to a child; a presentational component that itself calls
`inject*Query`.

**Do.** `chunk-detail.ts` (the container: owns the query, maps `pmItems`/`actionError`, forwards `detail`) renders
`chunk-detail-panel.ts` (the presentational panel), passing data down and re-emitting its outputs up unchanged. Under
the Exception: `local-identity.ts` and `local-pause-control.ts` (issue #131, #133) each inject their own status read
(and, for the latter, its own pause mutation) and render straight off kit primitives (`KitBadge`, `KitButton`) inside
the runner header's `[header-trailing]` slot — no row/card/form markup, so no presentational sibling is owed.

**Don't.** A single component that both injects `injectHubRunnersQuery()` and renders the registry table inline — a test
of the table now needs a stubbed client even when the row markup is all that changed.

## The kit is the presentational floor (`bzh:frontend-kit-floor`)

**Rule.** Every presentational component builds its chrome — panel shell, async loading/error/empty state, tone badges,
action buttons, choice chips, tab strips — from `fleet/lib/kit/`, never a re-typed copy. The kit itself depends on
nothing but `@angular/core` (+ common directives) and the token CSS (`design/tokens.css`) — no query, mutation, or
client injection, so it stays presentational and testable by plain inputs at the bottom of the dependency graph.

**Why.** A shared presentational floor is what makes "no duplicated chrome" a structural property rather than a review
habit — every future panel composes the kit instead of re-inventing the `.panel`/`.p-hdr`/`.status` shapes, and a chrome
fix (a token, a state message) lands once. The kit sits *under* every container and presentational component in the
dependency graph; nothing in the kit may depend upward on a feature.

**Detect.** A new component's style block declaring `.panel`/`.p-hdr`/`.p-body`/`.status`/`.lbl` (the retired chrome
classes, `web:structural-gate`'s grep sweep) outside `fleet/lib/kit/`; a kit component (`fleet/lib/kit/*`) importing a
query, mutation, or the generated API client.

**Do.** A new panel imports `KitPanel`/`KitAsyncState`/`KitBadge` from `fleet` and composes them; a status message
renders through `KitAsyncState`'s `loading`/`error`/`empty` states rather than a local `<p class="status">`.

**Don't.** A new panel pastes another `.panel { background: linear-gradient(...); border: 1px solid var(--bezel); }`
block — the exact duplication the kit exists to retire.

## A data-backed view's empty state is gated on a resolved read (`bzh:frontend-empty-state-gated`)

**Rule.** A view's empty-state copy renders only once the read backing it has resolved — never from a bare
`data().length === 0` check. A container maps its query's `isPending()`/`isError()` (never `isFetching()`) through
`query-state.ts`'s `asyncState`/`asyncStateOf` onto a `KitAsyncStateValue`, and the presentational view renders it
through `KitAsyncState` rather than inferring `'empty'` from an array that reads `[]` during the first fetch exactly as
it would once genuinely empty. A **disabled** query (`enabled: false` — a conditional read with nothing selected yet)
reports `isPending()` as permanently `true`; a container for one branches on its own "nothing selected" rest state
*before* consulting the triad, or that rest state renders as an endless spinner instead.

**Why.** `data() ?? []`'s `[]` is indistinguishable from a settled empty read — the exact conflation issue #181 fixed: a
healthy busy fleet reads as idle on every reload because the board showed its "FLEET IDLE" copy while the first
`GET /api/chunks` was still in flight. Reading `isPending()` rather than `isFetching()` is what keeps a background
refetch (a poll, an SSE-driven invalidation) from regressing an already-rendered view back to a loading state — the
property `query-state.ts`'s own doc comment asserts directly.

**Detect.** A component rendering a `data-testid` matching `*-empty` that does not also reference
`fleet-kit-async-state` in the same file (`web:structural-gate`'s third check, `EMPTY_STATE_EXEMPT_FILES` naming the
views a one-time sweep confirmed are reachable only after a parent's own triad has already resolved); a container
reading `query.isFetching()` where `isPending()` belongs; a conditional query's "nothing selected" state expressed as a
branch *after* (rather than before) the triad.

**Do.** `board-page.ts` derives `asyncState(chunksQuery, chunks().length === 0)` and hands it to `board-shell.ts`'s
`state` input, which renders `fleet-kit-async-state` in place of a bare length check. `chunk-detail.ts` branches on
`chunkId() === null` — its own rest state — before ever consulting `asyncState(detailQuery, false)`, since the detail
query is `enabled: false` while nothing is selected.

**Don't.** `@if (rows().length === 0) { <p>NO RUNNERS REGISTERED</p> }` off a query's `data() ?? []` with no
`isPending()`/`isError()` check anywhere in the component — indistinguishable from the pre-#181 defect this rule exists
to keep from recurring.

## Sub-barrels and the SSE registry are the disjoint-diff mechanism (`bzh:frontend-disjoint-diffs`)

**Rule.** Two agents changing two different features must produce diffs that touch no shared file beyond one sub-barrel
export line and one SSE registry row. Each feature directory under `fleet/lib/` owns an `index.ts` sub-barrel
re-exported once from the root `public-api.ts`; a live feature registers its invalidated query keys as a declarative row
in **its own daemon's** SSE dispatch registry rather than a new `case` in a hand-written switch. The mechanism is not
singular: the hub's board registers in `sse/fleet-live.ts`'s `EVENT_INVALIDATION_REGISTRY`, and the runner's local panel
registers in its own, disjoint `RUNNER_EVENT_INVALIDATION_REGISTRY` (`local-panel/src/lib/runner-live-updates.ts`,
blizzard#317 Phase 4) — one row in the registry that owns the daemon a feature actually reads from, never a case added
to either `dispatch()`. What a sub-barrel exports is decided by **a consumer outside its own feature directory**, not by
membership in that directory: a sibling only the feature's own components mount stays unexported, so the public surface
names what is actually re-stackable rather than everything present.

**Why.** A single monolithic `public-api.ts` and a hand-written event-dispatch `switch` are both **guaranteed merge
conflicts**: every feature that adds an export or a live-update path touches the same line range of the same file as
every other feature in flight. Sub-barrels and a data-shaped registry turn "add a feature" into "add a file plus one
export line plus one table row" — additive, not contended. A second daemon growing its own registry rather than reaching
into the first's keeps that guarantee: the hub's and the runner's registries never share a line range because they never
share a file.

**Detect.** A new top-level export added directly to `public-api.ts` instead of a feature sub-barrel; a new `case` added
to a live-updates `dispatch()` — `fleet-live.ts`'s or `runner-live-updates.ts`'s — instead of a registry row; a live
feature's invalidation logic added as a case in one daemon's registry for a query key that actually belongs to the
other; a sub-barrel export no consumer outside its own feature directory imports.

**Do.** `chunks/index.ts` re-exports every chunks-feature symbol a consumer outside `chunks/` imports; `public-api.ts`
carries one `export * from './lib/chunks'` line for it. A sibling mounted only by its own feature — `chunk-detail/`'s
`ChunkDetailHeader` — stays unexported. A new live-updated board feature adds a row keyed by its event type to
`sse/fleet-live.ts`'s `EVENT_INVALIDATION_REGISTRY` (a
`Record<HubEventType, (data) => readonly (readonly unknown[])[]>`, exhaustive over `HUB_EVENT_TYPES` so an unhandled
event type is a compile error) rather than a `case` in `dispatch()`; a new live-updated runner-panel read does the same
in `local-panel`'s own `RUNNER_EVENT_INVALIDATION_REGISTRY`, exhaustive over `RunnerEventType` on the same terms — two
registries, each exhaustive over its own daemon's event union, never one growing a branch for the other's kind.

**Don't.** Two features both editing the same 40-line span of `public-api.ts` to add their exports, or both adding a
`case` to the same `switch` — exactly the conflict this rule exists to design away.

## See also

- [../standards/frontend.md](../standards/frontend.md) — the kit adoption rule (`bzh:frontend-kit`) cites
  `bzh:frontend-kit-floor` rather than restating it; the toolchain (lint/test/generated-client) rules live there.
- [../verification/blizzard.md](../verification/blizzard.md) — `web:structural-gate`, the tooled grep sweep that
  enforces both `bzh:frontend-kit-floor`'s Detect and `bzh:frontend-empty-state-gated`'s.
- [./clean-architecture.md](./clean-architecture.md) — the daemon-side dependency-inversion this doc is the frontend's
  counterpart to.
