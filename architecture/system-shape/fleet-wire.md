# Fleet wire

This spoke owns what a hub change may do to the wire a runner reaches across a version-skewed deploy; the macro-shape
hub is [../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## A hub change to the runner-reached wire is additive, or acknowledged (`bzh:fleet-wire-additive`)

**Rule.** A change to a route, request or response schema, or enum the runner reaches must be additive to a
previous-minor runner's parse path, unless a commit that step lands on `master` carries a Conventional Commits `!`
marker in its subject, acknowledging the break — the commit itself for a direct landing, or the merge or any commit it
merges. A removed route or field keeps its old form beside the replacement, the way `GET /api/fleet/queue/peek`
(`src/blizzard/hub/api/fleet.py`) stays beside its matched `POST` counterpart.

**Why.** The hosted hub redeploys itself on every `master` commit while its runners are redeployed by hand
(`docs/versioning.md`'s skew window), so an unacknowledged break reaches a live runner with nothing to catch it before
the fleet wedges.

**Detect.** `blizzard:wire-compat` ([../../verification/blizzard.md](../../verification/blizzard.md)) is the mechanical
check — it fails a pull request against its merge-base and fails a push to `master` against the last commit `edge` was
published from. Its declared surface already covers the 17 `HubProxy` forwards under `src/blizzard/runner/api/`, since
every one targets an `/api/fleet/...` path; a runner call reaching the hub outside that surface constant is invisible to
it.

**Do.** A new optional response field; a new route kept beside its replacement; and, when a new runner→hub call reaches
outside the declared surface, extending `blizzard:wire-compat`'s surface constant in the same change.

**Don't.** A response enum gaining a value with no `!` on any commit the step lands — an older runner's closed-enum
parse (e.g. `ChunkStatus`, `ApplyOutcome`) raises on the unrecognized value instead of round-tripping it.

`bzh:fleet-wire-additive` is tooled by `blizzard:wire-compat`
([../../verification/blizzard.md](../../verification/blizzard.md)); no exemption stands.

**See also.** `bzh:shared-kernel` ([../clean-architecture.md](../clean-architecture.md)): where a vocabulary type the
wire carries is defined.
