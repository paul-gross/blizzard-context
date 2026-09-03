# Acquisition

How a chunk is granted to a runner, what the route locates, and which writes give tenure back. Spoke of the
[execution hub](../execution.md).

Acquisition is the hub granting a ready chunk to exactly one runner — the one point of cross-runner contention, where
fleet exactly-once is upheld. The claim is claim-by-route: the runner peeks the hub-ordered queue, acquires the
environments, and posts the complete route; the hub accepts exactly one claim per chunk. The environment identifier is
opaque to the hub — it knows which environment, never what an environment is.

Which entry a runner claims out of a peek carrying a [blocked marking](../work/statuses.md#the-blocked-marking) is that
runner's own choice, not the hub's: by default it reaches past a marked entry for the first unmarked one, rather than
spending an attempt on one it already knows is not yet claimable. An operator may instead configure a runner to hold at
a marked entry and claim nothing that tick — strictness the runner chooses, not a fleet-wide rule.

Tenure is sticky: consecutive node-steps of a chunk run on the holding runner, never re-queued between nodes.

## The route

The route is the locator fact making every held chunk findable: chunk to runner to workspace to environment. Route
liveness is not a proxy for being worked: a consumer folding routes into live occupancy must key on status.

## Giving tenure back

Three writes release a route by giving tenure back: detach, the hub's requeue of an escalated chunk, and a migration
that re-queues the chunk onto another graph. After each, the chunk re-derives ready and the next claim fences the old
runner out. What detach and the requeue each are is owned by [./recovery.md](./recovery.md), which also distinguishes
the hub's requeue from the holding runner's own.

Stop releases the route terminally — no next claim to fence — and a hub node landing the chunk's terminal releases it
too.

What does not release:

- A restart ([../work/restart.md](../work/restart.md)) keeps route, tenure, and environments, giving up only lease,
  epoch, and session: the holding runner re-enters the node in the same environments rather than the chunk re-queuing.
- A cross-graph restart records a migration that re-pins the chunk without re-queuing it — not one of the releasing
  writes.
- A terminal chunk can still hold a live route: a terminal transition authored by a runner node (the done shape
  [../work/statuses.md](../work/statuses.md) allows) releases nothing, so a done chunk may keep its finisher's route —
  harmless, because the claim path refuses a terminal chunk outright, so the route confers no tenure.
