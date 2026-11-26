# Disjoint diffs

How the suite's shared files are shaped so two agents editing different features do not collide. A spoke of the
[frontend structure hub](../frontend-structure.md); the rule follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`), rule-per-section.

## Shared files grow additively (`bzh:frontend-disjoint-diffs`)

**Rule.** Two agents changing two different features must produce diffs that touch no shared file beyond one entry
export line and one SSE registry row. A feature's public surface is the export lines naming it in its entry files under
`fleet/src/entries/` (`bzh:frontend-weight-class-entries`, [eager-shell.md](./eager-shell.md)); what an entry exports is
decided by a consumer outside the unit that declares it — a sibling only the feature's own components mount stays
unexported, so the public surface names what is actually re-stackable. A live feature registers its invalidated query
keys as a declarative row in its own daemon's SSE dispatch registry — the hub's board in `EVENT_INVALIDATION_REGISTRY`
(`hub/src/app/core/live/hub-live-updates.ts`), the runner's local panel in
`runner/src/app/core/live/runner-live-updates.ts` — never a `case` added to the shared
`LiveInvalidationSpine.dispatch()` (`fleet/src/lib/sse/live-invalidation-spine.ts`) both registries drive. The two
daemons' registries never share a line range because they never share a file.

Each daemon owns its whole live plane: its query keys (`hub/src/app/core/query-keys.ts`,
`runner/src/app/core/query-keys.ts`) and its registry sit in its own app. `fleet` keeps only what both daemons reach —
the SSE transport, `LiveInvalidationSpine`, the coalesce window, both stream vocabularies (`sse/hub-events.domain.ts`,
`sse/runner-stream.domain.ts`) and their translators, and the chunk and transcript key helpers that take a plane root.

**Why.** A monolithic surface file and a hand-written dispatch `switch` are guaranteed merge conflicts — every in-flight
feature touches the same line range; entries that group by feature and weight, and a data-shaped registry, make adding a
feature additive, not contended.

**Detect.**

- An entry export no consumer outside the unit that declares it imports, or a `public-api.ts` statement that re-exports
  anything but an entry — `web:structural-gate`'s disjoint-diffs sweep catches both mechanically.
- A bare `export *` in an entry, `shell-api.ts`, or `runner-shell-api.ts`, which re-exports a file's whole surface with
  no diff on the entry when it grows — `web:lint`'s `no-restricted-syntax` rule over `ExportAllDeclaration` catches this
  one mechanically; `public-api.ts` itself is exempt, since it legitimately stars the entries.
- A live feature's invalidation expressed as anything other than a row in its own daemon's registry — the shared
  `LiveInvalidationSpine.dispatch()` is the one place a `case` could physically be added, and it is private to
  `live-invalidation-spine.ts`; a registry row in one daemon for a query key that belongs to the other.

**Do.**

- `entries/transcripts.ts` names every transcripts symbol a consumer outside `transcripts/` imports at that weight, and
  a sibling mounted only by its own feature stays unexported.
- A new live board feature adds a row keyed by its event type to `EVENT_INVALIDATION_REGISTRY` — an `openLookup` table
  exhaustive over `HubEventKind`, so an unhandled domain event is a compile error, while a type this build does not know
  stales nothing (`bzh:frontend-open-vocabulary`, [wire.md](./wire.md)).

**Don't.** Two features both editing the same span of one file to add their exports, or both adding a `case` to the same
`switch`.
