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

**Rule.** A subscription's exhaustion holds back every runner of the host spending it and no other, and lifts for all of
them together when it clears. No runner's brake is engaged by it, and nothing a person does is needed to lift it, though
a person may.

**Why.** The limit belongs to the plan and carries its own expiry: every runner spending it would meet it on its next
start, a runner paid from another plan has no reason to stop, and a fact that expires should not wait for someone to
clear it.

**Detect.**

- A limit met by one runner while another of its host spending the same subscription keeps starting work.
- A runner on another subscription, or none, held back by a neighbour's limit.
- A runner's brake engaged by a usage limit.
- A held-back runner still waiting after a sample shows its held window turned over and open, whether or not the
  expected reset has come.
- A runner admitted on a sample under 100 percent in the same period the limit was met in.
- One still waiting an hour past its expected reset with no sample since.
- One held by a hold an operator cleared, with no mark and no newly exhausted window after the clear.

**Do.** Two runners of one host spend one plan and a third spends another; a limit met by the first holds back the first
two, the third keeps working, and the first two claim again — the limited lease waking — once a sample shows the window
turned over.

**Don't.** Engage the reporting runner's brake and wait for an operator to lift it, or open the floor on a sample at 99
percent taken in the period the limit was met in.

**See also.** [./hosts.md](./hosts.md) §Subscriptions — what a subscription is and how the host samples it;
[../../architecture/crash-correctness/runner.md](../../architecture/crash-correctness/runner.md) §The usage-limit mark —
how the mark and the park hold across a crash.
