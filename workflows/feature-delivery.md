# Feature delivery (`bzh:feature-delivery`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity.

## Rule

Working a node of a blizzard chunk, perform exactly the node role your session was primed with, then exit: blizzard
itself orchestrates feature delivery, and your reported facts move the chunk — never hand-drive the delivery sequence.
The default graph triages a chunk into one of three delivery lanes — `bas-dwf`, `adv-dwf`, or `bas-hwf`. A node worker
owes its node's prompt, done to [../standards/index.md](../standards/index.md) and proven before exit by the matrix rows
for the touched surface ([../verification/blizzard.md](../verification/blizzard.md)) — reported as facts and artifacts,
never a self-landed merge.

## Why

That choreography is domain-modeled platform behavior — exactly-once tenure, facts-derived statuses, hub-executed
delivery ([../domain/index.md](../domain/index.md)) — and an agent improvising commit-land-watch steps races the
orchestrator, producing double work.

## Scope

This rule governs delivery through blizzard. Ecosystem work delivered outside a fleet — landing to `master` by hand from
a winter feature environment — follows `workspace:/context/project/contributing.md` §Delivery and
`workspace:/context/winter/worktree-ops.md`, plus [../CONTRIBUTING.md](../CONTRIBUTING.md) for harness changes.

## What the platform owns

The choreography end to end — sequencing between nodes, the review carry-back, retries and escalation, delivery,
landing. A worker that cannot finish just exits with its facts, and the platform derives what happens next.

- Delivery is a hub-executed node, not an agent's role. Every code-delivering lane delivers through its `deliver` node's
  `land` action, and how each repository lands is that repository's landing policy, which
  [../domain/artifacts/delivery.md](../domain/artifacts/delivery.md) owns. Under the `merge-on-checks` policy the action
  opens a pull request for the repository, and the hub merges it with a merge commit only after a terminal-green check
  verdict.
- A human enters only where invited or where failure parks the chunk — asks, gate decisions, takeover
  ([../domain/humans.md](../domain/humans.md)).

## Detect

- A worker session merging a branch, pushing `master`, or opening its own pull request.
- A review node committing fixes to the work it reviews.

## Do

- A build worker whose tests pass pushes its feature branch, declares the tip as its node's commit artifact, and ends
  its session; the `deliver` node lands the work.
- A review worker that finds a defect records the finding, answers its node's judgement, and exits; the graph carries
  the chunk back to a build node.

## Don't

- Exceed the node role — a review worker does not fix what it reviews; the graph separates stations so their outputs
  stay independent.
- Land your own work from a node: `gh pr create`, `gh pr merge`, or `git push origin master` in a build worker's
  session.
