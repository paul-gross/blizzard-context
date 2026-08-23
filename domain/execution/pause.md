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
until it lifts.

The hub refuses a registry-paused runner's claim outright — a distinct `403` denial, not the `409` of a lost
exactly-once claim race — enforced hub-side whether or not the runner has mirrored the flag.

## Per-chunk pause

Per-chunk pause is a third independent lever: it kills the target chunk's in-flight worker while keeping its claim —
detach's counterpart, the lever that retains the route. What survives and how resume recovers it is owned by
[../work/statuses.md](../work/statuses.md) (`paused`); resume respawns the parked session under its unchanged session
id.

Pause does not freeze the chunk: an operator restart recorded while paused still mints its own epoch, and resume then
re-enters the moved node instead of the parked session ([../work/restart.md](../work/restart.md)).
