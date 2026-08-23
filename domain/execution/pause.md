# Pause — the operator's brakes

- **Operator controls are declarative state, not commands.** Pausing appends a fact; there is no directive queue.
  **Runner-level** pause has **two independent brakes**, because two parties stop a runner for different reasons: the
  **fleet's**, set at the hub and read by the runner on its own contact, and the runner's **own**, set on its machine —
  so it holds with the hub unreachable — and reported up to the hub, which never sets it. The two are **not** equally
  hard: the fleet's stops new claims and nothing else, so a chunk already in flight runs to completion under it; the
  runner's own additionally starts no process at all — no next attempt, no judgement, no resume of a dormant session —
  so an in-flight chunk halts at its next step boundary instead, and neither a stalled worker's reap nor an exhausted
  attempt's escalation fires until it lifts. Effective paused is their OR, each cleared only where it was set.
  **Per-chunk** pause is a third, independent lever targeting one chunk rather than the whole runner, and it does kill
  that chunk's in-flight worker while keeping its claim — see [work/statuses.md](../work/statuses.md) (`paused`) for
  what survives and how resume recovers it.

- **Pause is detach's deliberate counterpart: it keeps the route.** A per-chunk pause kills the chunk's live worker but
  leaves the lease, route, epoch, environments, and retry budget untouched, so resume respawns the session in place
  under the unchanged lease/epoch/session id ([work/statuses.md](../work/statuses.md)); detach is the lever that gives
  the claim away, pause is the one that holds it exactly where it is. That is a statement about what the *pause*
  changes, not a freeze on the chunk: an operator restart recorded while it is paused still mints its own epoch, and the
  resume then re-enters the moved node instead of the parked session ([work/restart.md](../work/restart.md)).

- **The hub, as claim arbiter, refuses a registry-paused runner's claim outright.** A claim from a runner the registry
  marks paused is denied before the claim race is even run — a distinct `403` denial, not the `409` a claim loses to
  another claimant on an exactly-once race. The hub enforces this itself, independent of whether the runner has already
  mirrored the pause flag on its own next pull.
