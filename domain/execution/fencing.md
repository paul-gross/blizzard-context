# Fencing

What bounds one node-step attempt, and how a stale attempt is kept from advancing the chunk. Spoke of the
[execution hub](../execution.md).

## The lease

Acquisition decides who holds the chunk; a lease records one attempt at one node — the executing party's own uncontended
single-writer bookkeeping. A lease is one node-step attempt: at a runner node, one agent session, heartbeat-renewed,
kept dormant while the chunk parks on a human ([../humans.md](../humans.md) owns parking). The heartbeat that keeps a
lease alive is a side effect of the worker's tool use — no agent cooperation required. A hub-executed node has no
session; the hub mints its lease itself, in the same write as the exit it records.

Each lease mints a fresh epoch, a counter that only rises across a chunk's attempts; the epoch is the fence every
state-advancing write is checked against.

## The stale-attempt rule (`bzh:epoch-fencing`)

Every state-advancing write for a chunk (transition, decision, artifacts) carries an epoch; a write below the chunk's
newest epoch is rejected, never recorded; a write a runner submits is rejected too unless its attempt owns that epoch;
and a terminal fact (stopped, delivered) rejects every later state-advancing write regardless of epoch. Each epoch has
one owner — the hub for an epoch it mints itself, a runner for an epoch its claim reserved or its lease took — the first
one recorded, and that owner keeps it for good. The epoch is ordinarily the producing lease's, but the fence belongs to
the chunk, not any lease — an operator restart ([../work/restart.md](../work/restart.md)) mints a hub-owned epoch with
no attempt or lease behind it, and a claim reserves the next epoch for its claimant before that claimant mints any
lease, each a fencing write setting the new floor the instant it lands, so the displaced attempt cannot still advance.

A worker presumed dead can wake and write after its successor started; fencing makes the successor authoritative and
bounces the zombie's late writes — a zombie can lose work but never land wrong work, without requiring reliable process
kills. A reap or reassignment therefore never trusts the old holder to be dead; it fences it out.

How an epoch is minted, owned, and read:

- Every claim mints its leases above the hub-supplied epoch floor: the chunk's newest epoch as the hub knows it, carried
  on the claim, never the claiming runner's local history — a first claim and a claim following a route-releasing write
  such as detach or a re-queuing migration ([../work/migration.md](../work/migration.md)) alike. A migration is fenced
  by the claim that follows it, never by its submitting attempt's own epoch.
- A claim reserves the next epoch for its claimant in the claim's own write, so the old holder's writes at or below it
  bounce from that instant — before the new holder reports anything.
- Only the runner holding the chunk's live route takes a fresh epoch — one above the newest, still unowned; any other
  mint lands only on an epoch its own runner already owns. The route here only refuses, never admits.
- A transition is never accepted because its submitter still holds the route — route tenure is not attempt fencing.
- A runner's write is refused, never recorded, when its attempt does not own the write's epoch — a hub-owned epoch, or
  one another runner owns. Its epoch alone never admits it.
- The epoch alone does not place a completion or decision at a node; [../work/transitions.md](../work/transitions.md)
  owns the guards at the write.
- A fencing write's own epoch is derived inside the transaction recording it, never from a read the write no longer
  holds.
- The party honoring the fence reads it generously — the hub's floor lags leases it has not yet heard of, so a fencing
  write can land level with the attempt it displaces, and level is displaced.

The one exception is a hub action's record of a merge that has already happened on a forge — the repository's landed
marker, its landed row, and the close intents beside them. It is admitted past the fence: a terminal chunk or a stale
epoch does not refuse it, because it records what the forge already did rather than a step the chunk may take. The fence
is still read on that write, and where it would have refused, the action is told so and touches no further repository.
It stays idempotent per chunk, node, marker name, and epoch.
