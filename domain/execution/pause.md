# Pause

What an operator's pause stops, what keeps running, and what happens to the claim. Spoke of the
[execution hub](../execution.md).

Operator controls are declarative state, not commands: pausing appends a fact, and there is no directive queue.

## Runner-level pause

A runner-level pause has two independent brakes: the fleet's, set at the hub and read by the runner on its own contact;
and the runner's own, set on its machine — so it holds with the hub unreachable — and reported up to a hub that never
sets it. Effective paused is the OR of the two brakes, each cleared only where it was set.

The fleet's brake stops new claims and nothing else: a chunk already in flight runs to completion. The runner's own
brake also starts no process at all — no next attempt, no judgement, no resume of a dormant session — so an in-flight
chunk halts at its next step boundary, and neither a stalled worker's reap nor an exhausted attempt's escalation fires
until it lifts. Two things still happen under it. A lease minted but never spawned is reaped: it is crash residue with
no live work behind it. And an operator restart that fences out a worker is honored at once: the displaced worker,
already at a stale epoch, is killed and its attempt closed, and only the re-entry into the moved node waits for the
brake to lift — as does a restart-resume after downtime, which preempts a fenced-out session rather than waking it.

The hub refuses a registry-paused runner's claim outright — a distinct `403` denial, not the `409` of a lost
exactly-once claim race — enforced hub-side whether or not the runner has mirrored the flag.

The runner's own brake is not only operator-set: it also engages itself when the runner's spend over its trailing
ceiling window reaches the configured ceiling, the reason naming the ceiling, the window, and the spend. The operator
and the ceiling are its only engagers — a subscription's usage limit holds the runner back without braking it
([./throttling.md](./throttling.md)). Either way only an operator clears the brake; the runner never lifts it on its
own, even once the window's spend has fallen back under the ceiling.

## Per-chunk pause

Per-chunk pause is a third independent lever: it interrupts the target chunk's in-flight worker, killing only a survivor
of that interrupt, while keeping its claim — detach's counterpart, the lever that retains the route. Which statuses
admit a pause, what survives one, and how resume recovers it are owned by [../work/statuses.md](../work/statuses.md)
(`paused`); resume respawns the parked session under its unchanged session id. A paused chunk starts no worker by any
path: a step the hub applied into a next node, or a pending requeue, holds the binding instead, and the node is entered
once the pause lifts.

Pause does not freeze the chunk: an operator restart recorded while paused still mints its own epoch, and resume then
re-enters the moved node instead of the parked session ([../work/restart.md](../work/restart.md)).
