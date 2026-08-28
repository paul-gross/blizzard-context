# Runner transcript reads

This spoke owns which plane serves a read of transcript data made for runner consumption; the macro-shape hub is
[../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Runner reads stay on the runner plane (`bzh:runner-plane-transcript-reads`)

**Rule.** A read of transcript data made for runner consumption — including a node-grouped read spanning whatever
transcript a chunk's history holds — is served from the runner plane: the runner's own `transcript_segments` store, or
the runner-scoped fleet route once a segment has shipped. It is never served by relaxing the operator-plane transcript
router's `reject_runner_principal` gate, and no runner-side code proxies to that router in place of its own store or
route.

**Why.** The operator plane carries no per-runner confinement, so widening it to serve a runner read exposes every
lease's transcripts to every runner, while the runner plane's existing ownership check already confines a read to the
requesting runner's own leases (`blizzard/docs/deployment/runner-auth.md` owns that check) — relaxing the boundary buys
nothing a plane-local read didn't already have.

**Detect.** A change removing or conditionally bypassing `reject_runner_principal` on
`blizzard/src/blizzard/hub/api/transcripts.py`'s router, or a new operator-plane transcript route with no runner-id
filter, motivated by a runner needing to read transcripts across nodes or leases; or new runner-side code calling an
operator-plane transcript endpoint instead of its own store or the runner-scoped fleet route.

**Do.** Serve a runner-context transcript read from the runner's own store, keyed
`(chunk_id, node_id, epoch,
generation)` (`blizzard/src/blizzard/runner/store/schema.py:486`), or through the
runner-scoped `GET /api/fleet/chunks/{chunk_id}/transcript-segments` route, gated by `_demand_lease_owner`
(`blizzard/src/blizzard/hub/api/fleet.py:111,570`). `TranscriptService.for_lease`
(`blizzard/src/blizzard/runner/transcripts/service.py:44`) already resolves local-versus-hub per lease behind one seam —
extend that seam for a future cross-runner requirement rather than opening the operator router.

**Don't.** Relax or bypass `reject_runner_principal` on `blizzard/src/blizzard/hub/api/transcripts.py:36`'s router to
let a runner read node-grouped transcripts — that widens the whole operator transcript router's exposure to serve one UI
feature.

### Recorded positions

Stated so a reviewer need not re-derive them:

- `blizzard#373` weighed node-grouped runner transcript reads under two shapes: (a) make the operator plane serve
  runners, either by chunk-scoping the existing runner-scoped fleet route or by relaxing `reject_runner_principal`; (b)
  serve the read from the runner's own `transcript_segments` table alone. Chunk-scoping the safe (a) variant inherits
  the same runner confinement `_demand_lease_owner` and the runner-scoped store already apply, so it returns the same
  view (b) does at the cost of a hub round-trip — its completeness advantage over (b) is illusory. Only relaxing
  `reject_runner_principal` is genuinely complete across runner hands, and that widens the whole operator router past
  what the feature justifies. (b) is the recommendation: the cheapest way to get exactly what the runner plane already
  permits, and it stays extensible — `TranscriptService.for_lease` already resolves local-versus-hub per lease, so a hub
  half can be added behind that seam without reopening the operator boundary if cross-runner completeness ever becomes a
  real requirement.
