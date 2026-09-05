# Disjoint diffs

How the suite's shared files are shaped so two agents editing different features do not collide. A spoke of the
[frontend structure hub](../frontend-structure.md); the rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Shared files grow additively (`bzh:frontend-disjoint-diffs`)

**Rule.** Two agents changing two different features must produce diffs that touch no shared file beyond one sub-barrel
export line and one SSE registry row. Each feature directory under `fleet/lib/` owns an `index.ts` sub-barrel
re-exported once from the root `public-api.ts`; what a sub-barrel exports is decided by a consumer outside its own
feature directory — a sibling only the feature's own components mount stays unexported, so the public surface names what
is actually re-stackable. A live feature registers its invalidated query keys as a declarative row in its own daemon's
SSE dispatch registry — the hub's board in `sse/fleet-live.ts`'s `EVENT_INVALIDATION_REGISTRY`, the runner's local panel
in its own disjoint `RUNNER_EVENT_INVALIDATION_REGISTRY` (`local-panel/src/lib/runner-live-updates.ts`) — never a `case`
added to the shared `LiveInvalidationSpine.dispatch()` (`fleet/sse/live-invalidation-spine.ts`) both registries drive.
The two daemons' registries never share a line range because they never share a file.

**Why.** A monolithic `public-api.ts` and a hand-written dispatch `switch` are guaranteed merge conflicts — every
in-flight feature touches the same line range; sub-barrels and a data-shaped registry make adding a feature additive,
not contended.

**Detect.**

- A new top-level export added directly to `public-api.ts` instead of a feature sub-barrel; a sub-barrel export no
  consumer outside its own feature directory imports.
- A sub-barrel `export *`, which re-exports the feature directory's whole surface with no diff on the barrel when it
  grows — `web:lint`'s `no-restricted-syntax` rule over `ExportAllDeclaration` in `projects/*/src/lib/*/index.ts`
  catches this one mechanically; the root `public-api.ts` itself is exempt, since it legitimately stars its sub-barrels.
- A live feature's invalidation expressed as anything other than a row in its own daemon's registry — the shared
  `LiveInvalidationSpine.dispatch()` is the one place a `case` could physically be added, and it is private to
  `live-invalidation-spine.ts`; a registry row in one daemon for a query key that belongs to the other.

**Do.**

- `chunks/index.ts` re-exports every chunks-feature symbol a consumer outside `chunks/` imports, and `public-api.ts`
  carries one `export * from './lib/chunks'` line; `chunk-detail/`'s `ChunkDetailHeader`, mounted only by its own
  feature, stays unexported.
- A new live board feature adds a row keyed by its event type to `EVENT_INVALIDATION_REGISTRY` — a
  `Record<HubEventType, (data) => readonly (readonly unknown[])[]>`, exhaustive over `HUB_EVENT_TYPES` so an unhandled
  event type is a compile error — and a new live runner-panel read does the same in
  `RUNNER_EVENT_INVALIDATION_REGISTRY`, exhaustive over `RunnerEventType`: each registry exhaustive over its own
  daemon's event union, never growing a branch for the other's kind.

**Don't.** Two features both editing the same span of `public-api.ts` to add their exports, or both adding a `case` to
the same `switch`.
