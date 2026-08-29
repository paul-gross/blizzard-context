# Artifact scope reads

This spoke owns blizzard's two rules for artifact-scope read locality; the macro-shape hub is
[../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Graph-scope reads are local (`bzh:graph-scope-reads-local`)

**Rule.** A graph's baked-in `artifacts:` declarations reach the worker with no hub call in the read path: the mint
stores each entry's already-inlined content, the node envelope carries the whole set, `Spawner._mint` pins that set into
the runner's own store as it mints the lease, and the worker's `--scope graph` read is answered from that pin alone,
keyed on the lease's `graph_id`. Keying the pin on `graph_id`, not the lease, lets one copy serve every chunk and
attempt on that mint, even a lease pinned to a mint the graph's name has since moved past.

**Why.** A mint is immutable, so the hub never holds a newer answer; and a declaration authored to be consulted
repeatedly (a docket, a rubric) would otherwise put a round-trip — and a hub outage — in the path of prose the runner
already holds.

**Scope.** Node scope keeps its hub-proxied forward (the worker holds no hub credential of its own), so only the graph
half is local; node-scope artifacts are produced per attempt, the hub alone holds their newest version, and the mint
itself remains the hub's — the rule binds only the declarations' path from envelope to mint-time pin to the worker's
read route.

**Detect.** A graph-scope read path that consults the hub — a proxy forward, an envelope re-fetch, a re-read call, or a
design leaving the declarations off the envelope; or a graph-scope read that fails when the hub is unreachable.

**Do.** `_graph_rows` in `src/blizzard/runner/api/artifacts.py` resolves the rows through
`IReadRunnerStore.graph_artifacts_for_graph(lease.graph_id)` with no `HubProxy`; the service test
`test_graph_scoped_artifact_reads_from_the_runners_own_pin_with_the_hub_unreachable` holds that read with the hub
unreachable.

**Don't.** Answering graph scope through the same hub-proxy forward node scope uses, on the grounds that one read path
is simpler than two — every declaration read then fails with the hub, which is the property the rule exists to buy.

**See also.** `bzh:system-scope-reads-live`, below — the sibling rule stating why the third scope is bound by the
opposite liveness rule, for its own reason. `bzh:graph-artifact-pointer-fallback` in
[../../standards/worker-nodes/graph-artifact-pointers.md](../../standards/worker-nodes/graph-artifact-pointers.md) owns
the fallback a prompt pointing at a baked declaration owes, because a lease pinned before the runner recorded the
declarations reads an empty pin.

## System-scope reads are live (`bzh:system-scope-reads-live`)

**Rule.** A worker's `--scope system` read always crosses the hub, on every call: `_system_rows` and `_system_hit` proxy
both `list` and `get` through `HubProxy` with no runner-local pin, cache, or mint-time copy ever standing in for the
upstream answer — unlike graph scope's mint-time pin, a system-scope read has nothing to be pinned at mint, because the
document it reads is not the graph's.

**Why.** The published document IS the shape the hub's own validator judges a submission against, and the two ship
together: a delivery script validates a run's submission against exactly the live `garden/finding-format` or
`garden/proposal-format` text, so a runner-local copy would hand a worker a stale validator target the moment blizzard
tightens the format under a mint nobody re-cut.

**Scope.** Binds `ArtifactScope.SYSTEM` reads specifically, not "every hub-proxied forward" generally: node scope is
also hub-proxied, since the worker holds no hub credential of its own, but a node-scope miss reflects an upstream node's
own output rather than a staleness risk in a published format. System scope's rule is narrower and stricter than node
scope's forward happening to reach the hub — it is that no runner-local state may ever answer the call, on purpose, so
that staleness cannot creep in through a future optimization.

**Detect.** A system-scope read served from anything the runner mirrors ahead of the call — a store row, a pin, a cache
— rather than a live upstream fetch; a design that answers `--scope system` when the hub is unreachable instead of
failing the read.

**Do.** `_system_rows` and `_system_hit` in `src/blizzard/runner/api/artifacts.py` call through `HubProxy` on every
invocation, with no local store consulted; the service test
`test_system_scope_read_fails_rather_than_resolving_locally_when_the_hub_is_unreachable` in
`tests/service/test_system_artifacts_service.py` holds the read failing outright with the hub unreachable, never
answering from nothing.

**Don't.** Answering system scope from a local cache or pin "because it's simpler" or "to save a round-trip" — that is
exactly the staleness the scope exists to prevent: the worker would validate against a version of the document that may
no longer be the one the hub's own validator judges by.

**See also.** `bzh:graph-scope-reads-local`, above — the two scopes are governed by opposite liveness rules for opposite
reasons, and citing one without the other invites assuming they behave alike.
