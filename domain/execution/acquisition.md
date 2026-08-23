# Acquisition and the route

**Acquisition** is the hub granting a ready chunk to exactly one runner — the one point of genuine cross-runner
contention, and where fleet exactly-once is upheld. The claim is **claim-by-route**: the runner peeks the hub-ordered
queue, acquires the environments, and posts the complete route; the hub accepts exactly one claim per chunk.

The **route** is the locator fact that makes every held chunk findable: chunk → runner → workspace → environment. The
environment identifier is opaque to the hub — it knows *which* environment, never what an environment is.

- **Runner stickiness.** Consecutive node-steps of a chunk run on the holding runner — no re-queue between nodes.
- **A route is released** by the write that gives the chunk's tenure back: **detach** — a superadmin's forcible release
  — along with the **hub's requeue** of an escalated chunk (§Failure and recovery distinguishes it from the runner's
  own) and a **migration that re-queues onto another graph**; after each the chunk re-derives `ready` and the old runner
  is fenced out by the next claim. **Stop** releases it too, but terminally — there is no next claim to fence. So does a
  **hub** node landing the chunk's terminal.
- **A terminal chunk may still hold a live route, and holding one grants nothing.** A terminal transition authored by a
  **runner** node — the shape [work/statuses.md](../work/statuses.md) (`done`) allows, where a graph routes further
  runner work after landing — releases no route, so a `done` chunk can go on carrying the route of the runner that
  finished it. That is untidy, not unsafe: the claim path refuses a terminal chunk outright, so a retained route confers
  no tenure on anyone. What it does mean is that **route liveness is not a proxy for "being worked"** — a consumer
  folding routes into live occupancy must key on status, which is why the chunk summary reports a terminal chunk as
  unrouted for the fleet registry's claim lines and slot bar, while the chunk detail keeps the raw route fact for the
  "where was this worked" read.
- **A restart keeps the route too, and discards the attempt.** Forcing a chunk onto a node
  ([work/restart.md](../work/restart.md)) leaves route, tenure and environments exactly where they are — only the lease,
  epoch and session are given up — so the holding runner re-enters the node in the same environments rather than the
  chunk going back to the queue. That holds when the move crosses a graph: the migration it records re-pins the chunk
  without re-queuing it, so it is not one of the releasing writes above.
