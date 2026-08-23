# Containers and async state

Where a component's logic goes, and what a data-backed view may render before its read resolves. A spoke of the
[frontend structure hub](../frontend-structure.md); each rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Container/presentational split (`bzh:frontend-container-presentational`)

**Rule.** A component that injects a query or mutation (a container) renders no inline domain markup of its own — it
maps loading/error state and forwards data down to a presentational sibling (inputs/outputs only, no injection) that
owns the template.

**Why.** A presentational component is testable with plain inputs and no client stub, and reusable between a live-data
container and a fixture-driven spec; a merged component forces every markup test through a query/mutation double.

**Exception.** A header-slot mini-container — projected into a shared header's `[header-trailing]`-style slot, the
composition boundary `BoardHeader` already exposes, its template entirely kit primitives (`fleet-kit-badge`,
`fleet-kit-button`, …) with no bespoke domain markup (rows, cards, forms) — may inject its own query/mutation without a
presentational sibling. The exception is narrow: the moment such a component grows a row, card, or form, it re-enters
the rule.

**Detect.** A component file that both calls an `inject*Query`/`inject*Mutation` and whose sibling `.html` template
carries domain markup (rows, cards, forms) rather than delegating to a child; a presentational component itself calling
`inject*Query`.

**Do.**

- `chunk-detail.ts` (the container — owns the query, maps `actionError` and the derived async state, forwards `detail`)
  renders the presentational `chunk-detail-panel.ts`, passing data down and re-emitting its outputs unchanged.
- Under the exception: `local-identity.ts` (its own session read and logout mutation) and `local-pause-control.ts` (its
  own status read and pause mutation) render straight off kit primitives (`KitBadge`, `KitButton`) inside the runner
  header's `[header-trailing]` slot, owing no presentational sibling.

**Don't.** A single component both injecting `injectHubRunnersQuery()` and rendering the registry table inline — testing
the table then needs a stubbed client even when only row markup changed.

## Empty state is gated on the read (`bzh:frontend-empty-state-gated`)

**Rule.** A view's empty-state copy renders only once the read backing it has resolved — never from a bare
`data().length === 0` check. The container maps its query's `isPending()`/`isError()` (never `isFetching()`) through
`query-state.ts`'s `asyncState`/`asyncStateOf` onto a `KitAsyncStateValue`, which the presentational view renders
through `KitAsyncState` rather than inferring `'empty'` from an array that reads `[]` during the first fetch just as
when genuinely empty. A disabled query (`enabled: false` — a conditional read with nothing selected yet) reports
`isPending()` permanently true, so its container branches on its own "nothing selected" rest state before consulting the
pending/error/empty triad, or that rest state renders as an endless spinner.

**Why.** `data() ?? []` is indistinguishable from a settled empty read — a real shipped defect rendered a healthy busy
fleet as "FLEET IDLE" on every reload while the first `GET /api/chunks` was still in flight. Why `isPending()` is read
rather than `isFetching()` is owned by `query-state.ts`'s own doc comment: a background refetch (a poll, an SSE-driven
invalidation) must not regress an already-rendered view to loading.

**Detect.** A component rendering a `data-testid` matching `*-empty` without referencing `fleet-kit-async-state` in the
same file — caught in review, not by a tool; a container reading `query.isFetching()` where `isPending()` belongs; a
conditional query's "nothing selected" state branched after rather than before the triad.

**Do.**

- `board-page.ts` derives `asyncState(chunksQuery, chunks().length === 0)` and hands it to `board-shell.ts`'s `state`
  input, which renders `fleet-kit-async-state` in place of a bare length check.
- `chunk-detail.ts` branches on `chunkId() === null` — its own rest state — before ever consulting
  `asyncState(detailQuery, false)`, since the detail query is `enabled: false` while nothing is selected.

**Don't.** `@if (rows().length === 0) { <p>NO RUNNERS REGISTERED</p> }` off a query's `data() ?? []` with no
`isPending()`/`isError()` check anywhere in the component.
