# Feature delivery (`bzh:feature-delivery`)

## Rule

Feature delivery is orchestrated by blizzard itself: a chunk travels its workflow graph — the default graph triages it
into a delivery lane (`bas-dwf` / `adv-dwf` / `bas-hwf`), whose canonical shape is `build → review → deliver` — and the
platform owns the choreography end to end: sequencing between nodes, the review carry-back, retries and escalation,
delivery, and landing. An agent never drives that sequence by hand — it performs exactly the node role its session was
primed with, exits, and the facts it reports move the chunk.

## Why

The delivery choreography is domain-modeled platform behavior — exactly-once tenure, facts-derived statuses,
hub-executed delivery ([../domain/index.md](../domain/index.md)) — so an agent improvising commit-land-watch steps
around it races the orchestrator it works under and produces the double-work the model exists to prevent.

## What each participant owes

- **A worker at a node** (build, review, …) owes its node's prompt, done to
  [../standards/index.md](../standards/index.md) and proven by the matrix rows for the touched surface
  ([../verification/blizzard.md](../verification/blizzard.md)) before it exits — its output reported as facts and
  artifacts, never a self-landed merge.
- **The hub** executes delivery itself — the merge-queue landing is a hub-executed node, no agent's role
  ([../domain/artifacts/delivery.md](../domain/artifacts/delivery.md)).
- **A human** enters only where invited or where failure parks the chunk — asks, gate decisions, takeover
  ([../domain/humans.md](../domain/humans.md)).

## Scope

This file governs feature delivery **through** blizzard. Work on the blizzard ecosystem itself delivered outside a fleet
— an agent in a winter feature environment landing to `master` by hand — follows the workspace delivery rules instead
(`workspace:/context/project/contributing.md` §Delivery, with the git mechanics in
`workspace:/context/worktree-ops.md`), plus [../CONTRIBUTING.md](../CONTRIBUTING.md) for changes to this harness.

## Don't

- Hand-drive the choreography from inside a node session — rebasing, merging, pushing to `master`, or watching CI on the
  chunk's behalf. The deliver node lands the work; the reported facts move the chunk.
- Exceed the node role — a build worker delivering its own commit, a review worker fixing what it reviews. The graph
  separates the stations precisely so their outputs stay independent.
- Treat retries, escalation, or the review carry-back as the worker's to manage — a worker that cannot finish exits with
  its facts, and the platform derives what happens next.

## See also

- [../domain/index.md](../domain/index.md) — the behavioral model of the orchestration this file defers to.
- [./release.md](./release.md) — cutting a release from the `master` the deliver node feeds.
