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
- Under the exception: `app-identity.ts` (its own session read and logout mutation) and `app-pause-control.ts` (its own
  status read and pause mutation) render straight off kit primitives (`KitBadge`, `KitButton`) inside the runner
  header's `[header-trailing]` slot, owing no presentational sibling.

**Don't.** A single component both injecting `injectHubRunnersQuery()` and rendering the registry table inline — testing
the table then needs a stubbed client even when only row markup changed.

## Containers compose; models derive (`bzh:frontend-containers-compose`)

**Rule.** Keep every `computed()` in a container to composition — read signals and query results, combine them with
`&&`, `||`, `??`, `?.`, and comparisons, and call imported functions. Branching, loops, and collection transforms live
in a pure `*.model.ts` beside the feature: it takes plain values (a `now: number`, never a clock), imports no Angular,
query, or `inject`, and is pinned by a sibling `*.model.spec.ts` that needs no `TestBed`. A structural query-handle
interface the model declares or imports, such as `AsyncStateQuery` or `WorkItemsQuery`, counts as a plain value: the
container passes its live query, and the spec passes a literal. A derivation that is really a backend classification
goes onto the wire instead, per `bzh:frontend-wire-conformist`.

**Why.** A branch inside a container's `computed()` is reachable only through a component fixture with stubbed queries,
so it goes untested or gets tested through markup; a pure function over plain values is tested case by case, and a
restated backend judgment shows up there as a function with no frontend reason to exist.

**Scope.** A container is a `@Component` class calling a query-bearing inject helper — a TanStack `inject*` function, or
any `inject*` function whose body calls one, transitively — header-slot mini-containers included. The rule binds each
`computed()` imported from `@angular/core` in such a class, together with any same-class method, getter, or
function-valued property the callback calls. Presentational components and non-component `inject*` helpers are outside
it, and so is an `@Injectable` class that holds a query, even one a container provides and reads: the rule binds only
the container's own class.

**Detect.** Tooled by `web:structural-gate`'s containers-compose sweep, proven first by
`assertContainersComposeDetectorWorks`: an `if`, `switch`, `?:`, loop, or collection-transform call (`.filter`, `.map`,
`.reduce`, `.sort`, `.slice`, `.find`, `.some`, and their kin, plus `Array.from` and `Object.entries`, `.keys`,
`.values`, and `.fromEntries`) anywhere in a container's `computed()` callback, nested arrows and followed
`this.<member>()` calls included. The sweep has no exemption list. The fix keeps the `computed()` field, its name, and
its type, and replaces only its body with a call into the model, so specs keep reaching the same field. Outside the
sweep, review asks:

- Does an event-handler method no `computed()` reaches derive what a model should own?
- Does a query-option lambda (`injectFooQuery(() => x()?.id ?? null)`) carry more than a null guard?
- Does a moved derivation restate a backend classification?

**Do.** `board-page.ts` declares
`boardChunks = computed(() => withPendingBoardChanges(this.chunks(), this.pendingPromotes(), this.pendingDeletes()))`;
the deletes filter and the promote override live in `board-page.model.ts`, and `board-page.model.spec.ts` pins each
branch without a fixture.

**Don't.** `rows = computed(() => (this.rowsQuery.data() ?? []).filter((r) => r.active).map(toRowVm))` in a container —
the filter's edge cases are now testable only by stubbing `rowsQuery` and rendering the component.

**See also.** `bzh:frontend-container-presentational`, `bzh:frontend-wire-conformist`, `bzh:frontend-pending-override`.

## Empty state is gated on the read (`bzh:frontend-empty-state-gated`)

**Rule.** A view's empty-state copy renders only once the read backing it has resolved — never from a bare
`data().length === 0` check. The container maps its query's `isPending()`/`isError()` (never `isFetching()`) through
`query-state.ts`'s `asyncState`/`asyncStateOf` onto a `KitAsyncStateValue`, which the presentational view renders
through `KitAsyncState` rather than inferring `'empty'` from an array that reads `[]` during the first fetch just as
when genuinely empty. A disabled query (`enabled: false` — a conditional read with nothing selected yet) reports
`isPending()` permanently true, so its own "nothing selected" rest state is answered before the pending/error/empty
triad is consulted, or that rest state renders as an endless spinner.

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
- `chunk-detail.model.ts`'s `openWorkItems(chunkId, query)` returns the dock's own rest state for a `null` chunk id
  before ever consulting `deriveWorkItemsState`, since the dock's queries are `enabled: false` while nothing is
  selected. A selection-gated panel elsewhere composes `query-state.ts`'s
  `restingAsyncState(nothingSelected, query, isEmpty)`, which answers `'empty'` while resting and `asyncState`
  otherwise.

**Don't.** `@if (rows().length === 0) { <p>NO RUNNERS REGISTERED</p> }` off a query's `data() ?? []` with no
`isPending()`/`isError()` check anywhere in the component.
