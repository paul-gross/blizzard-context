# Recovery

What happens when a lease expires, an attempt is exhausted, or a chunk must change runner. Spoke of the
[execution hub](../execution.md).

## Reap

Reap expires a lease with no live work behind it: one minted but never spawned, or one whose worker is alive but no
longer beating. It ends the attempt — retry, or escalation on exhaustion
([../humans/escalation.md](../humans/escalation.md)) — never by itself the chunk's tenure or environments.

A worker that has exited is never reaped: its exit is its done declaration, and judging it belongs to the step that
advances the chunk. Even an error-during-execution exit is never reaped: the runner never observes exit status, so
nothing exists to branch on — the backstop is the node's declared `produces:` plus the empty-delivery refusal at
delivery time, catching what the errored exit failed to produce regardless of exit status.

## Requeue

Requeue names two operations. The hub's supersedes the escalation and releases the route, returning the chunk to the
queue for the next claimant. The holding runner's own — the hand-back after a takeover
([../humans/takeover.md](../humans/takeover.md)) — keeps route, environments, and tenure, re-attempting the current node
in place against its existing retry budget.

## Detach

Detach is a superadmin's forcible release of a chunk from its runner: route released, the chunk re-derives ready, and
the next claim's epoch floor fences the old runner out.

## Reassignment

Reassignment moves a held chunk to another runner — the supported exception to stickiness: the new runner rebuilds the
environment from the chunk's commit artifacts, mints leases above the hub-supplied epoch floor, and may adopt
unsubmitted work found ahead of the last submitted artifact commit.
