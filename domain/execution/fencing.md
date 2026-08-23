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

**Rule.** Every state-advancing write for a chunk (transition, decision, artifacts) carries an epoch; a write below the
chunk's newest epoch is rejected, never recorded; and a terminal fact (stopped, delivered) rejects every later
state-advancing write regardless of epoch. The epoch is ordinarily the producing lease's, but the fence belongs to the
chunk, not any lease — an operator restart ([../work/restart.md](../work/restart.md)) mints an epoch with no attempt or
lease behind it, a fencing write setting the new floor the instant it lands, ahead of the re-entry's own lease, so the
displaced attempt cannot still advance.

**Why.** A worker presumed dead can wake and write after its successor started; fencing makes the successor
authoritative and bounces the zombie's late writes — a zombie can lose work but never land wrong work, without requiring
reliable process kills.

**Detect.**

- A state-advancing write path with no epoch check.
- A reap or reassignment that trusts the old holder to be dead instead of fencing it out.
- A migration relying on its submitting attempt's own epoch instead of next-claim fencing.
- The epoch check skipped once a chunk is terminal.

**Do.**

- Every fresh claim of a re-queued chunk (a reassignment, or a route-released re-queue such as detach or migration —
  [../work/migration.md](../work/migration.md)) mints new leases above the hub-supplied epoch floor: the chunk's newest
  epoch as the hub knows it, carried on the claim, never the claiming runner's local history.
- A runner that never drove the chunk still mints strictly above every prior attempt, so the old holder's in-flight
  submission bounces on arrival.
- Derive a fencing write's own epoch inside the transaction recording it, never from a read the write no longer holds.
- The party honoring the fence reads it generously — the hub's floor lags leases it has not yet heard of, so a fencing
  write can land level with the attempt it displaces, and level is displaced.

**Don't.** Never accept a transition because the submitter still holds the route — route tenure is not attempt fencing.
