# Failure and recovery

- **Reap** expires a lease with no live work behind it: one minted but never spawned, and one whose worker is still
  alive but has stopped beating. A worker that has **exited** is never reaped — its exit is its done declaration, and
  judging it belongs to the step that advances the chunk — **even an `error_during_execution` exit** (wontfix,
  blizzard#284): the runner never observes a worker's exit status at all, so there is no code to branch on instead — the
  backstop is exit-status-independent, a node's declared `produces:` plus the delivery-time empty-delivery refusal
  catching what an errored exit failed to produce. Reap ends the **attempt** — retry, or escalate on exhaustion
  ([humans/escalation.md](../humans/escalation.md)) — never by itself the chunk's tenure or its environments.
- **Requeue** is two operations sharing one name. The **hub's** supersedes the escalation *and* releases the route,
  returning the chunk to the queue for whoever claims it next. The **holding runner's** — the hand-back after a takeover
  ([humans/takeover.md](../humans/takeover.md)) — keeps route, environments and tenure, and simply re-attempts the
  current node in place against the retry budget it already had.
- **Reassignment** moves a held chunk to another runner — the supported exception to stickiness: the new runner rebuilds
  the environment from the chunk's commit artifacts, mints leases above the hub-supplied epoch floor, and may adopt
  unsubmitted in-progress work it finds ahead of the last submitted artifact commit.
- **Detach** forcibly releases a chunk from its runner: the route is released, the chunk re-derives ready, and the next
  claim's epoch floor fences the old runner.
