# Disjoint diffs across parallel agents

How the suite's shared files are shaped so two agents editing different features do not collide. Spoke of the
[frontend structure hub](../frontend-structure.md); each rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Sub-barrels and the SSE registry are the disjoint-diff mechanism (`bzh:frontend-disjoint-diffs`)

**Rule.** Two agents changing two different features must produce diffs that touch no shared file beyond one sub-barrel
export line and one SSE registry row. Each feature directory under `fleet/lib/` owns an `index.ts` sub-barrel
re-exported once from the root `public-api.ts`; a live feature registers its invalidated query keys as a declarative row
in **its own daemon's** SSE dispatch registry rather than a new `case` in a hand-written switch. The mechanism is not
singular: the hub's board registers in `sse/fleet-live.ts`'s `EVENT_INVALIDATION_REGISTRY`, and the runner's local panel
registers in its own, disjoint `RUNNER_EVENT_INVALIDATION_REGISTRY` (`local-panel/src/lib/runner-live-updates.ts`) — one
row in the registry that owns the daemon a feature actually reads from, never a case added to the shared
`LiveInvalidationSpine.dispatch()` (`fleet/sse/live-invalidation-spine.ts`) both registries drive. What a sub-barrel
exports is decided by **a consumer outside its own feature directory**, not by membership in that directory: a sibling
only the feature's own components mount stays unexported, so the public surface names what is actually re-stackable
rather than everything present.

**Why.** A single monolithic `public-api.ts` and a hand-written event-dispatch `switch` are both **guaranteed merge
conflicts**: every feature that adds an export or a live-update path touches the same line range of the same file as
every other feature in flight. Sub-barrels and a data-shaped registry turn "add a feature" into "add a file plus one
export line plus one table row" — additive, not contended. A second daemon growing its own registry rather than reaching
into the first's keeps that guarantee: the hub's and the runner's registries never share a line range because they never
share a file.

**Detect.** A new top-level export added directly to `public-api.ts` instead of a feature sub-barrel; a live feature's
invalidation logic expressed as anything other than a row in its own daemon's registry — the shared
`LiveInvalidationSpine.dispatch()` is the one place a `case` could physically be added, and it is private to
`live-invalidation-spine.ts`; a live feature's invalidation logic added as a case in one daemon's registry for a query
key that actually belongs to the other; a sub-barrel export no consumer outside its own feature directory imports.

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
