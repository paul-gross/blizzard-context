# Feature delivery (`bzh:feature-delivery`)

**Rule.** Blizzard itself orchestrates feature delivery: the default graph triages a chunk into one of three delivery
lanes — `bas-dwf`, `adv-dwf`, or `bas-hwf`. An agent performs exactly the node role its session was primed with and
exits; its reported facts move the chunk — it never hand-drives the delivery sequence.

**Why.** That choreography is domain-modeled platform behavior — exactly-once tenure, facts-derived statuses,
hub-executed delivery ([../domain/index.md](../domain/index.md)) — and an agent improvising commit-land-watch steps
races the orchestrator, producing double work.

**Scope.** This rule governs delivery through blizzard. Ecosystem work delivered outside a fleet — landing to `master`
by hand from a winter feature environment — follows `workspace:/context/project/contributing.md` §Delivery and
`workspace:/context/worktree-ops.md`, plus [../CONTRIBUTING.md](../CONTRIBUTING.md) for harness changes.

## What the platform owns

The choreography end to end — sequencing between nodes, the review carry-back, retries and escalation, delivery,
landing. A worker that cannot finish just exits with its facts, and the platform derives what happens next.

- The merge-queue landing is a hub-executed node — delivery is the hub's own act, no agent's role
  ([../domain/artifacts/delivery.md](../domain/artifacts/delivery.md)).
- A human enters only where invited or where failure parks the chunk — asks, gate decisions, takeover
  ([../domain/humans.md](../domain/humans.md)).

## What a node worker owes

Its node's prompt, done to [../standards/index.md](../standards/index.md) and proven before exit by the matrix rows for
the touched surface ([../verification/blizzard.md](../verification/blizzard.md)) — reported as facts and artifacts,
never a self-landed merge.

**Don't.** Exceed the node role — a review worker does not fix what it reviews; the graph separates stations so their
outputs stay independent.
