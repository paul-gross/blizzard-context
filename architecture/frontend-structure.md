# Frontend structure

The Angular suite's where-does-it-go / what-depends-on-what map — the frontend analog of [./clean-architecture.md](./clean-architecture.md)'s dependency-inversion for the daemon side. This is the **sole owner** of the container/presentational split (`canon:one-owner`): [../standards/frontend.md](../standards/frontend.md) cites the rules here rather than restating them.
Each rule follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Container/presentational split (`bzh:frontend-container-presentational`)

**Rule.** A component that injects a query or mutation (a **container**) renders no inline domain markup of its own — it maps loading/error state and forwards data down to a **presentational** sibling (inputs/outputs only, no injection) that owns the template.

**Why.** A presentational component is testable with plain inputs and no client stub, and is reusable across a container that reads live data and one a spec drives with a fixture — collapsing the two into one component forces every test of the markup through a query/mutation double, and forces every future consumer to carry the data layer along with the view.

**Exception.** A header-slot mini-container — a small component projected into a shared header's `[header-trailing]`-style slot, whose entire template is kit primitives (`fleet-kit-badge`, `fleet-kit-button`, …) with no bespoke domain markup (rows, cards, forms) of its own — may inject its own query/mutation without splitting out a presentational sibling. The slot itself is the composition boundary the host (`BoardHeader`) already exposes; a container/presentational split below it buys no testability the plain-kit template doesn't already have, only an extra file. This is narrow: the moment such a component grows a row, card, or form, it re-enters the rule.

**Detect.** A component file that both calls an `inject*Query`/`inject*Mutation` and carries a multi-line `template:` with domain markup (rows, cards, forms) rather than delegating to a child; a presentational component that itself calls `inject*Query`.

**Do.** `chunk-detail.ts` (the container: owns the query, maps `pmItems`/`actionError`, forwards `detail`) renders `chunk-detail-panel.ts` (the presentational panel), passing data down and re-emitting its outputs up unchanged. Under the Exception: `local-identity.ts` and `local-pause-control.ts` (issue #131, #133) each inject their own status read (and, for the latter, its own pause mutation) and render straight off kit primitives (`KitBadge`, `KitButton`) inside the runner header's `[header-trailing]` slot — no row/card/form markup, so no presentational sibling is owed.

**Don't.** A single component that both injects `injectHubRunnersQuery()` and renders the registry table inline — a test of the table now needs a stubbed client even when the row markup is all that changed.

## The kit is the presentational floor (`bzh:frontend-kit-floor`)

**Rule.** Every presentational component builds its chrome — panel shell, async loading/error/empty state, tone badges, action buttons, choice chips, tab strips — from `fleet/lib/kit/`, never a re-typed copy. The kit itself depends on nothing but `@angular/core` (+ common directives) and the token CSS (`design/tokens.css`) — no query, mutation, or client injection, so it stays presentational and testable by plain inputs at the bottom of the dependency graph.

**Why.** A shared presentational floor is what makes "no duplicated chrome" a structural property rather than a review habit — every future panel composes the kit instead of re-inventing the `.panel`/`.p-hdr`/`.status` shapes, and a chrome fix (a token, a state message) lands once. The kit sits *under* every container and presentational component in the dependency graph; nothing in the kit may depend upward on a feature.

**Detect.** A new component's style block declaring `.panel`/`.p-hdr`/`.p-body`/`.status`/`.lbl` (the retired chrome classes, `web:structural-gate`'s grep sweep) outside `fleet/lib/kit/`; a kit component (`fleet/lib/kit/*`) importing a query, mutation, or the generated API client.

**Do.** A new panel imports `KitPanel`/`KitAsyncState`/`KitBadge` from `fleet` and composes them; a status message renders through `KitAsyncState`'s `loading`/`error`/`empty` states rather than a local `<p class="status">`.

**Don't.** A new panel pastes another `.panel { background: linear-gradient(...); border: 1px solid var(--bezel); }` block — the exact duplication the kit exists to retire.

## Sub-barrels and the SSE registry are the disjoint-diff mechanism (`bzh:frontend-disjoint-diffs`)

**Rule.** Two agents changing two different features must produce diffs that touch no shared file beyond one sub-barrel export line and one SSE registry row. Each feature directory under `fleet/lib/` owns an `index.ts` sub-barrel re-exported once from the root `public-api.ts`; a live feature registers its invalidated query keys as a declarative row in the SSE dispatch registry (`sse/fleet-live.ts`) rather than a new `case` in a hand-written switch.

**Why.** A single monolithic `public-api.ts` and a hand-written event-dispatch `switch` are both **guaranteed merge conflicts**: every feature that adds an export or a live-update path touches the same line range of the same file as every other feature in flight. Sub-barrels and a data-shaped registry turn "add a feature" into "add a file plus one export line plus one table row" — additive, not contended.

**Detect.** A new top-level export added directly to `public-api.ts` instead of a feature sub-barrel; a new `case` added to `fleet-live.ts`'s `dispatch()` instead of a registry row.

**Do.** `chunks/index.ts` re-exports every chunks-feature symbol; `public-api.ts` carries one `export * from './lib/chunks'` line for it. A new live-updated feature adds a row keyed by its event type to `sse/fleet-live.ts`'s `EVENT_INVALIDATION_REGISTRY` (a `Record<HubEventType, (data) => readonly (readonly unknown[])[]>`, exhaustive over `HUB_EVENT_TYPES` so an unhandled event type is a compile error) rather than a `case` in `dispatch()`.

**Don't.** Two features both editing the same 40-line span of `public-api.ts` to add their exports, or both adding a `case` to the same `switch` — exactly the conflict this rule exists to design away.

## See also

- [../standards/frontend.md](../standards/frontend.md) — the kit adoption rule (`bzh:frontend-kit`) cites `bzh:frontend-kit-floor` rather than restating it; the toolchain (lint/test/generated-client) rules live there.
- [../verification/blizzard.md](../verification/blizzard.md) — `web:structural-gate`, the tooled grep sweep that enforces `bzh:frontend-kit-floor`'s Detect.
- [./clean-architecture.md](./clean-architecture.md) — the daemon-side dependency-inversion this doc is the frontend's counterpart to.
