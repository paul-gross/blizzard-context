# Lease, epoch, and fencing

A **lease** is one node-step attempt. At a runner node that means one agent session, renewed by heartbeat and kept
dormant while the chunk parks on a human ([humans.md](../humans.md)); a **hub**-executed node has no session at all, and
the hub mints that node's lease itself, in the same write as the exit it records. It is the executing party's own
single-writer bookkeeping — a runner has no rival on its own machine, the hub none over its own nodes — in deliberate
contrast to acquisition, the contended grant at the hub. Distinct concepts: acquisition decides *who holds the chunk*;
the lease records *one attempt at one node*.

Each lease mints a fresh **epoch** — a counter that only rises across a chunk's attempts — and the epoch is the fence
every state-advancing write is checked against. An operator's **restart** ([work/restart.md](../work/restart.md)) mints
one too, with no attempt behind it: the fence has to rise the instant the move lands, ahead of the re-entry's own lease,
or the attempt it displaces would still be able to advance the chunk.

The worker's **heartbeat** is a side effect of its tool use — no agent cooperation required — and is what keeps its
lease alive.

## Stale attempts are fenced out (`bzh:epoch-fencing`)

**Rule.** Every state-advancing write for a chunk — a transition, a decision, its artifacts — carries an epoch, and a
write below the chunk's newest epoch is rejected, never recorded; a terminal fact (stopped, delivered) rejects every
later state-advancing write regardless of epoch. The epoch is ordinarily the producing lease's, but the fence is the
chunk's, not any lease's: an operator restart ([work/restart.md](../work/restart.md)) mints one with no lease behind it,
and is itself a **fencing** write rather than a fenced one — it decides the new floor rather than being checked against
it.

**Why.** A worker presumed dead can wake and write after its successor started; fencing makes the successor
authoritative — the zombie's late writes bounce — so a zombie can lose work but never land wrong work, without requiring
anyone to kill processes reliably.

**Detect.** A state-advancing write path with no epoch check; a reap or reassignment design that assumes the old holder
is really dead instead of fencing it out, or a migration recorded at the submitting attempt's own epoch that relies on
it rather than on next-claim fencing; the epoch check skipped once a chunk is terminal.

**Do.** Every fresh claim of a re-queued chunk — a reassignment, or a route-released re-queue such as a detach or a
migration ([work/migration.md](../work/migration.md)) — mints new leases above the **hub-supplied** epoch floor: the
chunk's newest epoch as the hub knows it, carried on the claim, not whatever local history the claiming runner happens
to hold. A runner that never drove the chunk (no local floor of its own) still mints strictly above every prior attempt,
so the old holder's in-flight submission is rejected on arrival. Derive a fencing write's own epoch inside the
transaction that records it, never from a read the write is no longer holding. And read the fence generously on the
party that must *honor* it: the hub's floor lags every lease it has not yet been told about, so a fencing write can land
level with the attempt it displaces, and level is displaced.

**Don't.** Accept a transition because the submitting runner still holds the route — route tenure is not attempt
fencing.
