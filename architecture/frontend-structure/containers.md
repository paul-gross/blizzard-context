# Containers and their reads

Where a component's logic goes, and what a data-backed view may render before its read resolves. Spoke of the
[frontend structure hub](../frontend-structure.md); each rule follows the slot skeleton owned by
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

**Detect.** A component file that both calls an `inject*Query`/`inject*Mutation` and whose sibling `.html` template
carries domain markup (rows, cards, forms) rather than delegating to a child; a presentational component that itself
calls `inject*Query`.

**Do.** `chunk-detail.ts` (the container: owns the query, maps `pmItems`/`actionError`, forwards `detail`) renders
`chunk-detail-panel.ts` (the presentational panel), passing data down and re-emitting its outputs up unchanged. Under
the Exception: `local-identity.ts` and `local-pause-control.ts` (issue #131, #133) each inject their own status read
(and, for the latter, its own pause mutation) and render straight off kit primitives (`KitBadge`, `KitButton`) inside
the runner header's `[header-trailing]` slot — no row/card/form markup, so no presentational sibling is owed.

**Don't.** A single component that both injects `injectHubRunnersQuery()` and renders the registry table inline — a test
of the table now needs a stubbed client even when the row markup is all that changed.

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
`fleet-kit-async-state` in the same file — caught in review, not by a tool; a container reading `query.isFetching()`
where `isPending()` belongs; a conditional query's "nothing selected" state expressed as a branch *after* (rather than
before) the triad.

**Do.** `board-page.ts` derives `asyncState(chunksQuery, chunks().length === 0)` and hands it to `board-shell.ts`'s
`state` input, which renders `fleet-kit-async-state` in place of a bare length check. `chunk-detail.ts` branches on
`chunkId() === null` — its own rest state — before ever consulting `asyncState(detailQuery, false)`, since the detail
query is `enabled: false` while nothing is selected.

**Don't.** `@if (rows().length === 0) { <p>NO RUNNERS REGISTERED</p> }` off a query's `data() ?? []` with no
`isPending()`/`isError()` check anywhere in the component — indistinguishable from the pre-#181 defect this rule exists
to keep from recurring.
