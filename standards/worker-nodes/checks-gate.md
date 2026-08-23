# Gating a choice on the node's checks

How a graph author makes a choice mechanically unselectable while the node's `checks:` are red.

Parent: [../worker-nodes.md](../worker-nodes.md).

## `requires_checks` makes green checks a precondition of a choice (`bzh:worker-node-checks-gate`)

**Rule.** A choice may declare `requires_checks: true`; selecting it while any of the node's `checks:` is red is treated
as a failure, not a judgement — the engine consumes a retry and re-queues a fresh attempt, injecting the red evidence
into the re-attempt's judgement. No config flag governs the gate: it applies iff a choice declares `requires_checks`.
The gate is enforced twice off one shared predicate (`ChecksGate.violated` in `wire/completion.py`) — the runner's own
gate plus the hub's completion backstop — so a runner that skips its gate is still fenced by the hub.

**Why.** Without the gate, "checks are green" is enforced only socially — prompt prose plus the worker's honest
self-report — and the prose and the `checks:` YAML can silently drift. The gate makes the graph author's intent
mechanical without taking routing authority from the worker.

**Scope.** The runner runs the node's `checks:` at worker exit;
[../../domain/graphs/edges.md](../../domain/graphs/edges.md) owns the concept and which ill-formed gate shapes the
mint-time validator rejects. A red check reported through a non-gated choice (`fail`) routes normally. Declare `checks:`
and the gate only on a single-application graph, never a reusable one: `checks:` makes a graph application-specific
(`bzh:app-agnostic-graphs`, [../../architecture/system-shape/graphs.md](../../architecture/system-shape/graphs.md)).

**Do.** Gate the choice that must not be taken over red — typically build's `pass`, never its `fail`.

**Don't.** An engine-routed "check-failed" edge that overrides the worker's choice — rejected by design: it would split
routing authority between the graph author's choices and a mechanical router, and discard the worker's context-rich
`fail` reporting path.
