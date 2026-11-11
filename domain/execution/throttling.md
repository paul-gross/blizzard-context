# Throttling

What holds a runner back from starting work without anyone braking it, and what lets it go again. Spoke of the
[execution hub](../execution.md).

Before each tick's claims, and before every step or continuation of a parked session, a runner asks its gate whether to
start, and the gate answers from readings, never from a flag anyone set. A reading that turns restrictive stops further
claims from the next tick, while every step, a claimed chunk's first included, still asks before it starts. The breakers
answer first: a runner's brakes ([./pause.md](./pause.md)) refuse outright, and only past them is a throttle asked. A
throttle declines rather than refuses, and lifts of itself once its reading changes. The throttles, asked in this order
— the floor, then each the operator configures:

- The subscription floor.
- A pace against a window's elapsed share.
- A utilization line.
- A budget of spend over a trailing window against a dollar ceiling.
- A schedule.

A continuation of a step already begun answers to the floor alone. An escalation asks the breakers alone.

## An exhausted subscription holds back every runner spending it (`bzh:subscription-floor-reach`)

A subscription's exhaustion holds back every runner of the host spending it and no other — a runner on another
subscription, or on none, is not held back by it — and lifts for all of them together when it clears. No runner's brake
is engaged by it, and nothing a person does is needed to lift it, though a person may. The limit belongs to the plan and
carries its own expiry: every runner spending it would meet it on its next start, a runner paid from another plan has no
reason to stop, and a fact that expires should not wait for someone to clear it.

When the hold lifts:

- Once a sample shows the held window turned over and open, whether or not the expected reset has come. The held-back
  runners claim again, and the lease that met the limit wakes. A sample under 100 percent taken in the same period the
  limit was met in does not lift it.
- An hour past the expected reset, with no sample since.
- When an operator clears it; a cleared hold holds a runner back again only on a mark or a newly exhausted window after
  the clear.

[./hosts.md](./hosts.md) §Subscriptions states what a subscription is and how the host samples it, and
[../../architecture/crash-correctness/runner.md](../../architecture/crash-correctness/runner.md) §The usage-limit mark
states how the mark and the park hold across a crash.
